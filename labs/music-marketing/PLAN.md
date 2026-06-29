# PLAN — chaptered notebooks for the music-marketing causal lab

> Harmonizes three inputs: **FOUNDATIONS.md** (the methods + library research), the **5 existing
> notebooks** (the build-the-methods arc), and **REPLICATE.md / the identification study** (the
> stress-test-feasibility harness). Goal: a clean chapter structure that recycles what exists, adds the
> REPLICATE gate, and feeds the main curriculum's **NB 11 (observational)** + `lyra/observational.py`.

## The thesis (why this lab exists)
Music marketing measurement is **observational + data-poor**: few releases, channels co-launched
(collinearity), short windows, spend endogenous to expected success, coarse Spotify geo. The decades-old
methods (DiD, synthetic control, MMM, geo-lift) aren't in question — *whether they survive music's data
poverty and still emit a usable interval* is. So every notebook **plants ground truth and scores recovery**
— the same discipline as the main Lyra platform. The **identification study is the GO/KILL gate.**

## Two tracks, one structure
- **Track M (methods):** demonstrate each estimator on one synthetic dataset, scored vs truth. ← your NB 1–5.
- **Track R (REPLICATE / feasibility):** the Monte-Carlo recovery harness across a scarcity grid → verdict.
  ← the `vega/` identification study; **build it on `lyra.harness`** (or port the `vega/` package).

## Proposed chapters (recycle vs new)

| Ch | Title | Source | Action |
|---|---|---|---|
| **0** | `mml/` shared module — DGP + primitives (release-decay, adstock, Hill, NB-counts, viral, Gini) | NB 1–4 inline dupes | **NEW (small)** — extract once; kills the 4× copy-paste (mirrors `lyra.dgp`) |
| **1** | The streaming world — releases & daily streams, descriptive | NB 1 `music_streams_dgp` | **RECYCLE** (light: import `mml`) |
| **2** | A label roster — 10 artists / 40 releases / 2026 calendar (the canonical scenario) | NB 2 `label_campaign_2026` | **RECYCLE** (light) |
| **3** | The causal ladder — ad spend → streams; naive sign-flip → OLS→DiD→SC→SDID→AugSCM→BSC→MMM | NB 3 `causal_ad_spend` | **RECYCLE** (the centerpiece — keep) |
| **4** | Roster-scale MMM — hierarchical partial pooling + experiment calibration + budget opt | NB 4 `hierarchical_mmm` | **RECYCLE** (light) |
| **5** | Geo-lift & inference trust — are the tools interchangeable? FPR / coverage / power | NB 5 `geolift_calibration` | **RECYCLE + FIX** (add the missing `5_build_notebook.py` for parity) |
| **6** | **Identification study I — the harness** — plant channel mROAS → NB-MMM + geo anchor → score recovery (bias / coverage / keep-cut acc / κ-detection); one fit, one MC cell | REPLICATE.md + identification-study.md | ✅ **BUILT** — `mml/harness.py` (PyMC rebuild) + `ch6_identification_harness.ipynb` |
| **7** | **Identification study II — the verdict** — H1–H5 ledger across the scarcity grid (N×ρ×κ×endo×geo) · κ=0 null → **GO/RESCOPE/KILL** | identification-study.md + report_gating.md + FINDINGS.md | ✅ **BUILT** — `ch7_identification_verdict.ipynb` + `run_grid.py` → `outputs/grid_results.json`; verdict in `REPORT.md`. (misspec battery / low-spend mitigation still TODO) |
| **→** | **Distill → NB 11 (observational)** + `lyra/observational.py` | all of the above | ✅ **DONE** — `notebooks/11_observational.py` (selection on observables → hidden confounder → sensitivity analysis → ground-truth meta-validation → music-lab tie-in) + `lyra/observational.py` (DML, robustness value, OVB, E-value) |

## What we recycle vs leave alone
- **Recycle (Track M):** NB 1–4 with a light edit to import the shared `mml/` module; NB 3 is the
  centerpiece, keep it. NB 5 recycle **+ add its build script** (it's the only one with no `.py` — not
  regenerable today).
- **New (the REPLICATE gate):** Ch 6–7 + the `mml/` module. This is the part that directly answers
  "is this technically feasible given the data scarcity?"
- **Context only — do NOT turn into notebooks:** `counterpoint-idea-A`, `counterpoint-idea-E`,
  `music-ecosystem-actors`, `*-pitch.html`, `concept-brief`, `technical-proposal`. They frame *what the
  methods must prove* (decision-grade per-channel ROAS with usable intervals, work with few releases via
  pooling, identify the organic→paid multiplier κ) — keep as the brief, not as code.
- **`report_gating.md` + `FINDINGS.md`** = the *content* of Ch 7 (the verdict + the still-pending
  decision-grade M≥100 runs). Fold in, don't keep separate.

## Build hygiene (harmonization wins)
1. **One DGP, imported everywhere** (`mml/`), with `ground_truth()` exposed — exactly the `lyra.dgp` pattern.
2. **Recovery as asserted tests**, not just charts (CLAUDE.md's non-negotiable): the naive sign-flip, the
   pooling RMSE win, the κ=0 false-positive control → a small `labs/music-marketing/tests/`.
3. **Reuse `lyra.harness`** for Track R so the music lab and the platform share one recovery engine.
4. **Compute discipline:** the harness runs at *exploratory* M in the notebook (verdict already
   directionally GO); the full M≥100 grid is an **offline job** (GPU → hours; CPU → days). Don't block the
   notebook on it.

## The feasibility verdict so far (from FINDINGS, M=4 smoke + converged spot checks)
GO cell recovers: |rel bias| ≈ 0.13 · 80% coverage ≈ 0.88 · keep/cut acc ≈ 0.88 · κ excludes 0 in ~100% ·
pooling cuts RMSE ~85% · geo tightens ~20%. Known weak point: **low-spend channels (Spotify, Plugger) bias
upward**; Spotify straddles the break-even bar ~75%. Pending: the M≥100 decision-grade grid (compute-bound).

## Open forks (need your call — see the questions)
1. **The `vega/` harness package** — share it (we port/adapt) or **build Ch 6–7 fresh on `lyra.harness`** +
   the music DGP? (It's referenced in REPLICATE.md but not in the pasted files.)
2. **Anchor outcome** — stay on **Idea-A (streams**, what's already built) for the feasibility proof, or
   also spike **Idea-E (tickets**, the stronger business bet per the validation reports)?
3. **Refactor depth** — extract the shared `mml/` module now (recommended), or keep notebooks self-contained?
