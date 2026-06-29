---
title: "HTE estimation: metalearners & causal forests (cluster note)"
covers:
  - "Athey, Tibshirani & Wager 2019 — Generalized Random Forests (Annals of Statistics)"
  - "Xu, Ignatiadis, Sverdrup, Fleming, Wager, Shah 2022 — Treatment Heterogeneity for Survival Outcomes (survlearners)"
  - "Sverdrup & Wager 2024 — Treatment heterogeneity with right-censored outcomes using grf"
pdfs: ../pdfs/11-hte-metalearners-forests/
refs:
  - "grf guide — https://grf-labs.github.io/grf/articles/grf_guide.html"
  - "CausalML — https://causalml.readthedocs.io"
tags: [causal-inference, HTE, CATE, machine-learning, random-forest, metalearners, off-policy-evaluation]
feeds: [inference/hte.py, inference/ope.py, Game B targeting/eval]
related: [[causal-forests]], [[metalearners]], [[hte]], [[dml]], [[policy-learning]]
status: processed   # via grf guide + Wager ch.4 + abstracts; full GRF proof not re-read (token budget)
read_on: 2026-06-02
equations: notation/causal-forests.md, notation/metalearners.md, notation/hte.md
---

# HTE: metalearners & causal forests

Daniel's point is right: the whole framework (Wager ch.4, the DML legs, Game B) **leans on CATE estimation**, so
the primary HTE methods belong in the library. This note covers the cluster; the math is in
[[causal-forests]] and [[metalearners]]. (Processed from the grf guide + Wager ch.4 + abstracts — the full
GRF *Annals* proof wasn't re-read, per the token-budget rule; refine the sheet if we need the asymptotics.)

## One-line claims
- **GRF (Athey–Tibshirani–Wager 2019):** a random forest is an *adaptive kernel*; reuse its neighborhoods to
  solve a **local moment equation** for the CATE — giving honest, asymptotically-normal $\hat\tau(x)$ with CIs.
- **Metalearners (Künzel/Nie-Wager/Kennedy):** recipes (S/T/X/R/DR) to turn *any* ML regressor into a CATE estimator.
- **Survival variants (Xu 2022, Sverdrup-Wager 2024):** the same S/T/X/R + `causal_survival_forest` for right-censored RMST.

## First-person takeaways
- **Causal forest = R-learner with forest weights.** It centers $Y,W$ on $\hat\ell,\hat e$ (orthogonalization) and
  solves a *local* Robinson regression weighted by leaf co-occurrence $\alpha_i(x)$. So it's not a separate
  paradigm from DML — it's the forest instantiation of the same orthogonal moment (ch.4). Good — one mental model.
- **The `grf` readout API is what I actually want**, not raw CATEs: `average_treatment_effect` (DR ATE+CI),
  `best_linear_projection` (which features drive heterogeneity), `rank_average_treatment_effect` (**RATE/AUTOC** — a
  *formal* heterogeneity test). This is exactly the Game-B question: does the ranker's predicted uplift rank units by realized effect?
- **Honesty + subsampling** is what buys valid inference (Wager-Athey 2018) — split-sample within each tree, OOB cross-fitting.
- **Metalearner choice is about data balance**, not taste: S (small/zero effect), T (balanced, data-rich), **X (unbalanced — early ramps!)**, R/DR (orthogonal default). The X-learner's relevance to Vega's low-treated-share ramp phase is notable.
- **Known propensity is our cheat code again:** `W.hat = 0.5` (or the engine's $e$) removes propensity-estimation error — same spirit as DR Cor 3.3.

## How we exploit it → modules
- `inference/hte.py`: expose S/T/X/R/DR (`econml`/`causalml`) **and** causal forest (`econml.CausalForestDML` / `grf`). Don't hand-roll.
- **Game B eval:** RATE/AUTOC as the heterogeneity/eval metric; calibrate the proxy quality-score against ground-truth $\tau$ (the eval-funnel point).
- `inference/ope.py` + policy: `get_scores` (DR scores) → `policytree`-style shallow policy ([[policy-learning]]).

## Metalearner primary sources
- ✅ **Künzel, Sekhon, Bickel & Yu 2019** — *Metalearners…* (PNAS): the S/T/X paper. **In `pdfs/11-…/`** (confirmed against [[metalearners]]).
- ⬜ **Nie & Wager 2021** — *Quasi-oracle estimation…* (R-learner).
- ⬜ **Kennedy 2023** — *Towards optimal doubly robust estimation…* (DR-learner).

## Cross-links
Equations: [[causal-forests]], [[metalearners]]; foundations: [[hte]] (Wager ch.4), [[dml]], [[ate-estimators]];
downstream: [[policy-learning]] (targeting), [[interference]] (spillover-aware CATE / Munro-Kuang-Wager).
