"""The ship decision rule (LYRA §3, the DECIDED state). Promoted from NB 08.

A **decision rule** maps the experiment's metric readouts → ship / no-ship; controlling per-metric
significance alone is *not* a decision (Schultzberg–Ankargren–Frånberg 2024). The rule is a **conjunction**:
ship only if the **success metric (OEC) shows superiority** *and* **every guardrail is non-inferior** (a
guardrail regression blocks the ship even if the primary moves). Optionally scores the launch by a
**trade-off vector** Λ over metric effects (Ng–Imbens 2026 — guardrails = large λ).
"""

from __future__ import annotations


def superior(ci_low: float, ci_high: float, direction: str = "up") -> bool:
    """Superiority: the CI excludes 0 in the intended direction."""
    return bool(ci_low > 0) if direction == "up" else bool(ci_high < 0)


def non_inferior(ci_low: float, ci_high: float, margin: float, direction: str = "up") -> bool:
    """Non-inferiority within a margin: a higher-is-better guardrail must not drop below −margin."""
    m = abs(margin)
    return bool(ci_low > -m) if direction == "up" else bool(ci_high < m)


def ship_decision(primary: dict, guardrails=(), weights: dict | None = None) -> dict:
    """Conjunctive ship rule. ``primary``/``guardrails`` carry ``ci_low``/``ci_high``/``direction``
    (+ ``margin``/``name`` for guardrails). Returns the verdict + per-metric breakdown + (optional) Λ-value."""
    p_ok = superior(primary["ci_low"], primary["ci_high"], primary.get("direction", "up"))
    gz = []
    for g in guardrails:
        ok = non_inferior(g["ci_low"], g["ci_high"], g["margin"], g.get("direction", "up"))
        gz.append({**g, "non_inferior": ok})
    blocked = [g for g in gz if not g["non_inferior"]]
    ship = p_ok and not blocked
    if ship:
        reason = "primary shows superiority and all guardrails are non-inferior"
    elif not p_ok:
        reason = "primary not yet significant — keep collecting"
    else:
        reason = f"blocked: {blocked[0]['name']} regressed beyond its margin"
    out = {"ship": bool(ship), "primary_superior": bool(p_ok),
           "guardrails": gz, "blocked": [g["name"] for g in blocked], "reason": reason}
    if weights:                                      # Ng–Imbens Λ-weighted launch value (optional)
        out["value"] = float(weights.get("primary", 1.0) * primary.get("effect", 0.0)
                             + sum(weights.get(g["name"], 0.0) * g.get("effect", 0.0) for g in gz))
    return out
