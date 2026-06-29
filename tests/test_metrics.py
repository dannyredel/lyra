"""Tests for the typed metric layer (LYRA §4/§10).

The harness gate again: each metric type must (a) recover its world's truth with ~nominal coverage,
and (b) pass A/A (no false effect under the null). The headline asserted fact: the **delta method**
covers a clustered ratio while the **naive** session-iid variance under-covers AND over-flags A/A.
"""

import pytest

from lyra.dgp import BinaryDGP, PrePostDGP, RatioDGP
from lyra.harness import harness
from lyra.metrics import (CupedMetric, MeanMetric, MetricSpec, NaiveRatioMetric,
                          ProportionMetric, RatioMetric, estimator_for)


def test_proportion_recovers_risk_difference():
    r = harness(ProportionMetric(), BinaryDGP(), R=200, n=8000)
    assert abs(r["bias"]) < 0.004 and r["coverage"] >= 0.9, r


def test_delta_ratio_covers_clustered_but_naive_undercovers():
    """The headline: under user heterogeneity, delta covers ~95% while naive (session-iid) collapses."""
    dgp = RatioDGP(dcr=0.02, user_sigma=0.20)
    delta = harness(RatioMetric(), dgp, R=300, n=4000)
    naive = harness(NaiveRatioMetric(), dgp, R=300, n=4000)
    assert abs(delta["bias"]) < 0.004 and abs(naive["bias"]) < 0.004      # same point...
    assert delta["coverage"] >= 0.90                                      # ...right variance
    assert naive["coverage"] < 0.85                                       # ...wrong variance under-covers
    assert naive["ci_width"] < delta["ci_width"]                          # naive CI is too narrow


def test_cuped_reduces_variance_without_bias():
    dgp = PrePostDGP(ate=0.3, rho=0.7)
    plain = harness(MeanMetric(), dgp, R=300, n=3000)
    cuped = harness(CupedMetric(), dgp, R=300, n=3000)
    assert abs(cuped["bias"]) < 0.02 and cuped["coverage"] >= 0.9
    assert cuped["ci_width"] < 0.8 * plain["ci_width"]                    # ~1-rho^2 = 0.51 reduction


def test_aa_gate_naive_ratio_over_flags():
    """A/A (effect off): trustworthy metrics flag ~5%; the broken naive ratio over-flags."""
    null = RatioDGP(dcr=0.0, user_sigma=0.20)
    assert harness(RatioMetric(), null, R=400, n=4000)["reject_rate"] < 0.09
    assert harness(NaiveRatioMetric(), null, R=400, n=4000)["reject_rate"] > 0.12
    assert harness(ProportionMetric(), BinaryDGP(beta=0.0), R=400, n=6000)["reject_rate"] < 0.09


def test_registry_routes_type_to_estimator():
    assert isinstance(estimator_for(MetricSpec("cvr", 1, "proportion", "primary")), ProportionMetric)
    assert isinstance(estimator_for(MetricSpec("gmv_ps", 1, "ratio", "primary")), RatioMetric)
