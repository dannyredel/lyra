"""Switchback DGP — temporal interference (LYRA §5, L2). Promoted from ``notebooks/06_switchback``.

Holds a market fixed and randomizes treatment **over time** (cell = cluster × period), trading
cross-sectional interference (NB 05) for **temporal** problems: carryover, autocorrelation, and a finite
lumpy set of cells. Outcome (Pankratev 2026):
``y = mu + (alpha_cl + gamma_t + delta_{cl,t}) + tau_cl·T + carryover + eps``. Estimate with a
**cluster-robust** OLS clustered on the market (``ClusterOLS(x="treat", cluster="cluster")``); add CUPED on
``x_hist`` for variance reduction. ``ground_truth().ate = tau`` (clean DGP, no carryover).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.protocols import GroundTruth

_W_CARRY = np.array([0.3, 0.2, 0.1])      # carryover decay weights


class SwitchbackDGP:
    name = "switchback"

    def __init__(self, J: int = 40, H: int = 18, n_bar: int = 12, tau: float = 20.0, tau_sd: float = 10.0,
                 S_cl: float = 0.05, S_time: float = 0.03, S_int: float = 0.02, S_res: float = 0.90,
                 sigma_total: float = 1000.0, mu: float = 2000.0, rho: float = 0.3, cv: float = 1.0,
                 carry: float = 0.0):
        self.J, self.H, self.n_bar, self.tau, self.tau_sd = J, H, n_bar, tau, tau_sd
        self.S = (S_cl, S_time, S_int, S_res)
        self.sigma_total, self.mu, self.rho, self.cv, self.carry = sigma_total, mu, rho, cv, carry

    def sample(self, n: int = 0, seed: int = 0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        J, H, n_bar = self.J, self.H, self.n_bar
        s_cl, s_tm, s_in, s_rs = (np.sqrt(s) * self.sigma_total for s in self.S)
        z_cl = rng.standard_normal(J)
        f = np.sin(2.5 * z_cl) + 0.5 * z_cl ** 2
        alpha = s_cl * (f - f.mean()) / (f.std() + 1e-9)                       # nonlinear cluster effect
        gamma = s_tm * np.sqrt(2) * np.sin(2 * np.pi * np.arange(H) / 24)       # diurnal
        delta = np.zeros((J, H)); delta[:, 0] = rng.normal(0, s_in, J)          # AR(1) cluster×time
        for t in range(1, H):
            delta[:, t] = self.rho * delta[:, t - 1] + rng.normal(0, s_in * np.sqrt(1 - self.rho ** 2), J)
        T = rng.integers(0, 2, (J, H))
        tau_cl = rng.normal(self.tau, self.tau_sd, J)
        carry = np.zeros((J, H))
        for t in range(H):
            for k in (1, 2, 3):
                if t - k >= 0:
                    carry[:, t] += _W_CARRY[k - 1] * self.carry * tau_cl * (T[:, t - k] - T[:, t])
        if self.cv <= 0:
            n_cell = np.full((J, H), n_bar, dtype=int)
        else:
            shape = 1.0 / self.cv ** 2
            n_cell = np.maximum(1, np.round(rng.gamma(shape, n_bar / shape, (J, H)))).astype(int)
        jj, tt = np.meshgrid(np.arange(J), np.arange(H), indexing="ij")
        macro_cell = alpha[jj] + gamma[tt] + delta
        treat_cell = tau_cl[jj] * T + carry
        rep = n_cell.ravel()
        cl = np.repeat(jj.ravel(), rep); pe = np.repeat(tt.ravel(), rep)
        y = self.mu + np.repeat(macro_cell.ravel(), rep) + np.repeat(treat_cell.ravel(), rep) \
            + rng.normal(0, s_rs, rep.sum())
        x_hist = alpha[cl] + gamma[pe] + rng.normal(0, np.sqrt(s_cl ** 2 + s_tm ** 2), rep.sum())
        return pd.DataFrame({"cluster": cl, "period": pe, "treat": np.repeat(T.ravel(), rep),
                             "y": y, "x_hist": x_hist, "z": z_cl[cl]})

    def ground_truth(self) -> GroundTruth:
        return GroundTruth(ate=float(self.tau), extra={"estimand": "switchback ATE", "design": "temporal",
                                                       "carry": self.carry})
