"""Core randomized-ATE estimators behind the `Estimator` Protocol (LYRA §8).
Promoted verbatim from the raw functions in ``notebooks/01_spine``.

The three-way contrast is the spine **and** the misspecification demo:
- **DiffInMeans** — unbiased under randomization, biased under confounding;
- **OLSAdjust** — linear covariate adjustment; biased when the baseline is nonlinear;
- **AIPW** — doubly-robust, cross-fitted; survives nonlinear confounding with flexible nuisances.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.model_selection import KFold

from lyra.dgp import covariate_cols
from lyra.protocols import EstimatorResult


class DiffInMeans:
    name, estimand, requires = "diff", "ATE", set()

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        t = df.loc[df.treat == 1, "y"].to_numpy(float)
        c = df.loc[df.treat == 0, "y"].to_numpy(float)
        point = float(t.mean() - c.mean())
        vt, vc = t.var(ddof=1) / t.size, c.var(ddof=1) / c.size
        se = float(np.sqrt(vt + vc))                                  # Welch SE
        dof = (vt + vc) ** 2 / (vt ** 2 / (t.size - 1) + vc ** 2 / (c.size - 1))
        h = stats.t.ppf(0.975, dof) * se
        p = float(2 * stats.t.sf(abs(point) / se, dof)) if se > 0 else float("nan")
        return EstimatorResult("diff", point, (point - h, point + h), se=se, p_value=p)


class OLSAdjust:
    """OLS of y on treatment + linear covariates, HC1-robust SE."""

    name, estimand, requires = "ols", "ATE", {"covariates"}

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        xcols = covariate_cols(df)
        X = sm.add_constant(df[["treat", *xcols]].to_numpy(float))
        m = sm.OLS(df.y.to_numpy(float), X).fit(cov_type="HC1")
        b, se = float(m.params[1]), float(m.bse[1])                   # 0=const, 1=treat
        return EstimatorResult("ols", b, (b - 1.96 * se, b + 1.96 * se), se=se,
                               p_value=float(m.pvalues[1]), method_metadata={"adjustment": "linear"})


class AIPW:
    """Doubly-robust AIPW with cross-fitted flexible nuisances + estimated propensity."""

    name, estimand, requires = "aipw", "ATE", {"covariates"}

    def __init__(self, n_splits: int = 3, clip: float = 0.02, seed: int = 0):
        self.n_splits, self.clip, self.seed = n_splits, clip, seed

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        xcols = covariate_cols(df)
        X = df[xcols].to_numpy(float); y = df.y.to_numpy(float); t = df.treat.to_numpy(int)
        n = len(df); mu1 = np.zeros(n); mu0 = np.zeros(n); e = np.full(n, 0.5)
        for tr, te in KFold(self.n_splits, shuffle=True, random_state=self.seed).split(X):
            for arm, mu in ((1, mu1), (0, mu0)):
                sel = tr[t[tr] == arm]
                g = HistGradientBoostingRegressor(max_depth=3, max_iter=100, learning_rate=0.1)
                g.fit(X[sel], y[sel]); mu[te] = g.predict(X[te])
            if 0 < t[tr].mean() < 1:
                cl = HistGradientBoostingClassifier(max_depth=3, max_iter=100, learning_rate=0.1)
                cl.fit(X[tr], t[tr]); e[te] = cl.predict_proba(X[te])[:, 1]
        e = np.clip(e, self.clip, 1 - self.clip)
        psi = mu1 - mu0 + t / e * (y - mu1) - (1 - t) / (1 - e) * (y - mu0)
        point = float(psi.mean()); se = float(psi.std(ddof=1) / np.sqrt(n))
        p = float(2 * (1 - stats.norm.cdf(abs(point) / se))) if se > 0 else float("nan")
        return EstimatorResult("aipw", point, (point - 1.96 * se, point + 1.96 * se), se=se, p_value=p,
                               diagnostics={"overlap_min_e": float(e.min()), "overlap_max_e": float(e.max())})


ALL = [DiffInMeans(), OLSAdjust(), AIPW()]
