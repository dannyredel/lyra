"""Anytime-valid confidence-sequence tests (T-41).

Two properties:
1. **Coverage** — at the final sample size the CS covers the true ATE (on the unbiased budget-split
   design), and it is always *wider* than the fixed-horizon CI (the price of peeking).
2. **Always-valid under peeking** — on an A/A null (no effect), the time-uniform CS covers zero at
   *every* day. A fixed-horizon test peeked daily would inflate Type-I toward 1; the CS does not.
"""

from __future__ import annotations

from inference import anytime_valid, naive
from inference.base import user_outcomes


def test_cs_covers_truth_and_is_wider_than_fixed(iso):
    """CS on the budget-split design covers the ATE, and is wider than the naive fixed-horizon CI."""
    ate = iso.gt.ate
    df = user_outcomes(iso.runs["bsplit_hi"], iso.exp)
    cs = anytime_valid.estimate(df)
    fixed = naive.estimate(df)
    assert cs.covers(ate), f"CS [{cs.ci_low:.4f}, {cs.ci_high:.4f}] failed to cover ATE {ate:.4f}"
    # same point, strictly wider interval (anytime-valid multiplier > z_{1-α/2})
    assert abs(cs.point - fixed.point) < 1e-9
    assert (cs.ci_high - cs.ci_low) > (fixed.ci_high - fixed.ci_low)
    assert cs.extra["cs_multiplier"] > 1.959964


def test_cs_never_flags_aa_under_daily_peeking(aa):
    """The A/A confidence sequence must cover zero at EVERY day (safe to peek daily)."""
    seq = anytime_valid.sequence_from_log(aa.events_dir, "aa_null_1", horizon=10)
    assert len(seq) >= 3, "expected a multi-day sequence"
    bad = [p for p in seq if not (p["ci_low"] <= 0 <= p["ci_high"])]
    assert not bad, f"CS excluded zero on an A/A at days {[p['day'] for p in bad]} (false positive)"
