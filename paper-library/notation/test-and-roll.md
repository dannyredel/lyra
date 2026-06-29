---
sheet: test-and-roll
covers: [Feit & Berman 2019 (Test & Roll), Kawato & Sakaguchi 2026 (Prior-Free Sample Size for Test-and-Roll)]
feeds: [the ramp logic, the decision framework, OEC / power calculator]
---

# Test & Roll — profit-maximizing sample size — equations

A **decision-theoretic** alternative to classical power analysis ([[power-mde]]): don't test for *significance* —
choose the test size that **maximizes profit over a finite population**, then **roll the winner** to everyone else.
This is literally Vega's ramp + OEC.

## Setting (Feit & Berman 2019)
Finite population $N$. **Test** stage: $n_1+n_2$ units randomized across two treatments (some get the worse arm —
*opportunity cost*). **Roll** stage: deploy one treatment to the remaining $N-n_1-n_2$ based on the test
(*deployment-error cost*). Maximize total expected profit $E[\Pi_T]+E[\Pi_D]$.

**Model:** response $Y_j\sim N(m_j,s^2)$ with priors $m_j\sim N(\mu,\sigma^2)$; $s$ = response-noise SD (known/estimated),
$\sigma$ = prior SD of the mean response. Implied prior on the effect $m_1-m_2\sim N(0,2\sigma^2)$.
**Decision rule** = **pick the winner**: with symmetric priors and $n_1=n_2$, $\delta(y_1,y_2)=\mathbb 1\{y_1>y_2\}$ — *no significance threshold*.

## Profit-maximizing test size
$$n^*_1=n^*_2=\sqrt{\frac{N}{4}\Big(\frac{s}{\sigma}\Big)^2+\frac34\Big(\frac{s}{\sigma}\Big)^4}-\frac34\Big(\frac{s}{\sigma}\Big)^2\ \le\ \frac{\sqrt N\,s}{2\sigma}.$$
Properties (all contrasting NHST):
- **Scales with $\sqrt N$** (and is always $<N$). NHST $n_{HT}=(z_{1-\alpha/2}+z_\beta)^2\,2s^2/d^2$ ignores $N$.
- **Sub-linear in noise** — grows with the SD $s$, not the variance $s^2$ ⇒ much *smaller* tests for noisy responses
  (where NHST often demands $n_{HT}>N$, Lewis–Rao).
- **Decreases with $\sigma$** — more prior uncertainty / bigger expected gap ⇒ smaller test needed.
- **Near-bandit**: achieves regret $O(\sqrt N)$, close to a multi-armed bandit, but with only two allocation decisions
  (a constrained bandit) and a closed form.
- **Asymmetric priors** ⇒ unequal arm sizes / small holdouts arise naturally (rationalizes the "tiny holdout" practice).

## Prior-free version (Kawato & Sakaguchi 2026)
Test & Roll needs a prior $(\mu,\sigma)$. Kawato–Sakaguchi remove it via **welfare-aware minimax regret**, but show
that *absolute* minimax regret over-penalizes exploration → implausibly tiny experiments. Their fix — the
**Worst-case Marginal Benefit (WMB)** rule: add experimental units while the worst-case marginal benefit of one more
matched pair exceeds its marginal exploration cost. Result — a **rule of thirds**:
$$m^*\approx \tfrac{N}{3}\quad(\text{test }\sim\tfrac13,\ \text{roll }\sim\tfrac23),$$
for Bernoulli outcomes (Gaussian approx, excl. pathological cases) and *exactly* for Gaussian known-variance. Prior-free, plug-and-play.

## Vega hooks
- **The ramp IS test-and-roll.** A/A → 1% → 5% → 20% → 50% → ship = "test on a subset, roll the winner." Feit–Berman /
  the rule-of-thirds give a *principled* allocation vs an ad-hoc `ramp_schedule` — and we can compare them in the sim.
- **OEC = profit.** Vega's primary metric (margin per active user) *is* the objective; reward-sizing = "test the richer
  reward on $n$, roll the better reward to the rest." Reward design is a test-and-roll decision.
- **Finite population.** Vega's $N$ (50k–100k agents) is known ⇒ the $\sqrt N$ scaling / finite-$N$ framing apply
  directly (unlike NHST, which ignores $N$).
- **Decision framework.** "Pick the winner / maximize profit" is a cleaner ship rule than $p<0.05$ — and Vega can
  *measure* the profit gap between test-and-roll sizing and NHST sizing against ground truth.
- Cross-link [[power-mde]] (the NHST alternative it replaces), [[adaptive-experiments]] (bandit), [[platform-experimentation]].
