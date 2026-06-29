"""Staggered-entry panel — for peeking (NB 07) & DiD (NB 11). Promoted from ``notebooks/02_dgp_zoo``.

Ports the structure of Daniel's ``paper-library/monte_carlo_did_cov.qmd`` (Sant'Anna–Zhao 2020 DGP 1):
units observed over periods, **entering treatment at different times** (staggered), with **selection on
X** and a **calendar trend**. The known **ATT** is what DiD must recover — and diff-in-means is biased
here (treated cohorts differ at baseline + the trend), which is the whole point.

``sample`` returns a **long** panel (``unit, period, treated_group, G, post, y``). ``G`` is the adoption
period (a large sentinel = never treated); ``post = 1{period ≥ G}``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.protocols import GroundTruth

_NEVER = 10 ** 6


def _sig(z):
    return 1.0 / (1.0 + np.exp(-z))


class StaggeredPanelDGP:
    name = "panel-staggered"

    def __init__(self, T: int = 6, att: float = 1.0, xi_ps: float = 0.75, trend: float = 0.5, d: int = 4):
        self.T, self.att, self.xi_ps, self.trend, self.d = T, att, xi_ps, trend, d

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        X = rng.normal(0, 1, (n, self.d))
        fx = X @ np.array([1.0, -0.5, 0.3, 0.2])                       # covariate index drives Y and selection
        treated = (rng.random(n) < _sig(self.xi_ps * fx)).astype(int)  # eventually-treated (selection on X)
        G = np.where(treated == 1, rng.integers(3, self.T + 1, n), _NEVER)
        eta = fx + rng.normal(0, 1, n)                                 # unit fixed effect (correlated with X)
        out = []
        for t in range(1, self.T + 1):
            post = (t >= G).astype(int)
            y = eta + self.trend * t + self.att * post + rng.normal(0, 1, n)
            out.append(pd.DataFrame({"unit": np.arange(n), "period": t, "treated_group": treated,
                                     "G": G, "post": post, "y": y}))
        return pd.concat(out, ignore_index=True)

    def ground_truth(self) -> GroundTruth:
        return GroundTruth(ate=float(self.att), extra={"estimand": "ATT", "design": "staggered_adoption"})
