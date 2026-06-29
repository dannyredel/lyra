# Reading List & Library — single source of truth

The one catalog for Vega's reading. Merges what we **physically have** (PDFs under `pdfs/<NN-topic>/`)
with what we still **want** (`⬜` rows), the per-item **rationale**, and the **Vega module each feeds**.
This file supersedes the old split between `INDEX.md` and `LITERATURE.md`
(see [`../LITERATURE.md`](../LITERATURE.md), now a pointer).

Processed first-person notes go in [`papers/`](papers/); equation/notation sheets in
[`notation/`](notation/). Workflow + template in [README.md](README.md).

**Status:** `✅` have PDF · `⬜` to acquire (links in the [Acquisition appendix](#acquisition-links)).
**Kind:** 📘 book · 📄 paper · 📊 industry blog · 🛠 package docs · 🔗 link.  **⭐ = foundational.**

---

## Foundational set (read/keep closest)

| ⭐ | Doc | Topic | Why |
|---|---|---|---|
| 📘 | **Wager — Causal Inference (Nov 2025)** | 00 | Primary textbook; the **preferred language/notation** for the project. |
| 📘 | **Chernozhukov et al — Applied Causal Inference / Causal ML book (2022)** | 00 | The applied-causal-ML reference; pairs with package docs. |
| 📄 | **CCDDHNR 2018 — Double/Debiased ML for Treatment & Structural Parameters** | 01 | *The* DML paper: Neyman-orthogonal scores + cross-fitting. |
| 📄 | **Belloni, Chernozhukov & Hansen 2014 (REStud) — Post-double-selection** | 01 | Uniformly valid inference after selecting among high-dim controls. |
| 📄 | **Ahrens et al 2026 — Intro to DML** | 01 | The gateway/teaching version; orients the `inference/` adjustment layer. |
| 📄 | **Johari et al 2021 — Experimental Design in Two-Sided Platforms** | 02 | Theoretical core of the thesis: when CR vs LR randomization is biased. |
| 📄 | **Masoero et al 2025 — Multiple Randomization Designs** | 02 | Modern design frame for marketplace interference. |
| 📄 | **Holtz et al 2024 — Cluster Randomization (Airbnb pricing)** | 02 | The canonical *applied* interference correction → `inference/cluster.py`. |
| 📄 | **Howard et al 2022 / Johari et al 2017** | 04 | Confidence sequences + the peeking problem → `inference/anytime_valid.py`. |
| 🛠 | **DoubleML + EconML docs** | 01 | Implementation foundations for the estimator library. |

---

## 00 · Foundational — books & references
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📘⭐ | Wager — *Causal Inference* (Nov 2025) | Primary textbook; preferred notation. **ch.1–7, 10–13 processed** → note [`papers/wager-causal-inference.md`](papers/wager-causal-inference.md); 9 equation sheets in `notation/` (ate-estimators, hte, dml, **interference**, iv-late, adaptive-experiments, balancing, policy-learning, event-study-did). md in `md/`. Pending: ch.8, 9, 14–16. |
| ✅ | 📘⭐ | Chernozhukov, Hansen, Kallus, Spindler, Syrgkanis — *Applied Causal Inference Powered by ML/AI* (2022) | DML/Causal-ML reference. |
| ✅ | 🔗 | Victor Chernozhukov — homepage (saved) | Index to his papers; sourced the DML originals below. |
| ✅ | 📄⭐ | Imbens & Wooldridge 2009 — *Recent Developments in the Econometrics of Program Evaluation* | The canonical program-evaluation review (unconfoundedness, regression/matching/IPW/DiD). Source for the regression-with-controls + OLS-weighting material → [`notation/ate-estimators.md`](notation/ate-estimators.md) §3.1. |

## 01 · Causal ML / Double ML — methods & tooling → `inference/` adjustment layer, `inference/hte.py`
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📄⭐ | CCDDHNR 2018 — *DML for Treatment & Structural Parameters* (Econometrics J) | The DML method. |
| ✅ | 📄⭐ | Belloni, Chernozhukov & Hansen 2014 — *Inference after Selection amongst High-Dim Controls* (REStud) | Post-double-selection; uniform inference. |
| ✅ | 📄 | Belloni, Chernozhukov & Hansen 2014 — *High-Dim Methods & Inference on Structural/Treatment Effects* (JEP) | The accessible survey of the above. |
| ✅ | 📄⭐ | Ahrens et al 2026 — *An Introduction to DML* | Teaching version; recommended-practice. |
| ✅ | 📄 | Bach et al 2025 — *Sensitivity Analysis for Causal ML* (Booking.com) | Robustness to unobserved confounding (OVB bounds). |
| ✅ | 🛠⭐ | DoubleML — Python package docs | Implementation reference. |
| ✅ | 🛠⭐ | EconML — Python package docs | HTE/DML implementations (your wheelhouse). |
| ✅ | 🛠 | DoubleML — *The Basics of Double ML* | Tutorial. |
| ✅ | 🔗 | **Daniel's DML notes** (Notion export) — `DML Export Notion/` | Comprehensive: estimator taxonomy, two-biases framing, Double-Selection family (Belloni'14a/b), DS-IV/PLIV, rigorous/adaptive/root-Lasso. The deep reference; conceptual spine distilled into [`notation/dml.md`](notation/dml.md). |
| ⬜ | 📄 | CCDDHN 2017 — *Double/Debiased/Neyman ML of Treatment Effects* (AER P&P) | The short companion to the 2018 paper. |
| ⬜ | 📄 | Bach, Chernozhukov, Kurz & Spindler 2022 — *DoubleML* (JMLR) | The software paper behind the docs. |
| ⬜ | 📄 | Chernozhukov, Newey & Singh 2022 — *Automatic Debiased ML* (Econometrica) | Auto-orthogonalization. |
| ⬜ | 📄 | Semenova & Chernozhukov 2021 — *Debiased ML of CATEs* | CATE via DML → `inference/hte.py`. |

## 02 · Marketplace interference — the core thesis → `inference/cluster.py`, `budget_split.py`, ramp diagnostic
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📊 | DoorDash 2022 — *Balancing Network Effects, Learning Effects & Power* | The interference/learning/power three-way tension. |
| | | **two-sided-randomization/** | |
| ✅ | 📄⭐ | Johari et al 2021 — *Two-Sided Platforms: An Analysis of Bias* | CR/LR/TSR; bias depends on market balance. |
| ✅ | 📄⭐ | Masoero et al 2025 — *Multiple Randomization Designs* (Amazon/Imbens) | SMRDs; main/direct/spillover effects. |
| ✅ | 📄 | Sudijono et al 2026 — *Regression Adjustments for Double Randomization* | Variance-optimal MRD adjustment. |
| | | **cluster-and-network/** | |
| ✅ | 📄⭐ | Holtz et al 2024 — *Cluster Randomization* (Airbnb pricing, Mgmt Sci) | Applied interference-bias reduction. |
| ✅ | 📄 | Eckles, Karrer & Ugander 2016 — *Experiments in Networks: Reducing Bias from Interference* | Exposure-mapping bias reduction. |
| ✅ | 📄 | Hansen 2024/25 — *Jackknife SEs for Clustered Regression* | Cluster-robust SEs / small-#-clusters; the **CV3** jackknife. |
| | | **cluster-robust SE inference** → **NB 04** (standard-errors notebook); packages in [`../STACK.md`](../STACK.md) | |
| ✅ | 🛠 | sandwich **`sandwich-CL`** vignette — *Clustered Covariances* | The CRVE implementation reference (read first to get CV1/CR2/CV3 right). |
| ⬜ | 📄⭐ | **Cameron & Miller** — *A Practitioner's Guide to Cluster-Robust Inference* | Canonical guide: CRVE, when/how to cluster, few-clusters fixes. |
| ⬜ | 📄⭐ | **MacKinnon, Nielsen & Webb 2023** — *Cluster-Robust Inference: A Guide to Empirical Practice* (J.Econometrics) | Modern guidance: CV1/CV2/CV3, few clusters, wild cluster bootstrap. |
| ⬜ | 📄 | **MacKinnon & Webb 2023** — *Fast & Reliable Jackknife and Bootstrap Methods for Cluster-Robust Inference* | CV3 variance + the new wild cluster bootstrap (→ `wildboottest`/`fwildclusterboot`). |
| ⬜ | 📄 | **Hansen 2025** — *Jackknife SEs for Difference-in-Difference Regression* | Jackknife CV3 for DiD; pairs with NB 11 (DiD). |
| ⬜ | 📊 | Glovo 2022 — *Cluster-randomized experiments at Glovo* (Clavijo & Toce) | Compute SEs at cluster level or overstate precision. |
| ⬜ | 📄 | LinkedIn — *Budget-split Design* (Liu et al) | The fix for budget interference → `inference/budget_split.py`. |
| ⬜ | 📊 | Vinted — *When A/B Tests Lie* | Cleanest statement of uplift-decay-with-allocation. |
| ⬜ | 📄 | Hudgens & Halloran 2008; Aronow & Samii 2017 | Partial-interference / exposure-mapping theory. |
| ⬜ | 📄⭐ | **Munro, Kuang & Wager 2025** — marketplace equilibrium interference | Direct/indirect effects when prices align supply & demand + spillover-aware targeting — **≈ the Vega setting** (cited in Wager ch.12). |
| ⬜ | 📄 | Leung 2022 (approx. network interference); Hu, Li & Wager 2022 (ADE/AIE); Athey, Eckles & Imbens 2018 (interference testing) | Estimation/testing machinery from Wager ch.11–12. |

## 03 · Switchback → `inference/switchback.py` (Phase-3 Glovo; design vocabulary now)
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📄⭐ | Bojinov et al 2021 — *Design & Analysis of Switchback Experiments* (HBS) | The foundation: potential outcomes, carryover order *m*, optimal switch duration. → primer + lab. |
| ✅ | 📄⭐ | **Pankratev 2026 — *Powerful Switchback Experiments – Or Not?*** (DoorDash, arXiv:2606.03012) | **Closed-form power formula** + the structural floor (macro shocks ×(1+cv²)); estimator-level choice. |
| ✅ | 📊⭐ | **Pankratev 2026 — *Design-Aware Variance Reduction for Switchbacks*** (poster) | The **DGP + Raw/CUPED/CUPAC/DML-DR** comparative study; the lab re-implements its sim. |
| ✅ | 📄 | Liu & Zhong 2026 — *Randomization Tests in Switchback* | Finite-sample CRTs, carryover horizon. |
| ✅ | 📄 | Missault et al 2025 — *Robust & Efficient Multiple-unit Switchback* (Amazon) | "Regular Balanced Switchback Designs." |
| ⬜ | 📊 | DoorDash 2018/2019 — switchback posts (Kastelman/Ramesh; Sneider/Tang) | The canonical industry pattern. |
| ✅ | 📝 | **Primer + lab** — `papers/switchback-and-variance-reduction.md` + `notebooks/04_switchback_lab` | Pedagogic summary + hands-on lab (sim, 4 estimators, power floor, Type-S). |

## 04 · Sequential / anytime-valid → `inference/anytime_valid.py`, live dashboard
> The four Spotify blog PDFs were image-only exports, so they were **fetched live from engineering.atspotify.com**
> (2026-06-02) and processed into [`notation/anytime-valid.md`](notation/anytime-valid.md) §5 (GST vs AVI/mSPRT vs
> Bonferroni · within-unit "Peeking 2.0" · fixed-power). **Papers they cite → acquire** (`04-…/`):
> _Owned now ✅:_ Nordin & Schultzberg 2024 (Fixed-Power); Larsen et al 2023/24 (review, in §05). _Still ⬜:_
> **Lan & DeMets 1983** (alpha-spending, the GST foundation) · **Jennison & Turnbull** *Group Sequential Methods* (book) ·
> **Lindon, Malek & Zhang 2022** mSPRT `arXiv:2210.08589` · **Wald 1945** (SPRT) ·
> Guo & Deng 2015 `arXiv:1501.00450` · Kim & Tsiatis 2020 · Wassmer & Brannath 2016 (book). Longitudinal:
> Liang & Zeger 1986 (GEE) · Diggle et al *Analysis of Longitudinal Data* · Shoben 2010 (diss.) · Wong et al 2021 `arXiv:2102.11297`.

| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📄⭐ | Howard et al 2022 — *Confidence sequences / time-uniform bounds* | Modern CS basis (LIL rate, supermartingale+Ville). **Processed** → [`notation/anytime-valid.md`](notation/anytime-valid.md). |
| ✅ | 📄⭐ | Johari et al 2017 — *Peeking at A/B Tests* | Peeking problem + mSPRT. **Processed** → [`notation/anytime-valid.md`](notation/anytime-valid.md), synthesis [`papers/platform-experimentation.md`](papers/platform-experimentation.md). |
| ✅ | 📄 | Imbens et al 2026b — *Demonstration Experiments* | Adaptive/MAB; anytime-valid "≥1 arm beats threshold." |
| ✅ | 📊 | Spotify — *Peeking Problem 2.0* (Part 1) | Longitudinal data breaks naive sequential tests. |
| ✅ | 📊 | Spotify — *Sequential Testing* (Part 2) | Their group-sequential fix. |
| ✅ | 📊 | Spotify — *Choosing a Sequential Testing Framework* | CS vs GST vs mSPRT comparison. |
| ✅ | 📊 | Spotify — *Fixed-Power Designs* (Nordin & Schultzberg) | "What you peek at" > "if you peek." |
| ✅ | 📄 | Nordin & Schultzberg 2024 — *Fixed-Power Designs* (arXiv:2405.03487) | The paper behind the blog → [`notation/anytime-valid.md`](notation/anytime-valid.md) §5. |
| ✅ | 📄 | *Anytime-Valid Inference for μ* — **supplementary material only** | Appendix (limitations of fixed-$n$ testing); the main paper is missing — re-download. |
| ⬜ | 📄 | Waudby-Smith et al 2023 — *Asymptotic Confidence Sequences* | Drop-in CS; likely our default. |
| ⬜ | 📄 | Lindon et al 2022 (Netflix) — *Design-Based Confidence Sequences* | CS for A/B, panel & switchback. |
| ⬜ | 📚 | Lan & DeMets 1983; Jennison & Turnbull (book) | Classic group-sequential basis. |

## 05 · Power & decision frameworks → power/MDE, decision banner, guardrails
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 🔗⭐ | **Spotify Confidence — Sample Size Calculation I/II/III** (SSC playgrounds) | The progressive sample-size calculator (base → multiple-testing/guardrail corrections → allocation+CUPED+binary) as a **DRAFT-gate** in experiment creation. **Processed** → [`papers/sample-size-calculation.md`](papers/sample-size-calculation.md); links + drops in `pdfs/05-…/confidence-ssc/`. Feeds **NB 08** + the chassis power-gate. |
| ✅ | 📊 | Schultzberg 2026 — *What Makes a Good Sample Size Calculator?* (Confidence) | The calculator is the **frontend of the analysis pipeline** — sequential/MTC/variance-reduction/clustering/triggering all change $N$; Fixed-Power monitoring. → same note. |
| ✅ | 📄⭐ | **Schultzberg, Ankargren & Frånberg 2024 — *Risk-Aware Product Decisions w/ Multiple Metrics*** (arXiv:2402.11609) | The **decision-rule** framework (success/guardrail-NIM/deterioration/quality); guardrails-NIM need no α-correction but Type-II correction. *(= the formerly image-only Spotify PDF, now full text.)* → platform-engineering.md + sample-size note. |
| ✅ | 📊 | Schultzberg 2026 — *Are Optimal Multiple Testing Corrections Optimal for You?* (Confidence) | **Why Bonferroni**: closed-form sizing (α/S over *success only*), simultaneous CIs, pairs with group-sequential; FWER vs FDR. |
| ⬜ | 📄 | Schultzberg et al — *Multiple-testing corrections* paper (arXiv:**2604.09256**) | the paper behind the MTC blog (full simulations). **acquire.** |
| ✅ | 📄⭐ | **Nordin & Schultzberg 2024 — *Precision-based designs for sequential experiments*** (arXiv:2405.03487; filed §04) | **Fixed-Power / Fixed-Width-CI designs**: stop at a target precision/power without pre-specifying variance; peeking at variance is FPR-safe. → power monitoring; notation/anytime-valid.md. |
| ✅ | 📄⭐ | Kohavi et al 2026 — *Power Analysis is Essential* | Power discipline: $n\approx16\sigma^2/\delta^2$, MDE, SRM, Type-S/M exaggeration, winner's curse, FPR. **Processed** → [`notation/power-mde.md`](notation/power-mde.md). Co-authors incl. Gelman, Imbens. |
| ✅ | 📄⭐ | Gelman & Carlin 2014 — *Beyond Power Calculations: Type S & Type M Errors* | The exaggeration / winner's-curse paper → [`notation/power-mde.md`](notation/power-mde.md) §4. |
| ✅ | 📄 | Deng, Knoblich & Lu 2018 — *Delta Method in Metric Analytics* (KDD) | Variance for ratio metrics (randomize-by-user, analyze-by-event) → correct power. |
| ✅ | 📄⭐ | Larsen et al 2023/24 — *Statistical Challenges in OCEs: A Review* (Amer. Statistician) | Comprehensive A/B-methodology review — the platform-ops anchor. _(unprocessed — worth a takeaways pass)_ |
| ✅ | 📄 | Nie et al 2022 — *Ensure A/B Test Quality at Scale: Randomization Validation & SRM Detection* (eBay, CIKM) | SRM + PSI via sequential analysis → the SRM guardrail (EVENT_LOG §6.6). |
| ⬜ | 📄 | **Power cluster (still ⬜):** Cohen 1988/1992 · Button et al 2013 · Simonsohn 2015 · Benjamin et al 2017 (α=0.005) · Azevedo et al 2020 (fat tails) · van Belle 2008 · **Kohavi–Tang–Xu 2020 (book)** | The remaining references. |
| ✅ | 📄⭐ | Feit & Berman 2019 — *Test & Roll: Profit-Maximizing A/B Tests* | **Decision-theoretic sample size**: test small, roll the winner; $n^*\propto\sqrt N\,s/\sigma$ (≪ NHST). **Processed** → [`notation/test-and-roll.md`](notation/test-and-roll.md). = Vega's ramp + OEC. |
| ✅ | 📄 | Kawato & Sakaguchi 2026 — *Prior-Free Sample Size for Test-and-Roll* | Prior-free WMB rule → **rule of thirds** $m\approx N/3$. Processed → same sheet. |
| ✅ | 📄 | Ng & Imbens 2026 — *Scalable Decisions: a Bayesian Decision-Theoretic Approach* | Multi-metric launch decisions. |
| ✅ | 📊 | Spotify — *Risk-Aware Product Decisions with Multiple Metrics* | Decision rules across metrics. |
| ⬜ | 📚 | Kohavi, Tang & Xu 2020 — *Trustworthy Online Controlled Experiments* | The practitioner bible (SRM, guardrails, OEC). |
| ⬜ | 📄 | Deng, Xu, Kohavi & Walker 2013 — *CUPED* | Variance reduction → `inference/cuped.py`. |

## 06 · Evaluation funnel & ranking → Game B, eval leg, `inference/ope.py`, `hte.py`
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📄 | Schultzberg & Ottens 2024 — *Navigating the Evaluation Funnel* | verify→validate; interleaving; counterfactual logging. |
| ✅ | 📊 | Spotify — *Better Experiments with LLM Evals* | Evals as proxies needing offline-online calibration. |
| ✅ | 📄 | Zhang et al 2026 — *Interleaving & Counterfactual Eval for Airbnb Search* (KDD'25) | +100× sensitivity ranking eval. |
| ⬜ | 📄 | Dudík, Langford & Li 2011 — *Doubly Robust Policy Evaluation* | IPS/DR → `inference/ope.py`. |
| ⬜ | 📄 | Swaminathan & Joachims 2015 — *Self-normalized estimator / CRM* | OPE for ranking. |
| ⬜ | 📄 | Wager & Athey 2018 (Causal Forests); Athey, Tibshirani & Wager 2019 (GRF) | → `inference/hte.py`. |
| ⬜ | 📄 | Künzel et al 2019 — *Metalearners (S/T/X)* | CATE recipes to compare. |

## 07 · Demand, pricing & LLM agents → calibration anchors; Phase-3 verticals; "AI products" signal
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📄 | Bach et al 2026 — *Adventures in Demand Analysis Using AI* | Multimodal embeddings + DML for price elasticity. |
| ✅ | 📄 | Zhang et al 2026 — *Agentic Economic Modeling* (Chernozhukov) | LLM synthetic choices → bias-corrected demand/τ. Relates to our MNL agent + ground truth. |

## 08 · Personalization & platform craft → dashboard framing; recommendation spillover
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📄 | Holtz 2020 — *Engagement-Diversity Connection* (Spotify) | Personalization spillover/interference field experiment. |
| ✅ | 📊 | Spotify — *Experimenting with ML to Target In-App Messaging* | ML targeting + experimentation. |
| ✅ | 📊 | Spotify — *Why We Use Separate Tech Stacks…* | Architecture/governance. |
| ✅ | 📊 | Spotify — *Encouragement Designs and Instrumental [Variables]* | IV when you can't force exposure. |
| ⬜ | 📄 | Angrist, Imbens & Rubin 1996 — *Identification of Causal Effects Using IV* | LATE; behind encouragement designs. |
| ⬜ | 📊 | Zalando (ExpAn) / Trivago — platform & auction context | Phase-3 vertical framing. |

## 09 · Long-term & surrogates → short- vs long-term OEC split, surrogate modeling (B-15)
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📄 | Lal, Imbens & Hull 2026 — *Long-Term Causal Inference with Many Noisy Proxies* | Surrogates via regularized regression. |
| ⬜ | 📄 | Athey, Chetty, Imbens & Kang 2019 — *The Surrogate Index* | The theory behind the above. |

## 10 · Incrementality & attribution (JD-critical leg; **no PDFs yet**) → `inference/incrementality.py`, `validation/criteo.py`
| | Kind | Doc | Why |
|---|---|---|---|
| ⬜ | 📄 | Johnson, Lewis & Nubbemeyer 2017 — *Ghost Ads* (JMR) | The incrementality method. |
| ⬜ | 📄 | Johnson, Lewis & Nubbemeyer — *Ad Effectiveness Funnel & Carryover* (meta) | Effect-size/carryover calibration. |
| ⬜ | 📄 | Lewis & Rao 2015 — *Unfavorable Economics of Measuring Ad Returns* (QJE) | Why incrementality is hard → why our ground truth is valuable. |
| ⬜ | 📄 | Diemert et al 2018 — *Criteo Uplift dataset* | The real-data validation leg. |

## 11 · HTE — metalearners & causal forests → `inference/hte.py`, `inference/ope.py`, Game B targeting/eval
Equation sheets: [`notation/metalearners.md`](notation/metalearners.md), [`notation/causal-forests.md`](notation/causal-forests.md); cluster note [`papers/hte-metalearners-forests.md`](papers/hte-metalearners-forests.md).
| | Kind | Doc | Why |
|---|---|---|---|
| ✅ | 📄⭐ | Athey, Tibshirani & Wager 2019 — *Generalized Random Forests* (Annals) | The causal-forest primary source; forest = adaptive kernel solving local moments. |
| ✅ | 📄 | Xu et al 2022 — *Treatment Heterogeneity for Survival Outcomes* (`survlearners`) | Metalearner (S/T/X/R) guidance, survival setting; Wager co-author. |
| ✅ | 📄 | Sverdrup & Wager 2024 — *Right-censored HTE using grf* | `causal_survival_forest` (RMST CATE). |
| ✅ | 🔗 | **grf guide** — grf-labs.github.io/grf/articles/grf_guide.html | Practical causal-forest API (RATE/AUTOC, BLP, DR scores). |
| ✅ | 🔗 | **CausalML** — causalml.readthedocs.io | Uber's uplift/metalearner Python library. |
| ✅ | 📄⭐ | Künzel, Sekhon, Bickel & Yu 2019 — *Metalearners* (PNAS) | The S/T/X-learner primary paper. |
| ⬜ | 📄 | Nie & Wager 2021 — *Quasi-oracle estimation* (R-learner); Kennedy 2023 (DR-learner) | Orthogonal CATE recipes (primary). |

## 12 · Platform engineering & operations → the chassis (processed 2026-06-04) → [`papers/platform-engineering.md`](papers/platform-engineering.md)
The "steal for platform building" pass. All ✅ processed into the **platform-engineering playbook** (organized by chassis component) unless noted. PDFs filed under `08-…/` (platform craft) and `04-…/` (peeking).
| | Kind | Doc | Steal |
|---|---|---|---|
| ✅ | 📊 | Netflix — *Design Principles for Math-Engineering in the Experimentation Platform* | primitives+composition; graduation pipeline; introspectable stages; Arrow. |
| ✅ | 📊 | Netflix — *Reimagining Experimentation Analysis* | **Metrics Repo** (code→JSON→on-demand SQL, no backfill); 2-fn estimator; Plotly-JSON viz. |
| ✅ | 📊 | Stitch Fix — *Building our Centralized Experimental Platform* | #oneway; one assignment service; owned/auditable metric defs + BYOD; meta-analysis. |
| ✅ | 📊 | DoorDash — *Curie / Experimentation Analysis Platform* | exposure-event lifecycle; JinjaSQL + dedup CTE; async + on-demand recompute; typed stats; built-in SRM. |
| ✅ | 📊 | Squarespace — *How We Reimagined A/B Testing* | Praetor subject-abstraction; opinionated stats lib; A/B-form gate + test log. |
| ✅ | 📄 | Fabijan et al 2021 (SEAA) — *It Takes a Flywheel to Fly* | value↔investment flywheel; **Entrance/Exit reviews**; measure-the-program; maturity. |
| ✅ | 📄 | *First Practical OCE Summit 2019* (SIGKDD, 13 orgs) | OEC design+validation (labeled corpus/degradation); metric taxonomy; interference frontier; layers+additivity. |
| ✅ | 📄 | *Open Guide to A/B Testing* (GrowthBook) | trust-pitfalls catalog; named laws (Twyman/Goodhart/Simpson); win-rate-is-a-trap; traffic-light guardrails. |
| ✅ | 📄 | **Ng & Imbens 2026** — *Scalable Decisions* (also §05) | decision-theoretic launch rule + trade-off vector $\Lambda$; guardrail=inflated $\lambda$; hierarchical prior (+38%). |
| ✅ | 📄 | **Nie et al 2022** — *SRM detection* (eBay; also §05) | **sequential SRM** (precision 28%→95%); PSI randomization gate; 4-way diagnostic. |
| ✅ | 📄 | **Schultzberg & Ottens 2024** — *Eval Funnel* (also §06) | verify→validate funnel as the lifecycle; necessary/sufficient; sequential for abort only. |
| ✅ | 📄 | **Larsen et al 2023** — *OCE Challenges review* (also §05) | metric taxonomy; A/A+SRM as trust gates; sequential lineage; triggered/diluted effects. |
| ✅ | 📊 | Etsy — *How Etsy Handles Peeking* (filed §04) | the **scorecard state→message vocabulary**; CI color-bar; early-stop haircut + 7-day min. |
| ✅ | 🔗 | Evan Miller ×2 — *How Not To Run an A/B Test* · *Simple Sequential A/B* (§04) | peeking inflation; $n=16\sigma^2/\delta^2$; gambler's-ruin boundary $d^*\approx2.25\sqrt N$. |
| ✅ | 📄 | Deng & Lu 2016 — *Continuous Monitoring without Pain* (`1602.05549`, §04) | optional-stopping validity thm; FDR vs Type-I; LIL; **proper-stopping invariant**. |
| ✅ | 🔗 | Variance-Explained · Convoy — *Bayesian A/B & peeking* (§04) | Bayesian stopping still inflates Type-I; expected-loss stop + switching cost δ; prior-calibration caveat. |
| ✅ | 📄 | Spotify — *Risk-Aware Product Decisions w/ Multiple Metrics* | guardrails as non-inferiority; ship = conjunction. **Resolved 2026-06-07**: arXiv:2402.11609 text version now in §05 (the image-only blog PDF is superseded). |
| ✅ | 📄 | Deng et al 2013 — **CUPED** original (filed §05) | ANCOVA equiv ($1-R^2$); ratio-CUPED via delta; missing-coverage; triggered covariates; validity guard. → metrics layer. |

## 13 · DGP simulation methodology → Vega DGP zoo (processed 2026-06-04) → [`notation/frugal-parameterization.md`](notation/frugal-parameterization.md)
| | Kind | Doc | Steal |
|---|---|---|---|
| ✅ | 📄⭐ | Evans & Didelez 2024 — *The Frugal Parameterization* (JRSS-B) | author a DGP whose **ATE/CATE is a primitive**; confounding as a free dial; swap estimands via cognate kernels. |
| ✅ | 🔗 | Orduz — *Frugal Parameterization in PyMC* | worked Bayesian recipe; priors on the effect + copula dependence. |

## Cluster-robust SE pass (processed 2026-06-04) → [`notation/cluster-robust-se.md`](notation/cluster-robust-se.md)
Cameron–Miller 2015 · MacKinnon 2022 · sandwich-CL ✅ processed (CV1/CV2/CV3 + wild cluster bootstrap + few-clusters) → feeds **NB 04**.

---

## Suggested reading order
1. **Frame:** Vinted/Glovo interference + Holtz 2024 + skim Kohavi book → state the thesis cold.
2. **Core methods:** Johari 2021 + Masoero 2025 (interference) → DML (CCDDHNR 2018 / Ahrens 2026) →
   Hansen 2025 (cluster SEs) → Howard 2022 + Johari 2017 + Spotify Peeking 2.0 (anytime-valid).
3. **Incrementality:** Ghost Ads + Lewis-Rao (acquire first).
4. **Ranking leg:** Wager-Athey + DR policy eval + Zhang 2026 interleaving + Schultzberg-Ottens.
5. **Theory/long-term backfill:** Hudgens-Halloran, surrogate index, Auto-DML.

## Acquisition links
Best-effort identifiers; verify the version before citing. Drop the PDF in the listed folder and flip `⬜`→`✅`.

- **DML originals** (`01-causal-ml-dml/`): CCDDHN 2017 `arXiv:1701.08687` · DoubleML-JMLR `arXiv:2104.03220` ·
  Auto-DML `arXiv:1809.05224` · Semenova-Chernozhukov `arXiv:1912.12945`.
- **Interference** (`02-…/`): Glovo cluster (blog) · LinkedIn budget-split (search "Trustworthy Online
  Marketplace Experimentation Budget-split") · Hudgens-Halloran 2008 (JASA) · Aronow-Samii 2017 (AOAS) · Vinted (blog).
- **Cluster-robust SEs** (`02-…/cluster-and-network/`, → NB 04): Cameron & Miller *Practitioner's Guide*
  (J.Human Resources 2015) · MacKinnon, Nielsen & Webb 2023 *Guide to Empirical Practice* (J.Econometrics) ·
  MacKinnon & Webb 2023 *Fast & Reliable Jackknife/Bootstrap* · Hansen 2025 *Jackknife SEs for DiD*.
  Libraries: `pyfixest`, `wildboottest` (py); R `fwildclusterboot`/`fixest`/`sandwich`/`summclust`.
- **Switchback** (`03-switchback/`): DoorDash switchback posts 2018/2019.
- **Anytime-valid** (`04-…/`): Waudby-Smith et al `arXiv:2103.06476` · Netflix design-based CS `arXiv:2210.08639` · Lan-DeMets 1983 · Jennison-Turnbull (book).
- **Power/decisions** (`05-…/`): **Kohavi-Tang-Xu 2020 (the bible)** · CUPED (Deng et al 2013, WSDM) · Gelman–Carlin 2014 (Type S/M) · Cohen 1988 · Button et al 2013 · Simonsohn 2015 · Benjamin et al 2017 · Deng–Knoblich–Lu 2018 (Delta method) · Azevedo et al 2020 · van Belle 2008 (rules of thumb).
- **DiD / event-study** (Phase-3; → new `12-did-panel/` on first drop): Callaway–Sant'Anna 2021 · Sun–Abraham 2021 · Borusyak–Jaravel–Spiess 2024 · de Chaisemartin–d'Haultfœuille 2020 · Arkhangelsky et al. 2021 (SDID) · Abadie et al. 2010 (synthetic control). Map to `pyfixest`/`differences`.
- **OPE** (`06-…/`): Dudík et al `arXiv:1103.4601` · Swaminathan-Joachims 2015.
- **HTE metalearners** (`11-…/`, primary sources): Wager-Athey 2018 (JASA) · Nie-Wager 2021 (R-learner) · Kennedy 2023 (DR-learner). _(GRF 2019 ✅, Künzel et al 2019 ✅ owned.)_
- **Personalization/IV** (`08-…/`): Angrist-Imbens-Rubin 1996 (JASA).
- **Long-term** (`09-…/`): Athey-Chetty-Imbens-Kang `arXiv:1603.09326`.
- **Incrementality** (`10-incrementality-attribution/`): Ghost Ads (SSRN 2620078) · Lewis-Rao 2015 (QJE) · Criteo Uplift (Diemert et al 2018).
- **PyMC-Labs / Bayesian-causal** (→ new `11-bayesian-causal/` on first drop): CausalPy `causalpy.readthedocs.io` ·
  PyMC `pymc.io` · pymc-marketing `pymc-marketing.io` · PyMC example gallery (Causal Inference).
