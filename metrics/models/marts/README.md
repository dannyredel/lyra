# marts/

The readouts the inference layer + dashboard consume:

- `experiment_readout` — per experiment/arm/day: primary metric (`margin_per_active_user` /
  `completions_per_user`), counts, effort.
- `guardrails` — advertiser ROAS, D7 retention, payout cost vs `metrics.guardrails` thresholds.
- `ramp_panel` — effect grouped by `allocation` (the interference-decay money-shot input).
- `srm` — realized vs intended arm shares (health flag).

These are tables (materialized) so the replay dashboard reads snapshots cheaply. (T-21)
