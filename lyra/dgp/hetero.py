"""Heterogeneous-effect DGP (LYRA §5) — a known CATE surface for validating τ̂(x). Promoted from NB 09.

A randomized experiment whose effect **varies by covariate**: ``tau(X) = 0.5 + x0 − 0.5·x1`` over a
nonlinear nuisance ``m(X) = sin 2x0 + x1² + 0.5·x2`` (x2–x4 are noise). The ATE is ~+0.5 but the per-unit
effect ranges widely — so a CATE estimator can be graded against the *true* surface (``tau(X)``), which a
real platform can never see.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.protocols import GroundTruth


class HeteroDGP:
    name = "hetero"

    def __init__(self, d: int = 5, seed: int = 0):
        self.d = d

    def tau(self, X) -> np.ndarray:
        """The true CATE surface τ(x) (we author it)."""
        X = np.asarray(X, float)
        return 0.5 + X[:, 0] - 0.5 * X[:, 1]

    def _m(self, X: np.ndarray) -> np.ndarray:
        return np.sin(2 * X[:, 0]) + X[:, 1] ** 2 + 0.5 * X[:, 2]

    def sample(self, n: int = 6000, seed: int = 0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        X = rng.standard_normal((n, self.d))
        T = rng.integers(0, 2, n)                                  # randomized, e = 0.5
        y = self._m(X) + (T - 0.5) * self.tau(X) + rng.standard_normal(n)
        cols = {f"x{j}": X[:, j] for j in range(self.d)}
        return pd.DataFrame({**cols, "treat": T, "x": X[:, 0], "y": y})

    def ground_truth(self) -> GroundTruth:
        rng = np.random.default_rng(12345)
        ate = float(self.tau(rng.standard_normal((200_000, self.d))).mean())
        return GroundTruth(ate=ate, extra={"estimand": "ATE", "note": "heterogeneous τ(x)"})
