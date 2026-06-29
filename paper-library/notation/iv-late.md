---
sheet: iv-late
covers: [Wager Causal Inference ch.10 (Local Average Treatment Effects)]
feeds: [inference/incrementality.py, demand/price-elasticity calibration, Phase-3 auction verticals]
---

# Instrumental variables & LATE — equations (Wager ch.10)

Why it's in Vega: **ghost-ads / encouragement is an IV design** — the reward/exposure is a randomized
*nudge* $Z$ on whether the user actually engages ($W$); incrementality = the compliers' effect. Also the
**supply–demand IV** is the price-elasticity story for the marketplace.

## Setup
Instrument $Z$, treatment received $W$ (endogenous), outcome $Y$. Treatment potential outcomes
$W_i(z)$, so $W_i=W_i(Z_i)$. Four assumptions:
- **Exclusion:** $Z$ affects $Y$ only through $W$: $Y_i(w,z)=Y_i(w)$.
- **Exogeneity:** $\{Y_i(0),Y_i(1),W_i(0),W_i(1)\}\perp\!\!\!\perp Z_i$.
- **Relevance:** $E[W_i(1)-W_i(0)]\neq0$.
- **Monotonicity (no defiers):** $P(C_i=\{1,0\})=0$.

## IV estimand (Wald)
$$\hat\tau_{IV}=\frac{\widehat{\mathrm{Cov}}[Y,Z]}{\widehat{\mathrm{Cov}}[W,Z]}\ \xrightarrow{p}\ \tau_{IV}=\frac{\mathrm{Cov}[Y,Z]}{\mathrm{Cov}[W,Z]}.$$
Binary $Z,W$: $\ \tau_{IV}=\dfrac{E[Y\mid Z{=}1]-E[Y\mid Z{=}0]}{E[W\mid Z{=}1]-E[W\mid Z{=}0]}$ (ITT over first stage).

## LATE theorem (compliers)
Under the four assumptions:
$$\tau_{IV}=E\big[Y_i(1)-Y_i(0)\mid C_i=\text{complier}\big].$$
Compliance types from $(W_i(0),W_i(1))$: never-taker, always-taker, **complier**, defier (ruled out).
*Practical:* raw diff-in-means $\div$ first-stage take-up = LATE (e.g. Oregon Medicaid: divide by 0.3).
Different instruments → different complier sets → **different LATEs** (don't naively pool without linearity).

## Supply–demand IV (price elasticity)
Equilibrium $S_i(P_i,Z_i)=Q_i(P_i,Z_i)$; instrument $Z$ shifts supply, never directly demand. Then IV recovers
$$\tau_{IV}=\frac{\int E[Q_i'(p)\mid P_i(0)\le p\le P_i(1)]\,P[P_i(0)\le p\le P_i(1)]\,dp}{\int P[P_i(0)\le p\le P_i(1)]\,dp}$$
— a positive-weighted average of demand slopes over the price range the instrument moves. (Demand work uses $\log Q,\log P$.)

## Marginal treatment effect (MTE) — latent choice / threshold crossing
$W_i=\mathbb 1\{U_i\ge c(Z_i)\}$, $U_i\sim\mathrm{Unif}[0,1]$ WLOG. $\tau(u)=E[Y_i(1)-Y_i(0)\mid U_i=u]$.
Local IV identification: $\ \tau(c(z))=\dfrac{\frac{d}{dz}E[Y\mid Z=z]}{\frac{d}{dz}P(W{=}1\mid Z=z)}.$
LATE = a weighted average of $\tau(u)$ over the compliers the instrument moves; single jump in $c(\cdot)$ ⇒ back to the simple LATE.

## Vega hooks
- **`inference/incrementality.py`:** ghost-ads holdout = encouragement design. The reward $Z$ nudges engagement $W$;
  lift on advertiser conversions among *responders* is a LATE. Validate against the engine's known $\tau$.
- **Calibration / demand:** supply–demand IV ↔ reward-elasticity of completions; anchors the choice-model betas.
- **Phase-3 (auction/Trivago):** bid/price endogeneity → IV. Cross-link [[interference]] (equilibrium effects), [[ate-estimators]].
