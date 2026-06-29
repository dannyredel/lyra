---
sheet: <paper-or-topic-slug>
covers: [<paper slug(s) from INDEX>]
feeds: [inference/<x>.py]
---

# <Estimator / topic> — equations

> Write all math as **LaTeX in markdown**: inline `$...$`, display `$$...$$`. Use `\mid` inside
> tables. Restate every equation in canonical notation ([NOTATION.md](NOTATION.md)).

## Setup / model
The data-generating assumptions in **canonical notation** (see [NOTATION.md](NOTATION.md)).

## Estimand
What parameter we target (e.g. `τ = E[Y(1) − Y(0)]`), in one line.

## Score / moment (paper notation)
Equation(s) exactly as written in the source — so it's checkable.

## Score / moment (canonical notation)
Same, translated. Note any symbol clashes resolved (update NOTATION.md crosswalk).

## Estimator
The computable form (e.g. cross-fitted residual-on-residual regression). Pseudo-formula is fine.

## Variance / CI
SE form, coverage claim, the `1−α` interval.

## Assumptions / failure modes
Where it's valid; what breaks it (and how Vega's sim stresses it).

## Vega hook
The `inference/<x>.py` function this becomes; the recovery test it implies.
