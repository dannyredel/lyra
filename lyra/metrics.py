"""Typed, governed metrics — the metric layer (LYRA §4). Promoted from ``notebooks/03_metrics``.

A metric is a **versioned, typed object**; the ``type`` selects the correct variance — defining the
metric right is *what makes the inference right* (Layer 4 → Layer 5). Each metric implements the
`Estimator` Protocol, so the harness certifies it and the scorecard can bind to a metric **version**.

Types → estimators: ``mean`` → Welch · ``proportion`` → two-proportion z · ``ratio`` → **delta method**
(Deng–Knoblich–Lu 2018; user-level, robust to the random/correlated denominator). ``CupedMetric`` is a
variance-reduction wrapper (pre-period covariate). ``NaiveRatioMetric`` is kept as a *documented foil* —
the session-iid variance that under-covers — used to show the A/A gate catching it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from lyra.protocols import EstimatorResult

Z = 1.959963985


@dataclass(frozen=True)
class MetricSpec:
    """A governed metric definition. ``type`` drives the variance; ``version`` makes tests comparable."""

    name: str
    version: int
    type: str                 # "mean" | "proportion" | "ratio" | "quantile" | "count"
    cls: str                  # "primary" | "secondary" | "guardrail"
    direction: str = "up"     # "up" = higher is better


def _result(name, d, se, estimand="ATE", **meta) -> EstimatorResult:
    p = float(2 * (1 - stats.norm.cdf(abs(d) / se))) if se > 0 else float("nan")
    return EstimatorResult(name, float(d), (d - Z * se, d + Z * se), se=float(se), estimand=estimand,
                           p_value=p, method_metadata=meta)


class MeanMetric:
    name, estimand, requires = "mean", "ATE", set()

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        t = df.loc[df.treat == 1, "y"].to_numpy(float); c = df.loc[df.treat == 0, "y"].to_numpy(float)
        se = np.sqrt(t.var(ddof=1) / t.size + c.var(ddof=1) / c.size)
        return _result("mean", t.mean() - c.mean(), se)


class ProportionMetric:
    """Two-proportion z — the Bernoulli variance p(1-p)."""

    name, estimand, requires = "proportion", "ATE", set()

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        t = df.loc[df.treat == 1, "y"].to_numpy(float); c = df.loc[df.treat == 0, "y"].to_numpy(float)
        p1, p0 = t.mean(), c.mean()
        se = np.sqrt(p1 * (1 - p1) / t.size + p0 * (1 - p0) / c.size)
        return _result("proportion", p1 - p0, se, estimand="risk_difference")


def _delta_arm(num, den):
    K, nbar, theta = len(num), den.mean(), num.sum() / den.sum()
    var = (num.var(ddof=1) - 2 * theta * np.cov(num, den)[0, 1] + theta ** 2 * den.var(ddof=1)) / (K * nbar ** 2)
    return theta, var


class RatioMetric:
    """Ratio metric (e.g. conv/session) via the **delta method** at the randomization unit (user)."""

    name, estimand, requires = "ratio", "ATE", {"numerator", "denominator"}

    def __init__(self, num: str = "conversions", den: str = "sessions"):
        self.num, self.den = num, den

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        a, b = df[df.treat == 1], df[df.treat == 0]
        t1, v1 = _delta_arm(a[self.num].to_numpy(float), a[self.den].to_numpy(float))
        t0, v0 = _delta_arm(b[self.num].to_numpy(float), b[self.den].to_numpy(float))
        return _result("ratio", t1 - t0, np.sqrt(v1 + v0), estimand="ratio_difference")


class NaiveRatioMetric:
    """WRONG-on-purpose foil: treats every session as iid Bernoulli → under-covers under user clustering."""

    name, estimand, requires = "ratio_naive", "ATE", {"numerator", "denominator"}

    def __init__(self, num: str = "conversions", den: str = "sessions"):
        self.num, self.den = num, den

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        def arm(s):
            N = s[self.den].sum(); th = s[self.num].sum() / N; return th, th * (1 - th) / N
        t1, v1 = arm(df[df.treat == 1]); t0, v0 = arm(df[df.treat == 0])
        return _result("ratio_naive", t1 - t0, np.sqrt(v1 + v0), estimand="ratio_difference")


class CupedMetric:
    """Variance reduction: subtract a pre-period covariate's predictable part (unbiased, cuts ~1-ρ²)."""

    name, estimand, requires = "cuped", "ATE", {"pre_period"}

    def __init__(self, pre: str = "x_pre"):
        self.pre = pre

    def estimate(self, df: pd.DataFrame, config: dict | None = None) -> EstimatorResult:
        x, y = df[self.pre].to_numpy(float), df.y.to_numpy(float)
        theta = np.cov(y, x)[0, 1] / x.var(ddof=1)
        ya = y - theta * (x - x.mean())
        t, c = ya[df.treat == 1], ya[df.treat == 0]
        se = np.sqrt(t.var(ddof=1) / t.size + c.var(ddof=1) / c.size)
        return _result("cuped", t.mean() - c.mean(), se, theta=float(theta))


REGISTRY = {"mean": MeanMetric, "proportion": ProportionMetric, "ratio": RatioMetric}


def estimator_for(spec: MetricSpec):
    """Route a metric spec to its type-correct estimator (Layer 4 → Layer 5)."""
    return REGISTRY[spec.type]()
