"""Sequential & diagnostics tests (LYRA §10) — the peek-safe layer: the confidence sequence controls
the false-positive rate under continuous monitoring (the fixed-z test does not), the advisory stops on a
CS excluding 0, BH-FDR controls discoveries, and SRM flags imbalance."""

import math

import numpy as np

from lyra.diagnostics import bh_fdr, srm_chi2
from lyra.sequential import advisory, confidence_sequence, cs_multiplier


def accrue(effect=0.0, per_day=500, days=40, p0=0.20, seed=0):
    rng = np.random.default_rng(seed); ct = cc = nt = nc = 0; out = []
    for d in range(days):
        h = per_day // 2
        ct += rng.binomial(h, p0 + effect); nt += h
        cc += rng.binomial(h, p0); nc += h
        p1, p0h = ct / nt, cc / nc
        se = math.sqrt(p1 * (1 - p1) / nt + p0h * (1 - p0h) / nc)
        out.append({"day": d + 1, "point": p1 - p0h, "se": se, "n": nt + nc})
    return out


def test_cs_multiplier_is_the_peeking_tax():
    assert cs_multiplier(10_000) > 1.959964            # always wider than the fixed z


def test_cs_controls_peeking_fpr_but_fixed_does_not():
    R = 600
    cs = np.mean([any(abs(r["point"]) > cs_multiplier(r["n"]) * r["se"] for r in accrue(0.0, seed=s)) for s in range(R)])
    fx = np.mean([any(abs(r["point"]) / r["se"] > 1.959964 for r in accrue(0.0, seed=s)) for s in range(R)])
    assert cs < 0.10                                    # peek-safe (≤ α)
    assert fx > 0.15                                    # naive peeking inflates the false-positive rate


def test_advisory_stops_on_real_effect_only():
    assert advisory(confidence_sequence(accrue(effect=0.05, seed=1)), powered=True)["state"] == "stop"
    assert advisory(confidence_sequence(accrue(0.0, seed=1)), powered=True)["state"] in ("keep", "collecting")


def test_bh_fdr_controls_discoveries():
    rng = np.random.default_rng(0)
    assert bh_fdr(rng.random(20).tolist())["n_significant"] <= 2          # all null → few rejections
    assert bh_fdr([0.0001, 0.0002, 0.5, 0.6, 0.7])["n_significant"] >= 2  # strong signals rejected


def test_srm_flags_imbalance():
    assert srm_chi2({"control": 5000, "treatment": 5000}, {"control": .5, "treatment": .5})[1] > 0.05
    assert srm_chi2({"control": 5400, "treatment": 4600}, {"control": .5, "treatment": .5})[1] < 0.001
