"""Incrementality (ghost-ads holdout) test (T-43).

The holdout arm has the reward withheld (reward_shown=0) but can convert organically (D-14). The
incremental lift = treatment − holdout on conversions per user must be **positive and significant**
(the reward causes completions), and the holdout's organic conversion rate must sit **below** the
treatment rate.
"""

from __future__ import annotations

from inference import incrementality
from inference.base import user_outcomes


def test_reward_has_positive_incremental_lift(incr):
    df = user_outcomes(incr.events_dir, incr.exp)
    assert (df["arm"] == "holdout").sum() > 50, "need a populated holdout arm"

    lift = incrementality.estimate(df)            # treatment vs holdout on n_conv
    assert lift.point > 0, f"incremental lift not positive: {lift.point:.4f}"
    assert not lift.covers(0.0), f"lift CI [{lift.ci_low:.4f}, {lift.ci_high:.4f}] covers zero"
    # holdout (reward withheld) converts less than treatment (reward served)
    assert lift.extra["baseline_holdout"] < lift.extra["treatment_rate"]


def test_holdout_conversions_carry_no_reward(incr):
    """Ghost-ads invariant (EVENT_LOG §6.5 revised): holdout conversions serve reward_shown=0."""
    import duckdb

    glob = f"{incr.events_dir}/day=*/events.parquet".replace("\\", "/")
    con = duckdb.connect()
    bad = con.execute(
        f"""select count(*) from read_parquet('{glob}')
            where event_type='conversion' and variant='holdout' and reward_shown != 0"""
    ).fetchone()[0]
    con.close()
    assert bad == 0, f"{bad} holdout conversions served a non-zero reward"
