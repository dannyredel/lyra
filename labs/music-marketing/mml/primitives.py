"""Shared DGP primitives for the music-marketing lab.

Extracted once from the (previously copy-pasted) notebook code so every chapter imports the same math —
the `lyra.dgp` pattern, applied to the lab. Carryover (adstock), saturation (Hill / logistic),
over-dispersed counts, viral shocks, concentration. See FOUNDATIONS.md §2.
"""

from __future__ import annotations

import numpy as np


def adstock(x, theta: float):
    """Geometric carryover: ``adstock_t = x_t + theta · adstock_{t-1}`` (theta ∈ [0,1))."""
    x = np.asarray(x, float)
    out = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc = v + theta * acc
        out[i] = acc
    return out


def hill(x, alpha: float, kappa: float):
    """Hill saturation ``x^a / (x^a + kappa^a)`` — flexible S-curve; ``kappa`` = half-saturation point."""
    xa = np.power(np.maximum(x, 0), alpha)
    return xa / (xa + np.power(kappa, alpha))


def logsat(x, lam: float):
    """Logistic saturation ``(1 − e^{−λx}) / (1 + e^{−λx})``."""
    return (1 - np.exp(-lam * x)) / (1 + np.exp(-lam * x))


def nb_draw(mu, r: float, gen: np.random.Generator):
    """NegBinomial draw with mean ``mu`` and dispersion ``r`` (mean preserved; smaller r = spikier)."""
    mu = np.maximum(mu, 1e-6)
    return gen.negative_binomial(r, r / (r + mu))


def viral_bump(n_obs: int, rng: np.random.Generator, *, p_track=0.30, n_lambda=1.2,
               mag_lo=3.0, mag_hi=18.0, tau=9.0):
    """Transient multiplicative viral bumps over days ``a = 0 … n_obs−1`` (mostly zero; rare spikes)."""
    bump = np.zeros(n_obs)
    if rng.random() >= p_track:
        return bump
    a = np.arange(n_obs)
    for _ in range(1 + rng.poisson(n_lambda)):
        t0 = rng.integers(0, n_obs)
        bump += np.where(a >= t0, rng.uniform(mag_lo, mag_hi) * np.exp(-(a - t0) / tau), 0.0)
    return bump


def gini(x):
    """Gini concentration coefficient (0 = equal, →1 = a few hits dominate)."""
    x = np.sort(np.asarray(x, float)); n = x.size
    if n == 0 or x.sum() == 0:
        return 0.0
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))
