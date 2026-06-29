# NOTATION.md — canonical symbols + crosswalk

The one notation the library translates everything into. Write all math as **LaTeX inside markdown**:
inline `$...$` (e.g. `$E(\Delta x_{it}\,\Delta u_{it})=0$` → $E(\Delta x_{it}\,\Delta u_{it})=0$),
display `$$...$$`. In tables use `\mid` for the conditioning bar (a literal `|` breaks the table).
Aligned to Vega's [`EVENT_LOG.md`](../../EVENT_LOG.md) fields where possible.

## Canonical symbols

| Symbol | Meaning | Vega event-log tie-in |
|---|---|---|
| $i$ | unit (agent/user) | `user_id` |
| $c$ | cluster (geo/segment) | `cluster_id` |
| $t$ | time / simulated day | `day`, `ts` |
| $j$ | offer | `offer_id` |
| $e$ | experiment | `experiment_id` |
| $W$ | treatment arm / indicator, $W\in\{0,1\}$ (or control/treatment/holdout) | `variant` |
| $a$ | treatment **allocation** (treated share at assignment) | `allocation` |
| $Y$ | outcome (primary-metric realization) | `value` / metric |
| $Y(w)$ | potential outcome under arm $w$ | — (counterfactual) |
| $X$ | pre-treatment covariates | pre-period features |
| $\tau$ | treatment effect (ATE); $\tau(x)$ = CATE | — |
| $\tau_i$ | **per-unit ground-truth effect** | `ground_truth_tau` (engine-written, estimator-hidden) |
| $m(X)$ | propensity / treatment model $m(X)=E[W\mid X]$ | `propensity` (logged, for OPE) |
| $\ell(X)$ | outcome regression $\ell(X)=E[Y\mid X]$ | — |
| $g(w,X)$ | arm-specific outcome $g(w,X)=E[Y\mid W=w,X]$ | — |
| $\eta$ | nuisance parameters $(\ell, m, g, \dots)$ | — |
| $\psi$ | score / moment function | — |
| $\theta$ | low-dim target parameter (often $\tau$) | — |
| $\alpha$ | test level (Type-I); $1-\alpha$ CI | `inference.alpha` |
| $K$ | cross-fitting folds | — |

> Conflicts to watch: we use $W$ for treatment (Wager/Athey convention) and $a$ for allocation;
> DML papers use $D$ for treatment and $m_0$ for $E[D\mid X]$ — translate $D\to W$, $m_0\to m$ on
> their sheets. Market balance (Johari) and the CS tuning constant are both often written $\rho$ —
> disambiguate per sheet.

## Crosswalk (paper symbol → canonical)

| Paper / topic | Their symbol | → Canonical | Note |
|---|---|---|---|
| CCDDHNR 2018 (DML) | $D$, $m_0(X)=E[D\mid X]$, $\ell_0=E[Y\mid X]$, $g_0$ | $W,\ m,\ \ell,\ g$ | partialling-out form |
| Wager (book) | $W$, propensity $e(x)$ | $W,\ m$ | $e(x)\to m(X)$ |
| Imbens–Rubin | $T$ or $D$, $e(x)$ | $W,\ m$ | potential outcomes $Y(0),Y(1)$ ✓ |
| Johari 2021 (two-sided) | designs CR/LR/TSR; market balance $\rho$ | designs; $a$ for share | keep $\rho$ for market balance |
| Howard 2022 (CS) | $\text{CI}_t$, mixture $\rho$ | $\text{CI}_t$; CS-$\rho$ | CS tuning $\rho^2 \neq$ market balance |
| OPE (Dudík/Swaminathan) | logging policy $\mu$, target $\pi$, propensity $p$ | $\mu,\ \pi,\ m$ | importance weight $\pi/\mu$ |
| **Wager book (ch.1–4)** | $W$ treatment; $e(x)$ propensity; $\mu_{(w)}(x)=E[Y\mid X,W{=}w]$; $\tau(x)$ CATE | $W$; $m(X)$; $g(w,X)$; $\tau(x)$ | $e\to m$, $\mu_{(w)}\to g(w,\cdot)$ |
| ⚠️ **Wager $m(x)$ clash** | $m(x)=E[Y\mid X=x]$ (marginal **outcome**) | $\ell(X)$ | Wager's $m$ is the OUTCOME regression, NOT propensity. Canonical/DoubleML $m(X)=E[W\mid X]$ is the propensity. Always translate Wager $m\to\ell$, $e\to m$. |
| Wager AIPW/R-learner | score $\Gamma_i$; featurization $\psi(x)$; $R$-loss | $\psi$ (score), $\psi(x)$ feats | $\Gamma_i$ = AIPW score (= canonical $\psi$ moment) |
| Wager ch.11–12 (interference) | $\mathbf w\in\{0,1\}^n$; exposure $H_i(\mathbf w)$; exposure propensity $e_i(h)$; HT weight $\Gamma_i(h)$; dep. graph $G$; exposure effect $\bar\tau(h,h')$ | keep as-is | bold = cross-unit vectors; $e_i(h)$ generalizes propensity to exposure levels |
| Wager ch.10 (IV/LATE) | instrument $Z$; received treatment $W$; compliance type $C_i$; MTE $\tau(u)$ | $Z$, $W$, $\tau(u)$ | $W$ here is *received* (endogenous), $Z$ the randomized nudge |
| Wager ch.6 (bandits) | arm $k$; assignment prob $e_{t,k}$; regret $R_T$ | $e_{t,k}$ ~ time-varying $m$ | $1/\sqrt{e}$ (not $1/e$) weights for valid adaptive CIs |
| Wager ch.5 (policy) | policy $\pi(x)$; value $V(\pi)$; AIPW score $\hat\Gamma_i$; priority $S(x)$ | $\pi$, $V$, $\hat\Gamma_i$ | $V_{AIPW}(\pi)$ = DR off-policy value; $\hat\Gamma_i$ same as ch.3 AIPW score |
| Wager ch.13 (DiD/panel) | $Y_{it}$, $W_{it}$; adoption $D_i$/$H_i$; $\bar\tau_{ATT}$; TWFE $\alpha_i,\beta_t$; weights $\gamma_{it}$ | keep | panel double-index $(i,t)$; $\beta_t$ = time FE (≠ regression coef elsewhere) |
| Causal forests (GRF) | forest weights $\alpha_i(x)$; `Y.hat` $=\hat\ell$; `W.hat` $=\hat e$; DR score $\hat\Gamma_i$ | $\alpha_i(x)$, $\ell$, $m$, $\hat\Gamma_i$ | grf `Y.hat`/`W.hat` = canonical $\ell$/$m$; $\alpha_i(x)$ = adaptive kernel weight |
| Metalearners | $\hat\mu_{(w)}$; imputed effects $\tilde D_i$; X-weight $g(x)$ | $g(w,X)$, $\tilde D_i$, $g(x)$ | S/T/X/R/DR; $g(x)$ commonly $=\hat e$ |

_Add a row whenever a new sheet surfaces a clash._
