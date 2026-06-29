"""Anytime-valid inference — confidence sequences for the live (replayed) dashboard.

Responsibility (T-41): time-uniform CIs that stay valid under continuous peeking, so the dashboard
can show a band that narrows as simulated days accumulate without inflating type-I error.
Methods (``inference.anytime_valid.method``): ``asymptotic_cs`` (default) | ``msprt``; ``rho2``
tunes where the sequence is tightest.

This is a **crown-jewel deliverable** (STACK.md): there is no de-facto Python package, so we
implement the estimator and validate its coverage against ground truth. We use the **asymptotic
confidence sequence** of Waudby-Smith, Ramdas et al. — a roughly $\\log t$ widening of the usual
CLT interval that is *time-uniform*: with probability $\\ge 1-\\alpha$ the interval covers the truth
at **every** sample size simultaneously, so you may peek/stop whenever you like.

For a running mean with sample SD $\\hat\\sigma_t$ over $t$ observations, the CS half-width is

    h_t = \\hat\\sigma_t * sqrt( (2 (t ρ² + 1)) / (t² ρ²) * log( sqrt(t ρ² + 1) / α ) ).

Applied to a difference-in-means (the ATE), the half-width is the fixed-$n$ standard error times the
same time-uniform multiplier — the multiplier is the explicit *price of peeking* (always $> z_{α/2}$)
and the band still shrinks at $\\sim\\sqrt{\\log t / t}$.

Caution (longitudinal "Peeking 2.0", Spotify): with many observations per unit the increments are
correlated; here we form the sequence over the **per-user** outcome (one observation per user up to
day $t$), so the unit is the user and the cumulative-by-day series is a valid mean process. Refs:
Johari et al. 2017; Howard/Ramdas et al. 2021; Waudby-Smith et al. 2023.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from inference.base import Effect, user_outcomes

DEFAULT_RHO2 = 0.05


def cs_multiplier(t: int, alpha: float, rho2: float = DEFAULT_RHO2) -> float:
    """Time-uniform multiplier on the standard error (replaces $z_{1-α/2}$ in a fixed-$n$ CI)."""
    if t < 1:
        return float("inf")
    a = t * rho2
    return math.sqrt(2.0 * (a + 1.0) / (a) * math.log(math.sqrt(a + 1.0) / alpha))


def _diff_in_means(treat: np.ndarray, control: np.ndarray):
    n_t, n_c = treat.size, control.size
    point = float(treat.mean() - control.mean())
    # unbiased sample variances; guard tiny arms
    var_t = float(treat.var(ddof=1)) if n_t > 1 else 0.0
    var_c = float(control.var(ddof=1)) if n_c > 1 else 0.0
    se = math.sqrt(var_t / max(n_t, 1) + var_c / max(n_c, 1))
    return point, se, n_t, n_c


def estimate(df: pd.DataFrame, alpha: float = 0.05, rho2: float = DEFAULT_RHO2) -> Effect:
    """Anytime-valid confidence-sequence interval for the ATE at the current sample size.

    Same point estimate as the naive difference-in-means, but the interval is time-uniform — safe to
    report after peeking. Wider than the fixed-horizon CI by the ``cs_multiplier`` (the peeking tax).
    """
    treat = df.loc[df["arm"] == "treatment", "outcome"].to_numpy(dtype=float)
    control = df.loc[df["arm"] == "control", "outcome"].to_numpy(dtype=float)
    if treat.size == 0 or control.size == 0:
        raise ValueError("anytime_valid.estimate: need both treatment and control users")

    point, se, n_t, n_c = _diff_in_means(treat, control)
    mult = cs_multiplier(n_t + n_c, alpha, rho2)
    half = mult * se
    return Effect(
        estimator="anytime_valid_cs",
        point=point,
        ci_low=point - half,
        ci_high=point + half,
        se=se,
        n_treatment=n_t,
        n_control=n_c,
        extra={"rho2": rho2, "cs_multiplier": mult},
    )


def estimate_sequence(
    assignments: pd.DataFrame,
    conversions: pd.DataFrame,
    horizon: int,
    alpha: float = 0.05,
    rho2: float = DEFAULT_RHO2,
) -> list[dict]:
    """Per-day confidence sequence over cumulative outcomes — the dashboard's always-valid band.

    ``assignments``: one row per assigned user (``user_id, arm``) — includes non-converters, so the
    arm denominators are right. ``conversions``: one row per conversion (``user_id, day, value``).
    Because the CS is time-uniform, the whole trajectory has joint coverage — peeking at any/every
    day is safe (this is the property a fixed-horizon CI lacks).
    """
    arms = assignments[assignments["arm"].isin(["treatment", "control"])][["user_id", "arm"]]
    out = []
    for d in range(horizon):
        upto = conversions[conversions["day"] <= d].groupby("user_id")["value"].sum()
        merged = arms.copy()
        merged["outcome"] = merged["user_id"].map(upto).fillna(0.0)
        treat = merged.loc[merged["arm"] == "treatment", "outcome"].to_numpy(float)
        control = merged.loc[merged["arm"] == "control", "outcome"].to_numpy(float)
        if treat.size < 5 or control.size < 5:
            continue
        point, se, n_t, n_c = _diff_in_means(treat, control)
        half = cs_multiplier(n_t + n_c, alpha, rho2) * se
        out.append({"day": d, "point": round(point, 6),
                    "ci_low": round(point - half, 6), "ci_high": round(point + half, 6),
                    "n": n_t + n_c})
    return out


def sequence_from_log(events_dir, experiment_id: str, horizon: int, alpha: float = 0.05,
                      rho2: float = DEFAULT_RHO2) -> list[dict]:
    """Convenience: load assignments + conversions and build the per-day CS."""
    from inference.base import experiment_assignments, experiment_conversions

    return estimate_sequence(
        experiment_assignments(events_dir, experiment_id),
        experiment_conversions(events_dir, experiment_id),
        horizon, alpha=alpha, rho2=rho2,
    )


def estimate_from_log(events_dir, experiment_id: str, alpha: float = 0.05,
                      rho2: float = DEFAULT_RHO2) -> Effect:
    return estimate(user_outcomes(events_dir, experiment_id), alpha=alpha, rho2=rho2)
