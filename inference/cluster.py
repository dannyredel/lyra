"""Cluster-robust estimator — aggregate to the randomization unit before testing.

Responsibility (T-31): when assignment is at ``cluster_id``, compute the effect and SEs at the
cluster level (``inference.cluster.unit``). Randomizing at cluster level but testing at user level
massively overstates precision (inflated type-I) — the Glovo lesson. This is a canonical correction
for the attention/interference bias the naive estimator suffers.

Ref: Glovo cluster-randomization (Clavijo & Toce 2022). Recovery test: covers ground truth at
nominal rate where naive does not.

What it fixes (and what it doesn't): the **standard error**. For a cluster-randomized A/A, the
user-level naive SE is far too small (users within a cluster are correlated and share an arm), so it
flags false positives; cluster-robust SEs (CRV1) restore the nominal Type-I rate. It does *not*
remove the point-estimate bias from budget cannibalization — that needs a design change
(``budget_split``), since the bias is cross-arm interference, not a variance artefact.

Implementation: OLS ``outcome ~ treat`` at the user level with cluster-robust covariance clustered
on ``cluster_id`` (statsmodels ``cov_type="cluster"``) — STACK.md: use the library's SEs.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from inference.base import Effect, user_outcomes


def estimate(df: pd.DataFrame, alpha: float = 0.05) -> Effect:
    """Diff-in-means with cluster-robust SEs clustered on ``cluster_id`` (holdout excluded)."""
    d = df[df["arm"].isin(["treatment", "control"])].copy()
    if d.empty or d["arm"].nunique() < 2:
        raise ValueError("cluster.estimate: need both treatment and control users")
    d["treat"] = (d["arm"] == "treatment").astype(int)

    model = smf.ols("outcome ~ treat", data=d).fit(
        cov_type="cluster", cov_kwds={"groups": d["cluster_id"]}
    )
    point = float(model.params["treat"])
    se = float(model.bse["treat"])
    lo, hi = model.conf_int(alpha=alpha).loc["treat"].tolist()
    n_t = int(d["treat"].sum())
    n_c = int((1 - d["treat"]).sum())
    return Effect(
        estimator="cluster",
        point=point,
        ci_low=float(lo),
        ci_high=float(hi),
        se=se,
        n_treatment=n_t,
        n_control=n_c,
        p_value=float(model.pvalues["treat"]),
        extra={"n_clusters": int(d["cluster_id"].nunique())},
    )


def estimate_from_log(events_dir, experiment_id: str, alpha: float = 0.05) -> Effect:
    return estimate(user_outcomes(events_dir, experiment_id), alpha=alpha)
