---
sheet: adaptive-experiments
covers: [Wager Causal Inference ch.6 (Adaptive Experiments)]
feeds: [inference/anytime_valid.py, ramp/allocation logic, Imbens 2026b Demonstration Experiments]
---

# Adaptive experiments / bandits — equations (Wager ch.6)

Relevance: Vega's ramp + any adaptive allocation must not break inference. Adaptive data is **non-IID**
(past outcomes drive future assignment), so naive estimators lose normality — exactly the peeking/longitudinal
caution in the anytime-valid layer.

## Setup
Stream $t=1..T$, arms $k=1..K$, $W_t\in\{1..K\}$ a function of the past, reward $Y_t=Y_t(W_t)$, $\mu_k=E[Y_t(k)]$.
**Regret** $R_T=\sum_{t=1}^T(\mu^*-\mu_{W_t})$, $\mu^*=\max_k\mu_k$. Goal: sub-linear regret (explore→exploit).

## UCB (optimism in the face of uncertainty)
$$W_t\in\arg\max_k \hat U_{k,t},\qquad \hat U_{k,t}=\hat\mu_{k,t-1}+2\sigma\sqrt{\tfrac{\log T}{n_{k,t-1}}}.$$
Regret bound (UCB1): $\ R_T\le 16\sigma^2\log T\sum_{k:\mu_k\neq\mu^*}\tfrac1{\mu^*-\mu_k}+(\mu^*-\mu_k)$ w.h.p.
⇒ $R_T=O(\log T)$. Worst case over weak gaps: $O(\sqrt{KT\log T})$.

## Thompson sampling (Bayesian; fewer knobs)
Sample $(\mu_1',..,\mu_K')\sim\Pi_{t-1}$, play $\arg\max_k\mu_k'$, update posterior. Effective assignment prob
$e_{k,t-1}=P_{\Pi_{t-1}}[\mu_k=\mu^*]$. With a flat prior + 1 draw/arm: tuning-free; empirically robust.

## Inference after adaptive collection (the trap)
Sample mean $\hat\mu_k^{AVG}$ is **biased downward** and non-Gaussian; IPW $\hat\mu_k^{IPW}=\frac1T\sum_t\frac{\mathbb 1\{W_t=k\}Y_t}{e_{t,k}}$ is unbiased but **heavy-tailed**. Fix: **adaptively-weighted (variance-stabilizing)** estimator with $1/\sqrt{e_{t,k}}$ weights:
$$\hat\mu_k^{AW}=\frac{\sum_t \mathbb 1\{W_t=k\}Y_t/\sqrt{e_{t,k}}}{\sum_t \mathbb 1\{W_t=k\}/\sqrt{e_{t,k}}}.$$
The $1/\sqrt e$ (not $1/e$) weighting makes the per-step conditional variance predictable ⇒ **martingale CLT** ⇒ valid normal CIs (Hadad et al. 2021).

## Trade-off (no free lunch)
Aggressively regret-optimal data collection ⇒ **fragile post-experiment inference** (Lindeberg condition fails as $e_{t,k}\to0$). If you also want to learn for future policy, taper sub-optimal arms *less* aggressively.

## Vega hooks
- **`inference/anytime_valid.py`:** same non-IID lesson; confidence sequences (Howard et al.) are the LIL-based alternative to variance-stabilizing weights. Pairs with Imbens 2026b *Demonstration Experiments*.
- **Ramp/allocation:** if allocation ever responds to interim results, use $\hat\mu^{AW}$-style weighting, not raw means. Cross-link [[interference]] (both break IID), [[ate-estimators]].
