# paper-library/

Reading → first-person takeaways we can **exploit** in the build.

| File | What it is |
|---|---|
| [INDEX.md](INDEX.md) | **The single reading list** — every doc (have `✅` + want `⬜`), by topic, foundational set, what each feeds, reading order, acquisition links. Start here. Supersedes the old `../LITERATURE.md` and `TO_ACQUIRE.md`. |
| [PROCESSING.md](PROCESSING.md) | How to read papers **without burning tokens** (PDF→markdown, chapter-by-chapter, optional cheap-LLM offload). |
| [notation/](notation/) | Estimators & math, summarized — canonical [NOTATION.md](notation/NOTATION.md) + one equation sheet per paper/topic. |
| [TEMPLATE.md](TEMPLATE.md) | The note template processed papers use. |

## Layout

```
pdfs/                       # source PDFs, organized by topic
  00-foundational/          # books + references (Wager, Causal ML book, Victor's homepage)
  01-causal-ml-dml/         # DML methods + package-docs/ (DoubleML, EconML)
  02-marketplace-interference/   two-sided-randomization/ · cluster-and-network/
  03-switchback/
  04-sequential-anytime-valid/
  05-power-and-decisions/
  06-evaluation-and-ranking/
  07-demand-pricing-and-llm-agents/
  08-personalization-and-platform-craft/
  09-long-term-and-surrogates/
  10-incrementality-attribution/   # JD-critical leg; placeholder (no PDFs yet)
  11-hte-metalearners-forests/     # GRF/causal forests + S/T/X/R/DR metalearners
md/                         # PDF→markdown conversions (text, committed) — read these, not the PDFs
papers/                     # processed notes (one per doc), cross-linked
notation/                   # estimators & equations, in canonical notation
```

## Workflow

1. Drop a PDF into the matching `pdfs/<NN-topic>/` folder (add a new topic folder if nothing fits;
   then list it in [INDEX.md](INDEX.md)).
2. Say the word, and each gets processed into `papers/<slug>.md` via [TEMPLATE.md](TEMPLATE.md):
   first-person takeaways, the **exact Vega module/decision it feeds**, cross-links (`[[slug]]`).
3. The note's `feeds:` field is the contract — every processed paper names what it changes in the
   code or design. If a paper feeds nothing, it doesn't belong in the MVP reading.

## Tagging

Reuse the taxonomy in LITERATURE.md, e.g.
`causal-inference, double-ML, switchback, marketplace, interference, cluster-randomization,
anytime-valid, sequential-testing, variance-reduction, incrementality, attribution,
off-policy-evaluation, HTE, evaluation, proxy-metrics, experimentation-platform, bayesian`.

## Status

45 docs catalogued across 12 topics (2026-06-02), incl. the Belloni-Chernozhukov DML classics and
the GRF/metalearner HTE cluster (§11: GRF, Künzel S/T/X, survlearners).
Foundational set + per-topic listing in [INDEX.md](INDEX.md). **Processed so far:** Wager book
ch.1–7, 10–13 → note in `papers/` + 9 equation sheets in `notation/` (ate-estimators, hte, dml,
interference, iv-late, adaptive-experiments, balancing, policy-learning, event-study-did). Pipeline:
[PROCESSING.md](PROCESSING.md) (chapter-by-chapter, text not images).
