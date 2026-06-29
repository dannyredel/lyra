---
title: "Platform experimentation — the operational A/B layer (synthesis)"
covers:
  - "Johari, Pekelis, Koomen, Walsh 2017 — Peeking at A/B Tests (Optimizely Stats Engine)"
  - "Kohavi, Linowski, Vermeer, …, Gelman, Imbens, Rajagopal 2026 — Power Analysis is Essential"
tags: [experimentation-platform, A/B, sequential-testing, anytime-valid, power, MDE, SRM, FDR, guardrails]
feeds: [inference/anytime_valid.py, power/MDE calculator, EVENT_LOG SRM, dashboard, decision framework]
related: [[anytime-valid]], [[power-mde]], [[interference]], [[adaptive-experiments]]
status: processed
read_on: 2026-06-02
---

# Platform experimentation — the operational A/B layer

**The gap (Daniel's call):** everything else we've processed — Wager, DML, HTE, interference, IV, DiD — is the
**inference engine**. This note is the missing **operations layer**: the actual practice and challenges of running
*many* A/B tests *continuously* on a platform. It's a distinct body of work (Optimizely / Microsoft / Spotify /
Booking engineering + Kohavi-Tang-Xu) and it *is* what Vega's dashboard + decision framework deliver.

## The operational challenges → papers → Vega deliverable
| Challenge (running A/B at scale) | Library papers | Vega module / deliverable |
|---|---|---|
| **Peeking** — users continuously monitor & stop early → Type-I inflation (→100% if you wait) | Johari 2017 ([[anytime-valid]]); Howard 2022; Spotify Peeking 2.0 (×2), Choosing-a-Framework | `inference/anytime_valid.py`; the dashboard **confidence-sequence band** (narrows over simulated days) |
| **Power / MDE / sample size** — online effects are *tiny* (median ~0.1–0.3%), so most "wins" are underpowered noise; winner's curse / Type-M exaggeration | Kohavi 2026 ([[power-mde]]); Gelman–Carlin 2014; Spotify Fixed-Power | power/MDE calculator (trivial since we set $N$); the **decision framework** (don't ship exaggerated noise); show the MDE–duration–power surface |
| **Sample size as a *decision*** — test small, roll the winner; maximize profit over a finite population (not significance) | Feit & Berman 2019; Kawato & Sakaguchi 2026 ([[test-and-roll]]) | the **ramp** ($n^*\propto\sqrt N$ / rule-of-thirds $m\approx N/3$); OEC = profit; reward-sizing decision |
| **SRM** (sample-ratio mismatch) — realized split ≠ designed split → experiment untrustworthy | Kohavi 2026; Fabijan et al.; Kohavi-Tang-Xu | **`EVENT_LOG.md §6.6` SRM invariant** + dashboard health flag |
| **Multiple testing / FDR** across many concurrent experiments | (config `multiple_testing: bh_fdr`); Spotify Risk-Aware (multi-metric) | portfolio **FDR + collision matrix** (Phase 2) |
| **Experiment collision / interference** — concurrent tests share users / budget | Wager ch.11–12 ([[interference]]); Johari 2021; Munro-Kuang-Wager | cluster/budget-split; the **ramp/interference-decay diagnostic** |
| **Ramp / sequential rollout** — A/A → 1% → 5% → 20% → 50% → ship, SRM at each step | (config `ramp_schedule`); Kohavi-Tang-Xu | the **ramp diagnostic** + auto-rollback / kill-switch |
| **Guardrails / OEC / decision** — ship/no-ship rules, guardrail breaches | Kohavi-Tang-Xu; Ng-Imbens (Bayesian decision); Spotify Risk-Aware | **decision banner** + guardrail thresholds (config `metrics.guardrails`) |

## First-person takeaways
- **Peeking is the headline operational hazard** (Johari 2017): with continuous monitoring, fixed-horizon p-values
  are *guaranteed* to cross any α if you wait — false-positive rate → 100%. The fix is **always-valid** inference
  (p-values / confidence sequences valid at *any* stopping time). This is the methodological spine of Vega's live
  dashboard, and it lives in the **time** dimension — the CI narrows as simulated days accumulate, peeking-safe.
- **Power is the silent killer** (Kohavi 2026): online effects are ~0.1–1%, so a properly-powered test needs
  *millions* of users; a "significant" result from a small test is usually **winner's curse** — Gelman–Carlin
  Type-M *exaggeration* of 28×–200× at 3% power. Vega can *prove* this: because we know ground-truth $\tau$, the
  underpowered-significant-overstates-effect story is a measurable, assertable quantity (pairs with the naive-bias thesis).
- **Trustworthiness guardrails** (SRM, etc.) come *before* the readout — a 44:56 split when you designed 50:50 is a
  $10^{-460}$ event → the experiment is invalid, full stop. Vega already encodes SRM as an emitter invariant.
- **"Significant" ≠ "true":** with a ~10% base rate of real effects, α=0.05 and 80% power, a significant result is a
  **false positive ~22% of the time** (false-positive risk). The decision framework must reflect this, not just p<0.05.

## Why this matters for the JD / thesis
The target role is a *founding DS building the measurement stack*. The methods (DML, interference) prove causal
validity; **this operational layer proves you can run the platform** — peeking-safe monitoring, power discipline,
SRM/guardrails, FDR across a portfolio, ramp. Vega's dashboard screens (portfolio, experiment detail with the CS
band, ramp diagnostic, health flags) *are* this layer made visible.

## Acquire — the platform cluster
**Power (INDEX §05):** Gelman–Carlin 2014 (Type S/M) · Cohen 1988/1992 · Button et al. 2013 · Simonsohn 2015
(small telescopes) · Benjamin et al. 2017 (α=0.005) · Deng–Knoblich–Lu 2018 (Delta method) · Azevedo et al. 2020
(A/B fat tails) · van Belle 2008 · **Kohavi–Tang–Xu 2020 (the bible)**.
**Sequential (INDEX §04 — mined from the Spotify blogs, fetched live):** **Lan & DeMets 1983** (alpha-spending) ·
**Jennison & Turnbull** *Group Sequential Methods* (book) · **Lindon–Malek–Zhang 2022** mSPRT (arXiv:2210.08589) ·
**Nordin & Schultzberg 2024** Fixed-Power (arXiv:2405.03487) · **Larsen et al. 2024** *Statistical Challenges in OCEs:
A Review* · Wald 1945 (SPRT) · Guo & Deng 2015 · longitudinal: Liang–Zeger 1986, Diggle et al., Shoben 2010.

## Cross-links
Equations: [[anytime-valid]] (peeking / always-valid / mSPRT / CS), [[power-mde]] (sample size, MDE, SRM, Type S/M).
Method ties: [[interference]] (collision), [[adaptive-experiments]] (bandits also break IID inference), [[dml]] (CUPED → power).
