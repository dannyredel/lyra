# Harness build — Ch6–7 identification study (COMPLETE)

**DONE.** Engine `mml/harness.py` built + calibrated; Ch6 (harness driver) + Ch7 (verdict grid) executed
clean with figures; `REPORT.md` written for the Claude project. Final calibration: **spotify €5
(borderline/straddles)**, balanced spend shares, `alpha_nb~HalfNormal(1000)`, median point estimate.

**Final M=10 grid verdict (`outputs/grid_results.json`):** keep/cut is **GO across the whole realistic
grid** — 1.00 on easy cells → **0.85 worst case** (N=18, ρ=0.85, no geo), **no KILL**. Bias low everywhere
(0.04–0.08). κ detected 100% / null-FP 0%. Pooling cuts RMSE ~72%. The GO/RESCOPE *labels* flip on H2
(coverage), which is conservative + noisy at M=10 → certifying it is the pending **M≥100** job. Framing is
**honest exploratory** (keep/cut erosion is the signal, not the noisy labels). REPLICATE-faithful:
reproduces design + GO-cell behavior + the Spotify-straddle weak point; deltas = exploratory M, PyMC
rebuild, correct-spec only (no misspec battery / low-spend mitigation yet).

**Possible next steps (not done):** M≥100 decision-grade run; misspec battery (REPLICATE cell 8);
make `geo_prior` simulate a real randomized-holdout panel; distill → NB 11 + `lyra/observational.py`.

---
### (historical resume note below — kept for the calibration trail)

## What we're building (reminder)
Track R / REPLICATE — the **Monte-Carlo recovery harness** (PyMC rebuild of the missing `vega/` package):
plant per-channel mROAS + κ → fit a hierarchical NB-MMM → score recovery → repeat M× across a scarcity
grid → **GO / RESCOPE / KILL** via the H1–H5 ledger. Ch6 = the harness (driver+inspection); Ch7 = the
verdict grid. Then distill → NB 11 observational + `lyra/observational.py`.

## `mml/harness.py` — current design (all working)
- **DGP** `simulate_roster(scn, seed)`: 4 channels — meta €9 / tiktok €14 (KEEP) · spotify €4 / plugger €2.5
  (CUT), bar €6. Realized mROAS pinned to target **exactly** for any κ/γ (keep/cut truth never moves).
  Identification solved via: **per-release Dirichlet channel-mix** (concentration tied to ρ → ρ is the real
  collinearity knob) + **distinct flighting** (meta flat · tiktok hump · spotify ramp · plugger pulse).
  Endogeneity (γ): budget ∝ expected-success^γ. Poisson counts; organic decay + small weekly noise.
- **Model** `fit_mmm(estimator ∈ {nopool, pooled, pooled_geo})`: NB likelihood, **constrained baseline**
  (d~TruncN(0.18,0.04), logB~N(log max-streams, 0.25) — the fix that stopped media soaking the baseline),
  per-channel **skeptical prior** log(4) (below bar), partial pooling across releases, κ term, **geo anchor**
  = Potential on meta's mROAS. Point estimate = posterior **median** (robust to exp() skew).
- **scoring/MC/verdict**: `score_fit`, `run_cell` (convergence-gated on estimand R-hat≤1.05, div≤3%),
  `conclude` → H1–H5 ledger. Fast diagnostic `_diag.py` (oracle OLS, no MCMC) confirms design is identified
  (implied mROAS within 1–4% at every ρ).

## ✅ NOTEBOOKS BUILT (this session)
- **Ch6** `ch6_identification_harness.ipynb` — harness driver: plant world → naive straw-man → one fit
  (forest plot) → geo-anchor value → one MC cell → κ=0 null → one-cell GO ledger. Executed, 5 figures,
  cleaned of ABI noise. **Run with the `vega-mml` kernel** (registered = anaconda env w/ pymc/arviz;
  default `python3` kernel lacks them — that's why ch3+ never executed before).
- **Ch7** `ch7_identification_verdict.ipynb` — loads `outputs/grid_results.json` (from `run_grid.py`),
  renders the verdict frontier + degradation plots + per-channel bias + baseline ledger. Loads-and-plots
  only, so it's instant once the grid JSON exists.
- **`run_grid.py`** — offline grid job (one knob at a time off the GO baseline + κ=0 null) → JSON.
  `python run_grid.py 5` (~25 min, M=5 exploratory) / `20` for tighter. utf-8 stdout (Greek labels).
- **Env note:** `pip uninstall -y bottleneck numexpr` removes the numpy-2.x `_ARRAY_API` import noise for
  ALL notebooks (those pkgs are unusable under numpy 2.3.5 anyway; pandas works without them). Reversible.

## ✅ CALIBRATION LOCKED (this session)
Favorable corner **N=60, ρ=0.4** = clean **GO**: H1 bias 0.06 · H2 coverage 0.79 · H3 keep/cut 1.00 ·
H4 κ-null FP 0.00 · H5 pooling cuts RMSE 80%. Per-channel bias tiny (meta −0.02, tiktok −0.01, spo +0.08,
plu +0.04). Default cell **N=40, ρ=0.6** = **RESCOPE** (keep/cut 0.92, but low-ROAS magnitude bias). Gradient
for Ch7: GO (favorable) → RESCOPE (default) → KILL (hard: low N, high ρ, no geo).
Final fixes that locked it: balanced spend shares (0.30/0.28/0.22/0.20 — decouple ROAS from spend), organic
noise 0.025, **`alpha_nb ~ HalfNormal(1000)`** (was 2.0 — the over-coverage bug: too-tight dispersion prior
inflated intervals), `conclude()` keyed on H3 (keep/cut) for KILL-vs-RESCOPE. Build the notebooks now.

## Where calibration stands (history)
Last full MC (M=6, **old** shares 0.12/0.08, organic noise 0.04):
| H | metric | pooled_geo | bar | |
|---|---|---|---|---|
| H1 | median \|rel bias\| | **0.36** | <0.25 | FAIL (low-spend: spotify +0.54, plugger +0.93) |
| H2 | 80% coverage | **1.00** | 0.70–0.90 | FAIL (intervals too wide / over-conservative) |
| H3 | keep/cut acc | 0.83 | ≥0.80 | **PASS** |
| H4 | κ detected | 1.00 | power high | **PASS** (null FP not yet measured) |
| H5 | pooling RMSE cut | 39% (2.8 vs 4.6) | ≥20% | **PASS** |
Decision-relevant hypotheses pass; magnitudes/intervals on low-spend channels are the weak point (this *is*
REPLICATE's documented "Spotify straddles the bar" finding).

**Change made but NOT yet measured** (the MC to confirm it was the one interrupted): rebalanced shares to
0.18/0.14 + organic noise 0.04→0.025 — both aimed at H1 (less low-spend swamping) and H2 (tighter intervals).

## Next session — exact steps
1. **Run the MC** (already written): `python -u _mc.py` — GO cell + κ=0 null + verdict. See if H1/H2 now pass.
   (Driver files in the lab dir: `_mc.py`, `_smoke_fit.py` single-fit, `_diag.py` fast oracle. ~6–8 min.)
2. **If H1/H2 still fail:** either (a) accept a **RESCOPE** framing (honest: high-spend ROAS clean, low-spend
   magnitudes unreliable) or (b) give low-spend a touch more signal / less noise. Don't over-tune.
3. **Fix `conclude()` verdict logic** (noticed, not yet done): currently `recovery_ok = H1 and H3`, so an H1
   miss forces **KILL**. It should be **H3-driven** (keep/cut is the decision): H3 fail → KILL; H3 pass but
   H1/H2 fail → **RESCOPE**; all pass → GO.
4. **Build Ch6** (harness driver): plant truth → inspect roster + flighting → naive straw-man (wild bias) →
   geo prior → one fit (forest plot mROAS vs truth) → geo-anchor value (meta mis-ID'd without it) → one MC
   cell → **κ=0 null** (false-positive control). Pedagogic prose to ch1's bar.
5. **Build Ch7** (verdict grid): sweep N×ρ×κ×γ×geo at small M in-notebook (+ offline-job note for M≥100) →
   H1–H5 ledger table → GO/RESCOPE/KILL. Then distill learnings toward NB 11.

## Key learnings (so they aren't re-derived)
- Channels collinear because spend ∝ shared release budget → **per-release mix variation** is what identifies.
- Baseline-intercept prior must anchor to **launch peak** (max streams), not the mean — else media inflates.
- **NB, not Poisson**: the smooth baseline needs NB's dispersion cushion to absorb organic noise; pure
  Poisson diverges (R-hat 2.2, 500 divergences).
- Report the **median** mROAS; the exp() posterior is right-skewed so the mean over-states.
