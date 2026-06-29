---
sheet: dml
covers: [CCDDHNR 2018, Ahrens et al 2026, Belloni-Chernozhukov-Hansen 2014]
feeds: [inference/cuped.py, inference/hte.py, inference/ope.py]
---

# Double/Debiased Machine Learning (DML) — equations

Seeded from standard knowledge; refine against the PDFs in `pdfs/01-causal-ml-dml/` when processed.
Canonical notation per [NOTATION.md](NOTATION.md): treatment $W$, propensity $m(X)=E[W\mid X]$,
outcome regression $\ell(X)=E[Y\mid X]$, arm outcomes $g(w,X)=E[Y\mid W=w,X]$, nuisances $\eta$,
target $\theta$.

## 1. Partially Linear Regression (PLR) — the canonical case
CCDDHNR write $D$ for treatment; here $W$ (continuous or binary):

$$Y = W\,\theta_0 + g_0(X) + U, \qquad E[U \mid X, W] = 0$$
$$W = m_0(X) + V, \qquad E[V \mid X] = 0$$

$\theta_0$ is the target (a constant treatment effect). Plugging an ML estimate of $g_0$ into a
naive moment leaves **regularization bias** of the order of the nuisance rate, so $\hat\theta$ is
not $\sqrt{N}$-consistent.

## 1.1 Why naive ML fails — two biases, two fixes
Plug ML estimates $\hat g_0,\hat m_0$ into the moment for $\theta$ and decompose $\sqrt N(\hat\theta-\theta_0)=a+b+c$:
- $a$ — the $\sqrt N$-Gaussian sampling term (fine).
- $b$ — **regularization bias**: with the *naive* score, $b\propto \tfrac1{\sqrt N}\sum_i m_0(X_i)\,[g_0(X_i)-\hat g_0(X_i)]$ —
  first-order in the ML bias of $\hat g_0$, so $b=O(\sqrt N\,N^{-\alpha_g})\to\infty$ and $\lvert\sqrt N(\hat\theta-\theta_0)\rvert\to_p\infty$.
- $c$ — **overfitting bias**: $c\propto \tfrac1{\sqrt N}\sum_i V_i\,[\hat g_0(X_i)-g_0(X_i)]$ — nonzero when $\hat g_0$ is fit on the *same* data ($V$ correlates with the fit's error).

**Fix I — Neyman orthogonality** (kills $b$): the orthogonal (partialling-out/Robinson) score replaces $b$ with the **product** of the two nuisance errors,
$$b=(\text{E}[V^2])^{-1}\tfrac1{\sqrt N}\sum_i \underbrace{[\hat m_0(X_i)-m_0(X_i)]}_{N^{-\alpha_m}}\underbrace{[\hat g_0(X_i)-g_0(X_i)]}_{N^{-\alpha_g}},$$
so $b=O(\sqrt N\,N^{-(\alpha_m+\alpha_g)})\to_p 0$ once $\alpha_m+\alpha_g\ge\tfrac12$ (e.g. both $N^{-1/4}$).
**Fix II — sample-splitting / cross-fitting** (kills $c$): fit nuisances on a *different* fold than the one used to
evaluate the moment → $V\perp$ fit-error → $c\to_p 0$.

**FWL / Robinson.** The partialling-out estimator is Robinson (1988) made feasible with ML: residualize $Y$ and $D$
on $X$ (Frisch–Waugh–Lovell), then regress residual on residual. Orthogonality = "FWL with ML nuisances."

## 2. Neyman-orthogonal score (partialling-out / Robinson form)

$$\psi(O;\theta,\eta) = \big(\,Y - \ell_0(X) - \theta\,(W - m_0(X))\,\big)\,\big(W - m_0(X)\big),
\qquad \eta = (\ell_0, m_0)$$

**Orthogonality:** the Gateaux derivative $\partial_\eta\, E[\psi]$ vanishes at $(\theta_0,\eta_0)$,
so small nuisance errors don't propagate to first order — this is what makes ML nuisances admissible.

## 3. Estimator — cross-fitting (the "double" + sample-splitting)
Split into $K$ folds. For fold $k$, fit $\hat\ell_{-k}, \hat m_{-k}$ on the **other** folds, then form
out-of-fold residuals $\tilde Y_i = Y_i - \hat\ell_{-k}(X_i)$ and $\tilde W_i = W_i - \hat m_{-k}(X_i)$.
The DML estimator is residual-on-residual regression:

$$\check\theta = \Big(\textstyle\sum_i \tilde W_i \tilde W_i\Big)^{-1}\Big(\textstyle\sum_i \tilde W_i \tilde Y_i\Big)$$

## 3.1 The full algorithm step-by-step ($k$-fold) — from Daniel's notes
Notes' notation: outcome $y$, treatment $d$, controls $x$, target effect $\alpha$ (= canonical $\theta_0$);
folds $S_1,S_2$ ($k=2$). Two interchangeable Neyman-orthogonal **scores**:

**(a) Partialling-out (Robinson) score.**
- **Step 0** — partition into $k$ folds $S_1,S_2$ (size $n/k$).
- **Step 1** — on $S_1$, regress $y$ on $x$ (Lasso/Post-Lasso): $y_{i1}=x_{i1}'\theta_{01}+v_{i1}$;
  out-of-fold residuals on $S_2$: $\hat v_{i2}=y_{i2}-x_{i2}'\hat\theta_1$.
- **Step 2** — on $S_1$, regress $d$ on $x$: $d_{i1}=x_{i1}'\gamma_{01}+u_{i1}$; residuals $\hat u_{i2}=d_{i2}-x_{i2}'\hat\gamma_1$.
- **Step 3** — regress $\hat v_{i2}$ on $\hat u_{i2}$: $\ \hat\alpha_2=\big(\sum_i\hat u_{i2}^2\big)^{-1}\sum_i\hat u_{i2}\hat v_{i2}$.
- **Steps 4–6** — swap: fit $(\hat\theta_2,\hat\gamma_2)$ on $S_2$, residualize on $S_1$ → $\hat\alpha_1$.
- **Step 7** — aggregate (DML1/DML2 below).

**(b) IV-type (Neyman) score** — differs in two steps:
- **Step 1$'$** — regress $y$ on $x$ *without penalizing* $d$: $y_{i1}=\tilde\alpha_0 d_{i1}+x_{i1}'\beta_{01}+\varepsilon_i$
  ($\hat g_1(x)=x'\hat\beta_1$); residuals $\hat\varepsilon_{i2}=y_{i2}-\tilde\alpha d_{i2}-x_{i2}'\hat\beta_1$.
- **Step 3$'$** — regress $\hat\varepsilon_{i2}$ on $d_{i2}$ using $\hat u_{i2}$ as **instrument**:
  $\ \hat\alpha_2=\big[\sum_i\hat u_{i2}d_{i2}\big]^{-1}\big[\sum_i\hat u_{i2}\hat\varepsilon_{i2}\big]$.

Both are orthogonal; `doubleml` exposes them as `score="partialling out"` and `score="IV-type"`. Nuisances:
Lasso/Post-Lasso, random forest, boosting, etc.

**DML1 vs DML2 (aggregation across folds).**
$$\textbf{DML1: }\ \hat\alpha_{\rm DML}=\frac1k\sum_{k}\hat\alpha_k\qquad\text{(solve each fold, then average)}$$
$$\textbf{DML2: }\ \hat\alpha_{\rm DML}=\Big[\tfrac1n\sum_{k}\sum_i\hat u_{i}\,d_{i}\Big]^{-1}\Big[\tfrac1n\sum_{k}\sum_i\hat u_{i}\,\hat\varepsilon_{i}\Big]\quad\text{(pool moments, solve once)}$$
DML2 pools the empirical moment across folds before solving — usually more stable; the `doubleml` default.

## 4. Interactive Regression Model (IRM) — binary $W$, ATE (= AIPW / doubly-robust score)

$$\psi = \big(g(1,X) - g(0,X)\big)
+ \frac{W\,(Y - g(1,X))}{m(X)}
- \frac{(1-W)\,(Y - g(0,X))}{1 - m(X)}
- \theta, \qquad \theta_0 = E[Y(1) - Y(0)]$$

Doubly robust: consistent if **either** $g$ **or** $m$ is correct. (Same DR score the OPE leg uses —
see `inference/ope.py`.)

## 5. Inference
Under cross-fitting + rate conditions (nuisance $L_2$-rate $o(N^{-1/4})$):

$$\sqrt{N}\,(\check\theta - \theta_0) \xrightarrow{d} N(0, \sigma^2), \qquad
\hat\sigma^2 = \hat J^{-1}\,\hat E[\psi^2]\,\hat J^{-1}, \quad \hat J = \hat E[\partial_\theta \psi]$$

CI: $\ \check\theta \pm z_{1-\alpha/2}\,\hat\sigma/\sqrt{N}$.

## 6. Assumptions / failure modes
- Overlap: $m(X) \in (\epsilon, 1-\epsilon)$ (else IRM weights blow up — clip/trim).
- Nuisance rate $o(N^{-1/4})$ — slower ML breaks $\sqrt{N}$-normality.
- Orthogonality **and** cross-fitting are both required; dropping either reintroduces bias.

## 7. Vega hooks (use libraries, don't hand-roll — see ../../STACK.md)
- **CUPED** (`inference/cuped.py`): the linear special case of orthogonalized adjustment — DML with
  linear nuisances on pre-period covariates $X$. Implement via `statsmodels`/`linearmodels`; recovery
  test: CI still covers $\tau$, narrower.
- **HTE** (`inference/hte.py`): CATE $\tau(x)$ via DML — `econml` (`LinearDML`, `CausalForestDML`) or
  `doubleml` (`DoubleMLIRM`/`DoubleMLPLR`).
- **OPE** (`inference/ope.py`): the IRM/DR score in §4 is the doubly-robust off-policy estimator.

## 8. Double Selection (post-double-selection; Belloni–Chernozhukov–Hansen 2014)
The linear ancestor of the orthogonal score. To estimate $\alpha$ in $y=d\,\alpha+x'\beta+\varepsilon$ with
high-dimensional controls $x$:
- **Step 1** — Lasso regress $y$ on $x$; keep the selected controls $\hat I_1$ (predict the **outcome**).
- **Step 2** — Lasso regress $d$ on $x$; keep the selected controls $\hat I_2$ (predict the **treatment**).
- **Step 3** — OLS of $y$ on $d$ and the **union** $\hat I_1\cup\hat I_2$; the coefficient on $d$ is $\hat\alpha$.

**Why the union — the OMV problem (the whole point):** *single* selection (Step 1 only) can drop a control
$x_j$ that weakly predicts $y$ but **strongly predicts $d$** — i.e. a confounder → omitted-variable bias in
$\hat\alpha$. Including controls that predict **either** $y$ **or** $d$ closes that gap → uniformly valid
inference under approximate sparsity. Same intuition as the partialling-out score: residualize $y$ **and** $d$ on $x$.

**Double-Selection IV / PLIV (Chernozhukov et al. 2015).** Endogenous $d$ with instruments $z$ and many controls $x$:
$$y_i=\alpha_0 d_i+x_i'\beta_0+\varepsilon_i,\qquad d_i=x_i'\gamma_0+z_i'\delta_0+u_i.$$
Double-select the controls (from the $y$- and $d$-equations), residualize, then run **IV** of $y$ on $d$ using the
control-residualized instrument. Same orthogonality idea, IV moment. Relevant to Vega's IV/incrementality leg — see [[iv-late]].

## 9. The estimator family (comparison)
| Estimator | Idea | Bias handling | $\sqrt n$-valid? |
|---|---|---|---|
| **Naive post-selection** | single Lasso $Y\sim X$, then OLS $Y$ on $D$ + selected | **OMV bias** — drops controls that predict $D$ but weakly predict $Y$ | ✗ |
| **Double selection** (BCH 2014) | Lasso $Y\sim X$ **and** $D\sim X$, OLS on the union | removes OMV bias via the union | ✓ (sparsity) |
| **Partialling-out / Robinson** | residualize $Y,D$ on $X$ (ML), residual-on-residual | Neyman-orthogonal | ✓ |
| **DML** (CCDDHNR 2018) | partialling-out **or** IV-type score + **cross-fitting**, any ML | orthogonality (reg. bias) + cross-fit (overfit bias) | ✓, efficient |
| **PLIV / DS-IV** (Cherno 2015) | + instrument $z$ for endogenous $d$, many controls | orthogonal IV moment | ✓ |

All but the naive estimator are $\sqrt n$-valid under approximate sparsity / rate conditions; DML is the most
general (arbitrary ML nuisances). The deep Lasso machinery (rigorous/adaptive/root-Lasso, penalty loadings,
PLIV proofs) lives in Daniel's Notion export: `paper-library/DML Export Notion/`.
