"""Lyra chassis — the thin-but-real experimentation platform (LYRA §2; D-18).

The chassis wraps the deep `lyra/` inference engine with the boring-but-essential platform layers:
**assignment** (source-agnostic salted hashing) · the **experiment registry + lifecycle state machine** ·
the **DRAFT power-gate** · the **scorecard** (typed metrics + cluster-robust SEs + SRM + the state-gated
readout) — plus Lyra's superpower, the **ground-truth "certified" badge** (because Vega authors the DGP,
every readout is validated against a known truth). Design harvested in `papers/platform-engineering.md`.
"""
