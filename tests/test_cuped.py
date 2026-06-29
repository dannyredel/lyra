"""CUPED variance-reduction test (T-42).

CUPED regresses the outcome on a pre-treatment covariate (warmup-period margin). Because the
covariate is pre-treatment it leaves the effect's expectation unchanged but **reduces variance** by
~$1-\\rho^2$. So the test asserts: the CUPED standard error is strictly smaller than the unadjusted
(naive) standard error on the same data, and the covariate is informative ($\\rho>0$).
"""

from __future__ import annotations

from inference import cuped as cuped_est
from inference import naive
from inference.base import user_pre_post


def test_cuped_reduces_variance(cuped):
    df = user_pre_post(cuped.events_dir, cuped.exp, cuped.split)
    naive_post = naive.estimate(df.rename(columns={"post": "outcome"}))
    cu = cuped_est.estimate(df, outcome="post", covariate="pre")

    assert cu.extra["rho"] > 0.05, f"pre-period covariate not informative (rho={cu.extra['rho']:.3f})"
    assert cu.se < naive_post.se, (
        f"CUPED SE {cu.se:.5f} not below naive SE {naive_post.se:.5f}"
    )
    # unbiased: the adjusted point stays close to the unadjusted one (no systematic shift)
    assert abs(cu.point - naive_post.point) < 2.5 * naive_post.se
