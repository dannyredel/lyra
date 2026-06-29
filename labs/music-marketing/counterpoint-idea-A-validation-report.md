# Validation Report: Counterpoint (working name)

**Date:** 2026-06-20
**Pipeline depth:** Deep
**Idea classification:** B2B SaaS (services-led hybrid) · Napkin / pre-validation · Adjacent→disruptive-within-music · Pure commercial
**DVF weighting:** 35 Desirability / 30 Viability / 35 Feasibility *(moved off the 40/30/30 default because identification risk is co-equal with demand risk)*

> **What this is:** an independent, cross-platform, causal marketing-measurement layer for the music industry — one defensible per-release lift figure (incremental streams net of organic baseline, marginal ROAS by channel) for indie distributors and label-services companies. Sold services-first, productized on repetition.

---

## 🎯 Executive Summary

**Recommendation: PARK — with a defined, ~€0, ~6-week path to GO WITH PIVOTS.**

**Composite Score: 63/100 · Confidence: 37/100**

| Lens | Score | One-line read |
|---|---|---|
| 🟡 Desirability | 62/100 | Structurally real problem, soft felt-severity, inertia-bound switching |
| 🟡 Viability | 58/100 | Small TAM, base-healthy/bear-broken unit economics, a pricing paradox |
| 🟢 Feasibility | 68/100 | Bootstrappable + fast MVP lift it; identification-under-scarcity drags it |

**The thesis in one paragraph:**
Indie aggregators spend six figures a year on paid ads they can't causally measure, because every ad platform self-reports and over-attributes, and the conversion event is locked inside DSP walled gardens. Counterpoint sells the one measurement they can't buy from the platform taking their money: an independent, cross-platform, causal lift number, made possible by roster-level pooling of the aggregator's own first-party data. The main bet is that (a) the method can produce a *defensible* number under severe data scarcity, and (b) a slow, price-anchored buyer will pay 10–100× their current analytics spend for it.

**Top 3 reasons to pursue:**
1. The competitive quadrant (independent × causal × music) is genuinely empty — verified across multiple 2026 industry roundups.
2. Services-first GTM makes the venture bootstrappable and the MVP fast and cheap — the team can validate without funding.
3. The two assumptions most likely to kill it (identification, willingness-to-pay) are testable now for almost nothing, so expected information value per euro is extremely high.

**Top 3 reasons it could fail:**
1. The model may not *identify* credible effects under collinear, short-lived, thin per-release data — the "defensible number" may not be defensible.
2. Demand is inertia-bound: free incumbent dashboards, low awareness, high adoption-anxiety, and a brutal price anchor ($10–$1,400/yr analytics vs €6k–€144k/yr ask).
3. The pricing model is indexed to ad spend, which the product's own success reduces — and a funded generalist could enter the pond in 12–18 months.

**The single most important next step:**
Run the **Vega identification study** on synthetic rosters — can the estimators recover planted effects under realistic music data pathologies? It costs ~€0, needs no customer, and gates the entire venture. If it fails, KILL cleanly; if it passes, the venture's central feasibility risk drops sharply.

---

## 🟢 Green Lights / 🔴 Red Flags

| 🟢 Green Lights | 🔴 Red Flags |
|---|---|
| Empty competitive quadrant, verified | Price anchor is 10–100× current analytics spend |
| Over-attribution is a structurally real, documented phenomenon | Demand felt weakly; forces of progress favor inertia (switching ~45/100) |
| Services-first = bootstrappable, fast/cheap MVP | Identification under scarcity is research-grade and unproven |
| Strong founder fit on the hard (modelling) side | Pricing indexed to the spend the product reduces |
| Spotify lockdown strengthens the "buyer is the data source" moat | Small TAM (~€50–200M); boutique ceiling |
| Cheapest, most decisive test is runnable today | Moat is thin and time-boxed; no cross-customer network effect yet |

---

## 📊 Validation Scorecard

### Desirability (35% weight) — 62/100

| Sub-score | Weight | Score | Rubric anchor | Evidence |
|---|---|---|---|---|
| Problem severity | 25% | 60 | "Real but tolerable — users get by" | §1 — large €-stakes, weak felt-severity (invisible counterfactual) |
| Problem frequency | 15% | 60 | "Weekly" | §1 — continuous releases, episodic *measurement* decision |
| Job clarity | 15% | 60 | "Multiple jobs bundled — needs decomposition" | §1.3 — allocate / defend / recoup |
| ICP specificity | 15% | 72 | "Two of three filters + named persona" | §2 — tightened by the scale floor |
| Value-prop fit | 20% | 70 | "≥80% of top pains addressed" | §3 — functional pains relieved; anxiety pains not product-addressable |
| Switching willingness | 10% | 45 | "Aware, no urgency → status quo fine" | §1.4 — forces favor inertia |

### Viability (30% weight) — 58/100

| Sub-score | Weight | Score | Rubric anchor | Evidence |
|---|---|---|---|---|
| Market size (TAM) | 15% | 45 | "€10M–€100M" | §4 — small, boutique-scale |
| Obtainable market (SOM) | 20% | 55 | "€1M–€10M" | §4 — ~€2–3M, capture-dependent |
| Market growth | 10% | 58 | "5–15% CAGR" | §4 — recorded music ~6%; measurement category nascent |
| Unit economics | 25% | 58 | "LTV/CAC 3–5; payback 6–12mo" (base) | §6.3 — bear case breaks; GM below SaaS |
| Competitive density | 15% | 78 | "Greenfield" (temporary) | §5 — empty quadrant |
| Differentiation defensibility | 15% | 58 | "Clear differentiation, replicable 12–18mo" | §5 — no structural moat yet |

### Feasibility (35% weight) — 68/100

| Sub-score | Weight | Score | Rubric anchor | Evidence |
|---|---|---|---|---|
| Technical complexity | 25% | 50 | "Custom infra / novel integration → research-grade" | §3.3, §8 — identification under scarcity is the crux |
| Team-idea fit | 20% | 72 | "Two of three" | §9 — strong modelling; commercial single-point-dependent |
| Time to MVP | 15% | 78 | "1–3 months" | §9 — services MVP on partner back-data |
| Capital intensity | 20% | 80 | "Bootstrappable / pre-seed" | §6 — services-first self-funds |
| Regulatory/legal | 10% | 70 | "Standard GDPR-tier + some platform-ToS exposure" | §8 — data processing + S4A/ad-platform terms |
| Go-to-market clarity | 10% | 62 | "Clear primary, plausible secondary" | §9 — network is finite |

### Auxiliary meters
- **RISK: 70/100 (high)** — nine criticals (severity ≥12), but the top three are cheap to test.
- **DIFFERENTIATION: 68/100** — sharp positioning, thin structural defensibility.
- **CONFIDENCE: 37/100** — zero primary validation yet; the most fixable kind of low confidence.

---

## 1. Problem Definition

### 1.1 Problem statement
- **As-is:** Aggregators allocate six-figure annual ad budgets across Meta/TikTok/Spotify/playlist pluggers, deciding from each platform's self-reported ROAS plus gut feel about "momentum"; post-campaign they reconcile five dashboards that each claim the same plays.
- **Pain:** They can't separate caused streams from organic-that-would-have-happened; over-attribution means the dashboards collectively overcount; the result is silent misallocation and an inability to *defend* allocation to MDs/boards/artists.
- **Desired:** one independent, cross-platform number per release — incremental lift net of baseline, marginal ROAS by channel.
- **Gap:** three structural gaps (scale threshold; DSP-walled-garden conversion; no in-house econometrics at labels) *plus* one dangerous soft gap — **status-quo tolerance** (the upside-down royalty economics may be accepted as the cost of streaming rather than felt as a fixable problem).

### 1.2 Root cause (5 Whys)
Labels can't tell if spend caused anything → platforms self-attribute and overcount → the conversion happens inside a DSP with no cross-platform ground truth → user tracking dies at the ad→smart-link→DSP handoff and DSPs don't expose conversion data → **structural root: the e-commerce measurement stack never got built for music because the conversion is third-party-locked and per-advertiser spend was too fragmented to justify it — until aggregator consolidation + the data lockdown made the aggregator the only viable data holder.**

*Note:* the method (MMM, geo-lift) is not newly possible — it is years old. What is new is **data structure and competitive positioning**. Frame "why now" on that, not on "the math just matured."

### 1.3 Jobs-to-be-Done
- **Functional:** "When allocating next quarter's release budget, I want to know which spend drives durable listeners, so I can move money where it compounds."
- **Emotional:** stop feeling like I'm setting money on fire; stop being the platforms' upsell target.
- **Social:** be seen as a data-driven operator vs. the majors' data teams; defend decisions without being challenged.
- **Decomposition (key insight):** the job splits into **allocate** (invisible value), **defend/justify** (immediate felt value, clearest WTP), and **recoup/underwrite** (highest WTP, later). Lead with *defend*.

### 1.4 Forces of Progress
| Push (away) | Pull (toward) |
|---|---|
| Dashboards visibly conflict | One independent number platforms can't sell |
| Margin/streaming pressure | Cross-platform single truth |
| Board/MD asking "prove marketing works" | Deck-ready defensible figure |

| Anxiety (about adopting) | Habit (inertia) |
|---|---|
| Is the method credible or a black box? | Incumbent dashboards are free & there |
| Hand over all royalty + ad data? | Spotify Marquee lift is free & built-in |
| What if it says my past calls were wrong? | "Momentum is a vibe we trust" |

**Net force:** Push + Pull likely does **not** exceed Habit + Anxiety for the median label. Switching requires a high-push trigger *and* anxiety defused (legible method + frictionless data-sharing + "find upside" framing, not "audit").

### 1.5 Falsifiability
Wrong if ≥7/10 discovery leads say current dashboards are "good enough," or revisit allocation ≤once/year, or treat upside-down economics as "just how streaming works."

---

## 2. Target Customer

### 2.1 Primary ICP
| Filter | Value |
|---|---|
| Firmographic | Indie distributor / label-services co., ~50–150+ releases/yr, **€150k–€1M+ annual ad spend**, EU (DACH first), owns first-party distribution + ad data |
| Behavioral | Cross-platform paid; uses Chartmetric/Soundcharts; per-release allocation; S4A exports; smart links; revisits allocation ≥quarterly |
| Psychographic | "Pragmatist behind the majors" — data-curious, margin-pressured, wants to professionalize |
| Buying trigger | Board/investor ROI pressure; an expensive release that disappointed |
| Where they are | Label/distributor industry events; LinkedIn; trade press |

**Scale-floor finding:** at the cited ~€50k/month (~€600k/yr) incrementality threshold — independently corroborated by the industry's ~$100k/yr "keep it simple below this" rule — only Distributor/Catalog/top-of-Label tiers clear it. **The real ICP starts ~€150k/yr ad spend.** Sub-€150k labels are below the method's floor (decision: kept as a *descriptive-lite* upgrade funnel, not a causal product).

### 2.2 Persona — "Lena, Head of Performance, mid indie distributor (Berlin)"
~50 releases/yr, ~€350k ad budget, reports to MD. Trigger: a €40k priority-release push she can't attribute, and an MD now demanding roster-wide ROI ahead of an investor conversation. In her voice: *"I run five dashboards that each tell me I'm a genius. I don't believe any of them, and I can't tell my MD which €100k actually worked."* Tried: cost-per-stream spreadsheets, trusting Meta ROAS, a stale agency readout.

### 2.3 Anti-personas
1. Individual artists / managers (no roster, no data ownership).
2. Major labels (in-house data science; procurement).
3. Sub-€100k/yr-spend labels (below the method floor).
4. Pure catalog/sync companies (no live campaigns).

### 2.4 Buyer / User / Blocker
- **Buyer:** MD / Head of Commercial (ROI, recoupment, defensibility).
- **User / Champion:** performance lead (allocation, looking smart).
- **Blockers:** (a) data/ops/legal ("you want all our data?"); (b) **the champion is also the person the truth can embarrass** — the tool can audit its own internal sponsor.

### 2.5 Falsifiability
Wrong if WTP lives at the top of the ladder (A&R buying recoupment) not the MMM wedge — *or* if the data sits in an ops silo the buyer can't release internally (breaking the "buyer is the data source" thesis).

---

## 3. Solution & Value Proposition

### 3.1 Value Proposition Canvas (Track A)
| Customer side | | Solution side |
|---|---|---|
| Jobs: defend / allocate / recoup | ↔ | Per-release scorecard; portfolio allocation readout; one independent lift number |
| Pains: caused-vs-organic blindness; 5 conflicting ROAS; data-sharing & political-exposure anxiety | ↔ | Caused-vs-organic decomposition; cross-platform unification; independence — **but anxiety pains are not product-addressable** |
| Gains: trusted number; reallocation that recovers waste; the organic→paid multiplier | ↔ | Marginal ROAS; deck-ready figure; multiplier + half-life (delight, but double-edged) |

### 3.2 Value Proposition Statement
> For indie distributors spending €150k+/yr on release marketing, who can't tell which spend *caused* durable listeners, **Counterpoint** is an independent cross-platform causal-measurement layer **that** turns five conflicting platform ROAS numbers into one defensible per-release lift figure — **unlike** Chartmetric (descriptive) or Spotify Campaign Kit (self-reported) — **because** it's the only measurement a label can't buy from the platform taking its money.

### 3.3 Riskiest Assumption Test (re-ranked from the team's own §10)
| # | Assumption | Type | L×I | Cheap test | Falsification threshold |
|---|---|---|---|---|---|
| 1 | Identification under collinearity | Feas (S) | 16 | Vega synthetic-roster recovery | 80% CI on median channel ROAS spans break-even across realistic DGPs |
| 2 | Data access reliability | Surv (S) | 15 | Ask each prospect to pull a sample export in a week | <3/10 can without engineering escalation |
| 3 | Organic→paid multiplier estimable | Value+Feas | 15 | Event-study on one historical release | Multiplier CI includes zero |
| 4 | WTP at music scale | Value (V) | 15 | Present value-decoupled pricing + worked ROI; seek LOI | ≥7/10 react "that's 9% of my budget" |
| 5 | Geo-lift feasibility | Feas (S) | 12 | Power-analyze one clean territory split | <80% power on ≥1 channel |

**Missed by §10:** champion-exposure; within-roster-only pooling (no cross-customer learning); ownership ≠ usability.

---

## 4. Market

### 4.1 Sizing (TAM / SAM / SOM)
- **Bottom-up:** ~1,000–1,500 qualifying EU aggregators (~3,000–5,000 global) × ~€30k blended ACV → **TAM ~€90–150M; SAM (EU) ~€30–45M; SOM (3-yr, ~90 accounts) ~€2–3M.**
- **Top-down sanity:** indie recorded music ≈ 0.43 × $31.7B ≈ $13.6B; measurement is a sub-1% sliver → low-hundreds-of-€M ceiling. **Triangulates within ~2×.**
- **Sensitivity:** SAM spans ~€8M–€68M on ±50% of account count and ACV → confidence moderate.

**Read:** small TAM / boutique SAM, *consistent with the stated boutique ambition*. The constraint is capture in a thin market, not headroom. The qualifying-account count is a Fermi estimate (not a verified census) — worth confirming against MIDiA's distributor survey.

### 4.2 Market dynamics
- Stage: emerging (causal measurement category nascent in music). Recorded music CAGR ~6%; independents growing faster than the total.
- Tailwinds: data-lockdown forcing first-party models; margin pressure; general maturation of causal measurement.
- Headwinds: price anchor; low awareness; consolidation reducing buyer count.

### 4.3 Geographic priority
Tier 1: DACH (co-founder network). Tier 2: UK, Benelux, Nordics. Tier 3: US (larger but more competitive, generalists closer).

---

## 5. Competitive Landscape

### 5.1 Clusters (verified)
| Cluster | Players | State |
|---|---|---|
| Music-native, descriptive | Chartmetric, Soundcharts, Songstats, Viberate, Artist.tools | Dashboards: monitoring, reporting, A&R. Priced $10–$1,400/yr |
| Generic, causal | Recast, Measured, Haus, Triple Whale, Northbeam + OSS (Meridian, Robyn, PyMC-Marketing) | Triangulate MMM + incrementality + attribution; none music-specific |
| Music campaign tools | un:hurd, Spotify Campaign Kit | Automation / self-reported lift (un:hurd not independently re-verified) |
| Independent causal for music | — | **Empty** |

### 5.2 Indirect / substitute / do-nothing
**The do-nothing competitor is the strongest:** free platform dashboards + Spotify Marquee lift + gut feel. Zero switching cost. Plus DIY (a label hiring one analyst to run Meridian) and agency readouts.

### 5.3 Positioning map
- X-axis: descriptive ↔ causal. Y-axis: platform-dependent ↔ independent.
- Counterpoint sits alone in the **causal × independent** corner; closest neighbors (generic causal vendors) are one axis away and could move into music.

### 5.4 Blue Ocean — ERRC
| Eliminate | Reduce | Raise | Create |
|---|---|---|---|
| Platform self-attribution; 5-dashboard reconciliation; %-of-spend pricing | Attribution pillar; integration breadth; user-level tracking reliance | Independence/credibility; cross-platform unification; rigor under scarcity | Roster causal measurement; music estimands (multiplier, fan-LTV, recoupment); buyer-is-data-source model |

Passes Blue Ocean's three properties (focus, divergence, tagline) — **but it's a pond, not an ocean**: uncontested yet small and hard to fish.

### 5.5 Porter's Five Forces — structurally challenging
| Force | Level | Why |
|---|---|---|
| New entrants | Med-High | Methods open-source; barrier is relationships + domain, not math |
| Buyer power | High | Concentrated, slow, price-anchored; buyers hold the data; consolidating |
| Supplier power | High | Platforms (Spotify, Meta/TikTok) control the data; Spotify has restricted 3× in 18 months |
| Substitutes | High | Do-nothing dashboards, descriptive tools, agencies, DIY |
| Rivalry | Low (today) | Greenfield niche — temporary |

**Verdict:** four of five forces unfavorable; the favorable one (low rivalry) is a temporary greenfield. The opportunity rests on execution speed + relationship moat + first-mover, not industry economics.

---

## 6. Business Model

### 6.1 Lean Canvas
| Block | Content |
|---|---|
| Customer Segments | Mid+ indie distributors / label-services (€150k+ spend), DACH-first (+ descriptive-lite funnel) |
| Problem | Caused-vs-organic blindness; conflicting ROAS; unknown organic-lift trigger |
| Solution | Roster MMM scorecard; geo-lift ground-truth; calibration loop |
| UVP | "The only measurement a label can't buy from the platform taking its money" |
| Unfair Advantage | NI network (finite); causal-under-scarcity depth (head start); **no cross-customer network effect — moat must be built** |
| Channels | Warm intros → then unproven |
| Revenue | Spend-banded subscription + pilot + geo-lift add-ons |
| Cost Structure | Founder time; platform build; bespoke onboarding; analyst delivery; Bayesian compute |
| Key Metrics | design partners → paid pilots → pilot→annual conversion → NRR → hours/engagement → CAC by cohort |

### 6.2 Revenue model
Primary: spend-banded annual subscription (€6k–€96k+). Secondary: onboarding pilots (€8–15k one-time), geo-lift studies (€4–6k each). **Recommended pivot: decouple price from spend band** (flat value fee or share of waste recovered).

### 6.3 Unit economics (mid-tier, €350k spend, base case)
| Metric | Cash / warm | Loaded / blended |
|---|---|---|
| Subscription ACV | €24k | €24k |
| Gross margin | 60% | 55% |
| Contribution/yr | ~€14.4k | ~€13.2k |
| CAC | ~€4k | ~€8–15k |
| Churn (annual) | 15% (8–25%) | — |
| LTV (3-yr cap) | ~€43k | ~€40k |
| **LTV/CAC** | **~10+** | **~3 (bear ~1.4)** |
| Payback | ~3 mo | ~12 mo |

**Sensitivity (churn × GM × CAC dominate):** LTV/CAC ranges ~1.4 (bear) → ~3.5 (base) → ~10+ (bull). The spread is the risk. The two numbers a pilot must produce: actual annual retention and true loaded hours per geo-lift.

**Pricing paradox:** the fee is indexed to ad spend, which the product's success reduces — and if the category answer is "paid drives little durable lift," the revenue base erodes precisely because the product was right. Resolve via value-decoupled pricing + reallocation framing + climbing the non-spend-indexed ladder.

### 6.4 Revenue projections (founders' plan, treated as hypotheses)
| | Year 1 | Year 3 | Year 5 |
|---|---|---|---|
| Customers | a handful (pilots) | ~30–40 | ~90 |
| Revenue | ~€110k | ~€0.8–1.2M | ~€2.3M |

Boutique outcome by design (2 founders, bootstrapped). Caps upside; appropriate given the small TAM.

---

## 7. Theory of Change
**Skipped** — pure-commercial idea, no social-impact claim and no ≥3-hop impact chain. (Pipeline trigger not fired.)

---

## 8. Risk Register

### Critical risks (severity ≥12)
| Risk | Category | L×I | Mitigation |
|---|---|---|---|
| Identification fails under collinearity | Technical | 20 | Vega study first; aggregate-lift fallback |
| Demand soft / vitamin trap | Market | 15 | Trigger-segment discovery; "defend" framing |
| Price anchor unbreakable | Market | 15 | ROI framing; decouple price; LOI test |
| Geo-lift infeasible | Technical | 12 | Power-analyze first; MMM + Meta/TikTok geo |
| Multiplier unidentifiable | Technical | 12 | Historical event-study |
| Bear-case unit economics | Financial | 12 | Validate retention + delivery cost |
| Commercial single-point-dependency | Team | 12 | Transfer relationships; 2nd channel |
| Network saturation | Team/Growth | 12 | Prove non-network channel before scaling |
| Bespoke onboarding never standardizes | Operational | 12 | Pipeline tooling; track hours/engagement |

### Significant (severity 6–11)
TAM too small even for boutique (8); pricing paradox (9); funded generalist enters music (8); GDPR/data processing (6); platform-ToS exposure (8); founder focus split vs BeeSignal (9).

### Pre-mortem (June 2028, it failed)
1. Demand — elegant readouts, no renewals; a curiosity, not a dependency (30% churn).
2. Identification — intervals too wide to be actionable; the "defensible number" wasn't.
3. Competitive — a funded generalist added a music vertical in month 14.
4. Delivery — onboarding never standardized; 40 hrs/account; 35% margins; drowning at 30 accounts.
5. Founder — attention shifted to BeeSignal; network ran dry after ~18 intros.

**Implication:** saturation + focus-split + bespoke delivery compound into a stall; even a working model churns if it's a diagnostic rather than a dependency.

---

## 9. Execution

### 9.1 MVP definition
**Build:** roster MMM on one design partner's 12–24 months of back-data + one geo-lift; a single per-release scorecard. **Don't build yet:** the expansion ladder (fan-LTV, recoupment), descriptive-lite tier, automation. **Test of success:** a lift number with a usable credible interval that the partner agrees is decision-relevant, plus a paid pilot conversion.

### 9.2 Critical path
1. Vega identification study (gates everything).
2. 10 discovery conversations (trigger segment, data-pull, pricing reaction).
3. One historical-release event-study (multiplier recoverability).
4. One paid pilot + real geo-lift (only if 1–3 pass).

### 9.3 Team requirements
| Role | When | Critical or hire-later |
|---|---|---|
| Causal-inference / product (Daniel) | Now | Critical — strongest fit |
| Commercial / label relationships (co-founder) | Now | Critical — single point of dependency |
| Data/pipeline engineer | After pilot | Hire-later (the standardization bottleneck) |

### 9.4 Capital plan
Bootstrappable via services revenue (~€110k Y1 funds itself). No external round required — and the small TAM means none is warranted.

### 9.5 Go-to-market
- **Wedge:** the "defend" job for the trigger segment (labels under ROI pressure), DACH-first.
- **Channels:** warm intros (NI) first; a second channel (content/conferences/referrals) must be proven *before* scaling, since the network is finite.
- **First 10 customers:** founder-led, paid pilots converted from warm intros.

---

## 10. Decision

### Five-Gate assessment
| Gate | Pass/Fail | Why |
|---|---|---|
| 1. Problem real? | Pass (soft) | Structurally real, felt weakly |
| 2. Defensible position? | Marginal | Real but a pond; moat must be built |
| 3. Unit economics? | Pass-with-pivot | Base ok; needs price decoupled + retention proof |
| 4. Team can do it? | Pass | Buildable, fast, network access |
| 5. Best use of time? | Founder's call | Opportunity cost vs BeeSignal; boutique ceiling vs ambition |

### Recommendation: **PARK — with a defined, ~€0, ~6-week path to GO WITH PIVOTS**

**Why:** Composite 63 with Confidence 37 lands formally in PARK. But the low confidence is entirely attributable to *unrun, cheap, decisive tests* — not bad evidence. The expected information value of the €0/6-week battery is the highest-leverage action available. Don't build or commit; run the tests; let them flip the call.

### Proposed pivots (apply if the tests pass)
1. **Value-capture pivot** — price decoupled from spend band.
2. **Customer-segment pivot** — narrow to the high-push trigger segment.
3. **Customer-need pivot** — lead with the defend job, not the optimize job.
4. **Business-architecture pivot** — secure rights to learn across customers (the only compounding moat).

### Conditions to revisit / unlock GO
- Vega identification recovers planted effects with usable intervals.
- Discovery finds a trigger segment with WTP on value-decoupled pricing.
- A pilot shows retention >85% and standardizable geo-lift delivery.

### What would change this assessment
- Identification works → Feasibility re-rates up, → GO WITH PIVOTS.
- Identification fails → clean KILL.
- A funded generalist enters music → first-mover speed becomes existential.

---

## Appendix A: Sources & citations
1. Spotify for Developers — Quota Modes (250k MAU extended-access criteria). developer.spotify.com/documentation/web-api/concepts/quota-modes
2. Spotify for Developers — "Update on Developer Access and Platform Security," 6 Feb 2026 (Development Mode reduction; postponement update).
3. TechCrunch — Spotify Developer Mode API changes; Nov 2024 endpoint cuts (audio features, label info, popularity).
4. House of Martech — "Marketing Measurement 2026" (combined platform ROAS exceeds actual growth; over-attribution).
5. Measured — "Incrementality vs Attribution vs MMM decision tree" (triangulation as standard practice).
6. DigitalApplied — "Marketing Mix Modeling 2026" (78–104 weeks data; ~10 obs/variable).
7. Haus — "Open Haus #2" (smaller brands <~$100k/yr should keep measurement simple).
8. Orphiq — "Best Music Analytics Tools 2026" (Chartmetric/Soundcharts descriptive).
9. Orphiq — "Chartmetric vs Soundcharts vs Songstats."
10. Chartlex — "Best Chartmetric Alternative 2026" (analytics pricing).
11. Music24 — "Best Playlist Data Analysis Tools 2025" (Soundcharts pricing).
12. Music Business Worldwide — IFPI: global recorded music $31.7B in 2025, +6.4% YoY.
13. MIDiA Research — independents ~43% of market (ownership basis).
14. MIDiA / Music Industry Blog — ~13,000 non-major labels; superstar economy.
15. DJ Mag — major-label consolidation (UMG–Downtown–FUGA; EC Statement of Objections, Nov 2025).

*Confidence flags: Spotify lockdown — high (official source), but the "bans training on its data" sub-claim is unverified (medium-low). Empty-quadrant claim — medium-high (absence across multiple recent roundups). Qualifying-account count — Fermi estimate, not a census (low-medium).*

## Appendix B: Assumptions log
| Assumption | Confidence | Sensitivity | How to test |
|---|---|---|---|
| Identification works under scarcity | Low | Binary on viability | Vega study |
| WTP at 10–100× analytics anchor | Low | High | Discovery + LOI |
| Annual retention >85% | Unknown | High on LTV | Pilot |
| Buyer can release own data | Medium | High on onboarding | Discovery data-pull |
| Organic→paid multiplier estimable | Low-medium | Medium | Event-study |
| ~1,000–1,500 EU qualifying accounts | Low-medium | High on TAM | MIDiA survey |
| Non-network channel exists | Low | High on growth | Post-pilot experiment |

## Appendix C: Pipeline trace
**Applied:** 01 Problem · 02 JTBD · 03 ICP · 04 DVF · 05 Lean Canvas · 07 VPC · 08 Blue Ocean (triggered: empty-quadrant claim) · 09 Porter (triggered: platform dependency) · 11 Market Sizing · 12 Assumption Audit · 13 Competitive · 14 Unit Economics · 15 Risk · 16 Go/No-Go.
**Skipped:** 06 Business Model Canvas (used Lean Canvas — pre-revenue stage; graduate post-pilot) · 10 Theory of Change (no social dimension).
