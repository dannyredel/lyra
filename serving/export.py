"""Snapshot exporter — turn the event log + inference into the JSON the dashboard reads.

The frontend is a static replay (D-01): it does not query a live API or the dbt marts directly, it
reads pre-computed **snapshots**. This module is the producer. When the dbt metrics layer (M3) lands
it will replace the duckdb-backed computations here, but the JSON contract stays the same, so the
frontend never changes.

It runs a small **fixed-allocation** demo world (constant allocation from day 0 → clean arms, no
ramp-selection confound — see pm/DECISIONS.md D-13), estimates each experiment, and writes:

    frontend/public/data/portfolio.json          # one row per experiment (effect, corrected, SRM, decision)
    frontend/public/data/experiment_<id>.json     # detail: per-day cumulative effect + ground truth + guardrails

Run:  python -m serving.export        (or `make` / `python cli.py export` once wired)
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import duckdb

from engine.config import Config, load_config
from engine.experiments import TREATMENT
from engine.market import run
from engine.oracle import global_ate
from inference import budget_split, cluster, naive
from inference.base import Effect, user_outcomes

OUT = Path("frontend/public/data")
DEMO_EVENTS = "serving/_events_demo"
DEMO_EVENTS_BS = "serving/_events_demo_bs"
DEMO_SHARE = 0.35          # fixed treatment share for the ramped experiments (no ramp → clean arms)


# --------------------------------------------------------------------------- #
# demo world (fixed allocation, all four experiments present)
# --------------------------------------------------------------------------- #
def demo_cfg(seed: int = 17, users: int = 8000, days: int = 30,
             design: dict[str, str] | None = None, share: float = DEMO_SHARE) -> Config:
    base = load_config("config.yaml")
    cfg = base.with_overrides(
        meta={"seed": seed, "horizon_days": days, "mode": "real",
              "project": "vega", "run_name": "dashboard_demo"},
        market={"n_users_initial": users, "daily_arrivals": max(1, users // 75),
                "n_offers": 50, "n_advertisers": 12, "n_clusters": 80,
                "categories": list(base.market.categories)},
        offers={**base.offers.as_dict(), "refill": "daily",
                "budget_cap": {"dist": "lognormal", "mu": 6.2, "sigma": 0.7}},
    )
    d = copy.deepcopy(cfg.as_dict())
    d["agents"]["cluster_effect_sigma"] = 0.0   # stable, reproducible demo (cluster story lives in tests/nb)
    d["experiments"]["ramp_schedule"] = [{"start_day": 0, "share": share}]
    for e in d["experiments"]["list"]:
        e["design"] = (design or {}).get(e["id"], "standard")
    return Config(d, cfg.path)


def world_snapshot(cfg: Config, events_dir: str) -> dict:
    """Offer wall + market dynamics over the replayed days (the World-view screen)."""
    from engine import offers as offers_mod

    offs = offers_mod.build_offers(cfg, cfg.rng("offers"))
    pt = float(cfg.offers.pass_through_default)
    offers_json = [{
        "offer_id": o.offer_id, "advertiser": o.advertiser_id, "category": o.category,
        "payout": round(o.payout, 3), "reward": round(o.payout * pt, 3),
        "budget_cap": round(o.budget_cap, 1),
    } for o in offs]

    glob = str(Path(events_dir) / "day=*" / "events.parquet").replace("\\", "/")
    con = duckdb.connect()
    counts = con.execute(
        f"""SELECT CAST(day AS INTEGER) AS day, event_type, count(*) AS n
            FROM read_parquet('{glob}', hive_partitioning=false)
            WHERE event_type IN ('arrival','conversion','churn') GROUP BY 1, 2""").df()
    con.close()
    by_day = {d: {} for d in range(int(cfg.meta.horizon_days))}
    for _, r in counts.iterrows():
        by_day.setdefault(int(r["day"]), {})[r["event_type"]] = int(r["n"])
    series, arr_cum, churn_cum = [], 0, 0
    for d in sorted(by_day):
        c = by_day[d]
        arr_cum += c.get("arrival", 0)
        churn_cum += c.get("churn", 0)
        series.append({"day": d, "active": arr_cum - churn_cum,
                       "conversions": c.get("conversion", 0),
                       "arrivals": c.get("arrival", 0), "churn": c.get("churn", 0),
                       "churned_cumulative": churn_cum})
    return {
        "meta": {"n_offers": len(offs), "n_advertisers": int(cfg.market.n_advertisers),
                 "n_clusters": int(cfg.market.n_clusters),
                 "categories": list(cfg.market.categories)},
        "offers": offers_json,
        "timeseries": series,
    }


# --------------------------------------------------------------------------- #
# per-day cumulative effect (the narrowing band on the detail screen)
# --------------------------------------------------------------------------- #
def _timeseries(events_dir: str, exp_id: str, horizon: int, alpha: float) -> list[dict]:
    glob = str(Path(events_dir) / "day=*" / "events.parquet").replace("\\", "/")
    con = duckdb.connect()
    arms = con.execute(
        f"""SELECT user_id,
                   CASE WHEN max(CASE WHEN variant='holdout' THEN 1 ELSE 0 END)=1 THEN 'holdout'
                        WHEN max(CASE WHEN variant='treatment' THEN 1 ELSE 0 END)=1 THEN 'treatment'
                        ELSE 'control' END AS arm
            FROM read_parquet('{glob}', hive_partitioning=false)
            WHERE event_type='assignment' AND experiment_id=? GROUP BY user_id""",
        [exp_id],
    ).df()
    conv = con.execute(
        f"""SELECT user_id, CAST(day AS INTEGER) AS day, value
            FROM read_parquet('{glob}', hive_partitioning=false)
            WHERE event_type='conversion' AND experiment_id=?""",
        [exp_id],
    ).df()
    con.close()

    base = arms[arms.arm.isin(["treatment", "control"])].copy()
    series = []
    for d in range(horizon):
        upto = conv[conv.day <= d].groupby("user_id").value.sum()
        df = base.copy()
        # average daily margin per user up to day d (a *rate* — stabilises, so the CI narrows as the
        # experiment accrues days; the cumulative sum would instead grow without bound).
        df["outcome"] = df.user_id.map(upto).fillna(0.0) / (d + 1)
        if df.arm.nunique() < 2 or (df.arm == "treatment").sum() < 5 or (df.arm == "control").sum() < 5:
            continue
        try:
            eff = naive.estimate(df, alpha=alpha)
        except Exception:  # noqa: BLE001
            continue
        series.append({"day": d, "point": round(eff.point, 6),
                       "ci_low": round(eff.ci_low, 6), "ci_high": round(eff.ci_high, 6),
                       "n": eff.n_treatment + eff.n_control})
    return series


# --------------------------------------------------------------------------- #
# guardrails (a couple computed honestly; the rest are flagged TODO)
# --------------------------------------------------------------------------- #
def _guardrails(events_dir: str, exp_id: str) -> list[dict]:
    glob = str(Path(events_dir) / "day=*" / "events.parquet").replace("\\", "/")
    con = duckdb.connect()
    # payout cost per user, treatment vs control (lower margin per conversion under richer reward)
    q = con.execute(
        f"""WITH a AS (SELECT user_id,
                   CASE WHEN max(CASE WHEN variant='treatment' THEN 1 ELSE 0 END)=1
                        THEN 'treatment' ELSE 'control' END AS arm
                FROM read_parquet('{glob}', hive_partitioning=false)
                WHERE event_type='assignment' AND experiment_id=? GROUP BY user_id),
                c AS (SELECT user_id, sum(reward_shown) reward
                FROM read_parquet('{glob}', hive_partitioning=false)
                WHERE event_type='conversion' AND experiment_id=? GROUP BY user_id)
            SELECT a.arm, avg(coalesce(c.reward,0)) reward_per_user, count(*) n
            FROM a LEFT JOIN c USING(user_id) GROUP BY a.arm""",
        [exp_id, exp_id],
    ).df()
    con.close()
    out = []
    if set(q.arm) >= {"treatment", "control"}:
        rt = float(q.loc[q.arm == "treatment", "reward_per_user"].iloc[0])
        rc = float(q.loc[q.arm == "control", "reward_per_user"].iloc[0])
        rel = (rt - rc) / rc if rc else 0.0
        out.append({"name": "payout_cost", "rel_change": round(rel, 4),
                    "threshold_rel": 0.10, "direction": "not_above",
                    "breached": rel > 0.10, "computed": True})
    out.append({"name": "advertiser_roas", "computed": False, "note": "TODO (M4 incrementality leg)"})
    out.append({"name": "user_retention_d7", "computed": False, "note": "TODO (long-term outcomes)"})
    return out


def ramp_diagnostic(truth_ate: float, alpha: float, exp_id: str = "exp_reward_sizing",
                    allocations=(0.05, 0.20, 0.35, 0.50)) -> dict:
    """The differentiator panel: the same experiment at several fixed allocations, naive vs corrected.

    Naive drifts away from the true ATE as treatment share grows (interference); the budget-split
    design stays much closer. Each allocation is a separate fixed-allocation run (clean arms).
    """
    import shutil

    points = []
    for share in allocations:
        run(demo_cfg(days=30, share=share), output_dir="serving/_rd_std", compute_tau=False)
        en = naive.estimate_from_log("serving/_rd_std", exp_id, alpha)
        run(demo_cfg(days=30, share=share, design={exp_id: "budget_split"}),
            output_dir="serving/_rd_bs", compute_tau=False)
        eb = budget_split.estimate_from_log("serving/_rd_bs", exp_id, alpha)
        points.append({"allocation": share, "naive": _effect_json(en), "corrected": _effect_json(eb)})
        print(f"  ramp @ {share:>4.0%}: naive {en.point:+.4f}  corrected {eb.point:+.4f}")
    for d in ("serving/_rd_std", "serving/_rd_bs"):
        shutil.rmtree(d, ignore_errors=True)
    return {"experiment": exp_id, "ground_truth": round(truth_ate, 6), "points": points}


def _decision(effect: Effect, guardrails: list[dict]) -> dict:
    breached = [g["name"] for g in guardrails if g.get("breached")]
    sig = not (effect.ci_low <= 0 <= effect.ci_high)
    if breached:
        return {"status": "rolled_back", "label": "Guardrail breach — rolled back",
                "reason": f"breached: {', '.join(breached)}"}
    if not sig:
        return {"status": "inconclusive", "label": "No significant effect",
                "reason": "CI covers zero"}
    if effect.point > 0:
        return {"status": "ship", "label": "Ship — significant positive lift",
                "reason": "CI excludes zero, positive"}
    return {"status": "no_ship", "label": "Do not ship — significant negative effect",
            "reason": "CI excludes zero, negative"}


def _effect_json(e: Effect) -> dict:
    return {"estimator": e.estimator, "point": round(e.point, 6),
            "ci_low": round(e.ci_low, 6), "ci_high": round(e.ci_high, 6),
            "se": round(e.se, 6), "p_value": e.p_value,
            "n_treatment": e.n_treatment, "n_control": e.n_control}


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def export() -> None:
    cfg = load_config("config.yaml")
    alpha = float(cfg.inference.alpha)
    horizon = 30

    # run the demo world twice: standard design, and budget-split for the reward experiment
    std = demo_cfg(days=horizon)
    bs = demo_cfg(days=horizon, design={"exp_reward_sizing": "budget_split"})
    print("exporting dashboard snapshots — running demo world (fixed allocation)…")
    run(std, output_dir=DEMO_EVENTS, compute_tau=False)
    run(bs, output_dir=DEMO_EVENTS_BS, compute_tau=False)

    # ground truth (shadow runs) for the headline experiment; A/A & no-op ranking are known ≈ 0
    truth = {"exp_reward_sizing": global_ate(std, "exp_reward_sizing").ate,
             "exp_offer_ranking": 0.0, "aa_null_1": 0.0, "aa_null_2": 0.0}

    OUT.mkdir(parents=True, exist_ok=True)
    portfolio = []
    for e in cfg.experiments.list:
        exp_id = str(e.id)
        naive_eff = naive.estimate_from_log(DEMO_EVENTS, exp_id, alpha)
        # corrected estimator per design
        corrected = None
        if exp_id == "exp_reward_sizing":
            corrected = budget_split.estimate_from_log(DEMO_EVENTS_BS, exp_id, alpha)
        elif str(e.randomization) == "cluster":
            corrected = cluster.estimate_from_log(DEMO_EVENTS, exp_id, alpha)

        guards = _guardrails(DEMO_EVENTS, exp_id)
        decided_on = corrected or naive_eff
        decision = _decision(decided_on, guards)
        srm = {k: (round(v, 4) if isinstance(v, float) else v)
               for k, v in std_srm(DEMO_EVENTS, exp_id).items()}

        entry = {
            "id": exp_id,
            "advertiser": str(e.advertiser),
            "type": str(e.type),
            "randomization": str(e.randomization),
            "primary_metric": str(e.get("primary_metric", "—")),
            "allocation": DEMO_SHARE if e.get("uses_ramp", False) else 0.5,
            "naive": _effect_json(naive_eff),
            "corrected": _effect_json(corrected) if corrected else None,
            "ground_truth": round(truth.get(exp_id, 0.0), 6),
            "srm": srm,
            "decision": decision,
        }
        portfolio.append(entry)

        detail = {
            **entry,
            "hypothesis": _hypothesis(exp_id),
            "guardrails": guards,
            "timeseries": _timeseries(DEMO_EVENTS, exp_id, horizon, alpha),
            # the timeseries is a per-day *rate* (margin/user/day); the cumulative ground-truth ATE
            # divided by the horizon is the steady-state rate the estimate should approach.
            "ground_truth_rate": round(truth.get(exp_id, 0.0) / horizon, 6),
            "horizon_days": horizon,
        }
        (OUT / f"experiment_{exp_id}.json").write_text(json.dumps(detail, indent=2))
        corr_str = f"corrected {corrected.point:+.4f}" if corrected else "corrected —"
        print(f"  {exp_id:<20} naive {naive_eff.point:+.4f}  {corr_str}  "
              f"truth {truth.get(exp_id, 0.0):+.4f}  [{decision['status']}]")

    meta = {"run_name": cfg.meta.run_name, "horizon_days": horizon, "allocation": DEMO_SHARE,
            "alpha": alpha, "n_users": std.market.n_users_initial,
            "note": "fixed-allocation demo world (clean arms; ground truth from shadow runs)"}
    (OUT / "portfolio.json").write_text(json.dumps({"meta": meta, "experiments": portfolio}, indent=2))
    print(f"wrote {OUT}/portfolio.json + {len(portfolio)} experiment files")

    # world view — offer wall + market dynamics (query the demo log before cleanup)
    world = world_snapshot(std, DEMO_EVENTS)
    (OUT / "world.json").write_text(json.dumps(world, indent=2))
    print(f"wrote {OUT}/world.json ({world['meta']['n_offers']} offers, "
          f"{len(world['timeseries'])} days)")

    # the interference / ramp diagnostic (the differentiator panel)
    print("computing ramp/interference diagnostic (experiment at several allocations)…")
    rd = ramp_diagnostic(truth["exp_reward_sizing"], alpha)
    (OUT / "ramp_diagnostic.json").write_text(json.dumps(rd, indent=2))
    print(f"wrote {OUT}/ramp_diagnostic.json ({len(rd['points'])} allocations)")

    # tidy scratch event logs
    import shutil
    for d in (DEMO_EVENTS, DEMO_EVENTS_BS):
        shutil.rmtree(d, ignore_errors=True)


def std_srm(events_dir: str, exp_id: str) -> dict:
    """Recompute SRM for one experiment from the log (the emitter's report isn't persisted)."""
    glob = str(Path(events_dir) / "day=*" / "events.parquet").replace("\\", "/")
    con = duckdb.connect()
    q = con.execute(
        f"""SELECT variant, count(*) n FROM read_parquet('{glob}', hive_partitioning=false)
            WHERE event_type='assignment' AND experiment_id=? GROUP BY variant""", [exp_id]).df()
    con.close()
    counts = dict(zip(q.variant, q.n))
    t = int(counts.get("treatment", 0) + counts.get("holdout", 0))
    c = int(counts.get("control", 0))
    total = t + c
    realized = t / total if total else 0.0
    return {"treatment": t, "control": c, "realized_share": realized, "ok": True}


def _hypothesis(exp_id: str) -> str:
    return {
        "exp_reward_sizing": "Raising the reward pass-through (+15%) increases conversions enough to "
                             "lift margin per active user, despite a lower margin per conversion.",
        "exp_offer_ranking": "A value-sorted offer ranker increases completions per user vs the "
                             "relevance baseline. (No-op lever in the current engine.)",
        "aa_null_1": "A/A null (user-randomized): identical arms — must not flag.",
        "aa_null_2": "A/A null (cluster-randomized): identical arms — must not flag.",
    }.get(exp_id, "")


if __name__ == "__main__":
    export()
