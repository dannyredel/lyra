# DECISIONS.md — Vega decision log (ADR-lite)

Running log of decisions. The canonical "current state" summary lives in CLAUDE.md
"Decisions already made"; this file is the **history + rationale** behind those bullets.
When a decision changes, add a new entry (don't edit old ones) and update CLAUDE.md.

Format: `D-NN · date · status(ACCEPTED/SUPERSEDED/PROPOSED) · one-line decision` then Why / Implications.

---

### D-01 · 2026-06-02 · ACCEPTED · Replay the recorded event log, not live streaming
**Why:** anytime-valid inference lives in the time/data dimension (CI narrows as simulated days
accumulate), not in transport. A static replay always renders in an interview; a live host is a
liability. **Implications:** engine emits append-only parquet; frontend replays on a simulated
clock; streaming is a thin Phase-2 adapter. (PROPOSAL §9)

### D-02 · 2026-06-02 · ACCEPTED · MVP vertical = Almedia / Freecash (rewarded UA)
**Why:** reward-seekers are near utility-maximizers → a discrete-choice agent is defensible, which
kills the "your sim is fake" critique. Interference is economically clean (finite effort + finite
budgets). **Implications:** simulate the user side, experiment on the offer/reward side. Other
verticals are Phase 3+. (PROPOSAL §3)

### D-03 · 2026-06-02 · ACCEPTED · Two MVP experiments, one treatment per game
**Why:** isolated-by-design analysis while still sharing the global user pool (the leakage source).
Game A = reward sizing (budget cannibalization); Game B = offer-wall ranking (attention). Plus 2–3
A/A nulls + decoys. **Implications:** never stack treatments on one offer. (PROPOSAL §5)

### D-04 · 2026-06-02 · ACCEPTED · Incrementality (ghost-ads/PSA holdout) leg is in the MVP
**Why:** the target JD is attribution-heavy; "operationalising attribution models, MMPs" maps
directly. **Implications:** `variant=holdout`, impression fires, reward=0, no conversion credited;
lift = treatment vs holdout. (PROPOSAL §2, EVENT_LOG §5)

### D-05 · 2026-06-02 · ACCEPTED · Criteo Uplift real-data validation leg is in the MVP
**Why:** answers "real business context" — run the same estimator on real large-scale
incrementality data. **Implications:** `validation/criteo.py`. (PROPOSAL §2)

### D-06 · 2026-06-02 · ACCEPTED · Agent choice model = MNL / nested logit
**Why:** ground truth = the utility parameters we set; treatments are shifts to choice-model inputs,
so the engine knows `ground_truth_tau` exactly. **Implications:** `engine/choice.py`; `config.choice`
holds betas. Open: final MNL-vs-nested choice (parked). (PROPOSAL §4)

### D-07 · 2026-06-02 · ACCEPTED · Metrics layer is dbt/SQL over the event log, not pandas
**Why:** the dbt project is a deliverable ("here is a dbt project computing readouts"), designed for
BigQuery. **Implications:** `metrics/` dbt; DuckDB local target, BigQuery documented swap. (config `warehouse`)

### D-08 · 2026-06-02 · ACCEPTED · DuckDB local, BigQuery as documented swap
**Why:** runs on a laptop in seconds; BQ profile proves the cloud story without paying for it.
**Implications:** `warehouse.target: duckdb`; `profiles.yml` carries both. (config `warehouse`)

### D-09 · 2026-06-02 · ACCEPTED · Eval funnel is Phase 2, simulated judge only
**Why:** the causal point is offline-online calibration of a proxy against ground-truth tau, not the
judge itself. A simulated noisy/biased score is cheaper and makes the point cleaner. **Implications:**
do NOT build a real LLM judge; simulate the score in the engine for Game B. (CLAUDE.md, PROPOSAL §11)

### D-10 · 2026-06-02 · ACCEPTED · Flat top-level package layout (engine/, inference/, …)
**Why:** EVENT_LOG.md and the specs reference top-level paths (`engine/emit.py`,
`metrics/models/staging/`, `tests/test_recovery.py`) directly; matching them avoids friction.
**Implications:** no `src/vega/` nesting; `pyproject.toml` packages the top-level dirs.

### D-11 · 2026-06-03 · ACCEPTED · `refill: daily` is the default budget model (was `none`)
**Why:** at 60k-user scale, `refill: none` (permanent exhaustion, the original config default and
PROPOSAL §4 framing) is fragile: budgets either collapse the whole market on day ~1 (caps small) or
are so large they never bind, giving *no* interference (caps large) — only a narrow, hard-to-hold
window between. A **daily advertiser budget** (the standard UA campaign model) is both more realistic
and sustainable at scale: it partially binds each day, so treated users early in the day's random
order exhaust the budget and **starve control users later that day** — intra-day cannibalization that
persists over the whole horizon and still scales with allocation. Calibrated to `budget_cap` μ=8
(~58% of unconstrained daily demand served). **Implications:** `config.offers.refill: daily`,
`budget_cap.mu: 8`; the engine self-checks for market/population collapse and warns. `refill: none`
remains available for the permanent-exhaustion story but needs a budget probe to retune at scale.
Verified: 45-day run sustains (conv/day 41k→34k, active 60k→42k from natural churn), A/A SRM clean.
**Supersedes** the `refill: none` config default only; the *interference thesis* is unchanged
(budget cannibalization is still the channel, now intra-day rather than over-horizon).

### D-12 · 2026-06-03 · ACCEPTED · Ground truth at two levels; recovery target = global ATE via shadow runs
**Why:** the per-conversion `ground_truth_tau` written by the engine is a cheap agent-level *local*
effect (single-draw expected-margin lift). The estimand the recovery tests must target is the
**global ATE** on the OEC — the all-treated vs all-control world difference, which *includes* the
budget/effort interference. That can't be read off one partial-rollout run; it's computed by replaying
the engine counterfactually (`market.run(force_arm=...)`). **Implications:** M2 adds shadow runs;
`ground_truth_tau` column stays (HTE/oracle use), but tests compare estimators to the shadow ATE.

### D-13 · 2026-06-03 · ACCEPTED · Money-shot analysis is at FIXED allocation; the ramp is operational realism
**Why:** the engine's ramp raises treatment share over days via a monotone hash threshold (a user
becomes treatment once allocation passes their fixed hash). Combined with churn this creates an
**assignment-cohort selection confound**: early-churning users never cross into treatment, so the
"treatment" group over-represents long-survivors with systematically higher outcomes — inflating the
naive estimate of *any* ramped experiment, even the no-op ranking lever (observed: ranking shows a
spurious +0.40, p≈1e-102; the two independent experiments' arms correlate 0.19 through shared
survival). **Implications:** (1) the rigorous naive-vs-corrected money shot and all recovery/bias
tests run at **fixed allocation** (constant from day 0 ⇒ balanced, unconfounded arms — this is why
the probe and `tests/` are clean and the constant-allocation A/A nulls correctly do not flag); the
ramp/interference-decay panel is built from **separate fixed-allocation runs at 5/20/50%**, not one
time-varying run. (2) The single ramped `make run` log remains the realistic substrate for the
dashboard, but `cli infer` **flags ramped rows as cohort-confounded**. (3) Phase-2 option: a
cohort-correct ramped estimator (condition on assignment epoch / analyze post-stabilization), or fix
arms at full allocation and gate when treatment *activates* — deferred. The interference thesis is
unaffected (it's demonstrated cleanly at fixed allocation).

### D-14 · 2026-06-03 · ACCEPTED · Ghost-ads holdout converts *organically* (reward withheld, not blocked)
**Why:** EVENT_LOG had a latent contradiction — §6.5 said "no conversion for a holdout agent" while
§5 said "lift = treatment vs holdout on advertiser conversions" (which needs holdout to *have*
conversions). The ghost-ads / PSA-holdout design (Johnson–Lewis–Nubbemeyer 2017) resolves it: the
holdout has the **reward withheld** (`reward_shown = 0`, so a low pick-probability falls out of the
choice model), but can still complete the offer **organically**. The incremental lift = treatment −
holdout on conversions then measures the reward's *causal* effect (vs the Lewis–Rao "would have
converted anyway" baseline). **Implications:** `engine/market.py` lets holdout flow into the normal
conversion path (reward already 0); `engine/emit.py` §6.5 invariant revised to *allow* holdout
conversions but **assert `reward_shown = 0`** on them; `inference/incrementality.py` estimates the
lift; `tests/test_incrementality.py` asserts it's positive/significant and that holdout conversions
carry no reward. EVENT_LOG §2.3/§5/§6.5 updated.

### D-15 · 2026-06-03 · ACCEPTED · Per-cluster random effect gives clusters real structure (ICC>0)
**Why:** the cluster correction (`inference/cluster.py`) was inert because `cluster_id` was a random
label with no shared structure → intra-cluster correlation ICC≈0 → cluster-robust SE = naive SE
(surfaced honestly in `notebooks/03`). Added a **per-cluster random-effect intercept** on utility
(`agents.cluster_effect_sigma`, default 0.5; a shared geo/segment engagement shock), sampled once per
cluster from a new `clusters` RNG stream. **Implications:** within-cluster outcomes correlate
(ICC≈0.02), so a **cluster-randomized** experiment analyzed at the user level overstates precision and
needs cluster-robust SEs (~1.3× wider) — the Glovo lesson, now a real test (`tests/test_cluster.py`).
A **user-randomized** design is unaffected (the shared effect cancels across balanced arms). The
budget-channel **recovery tests isolate it off** (`iso_cfg` sets sigma=0), exactly as they already
isolate to one advertiser. `cluster_effect_sigma=0` recovers the prior inert-label behaviour. This is
the SE half of the cluster story; the bias half (cluster-contained interference a cluster design
*fixes*) is the Game-B leg, B-07.

### D-16 · 2026-06-04 · ACCEPTED · PIVOT — Vega becomes the DGP layer inside Lyra (an experimentation platform)
**Why:** the on-target artifact for a founding-DS role is *operating the experimentation chassis*
(assignment, logging, metrics, scorecard) — but that's the least differentiating thing to build. The
portfolio inversion: a **thin-but-real chassis** + a **deep inference engine** (the moat) + the
**simulator as a validation harness** (certify estimators recover known ground truth — a superpower
real platforms lack). So the project is reframed as **Lyra** (the platform) with **Vega** (the
DGP/sim/validation layer) inside it; the Almedia marketplace is **Vega Level-3** on a fidelity ladder
(L0 iid → L1 covariates→PO+CATE+confounding → L2 temporal/carryover → L3 marketplace).
**Implications:** new north-star **`LYRA.md`**; `PROPOSAL.md` retained as the Vega-L3 spec; CLAUDE.md
reframed. Core architecture = two parallel **Protocols** (`Estimator`/`DGP`) closed by the
`sim→assign→estimate→compare-to-truth` loop; the **Monte-Carlo harness = power engine + promotion
gate**. Everything built (`engine`, `inference`, `metrics`, `frontend`, `tests`, `notebooks`) maps to
a Lyra layer (LYRA §1) — **reframe, not restart**; we're ~mid-Phase-1. Operating model = **notebooks-
first promotion** (LYRA §10): `/research` notebook → harden behind the Protocol + harness → promote.
Naming (Lyra/Vega) and the eventual `lyra/`+`vega/` directory reorg are open (confirm before moving files).

### D-17 · 2026-06-04 · ACCEPTED · Notebook curriculum + the **raw-notebook-first** workflow
**Why:** Daniel learns/builds by writing each method **raw, by hand, in a Jupyter notebook first** (using
numpy/statsmodels/sklearn directly, seeing every mechanic) and *only then* extracts to `.py`. He
explicitly dislikes a notebook that imports pre-built helpers he hasn't built ([[notebooks-first-promotion]]).
**Decision:** the engine is built via a **12-notebook curriculum** (`notebooks/ROADMAP.md`), each notebook
= raw build → extract to `lyra/` behind the `Estimator`/`DGP` contract → harness-gate → register. The
`_old/` folder holds the 5 first-pass notebooks (recycle). Order: 01 spine · 02 DGP-zoo · 03 metrics ·
**04 cluster-SEs** · 05 designs/interference · 06 switchback · 07 sequential · 08 power/decisions · 09 CATE
· 10 uplift/policy · 11 observational · 12 incrementality. **Done:** NB 01→`lyra/{protocols,dgp,estimators,
harness}`, NB 02→`lyra/dgp/`, NB 03→`lyra/metrics.py`; 27 tests pass. (Mistake logged + corrected: never
pre-build the `.py` then have the notebook call it — raw first, always.)

### D-18 · 2026-06-04 · ACCEPTED · **Chassis MVP interlude after NB 04**, then resume notebooks
**Why:** the chassis is decoupled from the inference engine (the `Estimator`/`DGP` contracts + registry let
methods plug in later). After NB 04 we have a credible engine-v1 (core ATE + typed-metric variance +
cluster-robust SEs) — enough correctness to power real experiments without embarrassing inference, and a
demonstrable end-to-end platform is high portfolio value. **Decision:** after NB 04, do a **Chassis MVP**
(FastAPI: source-agnostic assignment + experiment registry/state-machine + governed metrics over the event
log + the **sequential-SRM gate** + evolve the existing React app into the **state-gated scorecard** with
CI-colored-bar), guided by **`papers/platform-engineering.md`** (the harvested playbook). Then NB 05+ plug
in incrementally. Two later notebooks *enrich* the scorecard rather than block it: sequential/always-valid
(NB 07 → advisory auto-stop) and power/decisions (NB 08 → DRAFT power-gate + decision rule).

### D-19 · 2026-06-07 · ACCEPTED · Two capability kinds — **per-experiment designs vs cross-cutting practices**, composed per experiment
**Why:** Daniel observed that NB 07 (sequential testing) shouldn't be "one more showcase experiment" — it's
a **practice that applies to *every* experiment**, not an experiment *type*. Generalizing: capabilities
split in two. **(1) Per-experiment design & estimator** (the moat — what makes *this* experiment's point+CI
correct; you pick the one that fits): metric-type→variance (NB 03), cluster-robust SE (NB 04), interference
(NB 05), switchback (NB 06), CATE (NB 09), DiD/IV (NB 11), incrementality (NB 12). **(2) Cross-cutting
practices** (applied to *all*): SRM · A/A · always-valid sequential monitoring + advisory stop (NB 07) ·
power-gate + decision rules (NB 08) · BH-FDR across the portfolio.
**Decision:** the **chassis composes both per experiment** — every experiment carries: right design · right
variance · SRM/A·A · always-valid monitoring · certified-vs-truth (and, NB 08, a power-gate + decision rule).
**Implications:** notebooks still build each piece raw→promote; but the *platform wiring* applies the
cross-cutting layer uniformly (the scorecard already runs SRM + the CS + the certified badge on every running
experiment; the registry shows portfolio FDR). Future cross-cutting notebooks (NB 08 power/decisions) wire
into DRAFT/DECIDED across all experiments, not as a single new experiment.

---

## Open decisions / parking lot (from PROPOSAL §12)
- Final project name (Vega? alternatives welcome).
- Exact MNL vs nested-logit choice for the agent model.
- BigQuery: "designed-for-BQ locally" vs actually run on BQ.
- How much of Phase 2 to fold forward if the interview timeline is tight.
