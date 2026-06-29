"""Switchback tests (LYRA §10) — temporal interference handled: a cluster-robust OLS recovers the
switchback ATE, and the CUPED variant keeps coverage while cutting the interval (variance reduction)."""

from lyra.dgp import SwitchbackDGP
from lyra.estimators_vr import SwitchbackCUPED
from lyra.harness import harness
from lyra.se import ClusterOLS


def test_cluster_robust_recovers_switchback_ate():
    rep = harness(ClusterOLS("CV1", x="treat", cluster="cluster"), SwitchbackDGP(), R=100)
    assert abs(rep["bias"]) < 0.35 * SwitchbackDGP().ground_truth().ate     # unbiased (noisy: 90% residual)
    assert rep["coverage"] >= 0.88                                          # cluster-robust CI covers τ


def test_cuped_reduces_variance_without_bias():
    raw = harness(ClusterOLS("CV1", x="treat", cluster="cluster"), SwitchbackDGP(), R=100)
    cup = harness(SwitchbackCUPED(), SwitchbackDGP(), R=100)
    assert cup["coverage"] >= 0.88                                          # still covers τ (unbiased)
    assert cup["ci_width"] < 0.85 * raw["ci_width"]                         # CUPED tightens the interval


def test_tuned_switchback_detects_and_certifies():
    dgp = SwitchbackDGP(J=55, H=22, n_bar=20, tau=70, tau_sd=15, sigma_total=320, cv=0.6)
    rep = harness(SwitchbackCUPED(), dgp, R=100)
    assert rep["reject_rate"] > 0.7 and rep["coverage"] >= 0.88             # detects the effect, certified
