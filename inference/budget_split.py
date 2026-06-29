"""Budget-split estimator — the fix for auction/budget interference.

Responsibility (T-32): analyze the reward-sizing experiment under a budget-split design, where the
shared advertiser budget is split so treatment and control don't compete for the same finite pool
(removing budget cannibalization). The corrected counterpart to naive on Game A.

Ref: LinkedIn "Trustworthy Online Marketplace Experimentation with Budget-split Design" (Liu et al.).
Also informs Phase-3 Trivago. Recovery test: covers ground truth as treated allocation grows.

The estimator itself is a plain difference-in-means — the *design* (separate per-arm budget pools,
``engine`` ``budget_split``) is what makes it unbiased. Each arm faces the per-user scarcity it
would face in its own all-arm world, so the contrast equals the global ATE. Running this estimator
on a *standard*-design log would inherit the naive bias: the correction lives in how the data was
generated, which is the whole point.
"""

from __future__ import annotations

import pandas as pd
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW

from inference.base import Effect, user_outcomes


def estimate(df: pd.DataFrame, alpha: float = 0.05) -> Effect:
    """Difference-in-means on per-user ``outcome`` (valid on budget-split-design data)."""
    treat = df.loc[df["arm"] == "treatment", "outcome"].to_numpy(dtype=float)
    control = df.loc[df["arm"] == "control", "outcome"].to_numpy(dtype=float)
    if treat.size == 0 or control.size == 0:
        raise ValueError("budget_split.estimate: need both treatment and control users")

    cm = CompareMeans(DescrStatsW(treat), DescrStatsW(control))
    point = float(treat.mean() - control.mean())
    lo, hi = cm.tconfint_diff(alpha=alpha, usevar="unequal")
    _, pval, _ = cm.ttest_ind(usevar="unequal")
    return Effect(
        estimator="budget_split",
        point=point,
        ci_low=float(lo),
        ci_high=float(hi),
        se=float(cm.std_meandiff_separatevar),
        n_treatment=int(treat.size),
        n_control=int(control.size),
        p_value=float(pval),
    )


def estimate_from_log(events_dir, experiment_id: str, alpha: float = 0.05) -> Effect:
    return estimate(user_outcomes(events_dir, experiment_id), alpha=alpha)
