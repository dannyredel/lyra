# Vega — A Ground-Truth Marketplace Lab for Causal Experimentation

> **PIVOT (2026-06-04): this is now the inner DGP layer of a broader platform.** See **[`LYRA.md`](LYRA.md)**
> for the current north star — *Lyra* is the experimentation **platform** (assignment, governed metrics,
> lifecycle, scorecard, harness); **Vega** is the **DGP + simulation + validation layer inside it**, and
> this marketplace is **Vega Level-3** (the agent-based DGP). This document is retained as the Vega-L3
> spec (the agent model, the two MVP experiments, calibration). Everything built so far slots into a
> Lyra layer (LYRA §1) — the pivot reframes, it doesn't restart.
>
> Working name: **Vega** (after La Vega Central, Santiago) / **Lyra** (the platform). Rename freely.
> Status: proposal / pre-build. Owner: Daniel.
> One-line pitch: *A calibrated two-sided-marketplace simulator that serves as a ground-truth
> environment to prove which causal estimators survive realistic interference — and the
> production-grade system that runs, monitors, and ships those experiments end to end.*

---

## 1. The thesis (why this is not a toy)

On a real platform you can **never** validate a causal method, because you never observe the
counterfactual. A calibrated simulator is the only place where ground truth exists. So the
simulator is not a workaround for lacking data — it is a **validation environment**, exactly how
serious experimentation teams stress-test estimators before trusting them on live users.

**Headline claim of the project:**
> The standard A/B test a typical team would run is biased by X% under realistic supply-side
> interference. Here is the simulation that proves it, the corrected toolkit that recovers truth,
> and the production system that runs it all — live-monitored, with always-valid inference.

The "money shot" is the contrast: the **naive** estimate drifting away from truth as treatment
share grows, while the **corrected** estimate stays on the ground-truth line.

Two pillars of evidence behind the pitch:
- **Real-business causal credibility** → Compass Lexecon cartel-damages and pass-on work (DiD,
  hedonic, structural). That is causal inference *in anger*.
- **Can-productionize credibility** → this project: engine-as-service, tested inference library,
  dbt/SQL metrics, CI, containerized, live dashboard.

---

## 2. Target role alignment (Almedia — Founding Data Scientist)

The JD maps almost verbatim onto this project:

| JD requirement | How Vega answers it |
|---|---|
| "Causal validity — not just p-values" | The entire thesis: interference bias + ground-truth-validated correction |
| "Incrementality testing across marketing, product, and rewards" | Reward-sizing (rewards), ranking (product), ghost-ads incrementality (marketing) |
| "Build the data pipelines and measurement stack" | Event log → dbt/SQL metrics → inference library → serving |
| "Operationalising attribution models … MMPs, probabilistic attribution" | Ghost-ads / PSA-holdout incrementality leg on advertiser conversions |
| "Zero-to-one … shipped something production-ready" | Engine-as-service, tested inference package, CI, Docker, deployed dashboard |
| "Python and SQL; GCP preferred; dbt" | Python engine + dbt/SQL metrics designed for BigQuery |
| "Translate model outputs into decisions for non-technical stakeholders" | The dashboard + explicit ship/no-ship decision framework |

**Two additions promoted to MVP specifically because of this JD:**
1. An **incrementality leg** (advertiser-conversion outcome via ghost-ads / PSA holdout).
2. A **real-data validation leg** on the **Criteo Uplift** dataset, so we can say "validated the
   same estimator on real large-scale incrementality data" — the answer to "real business context."

---

## 3. MVP vertical: Almedia / Freecash (rewarded UA)

A genuine two-sided market: **advertisers** (games/apps) on one side, **reward-seeking users**
(~70M on Freecash) on the other; the platform matches users to offers to maximize completions/ROAS.

**Why this vertical for the MVP:**
- The user side is unusually **simulatable** — reward-seekers are close to utility-maximizers
  (payout-per-effort), so a discrete-choice agent is *defensible*, not a hand-wave. This kills the
  "your sim is fake" critique better than any other vertical.
- It is the closest structural match to the "simulate one side, experiment on the other" idea.
- Interference is economically clean: finite user effort/attention + finite advertiser budgets.

**The framing:** simulate the reward-seeking **user** side; run experiments on the
**offer / reward-design** side.

---

## 4. The market model (the spine everything hangs off)

**Agents (users):** N reward-seeking agents, each with
- daily **effort budget** (time/attention),
- **reward sensitivity** (elasticity),
- per-**category conversion propensity**,
- a **churn hazard**.

**Offers (advertiser campaigns):** each offer has
- advertiser **payout**, **difficulty/effort** required,
- **reward shown** = payout × pass-through,
- **category**, **budget cap**.

**Choice:** users pick offers via discrete-choice utility,
`u = f(reward, effort, preference_match) + noise` — **MNL / nested logit** workhorse
(reuses the BeeSignal conjoint muscle). Because *we* set the utility parameters, **we know the
true effect** of any change → ground truth.

**Dynamics (daily ticks):** budgets deplete, offers exhaust, users churn, new users arrive.

**Where interference comes from (the bias we expose):**
- **Budget cannibalization** — a treated offer with a richer reward depletes advertiser budget
  faster and pulls users from control offers competing for the same finite user attention.
- **Cross-experiment leakage** — even experiments on *different* games interfere through the
  *shared user effort budget*: effort spent on Game A's richer reward is unavailable to Game B.

---

## 5. The two MVP experiments (one treatment per game)

Each experiment lives on its **own game/advertiser** → isolated by design, clean analysis, but
both draw on the **shared global user pool** (the source of cross-experiment leakage).

| | **Experiment 1 — Game A** | **Experiment 2 — Game B** |
|---|---|---|
| Lever | **Reward sizing** (+X% reward) | **Offer-wall ranking** (new sort algorithm) |
| Interference | Budget cannibalization | Attention competition |
| Story | Economic / pricing | Recommender / OPE leg |
| Naive estimator | User-level A/B (biased) | User-level A/B (biased) |
| Corrected estimator | Cluster / budget-split | Cluster + ranking-aware; OPE (IPS / DR) |

Plus **2–3 A/A nulls + decoys** running concurrently → demonstrates false-positive control,
experiment collision through shared users, and FDR across the portfolio.
Total **~4–6 concurrent experiments** for the MVP. (One experiment per game; do not stack
treatments on one offer.)

---

## 6. Experiment taxonomy (what "clients" actually test)

| Type | Example | Primary metric | Interference |
|---|---|---|---|
| Reward sizing / pass-through | +10% reward on a category | completion rate, margin | **High** |
| Reward schedule / timing | lump-sum vs milestone vs 90-day | retention, LTV | **High** + long-horizon |
| Offer-wall ranking / personalization | new sort algorithm | completions, value/user | **High** (attention) |
| Gamification (quests, streaks) | daily-bonus bar | DAU, retention | Medium |
| Onboarding flow | fewer signup steps | activation | **Low** |
| Re-engagement / notifications | send-time optimization | reactivation, churn | Low–Medium |

The low-interference rows are **contrast cases** — proof we know when a naive A/B is fine and
don't over-engineer. MVP headline = reward sizing + ranking; keep onboarding as the
"naive test works here" control.

---

## 7. Design decisions

**Metrics / OEC.** Primary: **margin per active user**. Guardrails: advertiser ROAS, user
retention, payout cost. Split **short-term** (completions today) vs **long-term** (retention/LTV)
— sets up surrogate / long-term-effect estimation as a theme (the 90-day reward case).

**Statistical design.** Power/MDE → duration (trivial since we control N); **CUPED** variance
reduction off pre-period activity; **anytime-valid inference** (confidence sequences) for the live
dashboard so peeking doesn't inflate error.

**Incrementality leg.** One experiment's outcome framed as advertiser-side incrementality: does
the reward *cause* conversions or capture users who'd convert anyway? **Ghost-ads / PSA-holdout**
design; measure lift **and validate it against ground truth**.

**Rollout / ramp.** `A/A → 1% → 5% → 20% → 50% → ship`, with SRM checks at each step.
Guardrail breach → **auto-rollback** (kill switch). The ramp is *where interference becomes
visible*: run the same experiment at 5/20/50% share and show the estimate drifting
(uplift-decay-with-allocation). This single panel ties ramp + interference + thesis together.

**Decision framework.** Explicit ship / no-ship rules + guardrail thresholds, so it reads like a
program, not a stats demo.

**Calibration (the anti-"fake" defense).** Anchor elasticities and effort distributions to
published stylized facts; peg plausible effect magnitudes to Almedia's real numbers (~2× 180-day
ROAS, ~3× ARPU, ~120% D7 retention) so simulated uplifts aren't fantasy.

---

## 8. Scale (config-driven; these are deliberate, stated scale-downs)

| Parameter | MVP value | Why |
|---|---|---|
| Users (agents) | **50k–100k** | Variance behaves like a real platform; 30–60-day run in seconds–minutes on a laptop |
| Offers / games | **30–80** (~2 under experiment) | Enough "wall" that ranking matters and cannibalization has somewhere to go |
| Clusters (geo/segment) | **50–200** | Below ~40, cluster-robust SEs get shaky — worth showing we know the boundary |
| Horizon | **30–60 days**, daily ticks | Long enough for long-term effects to diverge from day-one completions |

All in a `config.yaml`; dial N up to demo scaling, down for fast iteration. "Config-driven,
reproducible" is itself the production-grade signal.

---

## 9. Frontend & serving (decision: replay via recorded event log)

**Decision: replay, not streaming.** Transport (websocket vs file) is orthogonal to
production-maturity; the "beyond a notebook" signal is the *architecture*, not live polling.
Crucially, anytime-valid inference lives in the **time/data** dimension (CI narrows as simulated
days accumulate), **not** the transport dimension — so the sequential story is fully intact under
replay.

**Flavor: recorded event log, not precomputed charts.** The engine emits an append-only event
stream (assignments, conversions, budget decrements, churn) — the exact shape a real metrics
pipeline writes. The metrics+inference layer consumes it and produces snapshots; the dashboard
replays the log on a simulated clock. This is architecturally identical to consuming Kafka:
*"in production the source is a broker; here it's a recorded log replayed on a simulated clock"* —
swapping to live is a thin adapter, not a rewrite. And a static replay **always renders** in an
interview; a live host that spins down is a liability. Keep a local streaming mode to demo on request.

**Dashboard screens (what an internal platform actually looks like):**
1. **Portfolio / experiment list** — all running experiments: status, allocation %, primary metric,
   effect ± CI, health flag (SRM, guardrail breaches). The DS team's home page.
2. **Experiment detail** — hypothesis, metric defs, allocation, **confidence-sequence band**
   (narrows over time), guardrails, decision banner (not-yet-sig / ship / breached-rolled-back).
3. **Interference / ramp diagnostic** — *the differentiator* off-the-shelf tools lack: same effect
   at 5/20/50% allocation, naive drifting vs corrected stable on the ground-truth line.
4. **Market / world view** — the living simulated marketplace: offer wall, budgets depleting, user
   population (active/churned). Answers "what does a client/DS team see" — both world and experiments.
5. **(Phase 2) Portfolio stats** — FDR across experiments + collision matrix (which share users).

Stack: **React + Recharts** (matches the portfolio-site stack); time-slider / auto-advancing clock.
Deploy static (GitHub Pages).

---

## 10. Architecture (productionization is the point)

```
simulation engine  →  event log  →  metrics layer (dbt/SQL)  →  inference library  →  serving (API)  →  frontend (React)
```

- **Inference library is the crown jewel**: estimators (naive, CUPED, cluster-robust, budget-split,
  anytime-valid, OPE) as a standalone, importable, **unit-tested** package.
- **Tests assert the corrected estimator recovers ground truth within stated coverage** — only
  possible because we have a simulator. That test suite *is* the causal credibility, automated.
- **Metrics layer = dbt/SQL over the event log** (designed for BigQuery), not pandas transforms →
  turns "I know dbt" into "here is a dbt project computing experiment readouts."
- **Config-driven (YAML), containerized (Docker), CI runs the tests.** Reproducible by command.

(Full module map and the event-log data contract live in `STRUCTURE.md`.)

---

## 11. Phased roadmap

**Phase 1 — Almedia MVP (ship this first)**
Market model · reward-sizing + ranking experiments · naive-vs-corrected comparison ·
ramp/interference-decay diagnostic · CUPED · anytime-valid CIs · **incrementality (ghost-ads) leg**
· **Criteo real-data validation leg** · dbt/SQL metrics · replay dashboard · tested inference
library · Docker + CI.

**Phase 2 — Portfolio & policy depth (still Almedia)**
Parallel-experiment FDR + collision matrix · layered/overlapping assignment (Google-style) scaling
to 20–50 experiments · OPE depth on the ranking policy (IPS/DR + policy-value vs ground truth) ·
surrogate / long-term-effect estimation · streaming mode (FastAPI) as an optional showcase ·
**eval funnel for the ranking leg** (the "AI products" dimension): a proxy quality-score for ranking
variants sits *upstream* of Game B's experiment (verify before validate); the experiment validates
whether the judge-preferred variant moved completions/margin; then — uniquely possible in Vega —
calibrate the eval score against **ground-truth tau** to quantify how miscalibrated the proxy is.
Build a *simulated* noisy/biased judge in the engine, not a real LLM — it's cheaper and makes the
calibration (causal) point more cleanly. Pairs with rewarded-UA's growing use of ML ranking models
you'd want to eval-gate. (Also consider **interleaving** as a more sensitive ranking-eval method
for Game B than a plain split A/B — per Schultzberg & Ottens; and note the OPE leg's logged
propensities are the same **counterfactual logging** substrate the funnel relies on.)

**Phase 3+ — Other verticals (the long-term proposal)**
- **Glovo (delivery):** shared courier supply → **switchback + cluster** randomization.
- **Trivago (auction):** bid-equilibrium interference → **budget-split** design.
- **Zalando (ranking):** inventory/attention → cluster + uplift-decay diagnostic.
Each reuses the same engine/event-log/inference spine; only the market model + interference
mechanism + canonical correction change. Spotify's sequential-testing methods inform the
anytime-valid layer throughout.

---

## 12. Open decisions / parking lot
- Final project name (Vega? alternatives welcome).
- Exact MNL vs nested-logit choice for the agent model.
- Whether to expose the BigQuery story as "designed-for-BQ locally" or actually run on BQ.
- How much of Phase 2 to fold forward if interview timeline is tight.
