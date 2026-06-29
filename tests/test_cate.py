"""CATE tests (LYRA §10) — the estimators recover the *known* heterogeneous surface τ(x), the causal
forest's CIs cover it at ~nominal, and the X-learner/forest beat the regularization-shrunk S-learner."""

import numpy as np

from lyra.cate import CausalForest, SLearner, XLearner
from lyra.dgp import HeteroDGP

_XC = [f"x{j}" for j in range(5)]


def _split():
    H = HeteroDGP(seed=1)
    tr, te = H.sample(6000, seed=1), H.sample(4000, seed=2)
    Xte = te[_XC].to_numpy()
    return H, tr, Xte, H.tau(Xte)


def test_xlearner_recovers_cate():
    H, tr, Xte, tau = _split()
    pred = XLearner().fit(tr).predict_cate(Xte)
    assert np.corrcoef(pred, tau)[0, 1] > 0.85                 # tracks the true surface
    assert np.sqrt(np.mean((pred - tau) ** 2)) < 0.55          # small error vs ground truth


def test_causal_forest_ci_covers_true_tau():
    H, tr, Xte, tau = _split()
    cf = CausalForest(n_estimators=300).fit(tr)
    lb, ub = cf.predict_interval(Xte)
    assert np.mean((lb <= tau) & (tau <= ub)) >= 0.85          # honest pointwise CIs cover τ(x)
    assert abs(cf.predict_cate(Xte).mean() - tau.mean()) < 0.1  # ATE = mean CATE recovered


def test_slearner_shrinks_vs_xlearner():
    H, tr, Xte, tau = _split()
    s = SLearner().fit(tr).predict_cate(Xte)
    x = XLearner().fit(tr).predict_cate(Xte)
    assert s.std() < x.std()                                   # S-learner compresses the spread (toward ATE)
