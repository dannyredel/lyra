# LYRA — A Causal Experimentation Platform (the pivot)

> **Pitch:** An experimentation *platform* — assignment, logging, governed metrics, guardrails, and a
> deep causal-inference engine (switchback, interference-aware, CUPED++, always-valid, CATE→policy) —
> with a simulator where you can **watch every estimate hit a known ground truth**.
>
> **Lyra** = the platform / chassis. **Vega** = the DGP-and-simulation layer *inside* it (Vega is the
> brightest star in Lyra). Names are placeholders — rename freely.

This document **supersedes the framing of `PROPOSAL.md`**. The old proposal isn't thrown away: the
Almedia/Freecash marketplace becomes **Vega Level-3** (the agent-based DGP) and everything already
built slots into a Lyra layer (see §1). `PROPOSAL.md` is retained as the Vega-layer / L3 spec.

---

## 0. The strategic inversion (why this exists)

The gap between a strong causal DS and an *experimentation team* at a DoorDash / Almedia is **not the
statistics** — it's never having operated the chassis (assignment, logging, a metrics layer,
guardrails, a scorecard). A founding DS is hired to stand that chassis up. So the chassis is on-target
— but it's the *least differentiating* thing to build. The portfolio story is the **inversion**:

- **Chassis = thin but real** — assignment, event log, metrics, a minimal scorecard. Deliberately boring.
- **Inference engine = deep** — switchback, interference-aware estimation, CUPED++, always-valid,
  CATE→policy. The moat; no off-the-shelf tool (Statsig, GrowthBook, Eppo) does these well.
- **Simulator = the validation harness**, not a fake-data crutch — *because we set the true effect, we
  certify each estimator recovers it with correct coverage.* Real platforms can't do that internally.
  Ground truth is a **superpower**, not a missing-client weakness.

Throughline: *"I built an experimentation platform, and here are live experiments running on it — on a
marketplace simulator where you can **prove** the estimates are correct, and (later) on my own site."*

---

## 1. Where we are now (the pivot is mid-flight, not a restart)

We have already built a working spine + most of the inference engine + a starter scorecard. The pivot
**re-frames and connects** them; it does not discard them.

| Built today | Becomes (Lyra) | Status |
|---|---|---|
| `engine/` sim (config, agents, offers, choice, experiments, emit, market) | **Vega L3** agent-based DGP + append-only event log | ✅ |
| `engine/oracle.py` (all-treat vs all-control shadow runs) | `DGP.ground_truth()` + the **counterfactual-twin** trick (§5) | ✅ |
| `inference/{naive,cluster,budget_split,anytime_valid,cuped,incrementality}` | **Layer 5** estimators | ✅ built · need `Estimator` Protocol wrappers |
| `inference/base.py` (`Effect`, duckdb loader) | seed of `EstimatorResult` + the metric read-path | 🟡 |
| `metrics/` dbt (stg_events → marts; unit-aware SRM; effect+CI in SQL) | **Layer 4** metrics | ✅ built · need versioning + `type`-awareness |
| `tests/` (recovery, naive-bias, A/A, anytime-valid, CUPED, incrementality, cluster) | the **Monte-Carlo harness** | 🟡 ad-hoc → unify into one harness (§4) |
| `serving/export.py` + `frontend/` React dashboard (4 screens) | **Layer 7** scorecard | 🟡 → state-gated messaging + CI color-bar (§7) |
| `notebooks/` 01–04 (world, money-shot, estimators, switchback lab) | **Stage-1 `/research` Explore** (§10) | ✅ |
| `cli.py`, `config.yaml`, `EVENT_LOG.md` | orchestration; DGP config; the event contract (L3 instance) | ✅ |
| 15 decisions (D-01…D-15), 14 Python tests, dbt 23 tests | — | ✅ |

**Read:** we are effectively partway through **Phase 1**. The pivot's job is to add the *platform*
scaffolding (Protocols, harness, fidelity ladder, governed metrics, lifecycle, scorecard semantics)
and to **continue every new capability notebook-first** (§10).

---

## 2. Architecture — seven layers + Vega

Treat them **unequally**. Layers 1–4, 7 are thin; **Layer 5 is ~60% of the effort**; Layer 6 is cheap
credibility; Layer 8 (Vega) is the validation superpower.

| # | Layer | Weight | Have? |
|---|---|---|---|
| 1 | **Assignment / bucketing** — deterministic salted hashing, *source-agnostic* | small, once | 🟡 (engine hashes arms; not yet a standalone SDK fn) |
| 2 | **Experiment registry** — config + **state machine** + metric-version bindings | small | ⬜ |
| 3 | **Event ingestion** — one append-only log (exposures + metric events), same schema sim & live | small | ✅ (EVENT_LOG) |
| 4 | **Metrics layer** — versioned, type-aware definitions (governance) | medium | 🟡 (dbt, not yet governed) |
| 5 | **Stats / inference engine** — pluggable estimators behind one interface | **~60%** | ✅ core built; ⬜ Protocol + more methods |
| 6 | **Diagnostics / guardrails** — SRM, A/A, multiple testing, novelty/primacy | small, high-signal | 🟡 (SRM + A/A done) |
| 7 | **Scorecard UI** — React; state-gated messaging; CI color-bar | medium | 🟡 (dashboard built) |
| 8 | **Vega — DGP + simulation + validation harness** — emits events *and knows the truth* | the moat | ✅ L3; ⬜ L0–L2 |

The runtime glue: the **experiment lifecycle** (§7) is the state machine every experiment moves
through; three **governed registries** — Estimators (§3), Metrics (§6), DGPs (§5) — share one
discipline: *define once, version, validate, reuse.*

---

## 3. The two parallel interfaces (the core architectural decision)

Everything hangs off **two mirror-image contracts**. Estimators *guess*; DGPs *know*. The killer loop:

```
sim → assign → estimate → compare to truth → coverage / bias / power scorecard
```

```python
@dataclass
class EstimatorResult:
    point: float | np.ndarray      # scalar ATE, or per-unit/segment CATE vector
    ci: tuple | np.ndarray         # interval(s) — may be a confidence *sequence* (always-valid)
    se: float | np.ndarray | None
    diagnostics: dict              # SRM p, overlap, balance, assumption flags
    method_metadata: dict          # estimand, assumptions, design requirements, n used

class Estimator(Protocol):
    requires: set[str]             # {"pre_period", "switchback_design", "propensity", ...}
    estimand: str                  # "ATE" | "CATE" | "LATE" | "RMST_diff" | "GATE" | ...
    def estimate(self, exposures, metric_events, config) -> EstimatorResult: ...

class DGP(Protocol):
    def sample(self, n, assignment, seed) -> Events: ...   # observable events; hides Y(0),Y(1)
    def ground_truth(self) -> GroundTruth: ...             # {ATE, CATE(x), per_period_effect, ...}
    def counterfactual(self, seed) -> dict: ...            # parallel-worlds run for emergent DGPs
```

**Design the Estimator interface against the hardest two methods up front** (switchback + CATE), or you
refactor at Phase 3: `point` must allow `np.ndarray` (CATE), `ci` must allow a sequence (always-valid),
switchback's time-region design arrives via `config`. Our existing `inference.base.Effect` is the
scalar seed of `EstimatorResult`; wrapping the six built estimators in this Protocol is the first
hardening step. The symmetry between the two Protocols *is* the architecture — build the loop once and
every method added later earns a **"certified: yes/no"** badge for free.

---

## 4. The Monte-Carlo harness = the power engine (pull into Phase 1)

```
for seed in range(R):
    events = dgp.sample(n, assignment, seed)
    result = estimator.estimate(events, ...)
report: bias · RMSE · CI coverage (target 95%) · type-I (under null) · power (under alt)
```

**Power / MDE falls out of the same machinery** — power *is* "simulate under H1 N times, count
rejections." So sample-sizing is not a separate module; it's the harness under the alternative. This is
the **only honest way** to size switchback and clustered designs (closed-form formulas don't apply —
the switchback lab `notebooks/04` shows exactly this). It's also the **CI test for statistical
correctness** that gates promotion (§10), and what the DRAFT power-gate (§7) calls.

We already do this implicitly in `tests/test_recovery.py` etc. (assert coverage of a known ATE). The
pivot **generalizes those into one reusable `harness(estimator, dgp, R, n)`** returning the report —
turning scattered recovery tests into the platform's beating heart.

---

## 5. DGP fidelity ladder (we have L3; build L0→L2)

A DGP is a pluggable object implementing the Protocol. Build bottom-up; each rung unlocks methods.

| Level | Structure | Unlocks / validates | Have? |
|---|---|---|---|
| **0 — iid** | distributions + constant ATE | t-test, proportions, ratio/delta, CUPED | ⬜ |
| **1 — covariates → POs** | `X→(Y(0),Y(1))`, **CATE(X)** surface, **confounding knob** | meta-learners, forests, DML, AIPW, IPW — *and the OLS-vs-DR demo* | ⬜ |
| **2 — temporal** | autocorrelation, seasonality, **carryover** | switchback, always-valid, DiD | 🟡 (switchback sim in `nb04`, not yet a DGP object) |
| **3 — agent-based (Vega full)** | units interacting; interference *emerges* | cluster/two-sided/budget-split designs | ✅ (`engine/`) |

**Primary fidelity = semi-synthetic (data source B, §9):** real covariates `X`, *inject* a known
effect to generate `Y` (how ACIC benchmarks are built) — answers "but it's fake" because the covariates
aren't. **Counterfactual-twin trick (L3):** run the same seed all-treated vs all-control; the
difference *is* the true ATE even though no one typed it in — which is **exactly what `engine/oracle.py`
already does**. Generalizing it to the `DGP.counterfactual()` contract is the reconciliation.

---

## 6. Governed metrics + diagnostics (the Netflix lesson)

The metrics layer is **governance, not plumbing**: the same metric computed differently across
experiments (28- vs 30-day churn) silently breaks comparability. **A metric is a first-class,
versioned, centrally-defined object** — the metric analog of the estimator registry.

Spec fields: `name, version, owner, definition (raw events → numerator/denominator per unit),
type (mean|proportion|**ratio**|count|quantile), direction, class (primary|secondary|guardrail),
pre_period (for CUPED)`. Two payoffs: (1) **single source of truth** — an experiment binds a metric
*version*; redefining → `churn@v2` and the platform caveats cross-version comparisons; (2) **type drives
inference** — `type=ratio` → delta-method variance automatically (Deng 2018), wiring Layer 4 → Layer 5.
Metrics are computed **once** in the layer; estimators consume standardized num/denom and never
recompute. Metrics get **promoted** like estimators, but gated by **A/A (must show no effect) +
consistency**, not Monte-Carlo coverage.

We have the dbt skeleton (`mart_experiment_effects` already computes effect+CI in SQL; `mart_srm` is
unit-aware). The pivot adds `version`/`type`/`class` as non-optional fields and the type→variance route.

Diagnostics/guardrails (Layer 6): **SRM (χ²)** ✅, **A/A** ✅, multiple-testing (BH-FDR), novelty/primacy,
guardrail-metric regressions that **block ship even if the primary moves**.

---

## 7. Lifecycle state machine, assignment, scorecard semantics

**Lifecycle (a state machine, not "a button"):** `DRAFT → RUNNING → STOPPED → ANALYZED → DECIDED`.
- **DRAFT** binds metric *versions* and **runs the power analysis** (harness §4) — the platform
  *warns/refuses on an underpowered design* (the senior gate).
- **STOPPED** can be triggered by an **advisory** always-valid boundary (CS excludes 0 → *recommend*
  stop; human decides). Two Etsy rules: **min 7-day runtime** (absorb weekly cycles) and an
  **early-stop inflation flag** (mark magnitude-inflated → winner's-curse haircut).
- **DECIDED** records the **ship/no-ship decision** against a short checklist — recording the
  *decision*, not just the stats, is what makes it a platform.

**Source-agnostic assignment — the fork that matters: *who calls assignment?*** Both modes hit the
**same function** + **same log schema**: **Mode A (online/live SDK)** `get_variant(unit, exp)`→render→
`track()` (Phase 4); **Mode B (offline/batch over a stream)** — Vega/observational batch, the platform
assigns, the DGP reveals, the engine estimates (Phase 0–3). So a *simulated* and a *real* experiment are
**the same object** in the registry, one scorecard.

**Scorecard semantics (a guardrail against misinterpretation):** the headline is a **pure function of
statistical state** (collecting → not-powered grey · powered+CI-spans-0 → "no change" grey · CI-excl-0
→ signed effect green/red · early-stop → effect + "magnitude may be inflated"). The single
highest-ROI component is the **CI-as-colored-bar** (red if entirely <0, green if >0, grey if spans 0).
Our React dashboard already renders effect±CI + decision banners — extend it to the state-gated table.

---

## 8. The method registry (the engine menu, tiered)

The moat is breadth+depth of *certified* estimators. Already promoted ✅; the rest are the roadmap, each
**one module + one notebook** (§10, §11 of the idea). Abbreviated (full table in the idea doc):

- **Core randomized ATE (P1):** direct-diff ✅ · OLS/Lin · **AIPW** (the OLS-biases/AIPW-survives demo) ·
  Welch/two-prop/χ² · **delta-method ratio** · **cluster-robust** ✅ · bootstrap.
- **Variance reduction (P1):** **CUPED** ✅ · **CUPAC** (`nb04`, promote) · MLRATE · stratification.
- **Sequential/always-valid (P1):** group-sequential · **confidence sequences** ✅ · mSPRT · e-values.
- **Post-stopping (P2):** **winner's-curse haircut**.
- **Diagnostics (P1):** **SRM** ✅ · **A/A** ✅ · multiple-testing · novelty/primacy.
- **Interference/switchback (P3, the moat):** **switchback** (`nb04` explore; Bojinov optimal design) ·
  two-sided/multiple-randomization · graph-cluster + exposure mappings · **budget-split** ✅.
- **CATE/uplift→policy (P3):** S/T/X/R/DR/U-learners · causal forests/GRF · DML-for-CATE · BART/BCF ·
  **Qini/AUUC/RATE** · **policy learning**.
- **Observational/quasi-exp (P3.5, day-job adjacency):** DML · AIPW/TMLE · IPW · **modern DiD**
  (Callaway-Sant'Anna, Sun-Abraham) · synthetic control/SDiD · CausalImpact · RDD · **LATE/CACE/IV**.

---

## 9. Data strategy (A/B/C/D — different jobs, not competitors)

| Source | What | Job |
|---|---|---|
| **A — pure synthetic** | hand-specified DGP, exact truth | early levels (L0–L1) |
| **B — semi-synthetic** ⭐ | real `X`, injected known effect | **validation backbone** (truth + realism) |
| **C — benchmark replay** | LaLonde/NSW, IHDP, ACIC, **Criteo uplift**, Hillstrom | academic credibility, blog fuel |
| **D — real live observational** | Tankerkönig fuel, GBFS/GTFS, ENTSO-E, PyPI/GitHub | "runs in prod on real data" — *no ground truth* |

(The MVP's **Criteo Uplift validation leg** from `PROPOSAL.md` is source C.)

---

## 10. The operating model — **notebooks-first** promotion (this is how we work)

> **Daniel's stated preference, and the idea's §11, are the same discipline.** We build every new
> capability as a notebook *first*, then promote what earns its way in. Most DS portfolios are a
> notebook graveyard; a *visible promotion pipeline* is the rare senior signal.

**Stage 1 — Explore (`notebooks/` `/research`).** Hardcoded data, plots, messy, fast — exactly how
Daniel likes to work. `notebooks/01–04` already live here (the switchback lab is the model). *Most
things stay here forever, and that's correct.*

**Stage 2 — Harden (`inference/_candidate/`).** Trigger = *"if I have to reuse it."* Refactor the
notebook's core into a clean function, write the `estimate()` wrapper conforming to the `Estimator`
Protocol, then **point the Monte-Carlo harness at it (the gate)** — bad coverage on a DGP where we
*know* the truth → not ready.

**Stage 3 — Promote (registered estimator).** Register → appears in the scorecard → callable from a
live experiment. *Now it's "in production."*

The Protocol is the **stable contract across all three stages** — never rewrite, only wrap + validate.
Promotion checklist: implements Protocol ✓ · passes harness coverage ✓ · has a DGP that tests its
assumptions ✓ · registered ✓. (Metrics promote the same way, gated by A/A + consistency.)

**Retroactive read:** the six built estimators are "already promoted" (they have recovery tests = the
harness, just not yet unified); `notebooks/01–04` are the Explore stage. Going forward we run the loop
explicitly: **notebook → harden → promote**.

---

## 11. Phasing — from where we ARE

| Phase | Goal | What's left (have ✅) |
|---|---|---|
| **0 — spine** | runs end-to-end | ✅ assignment(arms)+log+sim. ⬜ standalone assignment fn + SDK stub; registry **state machine** |
| **1 — engine v1 + harness** | a real platform | ✅ Core estimators, CUPED, CS, SRM, A/A, dbt metrics. ⬜ **Estimator/DGP Protocols**, **unified harness**, **DGP L0/L1**, **AIPW + the misspecification "robustness grid"**, metric `version`/`type` |
| **2 — scorecard + temporal** | legible | ✅ React dashboard. ⬜ state-gated messaging + CI color-bar; **DGP L2 (carryover)**; winner's-curse haircut; advisory auto-stop |
| **3 — the moat** | differentiation | ⬜ switchback/two-sided (promote `nb04`); CATE pipeline + Qini/RATE + policy learning |
| **3.5 — day-job adjacency** | quasi-exp in prod | ⬜ DML, modern DiD, SDiD, CausalImpact, CACE; wire data source D |
| **4 — in production** | "deployed" is literal | ⬜ SDK Mode A on the portfolio site / a free tool |

**Scope discipline:** the risk is the scope sinkhole. Each estimator/metric = **one module + one
notebook**. Do **not** build enterprise periphery (RBAC, audit, integrations). Steal architecture from
GrowthBook; write our own core.

**Immediate next (Phase 1 spine of the new architecture):**
1. `lyra/protocols.py` — `Estimator`, `DGP`, `EstimatorResult` (design against switchback + CATE).
2. `lyra/harness.py` — `harness(estimator, dgp, R, n)` → bias/RMSE/coverage/type-I/power. Re-express
   the existing recovery tests through it.
3. **Vega L0 + L1 DGP objects** (iid; covariates→PO with a `CATE(X)` surface + confounding knob) —
   *led by a `/research` notebook* (`notebooks/05_dgp_ladder_and_harness`).
4. **AIPW estimator** + the **robustness grid** (OLS biases / AIPW survives) — the first new
   notebook→harden→promote loop, and a flagship demo.
5. Wrap the six built estimators in the `Estimator` Protocol; wrap `engine/` as the L3 `DGP`.

---

## 12. Tech stack & naming

- **Engine/platform:** Python (FastAPI when serving). **Store:** Postgres/Supabase or DuckDB/Parquet
  (current). **Stats:** numpy/scipy/statsmodels core; econml/causalml/doubleml for CATE/DML;
  linearmodels for IV/panel; R via rpy2 only where R-only (`did`, `synthdid`, `grf`).
- **Metrics:** versioned store (YAML/table compiled to SQL) — keep dbt; make `version`/`type`/`class`
  non-optional. **UI:** React + Vite (current), re-skin to the Ocean palette to match the Quarto
  portfolio. **Blog:** each method → a Quarto post.
- **Naming:** **Lyra** (platform) / **Vega** (DGP layer). The repo is currently named for Vega; if we
  adopt the nesting, the top-level becomes `lyra/` (platform) wrapping `vega/` (the current `engine/`).
  Rename freely — flagged as an open decision (D-16 to log once confirmed).

---

*See `PROPOSAL.md` for the Vega-L3 marketplace detail (the agent model, the two MVP experiments, the
event-log contract), and `ideas/lyra-experimentation-platform.md` for the full method-registry menu and
scorecard decision tables.*
