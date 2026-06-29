# Causal measurement for music marketing — feasibility lab

> **Status:** incubation / feasibility. Self-contained under `labs/` — not part of the Lyra platform
> (`lyra/`, `tests/`, `chassis/`), but free to import `lyra` (the harness, estimators) when useful.
> **Goal of this lab:** test the *technical feasibility* of the startup idea before committing. When it
> matures, distill the methodology into **NB 11 (observational)** + promote estimators to `lyra/observational.py`.

## The idea
Measure the **causal impact of ad spend / campaigns for music releases on streams** — how many
*incremental* streams a campaign actually **caused**, vs streams that would have happened anyway.

## Why it's hard (the causal problem)
- **Observational, not randomized.** Labels/artists choose *which* releases to push and *how much* to spend.
  Bigger, more-anticipated releases get **both** more spend **and** more organic streams → **selection /
  confounding**. A naive "streams during the campaign" or "spend vs streams" regression is biased upward —
  the same Lewis–Rao trap as ad attribution (NB 12), one level harder.
- **No clean counterfactual.** You rarely get a holdout for a release, so you must **construct** the
  counterfactual: what would the streams have been without the campaign?

## Method shortlist (what we'll test for feasibility)
| Method | When it fits | Data it needs | Lib |
|---|---|---|---|
| **CausalImpact / BSTS** (Brodersen 2015) | one release/campaign, a clear window + control series | streams time series for the release + control tracks/markets | `pycausalimpact` / `tfp` / `pymc` |
| **Synthetic control / SDID** (Abadie; Arkhangelsky 2021) | one–few treated releases, a donor pool of comparable releases/markets | release × time panel | `pysyncon` / hand-rolled |
| **DiD / event study (staggered)** (Callaway–Sant'Anna; Sun–Abraham) | many releases, campaigned vs not, varying timing | release × time panel + treatment timing | `differences` / `pyfixest` |
| **Geo-lift / matched-market** (the ad-measurement gold standard) | spend varies by geo/market | streams × market × day + spend × market | `GeoLift`-style / hand-rolled |
| **Panel DML** (double ML) | continuous spend, rich controls, want an elasticity | release/artist/time FE + features + spend | `doubleml` / `econml` |
| **IV / LATE** | an instrument for spend (auction shocks, budget pacing) | the instrument | `linearmodels` |

## The plan
1. **Data audit** — grain, coverage, the treatment definition, candidate control units. (`notebooks/01_data_audit`)
2. **Pick the design(s)** the data can actually support — likely CausalImpact and/or synthetic control + DiD first.
3. **Feasibility notebooks** — run the candidates, sanity-check, document what works and what breaks.
4. **Validate on a synthetic DGP** with known lift (the Lyra trick — `lyra.harness`) so we trust the
   *estimator* before trusting the *data*.
5. **Distill** → NB 11 (observational) + `lyra/observational.py`. See [`FINDINGS.md`](FINDINGS.md).

## Open questions (to scope — answers shape the method)
- **Data grain?** release × day streams? per-market? per-platform (Spotify/Apple/YouTube)?
- **Spend data?** per campaign? per geo? daily? which channels (Meta/Google/TikTok/playlist pitching)?
- **Any natural experiments?** geo holdouts, staggered rollouts, platform features, budget caps/pacing.
- **The decision it serves?** "should this release get a campaign / how much / where / when?"

## Layout
- `data/` — raw (gitignored) + processed. Drop source files here.
- `notebooks/` — exploration + feasibility (jupytext `.py:percent`, like the main curriculum).
- `src/` — reusable loaders / estimators for this lab.
- `FINDINGS.md` — running log of learnings → feeds NB 11.
