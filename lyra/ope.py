"""Off-policy evaluation (LYRA §8) — estimate a policy's value from logged data. Promoted from NB 10.

**IPS** (inverse-propensity) is unbiased but high-variance; **DR** (doubly-robust) adds the DR score as a
control variate → same target, far tighter. Validated in NB 10 to recover the *true* policy value.
"""

from __future__ import annotations

import numpy as np


def ips_value(pi, T, y, e: float = 0.5, cost: float = 0.0) -> float:
    """Horvitz–Thompson estimate of the policy's incremental value E[π(X)τ(X)] − cost·E[π]."""
    pi = np.asarray(pi); T = np.asarray(T); y = np.asarray(y, float)
    return float((pi * (T / e - (1 - T) / (1 - e)) * y).mean() - cost * pi.mean())


def dr_value(pi, G, cost: float = 0.0) -> float:
    """Doubly-robust policy value E[π(X)(Γ − cost)] using DR scores Γ (`lyra.policy.dr_scores`)."""
    pi = np.asarray(pi); G = np.asarray(G, float)
    return float((pi * (G - cost)).mean())
