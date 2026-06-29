"""Incrementality tests (LYRA §10, NB 12) — naive attribution overstates the lift several-fold, the
ghost-ad holdout (ITT) and CACE recover the authored truth, and the real Criteo estimate is sensible.
"""

import numpy as np
import pytest

from lyra.incrementality import cace, lift

_sig = lambda z: 1 / (1 + np.exp(-z))


def _sim(n=400_000, tau=0.015, seed=0):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)
    elig = rng.random(n) < 0.5
    shown = elig & (rng.random(n) < _sig(-0.4 + 1.2 * x))
    conv = (rng.random(n) < (_sig(-3.2 + 0.8 * x) + tau * shown)).astype(int)
    return x, elig, shown.astype(int), conv


def test_naive_overstates_and_holdout_recovers_truth():
    x, elig, shown, conv = _sim(); tau = 0.015
    assert conv[shown == 1].mean() > 3 * tau              # naive attribution wildly overstates
    yt, yc = conv[elig], conv[~elig]
    cc, itt = cace(yt, yc, shown[elig]), lift(yt, yc)
    assert abs(cc["point"] - tau) < 0.004                 # CACE recovers the per-exposed effect
    assert abs(itt["point"] - tau * shown[elig].mean()) < 0.003   # ITT = τ · exposure rate


def test_criteo_behaves_sensibly_at_scale():
    from validation.criteo import CACHE, load_sample, validate
    if not CACHE.exists():
        pytest.skip("Criteo sample not cached — run validation.criteo.load_sample() (streams from HF)")
    v = validate(load_sample())
    assert v["visit"]["point"] > 0 and v["visit"]["z"] > 5     # small but highly-significant positive lift
    assert v["conversion"]["point"] > 0 and v["conversion"]["z"] > 3
