# STRUCTURE.md — Vega module map

The data contract (event-log schema, invariants) lives in [`EVENT_LOG.md`](EVENT_LOG.md).
This file is the **module map**: where each responsibility lives and how the layers connect.
Keep it in sync with reality; if you move a module, update this file in the same change.

## Layering rule (do not collapse)

```
engine/  →  events/  →  metrics/ (dbt/SQL)  →  inference/  →  serving/ (API)  →  frontend/ (React)
   │           │              │                    │
 writes    append-only    typed views          tested
 the log    parquet       over the log         estimators
```

Each arrow is a **one-way dependency**. The engine knows nothing about inference or the
dashboard. Inference reads only what the metrics layer exposes (and, in `real` mode, never
sees `ground_truth_tau`). The only cross-layer interface is the event log.

---

## Directory map

```
Vega/
├── config.yaml              # single source of truth for a run (no magic numbers in code)
├── cli.py                   # `python -m vega ...` / make entrypoints: run, metrics, infer, validate
│
├── engine/                  # the simulator — emits the event log, computes NO experiment results
│   ├── config.py            # load + validate config.yaml into typed objects; seed management
│   ├── agents.py            # agent population: effort budget, reward sensitivity, churn hazard
│   ├── offers.py            # offer/advertiser campaigns: payout, difficulty, budget caps
│   ├── choice.py            # MNL / nested-logit utility = GROUND TRUTH; treatment = utility shift
│   ├── experiments.py       # assignment policies (user/cluster/holdout), ramp schedule, levers
│   ├── market.py            # the daily tick loop; orchestrates arrival→…→churn (EVENT_LOG §2)
│   └── emit.py              # the event-log writer; enforces schema + invariants (EVENT_LOG §1,3,6)
│
├── events/                  # OUTPUT: append-only parquet, day=NN/events.parquet (gitignored)
│
├── metrics/                 # dbt project over the event log (designed for BigQuery; DuckDB local)
│   ├── dbt_project.yml
│   ├── profiles.yml         # duckdb target (default) + bigquery profile (documented swap)
│   └── models/
│       ├── staging/         # typed views over raw parquet; `real` staging DROPS ground_truth_tau
│       ├── intermediate/    # per-(experiment,arm,day) aggregates; cluster aggregation
│       └── marts/           # experiment readouts, guardrails, ramp/allocation panel
│
├── inference/               # THE CROWN JEWEL — standalone, importable, unit-tested estimators
│   ├── naive.py             # user-level diff-in-means (the biased baseline we expose)
│   ├── cuped.py             # variance reduction off pre-period covariates
│   ├── cluster.py           # cluster-robust: aggregate to randomization unit before testing
│   ├── budget_split.py      # LinkedIn-style budget-split for auction/budget interference
│   ├── anytime_valid.py     # confidence sequences (asymptotic CS / mSPRT) for live peeking
│   ├── incrementality.py    # ghost-ads / PSA-holdout lift (treatment vs holdout)
│   ├── ope.py               # off-policy evaluation for ranking: IPS, doubly-robust
│   ├── hte.py               # heterogeneous effects (causal forest / metalearners) — ranking leg
│   ├── observational.py     # AIPW/DML + sensitivity to UNOBSERVED confounding (robustness value/OVB/E-value) [lyra/, NB 11]
│   └── switchback.py        # (Phase 3) region-time switchback estimator
│
├── validation/              # real-data leg — NOT simulated
│   └── criteo.py            # Criteo Uplift: run the same estimators on real incrementality data
│
├── serving/                 # (Phase 1.5/2) thin read API over metrics snapshots; replay clock
│
├── frontend/                # React + Recharts; replays the event log on a simulated clock
│
├── tests/                   # the test suite IS the causal credibility
│   ├── conftest.py          # fixtures: tiny seeded run, oracle-mode log reader
│   ├── test_recovery.py     # corrected estimator's CI covers ground_truth_tau at nominal rate
│   ├── test_naive_bias.py   # the naive estimator's bias is a measured, ASSERTED quantity
│   └── test_aa_null.py      # A/A must not flag; SRM within tolerance (EVENT_LOG §6)
│
├── notebooks/               # lab notebooks — the READ/EXPLAIN layer over the tested library
│   ├── nbtools.py           # thin shared helpers (style + config builders); no estimation logic
│   ├── 01_the_world.py      # engine walkthrough (paired .ipynb via jupytext)
│   ├── 02_money_shot.py     # naive bias vs allocation + budget-split recovery
│   └── 03_estimators_trust.py  # estimator forest, A/A nulls, ramp-selection confound
│                            # (notebooks import engine/inference; they never re-implement it)
│
├── paper-library/           # reading → first-person takeaways (see LITERATURE.md)
│   ├── pdfs/                # drop source PDFs here
│   └── papers/              # one processed note per paper, tagged, cross-linked
│
├── pm/                      # project management: progress, backlog, decisions, worklog
│
├── pyproject.toml           # package metadata + deps; installs `vega` + console script
├── Makefile                 # reproducible-by-command: make run / metrics / test / all
├── Dockerfile               # containerized run
└── .github/workflows/ci.yml # CI runs the test suite (recovery + naive-bias + A/A)
```

---

## Build order (mirrors CLAUDE.md "Current focus")

1. `engine/emit.py` — the writer enforcing EVENT_LOG §1/§3/§6.
2. `engine/market.py` tick loop emitting EVENT_LOG §2 in order; `config.py`, `agents.py`,
   `offers.py`, `choice.py`, `experiments.py` underneath it.
3. `metrics/models/staging/` — typed views; the `real` staging model drops `ground_truth_tau`.
4. `inference/naive.py` + `inference/cluster.py` (+ `budget_split.py`) and their recovery tests.
5. Ramp / interference-decay diagnostic (groups on `allocation`).
6. `inference/anytime_valid.py` → `cuped.py` → `incrementality.py`.
7. `validation/criteo.py` (real-data leg).
8. `frontend/` replay dashboard.

## Conventions

- **Config-driven.** Every number comes from `config.yaml` via `engine/config.py`. No literals.
- **Seeded.** `meta.seed` makes a run reproducible. Tests seed their own tiny runs.
- **Mode discipline.** `meta.mode: real` hides `ground_truth_tau` from metrics+inference; only
  `validation/` and `tests/` read it (oracle path). See EVENT_LOG §4.
- **Add an estimator in this order:** library module → recovery test → wire into metrics readout.
