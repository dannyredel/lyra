"""CUPED — variance reduction using pre-experiment data.

Responsibility (T-42): regression-adjust the outcome on a pre-period covariate to cut variance
without biasing the effect. Composes with the other estimators (adjust, then difference-in-means).

CUPED (Deng, Xu, Kohavi, Walker, WSDM 2013) replaces the outcome $Y$ with
$$\\tilde Y_i = Y_i - \\theta\\,(X_i - \\bar X),\\qquad \\theta = \\frac{\\mathrm{Cov}(Y,X)}{\\mathrm{Var}(X)},$$
where $X$ is a **pre-treatment** covariate (here: each user's margin during a warmup period, which the
treatment cannot have affected). Because $X$ is pre-treatment, $\\mathbb{E}[\\tilde Y]$ is unchanged
(unbiased) but its variance is reduced by the factor $1-\\rho^2$ with $\\rho=\\mathrm{Corr}(Y,X)$ — so
the effect estimate keeps the same expectation with a **tighter** CI. It is the linear special case of
regression adjustment / DML (see paper-library/notation/dml.md), and buys power for free.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW

from inference.base import Effect, user_pre_post


def adjust(df: pd.DataFrame, outcome: str = "post", covariate: str = "pre") -> pd.DataFrame:
    """Return ``df`` with a CUPED-adjusted outcome column ``y_cuped`` (θ from the pooled data)."""
    y = df[outcome].to_numpy(float)
    x = df[covariate].to_numpy(float)
    var_x = x.var(ddof=1)
    theta = float(np.cov(y, x, ddof=1)[0, 1] / var_x) if var_x > 0 else 0.0
    out = df.copy()
    out["y_cuped"] = y - theta * (x - x.mean())
    out.attrs["theta"] = theta
    out.attrs["rho"] = float(np.corrcoef(y, x)[0, 1]) if var_x > 0 else 0.0
    return out


def estimate(df: pd.DataFrame, alpha: float = 0.05,
             outcome: str = "post", covariate: str = "pre") -> Effect:
    """CUPED-adjusted difference-in-means (treatment − control); holdout excluded."""
    adj = adjust(df[df["arm"].isin(["treatment", "control"])], outcome, covariate)
    treat = adj.loc[adj["arm"] == "treatment", "y_cuped"].to_numpy(float)
    control = adj.loc[adj["arm"] == "control", "y_cuped"].to_numpy(float)
    if treat.size == 0 or control.size == 0:
        raise ValueError("cuped.estimate: need both treatment and control users")

    cm = CompareMeans(DescrStatsW(treat), DescrStatsW(control))
    point = float(treat.mean() - control.mean())
    lo, hi = cm.tconfint_diff(alpha=alpha, usevar="unequal")
    _, pval, _ = cm.ttest_ind(usevar="unequal")
    return Effect(
        estimator="cuped",
        point=point,
        ci_low=float(lo),
        ci_high=float(hi),
        se=float(cm.std_meandiff_separatevar),
        n_treatment=int(treat.size),
        n_control=int(control.size),
        p_value=float(pval),
        extra={"theta": adj.attrs["theta"], "rho": adj.attrs["rho"]},
    )


def estimate_from_log(events_dir, experiment_id: str, split_day: int, alpha: float = 0.05) -> Effect:
    return estimate(user_pre_post(events_dir, experiment_id, split_day), alpha=alpha)
