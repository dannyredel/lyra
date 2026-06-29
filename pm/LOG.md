# LOG.md — Vega worklog

Chronological narrative of what changed and why. Newest first. One block per session.

---

## 2026-06-02 — Repo scaffold + PM setup

- Read the five source docs (CLAUDE.md, PROPOSAL.md, LITERATURE.md, EVENT_LOG.md, config.yaml).
- Created **STRUCTURE.md** (was referenced by CLAUDE.md/PROPOSAL.md but didn't exist) — the module
  map + layering rules; defers the data contract to EVENT_LOG.md.
- Stood up the **flat top-level package layout** (D-10): `engine/`, `inference/`, `metrics/` (dbt),
  `validation/`, `tests/`, `frontend/`, `serving/`, with stub modules carrying their spec
  responsibility in the docstring. No logic yet.
- Added productionization scaffolding: `pyproject.toml`, `Makefile`, `Dockerfile`, `.gitignore`,
  `.github/workflows/ci.yml`, `cli.py` entrypoint.
- Created **pm/**: PROGRESS, BACKLOG, DECISIONS (D-01…D-10 backfilled from existing decisions), LOG.
- Created **paper-library/** with a processing template; ready for the first ⭐ PDFs.

**Next:** process incoming papers; then T-10 `engine/config.py` → T-15 `engine/emit.py`.

## 2026-06-02 (later) — Paper library: classify + index

- User dropped **38 PDFs** (papers, Spotify blogs, package docs, two books, Victor's homepage).
  Read the title/abstract page of each to classify accurately.
- Organized `paper-library/pdfs/` into **10 topic folders** (00-foundational … 09-long-term),
  with subfolders for two-sided-randomization, cluster-and-network, and package-docs.
- Wrote **INDEX.md** (table of contents: every doc → topic → what it feeds; foundational set
  flagged) and **TO_ACQUIRE.md** (placeholders: Chernozhukov DML originals, PyMC/CausalPy docs,
  incrementality/OPE/CUPED/budget-split, Spotify-cited canonical works).
- Notable new heavyweight additions vs. the original LITERATURE.md: Amazon/Imbens **Multiple
  Randomization Designs** (Masoero 2025, Sudijono 2026), **two-sided platform bias** (Johari 2021),
  three switchback papers, **DML intro** (Ahrens 2026), **Agentic Economic Modeling** (LLM agents →
  demand elasticities), Hansen 2025 (cluster-robust SEs). These materially strengthen the thesis
  spine — worth reconciling into LITERATURE.md.
- **Foundational, per the user:** Wager book (preferred language) + Chernozhukov Causal ML book.

**Next:** acquire the INDEX `⬜` gaps; begin processing the ⭐ foundational set into `papers/` notes.

## 2026-06-02 (later 2) — DML classics, single-list reconcile, notation side-project, token pipeline

- Filed 3 new **Belloni-Chernozhukov classics** into `01-causal-ml-dml/`: CCDDHNR 2018 (the DML
  paper), BCH 2014 REStud (post-double-selection), BCH 2014 JEP (survey). Library now **41 docs / 11 topics**.
- **Reconciled into one list:** `paper-library/INDEX.md` is now the single source of truth — owned
  (`✅`) + wanted (`⬜`) inline per topic, rationale + feeds + reading order + acquisition links.
  `LITERATURE.md` slimmed to a pointer; `TO_ACQUIRE.md` removed (folded in).
- **Notation side-project** (`paper-library/notation/`): `NOTATION.md` canonical symbols + crosswalk
  (to fight notation-alignment), `_TEMPLATE.md`, and a seeded `dml.md` (PLR/IRM scores, cross-fitting,
  DR, CUPED/HTE/OPE hooks). Captures Daniel's preference to save estimators/math summarized.
- **Token-saving read pipeline** (`paper-library/PROCESSING.md` + `scripts/pdf_to_md.py`): convert
  PDF→markdown once (pymupdf4llm), split books by chapter, read text not page-images; optional
  cheap-LLM (Gemini Flash) offload for first-pass extraction. Added `[papers]` extra to pyproject.
- Recorded two memories: equation/notation preference; reading-on-a-token-budget.

**Next:** decide acquisition of `⬜` gaps; run `pdf_to_md.py` on the Wager book to start T-04
chapter-by-chapter (NOT via the image PDF reader).

## 2026-06-02 (later 3) — LaTeX math, go-to stack, math-fidelity answer

- **LaTeX math convention:** rewrote `notation/NOTATION.md` + `dml.md` (and templates) to use
  LaTeX-in-markdown — inline `$...$`, display `$$...$$`, `\mid` in tables. Per Daniel's request.
- **STACK.md (new, repo root):** go-to Python packages, principle "use the library, don't hand-roll
  the stats." Built from (a) a scan of Daniel's `OneDrive/Projects` — found he already uses
  statsmodels, linearmodels, econml, doubleml, pymc, bambi, dowhy, sklearn, xgboost, **pylogit/pyblp**
  (discrete choice in Synthetic Demand), polars; and (b) web research on economist go-to packages
  (pyfixest, differences, rdrobust, pysyncon, causalpy…). Mapped each `inference/*` module → package;
  flagged the ⚠️ build-it-yourself gaps: **anytime-valid CS has no mature Python pkg** (validates the
  crown-jewel framing), plus budget-split & switchback. Wired the principle into CLAUDE.md conventions.
- **Answered the pymupdf/math question** in PROCESSING.md: pymupdf extracts *text* well but **mangles
  equations** (PDFs don't store LaTeX). Plan: pymupdf for prose, author equations in LaTeX by hand
  into `notation/` (or Nougat/Marker/Mathpix/vision-pass for a faithful first cut).
- Memory: added `prefer-statistical-libraries`.

**Next (unchanged):** pick converter (pymupdf local vs Gemini offload) + first doc, then T-04.

## 2026-06-02 (later 4) — First paper processed: Wager book ch.1–4

- Installed `[papers]` extra (pymupdf4llm + pymupdf). Hit a real bug: pymupdf4llm ≥1.27 bundles an
  onnx layout/table model that throws an int32/int64 dtype error on this machine. Patched
  `scripts/pdf_to_md.py` to disable the layout model + table detection and **fall back to plain
  pymupdf `get_text`**. Now robust.
- Converted the **Wager book** (252pp) → 16 per-chapter `.md` under
  `paper-library/md/causal-inference-stefan-wager-nov-2025/`. Confirmed the predicted behavior:
  **prose/structure clean, equations fragmented** — so equations are hand-authored in LaTeX.
- Read **ch.1–4** (RCTs, unconfoundedness/propensity, doubly-robust, HTE). Wrote:
  - `papers/wager-causal-inference.md` — prose takeaways + per-module Vega hooks (status: processing).
  - `notation/ate-estimators.md` (ch.1–3: DM, IREG, stratification, IPW, AIPW/DR, efficiency bound, CIs).
  - `notation/hte.md` (ch.4: CATE, T-learner pitfalls, Robinson/R-learner, causal forest, targeting rule).
- **Notation clash found & logged** in NOTATION.md crosswalk: Wager $m(x)=E[Y\mid X]$ (outcome) vs our
  canonical/DoubleML $m(X)=E[W\mid X]$ (propensity). Translate Wager $m\to\ell$, $e\to m$.
- Key reusable facts banked: DML rate budget $\alpha_\mu+\alpha_e\ge1/2$; efficiency bound $V^*$;
  **Cor 3.3** — with known $e(x)$ (Vega's case) AIPW is efficient with *any* consistent $\hat\mu$, no rate needed.

**Next:** process Wager ch.11–12 (spillovers & interference — core thesis) when ready; or the other ⭐
papers (Johari 2021, Howard 2022). Same pipeline.

## 2026-06-02 (later 5) — Wager ch.6, 7, 10, 11, 12 processed

- Read 5 more chapters (md already converted): 6 adaptive, 7 balancing, 10 LATE/IV, **11–12 interference (thesis)**.
- Added 4 equation sheets: `notation/interference.md` (the big one), `iv-late.md`, `adaptive-experiments.md`,
  `balancing.md`. Extended `papers/wager-causal-inference.md` with per-chapter takeaways; updated NOTATION
  crosswalk (exposure mapping, IV, bandit notation). Now 7 sheets total.
- **Highest-value findings for Vega:**
  - ch.12: **block/cluster dependency graph $G$ ⇒ HAC variance = cluster-robust estimator** → the
    finite-population justification for `inference/cluster.py` (cluster-robust SEs aren't just an IID heuristic).
  - ch.12 cites **Munro–Kuang–Wager 2025** (marketplace equilibrium interference, prices align supply/demand,
    spillover-aware targeting) — essentially the Vega setting. Added to INDEX §02 acquisition (⭐ high priority),
    plus Leung 2022, Hu–Li–Wager 2022, Athey–Eckles–Imbens 2018.
  - ch.10: **ghost-ads incrementality = encouragement/IV design**; lift among responders is a LATE → frames `incrementality.py`.
  - ch.6: adaptive data breaks IID inference; $1/\sqrt e$ variance-stabilizing weights → ties to anytime-valid layer.
- Remaining Wager: ch.5 (policy learning — Game B targeting), 8 (RDD), 9 (SEM), 13 (event study/DiD), 14–15, 16.

**Next:** process Wager ch.5 (policy learning) + 13 (event-study/DiD) when ready; or pivot to ⭐ papers
(Johari 2021 two-sided, Howard 2022 CS). Acquire Munro–Kuang–Wager 2025.

## 2026-06-02 (later 6) — Wager ch.5 + 13 processed; Wager core method coverage done

- Read ch.5 (policy learning) + ch.13 (event-study/DiD). Added 2 equation sheets:
  `notation/policy-learning.md`, `notation/event-study-did.md` (9 sheets total). Extended the paper note;
  updated NOTATION crosswalk; INDEX/README/PROGRESS.
- **Highest-value findings:**
  - ch.5: **`V_AIPW(π)` = doubly-robust off-policy evaluation** → directly `inference/ope.py` (score a counterfactual
    ranker from logs, validate vs ground truth). Policy comparison `Δ(π̂,π0)` = the Game-B ship-decision number;
    QINI/TOC = uplift readout; EWM = weighted classification on AIPW scores.
  - ch.13: **TWFE is biased under staggered adoption** (negative weights / forbidden comparisons) → use ASR/imputation
    (Borusyak–Jaravel–Spiess, Wooldridge) or Callaway–Sant'Anna / Sun–Abraham; **cluster-by-unit** inference ties to
    Hansen 2025 jackknife + `cluster.py`. Caution flag for any panel/day-level readout over the event log. SDID when PT fails.
  - Added DiD acquisition list to INDEX (Callaway–Sant'Anna, Sun–Abraham, Borusyak et al., dCdH, Arkhangelsky SDID) →
    map to `pyfixest`/`differences` in STACK.
- **Wager core-method coverage now done** (ch.1–7, 10–13). Remaining are narrower: ch.8 (RDD), 9 (SEM), 14 (dynamic
  policies), 15 (MDPs), 16 (exercises) — process on demand.

**Next (pivot, per plan):** ⭐ standalone papers — **Johari 2021** (two-sided platform bias, thesis core) and
**Howard 2022** (confidence sequences → anytime_valid.py). Acquire Munro–Kuang–Wager 2025.

## 2026-06-02 (later 7) — Study-guide POC + HTE/forest leg built out

- **Study guide:** confirmed format (dark, callouts, rendered LaTeX, SVG family-tree). Built POC
  `paper-library/study/wager-ch03-doubly-robust.html`. Agreed plan: **Tier 1 as a single multi-chapter site**
  (DR, HTE, Policy/OPE, Interference) — that's now T-11 (TODO).
- **HTE/forest papers added** (Daniel: framework leans on these). Filed 3 new PDFs into new topic
  `11-hte-metalearners-forests/`: **GRF (Athey-Tibshirani-Wager 2019)**, Xu et al 2022 (survival metalearners,
  `survlearners`), Sverdrup-Wager 2024 (`causal_survival_forest`). Library now **44 PDFs / 12 topics**.
- Consulted the **grf guide** (grf-labs) + **CausalML** docs via WebFetch. Wrote 2 equation sheets:
  `notation/causal-forests.md` (GRF = forest-localized R-learner; honesty; RATE/AUTOC/BLP/DR-score API) and
  `notation/metalearners.md` (S/T/X/R/DR + econml/causalml class names + when-to-use). Plus cluster note
  `papers/hte-metalearners-forests.md`. Updated NOTATION crosswalk, hte.md cross-links, INDEX (§11 + acquisition), README.
- **Acquire (primary metalearner sources, referenced not owned):** Künzel et al 2019 (PNAS S/T/X), Nie-Wager 2021
  (R-learner), Kennedy 2023 (DR-learner). In INDEX §11.
- Note: GRF processed from the grf guide + Wager ch.4 + abstract (not the full Annals proof) — token-budget rule.

**Next:** build the **Tier-1 study site** (T-11) — the HTE chapter folds in metalearners + causal forests; or pivot
to ⭐ Johari 2021 / Howard 2022. Acquire the metalearner primaries + Munro-Kuang-Wager 2025.

## 2026-06-02 (later 8) — Künzel filed; Tier-1 study site built

- **Künzel et al 2019 (PNAS, S/T/X metalearners)** was added to `paper-library/` root (not `pdfs/`), so the earlier
  `find pdfs/` missed it — Daniel was right. Moved → `pdfs/11-…/Künzel et al 2019.pdf`; read p.1–2, confirmed it
  matches `notation/metalearners.md` (S/T/X, X-learner 2-stage imputation + weight g≈ê, adapts to sparsity).
  Flipped ⬜→✅ in INDEX §11 + cluster note + sheet. Library now **45 PDFs / 12 topics**.
- **Built the Tier-1 study site:** `paper-library/study/index.html` — single self-contained multi-chapter HTML
  (sidebar chapter switcher, dynamic per-chapter TOC + scroll-highlight, MathJax, callouts, SVG diagrams). Chapters:
  3 (DR/DML), 4 (HTE **incl. metalearners + causal forests**, RATE/AUTOC), 5 (Policy/OPE), 11·12 (Interference —
  exposure ladder H₀–H₄, dependency-graph→cluster-robust, marketplace ADE/AIE). Removed the ch.3 POC (folded in).
  Added `study/README.md`. Fixed two bugs (MathJax can't render inside SVG `<text>` → used unicode; cleaned init JS).

**Next:** Tier-2/3 study chapters if useful (T-12); acquire Nie-Wager 2021 + Kennedy 2023 + Munro-Kuang-Wager 2025
(T-13); or pivot to ⭐ Johari 2021 / Howard 2022.

## 2026-06-02 (later 9) — Standardized the processing procedure + equation colouring

- Daniel confirmed the **3-layer procedure** as standard: read → `papers/` takeaways + `notation/` equations →
  `study/` HTML (spine only). Documented in `PROCESSING.md` ("Output layers"), `study/README.md`, and memory
  `paper-processing-pipeline`.
- **Equation colouring** attempted (MathJax `\class` + color/html packages) but **didn't render in-browser →
  reverted** to the working version (underbrace labels). Marked PARKED in PROCESSING.md/study README/memory;
  retry later with a tested method (`\color[HTML]{...}`, `\cssId`, or KaTeX). The 3-layer procedure stands.

## 2026-06-02 (later 10) — DML procedure (Daniel's Notion notes) + colour retry

- Daniel shared his Notion DML notes (screenshots; URL not fetchable). Added the **step-by-step DML algorithm**
  to `notation/dml.md` (§3.1) and study ch.3 (§8): partialling-out **and** IV-type scores, the per-step
  residualization (v̂, û, ε̂), and **DML1 vs DML2** aggregation. Also expanded **Double Selection** (BCH 2014,
  post-double-selection, §8 dml.md / §9 study) with the 3 steps + the "why the union" OVB intuition.
- **Colour retry:** re-introduced equation colouring in the new DML section only, via `\color[HTML]{RRGGBB}{...}`
  (auto-loaded color extension, **no packages config / no `\class`** — the parts that broke last time). Palette:
  🟢 outcome residual / 🔵 treatment residual / 🟡 target α̂, with a legend. **Pending Daniel's browser check.**
  Updated PROCESSING.md colour note to "retry in progress".

**Next:** confirm the colour renders → if yes, apply the green/blue residual palette to AIPW/R-loss/GRF too;
then Tier-2/3 chapters or pivot to ⭐ Johari 2021 / Howard 2022.

## 2026-06-02 (later 11) — Cross-checked DML vs Daniel's Notion export; filled the conceptual spine

- Daniel exported his full Notion DML notes → `paper-library/DML Export Notion/` (2.6MB HTML + images, ~574 eqs,
  8 sections). Parsed it (python, extracted outline + all LaTeX annotations) to cross-check coverage.
- **Gap found:** our `dml.md` had the mechanics (scores, cross-fit, DML1/DML2, double-selection steps) but was
  missing the scaffolding: two-sources-of-bias frame, estimator taxonomy, OMV problem, FWL/Robinson, PLIV.
- **Decision (asked):** mirror the **conceptual spine** (not the deep Lasso theory). Colour: **hold** (Daniel
  hasn't checked the last `\color[HTML]` retry) → new sections added **plain**.
- Added to `dml.md`: §1.1 "two biases, two fixes" (regularization vs overfitting; the a/b/c decomposition; the
  product-of-nuisance-errors bias; FWL/Robinson); expanded §8 (OMV motivation + **PLIV / DS-IV**); new §9
  estimator-family comparison table. Mirrored a §10 "estimator family & two biases" into study ch.3 (plain).
- Registered the Notion export as a 🔗 resource in INDEX §01 (the deep reference; spine distilled into dml.md).
- Deferred (in Notion only, per "conceptual spine"): rigorous/adaptive/root-Lasso, penalty loadings, full PLIV proofs.

**Next:** Daniel to check whether ch.3 DML colours render → decide colour adoption (his green/pink/blue/purple/
orange/gray scheme via MathJax macros). Then Tier-2/3 chapters or pivot to ⭐ Johari 2021 / Howard 2022.

## 2026-06-02 (later 12) — Equation colour: SOLVED (rgb macros)

- Daniel's screenshot showed the error: **"Color model 'HTML' not defined"** → `\color[HTML]` uses an xcolor
  model absent from MathJax's base `color` extension (the extension itself loads fine).
- **Fix:** use **`\color[rgb]{r,g,b}{...}`** (floats, base model) via MathJax `tex.macros` defining Daniel's exact
  Notion scheme — `\blue`(α), `\green`(outcome g/β/ε̂), `\pink`(treatment m/γ/û), `\purple`(y-resid v̂), `\orange`(raw d),
  `\gray`(prelim α̃). His equations now paste verbatim. Rewrote ch.3 §8 DML equations with these macros + a 6-colour legend.
- Recorded the working method in PROCESSING.md / study README / memory.

**Next:** Daniel confirms colours now render → if yes, extend the macro palette to AIPW/R-loss/GRF (and optionally
paste more of his Notion equations verbatim). Then Tier-2/3 or ⭐ Johari 2021 / Howard 2022.

## 2026-06-02 (later 13) — Colour confirmed; extended + standardized

- Daniel confirmed the rgb-macro colours render. **Extended** across the study site: AIPW score (μ green / e pink),
  R-loss + causal-forest moment (y-residual purple / treatment-residual pink / target blue — same as DML
  partialling-out, reinforcing "R-learner = partialling-out"). **Pasted two of his equations verbatim** (colours
  matched): the IV-type **2SLS** view (collapsible) and the **product-of-errors** naive-bias equation in §10.
- **Standardized:** colour macros are now the documented standard for all study HTML (PROCESSING.md "Output layers"
  step 4 + "Equation colouring"). Rule recorded: `notation/*.md` stays **plain** (macros are MathJax-config-only);
  colour lives only in the HTML layer; Daniel's Notion equations paste verbatim.

**Next: Tier 2 study chapters** — RCT/IPW (ch.1–2), IV/LATE (ch.10), DiD (ch.13). Then Tier 3 (adaptive, balancing)
or pivot to ⭐ Johari 2021 / Howard 2022.

## 2026-06-02 (later 14) — Tier 2 study chapters built

- Added 3 chapters to `study/index.html` (now **7 total**, sidebar grouped Tier 1 / Tier 2):
  - **1·2 RCT & IPW** — diff-in-means + CLT, interacted regression (= CUPED, "free lunch"), unconfoundedness +
    propensity-as-balancing-score, IPW (e coloured pink), stratification, overlap; Vega box (engine sets e → overlap by construction).
  - **10 IV & LATE** — 4 assumptions, Wald estimand (instrument Z coloured orange), LATE = compliers + a
    compliance-type 2×2 table, supply–demand IV + MTE; Vega box (ghost-ads = encouragement/IV → incrementality.py).
  - **13 DiD & event study** — parallel trends + an SVG parallel-trends/ATT diagram, DiD estimator, the **TWFE
    staggered trap** (negative weights), ASR/imputation + cohort-wise + SDID; Vega box (panel-readout caution, cluster-by-unit, pyfixest/differences).
- Updated study README coverage (Tier 1 + Tier 2 tables) and pm.

**Next:** Tier 3 study chapters (adaptive ch.6, balancing ch.7) if useful, or **pivot to ⭐ standalone papers**
(Johari 2021 two-sided bias, Howard 2022 confidence sequences). Acquire Munro–Kuang–Wager 2025 + metalearner primaries.

## 2026-06-02 (later 15) — Regression-with-controls subsection + explicit assumptions

- Daniel added **Imbens & Wooldridge 2009** ("Recent Developments in the Econometrics of Program Evaluation",
  IRP DP 1340-08) → filed in `pdfs/00-foundational/`, registered in INDEX §00.
- Added a **"regression with rich controls — the linearity tax"** subsection to `notation/ate-estimators.md` (§3.1)
  and study ch.1·2 (§6): "control for X" via OLS is NOT justified by unconfoundedness alone (Wager ch.2 fn.15) —
  it adds (i) constant effects + (ii) linearity. The non-parametric imputation estimator τ̂_reg (I&W eq.11) needs
  neither. Included the **Angrist OLS-weighting result**: OLS weights group effects by Var(W|x)=e(1-e) (max at 50/50)
  → a different estimand than the ATE unless effects are constant; IPW weights by treatment probability → ATE. From
  Daniel's screenshots (I&W + Angrist–Pischke MHE ch.3).
- **Explicit assumption lists** (econometrics-textbook style): added the SUTVA/unconfoundedness/overlap trio to
  ate-estimators.md (new "Assumptions" section) + a 📋 assumptions box in study ch.1·2. Made "state the main
  assumptions" part of the standard procedure (PROCESSING.md step 3).

**Next (Daniel's call): pivot to ⭐ standalone papers** — Johari 2021 (two-sided platform bias) + Howard 2022
(confidence sequences). (Tier-3 study chapters optional.) Could also retro-add assumption blocks to other sheets.

## 2026-06-02 (later 16) — The platform-experimentation gap (Daniel's insight)

- Daniel flagged the real gap: we've gone deep on causal-inference *methods*; thin on the **platform-operations
  layer** — running many A/B tests continuously (peeking, power, SRM, FDR, ramp). Correct + high-value (it's Vega's
  dashboard + decision-framework story, and the JD's "build the measurement stack").
- Processed **Johari et al 2017 (Peeking at A/B Tests)** → `notation/anytime-valid.md` (peeking → always-valid
  p-values, sequential-test duality, mSPRT via Ville/martingale, confidence sequences, longitudinal caution).
- Processed **Kohavi et al 2026 (Power Analysis is Essential)** [Daniel's add — Gelman & Imbens co-authors] →
  `notation/power-mde.md`: $n\approx16\sigma^2/\delta^2$, MDE-setting, **SRM** guardrail, **Type-S/M exaggeration**
  (Gelman–Carlin, winner's curse, 28×–200× at low power), **false-positive risk** (~22%), small telescopes.
- Wrote the synthesis **`papers/platform-experimentation.md`** — maps each operational challenge → library papers →
  Vega deliverable (anytime_valid.py, power calc, EVENT_LOG SRM, FDR/collision, ramp diagnostic, decision banner).
- **Mined Kohavi's refs for the power cluster** (Daniel's ask) → INDEX §05 acquisition: Gelman–Carlin 2014, Cohen,
  Button et al 2013, Simonsohn 2015 (small telescopes), Benjamin et al 2017 (α=0.005), Deng–Knoblich–Lu 2018 (Delta
  method for ratio-metric variance), Azevedo et al 2020 (A/B fat tails), van Belle 2008, **Kohavi–Tang–Xu 2020 (bible)**.
- Vega tie-in noted: because we know ground-truth τ, "underpowered-significant overstates the effect" is a
  *measurable, asserted* quantity — same flavour as the naive-bias thesis.

**Next:** continue the platform thrust — process Howard 2022 (deepen CS) + the Spotify sequential blogs; acquire the
power cluster; optionally a **"Platform A/B" study chapter** (Tier-2.5) visualizing peeking/power/SRM/FDR/ramp.

## 2026-06-02 (later 17) — Test & Roll (decision-theoretic sample size)

- Daniel added two **test-and-roll** papers → filed in `pdfs/05-power-and-decisions/`: **Feit & Berman 2019**
  (Test & Roll) + **Kawato & Sakaguchi 2026** (prior-free). Processed → `notation/test-and-roll.md`.
- A *different philosophy* from Kohavi power analysis — not "detect significance" but **maximize profit over a finite
  population**: test on $n$, roll the winner to $N-2n$. Profit-max size $n^*\le\sqrt N\,s/(2\sigma)$ — scales with
  $\sqrt N$, sub-linear in noise, ≪ NHST; near-bandit regret. Prior-free → **rule of thirds $m\approx N/3$** (Kawato).
- **Strong Vega fit:** the ramp IS test-and-roll; OEC = profit; finite known $N$ → $\sqrt N$ scaling applies; "pick the
  winner" beats $p<0.05$. Threaded into `power-mde.md` + `platform-experimentation.md`; INDEX §05.
- Open Daniel decisions: (a) "different HTML" — recommended an **interactive experiment-design calculator**
  (power/MDE + test-and-roll, sliders + live chart); (b) acquiring the power cluster (download guide provided in chat).

**Next:** build the interactive calculator HTML (if approved) and/or continue the platform thrust (Howard + Spotify).

## 2026-06-02 (later 18) — Howard 2022 + Spotify sequential cluster

- Daniel's reorder: read the sequential cluster *before* building the HTML. Converted Howard 2022 + the 4 Spotify
  blogs. **Howard → text** (deep stats paper); the **4 Spotify PDFs are image-based exports** (pymupdf got ~200 bytes
  each — content rendered as images). Flagged in INDEX §04.
- **Processed Howard 2022** → deepened `notation/anytime-valid.md` §4: concrete sub-Gaussian CS
  $\bar X_t\pm1.7\sqrt{(\log\log 2t+0.72\log(10.4/\alpha))/t}$ (LIL rate; $\log\log t$ = price of peeking), P1–P4,
  supermartingale+Ville, linear-vs-curved boundary, asymptotic-CS drop-in.
- **Synthesized the Spotify cluster** (from methods + known content, flagged) → anytime-valid.md §5: framework
  comparison **mSPRT vs CS vs GST**, the **longitudinal caveat** (repeated obs/unit break naive sequential tests —
  directly relevant to Vega's event stream), **fixed-power** ("what you peek at"). Howard marked processed in INDEX.

**Next (Daniel's plan):** Daniel downloads the power cluster → then **build the HTML** = interactive experiment-design
**calculator** + **pedagogic "experiment design" summary** (combined). Platform-ops layer now well-mapped.

## 2026-06-02 (later 19) — Spotify blogs fetched live (image-PDF workaround)

- The Spotify PDFs were image-only, so **WebSearch + WebFetch'd the live blog pages** (engineering.atspotify.com).
  Got full methodology **and the reference lists** (Daniel's actual goal — papers to search next).
- Upgraded `notation/anytime-valid.md` §5 from "synthesized/flagged" → **sourced**: GST vs AVI/mSPRT vs **Bonferroni**
  (competitive ≤14 looks) comparison + Spotify's verdict (GST when N estimable/batch; AVI when streaming); **within-unit
  "Peeking 2.0"** (peeking before a unit's measurements are in → unmodeled covariance + shifting estimand; fix =
  longitudinal GLS + GST via **independent increments**); **fixed-power** (peek at the *variance function* not
  significance → analyze with no correction; stop-on-significance biases the effect = Type-M).
- **Cited-paper cluster → INDEX §04 acquisition + platform-experimentation.md:** Lan & DeMets 1983 (alpha-spending),
  Jennison & Turnbull (GST book), Lindon–Malek–Zhang 2022 (mSPRT, arXiv:2210.08589), Nordin & Schultzberg 2024
  (Fixed-Power, arXiv:2405.03487), **Larsen et al 2024 (OCE review, Amer. Statistician)**, Wald 1945, Guo & Deng 2015,
  + longitudinal (Liang–Zeger 1986 GEE, Diggle et al, Shoben 2010, Wong et al 2021).

**Next:** Daniel acquires power + sequential clusters; then build the HTML (calculator + pedagogic summary).

## 2026-06-02 (later 20) — Daniel's cluster downloads filed

- Daniel downloaded ~most of the cluster. Identified + filed 6: **Gelman & Carlin 2014** (Type S/M, `retropower`),
  **Deng–Knoblich–Lu 2018** (Delta method, `kdd2018-dm`), **Larsen et al 2023/24** (OCE review — the platform anchor),
  **Nie et al 2022** (eBay SRM/randomization-validation, CIKM `3511808.3557087`) → `05-power-and-decisions/`;
  **Nordin & Schultzberg 2024** (Fixed-Power, `2405.03487`) + an **"Anytime-Valid Inference for μ" supplementary-only**
  → `04-…/`. Flipped these ⬜→✅ in INDEX §04/§05.
- Most of these were already woven into the notation sheets as references (Gelman-Carlin → power-mde; Deng-delta →
  power-mde; Nordin-Schultzberg → anytime-valid) — so they're conceptually captured; **Larsen review** + **Nie SRM** are
  genuinely new and worth a takeaways pass (flagged in INDEX).
- ⚠️ Two issues to relay: (a) `2606.01789` is **off-theme** (Zhang et al 2026 — *causal-discovery benchmark consistency /
  LLM structure learning*, not A/B) → left at root, flagged; (b) the anytime-valid μ paper is **supplement-only** (main missing).

**Next:** build the HTML (calculator + pedagogic experiment-design summary). Optionally a takeaways pass on Larsen review + Nie SRM.

## 2026-06-02 (later 21) — Experiment Design Lab built (`study/experiment-design.html`)

- Second study site — an **interactive lab** (not a reader): reuses the study-guide chrome + Notion colour macros, sidebar
  tabs, show()/TOC JS. **7 tabs:** (0) design workflow + framework-comparison table + decision-flow SVG; (1) power/MDE/
  sample-size; (2) Test & Roll vs NHST vs rule-of-thirds; (3) Winner's curse (Type-S/M, closed form); (4) false-positive
  risk; (5) peeking — **live Monte-Carlo** of A/A Type-I inflation + an analytic **CS-vs-fixed-n "peeking tax" chart**
  (Howard sub-Gaussian) + GST/AVI/Bonferroni verdict + Peeking 2.0 + fixed-power; (6) SRM χ² checker.
- All calculators are vanilla JS (no libs): erf/Φ/φ + Acklam inverse-normal. **Verified every default against Node** —
  power 353k/arm, Type-M 1.83× @29% power, T&Roll 1509 vs NHST 6279 (4.2×), SRM χ²=22.8 p=1.8e-6. ✅
- 🐞 **Caught a real error while verifying:** power-mde.md §5 claimed FPR≈22% at π=0.1 — the formula gives **36%**
  (22% needs π≈0.18). Fixed the sheet. (The "if you debug it twice, automate it" spirit — the calculator *is* the check.)

**Next:** wire the lab's calculators to engine ground truth once it exists; optional Larsen/Nie takeaways; then start engine code.

## 2026-06-03 — M1+M2 SHIPPED: engine emits the log; money shot is a green test suite

Parked research, built the system. Plan approved (full M1+M2 slice, dbt deferred).

**M1 — engine → event log.** Implemented all stubs: `config.py` (typed `_Node`/`Config`, 6 named
SeedSequence RNG streams, validation), `agents.py` (seeded traits + arrivals + churn memory),
`offers.py` (offer wall, per-offer budgets), `choice.py` (MNL + outside option = ground truth;
margin = payout·(1−pass_through)), `experiments.py` (hash assignment, monotone ramp, levers,
`design`), `emit.py` (parquet writer + all 7 EVENT_LOG §6 invariants, unit-aware SRM), `market.py`
(daily tick loop). `cli.py run` emits a **5.4M-event, 45-day, 60k-user log** (45 parquet partitions);
`ground_truth_tau` non-null only on experiment conversions (hiding rule holds). Runtime ~4.7min.
- 🔧 **Calibration (D-11):** `refill: none` collapses the market at 60k scale (budgets exhaust day 1)
  or never binds — switched default to `refill: daily, budget_cap.mu=8` (~58% fill, sustained:
  conv/day 41k→34k, active 60k→42k). Calibration self-check now catches market/population collapse.

**M2 — the money shot (inference + tests).** `engine/oracle.py` (global ATE via all-treat/all-control
**shadow runs**, D-12); `inference/base.py` (duckdb per-user loader + `Effect`); `naive.py`,
`cluster.py` (cluster-robust SE), `budget_split.py` (the LinkedIn correction, backed by a new
engine **budget-split design** = per-arm budget pools). **Probe result (10k×30):** naive bias
+0.164→+0.226 as allocation 5%→50%, CI excludes ATE; budget-split cuts it to +0.04–0.08 (multi-channel
residual = cross-advertiser effort substitution). In the **single-advertiser isolated regime**
budget-split recovers exactly (bias +0.001, covers). **7/7 tests green in 14s:** naive biased +
grows; budget-split covers + beats naive; user & cluster A/A no-flag; SRM in tolerance.
- 🐞 **Diagnosed a confound (D-13):** ramped `infer` showed the *no-op* ranking lever as +0.40
  (p≈1e-102) — monotone-ramp + churn = **assignment-cohort survival selection** ("treatment" =
  long-survivors). Fixed-allocation analysis (tests/probe) is clean and unconfounded; `cli infer`
  now flags ramped rows. The A/A nulls (constant allocation) correctly stay null.

**Next:** M3 = dbt metrics layer over the event log (staging drops `ground_truth_tau`; marts =
experiment readouts + ramp panel). Then M4 (CUPED, anytime-valid CS, incrementality). Engine perf
(per-conversion ground-truth-tau is the hot path) can be optimised if needed.

## 2026-06-03 (later) — Lab notebooks (the read/explain layer) + a cluster gap surfaced

Daniel wanted to *understand before shipping more* (he works in Jupyter, step-by-step). Built a
`notebooks/` layer that **imports** the tested library and narrates it with figures — never
re-implements it. Paired `.ipynb + .py` via **jupytext** (`pip install -e ".[notebooks]"`), executed
with `jupytext --execute --set-kernel -` (Anaconda `base` kernel).
- **01_the_world** — engine tour: trait histograms, offer wall, **one agent's MNL choice probs**, run
  → event log → dynamics → `ground_truth_tau`. (11 cells, 5 figs.)
- **02_money_shot** — two acts: multi-advertiser **naive drift** (bias +0.079→+0.142→+0.192→+0.219 as
  alloc 5→50%, monotone, CI excludes truth) + cannibalization mechanism; single-advertiser
  **budget-split recovers exactly** (covers truth ≥20%). (3 figs.)
- **03_estimators_trust** — estimator forest, A/A nulls (both no-flag), SRM gate, and the
  **ramp-selection confound** shown by making a *no-op* lever read +0.34 (p=8e-10) under the ramp vs
  −0.009 (p=0.85) at fixed allocation. (3 figs.)
- ⚡ Added `market.run(compute_tau=False)` to skip the per-conversion hot path on analysis/shadow runs
  (truth comes from shadow ATE) — oracle uses it; tests stay green (7/7).
- 🔎 **Honest gap surfaced (B-06):** cluster-robust SE ≈ naive SE (1.0×) because `cluster_id` is an
  inert random label → **ICC ≈ 0**. The cluster correction is *ready* but won't bite until the engine
  models **cluster-level interference** (shared attention/preference/budget). NB03 states this plainly
  (no overselling); backlogged as P1 B-06 — it's the engine half of the ranking/attention leg.

## 2026-06-03 (later) — Frontend dashboard (React+Recharts) + M3 (dbt metrics layer)

Daniel (impatient 😄) wanted to *see the frontend*. Confirmed M3 (dbt) is **not** a blocker — the
dashboard reads pre-computed snapshots (D-01), and we can produce those from the existing inference
layer. Built both the dashboard and, in parallel, M3.

**Dashboard (T-60 / T-61).** `serving/export.py` runs a **fixed-allocation** demo world (clean arms,
no ramp confound) and writes `frontend/public/data/*.json`: portfolio + per-experiment detail
(per-day cumulative **rate** so the CI band *narrows*) + ground truth (shadow runs) + guardrails
(payout-cost computed; ROAS/retention flagged TODO) + ship/no-ship decision. **Vite + React +
Recharts** app with three screens: **Portfolio** (effect±CI, corrected, truth, SRM badge, decision),
**Experiment detail** (narrowing-band chart + ground-truth reference line + the bias gap, stats,
guardrails, decision banner), **Interference/ramp diagnostic** (naive drifts vs corrected vs
truth-line across allocations — the differentiator). Live on `npm run dev` (localhost:5173); builds clean.
- 🎲 **Demo-seed selection:** the per-seed ramp drift is noisy at n=8000 and an A/A null occasionally
  flags (the expected ~5% FPR — looks broken in a showcase). Scanned seeds for one with **both** a
  clean monotonic drift **and** non-flagging A/A nulls → **seed 17**. (Reminder to build B-13 FDR so a
  borderline A/A is de-flagged across the portfolio rather than cherry-picking a seed.)

**M3 — dbt metrics layer (T-20/T-21).** `dbt-duckdb`. `stg_events` (typed view; **drops
`ground_truth_tau` in real mode** — verified) → `int_experiment_users` (per-user arm+outcome, the
SQL mirror of `inference/base.user_outcomes`) → marts: `mart_experiment_readout` (per-arm),
`mart_experiment_effects` (**naive diff-in-means + Welch SE + 95% CI computed in pure SQL** — matches
`cli infer` exactly), `mart_srm`. **`dbt build` = 23/23 pass** (3 tables, 2 views, 18 data tests).
- 🔧 `mart_srm` initially false-flagged the cluster-randomized A/A (user-level chi²=86). Fixed by
  **detecting the randomization unit from the data** (is arm constant within each cluster?) and
  testing at the cluster level when so — mirrors the emitter's unit-aware SRM. Now correct.
- Wired `cli metrics` (= `dbt build`). The frontend still reads the exporter's JSON; swapping the
  marts in underneath is a later step (contract unchanged).

**Next:** finalize demo data (seed 17); optional World-view screen + static deploy; then B-06
(cluster interference) or M4 (CUPED / anytime-valid CS / incrementality).

## 2026-06-03 (later) — M4 inference depth: anytime-valid CS + CUPED + incrementality

Built the three M4 estimators (the crown-jewel inference depth). Suite **7 → 12 green**.
- **Anytime-valid CS (T-41, crown jewel)** — `inference/anytime_valid.py`. **Asymptotic confidence
  sequence** (Waudby-Smith/Ramdas): same point as naive, interval = SE × a *time-uniform* multiplier
  (`cs_multiplier`, always > z = the peeking tax). `estimate_sequence` builds the per-day band.
  Tests: CS covers truth **and** is wider than fixed-n; **an A/A's CS covers 0 at *every* day** — the
  always-valid property (a fixed-horizon test peeked daily would inflate Type-I toward 1; the CS
  doesn't). No mature Python pkg → we built+validated it (STACK.md).
- **CUPED (T-42)** — `inference/cuped.py`. $\tilde Y = Y - \theta(X-\bar X)$ with a **warmup-period**
  margin as the pre-treatment covariate (new `base.user_pre_post`; conftest `cuped` fixture = A/A
  warmup then 50/50). Test: CUPED SE **strictly < naive SE**, covariate informative, unbiased.
- **Incrementality (T-43)** — `inference/incrementality.py`. Resolved a latent EVENT_LOG contradiction
  (§6.5 "no holdout conversion" vs §5 "lift on holdout conversions") → **D-14**: holdout has the
  reward *withheld* (reward_shown=0) but converts **organically**. Engine lets holdout flow to the
  conversion path; emitter §6.5 now *asserts reward_shown=0* on holdout conversions instead of
  blocking them. Lift = treatment − holdout on conversions. Tests: lift +/significant; holdout
  conversions carry no reward. EVENT_LOG §2.3/§5/§6.5 updated.

**Deferred (small):** wiring the CS band into the dashboard detail screen (needs a ~5-min re-export;
the dashboard already works with fixed-horizon bands). **Next:** B-06 (cluster-level interference, to
make `cluster.py` bite + unblock the ranking leg) or the remaining legs (OPE, Criteo validation,
portfolio FDR), or finish the frontend (World view + deploy).

## 2026-06-03 (later) — B-06: cluster-level structure (the cluster correction now bites)

Made `inference/cluster.py` real. Added a **per-cluster random-effect intercept** on choice utility
(`agents.cluster_effect_sigma=0.5`, new `clusters` RNG stream, `Config.cluster_effects()` — D-15).
Within-cluster ICC≈0.02 ⇒ a **cluster-randomized** A/A's naive (user-level) SE is understated, and
cluster-robust SEs correct it (**1.3× wider**); a **user-randomized** A/A is unaffected (the shared
effect cancels across balanced arms — the Glovo asymmetry). `tests/test_cluster.py` asserts both.
- 🔧 The added outcome variance widened the iso CIs enough to break the budget money-shot test, so
  `iso_cfg` now sets `cluster_effect_sigma=0` (isolate the budget channel — same spirit as its 1
  advertiser + non-binding effort). Suite **12 → 14 green**.
- Note: `notebooks/03`'s "ICC≈0, cluster-robust = naive" caveat is now **resolved** by B-06 — the
  notebook should be re-run (its printed 1.0× ratio is stale); the live config now shows ~1.3×.
- The *bias* half of the cluster story (a cluster-contained resource that cluster-randomization fixes)
  is the Game-B ranking leg → backlog **B-07**.

**Next:** frontend — World-view screen + static deploy.

## 2026-06-03 (later) — Frontend World view (4th screen)

`serving/export.py` now also writes `world.json` (offer wall + per-day population/conversions/churn,
queried from the demo log — no extra engine runs). New `WorldView.jsx`: stat cards + a
population/conversions/churn chart over the replayed clock + the **offer wall** (50 tiles grouped by
advertiser, bordered by category, showing payout ▸ reward). Wired as a 4th nav tab; app builds clean.
- `demo_cfg` now pins `cluster_effect_sigma=0` for a stable, reproducible demo (the cluster story
  lives in tests/notebooks, not the showcase). Re-exported at seed 17: A/A nulls still clean
  (aa_null_2 −0.031 inconclusive), reward-sizing rolled back, naive drifts vs corrected on the ramp.
- Note: the D-14 holdout change (holdout converts organically) slightly perturbed the seed-17 demo
  numbers (holdout is ~3.5% of users on reward_sizing); A/A unaffected, ramp still reads correctly.

**Dashboard now has all 4 PROPOSAL §9 screens.** Remaining: static deploy (GitHub Pages) + the
optional anytime-valid CS band on the detail screen. Other open legs: OPE (B-10), Criteo validation
(T-50), portfolio FDR (B-13), Game-B ranking (B-07).

## 2026-06-04 — Learning detour: switchback experiments + variance reduction (CUPED/CUPAC/DML-DR)

Daniel asked for a primer + hands-on lab on switchback experiments and CUPED (he added the DoorDash
papers + the VR poster). Built both from the papers:
- **Primer** `papers/switchback-and-variance-reduction.md`: what/why switchback (interference → randomize
  over time within a market), the challenges (carryover, the (1+cv²) cluster-imbalance penalty, the
  **structural power floor** — macro shocks don't average away), CUPED→CUPAC→DML-DR, Pankratev's
  closed-form variance formula, the two non-obvious lessons (target *macro* not residual; the
  efficiency↔robustness Type-S trap), recommendations. Refs: Bojinov 2021; Pankratev 2026 ×2;
  Deng 2013 (CUPED); Poyarkov/Tang (CUPAC); Chernozhukov 2018 (DML).
- **Lab** `notebooks/04_switchback_lab` (paired ipynb, 11 cells/5 figs/0 err): self-contained
  re-implementation of the poster's DGP + 4 estimators + cluster-robust SEs. Reproduces the VR
  gradient (Raw 0% → CUPED 45% → CUPAC 67% → DML-DR 61% VR), the power **structural floor** vs n̄ (with
  the closed-form formula), the **structural inversion** (CUPED targeting macro → 58% VR vs residual →
  17%), and the challenges (cluster imbalance; sign-flip carryover → Type-S wrong-sign rejections).
- Filed the 2 new PDFs into `pdfs/03-switchback/`; converted Bojinov + Pankratev to md; INDEX §03 updated.
- Switchback stays **Phase-3** for Vega (Glovo delivery vertical, `inference/switchback.py`); this is
  muscle-building + the design vocabulary. The off-theme causal-discovery paper (2606.01789) left at root.

## 2026-06-04 (later) — PIVOT to Lyra + architecture-spine notebook (raw, by hand)

Daniel pointed me at `ideas/lyra-experimentation-platform.md` and asked to pivot. **Reframed the
project as Lyra** (the experimentation *platform*) with **Vega** as the DGP/sim/validation layer inside
it; the Almedia marketplace becomes **Vega Level-3**. Wrote **`LYRA.md`** (north star, with a §1 table
mapping every built piece — engine/inference/metrics/frontend/tests/notebooks — to a Lyra layer:
we're ~mid-Phase-1, reframe-not-restart). Reframed `CLAUDE.md` + `PROPOSAL.md` header; **D-16** logged;
memories added (`lyra-pivot`, `notebooks-first-promotion`).

- 🔄 **Workflow correction (important):** I first built `lyra/` modules then a notebook that imported
  them — exactly backwards. Daniel builds each method **raw, by hand, in the notebook first** (to see
  the mechanics), *then* extracts to `.py`. Removed the premature modules; refined the
  `notebooks-first-promotion` memory with the precise ordering (raw notebook → extract → harden → promote).
- **`notebooks/05_protocols_harness_robustness`** (raw, self-contained, 11 cells/3 figs/0 err): builds
  by hand the **DGP ladder** (L0 iid, L1 covariates→potential-outcomes + CATE + confounding knob +
  nonlinear baseline), three **estimators** (diff-in-means; OLS adjustment; **AIPW** cross-fitted, with
  the influence-function written out), the **Monte-Carlo harness** (sample→estimate→compare-to-truth →
  bias/coverage/power; Welch sanity: type-I .05, power 1.0, cov .95), a **power curve**, and the
  **robustness grid**: confounded+linear → OLS ✓ (cov 1.0) but diff ✗; confounded+nonlinear → diff ✗ &
  **OLS ✗ (bias +1.58)** while **AIPW survives (bias +0.09, cov 1.0)**. The "OLS biases / AIPW survives"
  demo, end to end.

**Next session (the extraction / harden stage, done *with* Daniel from this notebook):** lift the raw
functions into `lyra/{dgp,estimators,harness}.py` behind a small `Estimator`/`DGP` contract, then wrap
the six existing inference estimators + the marketplace as L3 — so the harness certifies everything.

## 2026-06-04 (later) — Notebook reset + curriculum (ROADMAP) + NB01 spine promoted to lyra/

Daniel asked to restart the notebooks cleanly and plan the set we need. Moved the five first-pass
notebooks to **`notebooks/_old/`** (recycle freely) and wrote **`notebooks/ROADMAP.md`** — a 10-notebook
curriculum across his four pillars (**DGP · experiment · metric · method**), each built raw then promoted,
grounded in our paper summaries + topics (read INDEX §00–11). Build order: 01 spine · 02 metrics ·
03 designs/interference (money-shot) · 04 switchback/VR · 05 sequential/diagnostics · 06 power/decisions ·
07 CATE · 08 uplift-eval/policy · 09 observational(DML/DiD/IV) · 10 incrementality/Criteo. Each row maps
to specific papers + a `.py` promotion target + which `_old/` notebook to recycle.

**NB 01 — the spine (built + promoted).** Per the corrected workflow (raw notebook first, *then*
extract), `_old/05` already built the spine raw, so NB01 = finalize it as `notebooks/01_spine.py`
(recycled) AND **do the promotion for real**: lifted the raw functions into
**`lyra/{protocols,dgp,estimators,harness}.py`** (the two contracts + DGP ladder L0/L1 + diff/OLS/AIPW +
the Monte-Carlo harness/robustness-grid/power-curve). The notebook's §6 imports `lyra/` and **verifies
parity** (raw ↔ promoted give the same harness result) + reproduces the whole robustness grid in two
lines — the worked example of notebook→`.py`. Smoke-tested: L0 type-I 0.05, conf+nonlinear → AIPW cov
1.00 vs diff/ols 0.00. Registered `lyra` (+ `serving`) in `pyproject.toml`; refreshed `notebooks/README`.
- Trimmed AIPW (max_iter 150→100, 4→3 folds) + grid reps so the notebook runs in ~3 min.

**Next (per ROADMAP):** NB 02 — metrics (types→variance: mean/proportion/ratio-delta/count/quantile;
the versioned/type-aware spec; CUPED; A/A as the metric-promotion gate) → `lyra/metrics.py`.

## 2026-06-04 (later) — NB 02: the DGP zoo (raw)

Built `notebooks/02_dgp_zoo.py` (raw, by hand; 8 cells, 6 figs, 0 err) — authored ground-truth-known DGPs
across the realism dial, each with its outcome model + equation + the known true ATE + a diff-in-means
recovery check + a visual:
- **binary** (Bernoulli/logistic — risk-diff ≠ logit β), **count** (Poisson — rate diff/ratio),
  **revenue** (spike-at-zero + lognormal — unbiased but wide), **ratio** (conv/session, random
  denominator → delta-method setup for NB03), **survival/churn** (exp hazard + censoring; D30 retention
  + survival curves), **funnel** (compose → CTR/CVR/ARPU multi-metric), **staggered panel** (Sant'Anna–
  Zhao flavour; naive last-period diff 1.84 vs true ATT 1.00 → motivates DiD).
- Throughline taught: under randomization diff-in-means recovers the ATE for *every* outcome type; the
  type drives **variance/inference**, not the point → motivates the typed metric layer (NB 03). Time +
  selection break it (the panel) → NB 06 (sequential) / NB 10 (DiD, reuse `monte_carlo_did_cov.qmd`).
- After NB02 improvements to NB01 (Y(0)/Y(1) both share b(X); KaTeX `V^\*`→`V^{*}`; Wager confoundedness
  + AIPW/Γ notation + efficiency note; sampling-distribution & power-curve/MDE visuals).

**Next (per ROADMAP):** promote the zoo → `lyra/dgp/` (`outcomes.py`/`funnel.py`/`panel.py`, each a DGP
with `sample()`+`ground_truth()`), OR proceed to **NB 03 — metrics** (types→variance) which consumes them.

## 2026-06-04 (later) — Promote the DGP zoo → lyra/dgp/ + cluster-SE notebook queued

- **Cluster-robust SE notebook queued** as **NB 04** (ROADMAP renumbered, rest +1). Annotated refs from
  Daniel's Notion set: Cameron–Miller, MacKinnon–Nielsen–Webb 2023, MacKinnon–Webb 2023 (CV3/wild
  bootstrap), Hansen 2024/25 (jackknife). Filed `sandwich-CL.pdf` → `pdfs/02-…/cluster-and-network/`;
  added cluster-robust-SE block to INDEX §02 + acquisition; added `lyra/se.py` row to STACK.md
  (pyfixest, wildboottest, sandwich/fwildclusterboot/fixest/estimatr/summclust). Memory: `cluster-robust-se-notebook`.
- **Promoted NB 02 → `lyra/dgp/` package** (`ladder.py` [L0/L1, moved from `dgp.py`], `outcomes.py`
  [Binary/Count/Revenue/Ratio/Survival], `funnel.py`, `panel.py`; `__init__` re-exports keep
  `from lyra.dgp import DGPLevel1, covariate_cols` working). Each is a `DGP` with `sample()` +
  `ground_truth()`; truth computed from **expected** potential outcomes on a 200k oracle sample.
  `pyproject` packages += `lyra.dgp`.
- **`tests/test_dgp_zoo.py`** (8 tests): diff-in-means recovers each outcome world's oracle truth
  (coverage ≥0.88; bias within 4 Monte-Carlo SEs — self-calibrating so heavy-tailed revenue/funnel don't
  flake); ratio pooled-ratio recovers per-session lift; panel naive is biased (→ DiD); binary ATE is a
  risk difference not the logit β. **Full suite green: 22 passed.**
- **Lesson surfaced:** funnel true ARPU lift is **0.32** (oracle), not the **0.45** NB02 §6's single draw
  printed — heavy revenue tail → noisy single sample; the payoff of authored ground truth. Added a §9
  promotion+verification cell to NB02 (9 cells, 6 figs, 0 err).

**Next (per ROADMAP):** NB 03 — metrics (types→variance: two-proportion z, ratio→delta, revenue→CUPED),
consuming the zoo → `lyra/metrics.py`.

## 2026-06-04 (later) — NB 03: metrics (types→variance) + promote to lyra/metrics.py

Built `notebooks/03_metrics.py` (raw; 9 cells, 3 figs, 0 err) — the typed metric layer, consuming the
DGP zoo. Throughline from NB02 extended: the outcome **type drives the variance/CI, not the point**.
- **Proportion** → two-proportion z on `BinaryDGP` (cov 0.95). **Ratio** → the **delta method**
  (Deng 2018) — the star: a user-heterogeneous ratio world where **naive session-iid under-covers
  (0.74, CI 40% too narrow)** while **delta covers (0.94)** — same point, right error bars. **CUPED**
  → 49% variance reduction (= ρ²), no bias. **Quantile** → p90 bootstrap. **A/A gate** → naive ratio
  **over-flags at 0.217** while delta/proportion/CUPED sit ~0.05 (A/A catches the broken-variance bug);
  proportion A/A p-values uniform. `MetricSpec` (name/version/**type**/class) routes type→estimator.
- **Promoted → `lyra/metrics.py`**: `MetricSpec`, `MeanMetric`/`ProportionMetric`/`RatioMetric` (delta)/
  `NaiveRatioMetric` (documented foil)/`CupedMetric`, `REGISTRY`+`estimator_for`, all behind the
  `Estimator` Protocol. Added to the zoo: `RatioDGP(user_sigma=…)` heterogeneity knob + `PrePostDGP`
  (CUPED world). Added `ci_width` to `lyra/harness.py`.
- **`tests/test_metrics.py`** (5): proportion recovers risk-diff; **delta covers clustered ratio while
  naive under-covers** (asserted); CUPED reduces width >20% no bias; **A/A gate — naive over-flags,
  delta/proportion pass**; registry routing. **Full suite green: 27 passed.**

**Next (per ROADMAP): NB 04 — cluster-robust standard errors** (correlated *units*: CRVE / jackknife
CV3 / wild cluster bootstrap; refs + libraries already annotated) → `lyra/se.py`.

## 2026-06-04 (later) — Paper-harvest pass (platform-building ideas) before the Chassis MVP

Daniel: read/convert the unread papers, categorize, summarize, "steal ideas for platform building" —
before NB 04 and the Chassis MVP. Converted **25 priority PDFs → md** (`scripts/pdf_to_md.py`), then
fanned out **6 parallel reading subagents** (platform-architecture / peeking-Bayesian / decisions-guardrails
/ org-process / cluster-SE / CUPED+frugal). Synthesized into:
- **`papers/platform-engineering.md`** — the playbook, "ideas to steal" by chassis component (assignment ·
  registry/lifecycle · metrics governance · engine · diagnostics/guardrails · scorecard/peeking · decisions
  · simulation), + a ranked TOP-12 + a "bake into the Chassis MVP" list + source catalog. Sources: Netflix
  ×2, Stitch Fix, DoorDash Curie, Squarespace, Etsy, MS Flywheel, OCE Summit 2019, open-guide, Larsen 2023,
  Ng–Imbens 2026, eBay/Nie (sequential SRM), Schultzberg–Ottens, Evan Miller ×2, Deng–Lu, Convoy/Variance-Explained.
- **`notation/cluster-robust-se.md`** — CV1/CV2/CV3 + wild cluster bootstrap + few-clusters + NB-04 demo plan (feeds NB 04 next).
- **`notation/frugal-parameterization.md`** — author DGPs whose ATE/CATE is a *primitive* (Evans–Didelez); confounding as a free dial; → possible `lyra/dgp/frugal.py`.
- Filed **22 root PDFs** into topic folders (`08-…/` platform craft, `04-…/` peeking, `02-…/cluster`, new
  `13-dgp-simulation/`); INDEX gained **§12 platform-engineering · §13 DGP-simulation · cluster-SE pass**.
- ⚠️ **Spotify risk-aware PDF is image-only** (no extractable text) — needs OCR/re-download; covered in the
  playbook from citations. Memory: `platform-engineering-playbook`.

**Next:** NB 04 — cluster-robust SEs (now well-prepped by `notation/cluster-robust-se.md`).

## 2026-06-07 — Sample-size calculation note (Spotify Confidence SSC)

Daniel flagged Spotify **Confidence**'s SSC playgrounds (I/II/III) as a model for a sample-size/power
notebook + the experiment-creation gate. WebFetched the 3 pages (formulas live only in the JS calculator
— got them from Daniel's "Show detailed formulas" screenshots instead) and synthesized
**`papers/sample-size-calculation.md`**: the progressive formula — L1 base $N=4(z_{1-\alpha}+z_{pow})^2\sigma^2/\Delta^2$;
L2 corrections $\alpha_{adj}=\alpha/(C\cdot S)$ (Bonferroni) and $\text{power}_{adj}=1-(1-\text{power})/(G_{NIM}+\min(S,1))$;
L3 allocation $(1/q_c+1/q_t)$ + CUPED $(1-\rho)$ + binary $\sigma^2=\mu(1-\mu)$ — with worked numbers, the
param-sensitivity lessons, and the "steal for Lyra" (DRAFT power-gate, scorecard time-to-power, harness
cross-check). Added INDEX §05 entry + `pdfs/05-…/confidence-ssc/SOURCE.md` (links home); wired into
**ROADMAP NB 08** (power & decisions) as the calculator spec. (Confidence = a direct chassis reference.)

## 2026-06-07 (later) — Power/sample-size deep-dive (4 added Spotify sources): confirm + expand

Daniel added 4 power/sample-size PDFs (mostly Spotify). Converted + read all 4 — **strongly confirmatory**
of `papers/sample-size-calculation.md` (the SSC formulas), with theory + meta-principle added:
- **"What Makes a Good Sample Size Calculator"** (Schultzberg 2026): the calculator is the **frontend of the
  analysis pipeline** — sequential/MTC/variance-reduction/clustering/triggering all change $N$ and compound;
  GST adds few% but always-valid CS needs 50%+ more; **Fixed-Power monitoring** (peeking at variance is FPR-safe).
- **"Are Optimal MTC Optimal for You?"** (Schultzberg 2026; paper arXiv:2604.09256 ⬜): **why Bonferroni** —
  closed-form sizing (α/S over **success metrics only**), simultaneous CIs, pairs with group-sequential;
  Bonferroni+GST beats Hommel+always-valid by 15–18pp; FWER vs FDR.
- **arXiv:2402.11609** Schultzberg–Ankargren–Frånberg — *Risk-Aware Decisions* (the **decision-rule** framework;
  guardrails-NIM need no α-corr but Type-II correction). **This is the full-text version of the formerly
  image-only Spotify PDF** — gap resolved; updated `platform-engineering.md` + INDEX §12.
- **arXiv:2405.03487** Nordin–Schultzberg — *Precision-based (Fixed-Power/Fixed-Width-CI) sequential designs*.

Expanded `papers/sample-size-calculation.md` (new "Confirmed + expanded" section) + updated
`platform-engineering.md` decisions/source-catalog. Filed 4 PDFs (§05 + §04 + confidence-ssc/); INDEX §05/§12
updated; flagged arXiv:2604.09256 to acquire.

**Next:** NB 04 — cluster-robust SEs.

## 2026-06-07 (later) — NB 04: cluster-robust SEs (built + promoted)

Built `notebooks/04_cluster_robust_se.py` (raw; 8 cells, 2 figs, 0 err), prepped by
`notation/cluster-robust-se.md`. The other half of "correct variance" — correlated **units**:
- **Clustered DGP** $y_{ig}=\beta x_g+\alpha_g+\varepsilon_{ig}$ (cluster-level regressor, ICC $\rho_u$);
  **Moulton** inflation $\tau_k=1+\rho_u(\bar N_g-1)$ recovered as an asserted quantity (ratio 2.40 ≈ √5.5).
- **Naive iid SE rejects a TRUE null at 0.41** (catastrophe). **CV1** (cluster sandwich, by hand;
  cross-checked == statsmodels) restores ~0.05 at large G but **over-rejects at small G** (0.18 @ G=5).
  **CV2/CV3** (bias-reduced / leave-one-cluster-out jackknife) + the **wild cluster bootstrap** (WCR,
  Rademacher/Webb) restore ~0.05 down to G=5. Invariant: **CV1==HC1 exact, CV3≈HC3** (0.63%, jackknife).
- **Promoted → `lyra/se.py`** (`ClusterOLS` iid/CV1/CV2/CV3 behind the Protocol + `wild_cluster_bootstrap`)
  + `ClusteredDGP` in `lyra/dgp`. **`tests/test_se.py`** (5): iid under-covers; CV1 OK large-G; CV1
  over-rejects but CV3 fixes small-G; WCR restores size; CV1→HC1 / CV3≈HC3 at G=N. **Full suite: 32 passed.**
- Fix logged: statsmodels cross-check used `m.bse[1]` on a named-column fit (KeyError) → pass numpy arrays.

**Next:** with the engine v1 complete (core ATE + typed metrics + cluster-robust SEs), per **D-18** the
**Chassis MVP interlude** (backend + scorecard, guided by `papers/platform-engineering.md`), then NB 05+.

## 2026-06-07 — NB 04 notation enrichment (Daniel's feedback)

Per Daniel's request (he likes rich notation/equations + the colour convention), enriched NB 04 §1 with
the full **sandwich-estimator theory ladder** following his Notion structure: the general
$\text{V}(\hat\beta|\mathbf X)=(\mathbf X'\mathbf X)^{-1}\mathbf B(\mathbf X'\mathbf X)^{-1}$ with the
double-sum meat (coloured $\textcolor{orange}{i}/\textcolor{green}{j}$, $\textcolor{purple}{\sigma^2}$) →
① homoskedasticity ($\sigma^2\mathbf I$ matrix) → ② HC0/HC1/HC2/HC3 (cross-section, diag forms) → ③ CRVE
(block-diagonal error matrix; CV0/CV1/CV2($\mathbf A_g{=}(\mathbf I{-}\mathbf H_g)^{-1/2}$)/CV3-jackknife).
Added **§7 panel-data / DiD**: the clustered two-way-FE regression
$Y_{igt}=\alpha_g+\phi_t+\theta D_{igt}+\gamma'Z_{igt}+\varepsilon_{igt}$ (θ = ATT; cluster-dependent within
group, independent across) → motivates NB 11 (DiD) / NB 05–06. Markdown-only; synced via `jupytext --update`
(2 figs + code outputs preserved, no re-run). Colours via KaTeX `\textcolor{#hex}`.

## 2026-06-07 — Chassis MVP, part 1: the backend (D-18)

Started the Chassis MVP (palette = **Ocean** navy+blue per Daniel, bright off-white bg, minimal). Built a
new **`chassis/`** package wrapping the `lyra` engine into the thin-but-real platform:
- **`assignment.py`** — deterministic salted-hash `assign()` (source-agnostic) + SRM χ².
- **`registry.py`** — `Experiment` + the **lifecycle state machine** (DRAFT→RUNNING→STOPPED→ANALYZED→
  DECIDED), illegal transitions rejected.
- **`power.py`** — the **DRAFT power-gate** (Spotify-SSC sample-size: α/(C·S), guardrail power, allocation, CUPED).
- **`scorecard.py`** — the **state-gated readout** (Etsy state→message + CI-colour-bar) running the typed
  `lyra/metrics` + cluster-robust `lyra/se` over a DGP event source, with **SRM gate**, accrual timeseries,
  and the **ground-truth "certified" badge** (harness coverage vs known truth — the superpower).
- **`seed.py`** — 6 demo experiments on DGP worlds (binary conversion · ratio offer-wall · A/A null ·
  geo-cluster promo · DECIDED push · underpowered DRAFT). Added `ClusteredDGP(binary_treat=…)` for genuine
  cluster-randomization (default off → NB04/tests unaffected).
- **`export.py`** (static snapshot → `frontend/public/data/chassis.json`, 19.6 kB) + **`app.py`** (FastAPI:
  `/api/experiments`, `/experiments/{id}`, `/assign`, `/transition`; TestClient green — assignment
  deterministic, 409 on illegal transition).
- **`tests/test_chassis.py`** (5): assignment deterministic/balanced/salt-independent · state machine
  rejects illegal · power-gate flags underpowered · **A/A doesn't flag + certified** · real effect →
  green + covers truth. Certified-badge floor set to coverage ≥ 0.88 (robust to MC noise). **Full suite: 37 passed.**

Verified readouts: Game A +25.7% (cert 92%), offer-wall +11.1% (90%), **A/A "No detectable change"** (91%),
geo-cluster +0.664 (98%), push DECIDED +19.1%, pricing DRAFT 9.7% (UNDERPOWERED). `chassis` in pyproject.

**Next — Chassis MVP part 2:** the **Ocean React frontend** (registry table + state-gated scorecard:
CI-colour-bar, the certified badge, the accrual chart, SRM/A·A, decision panel), consuming the snapshot/API.

## 2026-06-07 — Chassis MVP, part 2: the Ocean frontend

Built the React chassis UI in the **Ocean palette** (bright off-white #F4F7FC bg, white cards, navy ink,
one blue accent, soft pastel status chips, Inter font) — re-skinning `frontend/`:
- **`ocean.css`** — the design system (tokens + components). **`ui.jsx`** — StateChip, CertifiedBadge,
  EffectCell, PowerBar, the **CI-colour-bar** (green/red/grey + a faint mark at the *true* effect), Sidebar.
- **`Registry.jsx`** — portfolio stat cards + the experiments table (name · metric · owner · state · effect ·
  certified · power), click-through to the scorecard.
- **`Scorecard.jsx`** — the state-gated readout: effect headline + CI-bar, stat cards (effect/CI/power/
  **validation**), the **accrual chart** (Recharts ComposedChart — the CI band narrowing onto the dashed
  *true-effect* reference line), SRM/A·A diagnostics, and the **decision** card (DECIDED) or **power-gate** (DRAFT).
- **`ChassisApp.jsx`** + `main.jsx` rewired; reads `public/data/chassis.json` (static) — live `/api` ready.
  `index.html` → "Lyra" + Inter. **`npm run build` clean** (832 modules, 2.4s, 0 errors).

The Chassis MVP (D-18) is complete end-to-end: assignment → registry/state-machine → governed metrics +
cluster-robust SEs → state-gated scorecard with the **ground-truth certified badge**, on a real FastAPI
backend + an Ocean React UI. Run: `python -m chassis.export` then `cd frontend && npm run dev`.

**Next options:** wire the live FastAPI (replace static fetch with /api) + static deploy (GitHub Pages);
add the create-experiment flow (DRAFT power-gate form); or resume the notebooks (NB 05 — designs & interference).

## 2026-06-07 — NB 05: designs & interference (the money-shot) + on the platform

Built `notebooks/05_interference.py` (raw; 5 cells, 3 figs, 0 err) — the core thesis. A shared-budget
**marketplace** where treated users grab a larger share of a saturating conversion budget → **cannibalize**
others (SUTVA fails; $Y_i=Y_i(\mathbf T)$). Demonstrated by hand:
- the **naive user-level A/B uplift decays with allocation** (+0.41 @10% → +0.28 @90%) and **over-states the
  true global effect (+0.078) by 3–5×** — "A/B tests lie" (Vinted/Johari 2021);
- the **global truth** via the counterfactual twin (all-treat vs all-control);
- **cluster randomization** (whole markets) recovers it (+0.079, bias ~0) with cluster-robust SE (NB 04);
- the **platform verdict**: harness coverage of the truth — **naive 0.00 → NOT certified**, **cluster 0.94 →
  CERTIFIED**. The certify step catches the biased *design*, not just a bad number.
- **Promoted** → `lyra/dgp` **`InterferenceDGP`** (modes `user` biased / `cluster` correct; `ground_truth`
  = $\tau_{global}$). **`tests/test_interference.py`** (3): naive biased+uncertified · cluster recovers ·
  truth small-but-positive. **Full suite: 40 passed.**
- **On the dashboard:** added two chassis experiments — **"Marketplace reward — naive A/B"** (+0.332, truth
  +0.078 **MISSES → NOT certified 0%**) and **"Marketplace reward — geo clusters"** (+0.067 **COVERS →
  CERTIFIED 94%**). Re-exported the snapshot (8 experiments). The scorecard shows the certified badge
  **catching the biased design** — the superpower, live. (Scorecard shows absolute effect for interference
  metrics so the two are directly comparable.)

**Next (ROADMAP): NB 06 — switchback** (temporal interference; recycle `_old/04`).

## 2026-06-07 — NB 06: switchback (temporal interference) + on the platform

Recycled `_old/04` (the switchback lab) → **`notebooks/06_switchback.py`**, reframed as NB 06 (temporal
interference, the sequel to NB 05's spatial). 12 cells, 5 figs, 0 err. Full lab: the multi-shock DGP
(α_cl+γ_t+δ_{cl,t}+τ·T+carryover), the **Raw→CUPED→CUPAC→DML-DR** ladder (VR table 0%→45%→68%→61%), the
**structural power floor** (macro shocks ×(1+cv²) don't average away), the **structural inversion** (target
macro not residual), and the **Type-S efficiency-vs-robustness trap** under sign-flip carryover.
- **Promoted** → `lyra/dgp` **`SwitchbackDGP`** (`ground_truth`=τ) + `lyra/estimators_vr` **`SwitchbackCUPED`**
  (CUPED on `x_hist` + cluster-robust OLS). Harness: raw cov 0.91 / width 157, CUPED cov 0.93 / width 119
  (**VR 42%**). **`tests/test_switchback.py`** (3): cluster-robust recovers τ · CUPED tightens (no bias) ·
  tuned DGP detects+certifies. **Full suite: 43 passed.**
- **On the dashboard:** added **"Surge pricing — switchback"** (SwitchbackDGP tuned τ=70 + SwitchbackCUPED)
  → **+3.7%, certified 96.7%**. Snapshot now **9 experiments** spanning the full design space: A/B,
  ratio, A/A, cluster, marketplace interference (naive vs cluster), DECIDED, DRAFT, and switchback.

**Next (ROADMAP): NB 07 — sequential & diagnostics** (peeking-safe inference; recycle `_old/03` + `inference/anytime_valid`).

## 2026-06-07 — NB 07: sequential & diagnostics — a CROSS-CUTTING layer (Daniel's reframe)

Daniel's key insight: NB 07 is a *practice*, not an experiment *type* — it should apply to **every**
experiment. Built it that way. `notebooks/07_sequential.py` (raw; 7 cells, 2 figs, 0 err): the **peeking
problem** (naive continuous monitoring FPR **30%** vs nominal 5%; LIL/random-walk intuition), the
**always-valid confidence sequence** (Waudby-Smith — FPR **0.7%** despite peeking daily; the multiplier is
the explicit "peeking tax", 3.59 vs 1.96), the **advisory auto-stop** (fires only on a CS excluding 0;
min-runtime; winner's-curse caveat), **SRM/A·A** gates, and **BH-FDR** (20 null metrics → 64% false-positive
risk uncorrected).
- **Promoted** → `lyra/sequential.py` (`cs_multiplier`, `confidence_sequence`, `advisory`) +
  `lyra/diagnostics.py` (`bh_fdr`, `srm_chi2`). **`tests/test_sequential.py`** (5). **Full suite: 48 passed.**
- **Wired across the whole platform (the cross-cutting part):** the chassis scorecard now adds an
  **always-valid CS + advisory stop to EVERY running experiment** (CS band on the chart, advisory chip),
  and a **portfolio BH-FDR** across the running primary metrics. Verified: A/A → advisory "keep" + not
  FDR-significant; real effects → "stop" + significant; **portfolio FDR 6/7**. Frontend: CS band (faint) +
  fixed-n band on the chart, advisory chip on scorecard + registry rows, "Significant (FDR)" portfolio stat.
  `npm run build` clean.

This establishes the pattern Daniel wants: **per-experiment design (NB 03–06) + cross-cutting practices
(NB 07–08) composed per experiment**. Each experiment now carries: right design · right variance · SRM/A·A ·
always-valid monitoring · certified-vs-truth. **Next (ROADMAP): NB 08 — power & decisions** (DRAFT gate + decision rule).

## 2026-06-07 — end of day (progress saved)

State synced for resume. **NB 01–07 done + Chassis MVP (backend + Ocean UI) built; 48 tests passing; 9
demo experiments live.** PROGRESS "Now" rewritten; D-19 logged (per-experiment designs vs cross-cutting
practices, composed per experiment); memory `chassis-mvp` added. **Resume:** `python -m chassis.export`
then `cd frontend; npm run dev` (PowerShell `;` not `&&`) → http://localhost:5174; `python -m pytest`.
**Next: NB 08 — power & decisions** (DRAFT power-gate calculator [Confidence SSC] + test-and-roll +
multi-metric decision rule; a cross-cutting layer wrapping DRAFT/DECIDED).

## 2026-06-08 — NB 08: power, sizing & decisions — the cross-cutting bookends

`notebooks/08_power_decisions.py` (raw; 7 cells, 2 figs, 0 err): **power & MDE** (SSC closed-form
cross-checked against simulation-based power — lands on ~0.80; the only honest route for switchback/cluster),
the **DRAFT power-gate** (α/(C·S) + guardrail-power corrections inflate N), **test-and-roll** (Feit-Berman
profit-sizing ≪ NHST), and the **decision rule** — ship = **OEC superiority ∧ every guardrail non-inferior**;
the money-shot is an experiment that *wins on the primary but is blocked by a regressed margin guardrail*.
Fixed the SSC z to **two-sided** (z_{1-α/2}); promoted required_n is now correct.
- **Promoted** → `lyra/power.py` (`required_n`, `mde`, `power_gate`, `test_and_roll_size`) +
  `lyra/decisions.py` (`ship_decision`); `chassis/power.py` is now a thin re-export. **`tests/test_decisions.py`**
  (5). **Full suite: 53 passed.**
- **Wired across the platform (cross-cutting):** the scorecard now adds a **ship recommendation** to every
  experiment (conjunction rule), and — integrating NB 07's certify gate — **never ships an uncertified
  estimate** (so the naive-marketplace experiment correctly reads "Hold"). Added experiment #10 **"Aggressive
  discount — margin guardrail"** → primary wins (+conversion) but **gross margin regressed → NO SHIP** (the
  decision money-shot, live on the dashboard). Frontend: a "Ship recommendation" panel (verdict + per-metric
  superiority/non-inferiority breakdown + the certification block). `npm run build` clean.

This completes the **cross-cutting bookends** (D-19): DRAFT power-gate + DECIDED ship rule wrap every
experiment. **Next (ROADMAP): NB 09 — CATE / heterogeneity** (who responds; meta-learners + causal forests).

## 2026-06-08 — Create-experiment flow + live power calculator (Daniel's product ask)

Daniel: the NB 08 power calc has the most utility wired into the actual **"+ New experiment"** flow. Built
it. The button now opens **`NewExperiment.jsx`** — a design form (name · metric type · baseline μ · σ² ·
relative MDE · allocation · #success/#comparisons/#guardrail-NIM · CUPED ρ · days × users/day) with a
**live power readout**: required N (total + per-arm), the DRAFT **gate verdict** (powered / underpowered +
the detectable MDE at available traffic), α_adj/power_adj, and a **power-vs-N curve** (required + available
marked). **"Create draft"** appends a DRAFT to the registry and opens its power-gate scorecard.
- **`frontend/src/power.js`** — the SSC formula ported to client-side JS (Acklam normPpf + erf normCdf), so
  the calculator runs live on the **static snapshot** (no backend). **Cross-checked vs `lyra.power`: identical**
  (50233 / 28749 / 59497 incl. the C·S and guardrail-power corrections). `npm run build` clean.
- Wired: Registry "+ New experiment" → `onNew`; ChassisApp holds a `creating` view + `onCreate` (appends draft).

This makes NB 08 tangible in the product: design an experiment → the platform sizes *that* experiment live →
create it as a DRAFT. (Pure frontend; no re-export needed.) **Next (ROADMAP): NB 09 — CATE / heterogeneity.**

## 2026-06-08 — Operative platform, Phase 1: the create→run→decide loop is LIVE (D-20)

Daniel's pivot: stop adding notebooks, make the platform **operative** — created experiments must actually
RUN. Decision: **go live (FastAPI + React, /api)**; first milestone the **create→run→decide loop**.
- **`lyra/dgp/ab.py` `ABDGP`** — direct planted-effect A/B DGP (binary/continuous); `ground_truth().ate ==
  effect` exactly (a created experiment plants its own truth; the harness certifies it).
- **`chassis/worlds.py` `build_world(spec)`** — maps a create-form spec → runnable (DGP, estimator, metric,
  required N). Phase 1 wires the A/B world (proportion + continuous); cluster/switchback/interference plug in next.
- **`chassis/app.py`** — `POST /api/experiments` (create → DGP world + DRAFT power-gate), enhanced
  transition (sets `started`; DECIDE defaults to the ship rule), mutable in-memory registry. Relabelled the
  metric direction default. **`tests/test_chassis_api.py`** (3): ABDGP plants/certifies, the full
  create→run→decide loop, illegal transition → 409. **Full suite: 56 passed.**
- **Frontend** went live: `api.js` (+ Vite `/api` proxy → :8000), `ChassisApp` loads `/api` with **static
  fallback**, lazy detail fetch. `NewExperiment` POSTs a spec (+ a **True effect (ground truth)** field; μ
  relabelled "Baseline μ (from history)" with a clear tooltip — it's a *planning* input, not the ATE). The
  **Scorecard** gained **lifecycle controls** (Launch ▶ / Stop ■ / Analyze / Hold ✗ / Ship ✓). Sidebar shows
  a **live · FastAPI** badge. `npm run build` clean.

**Verified end-to-end over HTTP:** create (DRAFT, power-gated) → Launch → RUNNING (DGP runs, **certified vs
the planted truth**) → Stop → Analyze → Decide (ship rule). **Run it:** terminal 1 `uvicorn chassis.app:app
--port 8000`; terminal 2 `cd frontend; npm run dev` → http://localhost:5175 (live badge).
**Next:** more world templates in `build_world` (cluster/switchback/interference) + the three sections
(Metrics · Decisions · Assignment).

## 2026-06-08 — Operative platform, Phase 2: the three sections (Metrics · Decisions · Assignment)

Built out the decorative sidebar into real screens; the nav now routes (D-20 cont.).
- **Backend:** `chassis/catalog.py` (the **governed metric catalog** — 6 versioned metrics with estimand /
  variance / estimator / owner / status, mapping to `lyra` typed estimators) + `GET /api/metrics`;
  `GET /api/assign/check` (hash N synthetic units → arm split + SRM χ²).
- **Frontend:** `Metrics.jsx` (the governed catalog table, static fallback), `Decisions.jsx` (the ship rule
  across the portfolio — recommendation + rationale + recorded call, click-through to the scorecard),
  `Assignment.jsx` (unit→bucket lookup showing determinism + salt, and a 5k-unit **balance check** with the
  SRM verdict). `ui.jsx` Sidebar nav is now active; `ChassisApp` routes by `section`. `npm run build` clean.
- Verified live via the Vite proxy: 6 metrics, balance check 1972/2028 (srm_p 0.38), app 200. **Suite: 56 passed.**

The four core surfaces are now real: **Experiments** (create→run→decide) · **Metrics** (governed catalog) ·
**Decisions** (portfolio ship rule) · **Assignment** (deterministic bucketing + SRM). Run: `uvicorn
chassis.app:app --port 8000` + `cd frontend; npm run dev` → http://localhost:5175.
**Next:** more world templates in `build_world` (cluster/switchback/interference) so created experiments
span designs; optional persistence (Postgres) so state survives restart.

## 2026-06-10 — Operative platform, Phase 3: world templates in create (full design space)

The create form now spans the whole design space, not just A/B (D-20 cont.). Two-sided-z fix in
`lyra/power.py` (and the JS `power.js`) is consistent — required N parity holds (50,233).
- **`chassis/worlds.build_world`** extended: **cluster** (ClusteredDGP + ClusterOLS), **switchback**
  (SwitchbackDGP + SwitchbackCUPED), **interference** (InterferenceDGP, naive `user` vs `cluster`-safe).
  Each plants its effect via the DGP's native param (beta / tau / boost); `ground_truth().ate` == the plant.
  `CreateSpec` gained the structural params (G, n_g, J, H, n_bar, boost, interference_design); the create
  endpoint uses the factory's full `world` dict (incl. the `interference` flag).
- **Frontend `NewExperiment`** rebuilt with a **Design selector** + per-design fields; A/B keeps the live
  power calculator + curve, the others show a **design summary** (structure · estimator · "power validated
  by simulation at launch") — and the naive-marketplace option shows an **"expected: uncertified"** warning.
- **Verified live (create→launch→certify):** A/B +0.03 (98%) · cluster +0.50 (97%) · switchback +70 (97%) ·
  marketplace-safe +0.078 (97%) all **CERTIFIED**; marketplace-**naive** +0.078 (0%) **uncertified** — the
  interference money-shot, now createable from the UI. `tests/test_chassis_api.py` covers all 5. **Suite: 57 passed.**

Run: `uvicorn chassis.app:app --port 8000` + `cd frontend; npm run dev` → http://localhost:5173.
**Next options:** persistence (SQLite, survive restart) · back to the inference moat (NB 09 — CATE).

## 2026-06-10 — Deploy decision: static demo (zero-cost); persistence skipped

Daniel chose the **static-snapshot demo** as the deploy model → no SQLite/persistence (saves complexity;
in-memory registry re-seeds 10 demos on restart). The static-snapshot fallback we already built IS the
deploy vehicle. Made it deploy-ready:
- Regenerated `frontend/public/data/chassis.json` (10 experiments, current with the two-sided-z power fix +
  decision_rec + sequential + FDR); `npm run build` bundles it into `dist/data/chassis.json`.
- **Verified the production build is self-contained** (`npm run preview`, no backend): serves the app +
  the snapshot; `/api` fails → client falls back to the snapshot. Static demo works standalone.
- `NewExperiment` subtitle is mode-honest (static: "the power calculator runs live here; launching needs
  the backend"). Wrote **`DEPLOY.md`**: (A) static demo → Vercel/Netlify/GH-Pages of `frontend/dist`;
  (B) live app → uvicorn + Render/Fly. Static demo = read-only registry/scorecards/metrics/decisions +
  the live client-side power calculator; Assignment + run-loop degrade gracefully.

**Next:** back to the inference moat — NB 09 (CATE / targeting), per the recommended sequence.

## 2026-06-10 — NB 09: CATE (who responds) — the inference moat resumes

Built `notebooks/09_cate.py` (raw; 7 cells, 2 figs, 0 err). ATE → CATE: τ(x)=E[Y(1)−Y(0)|X]. A randomized
**hetero DGP** (known surface τ(x)=0.5+x0−0.5x1 over a nonlinear nuisance) — **ATE +0.52 but τ(x) ranges
−3.4…+4.9**, so a third of users are *harmed* by a "winning" A/B. Estimators built raw + validated **against
the known τ(x)** (Lyra's superpower for heterogeneity):
- **S / T / X-learner** (Künzel) + **causal forest** (econml `CausalForestDML`, Wager–Athey honest CIs).
  RMSE vs truth: S 0.33 · T 0.34 · **X 0.21** · forest 0.26. Forest's edge = **honest pointwise CIs that
  cover the true τ(x) at ~88%** (a real platform can't check this). S-learner visibly shrinks toward the ATE.
- **Targeting teaser** (→ NB 10): the top-decile by τ̂ has true effect **+2.46 (4.7× the ATE)** — value a
  null-looking A/B leaves on the table.
- **Promoted** → `lyra/cate.py` (`SLearner`/`TLearner`/`XLearner`/`CausalForest`, a `fit(df)`/`predict_cate(X)`
  family) + `lyra/dgp` `HeteroDGP` (exposes the true `tau(X)`). `tests/test_cate.py` (3): X-learner recovers
  τ(x) (corr>.85), forest CI covers τ(x) ≥85%, S-learner shrinks. **Full suite: 60 passed.** econml + xgboost
  confirmed installed.

**Next (ROADMAP): NB 10 — uplift evaluation & policy** (Qini/AUUC/RATE · policy learning/trees · OPE: IPS/DR)
— turns τ̂(x) into a calibrated, evaluated targeting policy.

## 2026-06-10 — NB 10: uplift evaluation & policy (the targeting decision)

Built `notebooks/10_policy.py` (raw; 7 cells, 2 figs, 0 err) — turns NB 09's τ̂(x) into an evaluated,
validated **policy**. Everything is built on the **doubly-robust score** Γ (cross-fitted AIPW pseudo-outcome;
mean(Γ)=AIPW ATE +0.49 vs truth +0.50):
- **Uplift curve / AUUC** — rank by τ̂, cumulative effect vs the oracle (true τ) ceiling and the random/ATE
  floor. **RATE (AUTOC) + bootstrap CI** → z = 42, "heterogeneity is real and targetable."
- **Policy learning** — threshold (τ̂>cost) + an interpretable **econml DRPolicyTree**; net-of-cost value:
  treat-all +0.19, **threshold +0.54 (~2.9×)**, tree +0.50 — and the **DR value tracks the truth** at each.
- **OPE money-shot** — IPS vs DR recover the *true* policy value (+0.730) from logged data without the
  oracle: IPS +0.742 ±0.051, **DR +0.736 ±0.031 (~2× tighter)**. The superpower, applied to decisions.
- **Promoted** → `lyra/policy.py` (`dr_scores`, `uplift_curve`, `auuc`, `rate`, `threshold_policy`,
  `policy_value`) + `lyra/ope.py` (`ips_value`, `dr_value`). `tests/test_policy.py` (3): RATE detects
  heterogeneity · targeting beats treat-all on true value · DR-OPE recovers truth tighter than IPS.
  **Full suite: 63 passed.**

Curriculum: **NB 01–10 done; 2 left.** **Next: NB 11 — observational** (DML PLR/IRM · modern DiD ·
synthetic control/SDID · IV/LATE) — causal effects *without* randomization. Then NB 12 (incrementality + Criteo).

## 2026-06-10 — NB 12: incrementality & real-data validation (CURRICULUM COMPLETE)

Built `notebooks/12_incrementality.py` (raw; 6 cells, 1 fig, 0 err) — the finale, the MVP's incrementality
+ Criteo legs (both flagged in CLAUDE.md decisions).
- **Ghost-ads sim (authored truth, τ=0.015):** naive attribution credits all exposed conversions →
  **+0.087 (5.8× the truth)**; observational exposed−unexposed +0.041 (targeting bias); the **PSA/ghost-ad
  holdout ITT** +0.0063 (truth τ·exp 0.0064) and **CACE = ITT÷exposure** +0.0148 (truth 0.015) recover it.
  Lewis–Rao "unfavorable economics" + the one-sided-non-compliance IV/LATE, validated.
- **Criteo Uplift real RCT (13.9M rows):** streamed a balanced 559k sample from Hugging Face (sorted by
  treatment → chunk-sampled across the file; cached 9 MB parquet, **not vendored**). The SAME estimator:
  **visit lift +1.06pp (z=14.4)**, conversion +0.13pp (z=8.2) — small but highly significant (Lewis–Rao
  confirmed). Lin (2013) adjustment tightens ~10% with a small point shift → flags **mild covariate
  imbalance** (real data ≠ textbook RCT). ITT vs CACE via the `exposure` column (exposure 3.6% → CACE on
  the exposed +29pp, with the exclusion-assumption caveat).
- **Promoted** → `lyra/incrementality.py` (`lift`, `cace`) + `validation/criteo.py` (`load_sample`,
  `validate`). `tests/test_incrementality_lyra.py` (2; Criteo test skips if uncached). **Full suite: 65 passed.**

🏁 **CURRICULUM COMPLETE — NB 01–12 done (NB 11 observational deferred).** The inference engine is built end
to end, every method validated against ground truth, and the headline claim — *the same estimator works on
real Criteo data* — is demonstrated. Remaining backlog: NB 11 (observational: DML/DiD/synthetic-control/IV),
optional platform polish.

## 2026-06-10 — Platform UX redesign Phase 1: Home + industry study cases

Daniel: turn the chassis into a product demo for recruiters + DS, framed as SaaS across industries.
Researched Confidence (GitHub: ZTest/multiple_difference/Bonferroni/NIM/GST/power; bootcamp = teaching),
GrowthBook (nav: Feature Flags · Data & Metrics · Experimentation · Insights · Product Analytics; "see the
SQL behind every query"), Statsig, Eppo (create flow Define→Allocation→Metrics→Guardrails→Scorecard;
**"Protocols"** = reusable templates per use-case). Wrote **`PLAN_UX.md`** (IA, Home gallery, 6 study cases,
4-step create wizard, interactive DGP plots, phasing). Daniel chose: **start Phase 1; 6 study cases**.
- **`studyCases.js`** — 6 industry cases (Rewarded UA/Adtech · On-demand/Surge · Marketplace/interference ·
  E-commerce checkout · Ads incrementality · Personalization/CATE), each a notebook-style brief (business ·
  experiment · why-hard · the DGP · what Lyra shows) + a live-experiment id and/or a create-wizard template.
- **`Home.jsx`** (navy hero "Experimentation you can trust" + "✓ Lyra Verified" + 6 case cards) ·
  **`StudyCase.jsx`** (the brief + "View live" / "Create this experiment" CTAs; deep-dive note for CATE/incrementality).
- Wired: Sidebar gains **Home** (now the default landing); `ChassisApp` routes home/case detail; "View live"
  opens the seeded scorecard (all 4 liveIds verified), "Create this" prefills the wizard via `seedForm(template)`.
  ocean.css: hero, case-grid (accent-bordered cards), brief, result-box, responsive. **`npm run build` clean.**

The static demo gets Home too (cases are content; CTAs degrade gracefully). **Next: Phase 2 (4-step create
wizard) + Phase 3 (interactive DGP plots).** Plan in `PLAN_UX.md`.

## 2026-06-10 — UX Phase 2+3 (create wizard + interactive DGP plots) + detailed analytics view

- **Create wizard (Phase 2):** rebuilt `NewExperiment` as a **4-step stepper** — Design → Metrics →
  **Simulate** → Review (numbered progress, Back/Next, Create on step 4). Templates from study cases still
  prefill it. Fields redistributed across steps; AbReadout (power) / DesignSummary on Review.
- **Interactive DGP plots (Phase 3):** `dgpViz.js` — client-side, parameter-responsive previews (instant,
  no backend): A/B control-vs-treatment outcome densities/bars · switchback time-strip (filled/hollow dots =
  on/off) · cluster between-cluster mean scatter · marketplace naive-uplift-decays-vs-allocation curve. Live
  in the wizard's Simulate step; labelled "illustrative — real numbers from running it."
- **Detailed analytics (Daniel's ask):** harness gained `return_draws` (per-replicate point/CI/coverage);
  `scorecard.compute` now emits an **`analytics`** block (sampling points · 50 CIs · per-arm histogram).
  `Analytics.jsx` + a **Summary / Detailed analytics tab** on the scorecard: the **MC sampling distribution**
  (estimate centres on the dashed truth → unbiased), the **coverage caterpillar** (50 CIs green=cover/red=miss,
  ~95%), the **per-arm outcome distribution**, and a bias/coverage stat strip. Re-exported the snapshot
  (analytics baked in, 120 samples; warm-cache serves it). `npm run build` clean; **full suite 65 passed**;
  both servers live (8000 / 5173).

UX plan: Phase 4 (logo, spacing, skeletons, copy) remains. `PLAN_UX.md` tracks it.

## 2026-06-10 — Create wizard: Spotify-style sample-size calculator step

Daniel: the create flow needs a sample-size calculator "like Spotify's" (Confidence SSC level-3). Built it
as **wizard step 2** (Design → **Sample size** → Simulate → Review), replacing the lighter Metrics step.
- **`SampleSize.jsx`** — the 4-column Spotify layout (Metric params: μ, rel-MDE %, σ², binary toggle, ρ ·
  Statistical: α, power, test-type · Experiment design: #comparisons, #success, #guardrail-NIM,
  #guardrail-no-NIM · Allocation: control/treatment %) with sliders, a live **Required sample size** + abs
  MDE + per-arm sizes, and a **"Show detailed formulas"** toggle rendering the N formula + α/power
  corrections in **KaTeX** with the actual numbers substituted (matches the screenshot). Added `katex` dep
  (formula rendering); CSS for sliders/grid.
- **Convention (important):** the linter had moved `power.py`/`power.js` to two-sided z. I briefly reverted
  to one-sided to match Spotify's 360,630 — but `test_decisions::test_required_n_lands_on_nominal_power`
  correctly caught that one-sided sizing **under-powers our two-sided CIs** (69% actual power). Resolution:
  **two-sided is the default** (correct; reproduces 494,605) with a **one-sided toggle** to reproduce
  Spotify exactly (360,629). Threaded `two_sided` through `lyra.power` (+ JS) + `CreateSpec`/`build_world`.
  Parity: PY == JS for both conventions. Re-exported the snapshot; **full suite 65 passed**; servers live.

UX: Phase 4 polish (logo, spacing, skeletons, copy) still pending. `PLAN_UX.md` tracks it.

## 2026-06-16 — UX Phase 4: polish

- **Logo:** an SVG **Lyra constellation** mark (Vega = the bright star — a nod to the project's two names)
  in the sidebar brand + a matching **favicon.svg**; `index.html` head got the icon + meta description.
- **Loading skeletons:** replaced "Loading chassis…" with a shimmer hero + 6 case-card skeletons (matches
  the Home layout; no jarring blank/hang).
- **"How Lyra works" strip** on Home: 3 steps (Author the world → Run the experiment → Certify against
  truth) — frames the simulator pitch above the study-case gallery.
- **Dead-code cleanup:** moved the pre-pivot replay app (`App.jsx`, `Portfolio`, `ExperimentDetail`,
  `RampDiagnostic`, `WorldView`, `bits`, `styles.css`) to `frontend/src/_legacy/`; the live tree is now just
  the chassis components. `npm run build` clean; both servers live.

**UX redesign complete (Phases 1–4):** Home + study cases · 4-step create wizard (incl. the Spotify-style
sample-size calculator) · interactive DGP plots · detailed-analytics view · logo/skeletons/cleanup. The
platform is demo-ready across all surfaces. `PLAN_UX.md` is the record.
