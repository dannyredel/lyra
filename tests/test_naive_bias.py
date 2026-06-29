"""Naive-bias test — the bias is a measured, ASSERTED quantity, not just a chart.

Run the simulator under interference, estimate with the naive user-level estimator, and assert its
point estimate is biased away from the global ATE by a detectable margin — and that the bias GROWS
with treated ``allocation`` (the ramp/interference-decay signature). Pair with the corrected
estimator staying on the truth line (test_recovery). (T-30; PROPOSAL §7.)

Ground truth is the global ATE from counterfactual shadow runs (``engine.oracle``), not the
per-conversion local tau — the estimand the naive arm-contrast *should* recover but cannot under
interference.
"""

from __future__ import annotations

from inference import naive


def test_naive_is_biased_under_interference(iso):
    """At 50% allocation the naive CI must EXCLUDE the true ATE — the bias is real, not noise."""
    ate = iso.gt.ate
    eff = naive.estimate_from_log(iso.runs["std_hi"], iso.exp)
    assert not eff.covers(ate), (
        f"naive CI [{eff.ci_low:.4f}, {eff.ci_high:.4f}] unexpectedly covers ATE {ate:.4f} — "
        "interference bias not detected"
    )
    # biased toward zero (understates the treatment's harm under budget cannibalization)
    assert abs(eff.point) < abs(ate)


def test_naive_bias_grows_with_allocation(iso):
    """The interference signature: |naive − ATE| is larger at 50% than at 10% allocation."""
    ate = iso.gt.ate
    bias_lo = abs(naive.estimate_from_log(iso.runs["std_lo"], iso.exp).point - ate)
    bias_hi = abs(naive.estimate_from_log(iso.runs["std_hi"], iso.exp).point - ate)
    assert bias_hi > bias_lo, f"bias did not grow with allocation: lo={bias_lo:.4f} hi={bias_hi:.4f}"
