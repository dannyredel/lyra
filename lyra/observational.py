"""Observational causal inference — the assumption you can't test (LYRA §8). Promoted from NB 11.

Selection on **observables** is the easy half: with unconfoundedness given X, a doubly-robust / DML estimator
recovers the ATE even under nonlinear confounding (see `lyra.estimators.AIPW` and `DML` below). The hard half
is selection on **unobservables** — a hidden confounder U that no adjustment can remove, and whose absence is
**untestable from data**. The honest response is **sensitivity analysis**: quantify how strong an unobserved
confounder would have to be to overturn the finding, and benchmark that against the confounders you *did*
measure.

Two tools, both hand-rolled because the good packages are R-first (`sensemakr`) or unmaintained (STACK §47):
- **Cinelli & Hazlett (2020)** omitted-variable-bias framework — natural for regression/continuous outcomes:
  the **robustness value** RV, the bias from a confounder of given strength, the OVB contour, and benchmarking
  a hypothetical U against an observed covariate.
- **VanderWeele & Ding (2017)** **E-value** — a one-number summary on the risk-ratio scale.

`DML` wraps `econml.LinearDML` behind the `Estimator` Protocol so the harness can certify it next to AIPW.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.dgp import covariate_cols
from lyra.protocols import EstimatorResult


# ──────────────────────────────────────────────────────────────────────────────────────────────
# Modern doubly-robust ATE — the library estimator (econml DML), behind the Protocol
# ──────────────────────────────────────────────────────────────────────────────────────────────
class DML:
    """Double/debiased ML ATE via `econml.LinearDML` (cross-fitted, flexible nuisances). The library
    counterpart to the hand-rolled `lyra.estimators.AIPW` — recovers the ATE under selection on
    *observables* with a nonlinear baseline/propensity. Ref: Chernozhukov et al. 2018."""

    name, estimand, requires = "dml", "ATE", {"covariates"}

    def __init__(self, n_splits: int = 5, seed: int = 0):
        self.n_splits, self.seed = n_splits, seed

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        from econml.dml import LinearDML
        from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

        xcols = covariate_cols(df)
        Y = df.y.to_numpy(float); T = df.treat.to_numpy(int); W = df[xcols].to_numpy(float)
        est = LinearDML(model_y=HistGradientBoostingRegressor(max_depth=3, max_iter=150),
                        model_t=HistGradientBoostingClassifier(max_depth=3, max_iter=150),
                        discrete_treatment=True, cv=self.n_splits, random_state=self.seed)
        est.fit(Y, T, X=None, W=W)                       # X=None ⇒ constant effect (ATE), W = confounders
        ate = float(est.ate(X=None))
        lo, hi = (float(v) for v in est.ate_interval(X=None, alpha=0.05))
        se = (hi - lo) / (2 * 1.959963985)
        return EstimatorResult("dml", ate, (lo, hi), se=se, method_metadata={"backend": "econml.LinearDML"})


# ──────────────────────────────────────────────────────────────────────────────────────────────
# Sensitivity to UNOBSERVED confounding — Cinelli & Hazlett (2020), omitted-variable bias
# ──────────────────────────────────────────────────────────────────────────────────────────────
def partial_r2(t_stat: float, dof: int) -> float:
    """Partial R² of the treatment with the outcome, from its t-statistic: t²/(t²+dof). The share of
    residual outcome variance the treatment explains — the scale against which confounding is measured."""
    return float(t_stat ** 2 / (t_stat ** 2 + dof))


def robustness_value(t_stat: float, dof: int, q: float = 1.0, alpha: float | None = None) -> float:
    """**Robustness value** RV: the minimal partial R² an unobserved confounder must share with *both*
    treatment and outcome to move the estimate by 100·q% (q=1 ⇒ down to zero). RV=0.30 reads "confounding
    would need to explain 30% of the residual variation in both, beyond X, to explain away the effect."
    With ``alpha`` set, returns RV_{q,α} — the strength needed to also destroy significance at level α."""
    fq = q * abs(t_stat) / np.sqrt(dof)
    if alpha is not None:
        from scipy import stats
        t_crit = stats.t.ppf(1 - alpha / 2, dof - 1)
        fq = max((abs(t_stat) - t_crit), 0.0) * q / np.sqrt(dof)
    rv = 0.5 * (np.sqrt(fq ** 4 + 4 * fq ** 2) - fq ** 2)
    return float(np.clip(rv, 0.0, 1.0))


def ovb_bias(se: float, dof: int, r2_dz: float, r2_yz: float) -> float:
    """Bias an unobserved confounder Z would inject, given its partial R² with treatment (``r2_dz``) and
    with the outcome (``r2_yz``). bias = se·√dof · √( r2_yz · r2_dz / (1−r2_dz) ) — the Cinelli–Hazlett
    closed form. The amount the estimate would shift if Z were real."""
    bf = np.sqrt(r2_yz * r2_dz / (1.0 - r2_dz)) if r2_dz < 1 else np.inf
    return float(bf * se * np.sqrt(dof))


def adjusted_estimate(estimate: float, se: float, dof: int, r2_dz: float, r2_yz: float) -> float:
    """The estimate after subtracting the worst-case bias from a confounder of strength (r2_dz, r2_yz)
    — i.e. the bias is applied *toward the null* (the adversarial direction)."""
    bias = ovb_bias(se, dof, r2_dz, r2_yz)
    return float(np.sign(estimate) * max(abs(estimate) - bias, 0.0)) if estimate != 0 else -bias


def ovb_contour(estimate: float, se: float, dof: int, r2d_grid=None, r2y_grid=None):
    """Grid of worst-case adjusted estimates over (r2_dz, r2_yz) — the data behind the classic
    sensitivity *contour* plot whose 0-line shows which confounder strengths would explain the effect away.
    Returns ``(r2d, r2y, Z)`` with ``Z[i,j]`` the adjusted estimate at ``(r2d[j], r2y[i])``."""
    r2d = np.linspace(0, 0.6, 60) if r2d_grid is None else np.asarray(r2d_grid, float)
    r2y = np.linspace(0, 0.6, 60) if r2y_grid is None else np.asarray(r2y_grid, float)
    Z = np.array([[adjusted_estimate(estimate, se, dof, d, y) for d in r2d] for y in r2y])
    return r2d, r2y, Z


def benchmark_covariate(r2_yxj_resid: float, r2_dxj_resid: float, kd: float = 1.0, ky: float = 1.0):
    """Express a hypothetical confounder as "``kd``/``ky`` times as strong as observed covariate Xj".
    Given Xj's partial R² with treatment and outcome (after the *other* covariates), returns the implied
    ``(r2_dz, r2_yz)`` for a confounder ``kd``×/``ky``× as associated — the honest way to calibrate
    "how plausible is a strong-enough U?" against something you actually measured."""
    r2_dz = float(np.clip(kd * r2_dxj_resid, 0, 0.999))
    # outcome side scales the *bias factor*; clip into a valid partial-R²
    r2_yz = float(np.clip(ky * r2_yxj_resid, 0, 0.999))
    return r2_dz, r2_yz


# ──────────────────────────────────────────────────────────────────────────────────────────────
# E-value — VanderWeele & Ding (2017), a one-number summary on the risk-ratio scale
# ──────────────────────────────────────────────────────────────────────────────────────────────
def e_value(rr: float) -> float:
    """E-value for a risk ratio: the minimum strength (on the RR scale) of association an unmeasured
    confounder must have with *both* treatment and outcome to fully explain ``rr``. E = RR + √(RR·(RR−1)).
    Symmetric for RR<1 via 1/RR."""
    rr = 1.0 / rr if rr < 1 else rr
    return float(rr + np.sqrt(rr * (rr - 1.0)))


def e_value_smd(d: float) -> float:
    """E-value for a standardized mean difference (continuous outcome): convert to an approximate risk
    ratio RR ≈ exp(0.91·d) (VanderWeele–Ding §"continuous outcomes"), then take the E-value."""
    return e_value(float(np.exp(0.91 * d)))
