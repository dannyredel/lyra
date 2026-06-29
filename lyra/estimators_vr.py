"""Variance-reduction estimators for switchback / panel designs (LYRA §8). Promoted from NB 06.

`SwitchbackCUPED` is the realistic switchback analysis: CUPED-adjust the outcome on a **pre-period
baseline** (`x_hist`, the cell's historical α+γ), then a **cluster-robust OLS** clustered on the market.
Unbiased (the covariate is pre-treatment) but much tighter than the raw estimator. (The notebook also
builds CUPAC and DML-DR — the ML-covariate versions — raw; CUPED is the no-ML default we promote.)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from lyra.protocols import EstimatorResult
from lyra.se import se_cv1


class SwitchbackCUPED:
    name, estimand, requires = "switchback_cuped", "ATE", {"cluster", "pre_period"}

    def __init__(self, x: str = "treat", y: str = "y", cluster: str = "cluster", pre: str = "x_hist"):
        self.x, self.y, self.cluster, self.pre = x, y, cluster, pre

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        xh = df[self.pre].to_numpy(float); yv = df[self.y].to_numpy(float)
        theta = np.cov(yv, xh)[0, 1] / xh.var(ddof=1)            # CUPED coefficient (pre-period, no bias)
        adj = yv - theta * (xh - xh.mean())
        d = df.assign(_yc=adj)
        b, se = se_cv1(d, x=self.x, y="_yc", cluster=self.cluster)
        crit = float(stats.t.ppf(0.975, df[self.cluster].nunique() - 1))     # t(G-1) for cluster-robust
        p = float(2 * (1 - stats.norm.cdf(abs(b) / se))) if se > 0 else float("nan")
        return EstimatorResult("switchback_cuped", float(b), (b - crit * se, b + crit * se), se=float(se),
                               estimand="ATE", p_value=p, method_metadata={"theta": float(theta)})
