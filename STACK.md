# STACK.md — Python go-to packages

**Principle (Daniel's preference): use the library, don't hand-roll the statistics.** Don't write
OLS, clustered SEs, a propensity model, or a DML estimator by hand when a battle-tested package
exists — reach for `statsmodels`/`linearmodels`/`econml`/etc. and spend our effort on the parts
that are genuinely novel (the simulator, the interference story, the anytime-valid layer). Hand-roll
**only** where no good package exists (flagged ⚠️ below) — and there, that's the deliverable.

> Two reasons to prefer libraries here: (1) speed + correctness (their SEs/edge-cases are tested),
> (2) credibility — "I used `linearmodels` PanelOLS" reads better than a bespoke regression. The
> exception is Vega's crown-jewel estimators: when the point *is* the method (anytime-valid CS,
> budget-split), implement it cleanly and test it against ground truth.

## Already in Daniel's toolbox (from prior projects)
`pandas` · `numpy` · `scipy` · `scikit-learn` · `statsmodels` · `linearmodels` · `econml` ·
`doubleml` · `pymc` · `bambi` · `dowhy` · `xgboost` · `polars` · `shap` · **`pylogit` / `pyblp`**
(discrete-choice / BLP demand, in the *Synthetic Demand* engine) · `pylogit`-style custom MNL
(*beesignal*). → We standardize on these; they're familiar and proven in your work.

## Core data / numerics
- **numpy**, **pandas** — lingua franca. **polars** for large ETL if needed. **scipy** — distributions,
  optimization, linear algebra (the engine's MNL sampling, calibration checks).

## Map: Vega module → package (don't hand-code these)
| Module / task | Go-to package | Note |
|---|---|---|
| `engine/choice.py` — MNL/nested-logit **sampling** | `numpy`/`scipy` (Gumbel draws) | we *generate* choices (params known); sampling is a few lines, no estimation lib needed |
| `engine/choice.py` — if we ever *estimate* the choice model | **`pylogit`** / **`xlogit`** (GPU) / **`pyblp`** | matches your Synthetic Demand work |
| `inference/naive.py` — diff-in-means + CI | **`statsmodels`** (`OLS`, `ttest_ind`) | trivial but use the lib's SEs |
| `inference/cluster.py` — cluster-robust | **`statsmodels`** `cov_type="cluster"` or **`pyfixest`** (`feols`, `vcov={"CRV1": "cluster_id"}`) | pyfixest for many FEs; aggregate-to-unit per Glovo rule |
| `lyra/se.py` — robust / cluster-robust / bootstrap SEs (**NB 04**) | **`pyfixest`** (CRV1/CRV3 + wild cluster bootstrap), **`wildboottest`** (Python port of R `fwildclusterboot`), `statsmodels` (HC0–HC3, `cov_type="cluster"`), `linearmodels` | the jackknife **CV3** + **wild cluster bootstrap** for few clusters; R refs: `sandwich`, `estimatr` (`lm_robust`), `fixest` ([SE guide](https://lrberge.github.io/fixest/articles/standard_errors.html)), `summclust`, `fwildclusterboot`. Read `sandwich-CL` + Cameron–Miller first (INDEX §02) |
| `inference/cuped.py` — variance reduction | **`statsmodels`**/**`linearmodels`** (regression adjustment) | CUPED = linear DML special case (see notation/dml.md) |
| `inference/budget_split.py` | built on `statsmodels` | ⚠️ design-specific; thin custom wrapper |
| `inference/incrementality.py` — ghost-ads lift | **`statsmodels`** (treatment-vs-holdout means/regression) | DR option via `econml` |
| `inference/hte.py` — CATE | **`econml`** (`LinearDML`, `CausalForestDML`, DR-learner) / **`doubleml`** / **`causalml`** | your existing causal-ML stack |
| `inference/ope.py` — IPS / doubly-robust | **`econml`** policy eval / custom DR (score in notation/dml.md §4) | needs logged `propensity` |
| `inference/anytime_valid.py` — confidence sequences | ⚠️ **build it** | no mature Python pkg; `confseq` (Howard, thin binding) / `expectation` exist but we implement + test vs ground truth — this is a crown-jewel deliverable |
| `inference/switchback.py` (Phase 3) | ⚠️ mostly custom | Python DiD/switchback frontier is thin |
| Power / MDE | **`statsmodels.stats.power`** | trivial since we control $N$ |
| Multiple testing / FDR | **`statsmodels.stats.multitest`** (`multipletests`, BH) | portfolio FDR |
| Bayesian decision (Ng–Imbens leg) | **`pymc`** / **`bambi`** + **`arviz`** | your toolbox |
| Metrics layer | **dbt** + **duckdb** (already chosen) | not pandas — see config `warehouse` |
| Regression tables / readouts | **`stargazer`** or **`pystout`** (ingests linearmodels) | publication-style outputs |
| Plots (if any in Python) | **`matplotlib`**/**`seaborn`**; **`plotnine`** for ggplot-style | dashboard charts are React/Recharts though |

## Phase-3 / vertical extras (when those legs come)
- **DiD** (staggered): **`pyfixest`** (TWFE, Sun–Abraham, did2s) and **`differences`** (Callaway–Sant'Anna). ⚠️ frontier sensitivity tools (HonestDiD, did_imputation) are **R-first** — port or call R.
- **RDD**: **`rdrobust`** (official CCT port). · **Synthetic control**: **`pysyncon`**, or **`causalpy`** (Bayesian).
- **Quasi-experiment toolkits**: **`causalpy`** (PyMC-Labs), **`dowhy`** (assumption-explicit refutation).

## Notable gaps where we build (⚠️ = the inference library *is* the deliverable)
1. **Anytime-valid / sequential testing** — no de-facto Python package; we implement confidence
   sequences (Howard / Waudby-Smith) and validate coverage against ground truth.
2. **Budget-split & marketplace-interference corrections** — design-specific; thin wrappers over `statsmodels`.
3. **Switchback** (Phase 3) — largely custom.

> When adding a dependency, note *why* in the commit/PR (per CLAUDE.md). Prefer one of the packages
> above before introducing a new one.
