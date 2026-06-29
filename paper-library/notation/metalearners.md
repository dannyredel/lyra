---
sheet: metalearners
covers: [Künzel et al 2019 (S/T/X), Nie & Wager 2021 (R), Kennedy 2023 (DR); Xu et al 2022 survlearners chapter]
feeds: [inference/hte.py, inference/ope.py, Game B targeting, eval funnel]
---

# Metalearners for CATE — equations

**Metalearner** = a recipe that re-purposes any predictive ML model (the *base learner*) to estimate the
CATE $\tau(x)=E[Y(1)-Y(0)\mid X=x]$. Notation: $\mu_{(w)}(x)=E[Y\mid X=x,W=w]$, propensity $e(x)=E[W\mid X=x]$,
marginal outcome $\ell(x)=E[Y\mid X=x]$. The framework leans on these because Vega's `hte.py` + Game-B targeting need a CATE.

## S-learner (Single model)
Fit one model on the pooled data **with $W$ as a feature**: $\hat\mu(x,w)$. Then
$$\hat\tau_S(x)=\hat\mu(x,1)-\hat\mu(x,0).$$
👍 simple, pools all data, shrinks toward $\tau=0$ (good when the effect is small/absent). 👎 regularization can
shrink $W$'s influence to ~0 → **bias toward "no effect"** when the signal is real.

## T-learner (Two models)
Fit each arm separately: $\hat\mu_{(0)},\hat\mu_{(1)}$; then $\hat\tau_T(x)=\hat\mu_{(1)}(x)-\hat\mu_{(0)}(x)$.
👍 no $W$-shrinkage. 👎 **regularization-induced confounding** when arms are unbalanced or have different
complexity — the two models are regularized differently and their difference invents heterogeneity (Wager ch.4).

## X-learner (Künzel et al 2019 — built for unbalanced arms)
1. Fit $\hat\mu_{(0)},\hat\mu_{(1)}$ (as in T).
2. Impute per-unit effects against the *other* arm's model:
$$\tilde D_i^{1}=Y_i-\hat\mu_{(0)}(X_i)\ (\text{treated}),\qquad \tilde D_i^{0}=\hat\mu_{(1)}(X_i)-Y_i\ (\text{controls}).$$
3. Regress: $\hat\tau_1(x)$ on $\tilde D^1$ over treated, $\hat\tau_0(x)$ on $\tilde D^0$ over controls.
4. Combine with a weight $g(x)\in[0,1]$ (commonly $g=\hat e$):
$$\hat\tau_X(x)=g(x)\,\hat\tau_0(x)+(1-g(x))\,\hat\tau_1(x).$$
👍 shines when one arm is much larger (put weight on the estimate from the data-rich side). Relevant to Vega ramps where treated share is small early.

## R-learner (Nie & Wager 2021 — Robinson residualization)
Cross-fit $\hat\ell,\hat e$, minimize the **R-loss** (Neyman-orthogonal):
$$\hat\tau=\arg\min_\tau\frac1n\sum_i\Big((Y_i-\hat\ell^{(-k)}(X_i))-(W_i-\hat e^{(-k)}(X_i))\,\tau(X_i)\Big)^2+\Lambda(\tau).$$
Same object as the PLR/residual-on-residual estimator — see [[hte]], [[dml]]. Orthogonal ⇒ robust to slow nuisances.

## DR-learner (Kennedy 2023 — regress the AIPW score)
Form the doubly-robust pseudo-outcome (the AIPW score $\hat\Gamma_i$ from [[ate-estimators]] §6), then regress it on $X$:
$$\hat\tau_{DR}(x)=\mathbb E[\hat\Gamma_i\mid X_i=x]\ \text{(any regression)},\quad
\hat\Gamma_i=\hat\mu_{(1)}-\hat\mu_{(0)}+\tfrac{W_i(Y_i-\hat\mu_{(1)})}{\hat e}-\tfrac{(1-W_i)(Y_i-\hat\mu_{(0)})}{1-\hat e}.$$
Doubly robust + orthogonal; a strong general-purpose default.

## Picking one (Xu et al 2022 guidance)
| Use | When |
|---|---|
| S | effect small/sparse or possibly zero; few units |
| T | effects large, arms balanced, plenty of data per arm |
| X | arms unbalanced / one much larger (early ramp) |
| R / DR | general default with ML nuisances; orthogonal, $\sqrt n$-valid |

## Software (use it — ../../STACK.md)
- **`econml`**: `SLearner, TLearner, XLearner, DomainAdaptationLearner, DRLearner, NonParamDML, CausalForestDML`.
- **`causalml`** (Uber): `BaseSRegressor/Classifier, BaseTRegressor, BaseXRegressor, BaseRRegressor, BaseDRRegressor`; uplift trees `UpliftTreeClassifier, UpliftRandomForestClassifier`; `CausalTreeRegressor`.
- R: `survlearners` (Xu et al), `grf`/`rlearner`.

## Vega hooks
- `inference/hte.py`: offer S/T/X/R/DR via `econml`; **don't hand-roll**. R/DR-learner are the principled defaults (orthogonal).
- Game B targeting / eval funnel: CATE → threshold rule $\mathbb 1\{\hat\tau(x)>C\}$ (see [[policy-learning]]); the proxy quality-score is calibrated against ground-truth $\tau$.
- **Sources:** ✅ Künzel et al 2019 (PNAS, S/T/X) — in `pdfs/11-…/`. ⬜ still want Nie & Wager 2021 (R-learner), Kennedy 2023 (DR-learner). Cross-link [[causal-forests]], [[hte]], [[dml]].
