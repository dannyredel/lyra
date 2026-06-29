"""Diagnostics & multiple-testing — cross-cutting platform health (LYRA §6). Promoted from NB 07.

**SRM** (sample-ratio mismatch) gates every experiment; **Benjamini–Hochberg** controls the false
discovery rate across the metric battery / portfolio (20 metrics @ 5% → 64% chance of a false positive
without control). Steal: eBay SRM, the open-guide multiple-testing trap, Spotify "correct success metrics".
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def srm_chi2(counts: dict, allocations: dict) -> tuple[float, float]:
    """Sample-ratio-mismatch χ²: observed arm counts vs expected from the allocation → (chi2, p)."""
    total = sum(counts.values())
    obs = [counts[v] for v in allocations]
    exp = [allocations[v] * total for v in allocations]
    chi2 = sum((o - e) ** 2 / e for o, e in zip(obs, exp) if e > 0)
    return float(chi2), float(stats.chi2.sf(chi2, df=len(allocations) - 1))


def bh_fdr(pvalues, alpha: float = 0.05) -> dict:
    """Benjamini–Hochberg FDR control. Returns per-test rejections + the count surviving FDR."""
    p = np.asarray(pvalues, float); m = len(p)
    if m == 0:
        return {"rejected": [], "n_significant": 0, "cutoff": 0.0, "m": 0, "alpha": alpha}
    order = np.argsort(p); ranked = p[order]
    thresh = alpha * (np.arange(1, m + 1) / m)
    below = ranked <= thresh
    kmax = int(np.where(below)[0].max()) + 1 if below.any() else 0
    cutoff = float(ranked[kmax - 1]) if kmax > 0 else 0.0
    rej = (p <= cutoff) if kmax > 0 else np.zeros(m, bool)
    return {"rejected": rej.tolist(), "n_significant": int(rej.sum()), "cutoff": cutoff,
            "m": m, "alpha": alpha}
