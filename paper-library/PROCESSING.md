# PROCESSING.md — reading papers without burning tokens

**The core problem:** the assistant's PDF reader renders each page as an **image** (vision tokens).
A 300–400 page book (Wager, Causal ML book) read that way costs *tens of thousands* of tokens and
degrades math fidelity. Reading **plain text / markdown** is ~10× cheaper and exact for equations.

**The one rule:** convert each PDF to markdown **once**, commit the `.md`, and from then on only ever
read the `.md`. Never re-read a big PDF through the image reader.

## "If I convert to markdown, will I lose the equations?" — yes, partly, with pymupdf

Honest answer: **`pymupdf` / `pymupdf4llm` extract the text layer, and academic PDFs do *not* store
equations as LaTeX** — they're typeset glyphs (often custom font encodings). So display equations
come out **approximate or garbled** (subscripts flattened, symbols dropped/unicode-mangled). Prose,
section structure, and tables survive well; **the math does not reliably survive.**

So the plan splits by purpose:
- **Prose / summaries / takeaways** → `pymupdf4llm` is fine (and cheap). Use it for the `papers/` notes.
- **Equations we actually need** → we **author them in LaTeX by hand** into the `notation/` sheets
  (we're doing that anyway — see `notation/dml.md`). For a faithful first pass, either:
  - run **Nougat** (Meta) or **Marker** — trained on arXiv, output Markdown **+ LaTeX** for math; or
  - run **Mathpix** (paid API, best-in-class PDF→LaTeX); or
  - do a **vision pass on just the equation-dense pages** (cheap model) → transcribe to LaTeX.

Bottom line: **`pymupdf` for the words, LaTeX-by-hand (or Nougat) for the math.** Don't trust
pymupdf's equation output; verify any equation against the source page before it lands in a sheet.

## Recommended pipeline (default)

1. **Convert → markdown** with a text extractor (no vision tokens):
   - `pymupdf4llm` — fast, free, good general layout + basic math. **Default.**
   - `marker` — better tables/layout/math (heavier install).
   - `nougat` — outputs **LaTeX for equations**; best for the `notation/` sheets, slower.
   - `pdftotext` (poppler) — plain text, zero-frills fallback.
2. **Split big books by chapter** (so we process one chapter per session and cap tokens):
   use the PDF's table-of-contents bookmarks → one `.md` per chapter.
3. **Store** under `paper-library/md/<topic>/<slug>/chapter-NN.md` (text, committed — small & reusable).
4. **Process chapter-by-chapter** into a `papers/<slug>.md` note + a `notation/<slug>.md` equation
   sheet. Read only the chapter `.md` you're working on.

Use `scripts/pdf_to_md.py` for steps 1–2 (see below).

## Optional: offload the bulk read to a cheaper LLM

For the heavy foundational PDFs, do the *first pass* (summary + equation extraction) on a cheap,
long-context model, then have the assistant (Opus) only read the distilled output to integrate:

- **Gemini Flash / Flash-Lite** — native PDF input, very cheap, huge context. Good for "summarize
  this chapter + list every estimator and its equation in LaTeX." Needs a Google API key.
- A **local** model (e.g. via Ollama) — free, private, slower; fine for OCR/summarize.

Pattern: *cheap model extracts → commits `chapter-NN.summary.md` + `chapter-NN.equations.md` →
Opus reads those (small) and writes the canonical-notation sheet + Vega hooks.* Reserve the
expensive model for synthesis and notation alignment, not raw reading.

## Output layers — the standard procedure (read → takeaways → equations → HTML)

The confirmed workflow for processing a paper/chapter. Produce up to **three output layers** (not every doc
needs all of them — blogs/minor papers may stop at takeaways; only Tier-1 / spine material gets the HTML):

1. **Convert + read** (the pipeline above) — PDF→markdown once, read the text not the page-images, chapter-by-chapter.
2. **Takeaways → `papers/<slug>.md`** — prose: one-line claim, per-chapter first-person takeaways, "how we
   exploit it → which `inference/` module," numbers worth stealing, an *acquire* list. The "why I care" layer.
3. **Equations → `notation/<slug>.md`** — the math in **LaTeX, canonical notation** ([NOTATION.md](notation/NOTATION.md));
   log any notation clash in the crosswalk; tag the `inference/<x>.py` each estimator feeds. The reference layer.
   **State the main assumptions explicitly** (econometrics-textbook style — a numbered list: e.g. SUTVA /
   unconfoundedness / overlap; rate conditions; parallel trends) in both the sheet and the study chapter.
4. **HTML study summary → `study/index.html`** (Tier-1 / high-relevance only) — distil the takeaways + key
   equations into a chapter of the study site: rendered math, callouts (💡 intuition · ⚠️ pitfall · 🎯 Vega hook),
   SVG diagrams, and **equation colouring via the colour macros** (see "Equation colouring" below). The *learning* layer.
5. **Update** INDEX (status ✅/⬜ + links), README, `pm/LOG.md`.

> Rule of thumb: `papers/` + `notation/` for everything we read; promote to `study/` only the spine. If the math
> changes, fix the `.md` first, then mirror into the HTML.

### Equation colouring (HTML) — WORKING METHOD
Two dead ends, then the fix:
- ❌ `\class{...}{...}` + `tex.packages:{'[+]':['color','html']}` — broke all typesetting (html ext / packages config).
- ❌ `\color[HTML]{RRGGBB}{...}` — renders **"Color model 'HTML' not defined"** (the `HTML` model is `xcolor`, not in MathJax's base `color`).
- ✅ **`\color[rgb]{r,g,b}{...}`** (floats 0–1, base `color` model, auto-loaded) — works. Define **Daniel's Notion
  macros** in the MathJax config so his equations paste verbatim:
  ```
  tex: { macros: { blue:['\\color[rgb]{0.431,0.659,0.996}{#1}',1], green:[...], pink:[...], purple:[...], orange:[...], gray:[...] } }
  ```
**Palette (Daniel's scheme):** 🔵 `blue` = target α · 🟢 `green` = outcome model (g, β, ε̂) · 🩷 `pink` = treatment
model (m, γ, û) · 🟣 `purple` = y-residual v̂ · 🟠 `orange` = raw d · ⚪ `gray` = preliminary α̃.

**This is the STANDARD for all study-site HTML** (confirmed rendering 2026-06-02). Applied across DR (AIPW score,
the DML step-by-step, the product-of-errors bias, IV-type 2SLS) and HTE (R-loss, causal-forest moment) — the same
colours thread "it's one orthogonal object." Rules: use sparingly + a one-line legend; reuse the exact colours so
they *mean* something. Because the macros match Daniel's Notion, **his equations paste in verbatim** — prefer that
over re-deriving. ⚠️ Keep `notation/*.md` **plain** — the macros are MathJax-config-only, so markdown/GitHub
viewers don't have them (colour lives only in the HTML layer).

## Quick decision guide

| Doc | Approach |
|---|---|
| Short paper (≤ ~15 pp), prose takeaways | `pymupdf4llm` → one `.md` → read it. |
| Math-heavy paper (estimators we'll implement) | `marker`/`nougat` → `.md` with LaTeX → `notation/` sheet. |
| Book (Wager, Causal ML) | split by chapter → process the **relevant** chapters only, one per session. |
| Equation-only need | Gemini/Nougat extract equations → `notation/<slug>.md`; skip full prose. |

## Install

```
pip install -e ".[papers]"   # pymupdf4llm + pymupdf  (see pyproject.toml)
# heavier/optional: pip install marker-pdf  ;  pip install nougat-ocr
```
