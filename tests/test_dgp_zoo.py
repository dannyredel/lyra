"""Recovery tests for the promoted DGP zoo (LYRA §10 — the harness is the gate).

Each randomized outcome world must let difference-in-means *recover its authored truth* with ~nominal
coverage. The panel is the deliberate counter-example: naive diff is biased (→ DiD, NB 11).
"""

import pytest

from lyra.dgp import (BinaryDGP, CountDGP, FunnelDGP, RatioDGP, RevenueDGP,
                      StaggeredPanelDGP, SurvivalDGP)
from lyra.estimators import DiffInMeans
from lyra.harness import harness

RECOVERABLE = [BinaryDGP(), CountDGP(), RevenueDGP(), SurvivalDGP(), FunnelDGP()]


@pytest.mark.parametrize("dgp", RECOVERABLE, ids=lambda d: d.name)
def test_diff_in_means_recovers_truth(dgp):
    """Under randomization, diff-in-means is unbiased for the ATE of every outcome type, ~95% coverage.

    Coverage is the recovery criterion; the bias is checked against its own Monte-Carlo SE
    (≈ rmse/√R) so the heavy-tailed worlds (revenue, funnel) don't flake.
    """
    R, n = 120, 25000
    r = harness(DiffInMeans(), dgp, R=R, n=n)
    mc_se = r["rmse"] / R ** 0.5
    assert abs(r["bias"]) < 4 * mc_se, r          # within 4 Monte-Carlo SEs of zero
    assert r["coverage"] >= 0.88, r               # CIs cover the known truth at ~nominal rate


def test_ratio_pooled_recovers_per_session_rate():
    """The per-user ratio metric: the pooled ratio recovers the authored per-session conversion lift."""
    dgp = RatioDGP(dcr=0.02)
    df = dgp.sample(60_000, seed=0)
    pooled = lambda d: d.conversions.sum() / d.sessions.sum()
    est = pooled(df[df.treat == 1]) - pooled(df[df.treat == 0])
    assert abs(est - dgp.ground_truth().ate) < 0.004


def test_panel_naive_is_biased():
    """Staggered panel: ATT is known, but naive last-period diff is biased up (selection + trend) → DiD."""
    dgp = StaggeredPanelDGP(att=1.0)
    df = dgp.sample(5000, seed=0)
    last = df[df.period == df.period.max()]
    naive = last[last.treated_group == 1].y.mean() - last[last.treated_group == 0].y.mean()
    assert dgp.ground_truth().ate == 1.0
    assert naive > 1.3            # demonstrably inflated — the case for difference-in-differences


def test_binary_ate_is_risk_difference_not_logit_coef():
    """Sanity: the authored ATE is the risk difference E[p1-p0], not the logit coefficient beta."""
    dgp = BinaryDGP(beta=0.5)
    assert 0.0 < dgp.ground_truth().ate < 0.5          # risk diff, well below beta=0.5
