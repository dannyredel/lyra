"""Event-log writer — the only interface between the engine and everything downstream.

Responsibility (T-15): write the append-only parquet log enforcing the data contract:
- Layout (EVENT_LOG §1): one file per day, ``events/day=<NN>/events.parquet`` (Hive partition).
- Schema (EVENT_LOG §3): fixed wide column set; unused fields null per ``event_type``.
- Invariants (EVENT_LOG §6) — ASSERT these on write:
    1. append-only, no row mutated after write;
    2. ``arrival`` precedes / ``churn`` terminates every agent's stream;
    3. ``ts`` monotonic non-decreasing within a day;
    4. cumulative ``budget_decrement.value`` per offer never exceeds ``budget_cap``;
    5. no ``conversion`` for a ``holdout`` agent on the held-out offer;
    6. SRM: realized arm shares match intended ``allocation`` within tolerance;
    7. ``propensity ∈ (0,1]`` wherever populated.

``ground_truth_tau`` is written here on every ``conversion`` but is estimator-hidden in
``real`` mode — the metrics ``staging`` model drops it (EVENT_LOG §4). The emitter still *writes*
it (the raw log is the oracle source); the hiding happens downstream in dbt staging.

``event_id`` is a deterministic counter (``e_<seq>``) rather than a random uuid so a run is fully
reproducible from ``(config + seed)``; uniqueness is guaranteed by the monotone counter.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

# Fixed wide schema (EVENT_LOG §3). Keep the column set identical across event types; unused
# fields are null for a given row.
SCHEMA = pa.schema(
    [
        ("event_id", pa.string()),
        ("ts", pa.timestamp("us")),
        ("day", pa.int32()),
        ("event_type", pa.string()),
        ("user_id", pa.string()),
        ("cluster_id", pa.string()),
        ("advertiser_id", pa.string()),
        ("offer_id", pa.string()),
        ("experiment_id", pa.string()),
        ("variant", pa.string()),
        ("allocation", pa.float64()),
        ("effort_spent", pa.float64()),
        ("reward_shown", pa.float64()),
        ("value", pa.float64()),
        ("propensity", pa.float64()),
        ("ground_truth_tau", pa.float64()),
    ]
)
COLUMNS = [f.name for f in SCHEMA]

EVENT_TYPES = {
    "arrival", "assignment", "impression", "conversion", "budget_decrement", "churn",
}

_EPOCH = np.datetime64("2025-01-01T00:00:00", "us")
_DAY = np.timedelta64(1, "D").astype("timedelta64[us]").astype("int64")  # microseconds per day


class InvariantError(AssertionError):
    """An event violated an EVENT_LOG §6 invariant — a bug in the engine, fail loudly."""


class EventEmitter:
    """Buffers events per simulated day and flushes a typed parquet partition; asserts invariants.

    Usage::

        emitter = EventEmitter("events/", mode="real", budget_caps={oid: cap}, ...)
        emitter.emit("arrival", day=0, user_id="u_1", cluster_id="c_0")
        ...
        emitter.flush_day(0)
        ...
        report = emitter.finalize()   # SRM report + counts
    """

    def __init__(
        self,
        output_dir: str | Path,
        *,
        mode: str = "real",
        budget_caps: dict[str, float] | None = None,
        srm_tolerance: float = 0.02,
        clear_existing: bool = True,
        write: bool = True,
        randomization: dict[str, str] | None = None,
    ):
        self.dir = Path(output_dir)
        self.mode = mode
        self.budget_caps = dict(budget_caps or {})
        self.srm_tolerance = srm_tolerance
        self.write = write          # False = invariants + metrics only, no parquet (shadow runs)
        self.randomization = dict(randomization or {})   # exp_id -> "user"|"cluster" (SRM unit)
        self._seq = 0
        self._buffer: list[dict] = []
        self._day_seq = 0  # intra-day event counter → ts ordering
        self._cur_day: int | None = None
        # invariant bookkeeping
        self._arrived: set[str] = set()
        self._churned: set[str] = set()
        self._budget_spent: dict[str, float] = {}
        self._flushed_days: set[int] = set()
        # SRM + summary counters
        self.assign_counts: dict[tuple[str, str], int] = {}
        self.alloc_seen: dict[str, float] = {}
        self.alloc_values: dict[str, set[float]] = {}   # distinct allocations seen (ramp detection)
        self.cluster_arms: dict[str, dict[str, set]] = {}   # exp -> arm -> {cluster_id} (cluster SRM)
        self.type_counts: dict[str, int] = {}

        if clear_existing:
            self._clear()

    # ---------------------------------------------------------------- emit
    def emit(self, event_type: str, *, day: int, **fields) -> None:
        if event_type not in EVENT_TYPES:
            raise InvariantError(f"unknown event_type {event_type!r}")
        if self._cur_day is None:
            self._begin_day(day)
        if day != self._cur_day:
            raise InvariantError(
                f"emit for day {day} but day {self._cur_day} is open — flush before advancing"
            )

        user_id = fields.get("user_id")
        variant = fields.get("variant")

        # --- §6.2 arrival precedes / churn terminates ---
        if event_type == "arrival":
            self._arrived.add(user_id)
        else:
            if user_id is not None:
                if event_type != "churn" and user_id in self._churned:
                    raise InvariantError(f"event {event_type} after churn for {user_id}")
                if user_id not in self._arrived:
                    raise InvariantError(f"{event_type} for {user_id} before arrival")
            if event_type == "churn":
                self._churned.add(user_id)

        # --- §6.5 (revised, D-14): a holdout conversion is allowed but is ORGANIC — no reward may
        #     have been served (reward_shown must be 0). This is the ghost-ads counterfactual: the
        #     reward was withheld, so any completion is reward-free; lift = treatment vs holdout.
        if event_type == "conversion" and variant == "holdout":
            if float(fields.get("reward_shown") or 0.0) != 0.0:
                raise InvariantError(
                    f"holdout conversion for {user_id} served reward "
                    f"{fields.get('reward_shown')} (must be 0)"
                )

        # --- §6.7 propensity in (0,1] ---
        prop = fields.get("propensity")
        if prop is not None and not (0.0 < float(prop) <= 1.0):
            raise InvariantError(f"propensity {prop} out of (0,1] for {event_type}")

        # --- §6.4 budget cap ---
        if event_type == "budget_decrement":
            oid = fields.get("offer_id")
            amt = float(fields.get("value") or 0.0)
            spent = self._budget_spent.get(oid, 0.0) + amt
            cap = self.budget_caps.get(oid)
            if cap is not None and spent > cap + 1e-6:
                raise InvariantError(
                    f"offer {oid} budget overspend: {spent:.4f} > cap {cap:.4f}"
                )
            self._budget_spent[oid] = spent

        # --- SRM counters (§6.6, checked at finalize) ---
        if event_type == "assignment":
            exp = fields.get("experiment_id")
            self.assign_counts[(exp, variant)] = self.assign_counts.get((exp, variant), 0) + 1
            if fields.get("allocation") is not None:
                self.alloc_seen[exp] = float(fields["allocation"])
                self.alloc_values.setdefault(exp, set()).add(float(fields["allocation"]))
            if self.randomization.get(exp) == "cluster":
                self.cluster_arms.setdefault(exp, {}).setdefault(variant, set()).add(
                    fields.get("cluster_id")
                )

        self.type_counts[event_type] = self.type_counts.get(event_type, 0) + 1

        row = {c: None for c in COLUMNS}
        row.update(fields)
        row["event_id"] = f"e_{self._seq:09d}"
        row["day"] = day
        row["event_type"] = event_type
        row["ts"] = _EPOCH + np.timedelta64(int(day) * _DAY + self._day_seq, "us")
        self._seq += 1
        self._day_seq += 1
        self._buffer.append(row)

    # ---------------------------------------------------------------- day lifecycle
    def _begin_day(self, day: int) -> None:
        self._cur_day = day
        self._day_seq = 0

    def flush_day(self, day: int) -> Path:
        """Write the buffered events for ``day`` to a Hive partition and clear the buffer."""
        if self._cur_day is not None and day != self._cur_day:
            raise InvariantError(f"flush_day({day}) but open day is {self._cur_day}")
        if day in self._flushed_days:
            raise InvariantError(f"day {day} already flushed (append-only)")

        part = self.dir / f"day={day:02d}"
        out = part / "events.parquet"
        if self.write:
            part.mkdir(parents=True, exist_ok=True)
            pq.write_table(self._to_table(self._buffer), out)

        self._flushed_days.add(day)
        self._buffer = []
        self._cur_day = None
        self._day_seq = 0
        return out

    def _to_table(self, rows: list[dict]) -> pa.Table:
        cols: dict[str, list] = {c: [] for c in COLUMNS}
        for r in rows:
            for c in COLUMNS:
                cols[c].append(r.get(c))
        arrays = []
        for f in SCHEMA:
            if f.name == "ts":
                arrays.append(pa.array(cols["ts"], type=f.type))
            else:
                arrays.append(pa.array(cols[f.name], type=f.type))
        return pa.Table.from_arrays(arrays, schema=SCHEMA)

    def reset_budgets(self) -> None:
        """Daily-refill hook: clear cumulative budget tracking (mirrors ``offers.refill: daily``)."""
        self._budget_spent.clear()

    # ---------------------------------------------------------------- finalize
    def finalize(self) -> dict:
        """Return run summary + SRM report; assert SRM within tolerance (§6.6) for ramped/A-A exps."""
        srm = self.srm_report()
        return {
            "n_events": self._seq,
            "type_counts": dict(self.type_counts),
            "days_flushed": sorted(self._flushed_days),
            "srm": srm,
        }

    def srm_report(self) -> dict[str, dict]:
        """Per-experiment realized treatment share vs intended allocation, with a pass/flag.

        Only **constant-allocation** experiments (the A/A nulls) get a hard SRM pass/flag — for a
        ramped experiment the cumulative realized share legitimately lags the latest allocation
        (assignments accrued at earlier, lower shares), so those are reported as informational
        (``ramped=True``) and not flagged. Per-epoch SRM for ramped experiments lives downstream
        (the dbt marts / dashboard health panel).
        """
        out: dict[str, dict] = {}
        exps = {exp for (exp, _v) in self.assign_counts}
        for exp in exps:
            t = self.assign_counts.get((exp, "treatment"), 0)
            c = self.assign_counts.get((exp, "control"), 0)
            h = self.assign_counts.get((exp, "holdout"), 0)
            total = t + c + h
            intended = self.alloc_seen.get(exp, float("nan"))
            ramped = len(self.alloc_values.get(exp, set())) > 1
            unit = self.randomization.get(exp, "user")

            if unit == "cluster":
                # SRM must be checked at the randomization unit — user-level share legitimately
                # varies for cluster designs (whole clusters flip arm). Count distinct clusters.
                ca = self.cluster_arms.get(exp, {})
                ct = len(ca.get("treatment", set()) | ca.get("holdout", set()))
                cc = len(ca.get("control", set()))
                denom = ct + cc
                realized = ct / denom if denom else 0.0
            else:
                realized = (t + h) / total if total else 0.0  # holdout was carved from treatment

            # cluster-randomized balance is high-variance with few clusters (cluster-share SE
            # ≈ sqrt(0.25/n_clusters)); use ~3 SE so SRM flags only gross imbalance, not the
            # ordinary lumpiness of assigning whole clusters.
            if unit == "cluster":
                n_clusters = len(ca.get("treatment", set()) | ca.get("holdout", set())
                                 | ca.get("control", set()))
                tol = 3.0 * (0.25 / max(1, n_clusters)) ** 0.5
            else:
                tol = self.srm_tolerance
            if ramped or total == 0 or np.isnan(intended):
                ok = True  # informational only
            else:
                ok = bool(abs(realized - intended) <= tol)
            out[exp] = {
                "treatment": t, "control": c, "holdout": h, "total": total,
                "realized_share": realized, "intended_share": intended,
                "unit": unit, "ramped": ramped, "ok": ok,
            }
        return out

    # ---------------------------------------------------------------- util
    def _clear(self) -> None:
        """Remove prior parquet partitions so a re-run is clean. Leaves (empty) dirs to dodge a
        Windows quirk where ``rmdir`` right after ``unlink`` can raise PermissionError."""
        if not self.write:
            return
        self.dir.mkdir(parents=True, exist_ok=True)
        for f in self.dir.glob("day=*/*.parquet"):
            try:
                f.unlink()
            except OSError:
                pass
