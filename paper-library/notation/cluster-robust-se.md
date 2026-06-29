---
sheet: cluster-robust-se
covers: [Cameron & Miller 2015 (Practitioner's Guide), MacKinnon 2022, sandwich-CL vignette, Hansen 2024 (CV3)]
feeds: [lyra/se.py, notebooks/04 cluster-robust SEs]
---

# Cluster-robust standard errors — equations (NB 04)

Model $\mathbf y=\mathbf X\boldsymbol\beta+\mathbf u$, stacked by cluster $g=1..G$; cluster block
$(\mathbf y_g,\mathbf X_g,\mathbf u_g)$ size $N_g$, $\sum_g N_g=N$, $K$ regressors. OLS residuals
$\hat{\mathbf u}_g$; **cluster score** $\hat{\mathbf s}_g=\mathbf X_g^\top\hat{\mathbf u}_g$ ($K\times1$);
hat block $\mathbf H_{gg}=\mathbf X_g(\mathbf X^\top\mathbf X)^{-1}\mathbf X_g^\top$,
$\mathbf M_{gg}=\mathbf I_{N_g}-\mathbf H_{gg}$.

## The ladder (each generalizes an HC; all → HC0–HC3 when $G=N$ — a clean unit-test invariant)

**CV1 (the workhorse, CRVE).**
$$\text{CV1}=c\,(\mathbf X^\top\mathbf X)^{-1}\Big(\sum_{g}\hat{\mathbf s}_g\hat{\mathbf s}_g^\top\Big)(\mathbf X^\top\mathbf X)^{-1},\qquad c=\frac{G}{G-1}\frac{N-1}{N-K}.$$
Meat = sum of outer products of cluster scores. $c$ is Stata's default ($G/(G-1)$ alone is the simpler
SAS form). Consistent as $G\to\infty$. **Rank $=\min(K,G-1)$** → can't joint-test more than $G-1$ params.

**CV2 (bias-reduced, "HC2 for clusters", Bell–McCaffrey).** Transform residuals by the inverse symmetric
square root of the hat block, then standard meat:
$$\grave{\mathbf s}_g=\mathbf X_g^\top \mathbf M_{gg}^{-1/2}\hat{\mathbf u}_g,\qquad
\text{CV2}=(\mathbf X^\top\mathbf X)^{-1}\Big(\sum_g\grave{\mathbf s}_g\grave{\mathbf s}_g^\top\Big)(\mathbf X^\top\mathbf X)^{-1}.$$
Unbiased iff $\mathrm E[\mathbf u_g\mathbf u_g^\top]=\sigma^2\mathbf I$. **`estimatr::lm_robust` default.**

**CV3 (jackknife, "HC3 for clusters", Hansen/MacKinnon).** Leave-one-cluster-out — the fast, preferred form:
$$\text{CV3}=\frac{G-1}{G}\sum_{g}(\hat{\boldsymbol\beta}^{(g)}-\bar{\boldsymbol\beta})(\hat{\boldsymbol\beta}^{(g)}-\bar{\boldsymbol\beta})^\top,
\quad \hat{\boldsymbol\beta}^{(g)}=\hat{\boldsymbol\beta}-(\mathbf X^\top\mathbf X)^{-1}\mathbf X_g^\top \mathbf M_{gg}^{-1}\hat{\mathbf u}_g,$$
$\bar{\boldsymbol\beta}=\frac1G\sum_g\hat{\boldsymbol\beta}^{(g)}$. Closed-form update ⇒ **no refits**. Most
conservative (can under-reject); what `summclust` computes. (Equivalent residual-transform form uses
$\mathbf M_{gg}^{-1}$ with leading $\frac{G-1}{G}$.)

## Wild cluster bootstrap (WCR — restricted, the small-$G$ fix)
Bootstrap the **cluster-robust $t$** (pivotal), not $\hat\beta$. Test $H_0:\beta_k=\beta_0$:
1. OLS **subject to $H_0$** → $\tilde{\boldsymbol\beta}$, restricted residuals $\tilde{\mathbf u}_g$, scores
   $\tilde{\mathbf s}_g$. Compute original $t=\hat\tau$ from the unrestricted fit.
2. For $b=1..B$: one weight **per cluster** $v_g^{*}$ (same for all obs in $g$), **Rademacher** $\pm1$ w.p.½;
   bootstrap scores $\mathbf s_g^{*}=v_g^{*}\tilde{\mathbf s}_g$ → $\hat\beta^{*}_b$ (only the $G$-vector varies;
   $\mathbf X_g^\top\mathbf X_g$ cached) → cluster-robust $t^{*}_b$.
3. **p-value** symmetric $\hat P^{*}=\frac1B\sum_b\mathbf1(|t^{*}_b|>|t|)$; equal-tail variant for CIs (invert).
- **Weights:** Rademacher (default; only $2^{G-1}$ distinct $|t|$ → p-value can't be finer than $1/2^{G-1}$,
  so at $G=5$ floor $=0.0625$). Use **Webb 6-point** $\{\pm\sqrt{0.5},\pm1,\pm\sqrt{1.5}\}$ when $G<10$.
  Switch off Rademacher when $2^G<B+1$. Pick $B$ so $\alpha(B+1)\in\mathbb Z$ (e.g. $B=9999$).
- **WCU (unrestricted)** uses $\hat{\mathbf s}_g$: DGP independent of $H_0$ → one draw set serves all tests/CIs,
  but worse size than WCR. Why bootstrap $t$: size error $O(G^{-1})\to O(G^{-3/2})$ (asymptotic refinement).

## The few-clusters problem
- **Why CV1 over-rejects small $G$:** OLS overfits → residuals too small → meat biased down; and the meat
  averages only $G$ terms (no LLN). Empirical size (crit 1.96): ≈ .07/.08/.12/.21 at $G=30/20/10/5$ (worse
  unbalanced; worst with **few *treated* clusters**, even if total $G$ large).
- **dof, not $N(0,1)$:** use $T(G-1)$ (Bester–Conley–Hansen). **Bell–McCaffrey/Imbens–Kolesár data-driven dof**
  $v^*=(\sum_j\lambda_j)^2/\sum_j\lambda_j^2$ (Satterthwaite, eigenvalues of $\mathbf G^\top\hat\Omega\mathbf G$).
  Best small-$G$ analytic combo: **CV2 + $T(v^*)$**. Effective clusters $G^*=G/(1+\delta)$ (Carter et al.) —
  trouble when $G^*<20$.
- **Use the WCR bootstrap** whenever $G$ small/moderate or unbalanced; Webb weights for $G<10$.

## Packages (STACK.md `lyra/se.py`)
- **Python:** `statsmodels` `cov_type="cluster"` (CV1-ish); **`pyfixest`** `vcov={"CRV1"/"CRV3":"g"}` +
  `.wildboottest(...)`; **`wildboottest`** (port of `fwildclusterboot`). · **R:** `sandwich::vcovCL`
  (`type=HC0–HC3`, `cadjust`), `vcovBS(type="wild"/"webb")`; `estimatr::lm_robust(se_type="CR2")`;
  `fwildclusterboot::boottest`; `summclust`. **Gotcha:** finite-sample factors differ across packages (main
  source of disagreement).

## NB 04 demos (Monte-Carlo vs known truth — DGP $y_{ig}=\beta x_g+\alpha_g+\varepsilon_{ig}$, ICC $\rho_u$)
1. **Naive iid SE under-covers** under clustering; recover the **Moulton factor** $\tau_k\simeq1+\rho_x\rho_u(\bar N_g-1)$ as an asserted quantity.
2. **CV1 + $T(G{-}1)$ fixes it at large $G$** (≈95% coverage).
3. **CV1 over-rejects at small $G$** (sweep $G\in\{5,10,20,50\}$; reproduce the size curve; unbalanced worse).
4. **WCR bootstrap restores size** at small $G$ (Webb for $G<10$); show the $2^{G-1}$ p-value-discreteness wall.
5. **CV1 vs CV2(+$T(v^*)$) vs CV3** head-to-head; assert all → HC1/HC2/HC3 at $G=N$. (+A/A null: no over-flag.)
