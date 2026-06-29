# Lyra — A Causal Experimentation Platform

> **One-sentence pitch:** An experimentation platform — assignment, logging, governed metrics, guardrails, and a causal inference engine with switchback and always-valid testing — running live experiments, including a simulator where you can watch the estimates hit a known ground truth.

*(Naming note: **Lyra** = the platform / chassis. **Vega** = the DGP-and-simulation layer that lives inside it. Vega is the brightest star in the constellation Lyra, so the engine sits inside the platform by name as well as architecture. Placeholder — rename freely.)*

---

## 0. Strategic frame (why this exists)

The gap between a strong causal DS and an experimentation team at a DoorDash / Almedia is **not** the statistics. It's never having *operated the chassis*: assignment, logging, a metrics layer, guardrails, a scorecard. A founding DS is hired to stand that chassis up. So the chassis is the on-target artifact — but it's also the *least differentiating* thing to build (anyone can clone a scorecard).

**The inversion that is the whole portfolio story:**

- The **chassis is thin but real** — assignment, event log, metrics, a minimal scorecard. Deliberately boring.
- The **inference engine is deep** — switchback, interference-aware estimation, CUPED++, always-valid inference, CATE→policy. This is the moat; no off-the-shelf tool (Statsig, GrowthBook, Eppo) does these well.
- The **simulator is the validation harness, not a fake-data crutch** — because you set the true effect, you can *certify* that each estimator recovers it with correct coverage. Real data can never give you that. Missing clients isn't a weakness being patched; ground truth is a superpower the real platforms mostly lack internally.

**The throughline for the portfolio site:** *"I built an experimentation platform and here are live experiments running on it — on my own site, on a free tool, and on a marketplace simulator where you can prove the estimates are correct."*

---

## 1. Architecture — seven layers

Treat them **very unequally**. Layers 1–4 and 7 are boring and minimal; Layer 5 is the show; Layer 6 is cheap credibility. Two things bind them together at runtime: the **experiment lifecycle** (§3) is the state machine every experiment moves through, and three **governed registries** — estimators (§2), metrics (§4), and DGPs (§2/§5) — share one discipline: *define once, version, validate, reuse*.

| # | Layer | Build weight | Notes |
|---|-------|--------------|-------|
| 1 | **Assignment / bucketing** | small, build once | deterministic hashing, salted per experiment; *source-agnostic* (§3) |
| 2 | **Experiment registry** | small | config store: variants, allocations, targeting, **state machine**, metric-version bindings |
| 3 | **Event ingestion** | small | one append-only log: exposures + metric events; same schema for sim and live |
| 4 | **Metrics layer** | medium, **governed** | versioned, type-aware metric definitions; a metric is promoted like an estimator (§4) |
| 5 | **Stats / inference engine** | **~60% of effort** | pluggable estimators behind one interface |
| 6 | **Diagnostics / guardrails** | small, high signal | SRM, A/A, multiple testing, novelty/primacy, guardrail-metric regressions |
| 7 | **Scorecard UI** | medium | React, Ocean palette (#122140 / #1e6091), Fraunces + Commissioner — visibly *yours* |

Plus the thing that makes it more than a notebook:

| # | Layer | Notes |
|---|-------|-------|
| 8 | **Vega — DGP + simulation + validation harness** | mirrors Layer 5; emits events *and knows the truth*; Monte Carlo certification + power/MDE |

### Assignment detail (Layer 1)
Deterministic, stateless, reproducible:
```
bucket = hash(experiment_salt + unit_id) % 10000
variant = first allocation bucket containing `bucket`
```
Salted **per experiment** so the same unit isn't correlated across experiments (the classic carryover bug).

---

## 2. The two parallel interfaces (the core architectural decision)

Everything hangs off **two mirror-image contracts**. Estimators *guess*; DGPs *know*. The platform's killer loop closes them:

```
sim → assign → estimate → compare to truth → coverage / bias / power scorecard
```

### 2a. Estimator interface

Design it against the **hardest two methods up front** (switchback + CATE), not the t-test — or you refactor everything at Phase 3.

```python
@dataclass
class EstimatorResult:
    point: float | np.ndarray        # scalar ATE, or per-unit/per-segment CATE vector
    ci: tuple | np.ndarray           # interval(s); may be a confidence *sequence* for always-valid
    se: float | np.ndarray | None
    diagnostics: dict                # SRM p, overlap, balance, assumption flags
    method_metadata: dict            # estimand, assumptions, design requirements, n used

class Estimator(Protocol):
    requires: set[str]   # e.g. {"pre_period", "switchback_design", "propensity"}
    estimand: str        # "ATE" | "CATE" | "LATE" | "RMST_diff" | "GATE" | ...
    def estimate(self, exposures, metric_events, config) -> EstimatorResult: ...
```

Stress points that shape the interface:
- **Switchback** needs the time-region design passed in via `config`.
- **CATE** returns a *function / per-unit vector*, not a scalar — `point` must allow `np.ndarray`.
- **Always-valid** methods return a *confidence sequence*, not a fixed-n CI — `ci` must allow a sequence.

### 2b. DGP interface (Vega)

```python
class DGP(Protocol):
    def sample(self, n, assignment, seed) -> Events: ...   # observable events; hides Y(0), Y(1), confounders
    def ground_truth(self) -> GroundTruth: ...             # {ATE, CATE(x), per_period_effect, ...}
    def counterfactual(self, seed) -> dict: ...            # parallel-worlds run for emergent DGPs (see §5)
```

Symmetry between 2a and 2b *is* the architecture. Build the loop once and every method added later gets a "certified: yes/no" badge for free. (The metric registry, §4, is the third parallel contract.)

---

## 3. Experiment lifecycle (it's a state machine, not "a button")

The "create experiment" flow is correct — but the strong framing is a **lifecycle state machine**, because that's what turns a form-that-starts-a-process into a platform.

```
DRAFT → RUNNING → STOPPED → ANALYZED → DECIDED
```

- **DRAFT** — define variants, allocations, targeting, **bind metrics to specific metric versions** (§4), *and run the power analysis* (MDE detectable at expected traffic — uses the harness, §7). The platform **warns/refuses on an underpowered design**. That gate is a senior touch.
- **RUNNING** — assignment is live (deterministic hashing), exposures + metric events flow into the append-only log; registry flips status.
- **STOPPED** — manual, scheduled, or an **advisory** always-valid trigger. *Auto-stop is advisory:* when the confidence sequence excludes zero the platform **recommends** stopping; the human decides. (Honest about human-in-the-loop and easier to defend in an interview than auto-kill.)
- **ANALYZED → DECIDED** — scorecard renders lift / CI / diagnostics; you record the **ship / no-ship decision**. Recording the *decision*, not just the stats, is what makes it a platform and not a calculator. The DECIDED view surfaces a short **decision checklist** (results support the hypothesis? blocking other experiments? anything broken in the product even if metrics look fine?) — an Etsy practice — so the call is recorded against explicit criteria, not vibes.

**Two lifecycle rules worth encoding (both from Etsy):**
- **Minimum runtime guardrail** — run for at least **7 days regardless of significance**, to absorb weekday/weekend cycles. A *duration* rule, independent of the statistical stopping rule.
- **Early-stop inflation flag** — when an experiment is stopped on the advisory always-valid boundary *before* reaching planned power, mark the readout as **magnitude-inflated**: surface the winner's-curse caveat in the scorecard (§8) and apply the effect-size shrinkage / "haircut" (§9). Stopping early biases the magnitude upward even when the *direction* is right.

### Source-agnostic assignment — the fork that matters: *who calls assignment?*

Both modes ship; they hit the **same assignment function** and write the **same event-log schema**.

- **Mode A — Online / live.** A real app calls the SDK in real time: `get_variant(unit_id, "exp_42")` → render → `track()`. Powers experiments on the real portfolio site / free tool / offerwall clone. The genuine "in production" proof. **Phase 4.**
- **Mode B — Offline / batch over a stream.** Vega (or a real observational pull) produces a batch; the platform assigns; the DGP reveals outcomes; the engine estimates. Powers every simulation experiment + all validation. **Phase 0–3.**

**Why this matters:** because both modes share the assignment + log contract, a *simulated* experiment and a *real* experiment are **the same object** in the registry, analyzed by the **same scorecard**. The simulator isn't a separate toy — it's the same platform pointed at a different event source. You can show a recruiter a sim experiment and a live-site experiment side by side, identical machinery.

---

## 4. Metrics layer & metric governance (the Netflix lesson)

The metrics layer is **not plumbing, it's governance**. The failure mode mature orgs hit (Netflix, Airbnb's Metrics Repo, Uber): the same metric — "churn" — gets computed differently across experiments (28- vs 30-day window, voluntary vs involuntary, denominator = all users vs active), so tests *look* comparable but aren't. The result is no apple-to-apple comparison and eroded trust.

**Core principle: a metric is a first-class, versioned, centrally-defined object — the metric analog of the estimator registry.** Define once, version, reuse.

**Metric spec fields:**
- `name`, `version`, `owner`
- `definition` — SQL / structured spec mapping raw events → **numerator / denominator per unit**
- `type` — mean / proportion / **ratio** / count / quantile → **drives estimator + variance selection**
- `direction` — higher- or lower-is-better
- `class` — **primary** (decision) / **secondary** / **guardrail**
- optional `pre_period` definition for CUPED

**Two payoffs:**

1. **Single source of truth / apple-to-apple.** An experiment binds to a metric *version*, not an ad-hoc query. Same version across experiments = genuinely comparable. Redefining a metric creates a **new version** (`churn_rate@v2`); the platform can flag that experiment X used v1 and Y used v2 and **caveat the cross-version comparison** rather than silently mixing them.
2. **Type drives correct inference.** The metric declares `type=ratio` → the engine automatically routes to the **delta-method variance**; `proportion` → two-proportion z; etc. So **metric governance and statistical correctness are coupled** — defining the metric right is *what makes the variance right*. This is the concrete wire from Layer 4 → Layer 5.

**Architectural enforcement:** metrics are computed **once, in the metrics layer**; estimators consume the standardized numerator/denominator per unit and **never recompute from raw events**. That single-source-of-truth rule is what makes apple-to-apple structural rather than aspirational.

**Metric taxonomy** (a property stored in the registry):
- **Primary / decision** — what you're trying to move; powered for.
- **Secondary** — supporting / exploratory; multiple-testing corrected; not powered.
- **Guardrail** — must *not* degrade (latency, crashes, revenue, unsubscribes); a regression **blocks ship even if the primary moves**. Feeds the diagnostics layer (§6).

**Metrics get promoted too** (mirrors estimator promotion, §11): a metric definition earns trust through its own validation gate — run it through an **A/A test** (it should show *no* effect; a spurious effect under A/A means the definition is leaky/broken) plus a **consistency / backfill check**. Estimators are validated by the Monte Carlo harness against ground truth; metrics are validated by A/A + consistency.

**The unifying frame:** three parallel **governed registries** — Estimators, Metrics, DGPs — all under one discipline: *define once, version, validate, reuse.* Naming that symmetry is itself the senior signal.

---

## 5. DGP fidelity ladder

A hand-specified DGP is a pluggable object. Build the ladder bottom-up; each rung unlocks a class of methods.

| Level | Structure | Unlocks / validates |
|-------|-----------|---------------------|
| **0 — iid** | distributions + constant ATE | t-test, proportions, ratio/delta, CUPED |
| **1 — covariates → POs** | `X → (Y(0), Y(1))`, **CATE(X)** surface, **confounding knob** | all meta-learners, causal forests, DML, AIPW, IPW — *and the OLS-vs-DR demo* |
| **2 — temporal** | autocorrelation, seasonality, **carryover** (effect of `t` leaks to `t+1`) | switchback, sequential / always-valid, CausalImpact, DiD |
| **3 — agent-based (Vega full)** | units interacting in a marketplace; interference *emerges* | cluster randomization, two-sided designs |

**Primary fidelity = semi-synthetic (option B).** Real covariate distribution `X` (public dataset, or Tankerkönig station data), keep `X` real, **inject a known treatment effect** to generate `Y`. This is how the ACIC academic benchmarks are built: realistic covariates *and* known truth. It directly answers "but it's fake" — the covariates aren't. Pure synthetic (A) is fine for Levels 0–1 if B gets complicated.

**Counterfactual-twin trick (Level 3):** to keep ground truth in an *emergent* sim, run the same seed twice — once all-treated, once all-control. The difference in outcomes *is* the true ATE/CATE even though no one typed it in. (Good standalone blog post.)

---

## 6. The credibility move — misspecification stress-testing

The failure mode to design *against*: if the DGP exactly matches an estimator's assumptions, the estimator looks perfect and proves nothing — you graded the exam you wrote. The senior artifact is the opposite — deliberately **violate** assumptions and chart who degrades gracefully:

- Linear DGP → diff, OLS, AIPW all agree (sanity check).
- Nonlinear confounding → **OLS biases, AIPW survives** *(the core-ATE point, demonstrated)*.
- Hidden confounding → *everything* under unconfoundedness breaks (honest lesson; motivates IV / DiD).
- Interference → naive A/B provably wrong, switchback recovers truth.

**Deliverable: a "robustness grid"** — estimators × assumption-violations, colored by CI coverage. One of the most senior-looking things you can ship; it says *I know the limits of my tools*.

---

## 7. Validation / Monte Carlo harness (= the power engine)

Pull this **into Phase 1**, not later — it certifies every estimator you subsequently add, and it's the gate in the promotion workflow (§11).

```
for seed in range(R):
    events = dgp.sample(n, assignment, seed)
    result = estimator.estimate(events, ...)
report: bias, RMSE, CI coverage (target 95%), type-I (under null), power (under alt)
```

**Power / MDE falls out of the same machinery** — power *is* "simulate under the alternative N times, count rejections." So sample-size / MDE is not a separate module; it's the harness run under H1. This is the only honest way to size switchback and clustered designs (closed-form power formulas don't apply there). It's also what the DRAFT power gate (§3) calls.

**Recruiter-bait feature — the true-effect dial:** a slider that sets the true ATE, estimate + CI tracking it live as samples stream in. The slider is the trailer; the Monte Carlo harness behind it is the film. Keep both honest.

---

## 8. Scorecard UX principles (Layer 7)

*(Visual design still TBD — this fixes the **semantics** of what to show when, independent of styling. Drawn largely from Etsy's peeking write-up.)*

**Core principle: the scorecard is a guardrail against misinterpretation, not just a display.** Etsy found that always showing a raw "% Change" number invited peeking and false conclusions; the fix was to replace the number with a **state-aware message** until the statistics justify showing an effect. Lyra already computes power, the confidence sequence, and the always-valid boundary — so the headline is a *pure function of statistical state*. Cheap to build, and it makes the platform read as far more mature than a raw-numbers table.

**State → message decision table** (implement as a pure function so it's unit-testable):

| Statistical state | Headline cell | Detail header | CI bar |
|---|---|---|---|
| not enough data yet | "Collecting data" | "metric is not powered" | grey |
| powered, CI spans 0 | "No detectable change" | "no change detected" | grey |
| CI excludes 0 (planned power reached) | signed effect "+/− X%" | "change detected — confident" | green if +, red if − |
| stopped early (advisory), not yet powered | signed effect + ⚠ flag | "direction correct; magnitude may be inflated" | green/red + caveat |

**CI-as-colored-bar** — the key visual: a horizontal interval bar, **red if entirely negative, green if entirely positive, grey if it spans zero**. The grey-spans-zero rule is your CI / always-valid decision rendered visually; it's the single highest-ROI scorecard component. (Use semantic red/green for significance; keep the Ocean palette for chrome.)

**Surface "time-to-power" live during RUNNING**, not only at design time — you already have the number from the harness (§7); showing it helps coordinate experiments competing for the same surface.

**Honesty over flattery** — the early-stop caveat ("magnitude may be inflated") is *shown, not hidden*, and is backed by the haircut correction (§9). Surfacing the limitation is itself the senior signal.

*(You'll iterate on the actual visual/interaction design later; none of the above prescribes styling — only the state-to-message contract, which Claude Code can implement now and you can re-skin freely.)*

---

## 9. Method registry (the engine menu, tiered by phase)

Columns: **Phase** · **Method** · **Estimand** · **Key assumption** · **Data shape needed**

### Core randomized ATE — the spine (Phase 1)
| Phase | Method | Estimand | Assumption | Data shape |
|---|---|---|---|---|
| 1 | **Direct difference** ȳ₁−ȳ₀ | ATE | randomization only | exposures + metric |
| 1 | **OLS / Lin estimator** (treatment×covariate interactions) | ATE | linearity (Lin: none added) | + covariates |
| 1 | **Doubly-robust (AIPW)** | ATE | consistent if *either* model right | + covariates |
| 1 | Welch t / two-prop z / χ² / Mann-Whitney | ATE | — | exposures + metric |
| 1 | **Delta method for ratio metrics** | ratio ATE | random denominator | numerator + denom per unit |
| 1 | **Cluster-robust SEs** | ATE | unit ≠ analysis unit | cluster id |
| 1 | Bootstrap / block bootstrap | any | — | — |

*The three-way ATE comparison (direct / OLS / AIPW) is the spine **and** the headline misspecification demo — same code, two purposes.*

### Variance reduction (Phase 1)
| Phase | Method | Notes |
|---|---|---|
| 1 | **CUPED** | pre-period covariate |
| 1 | **CUPAC** | ML-predicted control variate (DoorDash's — on-target for Almedia) |
| 2 | MLRATE | ML regression-adjustment w/ valid inference; generalizes CUPAC |
| 1 | Stratification / post-stratification | |

### Sequential & always-valid (Phase 1 — defining feature of a *deployed* platform)
| Phase | Method | Notes |
|---|---|---|
| 1 | **Group-sequential** (O'Brien-Fleming / Pocock alpha-spending) | |
| 1 | **Confidence sequences** (Howard–Ramdas) | peek anytime, no error inflation; feeds advisory auto-stop (§3) |
| 2 | mSPRT | Optimizely's always-valid approach |
| 3 | e-values / testing-by-betting | frontier; standout blog post |

### Post-stopping correction (Phase 2)
| Phase | Method | Estimand | Notes |
|---|---|---|---|
| 2 | **Winner's-curse / early-stopping shrinkage ("haircut")** | de-biased effect | only for early-stopped readouts; corrects the upward magnitude bias from the advisory stop (§3); fully demonstrable against ground truth in the harness (§7) — natural blog post. Etsy applies a haircut + a "magnitude may be inflated" caveat; deeper treatment in their "Mitigating the winner's curse" follow-up. |

### Diagnostics / guardrails (Phase 1)
| Phase | Method | |
|---|---|---|
| 1 | **SRM** (χ²) | non-negotiable |
| 1 | A/A validation | also the metric-promotion gate (§4) |
| 1 | Multiple testing (Bonferroni / BH-FDR) | |
| 2 | Novelty / primacy detection | |

### Design-time / power (Phase 1 — falls out of harness §7)
| Phase | Method | |
|---|---|---|
| 1 | Power / MDE (analytic where valid) | |
| 1 | **Simulation-based power** | only honest option for switchback / clustered |

### The moat — interference / switchback (Phase 3)
| Phase | Method | Estimand | Notes |
|---|---|---|---|
| 3 | **Switchback** (time-region, carryover-robust, Bojinov–Simchi-Levi–Toth optimal design) | ATE under interference | marketplace flex |
| 3 | **Two-sided / multiple randomization** (Bajari et al.) | — | offers cannibalize → Almedia-relevant |
| 3 | **Graph cluster randomization + exposure mappings** (Ugander) | GATE | partial interference |

### The moat — CATE / uplift full pipeline (Phase 3)
| Phase | Method | Estimand | Notes |
|---|---|---|---|
| 3 | Meta-learners S / T / **X / R / DR / U** | CATE | full set |
| 3 | Causal forests / GRF | CATE | |
| 3 | DML-for-CATE (R-learner) | CATE | |
| 3 | Causal BART / BCF | CATE | honest Bayesian uncertainty |
| 3 | Uplift trees / Qini forests | uplift | marketing tradition |
| 3 | **Evaluation: Qini / AUUC / RATE / calibration** | — | *proving the ranking is real — don't skip* |
| 3 | **Policy learning / policy trees** (Athey–Wager) | optimal policy | "who do we actually treat" — closes the loop |

### Day-job adjacency — observational / quasi-experimental (Phase 3.5, near-free for you)
| Phase | Method | Estimand | Notes |
|---|---|---|---|
| 3.5 | **DML** (PLR + IRM) | ATE | DR under unconfoundedness |
| 3.5 | AIPW / TMLE *(pick one for v1)* | ATE | two DR traditions |
| 3.5 | IPW + overlap trimming; PS matching | ATE | expected even if dated |
| 3.5 | **Modern DiD**: Callaway–Sant'Anna, Sun–Abraham, dCDH, Borusyak | ATT | staggered-adoption fixes — authority signal |
| 3.5 | **Synthetic control / SDiD / matrix completion** | ATT | Abadie → Arkhangelsky → Athey |
| 3.5 | **CausalImpact / BSTS** | event effect | wires into Tankerkönig pipeline |
| 3.5 | RDD (sharp + fuzzy) / ITS | LATE / effect | |

### Noncompliance / IV (Phase 3.5 — underrated)
| Phase | Method | Estimand | Notes |
|---|---|---|---|
| 3.5 | 2SLS, **LATE / CACE**, ITT vs ToT | LATE | when users don't comply with assignment, ITT understates |

### Deferred / optional
| Method | Condition to include |
|---|---|
| Bandits (Thompson / UCB / LinUCB) + **post-adaptive inference** (Hadad et al.) | if you want adaptive allocation in scope; Vega can feed it |
| Survival: KM / Cox / causal survival forest / **RMST diff** | only with a real churn/retention outcome to point it at; else RMST-as-roadmap |
| Bayesian A/B (Beta-Binomial, P(B>A), expected loss) | nice-to-have |
| Surrogate index (Athey et al., long-term effects) | one frontier showpiece, higher effort |

---

## 10. Data strategy (A/B/C/D — each does a different job)

| Source | What it is | Job in the portfolio |
|---|---|---|
| **A — pure synthetic** | hand-specified DGP, exact truth | early levels (0–1), builds today |
| **B — semi-synthetic** ⭐ | real `X`, injected known effect | **validation backbone** — truth + realism, answers "it's fake" |
| **C — benchmark replay** | LaLonde/NSW, IHDP, ACIC, Criteo uplift, Hillstrom | academic credibility, blog fuel |
| **D — real live observational** | Tankerkönig fuel, GBFS/GTFS transit, ENTSO-E, PyPI/GitHub, Wikipedia/Trends | the "runs continuously in prod on real data" proof — *no ground truth*, so not validation |

They don't compete — they do different jobs. Naming which job each does is itself the senior framing.

---

## 11. Promotion workflow — notebook → engine

The workflow is itself a portfolio signal: a disciplined path from exploration to production is exactly the maturity a founding DS is hired for. Most DS portfolios are a notebook graveyard; a visible promotion pipeline is rare.

**Principle: not everything graduates, and the interface is the gate.** A method earns its way into the engine by implementing the `Estimator` Protocol *and* passing the harness. Metrics follow the same path through their own gate (§4).

**Stage 1 — Explore (`/research` notebook).** Exactly how you already work: hardcoded data, plots, messy, fast. The survival analysis lives here first — KM, Cox, causal survival forest; eyeball it; argue RMST vs hazard ratio. **Most things stay here forever, and that's correct** — a one-off DiD for a blog post never needs to be in the engine.

**Stage 2 — Harden (`/lyra/estimators/_candidate/`).** Trigger = your own rule, *"if I have to reuse it."* Refactor the notebook's core into a clean function, write the `estimate()` wrapper that conforms to the Protocol, then — **the gate** — point the **Monte Carlo harness** at it. Can't return a proper `EstimatorResult` → not ready. Bad coverage on a DGP where you *know* the truth → not ready. The harness is the **CI test for statistical correctness**. A method enters the engine because it *passed validation against known ground truth*, not because you trust it.

**Stage 3 — Promote (registered estimator).** Register in the method registry → it appears in the scorecard → it's callable from a live experiment. Now it's "in production."

**Worked example (survival):** notebook KM/Cox/RMST → pick RMST-diff as the estimand → wrap `RMSTDifferenceEstimator(Estimator)` with `estimand="RMST_diff"`, `requires={"event_time", "event_indicator"}` → run through the harness against a Level-2 DGP with a *known* survival difference → coverage checks out → register. The notebook stays in `/research` as the narrative; the engine gets the hardened module.

**Why this is cheap, not bureaucratic:** the Protocol is the **stable contract across all three stages**. You never rewrite, only wrap and validate.

**Promotion checklist:** implements Protocol ✓ · passes harness coverage ✓ · has a DGP that tests its assumptions ✓ · registered ✓.

**The point:** the harness is what lets you promote *safely*. Without ground-truth validation, "move to production" is just "I copied my notebook into another folder." With it, promotion *means* something — and that's the bit recruiters recognize. (Metrics promote the same way, gated by A/A + consistency instead of Monte Carlo coverage.)

---

## 12. Phasing roadmap

| Phase | Goal | Engine + platform | DGP / data | UI |
|---|---|---|---|---|
| **0 — spine** | it runs end-to-end | assignment (source-agnostic) + registry with **state machine** + event log + Python SDK (`get_variant()`, `track()`) | Vega Level 0–1 as load generator | none |
| **1 — engine v1 + harness** | a real platform | full Core ATE (diff/OLS/AIPW), CUPED+CUPAC, group-sequential + confidence sequences, SRM + multiple testing, **Monte Carlo harness = power/MDE**, **metric registry v1 (versioned, type-aware)** | Level 0–1, semi-synthetic injection (B) | minimal |
| **2 — scorecard + temporal** | legible to a recruiter | mSPRT, MLRATE, novelty/primacy, **winner's-curse haircut**; **DRAFT power gate + DECIDED decision-recording surfaced in UI**; advisory auto-stop | Level 2 temporal DGP (carryover) | **React scorecard** (Ocean palette) + **state-gated messaging, CI color-bar, live time-to-power** |
| **3 — the moat** | differentiation | switchback + two-sided; CATE full pipeline + Qini/RATE + policy learning; e-values | Level 3 agent-based Vega + counterfactual twin | + true-effect dial |
| **3.5 — day-job adjacency** | continuous quasi-exp in prod | DML, modern DiD, SDiD, CausalImpact, CACE | wire to **Tankerkönig (D)** | event-study view |
| **4 — in production** | "deployed" is literally true | SDK Mode A into portfolio site / free tool / offerwall clone | live data | live experiments widget |

**Scope discipline:** the real risk is the scope sinkhole — a one-person platform absorbs infinite effort. Each estimator (and each metric) is *one module + one blog post*. Do **not** build the enterprise periphery (RBAC, audit logs, integrations). Steal architecture ideas from GrowthBook (open source, Python stats engine); write your own core.

---

## 13. Tech stack (proposed)

- **Backend / engine:** Python (FastAPI). You have FastAPI + Supabase from BeeSignal — reuse it.
- **Store:** Postgres (Supabase). Event log = append-only table; no Kafka at this scale. DuckDB/Parquet for heavy offline Monte Carlo if needed.
- **Stats:** numpy/scipy/statsmodels core; `econml`, `causalml`, `doubleml` for CATE/DML; `linearmodels` for IV/panel; R via `rpy2` only where the package is R-only (e.g. `did`, `synthdid`, `grf`).
- **Metrics layer:** a **versioned metric store** — structured definitions (YAML or a small table) compiled to SQL, with `version` / `type` / `class` as first-class fields. Start thin (dbt-style views) but make *versioning and type* non-optional from day one, since type drives variance (§4).
- **UI:** React + Vite, Ocean palette (#122140 primary, #1e6091 accent), Fraunces + Commissioner — matches the Quarto portfolio so it reads as one body of work.
- **Blog integration:** each method → a Quarto post on dannyredel.github.io; the platform is the spine of the whole portfolio narrative.

---

## 14. First concrete steps for Claude Code (Phase 0)

1. Repo scaffold: `lyra/` (platform) + `vega/` (DGP) + `sdk/` + `ui/`.
2. Implement the **assignment function** + unit tests (determinism, salt independence, allocation correctness, SRM-clean split). Make it **source-agnostic** — same function for batch (Vega) and live (SDK).
3. Define the **three contracts**: `Estimator` and `DGP` Protocols (design against switchback + CATE shapes), plus a **metric spec** (`name`/`version`/`type`/`class`/`definition`).
4. Stand up the **experiment registry with the state machine** (`DRAFT→RUNNING→STOPPED→ANALYZED→DECIDED`) and the append-only event log.
5. Vega **Level 0–1 DGP**: covariates → potential outcomes with a `CATE(X)` surface + confounding knob + `ground_truth()`.
6. Seed **2 metrics** (one `mean`, one `ratio`) so the type→variance routing is exercised end-to-end.
7. **Three Core-ATE estimators** (direct diff, Lin/OLS, AIPW) implementing the interface.
8. **Monte Carlo harness**: run the three against the Level-1 DGP, report bias / RMSE / coverage / type-I / power → first robustness-grid cell.
9. Smoke-test the loop: sim → assign → estimate → compare to truth.

That gives a working spine + the first "OLS biases, AIPW survives" demo + the harness that powers everything after — all in Phase 0→1.
