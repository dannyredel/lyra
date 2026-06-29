"""Assignment / bucketing (LYRA §2 layer 1) — deterministic, stateless, **source-agnostic**.

The same function serves a simulated batch (Vega) and a live SDK call (`get_variant`). Salted **per
experiment** so the same unit isn't correlated across experiments (the classic carryover bug). Steal:
Stitch Fix #oneway / Squarespace Praetor — one assignment service behind every randomization.
"""

from __future__ import annotations

import hashlib


def bucket(unit_id: str, salt: str, n_buckets: int = 10_000) -> int:
    """Stable hash of (salt + unit) → a bucket in [0, n_buckets). SHA-256, first 8 hex digits."""
    digest = hashlib.sha256(f"{salt}::{unit_id}".encode()).hexdigest()
    return int(digest[:8], 16) % n_buckets


def assign(unit_id: str, salt: str, allocations: dict[str, float]) -> str:
    """Map a unit to a variant given per-variant allocation fractions (summing to ~1)."""
    b = bucket(unit_id, salt)
    edge = 0.0
    for variant, frac in allocations.items():
        edge += frac * 10_000
        if b < edge:
            return variant
    return list(allocations)[-1]


def srm_chi2(counts: dict[str, int], allocations: dict[str, float]) -> tuple[float, float]:
    """Sample-ratio-mismatch χ²: observed arm counts vs expected from the allocation. Returns (chi2, p)."""
    from scipy import stats
    total = sum(counts.values())
    obs = [counts[v] for v in allocations]
    exp = [allocations[v] * total for v in allocations]
    chi2 = sum((o - e) ** 2 / e for o, e in zip(obs, exp) if e > 0)
    p = float(stats.chi2.sf(chi2, df=len(allocations) - 1))
    return float(chi2), p
