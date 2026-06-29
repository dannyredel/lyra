---
sheet: balancing
covers: [Wager Causal Inference ch.7 (Balancing Estimators)]
feeds: [inference/cluster.py, inference/budget_split.py, inference/cuped.py (Riesz view)]
---

# Balancing estimators — equations (Wager ch.7)

Core idea: the propensity score's *real job* is to **balance covariates** between arms. So estimate weights
that directly target balance, rather than fitting a propensity model by MLE and hoping. (Optional chapter, but
the balance lens illuminates why cluster/budget-split designs work.)

## Balance is what IPW does
Oracle IPW achieves **population balance** for every basis function $\psi_j$:
$$E\Big[\tfrac{W_i\psi_j(X_i)}{e(X_i)}\Big]=E[\psi_j(X_i)]=E\Big[\tfrac{(1-W_i)\psi_j(X_i)}{1-e(X_i)}\Big].$$
Finite samples ⇒ aim for **sample balance** $\frac1n\sum_i\frac{W_i\psi_j(X_i)}{\hat e(X_i)}\approx\frac1n\sum_i\psi_j(X_i)$.

## Covariate-balancing propensity score (CBPS)
Instead of MLE, pick $\hat\theta$ to *enforce* sample balance (here linear $X$); equivalently minimize a convex loss:
$$\hat\theta_{(1)}=\arg\min_\theta\frac1n\sum_i\big(W_i e^{-X_i\theta}+(1-W_i)X_i\theta\big).$$
The resulting $\hat\tau_{CBPS}$ is $\sqrt n$-consistent, asymptotically normal, and **hits the AIPW efficiency
variance** $V^*$ (see [[ate-estimators]] §6) — unlike MLE-IPW. Stratification (ch.2) is CBPS for a saturated model.

## Approximate balancing weights (high-dim / non-parametric)
When exact balance is infeasible ($p\gg n$ or infinite sieve), solve for weights with bounded imbalance:
$$\hat\gamma^{(1)}=\arg\min_{\gamma_i\ge0}\ \tfrac1n\!\!\sum_{W_i=1}\!\!\gamma_i^2+\zeta n t^2\ \ \text{s.t.}\ \Big\|\tfrac1n\sum_i(\gamma_iW_i-1)X_i\Big\|_\infty\le t.$$
Then use an **augmented balancing** estimator (AIPW-shaped) so a decent regression mops up the residual imbalance:
$$\hat\tau_{AB}=\frac1n\sum_i\Big[X_i(\hat\beta_{(1)}-\hat\beta_{(0)})+W_i\hat\gamma_i^{(1)}(Y_i-X_i\hat\beta_{(1)})-(1-W_i)\hat\gamma_i^{(0)}(Y_i-X_i\hat\beta_{(0)})\Big].$$
$\sqrt n$-valid under sparsity $k\ll\sqrt n/\log p$ — same threshold as debiased-lasso inference.

## Riesz representer (the general view)
Any estimand linear in $P$ is $\theta=E[\gamma(X_i,W_i)Y_i]$ for a **Riesz representer** $\gamma$; for ATE,
$\gamma(x,w)=\frac w{e(x)}-\frac{1-w}{1-e(x)}$ (so IPW is Riesz weighting). Balancing weights = penalized empirical
Riesz representer (Hirshberg–Wager 2021); auto-DML estimates $\gamma$ directly (Chernozhukov–Newey–Singh 2022).

## Vega hooks
- **`inference/cluster.py` / `budget_split.py`:** both are *balance* devices (split the shared budget / aggregate to clusters so arms are comparable). CBPS/balancing is the principled weighting if we ever reweight rather than design-balance.
- **`inference/cuped.py`:** the Riesz/auto-DML view connects regression adjustment to the orthogonal-score machinery in [[dml]].
- Prefer libraries (`econml` has DRIV/Riesz-style; balancing weights are a thin convex solve) — STACK.md. Cross-link [[ate-estimators]].
