"""Uplift evaluation & policy learning (LYRA §8). Promoted from NB 10.

All built on the **doubly-robust score** Γ (AIPW pseudo-outcome, an unbiased per-unit τ estimate):
- `uplift_curve` / `auuc` — does ranking by τ̂ find the responders?
- `rate` — AUTOC summary + bootstrap SE → *is the heterogeneity real?*
- `threshold_policy` / `policy_value` — a deployable rule and its (DR) value.
See `lyra/ope.py` for IPS vs DR off-policy value estimation.
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor as _GBR
from sklearn.model_selection import KFold

_QS = np.linspace(0.05, 1.0, 40)


def dr_scores(X, T, y, e: float = 0.5, base=_GBR, folds: int = 4, seed: int = 0) -> np.ndarray:
    """Cross-fitted AIPW pseudo-outcome Γ_i (unbiased per-unit effect; robust to a wrong μ when e known)."""
    X = np.asarray(X, float); T = np.asarray(T); y = np.asarray(y, float)
    mu1 = np.zeros(len(y)); mu0 = np.zeros(len(y))
    for tr, te in KFold(folds, shuffle=True, random_state=seed).split(X):
        for arm, mu in ((1, mu1), (0, mu0)):
            sel = tr[T[tr] == arm]
            mu[te] = base().fit(X[sel], y[sel]).predict(X[te])
    return mu1 - mu0 + T / e * (y - mu1) - (1 - T) / (1 - e) * (y - mu0)


def uplift_curve(score, rank, qs=_QS) -> np.ndarray:
    """Average effect (`score`) of the top-q fraction ranked by `rank`, for each depth q."""
    score = np.asarray(score, float); order = np.argsort(-np.asarray(rank, float)); n = len(score)
    return np.array([score[order[: max(1, int(q * n))]].mean() for q in qs])


def auuc(score, rank, qs=_QS) -> float:
    """Area under the uplift curve above the random/ATE line (== AUTOC / RATE point estimate)."""
    return float(np.mean(uplift_curve(score, rank, qs) - np.asarray(score, float).mean()))


def rate(G, rank, qs=_QS, with_ci: bool = True, B: int = 300, seed: int = 0):
    """RATE (AUTOC). Returns (rate, bootstrap SE) by default — SE gives a test for real heterogeneity."""
    G = np.asarray(G, float); rank = np.asarray(rank, float)
    r = auuc(G, rank, qs)
    if not with_ci:
        return r
    rng = np.random.default_rng(seed); n = len(G)
    boots = [auuc(G[i], rank[i], qs) for i in (rng.integers(0, n, n) for _ in range(B))]
    return r, float(np.std(boots, ddof=1))


def threshold_policy(tau_hat, cost: float = 0.0) -> np.ndarray:
    """Treat iff the estimated effect beats the treatment cost."""
    return (np.asarray(tau_hat, float) > cost).astype(int)


def policy_value(pi, G, cost: float = 0.0) -> float:
    """DR estimate of a policy's net value E[π(X)(Γ − cost)]."""
    return float((np.asarray(pi) * (np.asarray(G, float) - cost)).mean())
