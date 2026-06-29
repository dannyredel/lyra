"""Snapshot exporter — compute the whole registry + scorecards once → static JSON for the frontend.

Lets the React app deploy static (no live server needed), while `chassis/app.py` serves the same data
live. `python -m chassis.export` writes `frontend/public/data/chassis.json`.
"""

from __future__ import annotations

import json
import pathlib

from chassis.scorecard import compute
from chassis.seed import build


def _row(exp) -> dict:
    return {"id": exp.id, "name": exp.name, "owner": exp.owner, "state": exp.state,
            "metric": exp.metric, "design": exp.design, "created": exp.created,
            "guardrails": exp.guardrails, "allocations": exp.allocations,
            "days": exp.days, "n_per_day": exp.n_per_day, "hypothesis": exp.hypothesis}


def build_snapshot(harness_R: int = 120) -> dict:
    from lyra.diagnostics import bh_fdr
    reg, worlds = build()
    experiments, scorecards = [], {}
    for exp in reg.all():
        dgp, est, req = worlds[exp.id]
        row = _row(exp)
        if exp.state == "DRAFT":
            avail = exp.days * exp.n_per_day
            row["power"] = {"required_n": req, "current_n": avail,
                            "pct_powered": round(min(100.0, 100 * avail / req), 1),
                            "powered": avail >= req}
        else:
            sc = compute(exp, dgp, est, req, harness_R=harness_R)
            scorecards[exp.id] = sc
            row.update({"readout": sc["readout"], "truth": sc["truth"], "power": sc["power"],
                        "diagnostics": sc["diagnostics"], "sequential": sc["sequential"],
                        "decision_rec": sc["decision_rec"]})
        experiments.append(row)
    # portfolio FDR — control false discoveries across the running primary metrics (cross-cutting)
    running = [e for e in experiments if e.get("readout") and e["state"] == "RUNNING"]
    fdr = bh_fdr([e["readout"]["p_value"] for e in running], alpha=0.05)
    for e, rej in zip(running, fdr["rejected"]):
        e["fdr_significant"] = bool(rej)
    return {"experiments": experiments, "scorecards": scorecards,
            "meta": {"n_experiments": len(experiments), "palette": "ocean",
                     "fdr": {"n_tested": fdr["m"], "n_significant": fdr["n_significant"], "alpha": 0.05}}}


def write(path: str = "frontend/public/data/chassis.json", harness_R: int = 120) -> dict:
    snap = build_snapshot(harness_R=harness_R)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snap, separators=(",", ":")))
    return snap


if __name__ == "__main__":
    s = write()
    print(f"wrote frontend/public/data/chassis.json — {s['meta']['n_experiments']} experiments")
