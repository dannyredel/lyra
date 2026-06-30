# BACKLOG.md — Vega

Prioritized queue of work not yet on the PROGRESS board. When an item is scheduled, move it to
PROGRESS.md (give it a `T-NN`) and leave a pointer here. Priority: P0 (next) · P1 · P2 · P3 (someday).

## P0 — portfolio / publishing (live as of 2026-06-30)
Live: **app** https://lyra-five-sable.vercel.app · **guide** https://lyra-docs-chi.vercel.app · **repo**
https://github.com/dannyredel/lyra · Vercel **auto-deploy** on `git push` (app root dir = `frontend`).
- **B-40 — Live backend (FastAPI → Render)** so create→run→decide runs online. **Plan written:
  [`pm/live-backend-plan.md`](live-backend-plan.md)** — execute next session. The static demo stays the fallback.
- **B-41** Docs auto-deploy via a GitHub Action (install Quarto → `quarto render docs` → deploy `_site` to the
  `lyra-docs` Vercel project with a token). Today the docs deploy manually (`cd docs/_site; vercel --prod`).
- **B-42** (minor) Commit attribution: commits show GitHub user `dannyredel-tech` (the email
  `dannyredel@gmail.com` is linked there, not to `dannyredel`). Repo is correctly under `dannyredel`. Fix only
  if the avatar bothers you — point `git config user.email` to an email verified on `dannyredel`.
- **B-43** Custom domain — **declined** (staying on `*.vercel.app`).
- ⚠️ **Watch-out (resolved B-39):** never let a broad `data/` gitignore rule (or build-output ignores) swallow
  `frontend/public/data/chassis.json` — the git build needs the static snapshot committed or the deployed app
  hangs on skeletons. Negation added in `.gitignore`.

## P1 — fast-follows once the MVP spine exists
- **B-01** Power/MDE calculator off the choice model (trivial since we control N). — PROPOSAL §7
- **B-02** SRM check as a reusable diagnostic + dashboard health flag. — EVENT_LOG §6
- **B-03** Auto-rollback / kill-switch on guardrail breach during ramp. — PROPOSAL §7
- **B-04** Decision framework: explicit ship/no-ship rules + guardrail thresholds. — PROPOSAL §7
- **B-05** Calibration self-check: compare aggregate outputs to `calibration.*` anchors, warn on drift.

## P1 — fast-follows (cont.)
- ✅ **B-06 (DONE 2026-06-03)** **Cluster-level interference** — added a per-cluster random-effect
  intercept on utility (`agents.cluster_effect_sigma`, D-15) → within-cluster ICC ≈ 0.02, so a
  cluster-randomized design's naive (user-level) SE is understated and cluster-robust SEs correct it
  (~1.3× wider). `tests/test_cluster.py` asserts it (and that user-randomized SEs are unaffected — the
  Glovo asymmetry). Remaining for the **full Game-B leg**: a *cluster-contained resource* + a real
  ranking lever so cluster-randomization fixes a point-estimate *bias* (not just the SE) → new item B-07.
- **B-07** Game-B ranking leg: real ranker lever + cluster-contained attention/budget so
  cluster-randomization recovers the ATE where user-randomization is biased (the cluster money shot).
  Pairs with OPE (B-10) on the logged propensities. — PROPOSAL §5

## P2 — Phase 2 depth (still Almedia)
- **B-10** OPE depth on ranking: IPS + doubly-robust, policy-value vs ground truth. — `inference/ope.py`
- **B-11** HTE / CATE: causal forest + S/T/X-learners on the ranking leg. — `inference/hte.py`
- **B-12** Eval funnel for Game B: simulated noisy proxy score → calibrate vs ground-truth tau. — D-09
- **B-13** Portfolio FDR (BH) across concurrent experiments + collision matrix. — config `multiple_testing`
- **B-14** Layered/overlapping assignment (Google-style) scaling to 20–50 experiments.
- **B-15** Surrogate / long-term-effect estimation (90-day reward case). — config `metrics.horizons`
- **B-16** Streaming mode (FastAPI) as an optional showcase behind the replay adapter.
- **B-17** Interleaving as a more sensitive ranking-eval method for Game B. — Schultzberg & Ottens

## P3 — Phase 3+ other verticals (reuse the spine)
- **B-20** Glovo (delivery): switchback + cluster randomization. — `inference/switchback.py`
- **B-21** Trivago (auction): bid-equilibrium interference → budget-split.
- **B-22** Zalando (ranking): inventory/attention → cluster + uplift-decay diagnostic.

## Ideas / unsorted
- **B-30** Nested-logit variant of the choice model (resolve the open MNL-vs-nested decision).
- **B-31** Actually run the dbt project on BigQuery once (vs documented swap only).
- **B-32** Project rename decision (Vega vs alternatives).
