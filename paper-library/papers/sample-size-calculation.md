---
sheet: sample-size-calculation
covers: [Spotify Confidence — Sample Size Calculation bootcamp I/II/III (SSC playgrounds)]
feeds: [NB 08 power & decisions, chassis DRAFT power-gate, notation/power-mde.md, lyra power module]
source: https://confidence.spotify.com/bootcamp/sample-size-calculation-i/ssc-playground-i
        https://confidence.spotify.com/bootcamp/sample-size-calculation-ii/ssc-playground-ii
        https://confidence.spotify.com/bootcamp/sample-size-calculation-iii/ssc-playground-iii
---

# Sample-size calculation — the Confidence SSC playground (3 progressive levels)

Spotify's **Confidence** platform teaches sample-sizing as a **progressive calculator** you fill in *when
creating an experiment* (the DRAFT gate). Each level adds real-world complications on top of the textbook
formula. Transcribed from the "Show detailed formulas" view (Daniel's screenshots) + the bootcamp lessons.
This is the spec for **NB 08 (power & decisions)** and the platform's **DRAFT power-gate**.

## Level 1 — the base two-sample formula
$$N \;=\; \frac{4\,(z_{1-\alpha} + z_{\text{power}})^2\,\sigma^2}{[\,\mu \cdot \text{relMDE}\,]^2}$$
- $N$ = **total** sample (both arms); balanced 50/50 ⇒ each arm $N/2$.
- $\mu$ metric mean · $\sigma^2$ metric variance · **relMDE** relative minimum detectable effect (or NIM,
  non-inferiority margin), so the **absolute** effect is $\Delta=\mu\cdot\text{relMDE}$.
- $z_{1-\alpha}$ (one-sided) and $z_{\text{power}}$ are normal quantiles. The **"4"** $=2\text{ arms}\times2$
  (the difference-in-means has variance $2\sigma^2/n_{\text{arm}}$ under balance).
- *Worked (screenshot):* $\mu{=}0.5,\ \text{relMDE}{=}1\%\Rightarrow\Delta{=}0.005,\ \sigma^2{=}0.5,\
  \alpha{=}0.1\Rightarrow z_{0.9}{=}1.282,\ \text{power}{=}0.59\Rightarrow z_{0.59}{=}0.228$. →
  $N=\frac{4(1.282+0.228)^2(0.5)}{(0.005)^2}\approx \mathbf{182{,}190}$ (91,095/arm).

**Parameter sensitivities (the L1 lesson — explore, don't just derive):** $N\propto 1/\Delta^2$ (halve the
MDE → **4×** the sample), $N\propto\sigma^2$ (linear), $N$ rises **steeply** with power (0.8→0.9 is a big jump
because $z$ moves fast in the tail), and $N\to$ small as $\sigma^2\to0$.

## Level 2 — experiment-design corrections (multiple testing + guardrails)
Same $N$ formula but with $\alpha\to\alpha_{adj}$ and $\text{power}\to\text{power}_{adj}$:

**Multiple-testing (Bonferroni) on $\alpha$:**
$$\alpha_{adj} \;=\; \frac{\alpha}{(\#\text{ comparisons})\times(\#\text{ success metrics})}$$
More variant comparisons or success metrics → split $\alpha$ → smaller per-test $\alpha$ → larger
$z_{1-\alpha_{adj}}$ → **larger $N$**. Controls family-wise Type-I across the metric battery.

**Family-wise power on guardrails with NIMs:**
$$\text{power}_{adj} \;=\; 1 - \frac{1-\text{power}}{(\#\text{ guardrails with NIMs}) + \min(\#\text{ success metrics},\,1)}$$
Each guardrail tested for non-inferiority (a NIM) consumes Type-II budget, so the **per-test power must rise**
to keep family-wise power → larger $z_{\text{power}_{adj}}$ → **larger $N$**. The $\min(\#\text{success},1)$
keeps ≥1 in the denominator (you always run the success test). **Guardrails *without* NIMs cost nothing**
(they're monitored, not powered for non-inferiority).
- *Worked (screenshot):* 1 comparison, 1 success, 0 guardrails-with-NIMs, $\alpha{=}0.1$, power${=}0.8$ →
  $\alpha_{adj}=0.1$ ($z{=}1.282$), $\text{power}_{adj}=1-\frac{0.2}{0+1}=0.8$ ($z{=}0.842$) →
  $N=\frac{4(1.282+0.842)^2(0.5)}{(0.005)^2}\approx \mathbf{360{,}630}$.

> **Non-linearity lesson (L2):** because $z(\cdot)$ is non-linear, *which metric type costs the most* depends
> on the $\alpha$/power settings — a comparison vs a success metric vs a guardrail-with-NIM trade differently.

## Level 3 — allocation + CUPED + binary metrics
$$N \;=\; \big(\underbrace{\tfrac{1}{q_c}+\tfrac{1}{q_t}}_{\text{allocation}}\big)\,
  \frac{(z_{1-\alpha_{adj}} + z_{\text{power}_{adj}})^2\,\sigma^2\,(1-\rho)}{[\,\mu\cdot\text{relMDE}\,]^2}$$
- **Allocation:** $q_c,q_t$ = control/treatment proportions ($q_c+q_t=1$). At **50/50**, $\tfrac{1}{q_c}+
  \tfrac{1}{q_t}=4$ ⇒ recovers Level 1's "4"; **balanced is optimal** (any imbalance *raises* $N$). Confidence
  writes this allocation factor via a ratio $\kappa$ (treatment:control); at $\kappa{=}1$ it is balanced.
  *(Their "Show detailed formulas" renders it as a $(1+\kappa)$-style factor; the load-bearing fact is it
  reduces to 4 at 50/50 and grows with imbalance — verify the exact constant against the live tool.)*
- **Variance reduction (CUPED), $\rho\in[0,0.5]$:** multiply by $(1-\rho)$ — a CUPED/regression-adjustment
  covariate with outcome-correlation $\rho_{corr}$ cuts variance by $1-\rho_{corr}^2$; here $\rho$ is that
  reduction fraction. *Fewer users for the same power.* (= our NB 03 CUPED, on the design side.)
- **Binary metric toggle:** sets $\sigma^2=\mu(1-\mu)$ automatically (Bernoulli variance), so you only enter $\mu$.
- *Worked (screenshot):* 50/50, $\rho{=}0$ → unchanged from L2, $N\approx 360{,}630$.

## The whole formula (all levels)
$$\boxed{\,N=\Big(\tfrac{1}{q_c}+\tfrac{1}{q_t}\Big)\frac{\big(z_{1-\alpha_{adj}}+z_{\text{power}_{adj}}\big)^2\,\sigma^2\,(1-\rho)}{(\mu\cdot\text{relMDE})^2}\,},\quad
\alpha_{adj}=\frac{\alpha}{C\cdot S},\quad
\text{power}_{adj}=1-\frac{1-\text{power}}{G_{\text{NIM}}+\min(S,1)}$$
($C$ comparisons, $S$ success metrics, $G_{\text{NIM}}$ guardrails-with-NIMs, $\sigma^2=\mu(1-\mu)$ if binary).

## Steal for Lyra
- **DRAFT power-gate** (LYRA §3, the senior touch): this calculator *is* the gate — at experiment creation,
  refuse/warn on an underpowered design. Confidence proves sample-sizing belongs **in the creation flow**.
- **NB 08 (power & decisions)** builds this as a function + an interactive lab (we already have a 7-tab
  power lab in `study/experiment-design.html`; this adds the design-corrections + allocation + CUPED layers).
  Pairs with **test-and-roll** (`notation/test-and-roll.md`) as the *decision-theoretic* alternative to NHST sizing.
- **Scorecard "time-to-power"** (LYRA §8): the same machinery, shown live during RUNNING — how long until the
  design reaches its MDE at current traffic.
- **Harness cross-check** (the Vega superpower): our Monte-Carlo harness *is* simulation-based power (power
  = "simulate under H1, count rejections"), so we can **certify this closed-form $N$** against simulated
  coverage/power for L0/L1 DGPs — and it's the *only* honest sizing for switchback/clustered (no closed form).
- **Guardrail accounting**: the $\alpha_{adj}$/$\text{power}_{adj}$ corrections encode the metric taxonomy
  (success vs guardrail-with-NIM vs guardrail-without) from the metrics layer — wire the metric `class`/NIM
  into the sizing automatically.

## Confirmed + expanded (Spotify papers & Confidence blogs, added 2026-06-07)
Four new sources **confirm** the formulas above and add the *theory* + the operational meta-principle.

**The meta-principle: the calculator is the *frontend of the analysis pipeline*** ("What Makes a Good
Sample Size Calculator", Schultzberg 2026). A sample size is only right if the calculator knows how the
experiment will be **analyzed** — most calculators are standalone widgets assuming a fixed-sample
two-sample $z$, so "you plan one experiment and run another." Every design choice (sequential method,
correction, variance reduction, clustering, triggering) silently changes $N$, and the errors **compound
multiplicatively**. → For Lyra: the **DRAFT power-gate must call the same typed-metric / sequential /
cluster / CUPED machinery as the scorecard** (one engine, not a detached widget).

- **Sequential testing changes $N$:** GST (O'Brien–Fleming) adds only a few % over fixed-sample;
  **always-valid CS needs 50%+ more** (n=500/grp: GST power 0.89–0.93 vs always-valid 0.71–0.76). The calc
  must know the method, # interim looks, and the α-spending function.
- **Multiple testing — the family is *success metrics only*** (confirms $\alpha_{adj}=\alpha/(C\cdot S)$).
  Formal result (Schultzberg–Ankargren–Frånberg 2024, **arXiv:2402.11609**): **guardrails with
  non-inferiority tests need *no* α-correction** — they only *veto* a ship, so a guardrail false-positive
  can't cause a bad ship. Median Spotify exp = 2 success + 4 guardrails → α/2, **not** α/6. And the
  **Type-II rate *must* be corrected** when the rule has non-inferiority/deterioration/quality tests
  (confirms $\text{power}_{adj}$). **Why Bonferroni** over Holm/Hommel/BH ("Are Optimal MTC Optimal for
  You?", arXiv:2604.09256): only Bonferroni's α/S plugs into a **closed-form** size (others need
  simulation — ordering-dependent / unknown null-share); gives **simultaneous CIs for every metric**; and
  **pairs with group-sequential** (each metric vs its own α-budget). Power gap is only ~4–5pp (success-only
  family), ≈0 when few metrics truly move; **Bonferroni+GST beats Hommel+always-valid by 15–18pp**. Target
  **FWER** (P(≥1 false ship)≤5%), not FDR, for ship decisions.
- **During-experiment power monitoring — Fixed-Power Designs** (Nordin–Schultzberg 2024, **arXiv:2405.03487**
  "Precision-based designs"): pre-experiment variance is too optimistic (treatment heterogeneity inflates the
  treated-group variance). **Power depends on the variance, not the effect estimate, so peeking at
  variance/power does *not* inflate FPR** — update the required $N$ from observed variance as data accrues
  (FWCID stops at a target CI width; FPD guarantees power without pre-specifying variances). → Lyra scorecard
  **"time-to-power"** + a self-updating $N$; flags underpowered runs *before* an inconclusive readout.
- **Population/variance refinements:** **trigger analysis** (filter to actually-exposed users) can slash $N$
  (10% exposed → size the triggered population); **percentile metrics** (p99) use a different variance
  formula; **cluster randomization** → effective $N$ from cluster count + ICC, not # users (→ NB 04/05).
- **The decision-rule framing (the DECIDED state, formalized; arXiv:2402.11609):** a *decision rule*
  exhaustively maps test results → ship/no-ship; MTC only bounds Type-I of an *implied* rule — unless your
  desired rule matches it, it's wrong. Metric roles: **success · guardrail (non-inferiority) · deterioration
  · quality**; design+analysis must align with the rule. → Lyra's DECIDED state records the explicit rule.

## Source
Spotify **Confidence** bootcamp, Sample Size Calculation [I](https://confidence.spotify.com/bootcamp/sample-size-calculation-i/ssc-playground-i) ·
[II](https://confidence.spotify.com/bootcamp/sample-size-calculation-ii/ssc-playground-ii) ·
[III](https://confidence.spotify.com/bootcamp/sample-size-calculation-iii/ssc-playground-iii) (interactive
SSC playgrounds; formulas visible via "Show detailed formulas"). Confidence is Spotify's open experimentation
platform — a direct reference for Lyra's chassis.
