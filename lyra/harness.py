"""The Monte-Carlo harness — the power engine + the promotion gate (LYRA §4).
Promoted from ``notebooks/01_spine``.

```
for seed in range(R):
    df = dgp.sample(n, seed)
    res = estimator.estimate(df)
report: bias · RMSE · CI coverage (target 1-α) · reject-rate (type-I under H0 / power under H1)
```

Coverage against a known truth is the **CI test for statistical correctness** that gates an estimator
into the engine. One function certifies every method we add.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.protocols import DGP, Estimator


def harness(estimator: Estimator, dgp: DGP, R: int = 200, n: int = 2000, seed0: int = 1000,
            return_draws: bool = False) -> dict:
    """Run ``estimator`` on ``R`` draws from ``dgp``; report bias/RMSE/coverage/reject-rate.

    With ``return_draws``, also return the per-replicate point/interval/coverage arrays — the raw material
    for the sampling-distribution and coverage-caterpillar plots (the detailed analytics view)."""
    truth = dgp.ground_truth().ate
    pts, los, his, cover, rej, wid = [], [], [], [], [], []
    for r in range(R):
        res = estimator.estimate(dgp.sample(n, seed=seed0 + r))
        lo, hi = res.ci
        pts.append(float(res.point)); los.append(float(lo)); his.append(float(hi))
        cover.append(bool(lo <= truth <= hi))
        rej.append(not (lo <= 0.0 <= hi))
        wid.append(float(hi - lo))
    pts = np.array(pts)
    out = {
        "estimator": getattr(estimator, "name", type(estimator).__name__),
        "dgp": getattr(dgp, "name", type(dgp).__name__),
        "R": R, "n": n, "truth": truth,
        "bias": float(pts.mean() - truth),
        "rmse": float(np.sqrt(np.mean((pts - truth) ** 2))),
        "coverage": float(np.mean(cover)),
        "ci_width": float(np.mean(wid)),
        "reject_rate": float(np.mean(rej)),
        "label": "type_I" if abs(truth) < 1e-9 else "power",
    }
    if return_draws:
        out["draws"] = {"points": pts.tolist(), "lo": los, "hi": his, "covers": cover}
    return out


def robustness_grid(estimators, scenarios: dict, R: int = 120, n: int = 1500, seed0: int = 1000) -> pd.DataFrame:
    """Estimators × assumption-violation DGPs → tidy table of bias + coverage (LYRA §6)."""
    rows = []
    for scen, dgp in scenarios.items():
        for est in estimators:
            rep = harness(est, dgp, R=R, n=n, seed0=seed0)
            rows.append({"scenario": scen, "estimator": rep["estimator"],
                         "bias": rep["bias"], "coverage": rep["coverage"], "rmse": rep["rmse"]})
    return pd.DataFrame(rows)


def power_curve(estimator: Estimator, make_dgp, effects, R: int = 200, n: int = 2000) -> pd.DataFrame:
    """Power vs true effect — ``make_dgp(ate)`` builds the DGP at each effect (type-I at ate=0)."""
    return pd.DataFrame([{"effect": tau, **{k: harness(estimator, make_dgp(tau), R=R, n=n)[k]
                                            for k in ("reject_rate", "coverage", "label")}}
                         for tau in effects])
