"""Cluster-robust SE tests (LYRA §10). The harness certifies *size* (rejection of a true null) against
``ClusteredDGP`` (truth beta=0): naive iid is broken everywhere; CV1 works at large G but over-rejects at
small G; CV3 and the wild cluster bootstrap restore size; CV1/CV3 collapse to HC1/HC3 at G=N.
"""

import numpy as np
import statsmodels.api as sm

from lyra.dgp import ClusteredDGP
from lyra.harness import harness
from lyra.se import ClusterOLS, se_cv1, se_cv3, wild_cluster_bootstrap


def _size(vcov, G, n_g=10, R=300):
    return harness(ClusterOLS(vcov), ClusteredDGP(G=G, n_g=n_g, beta=0.0), R=R)["reject_rate"]


def test_naive_iid_under_covers():
    """Naive iid SE rejects a true null far above 5% under clustering (the catastrophe)."""
    assert _size("iid", G=50) > 0.20


def test_cv1_correct_at_large_G():
    assert _size("CV1", G=60) < 0.10


def test_cv1_over_rejects_but_cv3_fixes_small_G():
    """The few-clusters problem: CV1 over-rejects at small G; the CV3 jackknife restores ~5%."""
    assert _size("CV1", G=6, n_g=8) > 0.10
    assert _size("CV3", G=6, n_g=8) < 0.09


def test_wild_cluster_bootstrap_restores_size_small_G():
    dgp = ClusteredDGP(G=6, n_g=8, beta=0.0)
    size = np.mean([wild_cluster_bootstrap(dgp.sample(seed=r), B=199, seed=9000 + r) < 0.05
                    for r in range(150)])
    assert size < 0.10


def test_cluster_se_reduces_to_HC_at_G_equals_N():
    """G=N (each obs its own cluster): CV1==HC1 *exactly*; CV3 ≈ HC3 (jackknife is approximate-HC3)."""
    df = ClusteredDGP(G=80, n_g=1, beta=0.4).sample(seed=3)      # n_g=1 ⇒ one obs per cluster ⇒ G=N
    fit = lambda hc: sm.OLS(df.y.to_numpy(), sm.add_constant(df.x.to_numpy())).fit(cov_type=hc).bse[1]
    assert abs(se_cv1(df)[1] - fit("HC1")) < 1e-7                     # CV1 = HC1 algebraically
    assert abs(se_cv3(df)[1] - fit("HC3")) / fit("HC3") < 0.03        # CV3 ≈ HC3 (leave-one-out jackknife)
