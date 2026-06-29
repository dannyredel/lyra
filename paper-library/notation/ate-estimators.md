---
sheet: ate-estimators
covers: [Wager Causal Inference ch.1–3 (RCTs, Unconfoundedness/Propensity, Doubly Robust), Imbens & Wooldridge 2009]
feeds: [inference/naive.py, inference/cuped.py, inference/cluster.py, inference/incrementality.py, inference/ope.py]
---

# ATE estimation under unconfoundedness — equations (Wager ch.1–3)

Local notation (book's, mapped to canonical in [NOTATION.md](NOTATION.md)): treatment $W\in\{0,1\}$;
propensity $e(x)=P(W=1\mid X=x)$ **(= canonical $m(X)$)**; response surfaces
$\mu_{(w)}(x)=E[Y\mid X=x,W=w]$ **(= canonical $g(w,X)$)**; $\sigma^2_{(w)}(x)=\mathrm{Var}[Y(w)\mid X=x]$.
The cross-fitting / orthogonal-score machinery is shared with [dml.md](dml.md).

## Assumptions (the standard trio — state them up front)
1. **SUTVA** — $Y_i=Y_i(W_i)$ (no interference; single version of treatment).
2. **Unconfoundedness** (selection on observables; Rosenbaum–Rubin 1983) — $W_i\perp\!\!\!\perp\{Y_i(0),Y_i(1)\}\mid X_i$.
3. **Overlap / positivity** — $\eta\le e(x)\le 1-\eta$ (strong) or $E[1/(e(X)(1-e(X)))]<\infty$ (weak).

In an RCT, (2) holds *by design* with $e(x)=\pi$ known. "Controlling for $X$" by regression adds **two more** — §3.1.

## Estimand
$$\tau = E[Y_i(1)-Y_i(0)], \qquad \tau(x)=E[Y_i(1)-Y_i(0)\mid X_i=x].$$
SUTVA $Y_i=Y_i(W_i)$; the fundamental problem: $\Delta_i=Y_i(1)-Y_i(0)$ is never observed.

## 1. Difference-in-means (RCT baseline) → `inference/naive.py`
$$\hat\tau_{DM}=\frac1{n_1}\sum_{W_i=1}Y_i-\frac1{n_0}\sum_{W_i=0}Y_i,\qquad
\sqrt n(\hat\tau_{DM}-\tau)\Rightarrow N(0,V_{DM}),\ \ V_{DM}=\frac{\mathrm{Var}[Y(1)]}{\pi}+\frac{\mathrm{Var}[Y(0)]}{1-\pi}.$$
Unbiased under randomization essentially without assumptions. CI: $\hat\tau_{DM}\pm\Phi^{-1}(1-\alpha/2)\sqrt{\hat V_{DM}/n}$.

## 2. Interacted regression adjustment → `inference/cuped.py`
Fit $Y_i\sim\alpha+W_i\tau+X_i\beta+W_iX_i\gamma$ (equiv. separate per-arm regressions); report
$\hat\tau_{IREG}=\hat\tau+\bar X\hat\gamma$. **Never worse than DM, even if the linear model is misspecified:**
$$V_{IREG}=V_{DM}-\lVert\beta_{(0)}^{*}+\beta_{(1)}^{*}\rVert_A^2\ \le\ V_{DM}.$$
This is the CUPED principle (regression-adjust on pre-treatment $X$ to cut variance, no bias).

## 3. Unconfoundedness, propensity, overlap
$$\{Y(0),Y(1)\}\perp\!\!\!\perp W\mid X\quad(\text{unconf.}),\qquad
\{Y(0),Y(1)\}\perp\!\!\!\perp W\mid e(X)\ \ (\text{balancing score}).$$
Overlap: strong $\eta\le e(x)\le 1-\eta$; weak $E[1/(e(X)(1-e(X)))]<\infty$. In Vega we *set* $e(x)$, so
overlap holds by construction — good for recovery tests.

## 3.1 Regression with rich controls — and the linearity tax (Imbens–Wooldridge 2009)
"Controlling for $X$" via $Y_i=\alpha+\tau W_i+\beta'X_i+\varepsilon_i$ is **not justified by unconfoundedness alone**
(Wager ch.2 fn.15). It silently adds: **(i) constant treatment effects** $\tau=Y_i(1)-Y_i(0)$, and **(ii) linearity**
$\mu_{(0)}(x)=\alpha+\beta'x$. Given both, unconfoundedness $\Leftrightarrow \varepsilon_i\perp\!\!\!\perp W_i\mid X_i$ and OLS $\hat\tau$ is the ATE.

The non-parametric **regression / imputation estimator** (I&W eq.11) needs neither assumption:
$$\hat\tau_{reg}=\frac1N\sum_i\big(\hat\mu_{(1)}(X_i)-\hat\mu_{(0)}(X_i)\big)\ \xrightarrow{\text{linear arms}}\ \hat\alpha_1-\hat\alpha_0,$$
the coefficient on $W_i$ in the **interacted** regression $Y_i\sim 1+W_i+X_i+W_i(X_i-\bar X)$ (§2).

**The OLS-weighting trap (Angrist; Angrist–Pischke MHE ch.3).** With discrete $X$, plain-control OLS and IPW are
*both* weighted averages of group effects $\tau_x$ — but with different weights:
$$\tau^{IPW}=\frac{\sum_x\tau_x\,e(x)\,P(X{=}x)}{\sum_x e(x)\,P(X{=}x)},\qquad
\tau^{OLS}=\frac{\sum_x\tau_x\,\sigma^2_{W|x}\,P(X{=}x)}{\sum_x \sigma^2_{W|x}\,P(X{=}x)},\quad \sigma^2_{W|x}=e(x)(1-e(x)).$$
OLS weights by the **conditional treatment variance** $\sigma^2_{W|x}$ (maximal at $e(x)=\tfrac12$) → over-weights
50/50-split strata, under-weights imbalanced ones; equals the ATE **iff** effects are constant ($\tau_x\equiv\tau$).
IPW weights by treatment probability → targets the ATE.

**Bottom line:** regression can be severely biased if the linear model is wrong globally (I&W); prefer
non-parametric adjustment / IPW / AIPW. This is the "linearity tax" the AIPW/DML machinery (§6, [dml.md](dml.md)) removes.

## 4. Stratification (discrete $X$) → `inference/cluster.py` (aggregate-to-unit analogue)
$$\hat\tau_{STRAT}=\sum_{x}\tfrac{n_x}{n}\hat\tau(x),\qquad
V_{STRAT}=\mathrm{Var}[\tau(X_i)]+E\!\left[\tfrac{\sigma^2_{(1)}(X_i)}{e(X_i)}+\tfrac{\sigma^2_{(0)}(X_i)}{1-e(X_i)}\right].$$
Remarkably $V_{STRAT}$ does **not** depend on the number of strata $p=|\mathcal X|$.

## 5. Inverse-propensity weighting (IPW)
$$\hat\tau_{IPW}=\frac1n\sum_i\!\left[\frac{W_iY_i}{\hat e(X_i)}-\frac{(1-W_i)Y_i}{1-\hat e(X_i)}\right],\qquad
V_{IPW^*}=V_{STRAT}+E\!\left[\frac{(\mu_{(0)}(X)+(1-e(X))\tau(X))^2}{e(X)(1-e(X))}\right]\ge V_{STRAT}.$$
Oracle IPW (true $e$) is unbiased but **inefficient**; with estimated $e$ only consistency was shown.

## 6. Augmented IPW = doubly robust (the workhorse) → `inference/incrementality.py`, `inference/ope.py`
$$\hat\tau_{AIPW}=\frac1n\sum_i\Big[\underbrace{\hat\mu_{(1)}(X_i)-\hat\mu_{(0)}(X_i)}_{\text{regression}}
+\underbrace{W_i\tfrac{Y_i-\hat\mu_{(1)}(X_i)}{\hat e(X_i)}-(1-W_i)\tfrac{Y_i-\hat\mu_{(0)}(X_i)}{1-\hat e(X_i)}}_{\text{IPW on residuals}}\Big].$$
Oracle score $\Gamma_i=\mu_{(1)}(X_i)-\mu_{(0)}(X_i)+W_i\tfrac{Y_i-\mu_{(1)}(X_i)}{e(X_i)}-(1-W_i)\tfrac{Y_i-\mu_{(0)}(X_i)}{1-e(X_i)}$.

- **Weak DR:** consistent if **either** $\hat\mu$ **or** $\hat e$ is consistent.
- **Strong DR (DML, cross-fitting):** if $\mathrm{RMSE}(\hat\mu)=o(n^{-\alpha_\mu})$, $\mathrm{RMSE}(\hat e)=o(n^{-\alpha_e})$ with
  $\alpha_\mu+\alpha_e\ge \tfrac12$ (e.g. both $=\tfrac14$), then
$$\sqrt n(\hat\tau_{AIPW}-\tau)\Rightarrow N(0,V^*),\quad
V^*=\mathrm{Var}[\tau(X)]+E\!\left[\tfrac{\sigma^2_{(1)}(X)}{e(X)}\right]+E\!\left[\tfrac{\sigma^2_{(0)}(X)}{1-e(X)}\right].$$
$V^*$ is the **semiparametric efficiency bound** (Thm 3.4). Cross-fit with $\hat\mu^{(-k(i))},\hat e^{(-k(i))}$.

Variance + CI: $\hat V_{AIPW}=\tfrac1{n-1}\sum_i(\hat\Gamma_i-\hat\tau)^2$, $\ \hat\tau_{AIPW}\pm\Phi^{-1}(1-\alpha/2)\sqrt{\hat V_{AIPW}/n}$.

**Known propensity (Vega's case! Cor 3.3):** with true $e(x)$, AIPW hits $V^*$ using **any** consistent
$\hat\mu$ — *no rate condition*. Since Vega knows $e(x)$, recovery tests can lean on this.

## Vega hooks
- `naive.py` = §1 $\hat\tau_{DM}$ (the biased-under-interference baseline). `cuped.py` = §2 regression adjustment.
- `cluster.py`: §4 aggregate-to-unit + $V_{STRAT}$-style variance (use `statsmodels`/`pyfixest`, not by hand — see ../../STACK.md).
- `incrementality.py`: treatment-vs-holdout is the 2-arm AIPW/DR contrast (§6). `ope.py`: the DR score is the same object.
- Overlap/positivity ↔ SRM & the engine-set $e(x)$. Cross-link [dml.md](dml.md) for the orthogonal-score view.
