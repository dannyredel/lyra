"""The funnel — one DGP, many metrics (Almedia-flavoured). Promoted from ``notebooks/02_dgp_zoo``.

impression → click → convert → revenue. The lever lifts conversion and spend, so each metric has its
own true ATE (and guardrails move too). The primary OEC is **ARPU**; CTR/CVR lifts ride in ``extra``.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.protocols import GroundTruth

_ORACLE_N, _ORACLE_SEED = 200_000, 12345


def _sig(z):
    return 1.0 / (1.0 + np.exp(-z))


class FunnelDGP:
    name = "funnel"

    def __init__(self, d_cvr: float = 0.03, d_logrev: float = 0.12, sigma: float = 1.0, d: int = 3):
        self.d_cvr, self.d_logrev, self.sigma, self.d = d_cvr, d_logrev, sigma, d

    def _rates(self, X):
        p_clk = _sig(-0.5 + 0.4 * X[:, 0])
        p_cvr0 = _sig(-1.0 + 0.5 * X[:, 1])
        p_cvr1 = np.clip(p_cvr0 + self.d_cvr, 0, 1)
        return p_clk, p_cvr0, p_cvr1

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        X = rng.normal(0, 1, (n, self.d)); treat = (rng.random(n) < 0.5).astype(int)
        p_clk, p_cvr0, p_cvr1 = self._rates(X)
        p_cvr = np.where(treat == 1, p_cvr1, p_cvr0)
        click = rng.random(n) < p_clk
        convert = click & (rng.random(n) < p_cvr)
        revenue = convert * np.exp(rng.normal(2.0 + self.d_logrev * treat, self.sigma))
        return pd.DataFrame({"treat": treat, "click": click.astype(int),
                             "convert": convert.astype(int), "revenue": revenue, "y": revenue})

    def ground_truth(self) -> GroundTruth:
        rng = np.random.default_rng(_ORACLE_SEED)
        X = rng.normal(0, 1, (_ORACLE_N, self.d))
        p_clk, p_cvr0, p_cvr1 = self._rates(X)
        spend = lambda dlr: np.exp(2.0 + dlr + self.sigma ** 2 / 2)          # E[exp(N(2+dlr,σ))]
        arpu0 = (p_clk * p_cvr0 * spend(0.0)).mean()
        arpu1 = (p_clk * p_cvr1 * spend(self.d_logrev)).mean()
        return GroundTruth(ate=float(arpu1 - arpu0), extra={
            "estimand": "ARPU difference",
            "CTR_lift": 0.0,
            "CVR_lift": float((p_clk * (p_cvr1 - p_cvr0)).mean())})
