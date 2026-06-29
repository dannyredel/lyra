---
sheet: frugal-parameterization
covers: [Evans & Didelez 2024 (JRSS-B) - The Frugal Parameterization; Orduz - Frugal Param in PyMC; pkg causl]
feeds: [lyra/dgp (the DGP zoo), Vega ground-truth simulation, recovery harness]
---

# Frugal parameterization — author DGPs with a *known* causal effect

**Problem.** In a generative model $Z\to X\to Y$, $Z\to Y$, the estimand (ATE $=\mathbb E[Y\mid do(1)]-
\mathbb E[Y\mid do(0)]$) is a **marginal of the interventional law**, but you only specify *conditionals*
$p_{Y\mid XZ}$. So the ATE is a tangled function of all params (it equals the coefficient $\beta_1$ *only*
in the linear-Gaussian case; not for logistic / interactions). ⇒ you can't put a prior on the effect, can't
simulate data with a chosen ATE without reverse-engineering, and hit the **g-null paradox**. Our hand-built
zoo dodges this by computing truth from expected potential outcomes — frugal makes truth a **primitive**.

**Idea — put the causal effect at the center.** Decompose the joint into 3 **variation-independent** pieces:
$$\theta=(\;\underbrace{\theta_{ZX}}_{\text{(a) the past}}\;,\;\underbrace{\theta^\star_{Y\mid X}}_{\text{(b) causal margin}}\;,\;\underbrace{\phi^\star_{YZ\mid X}}_{\text{(c) dependence}}\;).$$
- **(a) past** $p_{ZX}$ — confounder dist + propensity $p_{X\mid Z}$.
- **(b) causal margin** $p^\star_{Y\mid X}(y\mid x)=p_{Y\mid X}(y\mid do(x))$ — **write the ATE/CATE here, directly.**
- **(c) dependence** $\phi^\star_{YZ\mid X}$ — a conditional **odds ratio** (discrete; obs = causal invariant,
  $\phi^\star=\phi$) or **copula** (continuous), carrying confounding *not* mediated by $X$.

**Variation independence** ⇒ parameter spaces are a Cartesian product: *any* effect is compatible with *any*
confounding and *any* propensity. A product prior $p(\text{past})p(\text{causal})p(\text{dep})$ is always
valid; an informative prior on the ATE (from a pilot RCT) doesn't leak into the propensity/confounding.

## Gaussian recipe (the one to simulate from)
Causal margin $Y^\star\sim N(\mu_0+\delta x,\sigma_c^2)$ (**$\delta$ = ATE, set it**); $Z\sim N(0,1)$; couple via
Gaussian copula corr $\rho$. Condition on $Z$ (+ no-unmeasured-confounding) → the **observational likelihood**:
$$\boxed{\;Y\mid X{=}x,Z{=}z\ \sim\ N\big((\mu_0+\delta x)+\rho\sigma_c z,\ \ \sigma_c^2(1-\rho^2)\big)\;}$$
Simulate: draw $Z$; $X\sim\text{Bernoulli}(\sigma(\alpha_0+\alpha_1 Z))$; then $Y$ from the box. **ATE $=\delta$
exactly, for any $\alpha,\rho$.** Map to standard $Y\mid X,Z\sim N(\beta_0+\beta_1x+\beta_2z,\sigma^2)$:
$$\beta_0=\mu_0,\ \beta_1=\delta,\ \beta_2=\rho\sigma_c,\ \sigma=\sigma_c\sqrt{1-\rho^2};\qquad
\delta=\beta_1,\ \sigma_c=\sqrt{\sigma^2+\beta_2^2},\ \rho=\beta_2/\sqrt{\sigma^2+\beta_2^2}.$$
$\rho^2$ = fraction of interventional outcome variance from the confounder ($\rho=0$ ⇒ unconfounded). Always
$\sigma_c\ge\sigma$.

## Cognate distributions — swap estimands by a weight kernel (Thm 3.1)
$p^\star_{Y\mid X}(y\mid x)=\int p_{Y\mid ZX}(y\mid z,x)\,w(z\mid x)\,dz$; the choice of $w$ picks the estimand:
$w=p_Z$ → **ATE (back-door)**; $w=p_{Z\mid X{=}1}$ → **ETT**; $p_{Z\mid X{=}0}$ → **ETC**; $w=p_{Z\mid X}$ →
ordinary conditional. So one DGP serves multiple estimands, each with its own known truth.

## General machinery
- Discrete: conditional **odds ratio** (variation-independent; recover joint by iterative proportional fitting).
- Continuous/non-Gaussian: **copulas** (Sklar) — any marginals + any family (Clayton/Frank/Gumbel). Mixed:
  dichotomized-Gaussian copula. Many confounders: **vine / pair-copula**. Continuous $X$: dose-response margin.
- Survival MSMs / dynamic treatment with time-varying confounding: frugal avoids the simulation "nightmare".
- Reference impl: R pkg **`causl`** (Evans). PyMC pattern: priors on $\delta$, copula $\rho$, propensity separate.

## Why for Vega's DGP zoo
1. **Estimand as a primitive** (set $\delta$ / a CATE function $\delta(c)$), not derived → exact ground truth for the recovery harness.
2. **Confounding as a free dial** ($\rho$ / odds ratio) *independent of the effect* → sweep 0→strong with ATE fixed; demonstrate naive bias as an asserted quantity; stress-test DML/IPW/AIPW (our NB 01 robustness grid, principled).
3. **Switch ATE/ETT/ETC** via the weight kernel — a platform reporting multiple estimands validates each vs its own truth.
4. **CATE→policy ground truth**: $\delta=\delta(c)$ via a link on covariates → known CATE for the inference engine's CATE leg (NB 09).
5. Avoids g-null / incompatible-margin pathologies when the zoo grows time-varying-confounding worlds.
6. **Bayesian recovery test**: combine a simulated pilot-RCT prior on $\delta$ with observational data; check the posterior covers the planted $\delta$.

**Possible promotion:** a `lyra/dgp/frugal.py` `FrugalDGP(delta, rho, propensity, copula=...)` whose
`ground_truth().ate == delta` by construction — a copula-confounded upgrade to `DGPLevel1`.
