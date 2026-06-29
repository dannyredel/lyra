# PROGRESS.md — Lyra/Vega status board

> Status: `TODO`·`WIP`·`BLOCKED`·`DONE`·`PARKED`. Last updated: **2026-06-25**.
> **Lyra** — read `LYRA.md` (north star) · `notebooks/ROADMAP.md` (curriculum) · `DEPLOY.md` · the memories.

## Now — platform is **feature-complete + demo-ready**; next focus = **PUBLISH to a live website**

The build is done. The platform is real end-to-end and the deploy model is decided + verified. The
remaining work is **shipping it live + publish polish**, not features.

1. **Inference engine (`lyra/`)** — curriculum **NB 01–12 COMPLETE** (incl. **NB 11 observational, done
   2026-06-25**: selection-on-observables → hidden confounder → sensitivity analysis [robustness value / OVB /
   E-value] → ground-truth meta-validation → `lyra/observational.py`). Every method validated vs ground truth.
2. **Chassis (`chassis/`, FastAPI)** — operative **create → run → decide** loop; four surfaces
   (**Experiments** · **Metrics** governed catalog · **Decisions** portfolio ship-rule · **Assignment**
   bucketing+SRM); world templates span the design space (A/B · cluster · switchback · interference);
   certified-vs-truth badge · always-valid CS · SRM · FDR.
3. **Frontend (`frontend/`, Vite+React+Recharts, "Ocean")** — **UX redesign complete (Phases 1–4)**: Home +
   6 industry study cases · 4-step create wizard (incl. the **Spotify-style sample-size calculator**) ·
   interactive client-side DGP plots · **detailed-analytics** scorecard tab (MC sampling dist · coverage
   caterpillar · per-arm hist) · Lyra-constellation logo · skeletons. Pre-pivot replay app retired to `_legacy/`.

**Deploy model (decided 2026-06-10):** **static-snapshot demo** — the app falls back to
`frontend/public/data/chassis.json` when `/api` is unreachable, so `frontend/dist/` is a self-contained
static site (verified via `npm run preview`). Zero-cost host (Vercel/Netlify/GH-Pages). Live backend
(create→run→decide) is the optional paid path (Render/Fly). See **`DEPLOY.md`**. **65 tests passing.**

**The music-marketing lab** (`labs/music-marketing/`) — the geo-lift/MMM identification study — is **parked
as a self-contained side lab** (distilled into NB 11); not part of the platform publish.

### ▶ Resume — publish path (see "Phase P — Publish" below)
- Static demo (deploy vehicle): `python -m chassis.export` → `cd frontend; npm run build` → deploy `dist/`.
  Live app (local full loop): `uvicorn chassis.app:app --port 8000` + `cd frontend; npm run dev`.
  Tests: `python -m pytest`. (PowerShell: use `;` not `&&`.)

## Phase P — Publish to a website (next focus)

| ID | Task | Status | Notes |
|---|---|---|---|
| P-01 | Refresh snapshot + confirm `npm run build` / `preview` is current & self-contained | TODO | regen `chassis.json`; sanity-check all surfaces read-only |
| P-02 | Deploy static `frontend/dist` to a host (Vercel rec.) + SPA rewrites + verify live URL | TODO | the actual "publish" — fast win |
| P-03 | Publish polish: Home/pitch copy, OG image + meta, mobile pass, demo-mode clarity | TODO | recruiter-readable in 30s; simulator-superpower unmissable |
| P-04 | About/credits + links (GitHub, LinkedIn, the notebook curriculum / study site) | TODO | show the depth behind the demo |
| P-05 | (optional) Live backend on Render/Fly so create→run→decide works online | TODO | fast-follow; cold-starts + in-memory state |

**Lyra engine — the new `lyra/` package (notebooks-first):**
| NB | Topic | Notebook | Promoted to | Status |
|---|---|---|---|---|
| 01 | Spine: contracts + harness + DGP-ladder(L0/L1) + Core-ATE(diff/OLS/**AIPW**) + robustness-grid | `notebooks/01_spine` | `lyra/{protocols,dgp,estimators,harness}.py` | **DONE** |
| 02 | DGP zoo: binary/count/revenue/ratio/survival/funnel/staggered-panel | `notebooks/02_dgp_zoo` | `lyra/dgp/{ladder,outcomes,funnel,panel}.py` | **DONE** |
| 03 | Metrics: type→variance (proportion-z · ratio-**delta** · CUPED · A/A gate · `MetricSpec`) | `notebooks/03_metrics` | `lyra/metrics.py` | **DONE** |
| 04 | **Cluster-robust SEs** (CV1/CV2/CV3 · wild cluster bootstrap · few-clusters · Moulton) | `notebooks/04_cluster_robust_se` | `lyra/se.py` + `lyra/dgp` `ClusteredDGP` | **DONE** |
| 05 | **Designs & interference** — shared-budget marketplace · naive-decay money-shot · cluster fix · the certify verdict | `notebooks/05_interference` | `lyra/dgp` `InterferenceDGP` | **DONE** |
| 06 | **Temporal interference — switchback** + VR (Raw→CUPED→CUPAC→DML-DR) + power floor + Type-S | `notebooks/06_switchback` (recycled `_old/04`) | `lyra/dgp` `SwitchbackDGP` + `lyra/estimators_vr` `SwitchbackCUPED` | **DONE** |
| 07 | **Sequential & diagnostics** — always-valid CS + advisory stop + BH-FDR (**cross-cutting layer on every experiment**) | `notebooks/07_sequential` | `lyra/{sequential,diagnostics}.py` | **DONE** |
| 08 | **Power, sizing & decisions** — SSC + sim-power + test-and-roll + the **ship rule** (OEC superiority ∧ guardrails non-inferior ∧ certified) — **cross-cutting bookends** | `notebooks/08_power_decisions` | `lyra/{power,decisions}.py` | **DONE** |
| 09 | **CATE — who responds** — S/T/X-learners + causal forest, validated vs the known τ(x) (RMSE + honest-CI coverage) | `notebooks/09_cate` | `lyra/cate.py` + `lyra/dgp` `HeteroDGP` | **DONE** |
| 10 | **Uplift eval & policy** — DR-scores · uplift/AUUC · RATE (real-heterogeneity test) · threshold/tree policy · IPS-vs-DR OPE, validated vs truth | `notebooks/10_policy` | `lyra/policy.py` + `lyra/ope.py` | **DONE** |
| 11 | **Observational — selection on observables (AIPW/DML) → hidden confounder → sensitivity analysis (robustness value · OVB contour · E-value) → ground-truth meta-validation** | `notebooks/11_observational` | `lyra/observational.py` | **DONE** (2026-06-25) |
| 12 | **Incrementality & real-data** — ghost-ads/PSA holdout (naive 6× biased → ITT/CACE recover truth) · **Criteo Uplift RCT** validated at scale | `notebooks/12_incrementality` | `lyra/incrementality.py` + `validation/criteo.py` | **DONE** |

Tests: **65 passing** (dgp_zoo 8 · metrics 5 · se 5 · chassis 5 · chassis_api 4 · interference 3 · switchback 3 · sequential 5 · cate 3 · policy 3 · incrementality_lyra 2 · original 14 + more). `_old/`
holds the 5 first-pass notebooks (recycle).

**Paper-harvest DONE (2026-06-04):** `papers/platform-engineering.md` (the **chassis playbook** — ideas
to steal, by component) + `notation/{cluster-robust-se,frugal-parameterization}.md`. 25 PDFs converted,
read via 6 subagents, 22 filed; INDEX §12/§13 added. ⚠️ Spotify risk-aware PDF is image-only (needs OCR).

**Then — Chassis MVP interlude (D-18), after NB 04:** stand up the thin-but-real platform (FastAPI
assignment + registry/state-machine + governed metrics over the event log + sequential-SRM gate +
evolve the React app into the state-gated scorecard), per the playbook; then resume NB 05+.

| ID | Task | Status | Notes |
|---|---|---|---|
| T-01 | Repo scaffold: folder structure, STRUCTURE.md, pm/, packaging, CI, Docker | WIP | this session |
| T-02 | `paper-library/`: 38 PDFs classified into 10 topics; INDEX.md + TO_ACQUIRE.md written | DONE | 2026-06-02 |
| T-03 | Acquire INDEX `⬜` gaps (PyMC/CausalPy, incrementality, OPE, CUPED, surrogate index) | TODO | DML classics now ✅ |
| T-04 | Process ⭐ foundational set into `papers/` + `notation/` (via PROCESSING.md pipeline) | WIP | Wager ch.1–7,10–13 done; Johari 2017 + Kohavi 2026 done 2026-06-02; ch.8,9,14–16 + Howard 2022 + Spotify cluster pending |
| T-14 | **Platform-experimentation thrust** (the operational A/B gap): peeking/anytime-valid, power/MDE, test-and-roll, SRM, FDR, ramp | DONE | `papers/platform-experimentation.md` + `notation/{anytime-valid,power-mde,test-and-roll}.md` + **`study/experiment-design.html`** (7-tab interactive lab: power/MDE, test&roll, Type-S/M, FPR, peeking MC + CS-tax chart, SRM — all live JS, math verified in Node). Caught + fixed a 22%→36% FPR error in power-mde.md. |
| T-15 | Acquire power cluster + Kohavi-Tang-Xu book | WIP | ✅ owned: Gelman-Carlin'14, Deng-delta'18, Larsen'23/24 (review), Nie'22 (eBay SRM), Nordin-Schultzberg'24. Still ⬜: Cohen, Button, Simonsohn, Benjamin, Azevedo, van Belle, KTX book |
| T-05 | Reconcile INDEX ↔ LITERATURE into one list | DONE | 2026-06-02; INDEX is now the single source |
| T-10 | HTE leg: GRF + metalearners filed (§11) + 2 notation sheets + cluster note | DONE | 2026-06-02 |
| T-11 | Build Tier-1 study site (single multi-chapter HTML): DR, HTE(+metalearners/forests), Policy/OPE, Interference | DONE | 2026-06-02 · `study/index.html` |
| T-12 | Tier-2 study chapters: RCT/IPW, IV/LATE, DiD | DONE | 2026-06-02 · 7 chapters live |
| T-12b | (opt) Tier-3 study chapters: adaptive (ch.6), balancing (ch.7) | TODO | if useful |
| T-13 | Acquire metalearner primaries (Nie-Wager 2021, Kennedy 2023) + Munro-Kuang-Wager 2025 | TODO | Künzel ✅ |
| T-06 | Equation/notation side-project (`paper-library/notation/`) seeded; `dml.md` written | DONE | 2026-06-02 |
| T-07 | Token-saving read pipeline: `scripts/pdf_to_md.py` + `PROCESSING.md` | DONE | 2026-06-02 |
| T-08 | `STACK.md` — go-to Python packages (lib-over-handcode); wired into CLAUDE.md | DONE | 2026-06-02 |
| T-09 | Notation sheets use LaTeX-in-markdown convention | DONE | 2026-06-02 |

## Phase 1 — Almedia MVP (build order)

| ID | Task | Status | Spec ref |
|---|---|---|---|
| T-10 | `engine/config.py` — load + validate `config.yaml`, seed mgmt | DONE | config.yaml · `_Node`/`Config`, 6 RNG streams |
| T-11 | `engine/agents.py` — seeded agent population | DONE | PROPOSAL §4 · traits + arrivals + churn memory |
| T-12 | `engine/offers.py` — offers/advertisers, budget caps | DONE | config `offers` · adv_A.. letters, per-offer budget |
| T-13 | `engine/choice.py` — MNL/nested-logit utility (= ground truth) | DONE | config `choice` · MNL + outside option (nested → Phase 3) |
| T-14 | `engine/experiments.py` — assignment policies + ramp + levers | DONE | EVENT_LOG §2 · hash assign, monotone ramp, `design` |
| T-15 | `engine/emit.py` — event-log writer, enforce invariants | DONE | EVENT_LOG §1/§3/§6 · parquet, 7 invariants, unit-aware SRM |
| T-16 | `engine/market.py` — daily tick loop, emit in order | DONE | EVENT_LOG §2 · tick loop + budget-split + calibration |
| T-17 | `cli.py` — `make run`/`infer` emits + reads the log | DONE | `run` (5.4M-event log) + `infer` readout |
| T-18 | `engine/oracle.py` — global ATE via counterfactual shadow runs | DONE | M2 ground truth (D-12) |
| T-20 | `metrics/` dbt: staging views; `real` drops `ground_truth_tau` | DONE | M3 · `stg_events` (real-mode tau drop verified) |
| T-21 | `metrics/` intermediate + marts: experiment readouts, SRM | DONE | M3 · `int_experiment_users` → `mart_{experiment_readout,experiment_effects,srm}`; effect+CI in SQL; **unit-aware SRM** (data-detects cluster vs user); 23 dbt tests pass |
| T-30 | `inference/naive.py` + `test_naive_bias.py` (assert the bias) | DONE | bias excludes ATE + grows w/ allocation ✅ |
| T-31 | `inference/cluster.py` + A/A SE test | DONE | cluster-robust SE; A/A no-flag ✅ |
| T-32 | `inference/budget_split.py` + recovery test | DONE | design recovers ATE (coverage) ✅ |
| T-33 | `tests/test_aa_null.py` — A/A must not flag; SRM check | DONE | user+cluster A/A no-flag + unit-aware SRM ✅ |
| T-34 | `inference/base.py` — duckdb per-user loader + `Effect` type | DONE | reads parquet directly (dbt = M3) |
| T-40 | Ramp / interference-decay diagnostic (the money-shot panel) | WIP | fixed-alloc bias-vs-allocation proven in probe+tests; panel viz → dashboard |
| T-41 | `inference/anytime_valid.py` — confidence sequences | DONE | M4 · asymptotic CS (Waudby-Smith); covers truth + wider than fixed-n; **A/A CS covers 0 at every day** (peeking-safe) |
| T-42 | `inference/cuped.py` — variance reduction | DONE | M4 · warmup covariate; SE strictly < naive, unbiased |
| T-43 | `inference/incrementality.py` — ghost-ads holdout lift | DONE | M4 · treatment-vs-holdout on conversions; holdout converts organically (D-14); lift +sig |
| T-50 | `validation/criteo.py` — real-data leg | TODO | Criteo Uplift |
| T-60 | `frontend/` replay dashboard (portfolio, detail, ramp, world) | WIP | PROPOSAL §9 · **Vite+React+Recharts**, 4 screens live: Portfolio · Experiment-detail (narrowing band + ground-truth line + guardrails + decision banner) · Interference/ramp diagnostic · **World view** (offer wall + population/conversions over the clock). `world.json` in exporter. Remaining: static deploy (GitHub Pages) + optional anytime-valid CS band. |
| T-61 | `serving/export.py` — snapshot exporter (events+inference → dashboard JSON) | DONE | bridges to frontend without M3 on the path; will swap to dbt marts later |

## Phase 2+ — parked (see BACKLOG.md)

OPE depth (IPS/DR), HTE, eval funnel, FDR/collision matrix, streaming adapter, switchback,
other verticals (Glovo/Trivago/Zalando).

## Done

_(nothing shipped yet)_
