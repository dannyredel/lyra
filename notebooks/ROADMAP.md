# Notebook roadmap — the Lyra curriculum

How we build the platform: **one raw notebook per coherent chunk**, built by hand from the libraries
(learn first), then **promoted** to `.py` behind the harness (LYRA §10, [[notebooks-first-promotion]]).
Each notebook advances one or more of the **four pillars** Daniel named:

> **DGP** (the world we author) · **Experiment** (how we randomize) · **Metric** (what we measure) ·
> **Method** (how we estimate). The **harness** (`sim → estimate → compare-to-truth → coverage/power`)
> certifies every method against a known truth — the spine all of it hangs off.

`_old/` holds the four previous notebooks (01 world · 02 money-shot · 03 estimators/trust ·
04 switchback · 05 spine) — recycle freely.

---

## The curriculum (build order)

| # | Notebook | Pillars it builds | Backed by (papers) | Promotes to `.py` | Recycle |
|---|---|---|---|---|---|
| **01** | **Spine — contracts, harness, DGP ladder, Core ATE** | DGP L0/L1 · Method (diff/OLS/**AIPW**) · the **harness** + **robustness grid** | Wager ch.1–3 · Imbens–Wooldridge · CCDDHNR (AIPW/DML) | `lyra/{protocols,dgp,estimators,harness}.py` | **`_old/05`** |
| **02** | **DGP zoo — realistic platform worlds** | **DGP** (the realism dial): outcome *types* (**binary clicks/conversions** · **count** sessions · **revenue** · **ratio** GMV/user · **churn/survival**) · a stylized **funnel** (impression→click→convert→revenue, Almedia-flavoured) · a **panel with staggered entry** (units join the treated group in different periods → peeking/DiD) | Wager ch.1 · Kohavi 2026 · (delta) Deng 2018 · (calibration) Almedia figures | `lyra/dgp/` (expand the ladder) | — |
| **03** | **Metrics — types drive variance** | **Metric** (mean · proportion-z · **ratio→delta** · count · quantile) · the spec (name/version/**type**/class) · **CUPED** pre-period · **A/A** as the metric-promotion gate | Deng–Knoblich–Lu 2018 (delta) · Deng 2013 (CUPED) · Kohavi 2026 | `lyra/metrics.py` | — |
| **04** | **Standard errors — robust · cluster-robust · bootstrap** | Method (**HC0–HC3** robust · **CRVE** cluster-robust · **CR2 / jackknife CV3** · **wild cluster bootstrap** · the **few-clusters** problem) — stress-tested on the clustered DGP (NB02) + the harness | **Cameron–Miller** (practitioner guide) · **MacKinnon–Nielsen–Webb 2023** (empirical practice) · **MacKinnon–Webb 2023** (wild bootstrap / jackknife / CV3) · **Hansen 2024/25** (jackknife SEs, clustered + DiD) · `sandwich-CL` vignette | `lyra/se.py` | — |
| **05** | **Designs & interference — the marketplace DGP** | DGP **L3** (agent marketplace) · Experiment (**A/B vs cluster vs two-sided/MRD**) · Method (cluster-robust [→NB04], **budget-split**) — the **money-shot** (naive biased → corrected recovers truth) | Johari 2021 · Holtz 2024 · Masoero 2025 · Hansen 2025 · LinkedIn budget-split | wrap `engine/` as a `DGP`; `lyra/estimators_cluster.py` | **`_old/01,02`** + `engine/` |
| **06** | **Temporal & variance reduction — switchback** | DGP **L2** (carryover/AR1) · Experiment (**switchback**) · Method (**CUPED/CUPAC/DML-DR**, power floor, Type-S) | Bojinov 2021 · Pankratev 2026 ×2 | `lyra/{dgp_temporal,estimators_vr}.py` | **`_old/04`** |
| **07** | **Sequential & diagnostics — peek safely** | Method (**confidence sequences / mSPRT / GST**) — on the **staggered-entry** panel from NB02 · diagnostics (**SRM · A/A · BH-FDR** · winner's-curse) | Howard 2022 · Johari 2017 · Spotify · Nordin–Schultzberg · Gelman–Carlin · Nie 2022 | `lyra/{sequential,diagnostics}.py` | **`_old/03`** + `inference/anytime_valid` |
| **08** | **Power & decisions** | Experiment (**sample-size / power-MDE calculator** — the **Confidence-SSC** 3-level formula: base → multiple-testing+guardrail corrections → allocation+CUPED+binary; the **DRAFT gate**; cross-checked vs the harness) · Method (**test-and-roll** profit-max sizing) · decision (multi-metric, the banner) | **Confidence SSC** (`papers/sample-size-calculation.md`) · Kohavi 2026 · Feit–Berman · Kawato · Ng–Imbens | `lyra/{power,decisions}.py` | experiment-design HTML lab |
| **09** | **CATE — who responds** | DGP (L1 + **CATE(X)** surface) · Method (**S/T/X/R/DR-learners · causal forests/GRF · DML-for-CATE**) | Künzel 2019 · Wager–Athey/GRF 2019 · Nie–Wager · Semenova–Cherno | `inference/hte.py` | — |
| **10** | **Uplift evaluation & policy** | Method (**Qini/AUUC/RATE/calibration** · **policy learning/trees** · **OPE: IPS/DR**) | GRF guide (RATE) · Dudík DR-policy · Schultzberg–Ottens · Zhang 2026 | `inference/{ope,policy}.py` | — |
| **11** | **Observational / day-job adjacency** | DGP (confounded, no randomization) · Method (**DML PLR/IRM · modern DiD · synthetic control/SDID · IV/LATE/CACE · sensitivity**) | CCDDHNR · Callaway–Sant'Anna · Sun–Abraham · Arkhangelsky · AIR 1996 · Bach 2025 | `lyra/observational.py` | — |
| **12** | **Incrementality & real-data validation** | Experiment (**ghost-ads / PSA holdout**) · Method (incrementality lift) · validation on **real** data (Criteo uplift) | Ghost Ads (Johnson–Lewis–Nubbemeyer) · Lewis–Rao · Criteo | `validation/criteo.py` | `inference/incrementality` |

> **NB 04 — cluster-robust / jackknife / bootstrap SE reading + libraries** (annotate now, build later).
> *Papers* (Daniel's Notion study set): **Cameron & Miller** — *A Practitioner's Guide to Cluster-Robust
> Inference*; **MacKinnon, Nielsen & Webb 2023** — *Cluster-Robust Inference: A Guide to Empirical
> Practice*; **MacKinnon & Webb 2023** — *Fast & Reliable Jackknife and Bootstrap Methods* (CV3 variance,
> jackknife estimators, new wild cluster bootstrap); **Hansen 2024** — *Jackknife SEs for Clustered
> Regression* (✅ in `pdfs/02-…/cluster-and-network/`); **Hansen 2025** — *Jackknife SEs for DiD*;
> sandwich **`sandwich-CL`** vignette (✅ `pdfs/02-…/cluster-and-network/`). *Libraries:* Python —
> **pyfixest** (`feols` + CRV + wild bootstrap), **wildboottest** (port of `fwildclusterboot`),
> `statsmodels` (`cov_type="cluster"`), `linearmodels`; R refs — **fixest** (`feols`,
> [SE guide](https://lrberge.github.io/fixest/articles/standard_errors.html)), **sandwich**, **estimatr**
> (`lm_robust`), **summclust**, **plm**, **fwildclusterboot** (<https://s3alfisc.github.io/fwildclusterboot/>).
> *Next step before building:* read `sandwich-CL` + Cameron–Miller to get CRVE/CR2/CV3 right.

> **On DGPs (Daniel's question — "more DGPs, here or another notebook?").** Both. The **shared, reusable**
> worlds (outcome types, the funnel, the staggered-entry panel) get their own **NB 02 — DGP zoo**, which
> grows into a `lyra/dgp/` package every later notebook draws from. But **specialised** DGPs stay with
> their topic: the carryover/AR1 temporal world lives in NB06 (switchback), the agent marketplace (L3)
> in NB05, network/cluster interference in NB05. The DGP zoo is the **realism dial**; topic notebooks add
> the one twist their method needs.
>
> **Ready-made panel/DiD DGP to reuse:** `paper-library/monte_carlo_did_cov.qmd` — Daniel's own
> Monte-Carlo following **Sant'Anna–Zhao (2020) DGP 1** (repeated cross-sections; `DRDID`/`did`/`fixest`).
> Port its data-generating recipe into **NB 02** (the staggered-entry panel world) and lean on it again
> in **NB 11** (modern DiD / DRDID) — it already encodes covariate-dependent propensity + outcome drift,
> exactly the DiD confounding structure.

**Frontier / later (one-offs, stay in `/research`):** long-term & surrogates (Lal–Imbens–Hull) ·
bandits + post-adaptive inference · survival / RMST (Sverdrup–Wager) · LLM-agent demand (Zhang 2026).

---

## How each notebook is structured (the template)

1. **The question** — what problem, why it bites (verbatim + the paper it comes from).
2. **Author the DGP** — by hand, so we *know* the truth (and can break assumptions).
3. **Build the method(s) raw** — numpy/statsmodels/sklearn directly; write the estimator's equation.
4. **Certify with the harness** — bias / coverage / power vs ground truth; the robustness view.
5. **The lesson** — what we learned; *then* the promotion note (what lifts into `.py`).

Model notebook: `_old/04_switchback_lab` (and `_old/05` for the spine).

---

## Recommended first build

**NB 01 — the spine.** It's the foundation every later notebook calls, and `_old/05` already built it
raw (DGP ladder L0/L1 · diff/OLS/AIPW · the harness · the OLS-biases/AIPW-survives grid). So NB 01 =
finalize that content as the canonical first notebook **and run the promotion for real** — lift the raw
functions into `lyra/{protocols,dgp,estimators,harness}.py` behind the small `Estimator`/`DGP` contract.
That makes NB 01 the worked example of the whole notebook→`.py` workflow, and unlocks the harness as a
reusable certifier for NBs 02–10.
