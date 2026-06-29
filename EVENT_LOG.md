# EVENT_LOG.md — Vega event-log emitter spec

The event log is the **only** interface between the engine and everything downstream (metrics,
inference, dashboard). Build the engine to this spec; build the dbt staging models to read it.
It deliberately mimics a production event stream — it stands in for Kafka, so swapping to a live
broker later is an adapter, not a rewrite.

---

## 1. Format & layout

- **Append-only.** Events are never updated or deleted; corrections are new events.
- One file per simulated day: `events/day=<NN>/events.parquet` (Hive-style partition).
- Columns are typed (see §3). `ts` is the simulated clock; wall-clock time is irrelevant.
- Every run is reproducible from `config.yaml` + `meta.seed`.

---

## 2. Event types & when they fire (per daily tick)

The engine processes one **tick = one simulated day**. Within a tick, emit events in this order so
the log is causally consistent:

1. **`arrival`** — for each new agent created this tick (`market.daily_arrivals`).
   Establishes the agent before it can be assigned or convert.
2. **`assignment`** — when an agent entering the offer wall is bucketed into an experiment
   arm. Emitted at most once per (agent, experiment) per its assignment policy.
   - `user` randomization → assign on first exposure, sticky thereafter.
   - `cluster` randomization → arm determined by the agent's `cluster_id`.
   - `holdout` (incrementality) → carved out of treatment per `incrementality.holdout_share`.
3. **`impression`** — agent views an offer (the choice set was shown). Always emitted for the
   offers an agent actually considered this tick. **For `holdout` agents, impressions fire with
   `reward_shown = 0`** (reward withheld) — the ghost-ads counterfactual. The agent may still
   complete the offer *organically* (a conversion with `reward_shown = 0`), see §6.5/D-14.
4. **`conversion`** — agent completes an offer. Carries `value` (margin contribution) and
   `reward_shown`. Drives the primary/guardrail metrics.
5. **`budget_decrement`** — advertiser budget reduced by a completion's payout. When an offer's
   cumulative decrements reach its `budget_cap`, the offer becomes unavailable (and stays so unless
   `offers.refill: daily`).
6. **`churn`** — agent leaves the platform (drawn against `churn_hazard`, lowered by recent
   rewards via `churn_reward_protection`). No further events for that agent.

> Ordering rule: an agent must have an `arrival` before any other event, and must not have events
> after its `churn`. The emitter asserts these.

---

## 3. Schema (one row per event)

| field | type | populated for | notes |
|---|---|---|---|
| `event_id` | string (uuid) | all | unique |
| `ts` | timestamp | all | simulated clock; monotonic non-decreasing within a day |
| `day` | int | all | tick index, 0…`horizon_days` |
| `event_type` | enum | all | `arrival`/`assignment`/`impression`/`conversion`/`budget_decrement`/`churn` |
| `user_id` | string | all | agent id |
| `cluster_id` | string | all | agent's geo/segment cluster |
| `advertiser_id` | string | impression, conversion, assignment, budget_decrement | game/app |
| `offer_id` | string | impression, conversion, budget_decrement | null for arrival/churn/assignment |
| `experiment_id` | string | assignment, impression, conversion | null if not under any experiment |
| `variant` | enum | assignment, impression, conversion | `control`/`treatment`/`holdout` |
| `allocation` | float | assignment | treatment share in effect at assignment time (ramp value) |
| `effort_spent` | float | impression, conversion | the shared resource that drives cannibalization |
| `reward_shown` | float | impression, conversion | `payout * pass_through`; 0 for holdout |
| `value` | float | conversion, budget_decrement | margin contribution / payout |
| `propensity` | float | assignment, impression | logged choice/assignment prob; required when `logs_propensity: true` (OPE) |
| `ground_truth_tau` | float | conversion | TRUE per-unit effect of the active treatment. **Engine-written, estimator-hidden** (see §4) |

Unused fields for a given `event_type` are null. Keep the column set fixed across event types
(wide log) for simple dbt staging.

---

## 4. `ground_truth_tau` — the rule that makes recovery tests meaningful

- The engine knows the true effect because treatments are defined as shifts to choice-model inputs
  (`config.choice`). It writes `ground_truth_tau` on every `conversion`.
- In `meta.mode: real`, the **metrics + inference layers must not read this column.** Enforce it:
  the dbt staging model for "real" runs drops `ground_truth_tau`; only `validation/` and
  `tests/test_recovery.py` read it (in `oracle` mode or directly from the raw log).
- This separation is the whole point: estimators see only what a real platform would see; the test
  suite checks their output against the hidden truth.

---

## 5. Encoding the things the analysis depends on

- **Ramp / interference-decay diagnostic** → `allocation` on each `assignment`. Downstream groups
  effects by `allocation` to show the naive estimate drifting while the corrected one stays flat.
- **Cross-experiment leakage** → emerges naturally: a single agent has a shared per-day
  `effort_budget`; `effort_spent` on Game A's richer treated offer leaves less for Game B. No
  special field — it falls out of the tick mechanics.
- **Incrementality / ghost-ads** → `variant = holdout`: `impression` fires, `reward_shown = 0`,
  no `conversion` credited to the reward. Lift = treatment vs holdout on advertiser conversions.
- **OPE** → `propensity` logged on assignment/impression for `exp_offer_ranking` so IPS/DR can
  reweight.

---

## 6. Invariants the emitter must guarantee (and assert)

1. Append-only; no row mutated after write.
2. `arrival` precedes, and `churn` terminates, every agent's event stream.
3. `ts` monotonic non-decreasing within a `day` partition.
4. Cumulative `budget_decrement.value` per offer never exceeds its `budget_cap`.
5. A `holdout` conversion is **organic**: it may occur (the agent completes despite the withheld
   reward) but must carry `reward_shown = 0` — no reward was served (D-14). Lift = treatment vs
   holdout on conversions (`inference/incrementality.py`).
6. SRM: realized arm shares match the intended `allocation` within sampling tolerance (this is the
   fixture `tests/test_aa_null.py` and the dashboard SRM flag both rely on).
7. `propensity ∈ (0,1]` wherever populated.

---

## 7. Worked micro-example (illustrative rows, fields trimmed)

```
day  event_type        user   cluster  advertiser  offer   exp                variant    alloc  effort  reward  value  tau
0    arrival           u_017  c_03     -           -       -                  -          -      -       -       -      -
7    assignment        u_017  c_03     adv_A       -       exp_reward_sizing  treatment  0.05   -       -       -      -
7    impression        u_017  c_03     adv_A       of_22   exp_reward_sizing  treatment  -      0.0     1.61    -      -
7    conversion        u_017  c_03     adv_A       of_22   exp_reward_sizing  treatment  -      1.8     1.61    0.74   0.09
7    budget_decrement  -      -        adv_A       of_22   -                  -          -      -       -       1.05   -
12   churn             u_017  c_03     -           -       -                  -          -      -       -       -      -
```

(`tau` = `ground_truth_tau`, present only on `conversion`, hidden from estimators in `real` mode.)

---

## 8. What Claude Code should build first against this spec

1. `engine/emit.py` — the writer enforcing §1, §3, §6.
2. `engine/market.py` tick loop emitting §2 in order.
3. `metrics/models/staging/` — typed views over the parquet; the "real" staging model drops
   `ground_truth_tau`.
4. `tests/test_recovery.py`, `tests/test_naive_bias.py`, `tests/test_aa_null.py` — read the raw log
   (oracle) and assert the §4/§6 guarantees and estimator behavior.
