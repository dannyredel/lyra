"""Recovery test — the corrected design/estimator covers ground truth where naive does not.

Run the simulator with a known global ATE (counterfactual shadow runs), estimate under the
budget-split design, and assert the interval covers truth at the nominal coverage
(``inference.alpha``). Reads truth via the oracle path only. This test suite IS the causal
credibility, automated. (T-31/T-32; EVENT_LOG §4.)

Regime: the single-advertiser isolated world where budget cannibalization is the only interference
channel, so the budget-split design recovers the ATE exactly. (In the full multi-advertiser market
a second channel — cross-advertiser effort substitution — leaves a residual; that's a Phase-2 story,
not a unit-test target.)
"""

from __future__ import annotations

from inference import budget_split, naive


def test_budget_split_recovers_ground_truth(iso):
    """Budget-split design at 50% allocation: the CI must COVER the true global ATE."""
    ate = iso.gt.ate
    eff = budget_split.estimate_from_log(iso.runs["bsplit_hi"], iso.exp)
    assert eff.covers(ate), (
        f"budget_split CI [{eff.ci_low:.4f}, {eff.ci_high:.4f}] failed to cover ATE {ate:.4f}"
    )


def test_budget_split_beats_naive(iso):
    """The correction must be a strict improvement: |bias_bsplit| < |bias_naive| at 50% allocation."""
    ate = iso.gt.ate
    bias_naive = abs(naive.estimate_from_log(iso.runs["std_hi"], iso.exp).point - ate)
    bias_bs = abs(budget_split.estimate_from_log(iso.runs["bsplit_hi"], iso.exp).point - ate)
    assert bias_bs < bias_naive, f"budget_split ({bias_bs:.4f}) did not beat naive ({bias_naive:.4f})"
