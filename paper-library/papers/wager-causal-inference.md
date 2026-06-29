---
title: "Causal Inference (book draft)"
authors: "Stefan Wager"
year: 2025
venue: "Book draft, Nov 2025 (Stanford GSB)"
pdf: ../pdfs/00-foundational/Causal Inference - Stefan Wager (Nov 2025).pdf
md: ../md/causal-inference-stefan-wager-nov-2025/
tags: [causal-inference, double-ML, potential-outcomes, propensity-score, doubly-robust, HTE, variance-reduction, interference, instrumental-variables, adaptive-experiments, balancing]
feeds: [inference/naive.py, inference/cuped.py, inference/cluster.py, inference/incrementality.py, inference/ope.py, inference/hte.py, inference/switchback.py, inference/anytime_valid.py]
related: [[dml]], [[ate-estimators]], [[hte]], [[interference]], [[iv-late]], [[adaptive-experiments]], [[balancing]], [[policy-learning]], [[event-study-did]]
status: processing   # ch.1–7, 10–13 done; ch.8, 9, 14–16 pending
read_on: 2026-06-02
equations: notation/{ate-estimators, hte, dml, interference, iv-late, adaptive-experiments, balancing, policy-learning, event-study-did}.md
---

# Wager — *Causal Inference* (ch.1–7, 10–13)

**The foundational text + preferred notation for Vega.** Equations live in the `notation/` sheets;
this note is the *prose takeaways + Vega hooks*. Done: ch.1–4 (ATE/DR/HTE), 5 (policy/OPE), 6 (adaptive),
7 (balancing), 10 (LATE/IV), **11–12 (interference — the thesis)**, 13 (event-study/DiD).
Pending: ch.8 (RDD), 9 (SEM), 14 (dynamic policies), 15 (MDPs), 16 (exercises).

## One-line claim
> Causal estimation under unconfoundedness is a semiparametric problem whose efficient solution is
> AIPW/DML with cross-fitting — and (almost) everything else (DM, regression adjustment, IPW,
> stratification, R-learner) is a special case or stepping stone to it.

## Chapter-by-chapter takeaways

**Ch.1 — RCTs.** Potential outcomes + SUTVA; the fundamental problem (only one $Y_i(w)$ observed).
Difference-in-means is unbiased *essentially without assumptions*. The non-obvious gem: the
**interacted regression adjustment** (full $W\times X$ interactions) is **never worse** than DM
asymptotically — *even when the linear model is misspecified* — and usually strictly better. This is
exactly the CUPED logic, and it's a free lunch. Neyman (finite-pop) vs superpopulation models matter
for interference (ch.11–12) and connect to Vega's "we author the DGP" stance.

**Ch.2 — Unconfoundedness & propensity.** Relax randomization → assume $\{Y(0),Y(1)\}\perp W\mid X$.
The propensity $e(x)$ is a **balancing score** (conditioning on $e(X)$ suffices). Stratification works
for discrete $X$ and its variance *doesn't grow with #strata*. IPW is the simple continuous-$X$ move
but is **inefficient** (oracle IPW has strictly larger variance than stratification). **Overlap** is the
load-bearing assumption — and Vega *sets* $e(x)$, so overlap holds by construction (huge for recovery tests).
Naive "control for $X$ by adding it to a regression" is **not** valid under unconfoundedness — must adjust non-parametrically.

**Ch.3 — Doubly robust (the crown chapter for us).** AIPW = regression first, then IPW on the
residuals. **Weak DR:** consistent if *either* $\hat\mu$ or $\hat e$ is right. **Strong DR / DML:** with
cross-fitting and nuisance rates $\alpha_\mu+\alpha_e\ge\tfrac12$ (e.g. both $n^{-1/4}$), AIPW is
$\sqrt n$-normal at the **semiparametric efficiency bound** $V^*$. **Cross-fitting** = honest
out-of-fold residuals → lets us bolt *any* ML nuisance estimator on without bias. **Cor 3.3 (Vega's
case):** with *known* $e(x)$, AIPW hits $V^*$ using *any* consistent $\hat\mu$ — **no rate condition**.
Closed-form variance + Gaussian CI. This chapter *is* `inference/`'s backbone.

**Ch.4 — HTE / CATE.** Target the CATE $\tau(x)$ (point-identified), not the ITE (not). **T-learner**
($\hat\mu_1-\hat\mu_0$) suffers **regularization-induced confounding** — invents heterogeneity when arms
are regularized differently / $e(x)$ varies. The fix: **R-learner** = residual-on-residual regression
(Robinson transform), Neyman-orthogonal, oracle-equivalent under the same rate conditions; **causal
forest** = R-learner with forests. Targeting rule is a **threshold on the CATE** $\mathbb 1\{\tau(x)>C\}$
(Prop 4.1) — directly the Game-B targeting/policy object.

## How we exploit it (concrete → modules)
- `inference/naive.py` ← DM (ch.1); the biased-under-interference baseline.
- `inference/cuped.py` ← interacted regression adjustment (ch.1) — variance reduction, never worse.
- `inference/cluster.py` ← stratification + its variance form (ch.2); aggregate-to-unit.
- `inference/incrementality.py` & `inference/ope.py` ← the AIPW/DR score (ch.3) — treatment-vs-holdout and DR policy value.
- `inference/hte.py` ← R-learner / causal forest (ch.4) via `econml`/`doubleml` (don't hand-roll — STACK.md).
- **Recovery-test leverage:** because Vega knows $e(x)$, Cor 3.3 says AIPW is efficient with weak nuisance
  assumptions — our recovery tests can assert efficient coverage cleanly.

## Numbers / facts worth stealing
- Nuisance rate budget $\alpha_\mu+\alpha_e\ge 1/2$ (both $n^{-1/4}$ suffices) — the practical DML threshold.
- Efficiency bound $V^*=\mathrm{Var}[\tau(X)]+E[\sigma^2_{(1)}/e]+E[\sigma^2_{(0)}/(1-e)]$ — the target variance to benchmark estimators against.
- Regression adjustment variance gain $\lVert\beta_{(0)}^*+\beta_{(1)}^*\rVert_A^2$ — how much CUPED-style adjustment buys.

## Chapter-by-chapter takeaways (continued)

**Ch.6 — Adaptive experiments.** UCB & Thompson sampling get $O(\log T)$ regret, but **adaptive data is
non-IID** → sample means are biased-down, IPW is heavy-tailed; valid CIs need **variance-stabilizing
$1/\sqrt e$ weights** (martingale CLT). And there's a hard trade-off: regret-optimal collection ⇒ fragile
inference. Maps to Vega's ramp/anytime-valid: if allocation ever reacts to interim data, don't use raw means.
Equations → [[adaptive-experiments]].

**Ch.7 — Balancing estimators.** The propensity's *real job is covariate balance*. **CBPS** learns weights by
minimizing a balancing loss (not MLE) and hits the AIPW efficiency variance; **approximate balancing weights**
+ augmentation extend this to high-dim. The **Riesz-representer** view ($\gamma=\frac w{e}-\frac{1-w}{1-e}$ for ATE)
unifies it with auto-DML. Lens for *why* cluster/budget-split designs work (they balance arms). → [[balancing]].

**Ch.10 — LATE / IV.** Wald $\hat\tau_{IV}=\widehat{\mathrm{Cov}}[Y,Z]/\widehat{\mathrm{Cov}}[W,Z]$; under
exclusion/exogeneity/relevance/monotonicity it's the **compliers' ATE**. **Ghost-ads incrementality is an
encouragement (IV) design** — the reward nudges engagement; lift among responders is a LATE. Supply–demand IV is
the price-elasticity story; MTE generalizes. → [[iv-late]], feeds `inference/incrementality.py`.

**Ch.11 — Spillovers & interference (THESIS).** SUTVA fails → $2^n$ potential outcomes, tamed by **exposure
mappings**. **Cluster-interference ⇒ SUTVA at cluster level ⇒ cluster-randomize** (the justification for
`cluster.py`). Nested null hierarchy $H_0\subset\!H_1(\text{SUTVA})\subset\!\dots\subset\!H_4$ tested by
permutation (closed testing, no multiplicity). The **ride-sharing market-re-equilibration** example is Vega's archetype.

**Ch.12 — Estimating under interference (THESIS).** HT/IPW over exposure propensities $e_i(h)$ is unbiased for
free. **Finite-population (Neyman) inference:** true variance unidentified, but the IID variance estimate is a
*conservative* bound. The **dependency-graph HAC variance**; crucially **block/cluster $G$ ⇒ exactly the
cluster-robust estimator** — so cluster-robust SEs are finite-population-correct, not an IID hack. **ADE/AIE** +
**Munro–Kuang–Wager 2025** (marketplace equilibrium interference, spillover-aware targeting) ≈ the Vega setting. → [[interference]].

**Ch.5 — Policy learning (OPE backbone).** From estimating $\tau(x)$ to deciding. The **AIPW policy value**
$\hat V_{AIPW}(\pi)$ *is* doubly-robust **off-policy evaluation** — score a counterfactual ranking policy from logs.
Policy comparison $\hat\Delta(\hat\pi,\pi_0)$ = benefit over status quo (the ship-decision number); **QINI/TOC**
curves = uplift readout. EWM = weighted classification on AIPW scores; regret $\sim\!\sqrt{\mathrm{VC}(\Pi)/n}$.
Restrict the deploy class $\Pi$ (gameable/protected features stay in $\hat\mu,\hat e$ but out of $\pi$). → [[policy-learning]], feeds `ope.py`.

**Ch.13 — Event-study / DiD.** Panel, off→on adoption; **parallel trends** + non-anticipation ⇒ DiD unbiased for
$\bar\tau_{ATT}$ (and DiD is "doubly robust": valid under randomization *or* parallel trends). **TWFE is biased
under staggered adoption** (negative weights / forbidden comparisons) — use **averaged-saturated-regression /
imputation** (Borusyak–Jaravel–Spiess, Wooldridge) or cohort-wise (Callaway–Sant'Anna, Sun–Abraham); **SDID**
when parallel trends fails. Inference: **cluster by unit**. → [[event-study-did]], feeds Phase-3 DiD + panel-readout caution.

## Open questions / for later chapters
- Notation: Wager's $m(x)=E[Y\mid X]$ clashes with DoubleML's $m=$ propensity (logged in NOTATION crosswalk).
- HOIF / minimal-rate efficiency (Robins et al. 2017) — beyond MVP, noted.
- **Acquire (ch.11–12 cites):** Munro–Kuang–Wager 2025 (marketplace equilibrium — high priority), Aronow–Samii
  2017, Leung 2022, Hu–Li–Wager 2022, Athey–Eckles–Imbens 2018. Added to INDEX §02 acquisition.
- **Acquire (ch.13 DiD cites):** Callaway–Sant'Anna 2021, Sun–Abraham 2021, Borusyak–Jaravel–Spiess 2024,
  de Chaisemartin–d'Haultfœuille 2020, Arkhangelsky et al. 2021 (SDID) — map to `pyfixest`/`differences` in STACK.
- Still to process: ch.8 (RDD), 9 (SEM), 14 (dynamic policies), 15 (MDPs).

## Cross-links
- Equations: [[ate-estimators]], [[hte]], [[dml]], [[interference]], [[iv-late]], [[adaptive-experiments]], [[balancing]].
- Library/INDEX foundational set; pairs with the Belloni–Chernozhukov DML classics in `01-causal-ml-dml/`.
