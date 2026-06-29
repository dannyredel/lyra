"""A/A null test — false-positive control + SRM.

The A/A experiments (``aa_null_1`` user-randomized, ``aa_null_2`` cluster-randomized) must NOT
flag a significant effect, and realized arm shares must match the intended ``allocation`` within
sampling tolerance (SRM — EVENT_LOG §6.6). (T-33.)

These are single-seed guards (the arms are identical — no lever — so there is no effect to find).
A fuller false-positive-*rate* test would loop over many seeds and assert the flag rate ≈ α; that
multi-seed version is a cheap extension but kept out of the default suite for runtime.
"""

from __future__ import annotations

from inference import cluster, naive

ALPHA = 0.05


def test_user_aa_does_not_flag(aa):
    """User-randomized A/A: naive must not find a significant effect (p > α)."""
    eff = naive.estimate_from_log(aa.events_dir, "aa_null_1", alpha=ALPHA)
    assert eff.p_value > ALPHA, f"user A/A falsely flagged: p={eff.p_value:.4f}, effect={eff.point:.5f}"
    assert eff.covers(0.0), "user A/A interval should cover zero effect"


def test_cluster_aa_does_not_flag(aa):
    """Cluster-randomized A/A: cluster-robust SEs must not flag (the Glovo over-precision fix)."""
    eff = cluster.estimate_from_log(aa.events_dir, "aa_null_2", alpha=ALPHA)
    assert eff.p_value > ALPHA, (
        f"cluster A/A falsely flagged: p={eff.p_value:.4f}, effect={eff.point:.5f}"
    )
    assert eff.covers(0.0), "cluster A/A interval should cover zero effect"


def test_srm_within_tolerance(aa):
    """Realized arm shares for the A/A nulls match the intended 50/50 within tolerance (EVENT_LOG §6.6)."""
    srm = aa.summary["srm"]
    for exp_id in ("aa_null_1", "aa_null_2"):
        rep = srm[exp_id]
        assert not rep["ramped"], f"{exp_id} should be constant-allocation"
        assert rep["ok"], (
            f"SRM flagged {exp_id}: realized={rep['realized_share']:.3f} "
            f"intended={rep['intended_share']:.3f}"
        )
