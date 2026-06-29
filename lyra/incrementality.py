"""Incrementality — ghost-ads / PSA-holdout lift & CACE (LYRA §8). Promoted from NB 12.

Naive attribution credits *every* conversion among the ad-exposed to the ad — wildly overstating the true
incremental effect, because most of those users would have converted anyway (Lewis–Rao). The fix is a
**holdout** (ghost ads / PSA): an eligible control with the ad withheld. `lift` is the treatment-vs-holdout
difference (the ITT); `cace` divides by the exposure rate to recover the **effect on the exposed**
(Bloom/Wald, one-sided non-compliance = IV/LATE). Ref: Johnson–Lewis–Nubbemeyer 2017; Lewis–Rao 2015.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def lift(y_treat, y_control, alpha: float = 0.05) -> dict:
    """Treatment-vs-holdout difference in means (the incremental ITT lift) with a Welch CI."""
    yt = np.asarray(y_treat, float); yc = np.asarray(y_control, float)
    nt, nc = len(yt), len(yc)
    point = yt.mean() - yc.mean()
    se = float(np.sqrt(yt.var(ddof=1) / nt + yc.var(ddof=1) / nc))
    z = float(stats.norm.ppf(1 - alpha / 2))
    p = float(2 * (1 - stats.norm.cdf(abs(point) / se))) if se > 0 else float("nan")
    return {"point": float(point), "ci_low": float(point - z * se), "ci_high": float(point + z * se),
            "se": se, "z": float(point / se) if se > 0 else float("nan"), "p_value": p,
            "n_treat": nt, "n_control": nc}


def cace(y_treat, y_control, exposed_treat, alpha: float = 0.05) -> dict:
    """Effect on the **exposed** (compliers): ITT ÷ exposure-rate among the treated (Wald / Bloom)."""
    itt = lift(y_treat, y_control, alpha)
    e = float(np.asarray(exposed_treat, float).mean())
    point, se = itt["point"] / e, itt["se"] / e
    z = float(stats.norm.ppf(1 - alpha / 2))
    return {"point": float(point), "ci_low": float(point - z * se), "ci_high": float(point + z * se),
            "se": float(se), "exposure_rate": e, "itt": itt["point"]}
