"""Chassis tests — assignment, the lifecycle state machine, the power-gate, and the scorecard's
state-gated readout + ground-truth certification (the platform's correctness guarantees)."""

import pytest

from chassis.assignment import assign
from chassis.power import power_gate
from chassis.scorecard import compute
from chassis.seed import build

SALT, ALLOC = "salt", {"control": 0.5, "treatment": 0.5}


def test_assignment_deterministic_balanced_salt_independent():
    v = [assign(f"u{i}", SALT, ALLOC) for i in range(4000)]
    assert assign("u1", SALT, ALLOC) == assign("u1", SALT, ALLOC)                 # deterministic
    assert 0.46 < sum(x == "treatment" for x in v) / len(v) < 0.54                # ~balanced
    v2 = [assign(f"u{i}", "other_salt", ALLOC) for i in range(4000)]
    assert sum(a != b for a, b in zip(v, v2)) > 1000                              # salted per experiment


def test_state_machine_rejects_illegal_transition():
    reg, _ = build()
    with pytest.raises(ValueError):
        reg.transition("exp_reward_a", "DECIDED")                                # RUNNING→DECIDED illegal
    reg.transition("exp_reward_a", "STOPPED")
    assert reg.get("exp_reward_a").state == "STOPPED"


def test_power_gate_flags_underpowered():
    g = power_gate(mu=0.40, rel_mde=0.03, sigma2=0.0, available_n=4000, binary=True)
    assert not g["powered"] and g["verdict"] == "UNDERPOWERED"


def test_scorecard_aa_does_not_flag_and_is_certified():
    reg, worlds = build()
    sc = compute(reg.get("exp_checkout_aa"), *worlds["exp_checkout_aa"][:2],
                 worlds["exp_checkout_aa"][2], harness_R=140)
    assert sc["readout"]["headline_state"] == "no_change"        # A/A must not flag
    assert sc["truth"]["covered"] and sc["truth"]["certified"]   # CI covers truth=0; harness certifies
    assert sc["diagnostics"]["aa_ok"]


def test_scorecard_real_effect_flags_green_and_covers_truth():
    reg, worlds = build()
    sc = compute(reg.get("exp_reward_a"), *worlds["exp_reward_a"][:2],
                 worlds["exp_reward_a"][2], harness_R=140)
    assert sc["readout"]["ci_color"] == "green"                  # detected positive effect
    assert sc["truth"]["covered"] and sc["truth"]["certified"]
