"""Streaming DGP (from notebook 1): a catalog of releases and their daily streams. Each track spikes at
release and decays exponentially; popularity × quality are log-normal (heavy-tailed → a few hits dominate);
Friday/weekend seasonality; rare viral bumps; over-dispersed NegBinomial counts. FOUNDATIONS.md §2.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from mml.primitives import nb_draw, viral_bump

DEFAULTS = dict(
    n_artists=30, tracks_lambda=3.0, start="2024-01-01", end="2025-12-31", min_observed=14,
    pop_mu=np.log(2000), pop_sigma=1.0, qual_mu=0.0, qual_sigma=0.85,
    halflife_med=25.0, halflife_sigma=0.40, halflife_qual_beta=0.15,
    dow_raw=np.array([0.95, 0.93, 0.95, 1.00, 1.18, 1.14, 1.06]),
    viral_p_track=0.30, viral_n_lambda=1.2, viral_mag_lo=3.0, viral_mag_hi=18.0, viral_tau=9.0, nb_r=6.0,
)


def simulate_catalog(seed: int = 0, **overrides):
    """Returns (tracks, panel): a release table and a long daily-streams panel (track × day)."""
    P = {**DEFAULTS, **overrides}
    rng = np.random.default_rng(seed)
    dates = pd.date_range(P["start"], P["end"], freq="D")
    dow_mult = P["dow_raw"] / P["dow_raw"].mean()

    pop = rng.lognormal(P["pop_mu"], P["pop_sigma"], P["n_artists"])
    release_hi = dates[-1] - pd.Timedelta(days=P["min_observed"]); span = (release_hi - dates[0]).days
    rows, tid = [], 0
    for aidx in range(P["n_artists"]):
        for _ in range(1 + rng.poisson(P["tracks_lambda"])):
            q = rng.lognormal(P["qual_mu"], P["qual_sigma"])
            hl = P["halflife_med"] * np.exp(P["halflife_qual_beta"] * np.log(q)) * np.exp(rng.normal(0, P["halflife_sigma"]))
            rel = dates[0] + pd.Timedelta(days=int(rng.integers(0, span + 1)))
            rows.append(dict(track_id=f"T{tid:03d}", artist_id=f"A{aidx:02d}", peak=pop[aidx] * q,
                             quality=q, half_life=hl, release_date=rel)); tid += 1
    tracks = pd.DataFrame(rows)

    panel = []
    for _, tr in tracks.iterrows():
        obs = dates[dates >= tr.release_date]; a = np.arange(len(obs))
        trng = np.random.default_rng(abs(hash(tr.track_id)) % (2**32))
        mu = (tr.peak * np.exp(-np.log(2) / tr.half_life * a) * dow_mult[obs.weekday.to_numpy()]
              * (1.0 + viral_bump(len(a), trng, p_track=P["viral_p_track"], n_lambda=P["viral_n_lambda"],
                                  mag_lo=P["viral_mag_lo"], mag_hi=P["viral_mag_hi"], tau=P["viral_tau"])))
        panel.append(pd.DataFrame(dict(date=obs, track_id=tr.track_id, artist_id=tr.artist_id,
                                       days_since_release=a, streams=nb_draw(mu, P["nb_r"], trng), mu=mu)))
    return tracks, pd.concat(panel, ignore_index=True)
