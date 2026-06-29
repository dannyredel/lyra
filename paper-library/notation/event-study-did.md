---
sheet: event-study-did
covers: [Wager Causal Inference ch.13 (Event-Study Designs)]
feeds: [inference/cluster.py, Phase-3 DiD verticals, panel/day-level readout caution]
---

# Event studies & difference-in-differences — equations (Wager ch.13)

Panel data $Y_{it}$, $W_{it}\in\{0,1\}$. **Event study** = treatment only switches off→on ($W_{it}\le W_{it'}$ for $t\le t'$).
**Block adoption:** shared event time $H$, $W_{it}=D_i\mathbb 1\{t>H\}$. **Staggered:** own start $H_i$, $W_{it}=\mathbb 1\{t>H_i\}$.

## Key assumptions
- **Non-anticipation** (13.1): $Y_{it}(0)=Y_{it}(1)$ for $t\le H$ (future treatment can't move past outcomes).
- **Parallel trends** (13.2): $\exists\,\beta_t$ with $E[Y_{it}(0)-Y_{i1}(0)]=\beta_t$ for all $i$ (untreated potential outcomes evolve in parallel).

## Estimand
$$\bar\tau_{ATT}=\frac{\sum_{i:D_i=1}\sum_{t>H}(Y_{it}(1)-Y_{it}(0))}{|\{i:D_i=1\}|\,(T-H)}\quad(\text{block}),\qquad
\text{staggered: avg over }(i,t)\text{ with }t>H_i\text{ vs never-treated }Y_{it}(\infty).$$

## DiD (block) — post-minus-pre, adopters minus non-adopters
$$\hat\tau_{DID}=\big[\bar Y^{\text{post}}_{D=1}-\bar Y^{\text{pre}}_{D=1}\big]-\big[\bar Y^{\text{post}}_{D=0}-\bar Y^{\text{pre}}_{D=0}\big].$$
**Double-robust flavor:** unbiased under *randomized adoption* (Thm 1.1) **or** under *parallel trends* (Thm 13.2). Lower variance than simple differencing when non-anticipation holds.

## Two-way fixed effects (TWFE) — and its staggered trap ⚠️
$$Y_{it}\sim\alpha_i+\beta_t+W_{it}\tau.$$
Equals $\hat\tau_{DID}$ under block adoption. **Under staggered adoption the TWFE $\hat\tau$ is biased / inconsistent for
$\bar\tau_{ATT}$** — its implied weights $\gamma_{it}$ (where $\hat\tau=\sum_{i,t}\gamma_{it}Y_{it}$) can be **negative** for
treated cells ("forbidden comparisons": already-treated units used as controls). Can converge *negative* even if every effect is positive.

## Fix: averaged saturated regression (ASR / imputation)
Saturate the treatment term, then average over treated cells:
$$Y_{it}\sim\alpha_i+\beta_t+W_{it}\theta_{it},\qquad \hat\tau_{ASR}=\frac{\sum_{W_{it}=1}\hat\theta_{it}}{|\{W_{it}=1\}|}.$$
Unbiased for $\bar\tau_{ATT}$ under (13.1)+(13.2) (Borusyak–Jaravel–Spiess imputation; Wooldridge 2025). Implied weights satisfy
$\sum_t\gamma_{it}=0$ (kills $\alpha_i$), $\sum_i\gamma_{it}=0$ (kills $\beta_t$), $\sum\gamma_{it}=1/\#\text{treated}$. Needs *some* never-treated units.
Efficient GLS variant: $\gamma=\arg\min\sum_i\gamma_{i\cdot}'\Sigma\gamma_{i\cdot}$ s.t. those constraints (quadratic program). **Cohort-wise** effects $\bar\tau_{ATT}^{h,t}$ (Callaway–Sant'Anna, Sun–Abraham) when no never-treated exist.

## Inference
**Cluster by unit** (all obs from a unit are dependent) — unit-clustered jackknife (Bertrand–Duflo–Mullainathan; ties to Hansen 2025 jackknife SE + [[interference]] §5 block-$G$).

## Synthetic control / SDID (when parallel trends fails)
Reweight controls $\gamma_i\ge0,\sum\gamma_i=1$ to restore pre-event parallel trends, then weighted DiD:
$$\hat\tau_{SDID}=\big[\bar Y^{\text{post}}_{D=1}-\bar Y^{\text{pre}}_{D=1}\big]-\sum_{i:D_i=0}\gamma_i\big[Y^{\text{post}}_i-Y^{\text{pre}}_i\big],\quad
\gamma=\arg\min_{\gamma',\alpha}\Big\|\textstyle\sum_{D_i=0}\gamma_i'Y_i^{(1:H)}-\alpha-\bar Y^{(1:H)}_{D=1}\Big\|^2.$$
Formal backing: interactive fixed-effects $Y_{it}=A_{i\cdot}\!\cdot B_{t\cdot}+W_{it}\tau+\varepsilon_{it}$; or matrix-completion (nuclear-norm) imputation of $Y_{it}(\infty)$.

## Vega hooks (use libraries — ../../STACK.md)
- **Phase-3 DiD verticals** + any **panel/day-level readout** over the event log: beware TWFE staggered bias; use ASR / Sun–Abraham via **`pyfixest`**, Callaway–Sant'Anna via **`differences`**, SDID via R `synthdid`.
- **`inference/cluster.py`:** unit-clustered SEs are the DiD analogue of cluster-robust inference (block dependency).
- Long-term/temporal split (config `metrics.horizons`) — event-study framing for short- vs long-run effects.
- **Acquire:** Callaway–Sant'Anna 2021, Sun–Abraham 2021, Borusyak–Jaravel–Spiess 2024, de Chaisemartin–d'Haultfœuille 2020, Arkhangelsky et al. 2021 (SDID). Cross-link [[interference]], [[balancing]].
