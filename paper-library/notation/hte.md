---
sheet: hte
covers: [Wager Causal Inference ch.4 (Heterogeneous Treatment Effects)]
feeds: [inference/hte.py, inference/ope.py, Game B ranking/targeting]
---

# Heterogeneous treatment effects / CATE — equations (Wager ch.4)

⚠️ **Notation clash (logged in [NOTATION.md](NOTATION.md) crosswalk):** Wager writes $m(x)=E[Y\mid X=x]$
(the *marginal outcome*), whereas our canonical / DoubleML convention uses $m(X)=E[W\mid X]$ (propensity).
Below, $e(x)$ = propensity, and we write the marginal outcome as $\ell(x)=E[Y\mid X=x]$ in canonical form.

## Estimand — CATE
$$\tau(x)=E[Y_i(1)-Y_i(0)\mid X_i=x]=\mu_{(1)}(x)-\mu_{(0)}(x).$$
Point-identified under unconfoundedness (unlike the ITE $\Delta_i$). **Targeting (Prop 4.1):** with per-treat
cost $C$, the welfare-optimal rule is $\mathbb 1\{\tau(x)>C\}$ — a threshold on the CATE. (→ Game B targeting / policy.)

## 1. T-learner (baseline, biased) 
$$\hat\tau_T(x)=\hat\mu_{(1)}(x)-\hat\mu_{(0)}(x).$$
Consistent but suffers **regularization bias** and **regularization-induced confounding**: $\hat\mu_{(0)},\hat\mu_{(1)}$
are regularized differently (esp. when $e(x)$ varies / arms unbalanced), so their difference invents spurious heterogeneity.

## 2. Semiparametric / partially linear specification
$$\tau(x)=\psi(x)\cdot\beta,\quad \psi:\mathcal X\to\mathbb R^d;\qquad
Y_i(w)=\mu_{(0)}(X_i)+w\,\psi(X_i)\cdot\beta+\varepsilon_i(w).$$

**Robinson transform** (canonical $\ell(x)=E[Y\mid X=x]$, $e(x)$ propensity):
$$Y_i-\ell(X_i)=\big(W_i-e(X_i)\big)\,\psi(X_i)\cdot\beta+\varepsilon_i.$$

## 3. R-learner = residual-on-residual regression → `inference/hte.py`
Cross-fit nuisances, then OLS of residual outcome on residual (featurized) treatment:
$$\tilde Y_i=Y_i-\hat\ell^{(-k(i))}(X_i),\quad \tilde Z_i=\psi(X_i)\big(W_i-\hat e^{(-k(i))}(X_i)\big),\quad
\hat\beta=\big(\textstyle\sum_i\tilde Z_i^{\otimes2}\big)^{-1}\textstyle\sum_i\tilde Z_i\tilde Y_i.$$
Neyman-orthogonal ⇒ oracle-equivalent and $\sqrt n$-normal when $\alpha_m+\alpha_e\ge\tfrac12$, $\alpha_e\ge\tfrac14$:
$$\sqrt n(\hat\beta-\beta)\Rightarrow N(0,V_\beta),\quad
V_\beta=\mathrm{Var}[\tilde Z_i^*]^{-1}\,E[\varepsilon_i^2\,\tilde Z_i^{*\otimes2}]\,\mathrm{Var}[\tilde Z_i^*]^{-1}.$$

**R-loss** (the objective; pair with lasso/ridge + CV-tuned $\lambda$; forests ⇒ **causal forest**, Athey–Tibshirani–Wager):
$$\hat\beta=\arg\min_\beta\frac1n\sum_i\big(\,\underbrace{Y_i-\hat\ell^{(-k(i))}(X_i)}_{\tilde Y_i}-\big(W_i-\hat e^{(-k(i))}(X_i)\big)\psi(X_i)\cdot\beta\big)^2+\lambda\,\mathrm{pen}(\beta).$$

## 4. Constant-effect special case ($\psi(x)\equiv1$, Cor 4.3)
Residual-on-residual then estimates a scalar $\tau$ and, under homoskedastic constant effects, **beats AIPW**:
$$V_\tau=\frac{\sigma^2}{E[e(X)(1-e(X))]}\ \le\ \sigma^2\,E\!\left[\tfrac1{e(X)(1-e(X))}\right]=V_{AIPW}\quad(\text{Jensen}).$$
Lesson: efficiency is relative to the assumptions — extra structure (constant effect) buys precision over the generic bound.

## Vega hooks (use libraries — ../../STACK.md)
- `inference/hte.py`: R-learner / causal forest via **`econml`** (`CausalForestDML`, `NonParamDML`) or **`doubleml`**; don't hand-roll.
- Game B (ranking): CATE → who to target; threshold rule $\mathbb 1\{\hat\tau(x)>C\}$ feeds policy value / the eval-funnel proxy.
- `ope.py`: CATE + propensities are the substrate for DR policy value.
- **Deeper dives:** [metalearners.md](metalearners.md) (S/T/X/R/DR recipes) and [causal-forests.md](causal-forests.md) (GRF — the forest instantiation of the R-learner).
- Cross-link [dml.md](dml.md) (R-learner *is* the PLR with featurized treatment) and [ate-estimators.md](ate-estimators.md).
