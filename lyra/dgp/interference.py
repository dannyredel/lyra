"""Marketplace interference DGP (LYRA §5, L3-lite). Promoted from ``notebooks/05_interference``.

A shared-budget marketplace where treated users grab a larger share of a **saturating** conversion budget,
so treating one user **cannibalizes** others (SUTVA fails). Two designs:
- ``design="user"`` — naive within-market A/B: ``DiffInMeans`` is **biased** for the global effect.
- ``design="cluster"`` — whole markets randomized: ``ClusterOLS`` **recovers** it (cluster-robust SE).

``ground_truth().ate`` is the **global effect** $\tau_{global}=E[Y(\mathbf 1)]-E[Y(\mathbf 0)]$ (all-treat vs
all-control) — the policy-relevant quantity both designs are graded against. The full agent-based
marketplace in ``engine/`` is the richer L3; this captures the cannibalization mechanism cleanly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.protocols import GroundTruth


class InterferenceDGP:
    name = "interference"

    def __init__(self, G: int = 40, n_g: int = 300, beta: float = 0.6, cmax: float = 0.62,
                 sat: float = 0.55, design: str = "cluster"):
        self.G, self.n_g, self.beta, self.cmax, self.sat, self.design = G, n_g, beta, cmax, sat, design

    def _market_conv(self, treat: np.ndarray) -> np.ndarray:
        u = np.exp(self.beta * treat); W = u.sum(); n = len(treat)
        totalC = n * self.cmax * (1 - np.exp(-W / (n * self.sat)))    # saturating shared budget
        return np.clip(totalC * u / W, 0, 1)

    def sample(self, n: int = 0, seed: int = 0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        tg = None
        if self.design == "cluster":
            tg = np.zeros(self.G); tg[: self.G // 2] = 1.0; rng.shuffle(tg)
        out = []
        for g in range(self.G):
            treat = (np.full(self.n_g, tg[g]) if self.design == "cluster"
                     else (rng.random(self.n_g) < 0.5).astype(float))
            p = self._market_conv(treat)
            y = (rng.random(self.n_g) < p).astype(int)
            out.append(pd.DataFrame({"g": g, "treat": treat.astype(int), "x": treat, "y": y}))
        return pd.concat(out, ignore_index=True)

    def ground_truth(self) -> GroundTruth:
        n = 200_000
        tau = float(self._market_conv(np.ones(n)).mean() - self._market_conv(np.zeros(n)).mean())
        return GroundTruth(ate=tau, extra={"estimand": "global_ATE", "design": self.design,
                                           "note": "all-treat vs all-control (interference-aware)"})
