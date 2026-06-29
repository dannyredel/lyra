---
sheet: power-mde
covers: [Kohavi et al 2026 (Power Analysis is Essential); Gelman–Carlin 2014; Cohen; Simonsohn 2015]
feeds: [power/MDE calculator, EVENT_LOG SRM guardrail, the decision framework, the naive-bias thesis]
---

# Power, MDE & sample size — equations (Kohavi et al 2026 + power cluster)

## Why it matters (Kohavi et al 2026)
Online A/B effects are **tiny** — median lift ~0.1–0.3%, rarely >2–3% (Microsoft/Bing, Airbnb, repositories). So a
properly-powered test needs *millions* of users. A "significant" result from a small test is usually noise: the
paper's three ~2M-user replications crush a published *55%* CTR lift to **~0.2% (non-significant)**.

## 1. Sample size / power
Two-sample test, effect $\delta$ (the **MDE**, minimum detectable effect), within-group SD $\sigma$, level $\alpha$, power $1-\beta$:
$$n_{\text{per arm}}=\frac{(z_{1-\alpha/2}+z_{1-\beta})^2\,2\sigma^2}{\delta^2}\ \approx\ \frac{16\,\sigma^2}{\delta^2}\quad(\alpha{=}0.05,\ \text{power}{=}80\%;\ \text{Lehr's rule}).$$
Binary metric: $\sigma^2=p(1-p)$. **Power** $=P(\text{reject}\mid\text{true effect}=\delta)$ — increasing in $n$ and $\delta$.
The MDE↔duration↔variance↔power knobs trade off; **variance reduction (CUPED, [[dml]]) buys power** by shrinking $\sigma^2$.

## 2. Choosing the MDE
Not free — set it from a **prior on effect sizes**: A/B repositories (GoodUI, Evidoo), average company effects
(~0.3%), or expert elicitation. In online settings Cohen's $d\approx0.01$ (tiny) for a "large" 5%-relative win →
classical "small/medium/large" $d$ thresholds don't transfer. Pick the smallest effect worth detecting, trade vs duration.

> **Decision-theoretic alternative:** skip the MDE/significance frame entirely — **test-and-roll** ([[test-and-roll]])
> picks the test size that *maximizes profit* over a finite population ($n^*\propto\sqrt N\,s/\sigma$), or prior-free
> the *rule of thirds* ($m\approx N/3$). Tests come out far smaller than NHST. This is Vega's ramp + OEC.

## 3. SRM — Sample Ratio Mismatch (a trustworthiness guardrail)
Designed split $\rho$ (e.g. 50:50) vs realized counts $(n_T,n_C)$: test with $\chi^2$ / z. If the p-value is
minuscule, the experiment is **untrustworthy** — stop (BAC Study 1: 44:56, $z\approx46$, $p\approx10^{-460}$).
A standard platform guardrail; in Vega it's the emitter invariant **EVENT_LOG §6.6** (realized arm shares vs `allocation`).

## 4. Type S / Type M errors & the winner's curse (Gelman–Carlin 2014)
Underpowered + significant ⇒ the estimate is *exaggerated* and may have the *wrong sign*:
- **Type-M (magnitude)** = exaggeration ratio $E[\,|\hat\delta|\mid \text{significant}]/|\delta|$ — large when power is low.
- **Type-S (sign)** = $P(\text{wrong sign}\mid \text{significant})$.
At 3% power, BAC's expected exaggeration is **~28×**; at 2.55% power, **>200×**. This is the winner's curse:
significant findings from small tests systematically overstate effects (Button et al. 2013).

## 5. "Significant" ≠ "true" — false-positive risk
With base rate of real effects $\pi$ (median experiment success ~10%, Kohavi et al. 2022), level $\alpha$, power $1-\beta$:
$$\text{FPR}=P(H_0\mid\text{significant})=\frac{(1-\pi)\,\alpha}{(1-\pi)\,\alpha+\pi\,(1-\beta)}\approx 36\%\ \ (\pi{=}0.1,\alpha{=}0.05,\text{power}{=}0.8).$$
(≈22% only at $\pi\approx0.18$; the low base rate is exactly why a "significant" result is so often null.)
Motivates lower $\alpha$ (Benjamin et al. 2017: 0.005) / Bayesian decisions. Ratio-metric CIs need **Fieller's theorem**;
randomize-by-user, analyze-by-event needs the **Delta method** (Deng–Knoblich–Lu 2018) for correct variance (→ correct power).

## 6. Small telescopes (Simonsohn 2015)
Ask not "is the replication consistent with the original *result*?" but "was the original *design* informative?".
$d_{33}$ = the true effect that would have given the original study **33% power**; if the replication effect $\ll d_{33}$,
the original telescope was too small. Replication $n$ ≈ 2.5× original.

## Vega hooks
- **Power/MDE calculator** — trivial since we *set* $N$, but the deliverable is to *show* the MDE–duration–power
  surface and pick run length (PROPOSAL §7). Variance reduction via CUPED feeds it.
- **SRM guardrail** — `EVENT_LOG §6.6` + a dashboard health flag (also `tests/test_aa_null.py`).
- **Decision framework** — don't ship underpowered noise; report **Type-M exaggeration** and **false-positive risk**, not just p<0.05.
- **Thesis tie-in** — because Vega knows ground-truth $\tau$, "underpowered-significant overstates the effect" becomes
  a *measured, asserted* quantity, exactly like the naive-bias demonstration. Cross-link [[anytime-valid]], [[platform-experimentation]].
