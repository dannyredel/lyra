# study/ — visual study guide

A single self-contained HTML site that turns the dense `notation/` + `papers/` reference layers into a
**learning** layer: rendered LaTeX, intuition / pitfall / 🎯 Vega-hook callouts, SVG diagrams, collapsible proofs.

- **Open:** double-click [`index.html`](index.html) (or open in a browser). Needs internet — math renders via the MathJax CDN.
- **Navigate:** sidebar switches chapters; the in-page TOC + scroll-highlight track sections within a chapter.

## Coverage
**Tier 1 — the spine**
| Chapter | Folds in |
|---|---|
| 3 · Doubly Robust / DML | AIPW, weak/strong DR, cross-fitting, efficiency bound, Cor 3.3, **DML step-by-step (both scores, DML1/DML2), Double Selection, two-biases + estimator family** |
| 4 · Heterogeneous Effects | CATE, **S/T/X metalearners** (Künzel), R/DR-learner, **causal forests/GRF**, RATE/AUTOC |
| 5 · Policy Learning / OPE | AIPW policy value (OPE), policy comparison (ship decision), QINI/TOC, EWM |
| 11·12 · Interference | exposure mappings (H₀–H₄), HT/IPW, finite-pop variance → cluster-robust, ADE/AIE, marketplace |

**Tier 2 — foundations**
| Chapter | Folds in |
|---|---|
| 1·2 · RCT &amp; IPW | diff-in-means, interacted regression (= CUPED), unconfoundedness, propensity as balancing score, IPW, stratification, overlap |
| 10 · IV &amp; LATE | Wald estimand, 4 assumptions, LATE = compliers (+ types table), supply–demand IV, MTE, ghost-ads = encouragement |
| 13 · DiD &amp; event study | parallel trends, DiD, **TWFE staggered trap**, ASR/imputation, cohort-wise, SDID; panel-readout caution |

## Conventions
- **Equation colouring** — working via `\color[rgb]{…}` MathJax macros matching Daniel's Notion scheme
  (`\blue`=α · `\green`=outcome · `\pink`=treatment · `\purple`=y-residual · `\orange`=raw d · `\gray`=prelim).
  Applied across DR (AIPW, DML steps, two-biases, IV-type 2SLS) and HTE (R-loss, GRF); `[HTML]` model is
  unsupported — see [`../PROCESSING.md`](../PROCESSING.md) → "Equation colouring". Procedure for new papers: same file → "Output layers".

## Relationship to the other layers
This is the *pedagogical* layer. Canonical reference stays in `../notation/*.md` (equations) and
`../papers/*.md` (prose takeaways); each chapter footer links back to its sheets. If the math changes, fix
the `.md` first, then mirror here.

**Tier 3 (not yet built):** adaptive experiments (ch.6), balancing estimators (ch.7).
