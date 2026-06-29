---
sheet: platform-engineering
covers: [Netflix (Design Principles; Reimagining Analysis), Stitch Fix, DoorDash Curie, Squarespace,
         Etsy peeking, Microsoft Flywheel (Fabijan), OCE Summit 2019, Open Guide to A/B Testing,
         Larsen 2023 review, Ng-Imbens 2026, Spotify risk-aware, Nie 2022 (eBay SRM),
         Schultzberg-Ottens 2024, Evan Miller, Deng-Lu 2016, Convoy/Variance-Explained Bayesian]
feeds: [LYRA.md chassis (layers 1-7), Chassis MVP, lyra/metrics.py, lyra/se.py, scorecard, decisions]
---

# Platform Engineering Playbook — ideas to steal for the Lyra chassis

Harvested from ~20 industry + academic sources (2026-06-04 paper pass). Organized by **chassis
component** (LYRA §2 layers). Each item: the idea · the source · the Lyra wire. Read this before the
**Chassis MVP** interlude. The recurring superpower: because **Vega authors the DGP**, anything below
that "real platforms can't certify" (OEC sensitivity, SRM gate, guardrail logic, stopping rules) we
can **inject a known fault and assert the platform catches it** — recovery tests for the chassis itself.

---

## TL;DR — the 12 highest-leverage steals (ranked)

1. **Metrics-as-versioned-code → JSON-serializable → compiled to on-demand SQL over the event log**, so a
   metric-definition change needs **no backfill/migration** (Netflix Metrics Repo · DoorDash JinjaSQL ·
   Stitch Fix). *This is Lyra's governed metrics layer.*
2. **Decision-theoretic DECIDED state**: launch iff $R(a_1\mid x)<R(a_0\mid x)$ under a linear loss with a
   **trade-off vector $\Lambda$**; persist `{posterior, Λ, costs, risks, action}` (Ng–Imbens). *Replaces
   "p<0.05 → ship".*
3. **Scorecard = pure function of statistical state → a state label** (Etsy vocabulary), with the
   **CI-colored-bar** and the **winner's-curse caveat** on early stops. *The single highest-ROI UI piece.*
4. **SRM gate as a tolerance-band *sequential* test, not raw $\chi^2$** (eBay): lifts alert precision
   28%→95% at scale; auto-emit a 4-way diagnostic slice when it fires. *Raw $\chi^2$ false-positives at
   our simulated scale.*
5. **Estimator contract = 2-function override, notebook-first, promoted by PR/harness-gate** (Netflix
   Causal Models). *Exactly our `Estimator` Protocol + Monte-Carlo gate — already how we work.*
6. **One subject-abstracting assignment service**, settings-without-deploy, multi-strategy
   (Bernoulli/within-subject/bandit) (Stitch Fix #oneway · Squarespace Praetor · DoorDash). *Source-agnostic
   assignment = LYRA §3.*
7. **Exposure-event log drives an explicit lifecycle** with async + **on-demand recompute** and an indexed
   result store (DoorDash Curie). *Our append-only log → registry/state-machine → scorecard.*
8. **Verify→Validate funnel as the lifecycle**, with cheap **necessary** criteria that kill ideas before an
   A/B test; sequential tests for *abort* only, unbiased fixed-horizon for *ship* (Schultzberg–Ottens).
9. **Govern metrics by an explicit taxonomy** — data-quality / **OEC** / **guardrail** / diagnostic — and
   **validate the OEC against a labeled corpus + degradation experiments** (Larsen · OCE Summit). *Vega
   can certify this.*
10. **Guardrails = non-inferiority conjunction / inflated loss weight**: ship = (superiority on OEC) AND
    (every guardrail clears its non-inferiority margin) (Spotify risk-aware · Ng–Imbens).
11. **Proper-stopping invariant for advisory auto-stop** (Deng Thm 1): stop only on past/present data,
    aggregate to the randomization unit, no re-windowing / cherry-picking $t$; **min-runtime ≥ 1 week**;
    auto-stop fires only on a **pre-committed boundary**, never a raw $p<0.05$ dip.
12. **Frugal parameterization for the DGP zoo**: author DGPs whose **ATE/CATE is a primitive** (set, not
    derived), with confounding as a free dial (Evans–Didelez). *Principled upgrade to Vega's hand-built worlds.*

---

## 1 · Assignment / bucketing (LYRA §3)
- **One assignment service abstracting the *subject***: anonymous visitor vs logged-in user vs stylist vs
  cluster, behind one API (Squarespace **Praetor**, Stitch Fix). Multi-strategy: Bernoulli, within-subject,
  bandit (Stitch Fix). **Change test settings without a code deploy** (Squarespace). → our `get_variant()`
  must be source-agnostic + config-driven.
- **PSI bucket-uniformity gate** at assignment: $\text{PSI}=\sum_b(\hat p_b-\hat q_b)\ln(\hat p_b/\hat q_b)$,
  $\frac{1}{1/n+1/m}\text{PSI}\sim\chi^2_{B-1}$; eBay's $\text{PSI}_2$ hit **0% FPR / F≈100%**, beating χ²/KS/AD.

## 2 · Experiment registry + lifecycle state machine (LYRA §3)
- **Curie's explicit, exposure-driven lifecycle** (DoorDash): size (power/MDE) → configure metrics in UI →
  bucket on exposure → **log exposure events** → analyze (async queue + K8s) → results in indexed store →
  monitor → **ramp allocation** gradually. Async + **on-demand re-trigger** (fix a bad query, see results
  now, don't wait for cron). → our DRAFT→RUNNING→…→DECIDED, on the append-only log.
- **Entrance/Exit reviews** (Microsoft Flywheel): entrance captures hypothesis + **expected OEC impact** +
  target group; exit **auto-compares realized vs expected**. Doubles as institutional memory + training.
- **A/B-test-form as a required launch artifact** + a **searchable test log/registry** of everything ever
  run (Squarespace) — overlap detection, ownership, conflict avoidance.
- **Verify→Validate funnel with necessary/sufficient criteria** as lifecycle states (Schultzberg–Ottens):
  `DESIGN → VERIFY (cheap offline necessary checks) → VALIDATE (A/B) → DECIDED`, early-exit on any failed
  *necessary* criterion (only ~10–20% of ideas succeed → maximize early kill).
- **Layers / numberlines + a daily additivity check** for mutually-exclusive concurrent experiments (OCE
  Summit) — rare but catastrophic interactions.

## 3 · Governed metrics layer (LYRA §4) — *the Netflix lesson, operationalized*
- **Metrics-as-code, compiled to dynamic SQL on-demand** (Netflix Metrics Repo via PyPika; DoorDash
  JinjaSQL templates with bound params + an **exposures CTE that dedups** users in >1 bucket). Adding a
  metric = adding a SQL field/join; **no ETL backfill** when a definition changes. Each metric **serializes
  to JSON → API**. Owned/editable/auditable by DS teams, with a **Bring-Your-Own-Data** escape hatch
  (Stitch Fix). → versioned `MetricSpec` (we have it) compiled to dbt/SQL over the event log.
- **Metric taxonomy as a first-class tag**: `data-quality | OEC | guardrail | diagnostic` (Larsen, OCE
  Summit). Tier them; an owner per metric.
- **Certify the OEC** (the Vega superpower): validate an OEC against a **labeled corpus of past experiments**
  and **degradation experiments** (intentionally worsen the product, confirm the OEC catches it) (OCE
  Summit). We can *manufacture* both from ground truth.
- **Cross-experiment meta-analysis** to **tune metric definitions for sensitivity** / correlation with the
  North Star (Stitch Fix); **hierarchical cross-experiment prior** borrows strength (+38% efficiency,
  coverage preserved under A/A shuffles — Ng–Imbens).
- **CUPED extensions to support** (Deng 2013, beyond our basic $Y-\theta(X-\bar X)$): pooled $\theta$ across
  arms; **CUPED = ANCOVA**, reduction $1-R^2$ with multiple covariates; **ratio-metric CUPED via the delta
  method** (covariate grain ≠ metric grain); **missing-pre-period → presence-indicator** covariate;
  pre-trigger covariates for **triggered analysis**; the **validity guard** $\mathbb E[X^{(t)}]=\mathbb
  E[X^{(c)}]$ (a pre-period A/A on the covariate — the sign-flip pitfall, automate it). See [cuped notes].

## 4 · Inference engine (LYRA §5)
- **Compose primitives, never one function per experiment type** (Netflix Design Principles): a small
  grammar (DGP description, counterfactual sim, regression, bootstrap) composes into any analysis. Expose
  the pipeline as **steppable stages** (query→retrieve→preprocess→fit→estimate→post/MHT→serialize) for
  introspection. → our contracts + harness.
- **Estimator contract = override ~2 functions** in a model subclass; platform hides parallelization +
  compression; **promotion = a pull request**; same code in notebook and prod (Netflix). *We already do this
  (notebook→`lyra/`, harness gate).*
- **Metric-typed method selection** (DoorDash): Continuous→linear model, Proportional→…, **Ratio→delta
  method**, clustered→cluster-robust SE / cluster bootstrap, + CUPAC variance reduction. *We built the typed
  routing in NB 03.*
- **One opinionated default method** ends Frequentist-vs-Bayesian/p-value debates and makes elaborate tests
  self-service (Squarespace Horseradish). **Apache Arrow** for cross-language (py/R/C++) interchange; a
  **compression layer** (lossless or tunably-lossy) to run billion-row analyses single-machine (Netflix).

## 5 · Diagnostics / guardrails (LYRA §6)
- **SRM gate = tolerance-band *sequential* test, NOT raw $\chi^2$** (eBay Nie 2022): test $H_0:|p-p_0|\le
  \delta$, $\delta=\min(1\%,5\%\min(p_0,1-p_0))$, one-sided **SPRT** with Wald bounds $A=\log\frac{\beta}
  {1-\alpha}$, $B=\log\frac{1-\beta}{\alpha}$ → precision 28%→95%. Distinguish **assigned-traffic SRM**
  (randomizer) from **triggered-traffic SRM** (tracking). On fire, auto-slice by date / assigned-vs-triggered
  / cross-experiment / segment.
- **Mandatory A/A + SRM as trust pre-gates** that *block scorecard interpretation* (Larsen, Flywheel,
  open-guide). Plus suspicious-uplift, multiple-exposure, variation-id-mismatch, min-N-to-show (open-guide).
- **Traffic-light guardrail thresholds** ("chance of being worse" <65% green / 65–90% yellow / >90% red).
- **The named-laws as built-in checks** (open-guide): **Twyman** (verify surprising effects vs known DGP),
  **Goodhart** (test the OEC isn't gameable), **Simpson** (segment-aware). Each is a demonstrable Vega test.

## 6 · Scorecard / peeking UX (LYRA §7-8) — *Etsy is the template*
- **State → message vocabulary** (Etsy), as a pure unit-testable function of statistical state:
  headline ∈ `Waiting on data · Not enough data · No change · +X%`; detail ∈ `metric not powered · no
  detectable change · confident change · directional call OK, magnitude may be inflated`.
- **CI-colored-bar**: red if entirely <0, green if entirely >0, grey if spans 0 (= the always-valid decision,
  rendered). CI↔p duality: 90% CI excludes 0 ⟺ $p<0.1$.
- **Never surface a significance verdict on an underpowered / in-flight fixed-horizon test** — show the
  **MDE at current $n$** instead (Evan Miller): $\delta=(t_{\alpha/2}+t_\beta)\sigma\sqrt{2/n}$.
- **Advisory auto-stop fires only on a pre-committed boundary** (sequential $|T-C|\ge d^*\approx2.25\sqrt N$,
  or posterior odds $\ge K$, or expected loss $<\varepsilon$) — never a raw $p<0.05$ dip. Enforce
  **min-runtime ≥ 1 full week**; **haircut/shrink** early-stopped effect magnitudes.
- **Proper-stopping invariant** (Deng–Lu Thm 1): valid continuous monitoring needs a stopping rule on
  past/present data only, all data aggregated to the randomization unit, no re-windowing, no "test-until-win".
  By the **LIL**, a fixed boundary is crossed infinitely often under $H_0$ → naive monitoring drives FPR→1;
  a valid boundary grows $\gtrsim\sqrt{\log\log n}$ (Bayesian/mSPRT $\sim\sqrt{\log n}$).
- **Honest per-method guarantee label**: frequentist sequential → "Type-I controlled"; **Bayesian → show
  FDR $=1/(K+1)$**, caveat "controls expected loss/FDR, *not* Type-I, *and only if the prior is calibrated*"
  — Bayesian optional stopping still inflates Type-I (Variance-Explained: 2.5%→11.8%; Deng: 0.018→0.060).

## 7 · Decisions — the DECIDED state (LYRA §3)
- **Bayesian decision rule over multiple correlated metrics** (Ng–Imbens): launch iff $R(a_1\mid x)<R(a_0\mid
  x)$, $R(a\mid x)=\int \ell(a,w)P(w\mid x)\,dw$; linear loss $\ell(a_1,w)=-\sum_j\lambda_j w_j+c_1$. Each
  $\lambda_j$ = relative value of a unit move in metric $j$; launch/rollback costs $c_0,c_1$. **Guardrail =
  a large $\lambda_j$** (a regression dominates the loss even if the primary moved). Sweep $\Lambda$ →
  **decision-space visualization** (where does the call flip?).
- **Or guardrails as explicit non-inferiority tests** with margin $\delta$; **ship = AND** over typed criteria
  (Spotify risk-aware). Distribute $\alpha$ across the metric battery.
- **Threshold-of-caring + switching cost $\delta$** (Convoy): ship if expected loss $<\varepsilon$ **and** lift
  $>\delta$ — drives "show effect vs keep collecting" (keep collecting until confident-positive *or*
  confident-small-gap). Priors *weaker* than history suggests.
- **Record the decision, not just the stats**: `{posterior, Λ, costs, expected risks, action, checklist}`.

## 8 · Simulation / DGP — Vega (LYRA §5/§8)
- **Frugal parameterization** (Evans–Didelez; Orduz PyMC): decompose the joint into 3 **variation-independent**
  pieces — (a) the past $p_{ZX}$ (confounder + propensity), (b) the **causal margin** $p^\star_{Y\mid X}$
  *where you write the ATE/CATE directly*, (c) a **copula / odds-ratio** carrying residual confounding. So you
  **author a DGP whose estimand is a primitive**, with confounding as a **free dial** independent of the
  effect, and **swap estimands** (ATE/ETT/ETC) by changing a weight kernel. Gaussian recipe: $Y\mid X{=}x,Z{=}z
  \sim N\big((\mu_0+\delta x)+\rho\sigma_c z,\ \sigma_c^2(1-\rho^2)\big)$ — ATE $=\delta$ **by construction**.
  R pkg `causl`. → the principled upgrade to the DGP zoo (full notes in [notation/frugal-parameterization.md]).

---

## What to bake into the Chassis MVP (after NB 04)

Steal these first (thin but real): **(assignment)** one source-agnostic `get_variant` + PSI check ·
**(registry)** the state machine + an exposure-event log + the test-form/registry record · **(metrics)**
`MetricSpec` compiled to SQL over the log, typed + taxonomy-tagged · **(diagnostics)** the **sequential SRM
gate** + mandatory A/A · **(scorecard)** Etsy's state→message function + CI-colored-bar + MDE-when-underpowered
· **(decisions)** record `{Λ, costs, posterior, action}` with guardrails-as-non-inferiority. Defer to later
notebooks: advisory auto-stop (NB 07), the decision-theoretic prior (NB 08), CATE→policy (NB 09-10).

## Source catalog (one-liners)
- **Netflix — Design Principles**: primitives+composition, graduation pipeline, introspectable stages, Arrow.
- **Netflix — Reimagining Analysis**: Metrics Repo (code→JSON→on-demand SQL), 2-fn estimator, Plotly-JSON viz.
- **Stitch Fix**: #oneway centralization, one assignment service, owned/auditable metric defs + BYOD, meta-analysis.
- **DoorDash Curie**: exposure-event lifecycle, JinjaSQL templates + dedup CTE, async + on-demand recompute, typed stats, built-in SRM.
- **Squarespace**: Praetor subject-abstraction + settings-without-deploy, opinionated Horseradish lib, A/B-form gate + log.
- **Etsy**: the scorecard state→message vocabulary, CI color bar, early-stop haircut + 7-day min.
- **Microsoft Flywheel (Fabijan)**: the value↔investment flywheel, Entrance/Exit reviews, measure-the-program metrics, maturity Crawl→Fly.
- **OCE Summit 2019**: OEC design + validation (labeled corpus / degradation), metric taxonomy, interference as frontier, layers+additivity, embedded-expert programs.
- **Open Guide to A/B**: trust-pitfalls catalog, named laws (Twyman/Goodhart/Simpson), win-rate-is-a-trap, traffic-light guardrails.
- **Larsen 2023**: metric taxonomy, A/A+SRM as trust prerequisites, sequential lineage (SPRT→mSPRT→always-valid p), triggered/diluted effects.
- **Ng–Imbens 2026**: decision-theoretic launch rule + trade-off vector, guardrail=inflated λ, hierarchical cross-experiment prior (+38%).
- **Spotify risk-aware (Schultzberg–Ankargren–Frånberg 2024, arXiv:2402.11609)**: the **decision-rule** framework — exhaustively map test results → ship; metric roles success/guardrail-NIM/deterioration/quality; **guardrails-with-NIMs need no α-correction** (they only veto), but **Type-II must be corrected** for them; design+analysis must align with the rule.
- **Spotify multiple-testing (arXiv:2604.09256)**: **why Bonferroni** — closed-form sample-size (α/S), simultaneous CIs for every metric, pairs with group-sequential; correct only **success metrics** (α/2 not α/6); power gap over Holm/Hommel ~4–5pp; **Bonferroni+GST beats Hommel+always-valid by 15–18pp**; FWER vs FDR for ship decisions.
- **Spotify "good sample size calculator" (Schultzberg 2026)**: the calculator is the **frontend of the analysis pipeline** — sequential/MTC/variance-reduction/clustering/triggering all change $N$ and compound; **Fixed-Power Designs** monitor power *during* the run (peeking at variance is safe). → `papers/sample-size-calculation.md`.
- **Nie 2022 (eBay)**: PSI randomization gate, **sequential SRM** (precision 28%→95%), 4-way SRM diagnostic, assigned-vs-triggered.
- **Schultzberg–Ottens 2024**: verify→validate funnel, necessary vs sufficient, sequential for abort only.
- **Evan Miller ×2**: peeking inflation (26%!), $n=16\sigma^2/\delta^2$, gambler's-ruin sequential boundary $d^*\approx2.25\sqrt N$.
- **Deng–Lu 2016**: optional-stopping validity theorem, FDR vs Type-I, LIL, proper-stopping invariant.
- **Variance-Explained / Convoy**: Bayesian peeking still inflates Type-I; expected-loss stop + switching cost δ; prior-calibration caveat.
