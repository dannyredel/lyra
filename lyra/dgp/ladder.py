"""DGP fidelity ladder — lower rungs (LYRA §5). Promoted from ``notebooks/01_spine``.

- **L0 — iid:** distributions + a constant ATE.
- **L1 — covariates → potential outcomes:** ``X → (Y(0), Y(1))`` with a CATE surface, a baseline that
  can be **nonlinear** in X, and a **confounding knob** (propensity depends on X). The rung that
  powers the "OLS biases / AIPW survives" robustness demo.

(L2 temporal/carryover = NB06 switchback; L3 = the marketplace in ``engine/``.) Covariate columns are
``x0, x1, …``. ``sample`` returns only observable data; ``ground_truth`` is the harness's oracle.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.protocols import GroundTruth


class DGPLevel0:
    """L0 — iid, randomized, constant additive effect: ``y = mu + tau·T + N(0, sigma)``."""

    name = "L0-iid"

    def __init__(self, ate: float = 2.0, mu: float = 10.0, sigma: float = 5.0, p_treat: float = 0.5):
        self.ate, self.mu, self.sigma, self.p_treat = ate, mu, sigma, p_treat

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        treat = (rng.random(n) < self.p_treat).astype(int)
        y = self.mu + self.ate * treat + rng.normal(0, self.sigma, n)
        return pd.DataFrame({"treat": treat, "y": y})

    def ground_truth(self) -> GroundTruth:
        return GroundTruth(ate=self.ate)


def baseline(X: np.ndarray, nonlinear: bool) -> np.ndarray:
    """Untreated mean surface b(X) — linear, or a genuinely nonlinear function of the first covariates."""
    if nonlinear:
        return 2.0 * np.sin(1.5 * X[:, 0]) + X[:, 1] ** 2 + 1.5 * X[:, 0] * X[:, 1]
    return 1.2 * X[:, 0] - 0.8 * X[:, 1] + 0.5 * X[:, 2]


class DGPLevel1:
    """L1 — covariates → potential outcomes.

    ``Y(0)=b(X)+noise``, ``Y(1)=Y(0)+tau(X)`` with ``tau(X)=ate+het·x0`` (so E[tau]=ate). The
    **confounding knob**: ``confounding=0`` ⇒ randomized (e=0.5); ``>0`` ⇒ ``e(X)=σ(confounding·c(X))``
    correlated with the same X that drives the baseline.
    """

    name = "L1-covariates"

    def __init__(self, d: int = 5, ate: float = 2.0, sigma: float = 1.0,
                 confounding: float = 0.0, nonlinear: bool = False, het: float = 0.0):
        self.d, self.ate, self.sigma = d, ate, sigma
        self.confounding, self.nonlinear, self.het = confounding, nonlinear, het

    def _cate(self, X: np.ndarray) -> np.ndarray:
        return self.ate + self.het * X[:, 0]

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        X = rng.normal(0, 1, (n, self.d))
        b = baseline(X, self.nonlinear)
        c = X[:, 0] + (X[:, 1] ** 2 - 1.0)
        e = np.full(n, 0.5) if self.confounding == 0 else 1 / (1 + np.exp(-self.confounding * c))
        treat = (rng.random(n) < e).astype(int)
        y0 = b + rng.normal(0, self.sigma, n)
        y = y0 + self._cate(X) * treat
        df = pd.DataFrame(X, columns=[f"x{j}" for j in range(self.d)])
        df.insert(0, "y", y)
        df.insert(0, "treat", treat)
        return df

    def ground_truth(self) -> GroundTruth:
        return GroundTruth(ate=self.ate, cate=self._cate,
                           extra={"confounding": self.confounding, "nonlinear": self.nonlinear})


def covariate_cols(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("x")]
