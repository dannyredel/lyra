"""Power & decisions tests (LYRA §10) — the bookends: the SSC sample size lands on ~80% simulated power,
and the ship rule is a conjunction (a guardrail regression blocks the ship even when the primary wins)."""

import math

import numpy as np

from lyra.decisions import ship_decision
from lyra.power import mde, required_n
from lyra.power import test_and_roll_size as _tr_size   # aliased: avoid pytest collecting it as a test


def _sim_power(n_per_arm, p0, delta, R=2500, seed0=0):
    rng = np.random.default_rng(seed0); rej = 0
    for _ in range(R):
        c, t = rng.binomial(n_per_arm, p0), rng.binomial(n_per_arm, p0 + delta)
        p0h, p1h = c / n_per_arm, t / n_per_arm
        se = math.sqrt(p0h * (1 - p0h) / n_per_arm + p1h * (1 - p1h) / n_per_arm)
        rej += (se > 0 and abs(p1h - p0h) / se > 1.959964)
    return rej / R


def test_required_n_lands_on_nominal_power():
    out = required_n(0.20, 0.05, sigma2=0.0, binary=True)            # MDE = 0.01 abs
    pw = _sim_power(out["n_per_arm"], 0.20, 0.20 * 0.05)
    assert 0.74 < pw < 0.86                                          # closed-form N ≈ 80% simulated power


def test_mde_inverts_required_n():
    out = required_n(0.20, 0.05, sigma2=0.0, binary=True)
    back = mde(out["n_total"], 0.20, 0.0, binary=True)
    assert abs(back["rel_mde"] - 0.05) < 0.003                       # round-trips


def test_corrections_inflate_n():
    base = required_n(0.20, 0.05, sigma2=0.0, binary=True)["n_total"]
    more = required_n(0.20, 0.05, sigma2=0.0, binary=True, n_success=2, n_guardrail_nim=4)["n_total"]
    assert more > base                                               # multiple-testing + guardrail power cost N


def test_ship_rule_is_a_conjunction():
    win = {"ci_low": 0.012, "ci_high": 0.028, "direction": "up", "effect": 0.02}
    clean = [{"name": "latency", "ci_low": -0.01, "ci_high": 0.02, "margin": 0.03}]
    regressed = [{"name": "gross margin", "ci_low": -0.09, "ci_high": -0.03, "margin": 0.03}]
    assert ship_decision(win, clean)["ship"] is True                # primary wins + guardrail ok → ship
    bad = ship_decision(win, regressed)
    assert bad["ship"] is False and bad["blocked"] == ["gross margin"]   # guardrail regression blocks
    flat = {"ci_low": -0.01, "ci_high": 0.02, "direction": "up"}
    assert ship_decision(flat, clean)["ship"] is False              # primary not significant → hold


def test_test_and_roll_is_smaller_than_nhst():
    nhst = required_n(0.20, 0.05, sigma2=0.0, binary=True)["n_per_arm"]
    tr = _tr_size(200_000, math.sqrt(0.16), 0.05)
    assert tr < nhst                                                 # profit-sizing tests fewer per arm
