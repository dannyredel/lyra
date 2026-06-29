---
sheet: interference
covers: [Wager Causal Inference ch.11 (Spillovers & Interference), ch.12 (Estimating under Interference)]
feeds: [inference/cluster.py, inference/switchback.py, ramp/interference-decay diagnostic, the whole thesis]
---

# Interference & spillovers — equations (Wager ch.11–12)

**This is the Vega thesis chapter.** Under interference SUTVA fails, so each unit has up to $2^n$
potential outcomes $Y_i(\mathbf w)$, $\mathbf w\in\{0,1\}^n$. Everything below is about taming that
with structure (exposure mappings) and doing randomization-based (finite-population) inference.

## 1. Exposure mappings (taming $2^n$ potential outcomes)
An **exposure mapping** $H_i:\{0,1\}^n\to\mathcal H$ summarizes how the *whole* assignment hits unit $i$:
$$Y_i(\mathbf w)=Y_i(\mathbf w')\quad\text{whenever}\quad H_i(\mathbf w)=H_i(\mathbf w').$$
- **Cluster interference:** $H_i(\mathbf w)=(w_j)_{j\in C_i}$ — arbitrary spillover *within* cluster, none across.
  Then SUTVA holds *at the cluster level* → just run a **cluster-randomized** experiment and analyze normally. **(This is why `inference/cluster.py` is valid.)**
- **Network interference:** $H_i(\mathbf w)=(w_j)_{j\in\{i\}\cup N_i}$ for neighbors $N_i$. Can't always cluster away.
- **Nested null hierarchy** (ch.11) for *testing* which exposure is needed:
  $H_0$ no effect $\subset$ $H_1$ no spillover (SUTVA) $\subset$ $H_2$ anonymous ($w_i$, frac. treated nbrs) $\subset$ $H_3$ network $\subset$ $H_4$ generic.
  Test most→least restrictive; **closed testing ⇒ no multiplicity correction** for nested nulls.

## 2. Exposure effects (the estimands)
$$\bar\tau(h,h')=\frac1n\sum_{i=1}^n\big(Y_i(h')-Y_i(h)\big)\quad(h,h'\in\mathcal H).$$
E.g. direct effect = (treated) vs (pure control); spillover effect = (untreated-with-treated-neighbor) vs (pure control).

## 3. IPW / Horvitz–Thompson under interference → unbiased "for free"
Bernoulli design $W_i\sim\mathrm{Bern}(e_i)$; **exposure propensity** $e_i(h)=P(H_i(\mathbf W)=h)$. Then
$$\hat\tau_{IPW}(h,h')=\frac1n\sum_i\Big[\frac{\mathbb 1\{H_i(\mathbf W)=h'\}\,Y_i}{e_i(h')}-\frac{\mathbb 1\{H_i(\mathbf W)=h\}\,Y_i}{e_i(h)}\Big],\qquad E_W[\hat\tau_{IPW}]=\bar\tau(h,h').$$
Self-normalized (Hájek) version $\hat\tau_{SIPW}$ divides each arm by $\sum_i\Gamma_i$ — better finite-sample behavior. Weights $\Gamma_i(h)=\mathbb 1\{H_i(\mathbf W)=h\}/e_i(h)$.

## 4. Finite-population (randomization-only) inference — Neyman
No superpopulation; treat potential outcomes as fixed, randomness only from $\mathbf W$. The true variance
$\bar\sigma^2$ depends on *unobservable* potential-outcome differences and isn't identified — but a
**conservative, estimable bound** $\sigma^2\ge\bar\sigma^2$ exists, and it equals the usual IID variance estimate:
$$\bar\sigma^2=\frac1n\sum_i\Big[\tfrac{Y_i^2(1)}{e_i}+\tfrac{Y_i^2(0)}{1-e_i}-(Y_i(1)-Y_i(0))^2\Big]\ \le\ \sigma^2=\frac1n\sum_i\Big[\tfrac{Y_i^2(1)}{e_i}+\tfrac{Y_i^2(0)}{1-e_i}\Big].$$
**Takeaway:** the IID-sampling CI (ch.1) is *conservative* for the SATE under randomization alone.

## 5. CIs for exposure effects — the dependency graph + HAC/cluster-robust variance
Randomization **dependency graph** $G_{ij}=\mathbb 1\{(\{i\}\cup N_i)\cap(\{j\}\cup N_j)\neq\varnothing\}$
($G_{ij}=0\Rightarrow Y_i\perp_W Y_j$). HAC variance estimator (residualized, $\odot$ = elementwise):
$$\hat\sigma^2(h,h')=\tfrac1n\big(\Gamma(h')\odot\mathbf Y-\Gamma(h)\odot\mathbf Y\big)^\top G\big(\Gamma(h')\odot\mathbf Y-\Gamma(h)\odot\mathbf Y\big).$$
CLT for $\hat\tau_{SIPW}$ holds if max degree $\deg(G_n)=o(n^{1/4})$ (no single unit influences too many).
**Key for Vega:** when $G$ is **block-diagonal (clustered)**, $\hat\sigma^2$ is exactly the **cluster-robust
variance estimator** — so cluster-robust SEs are the finite-population-correct thing, not just an IID heuristic.
Conservativeness needs $G\succeq0$ (true for block/cluster $G$) **or** the non-neighbor-uncorrelated condition (12.29).

## 6. Direct / indirect effects (exposure-mapping-free alternative) → the marketplace case
$$\tau_{ADE}=\tfrac1n\sum_i E_W[Y_i(1,\mathbf W_{-i})-Y_i(0,\mathbf W_{-i})],\quad
\tau_{AIE}=\tfrac1n\sum_i\sum_{j\neq i}E_W[Y_j(W_i{=}1,\mathbf W_{-i})-Y_j(W_i{=}0,\mathbf W_{-i})].$$
**Munro, Kuang & Wager (2025)** derive these under *marketplace equilibrium interference* (prices align
supply & demand) + CATE-like **spillover-aware targeting** — essentially the Vega setting. (→ acquire; INDEX §02.)

## 7. Permutation tests for interference (ch.11)
Sharp-null ($H_0$) Fisher test: scramble $\mathbf W$, impute $T(\mathbf Y(\mathbf w),\mathbf w)$, $p=\frac{1+\#\{T_0\le T_b'\}}{1+B}$.
Testing $H_1$ (SUTVA vs spillover): **focal units** $F$ — only permute assignments matching $\mathbf W$ on $F$;
test stat = regression of $Y_i$ on fraction-treated-neighbors over $\{i\in F, w_i=0\}$. Use **studentized**
statistics so the test also has the right behavior against the Neyman (weak) null.

## Vega hooks
- **`inference/cluster.py`:** §5 *is* the justification — cluster-randomize, aggregate, cluster-robust SEs = finite-population-valid. Use `statsmodels`/`pyfixest` (STACK.md), don't hand-roll.
- **The thesis / ramp diagnostic:** exposure mappings name *exactly* what the engine violates; the naive A/B assumes $H_1$ (SUTVA) while the DGP is $H_4$-ish → bias grows with treated share.
- **`switchback.py`:** time-exposure is another exposure mapping; same finite-population machinery.
- **Acquire:** Munro–Kuang–Wager 2025 (marketplace equilibrium), Aronow–Samii 2017, Leung 2022, Hu–Li–Wager 2022, Athey–Eckles–Imbens 2018 (testing). Cross-link [[ate-estimators]] (HT/IPW roots), [[iv-late]].
