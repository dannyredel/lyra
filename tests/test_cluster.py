"""Cluster-robust SE test (B-06 / T-31, the Glovo lesson).

With a per-cluster random effect in the engine (``agents.cluster_effect_sigma``), users in the same
cluster have correlated outcomes (ICC > 0). For a **cluster-randomized** experiment, analyzing at the
user level then *overstates precision* — the naive SE is too small — and cluster-robust SEs correct
it. (For a *user*-randomized design the effect cancels across balanced arms, so the naive SE is fine;
this is exactly the asymmetry the lesson is about.)
"""

from __future__ import annotations

from inference import cluster, naive
from inference.base import user_outcomes


def test_cluster_robust_se_corrects_understatement(aa):
    """Cluster-randomized A/A: cluster-robust SE is meaningfully larger than the naive (user) SE."""
    df = user_outcomes(aa.events_dir, "aa_null_2")          # cluster-randomized
    en = naive.estimate(df)
    ec = cluster.estimate(df)
    assert ec.extra["n_clusters"] >= 30
    # ICC>0 ⇒ the honest (cluster-robust) SE exceeds the over-precise naive SE
    assert ec.se > 1.15 * en.se, (
        f"cluster-robust SE {ec.se:.5f} not inflated over naive {en.se:.5f} "
        f"(ratio {ec.se / en.se:.2f}) — is agents.cluster_effect_sigma > 0?"
    )
    # and it still correctly covers the (zero) A/A effect
    assert ec.covers(0.0)


def test_user_randomized_se_not_inflated(aa):
    """Sanity: for a USER-randomized A/A the cluster effect cancels, so naive ≈ cluster-robust SE."""
    df = user_outcomes(aa.events_dir, "aa_null_1")          # user-randomized
    en = naive.estimate(df)
    ec = cluster.estimate(df)
    assert ec.se < 1.15 * en.se, (
        f"user-randomized SEs should agree, got cluster {ec.se:.5f} vs naive {en.se:.5f}"
    )
