"""Realistic-outcome DGPs — the realism dial (LYRA §5). Promoted from ``notebooks/02_dgp_zoo``.

Each world authors potential outcomes so the **ground truth is known**, even through a nonlinear link.
The true ATE is computed from the *expected* potential outcomes on a large oracle sample (low Monte-
Carlo noise) — the counterfactual-twin idea. ``sample`` returns only observable data.

Lesson carried from NB 02: under randomization diff-in-means recovers the ATE for *every* type — the
outcome *type* drives the variance / correct inference (NB 03 metrics), not the point.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from lyra.protocols import GroundTruth

_ORACLE_N, _ORACLE_SEED = 200_000, 12345


def _sig(z):
    return 1.0 / (1.0 + np.exp(-z))


class BinaryDGP:
    """Conversion / click — Bernoulli with logistic link. ATE = risk difference E[p1−p0] (≠ logit β)."""

    name = "binary"

    def __init__(self, beta: float = 0.5, a0: float = -0.4, d: int = 3):
        self.beta, self.a0, self.d = beta, a0, d

    def _logodds(self, X):
        return self.a0 + 0.8 * X[:, 0] - 0.5 * X[:, 1]

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        X = rng.normal(0, 1, (n, self.d)); a = self._logodds(X)
        treat = (rng.random(n) < 0.5).astype(int)
        p = np.where(treat == 1, _sig(a + self.beta), _sig(a))
        df = pd.DataFrame({"treat": treat, "y": (rng.random(n) < p).astype(int)})
        df[[f"x{j}" for j in range(self.d)]] = X
        return df

    def ground_truth(self) -> GroundTruth:
        rng = np.random.default_rng(_ORACLE_SEED)
        a = self._logodds(rng.normal(0, 1, (_ORACLE_N, self.d)))
        ate = float((_sig(a + self.beta) - _sig(a)).mean())
        return GroundTruth(ate=ate, extra={"estimand": "risk_difference", "logit_beta": self.beta})


class CountDGP:
    """Sessions / visits — Poisson with log link. ATE = rate difference E[λ1−λ0]; rate ratio = e^β."""

    name = "count"

    def __init__(self, beta: float = 0.15, a0: float = 0.7, d: int = 3):
        self.beta, self.a0, self.d = beta, a0, d

    def _logmean(self, X):
        return self.a0 + 0.5 * X[:, 0]

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        X = rng.normal(0, 1, (n, self.d)); a = self._logmean(X)
        treat = (rng.random(n) < 0.5).astype(int)
        lam = np.where(treat == 1, np.exp(a + self.beta), np.exp(a))
        df = pd.DataFrame({"treat": treat, "y": rng.poisson(lam)})
        df[[f"x{j}" for j in range(self.d)]] = X
        return df

    def ground_truth(self) -> GroundTruth:
        rng = np.random.default_rng(_ORACLE_SEED)
        a = self._logmean(rng.normal(0, 1, (_ORACLE_N, self.d)))
        ate = float((np.exp(a + self.beta) - np.exp(a)).mean())
        return GroundTruth(ate=ate, extra={"estimand": "rate_difference", "rate_ratio": float(np.exp(self.beta))})


class RevenueDGP:
    """Revenue — spike-at-zero + lognormal (convert, then spend). Unbiased but heavy-tailed (→ CUPED)."""

    name = "revenue"

    def __init__(self, p0: float = 0.10, mu0: float = 2.0, sigma: float = 1.0, dp: float = 0.04, dmu: float = 0.10):
        self.p0, self.mu0, self.sigma, self.dp, self.dmu = p0, mu0, sigma, dp, dmu

    def _mean(self, p, mu):
        return p * np.exp(mu + self.sigma ** 2 / 2)

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        treat = (rng.random(n) < 0.5).astype(int)
        p = np.where(treat == 1, self.p0 + self.dp, self.p0)
        mu = np.where(treat == 1, self.mu0 + self.dmu, self.mu0)
        y = (rng.random(n) < p) * np.exp(rng.normal(mu, self.sigma))
        return pd.DataFrame({"treat": treat, "y": y})

    def ground_truth(self) -> GroundTruth:
        ate = self._mean(self.p0 + self.dp, self.mu0 + self.dmu) - self._mean(self.p0, self.mu0)
        return GroundTruth(ate=float(ate), extra={"estimand": "mean_difference"})


class RatioDGP:
    """GMV/conversions-per-session — randomize by user, measure by session (random denominator → delta method).

    The estimand is the per-session conversion-rate lift ``dcr``. ``sample`` returns the per-user table
    (``sessions``, ``conversions``, ``y=conversions/sessions``) both naive and delta-method estimators consume.
    """

    name = "ratio"

    def __init__(self, cr0: float = 0.20, dcr: float = 0.02, lam_sessions: float = 4.0,
                 user_sigma: float = 0.0):
        self.cr0, self.dcr, self.lam_sessions, self.user_sigma = cr0, dcr, lam_sessions, user_sigma

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        treat = (rng.random(n) < 0.5).astype(int)
        m = 1 + rng.poisson(self.lam_sessions, n)
        u = rng.normal(0, self.user_sigma, n) if self.user_sigma > 0 else 0.0   # user heterogeneity
        cr = np.clip(np.where(treat == 1, self.cr0 + self.dcr, self.cr0) + u, 0.001, 0.999)
        conv = rng.binomial(m, cr)
        df = pd.DataFrame({"treat": treat, "sessions": m, "conversions": conv})
        df["y"] = df.conversions / df.sessions
        return df

    def ground_truth(self) -> GroundTruth:
        return GroundTruth(ate=float(self.dcr), extra={"estimand": "per_session_conv_rate_difference",
                                                       "user_sigma": self.user_sigma})


class ClusteredDGP:
    """Correlated units — the cluster-robust-SE world (NB 04). Cluster-level regressor (worst case for
    naive SEs): ``y_ig = mu + beta·x_g + alpha_g + eps_ig`` with intra-cluster correlation ``rho_u``.
    The estimand is the coefficient ``beta`` (= ATE if ``x`` is a cluster-level treatment). ``sample``
    ignores the harness's ``n`` and uses ``G`` clusters of size ``n_g``."""

    name = "clustered"

    def __init__(self, G: int = 50, n_g: int = 10, beta: float = 0.0, rho_u: float = 0.5,
                 balanced: bool = True, binary_treat: bool = False):
        self.G, self.n_g, self.beta, self.rho_u = G, n_g, beta, rho_u
        self.balanced, self.binary_treat = balanced, binary_treat

    def sample(self, n: int = 0, seed: int = 0) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        sa, se = np.sqrt(self.rho_u), np.sqrt(1 - self.rho_u)
        sizes = [self.n_g] * self.G if self.balanced else \
            rng.integers(max(2, self.n_g // 3), self.n_g * 2, self.G)
        if self.binary_treat:                                  # cluster-randomized: half the clusters treated
            xg = np.zeros(self.G); xg[: self.G // 2] = 1.0; rng.shuffle(xg)
        else:
            xg = rng.normal(0, 1, self.G)                      # continuous cluster regressor (NB 04 / Moulton)
        out = []
        for g in range(self.G):
            a = rng.normal(0, sa)
            y = self.beta * xg[g] + a + rng.normal(0, se, sizes[g])
            d = {"g": g, "x": np.full(sizes[g], xg[g]), "y": y}
            if self.binary_treat:
                d["treat"] = np.full(sizes[g], int(xg[g]))
            out.append(pd.DataFrame(d))
        return pd.concat(out, ignore_index=True)

    def ground_truth(self) -> GroundTruth:
        return GroundTruth(ate=float(self.beta), extra={"estimand": "cluster_coef", "rho_u": self.rho_u,
                                                        "G": self.G, "n_g": self.n_g})


class PrePostDGP:
    """Pre/post world for variance reduction — a pre-experiment covariate ``x_pre`` correlated (ρ) with
    the outcome. ``y = mu + ρ·x_pre + ate·T + noise``; CUPED/regression-adjustment cut variance ~1−ρ²."""

    name = "pre-post"

    def __init__(self, ate: float = 0.3, rho: float = 0.7, mu: float = 5.0):
        self.ate, self.rho, self.mu = ate, rho, mu

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        treat = (rng.random(n) < 0.5).astype(int)
        x_pre = rng.normal(0, 1, n)
        y = self.mu + self.rho * x_pre + self.ate * treat + rng.normal(0, np.sqrt(1 - self.rho ** 2), n)
        return pd.DataFrame({"treat": treat, "y": y, "x_pre": x_pre})

    def ground_truth(self) -> GroundTruth:
        return GroundTruth(ate=float(self.ate), extra={"estimand": "mean_difference", "rho": self.rho})


class SurvivalDGP:
    """Churn / retention — exponential hazard (proportional) + censoring at horizon H.

    Primary OEC here is the **D30-retention** binary ``y = 1{T > 30}``; ``time``/``event`` are also
    returned for survival/RMST methods later. ATE = E[S1(30) − S0(30)]; hazard ratio = e^{−β}.
    """

    name = "survival"

    def __init__(self, beta: float = 0.4, lam0: float = 0.05, H: int = 60, day: int = 30, d: int = 2):
        self.beta, self.lam0, self.H, self.day, self.d = beta, lam0, H, day, d

    def _hazard(self, X, w):
        return self.lam0 * np.exp(0.3 * X[:, 0] - self.beta * w)

    def sample(self, n: int, seed: int) -> pd.DataFrame:
        rng = np.random.default_rng(seed)
        X = rng.normal(0, 1, (n, self.d)); treat = (rng.random(n) < 0.5).astype(int)
        T = rng.exponential(1 / self._hazard(X, treat))
        df = pd.DataFrame({"treat": treat, "time": np.minimum(T, self.H),
                           "event": (T <= self.H).astype(int), "y": (T > self.day).astype(int)})
        df[[f"x{j}" for j in range(self.d)]] = X
        return df

    def ground_truth(self) -> GroundTruth:
        rng = np.random.default_rng(_ORACLE_SEED)
        X = rng.normal(0, 1, (_ORACLE_N, self.d))
        s1 = np.exp(-self._hazard(X, 1) * self.day); s0 = np.exp(-self._hazard(X, 0) * self.day)
        return GroundTruth(ate=float((s1 - s0).mean()),
                           extra={"estimand": f"S(D{self.day}) difference", "hazard_ratio": float(np.exp(-self.beta))})
