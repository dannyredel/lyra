"""Direct planted-effect A/B DGP — the workhorse for *created* experiments (LYRA §5).

When a user creates an experiment on the platform they set a **true effect** (this is a simulator — we
author the ground truth). ``ABDGP`` plants it exactly: control draws from a baseline, treatment from the
baseline shifted by ``effect``, so ``ground_truth().ate == effect`` by construction. Binary (Bernoulli) or
continuous (Normal). The scorecard then certifies the estimate against this known truth.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.protocols import GroundTruth


class ABDGP:
    name = "ab"

    def __init__(self, mu: float = 0.2, effect: float = 0.01, binary: bool = True,
                 sigma: float = 1.0, q_control: float = 0.5):
        self.mu, self.effect, self.binary = mu, effect, binary
        self.sigma, self.q_control = sigma, q_control

    def sample(self, n: int = 10_000, seed: int = 0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        treat = (rng.random(n) >= self.q_control).astype(int)        # control share = q_control
        if self.binary:
            p = np.clip(self.mu + self.effect * treat, 0.0, 1.0)
            y = (rng.random(n) < p).astype(int)
        else:
            y = rng.normal(self.mu + self.effect * treat, self.sigma, n)
        return pd.DataFrame({"treat": treat, "x": treat.astype(float), "y": y})

    def ground_truth(self) -> GroundTruth:
        return GroundTruth(ate=float(self.effect),
                           extra={"estimand": "ATE", "baseline": self.mu, "binary": self.binary})
