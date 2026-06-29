"""Offline grid job for Ch7 — the decision-grade run that's too slow for the notebook.

Sweeps the scarcity grid (one knob at a time off the favorable baseline), plus a kappa=0 null, and writes
``outputs/grid_results.json``. Ch7 loads that and renders the verdict. Mirror of REPLICATE.md's run_study.py.

    python run_grid.py            # default M=5 (exploratory; ~30 min)
    python run_grid.py 20         # M=20 (tighter; hours)
"""
import sys, json, time, warnings, pathlib
warnings.filterwarnings("ignore")
try: sys.stdout.reconfigure(encoding="utf-8")   # labels carry Greek (ρ, γ); avoid cp1252 crash on Windows
except Exception: pass

from mml.harness import (verdict_grid, run_cell, conclude, Scenario, GO_BASELINE, CHANNELS)

M = int(sys.argv[1]) if len(sys.argv) > 1 else 5
out = pathlib.Path(__file__).parent / "outputs"; out.mkdir(exist_ok=True)
t0 = time.time()

cells = []
baseline_nopool = None
for label, axis, scn in verdict_grid():
    print(f"[{time.time()-t0:5.0f}s] cell: {label:24s} ({scn.label()})", flush=True)
    ests = ["nopool", "pooled_geo"] if axis == "—" else ["pooled_geo"]   # nopool only needed once (H5)
    res = run_cell(scn, M, estimators=ests)
    if "nopool" in res:
        baseline_nopool = res["nopool"]
    cells.append({"label": label, "axis": axis, "scenario": scn.label(),
                  "knobs": {"N": scn.N, "rho": scn.rho, "kappa": scn.kappa,
                            "gamma": scn.gamma, "geo": scn.geo_anchor},
                  "pooled_geo": res.get("pooled_geo", {"n_sims": 0})})

print(f"[{time.time()-t0:5.0f}s] null cell: kappa=0", flush=True)
null_scn = Scenario(N=GO_BASELINE.N, rho=GO_BASELINE.rho, kappa=0.0,
                    gamma=GO_BASELINE.gamma, geo_anchor=True)
null = run_cell(null_scn, M, estimators=["pooled_geo"])

# verdict per cell (re-use the baseline nopool for H5 and the shared null for H4)
for cell in cells:
    go_like = {"pooled_geo": cell["pooled_geo"], "nopool": baseline_nopool}
    v = conclude(go_like, null, primary="pooled_geo", baseline="nopool")
    cell["verdict"] = v["verdict"]
    cell["ledger"] = {h: {"pass": d["pass_"], "detail": d["detail"]} for h, d in v["ledger"].items()}

results = {"M": M, "channels": CHANNELS, "baseline_nopool": baseline_nopool,
           "null_kappa_fp": null["pooled_geo"].get("kappa_detected_frac"),
           "elapsed_s": round(time.time() - t0, 0), "cells": cells}
path = out / "grid_results.json"
path.write_text(json.dumps(results, indent=2, default=float))
print(f"\nwrote {path}  ({results['elapsed_s']:.0f}s, M={M})")
for c in cells:
    print(f"  {c['label']:24s} -> {c['verdict']}")
