"""Criteo Uplift validation (LYRA §10) — the SAME incrementality estimator on real large-scale data.

Runs `lyra.incrementality` against the **Criteo Uplift** dataset (Diemert et al. 2018) — a 13.9M-row RCT
purpose-built for incrementality. *No ground truth* here (real data), so the value is showing the estimator
**behaves sensibly at scale** (a small, highly-significant lift — the Lewis–Rao story), not coverage.

The dataset is **not vendored** (≈300 MB). `load_sample` streams a balanced systematic sample from Hugging
Face once and caches it under `validation/.cache/` (keep that out of version control). The file is sorted by
treatment, so we sample *across* chunks to get both arms.
"""

from __future__ import annotations

import pathlib

import pandas as pd

URL = "https://huggingface.co/datasets/criteo/criteo-uplift/resolve/main/criteo-research-uplift-v2.1.csv.gz"
CACHE = pathlib.Path(__file__).resolve().parent / ".cache" / "criteo_sample.parquet"
FEATURES = [f"f{j}" for j in range(12)]


def load_sample(frac: float = 0.04, refresh: bool = False) -> pd.DataFrame:
    """A balanced ~560k-row sample (cached). First call streams the full gz from HF (~1–2 min)."""
    if CACHE.exists() and not refresh:
        return pd.read_parquet(CACHE)
    parts = [ch.sample(frac=frac, random_state=i)
             for i, ch in enumerate(pd.read_csv(URL, compression="gzip", chunksize=1_000_000))]
    df = pd.concat(parts, ignore_index=True)
    CACHE.parent.mkdir(exist_ok=True)
    df.to_parquet(CACHE)
    return df


def validate(df: pd.DataFrame | None = None) -> dict:
    """Treatment-vs-control lift on visit & conversion + the exposure-based CACE (effect on the exposed)."""
    from lyra.incrementality import cace, lift
    if df is None:
        df = load_sample()
    t, c = df[df.treatment == 1], df[df.treatment == 0]
    out = {o: lift(t[o].to_numpy(), c[o].to_numpy()) for o in ("visit", "conversion")}
    out["visit_cace"] = cace(t["visit"].to_numpy(), c["visit"].to_numpy(), t["exposure"].to_numpy())
    return out
