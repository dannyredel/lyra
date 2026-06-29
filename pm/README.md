# pm/ — Project management for Vega

Lightweight, plain-text project tracking. No external tool; these files are the source of truth
and travel with the repo. Four files, each with one job:

| File | Job | Update cadence |
|---|---|---|
| [PROGRESS.md](PROGRESS.md) | What's done / in-flight / next, organized by phase + build order. The status board. | Every work session |
| [BACKLOG.md](BACKLOG.md) | Everything not yet scheduled, prioritized. The idea/task queue. | When new work is identified |
| [DECISIONS.md](DECISIONS.md) | Running log of decisions (ADR-lite). Feeds CLAUDE.md "Decisions already made". | When a decision is made/changed |
| [LOG.md](LOG.md) | Chronological worklog — what changed, when, why. The narrative. | End of each session |

## Conventions

- **Status tags:** `TODO` · `WIP` · `BLOCKED` · `DONE` · `PARKED`.
- **IDs:** tasks are `T-NN`, decisions `D-NN`, backlog items `B-NN`. Stable; never reuse.
- **Dates:** absolute (`2026-06-02`), never "yesterday".
- **One change, one place.** When a decision lands, record it in DECISIONS.md and, if it changes
  the spec, update CLAUDE.md / PROPOSAL.md / STRUCTURE.md in the same change — don't let them drift.
- **Closing the loop:** a backlog item that gets scheduled moves to PROGRESS.md (leave a pointer);
  a finished task gets a LOG.md line.

## Definition of done (a task is `DONE` only when)

1. Code is config-driven (no magic numbers) and seeded.
2. It has a test where the spec demands one (every estimator → recovery test; A/A → no-flag test).
3. Layer boundaries respected (engine emits no results; inference never reads `ground_truth_tau`
   in `real` mode).
4. PROGRESS.md + LOG.md updated.
