---
sheet: causal-forests
covers: [Athey, Tibshirani & Wager 2019 (GRF), Wager & Athey 2018 (causal forests), grf guide, Sverdrup-Wager 2024, Xu et al 2022]
feeds: [inference/hte.py, inference/ope.py, Game B heterogeneity/eval (RATE/AUTOC)]
refs: ["grf guide: https://grf-labs.github.io/grf/articles/grf_guide.html", "https://causalml.readthedocs.io"]
---

# Causal forests / Generalized Random Forests (GRF) — equations

Built from the grf guide + Wager ch.4 + the GRF abstract; refine against `pdfs/11-…/ATHEY et al 2019.pdf` when needed.
**One idea:** a random forest is an *adaptive kernel*; GRF reuses its data-driven neighborhoods to solve a *local
moment equation* for whatever parameter you want — for us, the CATE.

## 1. Forest as adaptive weighting
A forest prediction is a weighted average of training outcomes:
$$\hat\mu(x)=\sum_i \alpha_i(x)\,Y_i,\qquad \alpha_i(x)=\frac1B\sum_{b}\frac{\mathbb 1\{X_i\in L_b(x)\}}{|L_b(x)|},$$
where $\alpha_i(x)$ = how often training point $i$ falls in the same leaf $L_b(x)$ as $x$ across $B$ trees (adaptive similarity).

## 2. Causal forest = forest-localized R-learner
- **Splitting** maximizes treatment-effect heterogeneity: a split into children $L,R$ scores $\propto n_L n_R(\hat\tau_L-\hat\tau_R)^2$.
- **Prediction** solves the centered (Robinson / R-learner) local moment with forest weights — centering $Y$ on $\hat\ell(x)$ and $W$ on $\hat e(x)$:
$$\hat\tau(x)=\frac{\sum_i\alpha_i(x)\,(W_i-\hat e(X_i))\,(Y_i-\hat\ell(X_i))}{\sum_i\alpha_i(x)\,(W_i-\hat e(X_i))^2}.$$
In `grf`: `Y.hat` $=\hat\ell$, `W.hat` $=\hat e$ (auto-fit forests, or **supply known values**). General GRF form: solve
$E[\psi_{\theta(x),\nu(x)}(O_i)\mid X=x]=0$ via the weights $\alpha_i(x)$.

## 3. Honesty + subsampling ⇒ valid inference
**Honesty:** within each tree, use one subsample to choose splits and a *disjoint* subsample to estimate leaf
effects (no double-dipping). With subsampling (not bootstrap), $\hat\tau(x)$ is **pointwise consistent & asymptotically
Gaussian** (Wager & Athey 2018), with a variance from the **infinitesimal jackknife** ⇒ pointwise CIs
$\hat\tau(x)\pm z_{1-\alpha/2}\hat\sigma(x)$. **Out-of-bag** predictions give cross-fitting for free on training data.

## 4. Doubly-robust readouts (the useful API)
| `grf` function | what it gives |
|---|---|
| `causal_forest(X,Y,W, Y.hat, W.hat, clusters)` | CATE $\hat\tau(x)$ via §2 |
| `average_treatment_effect()` | **DR/AIPW ATE** + CI (averages scores $\hat\Gamma_i$) |
| `best_linear_projection(cf, A)` | regress $\hat\tau$ on covariates $A$ → which features drive heterogeneity (+ robust/clustered SEs) |
| `rank_average_treatment_effect()` | **RATE / TOC curve + AUTOC** — formal heterogeneity test |
| `variable_importance()`, `test_calibration()` | drivers; calibration check |
| `get_scores()` → `policytree::policy_tree(X,Γ,depth)` | DR scores → shallow policy (ch.5) |

DR score: $\hat\Gamma_i=\hat\tau(X_i)+\dfrac{W_i-\hat e(X_i)}{\hat e(X_i)(1-\hat e(X_i))}\big(Y_i-\hat\mu(X_i,W_i)\big)$.

## 5. Practical guidance (grf guide)
- **RCT / known propensity:** pass `W.hat = 0.5` (or the known $e$) — skips propensity estimation error. **Vega's case** (engine sets $e$).
- **Many covariates / moderate $n$:** pre-screen with a regression forest's `variable_importance`, keep top ~10 for the causal forest.
- **Assess heterogeneity rigorously:** don't eyeball the CATE histogram — use **RATE/AUTOC** with a t-test on $\text{AUTOC}\neq0$.
- GRF also does quantile regression, conditional average partial effects, and **HTE-via-IV** (instrumental forest).
- Extensions: `causal_survival_forest` (Sverdrup–Wager 2024) for right-censored RMST outcomes.

## Vega hooks
- `inference/hte.py`: causal forest via **`econml` `CausalForestDML`** (Python) or `grf` (R); RATE/AUTOC = the heterogeneity/eval metric for **Game B** (does the ranker's predicted uplift actually rank units by realized effect?).
- `best_linear_projection` → which offer/user features drive the ranking effect; `get_scores` → policy learning ([[policy-learning]]).
- Known $e(x)$ (`W.hat=0.5`) makes recovery tests clean — same point as DR ch.3 Cor 3.3 ([[ate-estimators]]).
- Cross-link [[metalearners]] (causal forest = R-learner with forests), [[hte]], [[dml]].
