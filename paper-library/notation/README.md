# notation/ — estimators & math, summarized

A side project Daniel cares about: capture the **estimators and notation** (the actual math) from
each paper in a compact, reusable form — so the library is not just prose takeaways but a
**formula reference** we can lift straight into `inference/`.

## Structure

- **[NOTATION.md](NOTATION.md)** — the **canonical symbol table** (one notation to rule them all) +
  a **crosswalk** mapping each paper's symbols onto it. This is where we fight the
  notation-alignment problem: papers clash (treatment is `D` vs `W` vs `T`; propensity `e(x)` vs
  `m(x)` vs `π`). Pick one canonical set, translate everything to it.
- **One sheet per paper or topic** — `<slug>.md` from [_TEMPLATE.md](_TEMPLATE.md): the estimator,
  its score/moment, assumptions, variance/CI, and the **canonical-notation restatement**.

## Granularity decision

Per-paper sheet when the math is distinctive; **per-topic sheet** when several papers share one
estimator family (e.g. all DML variants in [dml.md](dml.md), all confidence-sequence forms in one
`anytime-valid.md`). A single global equations file would be unmanageable — and aligning notation
across topics is hard, so we align *within* a topic first and reconcile in NOTATION.md.

## Convention

- Always give the equation **twice**: once in the paper's own notation (so it's checkable against
  the source), once **restated in canonical notation** (so it composes with the rest of the library
  and with Vega's `EVENT_LOG.md` fields).
- Tag each estimator with the Vega module it feeds (`inference/<x>.py`), same as INDEX.md.
- Notation alignment is explicitly a **"good enough now, reconcile later"** effort — flag clashes in
  NOTATION.md's crosswalk rather than blocking on a perfect unified scheme.
- **Write math as LaTeX in markdown** — inline `$...$`, display `$$...$$`, `\mid` inside tables
  (e.g. `$m(X)=E[W\mid X]$`). Renders in GitHub and the VS Code preview (KaTeX).
