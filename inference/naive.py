"""Naive user-level estimator — the biased baseline we deliberately expose.

Responsibility (T-30): user-level difference-in-means + a fixed-horizon CI, treating units as
independent. This is what a typical team runs. Under marketplace interference it is BIASED, and
``tests/test_naive_bias.py`` asserts that bias as a measured quantity (not just a chart). Its drift
as treated ``allocation`` grows is the money-shot panel (paired against the corrected estimators).

Feeds: ramp/interference-decay diagnostic.

We use ``statsmodels`` for the two-sample contrast (STACK.md: don't hand-roll the SEs) — Welch
(unequal-variance) by default, since arms can differ in size and variance under a ramp.
"""

from __future__ import annotations

import pandas as pd
from statsmodels.stats.weightstats import CompareMeans, DescrStatsW

from inference.base import Effect, user_outcomes


def estimate(df: pd.DataFrame, alpha: float = 0.05) -> Effect:
    """Difference-in-means (treatment − control) on per-user ``outcome``; holdout excluded.

    The estimand it *targets* is the global ATE, but under interference its probability limit is
    the contaminated arm-contrast — that gap is the bias the project measures.
    """
    treat = df.loc[df["arm"] == "treatment", "outcome"].to_numpy(dtype=float)
    control = df.loc[df["arm"] == "control", "outcome"].to_numpy(dtype=float)
    if treat.size == 0 or control.size == 0:
        raise ValueError("naive.estimate: need both treatment and control users")

    cm = CompareMeans(DescrStatsW(treat), DescrStatsW(control))
    point = float(treat.mean() - control.mean())
    lo, hi = cm.tconfint_diff(alpha=alpha, usevar="unequal")
    tstat, pval, _ = cm.ttest_ind(usevar="unequal")
    se = float(cm.std_meandiff_separatevar)

    return Effect(
        estimator="naive",
        point=point,
        ci_low=float(lo),
        ci_high=float(hi),
        se=se,
        n_treatment=int(treat.size),
        n_control=int(control.size),
        p_value=float(pval),
    )


def estimate_from_log(events_dir, experiment_id: str, alpha: float = 0.05) -> Effect:
    """Convenience: load the per-user table for ``experiment_id`` and estimate."""
    return estimate(user_outcomes(events_dir, experiment_id), alpha=alpha)
