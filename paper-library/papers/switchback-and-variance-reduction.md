---
paper: switchback-experiments-and-variance-reduction (primer)
covers:
  - Bojinov, Simchi-Levi & Zhao 2021 — Design and Analysis of Switchback Experiments
  - Pankratev 2026 — Powerful Switchback Experiments – Or Not? (closed-form power)
  - Pankratev 2026 — Design-Aware Variance Reduction for Switchback Experiments (the VR poster)
  - Deng, Xu, Kohavi & Walker 2013 — CUPED · Poyarkov et al 2016 / Tang et al 2020 — CUPAC
  - Chernozhukov et al 2018 — DML / doubly-robust
feeds: notebooks/04_switchback_lab (the hands-on lab)
---

# Switchback experiments, CUPED & variance reduction — a primer

A pedagogic summary for the hands-on lab (`notebooks/04_switchback_lab`). **What** these methods are,
**why** we need them, and **what makes them hard** — grounded in the DoorDash switchback papers.

---

## 1. What is a switchback experiment, and why?

On a marketplace/platform the unit of business interest is a **cross-sectional entity** observed over
time — a delivery zone, a city, a network of users. A naive user-level A/B test there is **biased by
interference**: a pricing or dispatch change affects *shared* supply (couriers, inventory, attention),
so a treated user's outcome depends on how many *others* are treated — SUTVA fails (see
[[interference]]). Randomizing at the *market* level (one big cluster per arm) avoids that but gives
you a sample size of ~2.

A **switchback** sidesteps both: hold the market fixed and **randomize the treatment over time** —
turn it on and off in successive periods, so the *same* market acts as its own treatment and control.
The unit of randomization is a **cell = cluster × time period**; an individual observation lives inside
a cell. Because both arms are realized within the same market, network/equilibrium effects largely
cancel (Kohavi et al. 2020; used at DoorDash, Lyft, Uber, Airbnb).

> **The trade you make.** You buy immunity to *cross-sectional* interference at the cost of new
> *temporal* problems — carryover, autocorrelation — and a finite, lumpy set of cluster×time cells.
> Those costs are exactly what the rest of this primer is about.

---

## 2. The data-generating process (the lab's sim)

The DoorDash VR study models a cell's outcome as a sum of **multi-level shocks** plus treatment and
SUTVA violations (Pankratev 2026):

$$Y_{i,cl,t} \;=\; \underbrace{\mu + \alpha_{cl} + \gamma_t + \delta_{cl,t}}_{\text{untreated outcome}}
\;+\; \underbrace{\tau_{cl}\,T_{cl,t}}_{\text{treatment}}
\;+\; \underbrace{\text{carryover}_{cl,t} + \text{spillover}_{cl,t}}_{\text{SUTVA violations}}
\;+\; \varepsilon_{i,cl,t}.$$

- $\alpha_{cl}\sim\mathcal N(0,\sigma^2_{cl})$ — **cluster** (geozone) effect; $\gamma_t$ — **time** (diurnal) effect;
  $\delta_{cl,t}$ — **cluster×time interaction** (often AR(1) with lag-1 $\rho$); $\varepsilon$ — idiosyncratic **residual**.
- $T_{cl,t}\sim\text{Bern}(0.5)$ assigned per cell; $\tau_{cl}\sim\mathcal N(\tau,\cdot)$ a heterogeneous effect.
- **Carryover** $=\sum_k w_k\,\rho_{co}\,\tau_{cl}\,(T_{cl,t-k}-T_{cl,t})$ — treatment in past periods bleeds into now (temporal SUTVA).
- **Spillover** — cross-sectional leakage between clusters (spatial SUTVA).

Define total variance $\sigma^2_{total}=\sigma^2_{cl}+\sigma^2_{time}+\sigma^2_{int}+\sigma^2_{res}$ and **variance
shares** $S_k=\sigma^2_k/\sigma^2_{total}$. The **macro share** $S_{macro}=S_{cl}+S_{time}+S_{int}$ is the part of
the noise that lives *above* the individual — and it is the villain of the story. (DoorDash baseline:
geozone 5%, hour 3%, geozone×hour 2%, residual **90%**.)

---

## 3. Why it's hard — the challenges

### 3.1 Carryover (temporal SUTVA) — the core switchback hazard
A treatment can persist after it's switched off (a price change still affects the next hour's demand).
If carryover has **order $m$** (lasts $m$ periods), naive difference-in-means is biased. **Bojinov,
Simchi-Levi & Zhao (2021)** give the potential-outcomes framework and the **optimal switchback design**:
choose the randomization grid (period length, switch points) to minimize estimator variance subject to
the carryover order — discard the first $m$ post-switch periods (or model them) so you compare clean
periods. Longer periods ⇒ less carryover contamination but fewer independent cells ⇒ less power.

### 3.2 The structural power floor (Pankratev's formula)
There was **no closed-form power formula** for switchbacks until Pankratev (2026). Delta-linearizing the
individual-level OLS estimator gives the asymptotic variance:

$$\boxed{\;\operatorname{Var}(\hat\tau)\;\approx\;\frac{4\,\sigma^2_{total}}{J\,H}\left[\;\frac{S_{res}}{\bar n}
\;+\; S_{macro}\Big(\tfrac{1}{\bar n} + 1 + cv^2\Big)\right]\;}$$

with $J$ clusters, $H$ periods, $\bar n$ = mean cell size, $cv$ = coefficient of variation of cell sizes.
Read it carefully — it contains the whole moral:

- The **residual** share is divided by $\bar n$: pack more observations into a cell and idiosyncratic noise
  averages away, exactly as standard sampling theory predicts.
- The **macro** share is multiplied by $\big(\tfrac1{\bar n}+1+cv^2\big)$ — the $+1$ does **not** vanish with
  $\bar n$. **Macro shocks do not average away.** No matter how dense your data, variance hits a
  **structural floor** $\propto S_{macro}(1+cv^2)$. Adding observations within cells has rapidly
  diminishing returns; to get power you need more **cells** ($J\!\cdot\!H$) or a smaller $S_{macro}$.

### 3.3 Cluster-size imbalance — the $(1+cv^2)$ penalty
Real markets have wildly uneven cells (a few huge zones, many tiny ones). The $cv^2$ term is a modern
**Moulton factor** (Eldridge et al. 2006): macro variance is *amplified* by cluster-size imbalance,
because large, volatile cells dominate the estimator's denominator as treatment reshuffles. Switchbacks
are *uniquely* exposed to this vs stepped-wedge designs (the constant on/off flipping is what does it).
**Stratification/pairing** helps the cluster and time penalties but **leaves the interaction term
$S_{int}$ fully exposed** — a hard ceiling on design tricks.

### 3.4 Temporal autocorrelation & estimator choice
The cluster×time shocks are autocorrelated ($\rho$); more autocorrelation ⇒ each cluster carries *less*
independent information ⇒ less power. And you must choose the **aggregation level**: the *individual*-level
estimator weights cells by size (suffers $1+cv^2$); the *cell*-level estimator weights all cells equally
(escapes $cv^2$ but pays a low-density penalty $\mathbb E[1/n_{cl,t}]$ on volatile small cells). There is an
exact threshold $cv^\*$ where they tie.

---

## 4. CUPED and the variance-reduction family

**Power is bought by shrinking variance.** Covariate adjustment is the cheapest lever.

### 4.1 CUPED — Controlled-experiment Using Pre-Experiment Data (Deng et al. 2013)
Replace the outcome with a covariate-adjusted version using a **pre-treatment** covariate $X$ (e.g. the
cell's historical baseline):
$$\tilde Y = Y - \theta\,(X-\bar X),\qquad \theta=\frac{\operatorname{Cov}(Y,X)}{\operatorname{Var}(X)}.$$
Because $X$ is pre-treatment, $\mathbb E[\tilde Y]$ (hence the effect) is unchanged, but the variance drops by
$1-\rho^2$ with $\rho=\operatorname{Corr}(Y,X)$. Free power, never worse than raw. (It is the linear special
case of regression adjustment / DML — see [[dml]], [[power-mde]].)

### 4.2 CUPAC — Control Using Predictions As Covariates (Poyarkov 2016; Tang 2020, DoorDash)
Use a **machine-learning prediction** $\hat g(\text{features})$ of the outcome as the CUPED covariate
instead of a single historical mean. A flexible model captures more signal ⇒ higher $\rho$ ⇒ more VR.

### 4.3 DML-DR — doubly-robust / AIPW (Chernozhukov et al. 2018)
The AIPW score with a cross-fitted outcome model $\hat\mu_w$ and the (known, $=\tfrac12$) propensity:
$$\hat\tau_{DR}=\frac1n\sum_i\Big[\hat\mu_1(X_i)-\hat\mu_0(X_i)+\tfrac{T_i}{e}(Y_i-\hat\mu_1)-\tfrac{1-T_i}{1-e}(Y_i-\hat\mu_0)\Big].$$
Most aggressive variance reduction; Neyman-orthogonal so robust to a wrong outcome model.

### 4.4 The DoorDash result (the headline table)
Across 26 regimes / 52,000 Monte-Carlo runs (the poster), at the baseline ($n_{cl}=200$, $n_t=24$):

| estimator | SE ratio (↓) | VR % | power | FPR | MDE |
|---|---|---|---|---|---|
| **Raw** (diff-in-means) | 1.000 | 0 % | 0.33 | .048 | 38.6 |
| **CUPED** | 0.853 | 27 % | 0.45 | .042 | 33.0 |
| **CUPAC** | 0.513 | 74 % | 0.81 | .044 | 19.8 |
| **DML-DR** | 0.361 | 87 % | 0.97 | .044 | 13.9 |

### 4.5 Two non-obvious lessons (this is the payoff)
1. **Target macro shocks, not residual noise — the structural inversion.** In a *standard* A/B test,
   residual noise dominates, so ML predicting individual behavior wins. In a *switchback*, residual noise
   is already suppressed by $1/\bar n$ while macro shocks are amplified by $1+cv^2$. So even though the
   macro share may be *small* (20%) and the residual share *large* (80%), halving the macro share is
   **~16× more effective** than halving the residual share ($0.5\cdot0.20\cdot3.25=0.325$ vs
   $0.5\cdot0.80\cdot0.05=0.02$). **A CUPAC model for a switchback must predict spatial/temporal macro
   features, not individual residuals.**
2. **Efficiency vs robustness — the price of precision under interference.** VR estimators assume the
   covariate model is right. Under benign (attenuating) carryover they still detect a directionally
   correct effect. But under **sign-flip carryover** the aggressive estimators (DML-DR) produce far more
   **wrong-sign (Type-S) rejections** — confidently significant in the *wrong* direction. Carryover biases
   all methods *equally*; what VR changes is that it shrinks the CI around the *biased* point, so a biased
   estimate becomes a confident error (Hampel et al. 1986, robust statistics).

> **Goldilocks (the poster's recommendation):** **CUPAC** captures ~85% of DML-DR's efficiency gains
> with robust CI calibration and no propensity-overfitting in small experiments → the **default for
> switchbacks where SUTVA cannot be guaranteed.** Use DML-DR when SUTVA holds and $n_{cl}\ge50$; fall
> back to **Raw** under severe sign-flip interference; **CUPED** when there's no ML infrastructure.

---

## 5. How this maps to Vega

Vega's MVP is the rewarded-UA vertical (user-side simulated, reward/offer-side experimented), where the
canonical corrections are **budget-split** (budget cannibalization) and **cluster-robust** SEs. Switchback
is a **Phase-3 vertical** (Glovo-style delivery: shared courier supply → switchback + cluster). This
primer + lab build the muscle for that leg, and CUPED already lives in Vega's inference library
([[power-mde]], `inference/cuped.py`). Cross-links: [[interference]], [[dml]], [[anytime-valid]].

## References
Bojinov, Simchi-Levi & Zhao (2021) *Design and Analysis of Switchback Experiments*. ·
Pankratev (2026) *Powerful Switchback Experiments – Or Not?* (arXiv:2606.03012) and *Design-Aware
Variance Reduction for Switchback Experiments* (poster). · Deng, Xu, Kohavi & Walker (2013) *CUPED*
(WSDM). · Poyarkov et al. (2016) / Tang et al. (2020) *CUPAC* (DoorDash). · Chernozhukov et al. (2018)
*Double/Debiased ML*. · Eldridge et al. (2006); Moulton (1986) — cluster-size imbalance. · Kohavi,
Tang & Xu (2020). · Hampel et al. (1986) — robust statistics.
