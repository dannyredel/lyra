"""Always-valid (sequential) inference — the peek-safe layer (LYRA §7-8). Promoted from NB 07.

A **cross-cutting practice**, not an experiment type: *every* running experiment gets an **always-valid
confidence sequence** (so you can peek any time without inflating error) and an **advisory stop**
recommendation. The CS is the Waudby-Smith asymptotic confidence sequence — the fixed-$n$ interval times a
time-uniform **multiplier** (the explicit *price of peeking*, always $> z_{\alpha/2}$), valid at *all*
sample sizes simultaneously. Steal: Etsy advisory auto-stop + magnitude-inflation caveat; Deng–Lu proper-
stopping; the LIL reason naive peeking fails.
"""

from __future__ import annotations

import math

DEFAULT_RHO2 = 0.05


def cs_multiplier(n: int, alpha: float = 0.05, rho2: float = DEFAULT_RHO2) -> float:
    """Time-uniform multiplier on the SE (replaces $z_{1-\alpha/2}$ in a fixed-$n$ CI). Grows ~√(log n)."""
    if n < 1:
        return float("inf")
    a = n * rho2
    return math.sqrt(2.0 * (a + 1.0) / a * math.log(math.sqrt(a + 1.0) / alpha))


def confidence_sequence(looks: list[dict], alpha: float = 0.05, rho2: float = DEFAULT_RHO2) -> list[dict]:
    """Per-look always-valid band. Each look needs ``point`` + (``se`` or a fixed-n ``ci``) + ``n``.
    Returns the looks with ``cs_low``/``cs_high`` (wider than the fixed-n CI — the peeking tax)."""
    out = []
    for r in looks:
        se = r.get("se")
        if se is None and "ci_low" in r:
            se = (r["ci_high"] - r["ci_low"]) / (2 * 1.959963985)
        n = r.get("n") or r.get("day") or 1
        half = cs_multiplier(max(int(n), 1), alpha, rho2) * (se or 0.0)
        out.append({**r, "cs_low": r["point"] - half, "cs_high": r["point"] + half})
    return out


def advisory(cs_looks: list[dict], powered: bool = True, min_looks: int = 3) -> dict:
    """Advisory stop recommendation from the latest always-valid look (the human still decides).

    Fires only on a CS that **excludes 0** (never a raw p-dip) and only after a minimum runtime; flags
    **magnitude-inflated** if stopped before the design was powered (the winner's-curse haircut).
    """
    if not cs_looks:
        return {"state": "collecting", "text": "Collecting data", "can_stop": False}
    last = cs_looks[-1]
    excludes0 = not (last["cs_low"] <= 0 <= last["cs_high"])
    if len(cs_looks) < min_looks:
        return {"state": "collecting", "text": "Collecting data — below minimum runtime", "can_stop": False}
    if excludes0:
        early = not powered
        return {"state": "stop", "can_stop": True, "magnitude_inflated": bool(early),
                "text": "Safe to stop — the always-valid interval excludes 0"
                        + (" (stopped early: magnitude may be inflated)" if early else "")}
    return {"state": "keep", "can_stop": False,
            "text": "Keep collecting — the always-valid interval still spans 0"}
