# CLAUDE.md — Vega

Context file for Claude Code. Read this first. Keep it updated as decisions change.

## What this project is

**PIVOT (2026-06-04 — read [`LYRA.md`](LYRA.md), the north star).** The project is now **Lyra**, a
causal **experimentation platform** (assignment · governed metrics · lifecycle state machine ·
guardrails · scorecard · a deep inference engine) with **Vega** — the DGP + simulation + validation
layer — living *inside* it. Because Vega authors the data-generating process, the platform can
**certify that every estimator recovers a known ground truth with correct coverage** — a superpower
real platforms lack. The strategic inversion: a *thin-but-real chassis*, a *deep inference engine* (the
moat: switchback, interference-aware, CUPED++, always-valid, CATE→policy), and the *simulator as the
validation harness*.

**Vega** (the original project, now the inner layer) simulates the **reward-seeking user side** of a
rewarded-UA marketplace (Almedia / Freecash) and experiments on the **offer/reward side** — this is
**Vega Level-3** (agent-based DGP) on the fidelity ladder (LYRA §5). Everything already built
(`engine/`, `inference/`, `metrics/`, `frontend/`, `tests/`, `notebooks/`) maps to a Lyra layer
(LYRA §1) — the pivot reframes, it does not restart.

Three things must always be visible in the code:
1. **Causal validity** — correct inference (incl. under interference), **validated against ground
   truth via the Monte-Carlo harness**.
2. **The platform chassis** — assignment, the event log, governed/versioned metrics, the lifecycle, a
   scorecard. Thin but real.
3. **Notebooks-first promotion** — every new method is a `/research` notebook *first*, then hardened
   behind the `Estimator` Protocol + the harness gate, then promoted (LYRA §10). Daniel's operating model.

See `LYRA.md` (platform / north star), `PROPOSAL.md` (Vega-L3 marketplace spec), `STRUCTURE.md` (module
map + event-log schema), `ideas/lyra-experimentation-platform.md` (full method menu + scorecard tables).

## Core architecture (do not collapse these layers)

```
simulation engine → event log → metrics (dbt/SQL) → inference library → serving (API) → frontend (React)
```

- The **engine** runs and emits an **append-only event log** (assignments, conversions, budget
  decrements, churn). It must not compute experiment results itself.
- The **metrics layer is dbt/SQL over the event log** (designed for BigQuery). Do not replace it
  with pandas transforms — the dbt project is a deliverable.
- The **inference library** is a standalone, importable, **unit-tested** Python package. It is the
  crown jewel. Every estimator ships with a test asserting it recovers the simulator's known ground
  truth within its stated coverage.
- The **frontend replays the event log** on a simulated clock (NOT live streaming — see decision
  below). It is read-only and deploys static.

## Decisions already made (don't relitigate without flagging)

- **Replay, not streaming.** Anytime-valid inference lives in the time/data dimension, not
  transport. Replay always renders in an interview; streaming is an optional Phase-2 showcase
  behind a thin adapter.
- **MVP vertical = Almedia / Freecash** (rewarded UA). Other verticals (Glovo switchback, Trivago
  budget-split, Zalando ranking) are Phase 3+, reusing this spine.
- **Two MVP experiments, one treatment per game:** Game A = reward sizing; Game B = offer-wall
  ranking. Plus 2–3 A/A nulls + decoys. Never stack treatments on one offer.
- **Incrementality leg (ghost-ads / PSA holdout) is in the MVP**, not Phase 2 — the target JD is
  attribution-heavy.
- **Criteo Uplift real-data validation leg is in the MVP** — needed to answer "real business context."
- **Agent choice model = MNL / nested logit.** Ground truth = the utility parameters we set.
- **Scale:** 50k–100k agents, 30–80 offers (~2 under experiment), 50–200 clusters, 30–60-day
  horizon. All in `config.yaml`.
- **OEC:** primary = margin per active user; guardrails = advertiser ROAS, retention, payout cost;
  split short-term vs long-term outcomes.
- **Eval funnel is Phase 2, simulated judge only.** The ranking leg (Game B) gets an upstream proxy
  quality-score (verify) feeding the experiment (validate), then the score is calibrated against
  ground-truth tau. Do NOT build a real LLM judge for this — simulate a noisy/biased score in the
  engine; the causal point is the offline-online calibration, not the judge itself.

## Stack & conventions

- **Python** for engine + inference library. **SQL/dbt** for metrics. **React + Recharts** for
  frontend. **Docker** + **CI** (run the test suite). GCP/BigQuery is the design target.
- **Use established statistical libraries; don't hand-roll the stats** (no OLS/clustered-SEs/DML by
  hand when `statsmodels`/`linearmodels`/`econml`/`doubleml`/`pyfixest`/`pymc` exist). Go-to package
  per task → [`STACK.md`](STACK.md). Hand-roll **only** the flagged gaps where no good package exists
  (anytime-valid CS, budget-split, switchback) — there the estimator *is* the deliverable.
- Everything **config-driven** via `config.yaml`. No magic numbers in code.
- **Reproducible by command** — a single `make`/CLI entrypoint should run a full experiment and
  emit the event log.
- **Calibrate, don't fantasize** — elasticities/effort anchored to published stylized facts; effect
  magnitudes pegged to Almedia's real figures (~2× 180-day ROAS, ~3× ARPU, ~120% D7 retention).
- Seed all randomness; runs must be reproducible given a seed + config.

## Testing rules (non-negotiable)

- Every estimator has a **recovery test**: on a simulated run with known ground-truth effect, the
  estimator's interval covers truth at its nominal rate.
- Demonstrate the **bias of the naive estimator** as a test/fixture, not just a chart — the bias is
  a measurable, asserted quantity.
- A/A tests must **not** flag (false-positive control); include this as a test.
- "If you debug it twice, automate it" (per the JD) — turn repeated manual checks into tests.

## Working style for Claude Code in this repo

- Prefer small, composable modules over monoliths. Keep layers decoupled (engine knows nothing
  about the dashboard).
- When adding an estimator, add it to the library + its recovery test + wire it into the metrics
  readout, in that order.
- Don't add a dependency without noting why in the PR/commit.
- Keep `PROPOSAL.md`, `STRUCTURE.md`, and this file in sync with reality; if a decision changes,
  update the "Decisions already made" section.

## Current focus

Phase 1 MVP. Build order suggestion: engine + event log → config → metrics (dbt) → inference
library (naive + cluster/budget-split + recovery tests) → ramp/interference diagnostic →
anytime-valid layer → CUPED → incrementality leg → Criteo validation → dashboard replay.
