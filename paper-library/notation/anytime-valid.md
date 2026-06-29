---
sheet: anytime-valid
covers: [Johari et al 2017 (Peeking at A/B Tests), Howard et al 2022 (confidence sequences — to deepen)]
feeds: [inference/anytime_valid.py, the live dashboard CS band, peeking-safe ramp]
---

# Anytime-valid inference (peeking, always-valid p-values, CS) — equations

## Assumptions / setting
Stream of observations; the experimenter may **stop at a data-dependent time $T$** (continuous monitoring). Goal:
control Type-I error / coverage *simultaneously over all $n$*, not at one pre-fixed sample size.

## 1. The peeking problem (why fixed-horizon breaks)
A **fixed-horizon** p-value $p_n$ is valid only at a pre-committed $n$: under $H_0$, $P_{\theta_0}(p_n\le s)\le s$
(superuniform). But if you **reject the first time $p_n\le\alpha$**, the realized Type-I error inflates — and is
*guaranteed* to hit any fixed $\alpha$ if you wait long enough (law of the iterated logarithm): error $\to 100\%$.
Even "peek then check post-hoc power" doesn't fix it (Johari 2017). 5–10× inflation is common at $n=10^4$.

## 2. Always-valid p-values (Johari et al 2017)
A sequence $(p_n)$ is an **always-valid p-value process** if for *any* (possibly infinite) stopping time $T$:
$$\forall s\in[0,1]:\quad P_{\theta_0}(p_T\le s)\le s.$$
**Duality with sequential tests (Thm 3.2).** A sequential test $(T(\alpha),\delta(\alpha))$ (nested decision rules,
each controlling Type-I at $\alpha$) ↔ an always-valid p-value:
$$p_n=\inf\{\alpha: T(\alpha)\le n,\ \delta(\alpha)=1\},\qquad \text{and "reject when } p_n\le\alpha\text{" implements the test.}$$
So you can monitor continuously, stop whenever, and report $p_T$ — Type-I stays $\le\alpha$.

## 3. mSPRT — the construction Optimizely uses
Mixture Sequential Probability Ratio Test. For a one-parameter exponential family with effect $\theta$, mix the SPRT
likelihood ratio over a prior (mixing distribution) $\pi$ on the alternative:
$$\Lambda_n^{\pi}=\int \frac{f_{\theta}(x_{1:n})}{f_{\theta_0}(x_{1:n})}\,d\pi(\theta),\qquad
p_n=\Big(\max\{1,\ \textstyle\sup_{m\le n}\Lambda_m^{\pi}\}\Big)^{-1}.$$
$\Lambda_n^\pi$ is a non-negative martingale under $H_0$ ⇒ by Ville's inequality $P(\sup_n\Lambda_n\ge 1/\alpha)\le\alpha$,
giving the always-valid guarantee. The running-max makes $p_n$ monotone non-increasing (interpretable).

## 4. Confidence sequences (Howard et al 2022) — the modern, rigorous form
A **confidence sequence (CS)** is a sequence of intervals $(CI_t)$ with **time-uniform** coverage:
$$P\big(\forall t\ge 1:\ \theta\in CI_t\big)\ge 1-\alpha.$$
Time-uniform (not pointwise) ⇒ safe to peek/stop **anytime**, under **any** stopping rule. Concrete sub-Gaussian CS for the mean (Howard et al 2022, eq. 2):
$$\bar X_t\ \pm\ 1.7\sqrt{\frac{\log\log(2t)+0.72\,\log(10.4/\alpha)}{t}}.$$
Width is $O\!\big(\sqrt{t^{-1}\log\log t}\big)$ — the **LIL rate**; the extra $\log\log t$ vs a fixed-$n$ CI's $\sqrt{1/t}$
is the unavoidable **price of peeking**. Properties (P1–P4): nonasymptotic & nonparametric · unbounded sample size ·
arbitrary stopping · width $\to 0$ at $\sim 1/\sqrt t$.
**Construction:** uniform exponential concentration (Cramér–Chernoff + LIL + SPRT) via a **non-negative
supermartingale** $M_t$ + **Ville's inequality** $P(\exists t: M_t\ge 1/\alpha)\le\alpha$. **Boundary shape** matters:
a *linear* boundary is valid but doesn't shrink to 0; a *curved* boundary (normal-mixture / stitched) shrinks to 0.
**Asymptotic CS** (Waudby-Smith et al.) is the practical drop-in — roughly a $\log\log t$ widening of the usual CLT CI; likely Vega's default.

## 5. Frameworks in practice — mSPRT vs CS vs GST (Spotify cluster)
*(The Spotify blog PDFs are image-based exports — not text-extractable; this synthesizes the methods above + the
series, fetched live 2026-06-02 — the PDF exports were image-only. Ankargren, Frånberg & Schultzberg.)*
| Framework | Anytime-valid? | Needs a horizon? | Looks | Note |
|---|---|---|---|---|
| **mSPRT / AVI** (Johari 2017; Lindon–Malek–Zhang 2022) | yes (any $T$) | no | continuous | mixture over an effect prior; bounded FPR regardless of tuning; best for **streaming** |
| **Confidence sequences** (Howard 2022) | yes (any $T$) | no | continuous | nonparametric, LIL rate; wider (the peeking tax) |
| **Group-sequential tests (GST)** (Lan–DeMets 1983; Jennison–Turnbull) | within a pre-planned design | **yes** | discrete | **alpha-spending**; **highest power** when max-$N$ is estimable; for **batch** data; infeasible past ~few-hundred looks |
| **Bonferroni** | yes | yes (pre-set #looks) | discrete | conservative, but *surprisingly competitive* at **≤14** looks |

**Spotify's verdict (Choosing-a-Framework):** **GST when the sample size is estimable** (batch, most power); **AVI/mSPRT
when $N$ is unknown / data streams** (you "only pay for the peeking you make"). Spotify's Confidence platform leans GST.

**Longitudinal-data — "Peeking 2.0" (within-unit peeking).** The new hazard: peeking at a unit *before all its
measurements are in*. With **repeated measures per user**, the within-unit covariance is unmodeled → inflated FPR, and the
*estimand itself shifts* between looks (open-ended metrics re-aggregate). **Fix (Part 2):** a longitudinal regression
$y_{it}=\beta_0+\delta\,d_{it}+\varepsilon_{it}$ estimated by **GLS** (or cluster-robust OLS/WLS), then a GST exploiting
the **independent-increments** property of the estimator across looks (reduces $L$-dim integrals to univariate
recursions). Sufficient stats for the $K\times K$ covariance grow as $K(K+1)/2$. **Directly relevant to Vega** —
agents emit many events over the horizon, so reading the event log sequentially *is* within-unit peeking. (Also: design-based CS, Netflix arXiv:2210.08639.)

**Fixed-power designs — "It's not IF you peek, it's WHAT you peek at" (Nordin–Schultzberg 2024).** Key insight:
*not all stopping rules are equally harmful* — **peeking at the variance function** (to estimate the required $N$) barely
hurts inference, whereas peeking at **significance / p-values** badly does. So: start with no fixed $N$, estimate the
required $N$ from accruing data, stop when current $N$ exceeds it, and **analyze with ordinary non-sequential methods —
no correction** (estimator stays consistent, CI keeps coverage). Bonus: sequential tests that *stop on significance*
yield **biased, over-estimated** effects (winner's curse — ties to [[power-mde]] Type-M).

## Vega hooks
- `inference/anytime_valid.py`: default **asymptotic CS** (config `anytime_valid.method: asymptotic_cs`, `rho2`),
  optional **mSPRT**. The dashboard's **confidence-sequence band** narrows over the *replayed* simulated clock —
  the whole sequential story is intact under replay (it lives in time/data, not transport; PROPOSAL §9).
- `tests/`: assert always-valid coverage under continuous "peeking" on the simulated stream (A/A must not flag even when peeked).
- Cross-link [[power-mde]] (fixed-power vs sequential), [[adaptive-experiments]] (LIL / variance-stabilizing weights), [[platform-experimentation]].
