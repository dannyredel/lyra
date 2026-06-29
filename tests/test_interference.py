"""Interference tests (LYRA §10) — the marketplace money-shot as asserted facts:
the naive user-level A/B is biased for the global effect (CI never covers truth), while cluster
randomization recovers it (~nominal coverage). The platform's certify step is what distinguishes them.
"""

from lyra.dgp import InterferenceDGP
from lyra.estimators import DiffInMeans
from lyra.harness import harness
from lyra.se import ClusterOLS


def test_naive_user_ab_is_biased_and_uncertified():
    """Under cannibalization the naive A/B over-states the global effect; its CI never covers truth."""
    rep = harness(DiffInMeans(), InterferenceDGP(design="user"), R=120, n=12000)
    assert rep["bias"] > 0.1                      # large positive bias (over-states the global lift)
    assert rep["coverage"] < 0.2                  # CI essentially never covers the truth → uncertified


def test_cluster_randomization_recovers_global_effect():
    rep = harness(ClusterOLS("CV1"), InterferenceDGP(design="cluster"), R=150, n=12000)
    assert abs(rep["bias"]) < 0.02                # recovers the global effect
    assert rep["coverage"] >= 0.88                # cluster-robust CI covers truth → certified


def test_global_truth_is_positive_but_small():
    """The true global effect is real but far below the naive uplift (cannibalization eats most of it)."""
    tau = InterferenceDGP().ground_truth().ate
    assert 0.02 < tau < 0.2
