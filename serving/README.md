# serving/ — read API over metrics snapshots (Phase 1.5 / 2)

Thin, read-only API the frontend calls to replay the experiment on a simulated clock. Serves the
mart snapshots day-by-day (`snapshot_cadence_days`). In production the source is a broker; here it's
the recorded log replayed — swapping to live streaming is a thin adapter (FastAPI), not a rewrite
(PROPOSAL §9, D-01). Not needed for the first static-replay build; the dashboard can read marts
directly to start.
