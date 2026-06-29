"""FastAPI app — the live chassis (LYRA §13). Serves the same data the static snapshot exports.

Run: ``uvicorn chassis.app:app --reload`` (the React dev server proxies ``/api`` here). Scorecards are
computed lazily and cached (each runs the harness, so first hit is the slow one).
"""

from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chassis.assignment import assign
from chassis.export import _row
from chassis.registry import Experiment
from chassis.scorecard import compute
from chassis.seed import build
from chassis.worlds import build_world

app = FastAPI(title="Lyra chassis", version="0.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_REG, _WORLDS = build()
_CACHE: dict[str, dict] = {}
_COUNTER = {"n": 0}
_HARNESS_R = 100


class CreateSpec(BaseModel):
    name: str = "Untitled experiment"
    hypothesis: str = ""
    owner: str = "Daniel R."
    design: str = "ab"                       # ab | cluster | switchback | interference
    metric_type: str = "proportion"          # proportion | continuous (ab only)
    mu: float = 0.2
    sigma2: float = 1.0
    true_effect: float = 0.01                # the planted ground truth (this is a simulator)
    rel_mde: float = 0.05
    q_control: float = 0.5
    alpha: float = 0.05
    power: float = 0.8
    two_sided: bool = True
    n_success: int = 1
    n_comparisons: int = 1
    n_guardrail_nim: int = 0
    rho: float = 0.0
    days: int = 21
    n_per_day: int = 1500
    # design-specific structure
    G: int = 60                              # clusters / markets (cluster, interference)
    n_g: int = 25                            # units per cluster
    J: int = 50                              # markets (switchback)
    H: int = 20                              # periods (switchback)
    n_bar: int = 18                          # units per cell (switchback)
    sigma_total: float = 320.0               # switchback noise scale
    boost: float = 0.6                       # cannibalization strength (interference)
    interference_design: str = "cluster"     # user (naive) | cluster (interference-safe)


def _scorecard(exp_id: str) -> dict:
    if exp_id not in _CACHE:
        exp = _REG.get(exp_id); dgp, est, req = _WORLDS[exp_id]
        _CACHE[exp_id] = compute(exp, dgp, est, req, harness_R=_HARNESS_R)
    return _CACHE[exp_id]


def _warm_cache_from_snapshot():
    """Seed the scorecard cache from the precomputed static snapshot so the first list is instant
    (otherwise the cold call recomputes every seed scorecard — harness × N — and the UI hangs)."""
    import json
    import pathlib
    p = pathlib.Path(__file__).resolve().parent.parent / "frontend" / "public" / "data" / "chassis.json"
    if not p.exists():
        return
    try:
        snap = json.loads(p.read_text(encoding="utf-8"))
        for eid, sc in snap.get("scorecards", {}).items():
            if eid in _WORLDS:
                _CACHE.setdefault(eid, sc)
    except Exception:
        pass


_warm_cache_from_snapshot()


def _draft_power(exp, req) -> dict:
    avail = exp.days * exp.n_per_day
    return {"required_n": req, "current_n": avail, "powered": avail >= req,
            "pct_powered": round(min(100.0, 100 * avail / req), 1)}


@app.get("/api/health")
def health():
    return {"ok": True, "experiments": len(_REG.all())}


@app.get("/api/experiments")
def list_experiments():
    rows = []
    for exp in _REG.all():
        row = _row(exp); _, _, req = _WORLDS[exp.id]
        if exp.state == "DRAFT":
            row["power"] = _draft_power(exp, req)
        else:
            sc = _scorecard(exp.id)
            row.update({"readout": sc["readout"], "truth": sc["truth"], "power": sc["power"],
                        "diagnostics": sc["diagnostics"], "sequential": sc["sequential"],
                        "decision_rec": sc["decision_rec"]})
        rows.append(row)
    from lyra.diagnostics import bh_fdr
    running = [e for e in rows if e.get("readout") and e["state"] == "RUNNING"]
    fdr = bh_fdr([e["readout"]["p_value"] for e in running], alpha=0.05)
    for e, rej in zip(running, fdr["rejected"]):
        e["fdr_significant"] = bool(rej)
    return {"experiments": rows, "fdr": {"n_tested": fdr["m"], "n_significant": fdr["n_significant"]}}


@app.get("/api/experiments/{exp_id}")
def get_experiment(exp_id: str):
    if exp_id not in _WORLDS:
        raise HTTPException(404, "no such experiment")
    exp = _REG.get(exp_id)
    if exp.state == "DRAFT":
        return {**_row(exp), "power": _draft_power(exp, _WORLDS[exp_id][2])}
    return _scorecard(exp_id)


@app.get("/api/assign")
def assign_unit(unit: str, experiment: str):
    """Source-agnostic assignment — the same function the live SDK's get_variant() would call."""
    if experiment not in _WORLDS:
        raise HTTPException(404, "no such experiment")
    exp = _REG.get(experiment)
    return {"unit": unit, "experiment": experiment, "salt": exp.salt,
            "variant": assign(unit, exp.salt, exp.allocations)}


@app.get("/api/assign/check")
def assign_check(experiment: str, n: int = 4000):
    """Hash n synthetic units → arm split + SRM χ² (the balance the deterministic assignment produces)."""
    if experiment not in _WORLDS:
        raise HTTPException(404, "no such experiment")
    from chassis.assignment import srm_chi2
    exp = _REG.get(experiment)
    counts = {v: 0 for v in exp.allocations}
    for i in range(min(n, 50_000)):
        counts[assign(f"user_{i}", exp.salt, exp.allocations)] += 1
    chi, p = srm_chi2(counts, exp.allocations)
    return {"experiment": experiment, "salt": exp.salt, "allocations": exp.allocations,
            "counts": counts, "n": sum(counts.values()), "srm_p": round(p, 3), "srm_ok": p > 0.001}


@app.get("/api/metrics")
def list_metrics():
    """The governed metric catalog (the metrics layer as a platform artifact)."""
    from chassis.catalog import METRICS
    return {"metrics": METRICS}


@app.post("/api/experiments")
def create_experiment(spec: CreateSpec):
    """Create an experiment from the design form → a runnable DGP world + DRAFT power-gate."""
    try:
        w = build_world(spec.model_dump())
    except ValueError as e:
        raise HTTPException(400, str(e))
    _COUNTER["n"] += 1
    eid = f"exp_user_{_COUNTER['n']}"
    exp = Experiment(eid, spec.name or "Untitled experiment", spec.hypothesis, spec.owner, eid + "_salt",
                     {"control": spec.q_control, "treatment": round(1 - spec.q_control, 4)},
                     w["metric"], "DRAFT", w["world"],
                     w["design"], spec.days, spec.n_per_day, date.today().isoformat(), "")
    _REG.add(exp)
    _WORLDS[eid] = (w["dgp"], w["est"], w["required"])
    return {**_row(exp), "power": _draft_power(exp, w["required"])}


@app.post("/api/experiments/{exp_id}/transition")
def transition(exp_id: str, to_state: str, ship: bool | None = None, rationale: str = ""):
    if exp_id not in _WORLDS:
        raise HTTPException(404, "no such experiment")
    decision = None
    if to_state == "DECIDED":
        if ship is None:                              # default to the platform's ship recommendation
            rec = _scorecard(exp_id).get("decision_rec", {})
            ship, rationale = bool(rec.get("ship")), rationale or rec.get("reason", "")
        decision = {"ship": ship, "rationale": rationale}
    try:
        exp = _REG.transition(exp_id, to_state, decision)
    except ValueError as e:
        raise HTTPException(409, str(e))
    if to_state == "RUNNING" and not exp.started:
        exp.started = date.today().isoformat()
    _CACHE.pop(exp_id, None)
    return {"id": exp_id, "state": exp.state, "decision": exp.decision}
