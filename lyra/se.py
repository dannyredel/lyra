"""Cluster-robust standard errors (LYRA §5/§6). Promoted from ``notebooks/04_cluster_robust_se``.

When units cluster and treatment is assigned at/correlated with the cluster level, the naive iid SE is
far too small (the **Moulton** inflation). The fix ladder — all built by hand against a known truth:
**CV1** (the cluster sandwich) → **CV2** (bias-reduced, "HC2 for clusters") → **CV3** (leave-one-cluster-out
jackknife, "HC3") → the **wild cluster bootstrap** (the few-clusters fix). Use $t_{G-1}$ critical values.

`ClusterOLS` implements the `Estimator` Protocol so the harness certifies size/coverage vs `ClusteredDGP`.
Cross-checked against `statsmodels` ``cov_type="cluster"`` (CV1) and HC1/HC3 at $G=N$ (the invariant).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from lyra.protocols import EstimatorResult

WEBB = np.sqrt([0.5, 1.0, 1.5])


def _design(df, x="x", y="y"):
    X = np.column_stack([np.ones(len(df)), df[x].to_numpy(float)])
    yv = df[y].to_numpy(float)
    XtXi = np.linalg.inv(X.T @ X); b = XtXi @ X.T @ yv
    return X, yv, b, yv - X @ b, XtXi


def _groups(df, cluster="g"):
    return [idx for _, idx in df.groupby(cluster).indices.items()]


def se_iid(df, **k):
    X, y, b, u, XtXi = _design(df, **{a: k[a] for a in ("x", "y") if a in k})
    n, kk = X.shape
    return b[1], float(np.sqrt(((u @ u) / (n - kk)) * XtXi[1, 1]))


def se_cv1(df, x="x", y="y", cluster="g"):
    X, yv, b, u, XtXi = _design(df, x, y); n, k = X.shape; gi = _groups(df, cluster); G = len(gi)
    meat = sum(np.outer(X[i].T @ u[i], X[i].T @ u[i]) for i in gi)
    c = (G / (G - 1)) * ((n - 1) / (n - k))
    return b[1], float(np.sqrt((c * XtXi @ meat @ XtXi)[1, 1]))


def se_cv2(df, x="x", y="y", cluster="g"):
    X, yv, b, u, XtXi = _design(df, x, y); k = X.shape[1]; meat = np.zeros((k, k))
    for idx in _groups(df, cluster):
        Xg = X[idx]; Mgg = np.eye(len(idx)) - Xg @ XtXi @ Xg.T
        w, Q = np.linalg.eigh(Mgg); Mhalf = Q @ np.diag(1 / np.sqrt(np.clip(w, 1e-10, None))) @ Q.T
        sg = Xg.T @ (Mhalf @ u[idx]); meat += np.outer(sg, sg)
    return b[1], float(np.sqrt((XtXi @ meat @ XtXi)[1, 1]))


def se_cv3(df, x="x", y="y", cluster="g"):
    X, yv, b, u, XtXi = _design(df, x, y); gi = _groups(df, cluster); G = len(gi); bs = []
    for idx in gi:
        Xg = X[idx]; Mgg = np.eye(len(idx)) - Xg @ XtXi @ Xg.T
        bs.append(b - XtXi @ Xg.T @ np.linalg.solve(Mgg, u[idx]))
    bs = np.array(bs); bb = bs.mean(0)
    V = (G - 1) / G * sum(np.outer(z - bb, z - bb) for z in bs)
    return b[1], float(np.sqrt(V[1, 1]))


_SE = {"iid": se_iid, "CV1": se_cv1, "CV2": se_cv2, "CV3": se_cv3}


class ClusterOLS:
    """OLS slope on ``x`` with a chosen variance estimator; CI uses t(G-1) (normal for iid)."""

    name, estimand, requires = "cluster_ols", "ATE", {"cluster"}

    def __init__(self, vcov: str = "CV1", x: str = "x", y: str = "y", cluster: str = "g"):
        self.vcov, self.x, self.y, self.cluster = vcov, x, y, cluster

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        if self.vcov == "iid":
            b, se = se_iid(df, x=self.x, y=self.y); crit = 1.959963985
        else:
            b, se = _SE[self.vcov](df, x=self.x, y=self.y, cluster=self.cluster)
            crit = float(stats.t.ppf(0.975, df[self.cluster].nunique() - 1))
        p = float(2 * (1 - stats.norm.cdf(abs(b) / se))) if se > 0 else float("nan")
        return EstimatorResult(f"cluster_ols[{self.vcov}]", float(b), (b - crit * se, b + crit * se),
                               se=se, estimand="coef", p_value=p, method_metadata={"vcov": self.vcov})


def wild_cluster_bootstrap(df, x="x", y="y", cluster="g", B=999, weights="auto", seed=0, beta0=0.0):
    """WCR restricted wild cluster bootstrap of the cluster-robust t for H0: beta = beta0.

    Returns the symmetric bootstrap p-value. Rademacher weights (Webb 6-point auto-selected for G<10).
    """
    rng = np.random.default_rng(seed)
    X, yv, b, u, XtXi = _design(df, x, y); n, k = X.shape; gi = _groups(df, cluster); G = len(gi)
    _, se1 = se_cv1(df, x, y, cluster); t0 = (b[1] - beta0) / se1
    # restricted fit: y = a + beta0*x + u_r  →  residuals around the H0 line
    a_r = (yv - beta0 * X[:, 1]).mean(); u_r = yv - beta0 * X[:, 1] - a_r
    use_webb = weights == "webb" or (weights == "auto" and G < 10)
    pool = np.r_[WEBB, -WEBB] if use_webb else np.array([-1.0, 1.0])
    c = (G / (G - 1)) * ((n - 1) / (n - k)); cnt = 0
    for _ in range(B):
        v = rng.choice(pool, G)
        ys = a_r + beta0 * X[:, 1] + np.concatenate([v[j] * u_r[gi[j]] for j in range(G)])
        bs = XtXi @ X.T @ ys; us = ys - X @ bs
        meat = sum(np.outer(X[i].T @ us[i], X[i].T @ us[i]) for i in gi)
        cnt += abs((bs[1] - beta0) / np.sqrt((c * XtXi @ meat @ XtXi)[1, 1])) >= abs(t0)
    return cnt / B
