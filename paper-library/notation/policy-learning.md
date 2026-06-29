---
sheet: policy-learning
covers: [Wager Causal Inference ch.5 (Policy Learning)]
feeds: [inference/ope.py, inference/hte.py, Game B ranking ship decision, QINI/TOC uplift eval]
---

# Policy learning & off-policy evaluation — equations (Wager ch.5)

The bridge from "estimate $\tau(x)$" to "decide who to treat." The AIPW **policy value** is exactly the
doubly-robust **off-policy evaluation** estimator Vega's ranking leg needs.

## Estimands
Policy $\pi:\mathcal X\to\{0,1\}$; **value** $V(\pi)=E[Y_i(\pi(X_i))]$. Unrestricted optimum thresholds the CATE:
$\pi^*(x)=\mathbb 1\{\tau(x)>0\}$. Workflow: **learn** $\hat\pi$ → **evaluate** $V(\hat\pi)$ (test set) → **deploy**.

## Off-policy evaluation (OPE) → `inference/ope.py`
IPW value (known propensity): $\hat V_{IPW}(\pi)=\frac1n\sum_i\frac{\mathbb 1\{W_i=\pi(X_i)\}\,Y_i}{P(W_i=\pi(X_i)\mid X_i)}$, unbiased.
**AIPW / doubly-robust value** (efficient, $\sqrt n$-normal, cross-fit):
$$\hat V_{AIPW}(\pi)=\frac1n\sum_i\Big[\hat\mu_{\pi(X_i)}(X_i)+\frac{\mathbb 1\{W_i=\pi(X_i)\}}{P(W_i=\pi(X_i)\mid X_i)}\big(Y_i-\hat\mu_{\pi(X_i)}(X_i)\big)\Big].$$

## Policy comparison & benefit (ship decision)
$$\hat\Delta_{AIPW}(\pi_1,\pi_2)=\frac1n\sum_i(\pi_1(X_i)-\pi_2(X_i))\,\hat\Gamma_i,\qquad
\hat\Gamma_i=\hat\mu_{(1)}-\hat\mu_{(0)}+\tfrac{W_i(Y_i-\hat\mu_{(1)})}{\hat e}-\tfrac{(1-W_i)(Y_i-\hat\mu_{(0)})}{1-\hat e}$$
(the AIPW score). **Benefit** $\Delta(\pi)=\Delta(\pi,\mathbf 0)$; note $\Delta(\mathbf 1)=$ ATE. Precision improves
because only the region where $\pi_1,\pi_2$ disagree contributes — directly the "new ranker vs status quo" comparison.

## Prioritization curves (uplift evaluation)
Priority $S:\mathcal X\to\mathbb R$, treat top-$q$: $\pi_S^q=\mathbb 1\{S(X_i)\ge F_S^{-1}(1-q)\}$.
**QINI:** $\Delta(\pi_S^q)$ vs $q$ (cost-benefit of spending more). **TOC:** $q^{-1}\Delta(\pi_S^q)-\Delta(\mathbf 1)$ vs $q$
(do the top-$q$ benefit more than random?). AUC-TOC with $S=\hat\tau$ = a heterogeneity measure (Yadlowsky et al. 2025).

## Empirical-welfare maximization (EWM)
Learn over a restricted class $\Pi$: $\hat\pi=\arg\max_{\pi\in\Pi}\hat V(\pi)$. Regret $R(\hat\pi)=\sup_{\pi\in\Pi}V(\pi)-V(\hat\pi)$.
$$R(\hat\pi)\le 2\sup_{\pi\in\Pi}|\hat V(\pi)-V(\pi)|,\qquad \sqrt n\,E[R(\hat\pi_{AIPW})]\lesssim\sqrt{\mathrm{VC}(\Pi)\cdot V^*}.$$
**Policy learning = weighted classification:** $\hat\pi=\arg\max_\pi\frac1n\sum_i(2\pi(X_i)-1)\,\mathrm{sign}(\hat\Gamma_i)\,|\hat\Gamma_i|$
(label = sign of AIPW score, weight = $|\hat\Gamma_i|$). ⚠️ Don't swap in a logistic/hinge surrogate — guarantees break.

## Policy class $\Pi$ — why restrict
$X$ plays two roles: (1) needed for unconfoundedness (use rich $X$ for $\hat\mu,\hat e$); (2) the *decision* rule should
exclude gameable / protected / hard-to-measure features. So fit nuisances broadly, but constrain $\pi\in\Pi$.

## Vega hooks
- **`inference/ope.py`:** $\hat V_{AIPW}(\pi)$ **is** the DR off-policy value — evaluate a counterfactual ranking policy from logged data, validate vs the engine's ground-truth policy value.
- **Game B ship decision:** $\hat\Delta_{AIPW}(\hat\pi,\pi_0)$ = benefit of the new ranker over the baseline ranker → the decision banner.
- **`inference/hte.py` / eval funnel:** threshold $\mathbb 1\{\hat\tau(x)>C\}$ targeting; QINI/TOC as the uplift readout. Cross-link [[hte]], [[ate-estimators]], [[dml]].
