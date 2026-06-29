"""Causal ad-spend → streams DGP (from notebook 3). A geo panel where paid spend is **endogenous**
(front-loaded into the post-launch decay phase), so naive spend↔streams correlation is negative and a
naive estimator sign-flips. ``ground_truth`` exposes the planted lift / iROAS so any estimator can be
scored. Incremental streams = ``Hill(adstock(spend))`` per channel on top of an organic baseline.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from mml.primitives import adstock, hill

# Market sizes. France is the largest market and is held out as a CONTROL, so every treated market — even
# Germany — sits *inside* the convex hull of the controls. That keeps synthetic control / geo-lift clean on
# raw streams (a treated unit larger than all controls can't be synthesised from them — the convex-hull trap;
# good geo design uses controls that bracket the treated markets).
GEO = {"DE": 1.00, "FR": 1.10, "ES": 0.70, "IT": 0.65, "NL": 0.45, "SE": 0.40,
       "PL": 0.50, "BE": 0.30, "AT": 0.28, "PT": 0.25, "IE": 0.20, "DK": 0.22}
CONTROL = ["FR", "NL", "PT", "DK"]
COHORTS = {28: ["DE", "ES"], 42: ["IT", "PL", "BE"], 56: ["SE", "AT", "IE"]}


def make_causal_panel(seed: int = 0, *, base_peak: float = 60_000.0, half_life: float = 30.0,
                      theta=None, vmax=None, alpha: float = 1.0, kappa: float = 600.0):
    """Country × day panel with confounded staggered ad spend. Returns (df, meta). The truth is in
    ``organic`` / ``incremental`` columns (and ``ground_truth``). ``vmax`` is calibrated so the all-treated
    lift ≈ 16% with a clearly negative *naive* national correlation (the confounding money-shot); pass a
    smaller/larger ``vmax`` to dial the effect (×0.31 → the raw build-script ~5% lift)."""
    rng = np.random.default_rng(seed)
    theta = theta or {"tiktok": 0.55, "instagram": 0.45}
    vmax = vmax or {"tiktok": 11000.0, "instagram": 5600.0}
    days = pd.date_range("2026-03-06", periods=119, freq="D"); T = len(days); a = np.arange(T)
    start_day = {c: g for g, cs in COHORTS.items() for c in cs}
    for c in CONTROL:
        start_day[c] = None
    lam = np.log(2) / half_life
    weekly = np.array([0.95, 0.93, 0.95, 1.00, 1.18, 1.14, 1.06]); weekly /= weekly.mean()
    nat_shock = np.exp(np.cumsum(rng.normal(0, 0.03, T)) + rng.normal(0, 0.02, T))   # shared market trend

    rows = []
    for c, size in GEO.items():
        organic = base_peak * size * np.exp(-lam * a) * weekly[days.weekday] * nat_shock * np.exp(rng.normal(0, 0.05, T))
        sd = start_day[c]
        spend = {ch: np.zeros(T) for ch in theta}
        if sd is not None:                                   # spend ramps in, then decays — into the tail
            prof = np.where(a >= sd, np.minimum((a - sd + 1) / 7, 1) * np.exp(-(np.maximum(a - sd - 7, 0)) / 70), 0)
            spend["tiktok"] = prof * (120 * size) * np.exp(rng.normal(0, 0.1, T))
            spend["instagram"] = prof * (80 * size) * np.exp(rng.normal(0, 0.1, T))
        incr = np.zeros(T)
        for ch in theta:
            incr += vmax[ch] * size * hill(adstock(spend[ch], theta[ch]), alpha, kappa)
        streams = rng.poisson(np.maximum(organic + incr, 0.1)).astype(float)
        for i in range(T):
            rows.append(dict(country=c, size=size, date=days[i], t=i, treated=int(sd is not None),
                             start_day=(sd if sd else -1), post=int(sd is not None and i >= sd),
                             tiktok=spend["tiktok"][i], instagram=spend["instagram"][i],
                             organic=organic[i], incremental=incr[i], streams=streams[i]))
    df = pd.DataFrame(rows)
    df["spend"] = df.tiktok + df.instagram
    meta = dict(days=days, control=CONTROL, cohorts=COHORTS, start_day=start_day,
                theta=theta, vmax=vmax, alpha=alpha, kappa=kappa)
    return df, meta


def ground_truth(df: pd.DataFrame, meta: dict | None = None) -> dict:
    """Planted lift by scope + iROAS (streams per €) — what every estimator on this panel tries to recover."""
    tp = df[(df.treated == 1) & (df.post == 1)]
    de = df[(df.country == "DE") & (df.t >= 28)]
    lift = lambda d: float(d.incremental.sum() / d.organic.sum())
    return {
        "national": lift(df), "all_treated": lift(tp), "de": lift(de),
        "true_iroas": float(tp.incremental.sum() / tp.spend.sum()),
        "spend_total": float(df.spend.sum()), "incremental_total": float(tp.incremental.sum()),
    }
