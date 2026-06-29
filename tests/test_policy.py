"""Uplift / policy / OPE tests (LYRA §10) — RATE detects the real heterogeneity, targeting beats
treat-all on the *true* value, and DR off-policy evaluation recovers the true policy value, tighter than IPS.
"""

import numpy as np

from lyra.cate import XLearner
from lyra.dgp import HeteroDGP
from lyra.ope import dr_value, ips_value
from lyra.policy import dr_scores, policy_value, rate, threshold_policy

_XC = [f"x{j}" for j in range(5)]


def _setup():
    H = HeteroDGP(seed=1)
    tr, te = H.sample(6000, seed=1), H.sample(6000, seed=7)
    X = te[_XC].to_numpy(); T = te["treat"].to_numpy(); y = te["y"].to_numpy()
    tau_hat = XLearner().fit(tr).predict_cate(X)
    return H, X, T, y, H.tau(X), tau_hat, dr_scores(X, T, y, e=0.5)


def test_rate_detects_real_heterogeneity():
    _, X, T, y, tau, tau_hat, G = _setup()
    r, se = rate(G, tau_hat, B=200)
    assert r / se > 2.5                                   # targeting value is significant


def test_targeting_beats_treat_all_on_true_value():
    _, X, T, y, tau, tau_hat, G = _setup()
    pi = threshold_policy(tau_hat, 0.0)
    assert float((pi * tau).mean()) > tau.mean() + 0.1    # excluding harmed users captures more value


def test_dr_ope_recovers_true_value_and_beats_ips():
    H = HeteroDGP(seed=1)
    model = XLearner().fit(H.sample(6000, seed=1))
    big = H.sample(50_000, seed=999); Xb = big[_XC].to_numpy()
    truth = float(((model.predict_cate(Xb) > 0).astype(int) * H.tau(Xb)).mean())
    ips, dr = [], []
    for s in range(15):
        d = H.sample(3000, seed=200 + s)
        Xd, Td, yd = d[_XC].to_numpy(), d["treat"].to_numpy(), d["y"].to_numpy()
        pid = (model.predict_cate(Xd) > 0).astype(int)
        ips.append(ips_value(pid, Td, yd)); dr.append(dr_value(pid, dr_scores(Xd, Td, yd, e=0.5)))
    assert abs(np.mean(dr) - truth) < 0.06                # DR recovers the true policy value
    assert np.std(dr) < np.std(ips)                       # and is tighter than IPS
