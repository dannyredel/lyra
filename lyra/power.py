"""Power / MDE / sample-size — the DRAFT power-gate (LYRA §3, §7). Promoted from NB 08.

The Spotify-Confidence SSC formula (`papers/sample-size-calculation.md`): base two-sample N, then
multiple-testing + guardrail corrections, allocation, and CUPED. A **cross-cutting practice** — every
experiment is sized at DRAFT and the platform warns/refuses on an underpowered design. The honest sizing
for switchback/clustered designs (no closed form) is **simulation-based power = the Monte-Carlo harness**
run under H1 (`harness(...)["reject_rate"]`).
"""

from __future__ import annotations

import math

from scipy.stats import norm


def _adjust(alpha, power, n_comparisons, n_success, n_guardrail_nim):
    alpha_adj = alpha / (n_comparisons * max(n_success, 1))                       # Bonferroni (success only)
    power_adj = 1 - (1 - power) / (n_guardrail_nim + max(min(n_success, 1), 1))   # family-wise power
    return alpha_adj, power_adj


def required_n(mu: float, rel_mde: float, sigma2: float, *, alpha: float = 0.05, power: float = 0.8,
               n_comparisons: int = 1, n_success: int = 1, n_guardrail_nim: int = 0,
               rho: float = 0.0, q_control: float = 0.5, binary: bool = False, two_sided: bool = True) -> dict:
    """Total required N (both arms). Returns the number + the adjusted α/power + the absolute MDE.

    ``two_sided`` (default) uses z_{1-α/2} — correct for the two-sided CIs the platform analyses with.
    ``two_sided=False`` is the one-sided Spotify-SSC convention (z_{1-α}); it under-powers a two-sided test."""
    if binary:
        sigma2 = mu * (1 - mu)
    a_adj, p_adj = _adjust(alpha, power, n_comparisons, n_success, n_guardrail_nim)
    z = norm.ppf(1 - (a_adj / 2 if two_sided else a_adj)) + norm.ppf(p_adj)
    delta = mu * rel_mde
    alloc = 1 / q_control + 1 / (1 - q_control)               # = 4 at 50/50; grows with imbalance
    n = alloc * z ** 2 * sigma2 * (1 - rho) / delta ** 2
    return {"n_total": int(round(n)), "n_per_arm": int(round(n * q_control)),
            "alpha_adj": a_adj, "power_adj": p_adj, "abs_mde": delta, "z": z}


def mde(n_total: int, mu: float, sigma2: float, *, alpha: float = 0.05, power: float = 0.8,
        n_comparisons: int = 1, n_success: int = 1, n_guardrail_nim: int = 0,
        rho: float = 0.0, q_control: float = 0.5, binary: bool = False, two_sided: bool = True) -> dict:
    """Invert the SSC formula: the minimum detectable effect at a given N (absolute + relative)."""
    if binary:
        sigma2 = mu * (1 - mu)
    a_adj, p_adj = _adjust(alpha, power, n_comparisons, n_success, n_guardrail_nim)
    z = norm.ppf(1 - (a_adj / 2 if two_sided else a_adj)) + norm.ppf(p_adj)
    alloc = 1 / q_control + 1 / (1 - q_control)
    delta = math.sqrt(alloc * z ** 2 * sigma2 * (1 - rho) / max(n_total, 1))
    return {"abs_mde": delta, "rel_mde": delta / mu if mu else float("nan")}


def power_gate(mu: float, rel_mde: float, sigma2: float, available_n: int, **kw) -> dict:
    """Compare available traffic to the required N; flag underpowered (the DRAFT gate)."""
    req = required_n(mu, rel_mde, sigma2, **kw)
    powered = available_n >= req["n_total"]
    return {**req, "available_n": available_n, "powered": powered,
            "pct_of_required": round(100 * available_n / req["n_total"], 1) if req["n_total"] else 0.0,
            "verdict": "OK" if powered else "UNDERPOWERED"}


def test_and_roll_size(N: int, sigma: float, s: float) -> int:
    """Profit-maximizing test size (Feit–Berman 2019): test small, roll the winner to the remaining N.
    ``sigma`` = outcome SD, ``s`` = prior SD of the arm means. n* per arm ≈ √(N/4·(s/σ)²+...) ≪ NHST."""
    r = (s / sigma) ** 2
    n = math.sqrt(N / 4 * (3 * r ** 2 + 4 * r) + (3 * r / 4) ** 2) - (3 * r / 4) if r > 0 else N / 2
    return max(1, int(round(n)))
