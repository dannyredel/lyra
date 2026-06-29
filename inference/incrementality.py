"""Incrementality — ghost-ads / PSA-holdout lift on advertiser conversions.

Responsibility (T-43): estimate the causal lift of the reward by comparing ``treatment`` to
``holdout`` — the ghost-ads counterfactual where the reward is withheld (``reward_shown = 0``) but
the user can still complete the offer **organically** (D-14). Answers "does the reward CAUSE
conversions, or just capture users who'd convert anyway?"

The lift is a difference-in-means of **conversions per user** between the treatment arm (reward
served) and the holdout arm (reward withheld):
$$\\widehat{\\text{lift}} = \\bar n^{\\text{conv}}_{\\text{treatment}} - \\bar n^{\\text{conv}}_{\\text{holdout}}.$$
A positive, significant lift means the reward is incremental; a lift near zero would mean those
conversions would have happened anyway (the Lewis–Rao "unfavorable economics" warning).

Ref: Johnson, Lewis & Nubbemeyer "Ghost Ads" (JMR 2017); Lewis & Rao (QJE 2015) — incrementality is
hard even at scale, which is exactly why a ground-truth sim is valuable. The same estimator runs on
the real Criteo Uplift data in ``validation/criteo.py``.
"""

from __future__ import annotations

import pandas as pd
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW

from inference.base import Effect, user_outcomes


def estimate(df: pd.DataFrame, alpha: float = 0.05, outcome: str = "n_conv") -> Effect:
    """Treatment-vs-holdout difference in ``outcome`` (default: conversions per user)."""
    treat = df.loc[df["arm"] == "treatment", outcome].to_numpy(dtype=float)
    holdout = df.loc[df["arm"] == "holdout", outcome].to_numpy(dtype=float)
    if treat.size == 0 or holdout.size == 0:
        raise ValueError("incrementality.estimate: need both treatment and holdout users "
                         "(enable experiments.incrementality.holdout_share)")

    cm = CompareMeans(DescrStatsW(treat), DescrStatsW(holdout))
    point = float(treat.mean() - holdout.mean())
    lo, hi = cm.tconfint_diff(alpha=alpha, usevar="unequal")
    _, pval, _ = cm.ttest_ind(usevar="unequal")
    return Effect(
        estimator="incrementality",
        point=point,
        ci_low=float(lo),
        ci_high=float(hi),
        se=float(cm.std_meandiff_separatevar),
        n_treatment=int(treat.size),
        n_control=int(holdout.size),     # n_control field holds the holdout count here
        p_value=float(pval),
        extra={"baseline_holdout": float(holdout.mean()),
               "treatment_rate": float(treat.mean())},
    )


def estimate_from_log(events_dir, experiment_id: str, alpha: float = 0.05) -> Effect:
    return estimate(user_outcomes(events_dir, experiment_id), alpha=alpha)
