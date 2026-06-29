# Validation Report: Counterpoint-Live (idea E)

**Date:** 2026-06-20
**Pipeline depth:** Deep
**Idea classification:** B2B SaaS (services-led hybrid) · Napkin / pre-validation · Adjacent→disruptive-within-live · Pure commercial
**DVF weighting:** 40 Desirability / 30 Viability / 30 Feasibility *(default — identification is easier here than in the music-label case, so no feasibility elevation)*

> **What this is:** an independent causal-measurement layer for live music — decomposing every on-sale into **announcement-driven baseline vs. ad-driven incremental** ticket sales, per market, across channels. Sold to independent promoters and festivals as a **bifurcated product**: a retrospective MMM (reactive, always-on) + planned geo-lift studies (proactive), unified by a calibration loop. Services-first, productized on repetition.

---

## 🎯 Executive Summary

**Recommendation: PARK — with a defined, ~€0, ~6-week path to GO WITH PIVOTS. And of the two ideas validated, point the test battery at E first.**

**Composite Score: 67/100 · Confidence: 41/100**

| Lens | Score | One-line read |
|---|---|---|
| 🟢 Desirability | 68/100 | Sharp, concrete soft-show trigger; bifurcation defuses the timing anxiety |
| 🟡 Viability | 62/100 | Bigger/faster market + weak pricing paradox; seasonal/lumpy business |
| 🟢 Feasibility | 71/100 | Easier identification (clean tickets, natural experiments) + softer data wall + fast MVP |

**The thesis in one paragraph:**
Promoters spend heavily to drive on-sales and rescue slow-selling shows, but the on-sale spike is driven by the *artist announcement*, not the ads — yet ads running in that window get the credit. Counterpoint-Live sells the one read they can't get from the party running their ads or their ticketing: an independent decomposition of announcement-baseline vs. ad-driven incremental, per market. The main bets are (a) the announcement spike is statistically separable from ad lift, and (b) measurement-minded promoters on accessible ticketing will pay a retainer + per-study fee.

**Top 3 reasons to pursue:**
1. The pain is concrete, felt, and owned — a flopping on-sale is a money-losing crisis with a clear decision attached (sharper than music labels' diffuse over-attribution).
2. Feasibility is favorable: clean dated geo-located ticket sales + a tour's many city-markets with staggered on-sales = a near-natural experiment; the panel/staggered-DiD family is the natural workhorse.
3. Timing: the April 2026 Live Nation–Ticketmaster monopoly verdict + the rise of API-first ticketing are prying open the walled garden your accessible-data ICP sits in.

**Top 3 reasons it could fail:**
1. Promoters may "fill the room another way" (discount/paper/dynamic-price) rather than buy measurement.
2. The announcement spike and the ad burst co-occur at on-sale — they may not be cleanly separable.
3. Fragmented, seasonal, project-based buyers + the agency gatekeeper make efficient acquisition and steady revenue hard.

**The single most important next step:**
Run the **Vega-E identification study** (announcement-spike separability on synthetic staggered city-markets) in parallel with **8–10 promoter discovery conversations**. Both ~€0, ~6 weeks; they gate the venture.

---

## 🟢 Green Lights / 🔴 Red Flags

| 🟢 Green Lights | 🔴 Red Flags |
|---|---|
| Concrete, owned, felt pain (soft shows) | Discount/paper/dynamic-pricing are strong substitutes |
| Clean outcome + natural geo experiments → easier identification | Announcement spike may not separate from ad lift |
| Data keystone softer than feared (counts, not fan PII) | Fragmented, seasonal, project-based buyers |
| Antitrust verdict + API-first ticketing = tailwind | Agency gatekeeper (blocker vs channel) |
| Weak pricing paradox (no self-cannibalization) | Boutique-scale SOM; Barbara's fit is adjacent, not inside |
| Viable compounding moat (cross-tour benchmarks) | Ticketmaster-adjacent extraction may be coarse |

---

## 📊 Validation Scorecard

### Desirability (40% weight) — 68/100
| Sub-score | Weight | Score | Rubric anchor | Evidence |
|---|---|---|---|---|
| Problem severity | 25% | 70 | "Significant — actively seek workarounds" (soft shows) | §1 |
| Problem frequency | 15% | 65 | "Weekly"→on-sales recurring | §1 |
| Job clarity | 15% | 65 | "Did rescue spend move tickets" is sharp | §1.3 |
| ICP specificity | 15% | 70 | Tight w/ data-access + electronic beachhead | §2 |
| Value-prop fit | 20% | 72 | Announcement-decomposition relieves the core pain | §3 |
| Switching willingness | 10% | 57 | Concrete push; bifurcation defuses timing anxiety | §1.4 |

### Viability (30% weight) — 62/100
| Sub-score | Weight | Score | Rubric anchor | Evidence |
|---|---|---|---|---|
| Market size (TAM) | 15% | 52 | "€10M–€100M+" addressable measurement slice | §4 |
| Obtainable (SOM 3-yr) | 20% | 57 | "€1M–€10M" (~€2–4M) | §4 |
| Market growth | 10% | 68 | Live ~6–8%, festivals 9–17%+ | §4 |
| Unit economics | 25% | 62 | "LTV/CAC 3–5; payback 6–12mo" base | §6.3 |
| Competitive density | 15% | 78 | "Greenfield vertical" (temporary) | §5 |
| Differentiation | 15% | 60 | "Clear differentiation; viable benchmark moat" | §5 |

### Feasibility (30% weight) — 71/100
| Sub-score | Weight | Score | Rubric anchor | Evidence |
|---|---|---|---|---|
| Technical complexity | 25% | 62 | Identification easier — clean tickets, natural units | §3.3, §8 |
| Team-idea fit | 20% | 73 | Barbara's DJ/festival adjacency closer to E's ICP | §9 |
| Time to MVP | 15% | 78 | Retrospective MMM on past tours is fast | §9 |
| Capital intensity | 20% | 80 | Bootstrappable, services-first | §6 |
| Regulatory/legal | 10% | 68 | Data processing (counts, not PII — easier) + ToS | §8 |
| Go-to-market clarity | 10% | 60 | Network finite; **agency fork unresolved** | §9 |

### Auxiliary meters
- **RISK: 62/100** — six criticals (top severity 15); lighter than Counterpoint.
- **DIFFERENTIATION: 68/100** — sharp positioning (announcement-decomposition), replicable method.
- **CONFIDENCE: 41/100** — zero primary validation yet; keystone softened on evidence.

---

## 1. Problem Definition

### 1.1 Problem statement
- **As-is:** promoters spend on paid (Meta/TikTok/Google + DOOH/radio/influencer) to drive on-sales and rescue slow shows, judging by "did it hit target" + platform ROAS + ticketing referral data, often via agencies on "X% of gross" heuristics.
- **Pain:** the announcement-driven on-sale spike gets credited to the ads running during it; promoters can't tell whether rescue spend moved incremental tickets or coincided with natural pickup.
- **Desired:** per-show/per-market incremental sales caused by marketing, net of announcement baseline; "which markets need (and respond to) spend."
- **Gap:** announcement-spike confounding + endogeneity (hot shows get more spend and sell out) + ticketing-platform data walls + a gut/relationship culture. **Soft gap:** for hot shows nobody cares → felt pain concentrates on soft shows (which defines the trigger segment).

### 1.2 Root cause (5 Whys)
Can't tell what spend did → announcement drives the spike, ads claim it → no counterfactual; conversion on a third-party ticketing platform → platforms wall the data, industry markets on gut → **root: live is built on access/relationships/inventory and is consolidated (Live Nation–Ticketmaster), so measurement infrastructure never got built — and the entity that could (Ticketmaster) is conflicted, selling promo while owning the data.**

### 1.3 Jobs-to-be-Done
- **Functional:** "when a show/leg isn't selling, know whether more spend will move incremental tickets (and where)"; plus "plan the next tour's budget where it *causes* sales."
- **Emotional:** replace on-sale panic with something other than gut.
- **Social:** justify spend to the MD **and the artist's manager** (tour marketing is watched/recoupable against the artist).

### 1.4 Forces of Progress
| PUSH | PULL |
|---|---|
| Slow on-sale = visible, money-losing panic | Independent number on what spend caused |
| Thin tour margins; rising ad costs | Per-market guidance |
| Finance asking "did the rescue spend work?" | Announcement-spike decomposition |

| ANXIETY | HABIT |
|---|---|
| "Can I get my data out of Ticketmaster/Eventim?" | "We always spend X% of gross" |
| "On-sale is now — no time for experiments" | Agencies run ads + report their own numbers |
| Method credibility / data-sharing | Free ticketing + Meta dashboards; gut culture |

**Net force:** in the trigger segment PUSH is strong and concrete. Blockers are the data-access anxiety and the speed of live — both addressed by the bifurcated product (retrospective MMM needs no experiment; serves the in-the-moment need).

### 1.5 Falsifiability
Wrong if hot shows sell out regardless (measurement moot) *and* soft shows are "solved" by discount/paper rather than felt as a measurement gap.

---

## 2. Target Customer

### 2.1 Primary ICP
| Filter | Value |
|---|---|
| Firmographic | Independent/mid promoters, festivals, venue groups; **€100k+/yr** marketing; inventory risk; EU-first (DACH + electronic/festival) |
| **Data-access (decisive)** | Accessible ticketing — **DICE / vivenu / Ticket Fairy / See Tickets / self-ticketed**, not Ticketmaster/Eventim-locked |
| Behavioral | Runs paid for on-sales; budgets per tour/festival; burned by a soft show; often uses an agency |
| Psychographic | "Modern independent promoter" — margin-pressured, data-curious, tired of gut-and-pray |

The data-access filter is E's analog of a scale floor; the DICE-heavy electronic/festival scene is the natural beachhead (soft-show risk + accessible data + Barbara's adjacency).

### 2.2 Persona — "Jonas, Head of Marketing, independent electronic promoter/festival group (Amsterdam/Berlin)"
~120 events/yr + one 20k-cap festival, ~€800k marketing, DICE + Meta/TikTok. Trigger: festival second-release undersold + a club tour's midweek dates flopped despite €30k of rescue spend; MD wants proof before next year's budget. *"When a show's slow I panic-spend, and I can't tell you afterward whether it helped or whether those tickets were always going to trickle in."*

### 2.3 Anti-personas
Live Nation/AEG (in-house + Ticketmaster data + procurement); tiny clubs (sub-scale); sold-out arena acts (no inventory risk); Ticketmaster/Eventim-locked promoters (until authorized export is proven).

### 2.4 Buyer / User / Blocker
- **Buyer:** promoter MD / festival director. **User/Champion:** head of marketing (the panic-spender). **Influencers:** artist's manager/agent, festival sponsors.
- **Blockers:** ticketing platform / data access (Ticketmaster conflicted); **the agency running the ads** (gatekeeper — blocker or channel); gut-driven old-guard.

### 2.5 Falsifiability
Wrong if the real buyer is the agency or the ticketing platform, not the promoter; or if data is universally walled.

---

## 3. Solution & Value Proposition

### 3.1 Value Proposition Canvas (bifurcated)
| Customer side | | Solution side |
|---|---|---|
| Jobs: defend spend (MD + artist mgr); rescue soft show (reactive); plan next tour (proactive) | ↔ | M1: per-tour/market incremental scorecard + announcement-baseline decomposition · M2: geo-lift ground truth |
| Pains: can't tell rescue spend worked; announcement over-credits ads; data access; no time | ↔ | Decomposition + per-market read + independence; **M1 defuses the timing/speed anxiety**; data access handled by ICP filter |
| Gains: saved soft shows; defensible budget; per-market guidance | ↔ | Reallocation that fills rooms; spike decomposition (delight); geo-lift "we proved it" |

### 3.2 Value Proposition Statement
> For independent promoters & festivals with inventory risk on accessible ticketing, who can't tell whether on-sale/rescue spend moved *incremental* tickets vs. demand the artist announcement already created, **Counterpoint-Live** decomposes every on-sale into announcement-driven baseline vs. ad-driven incremental, per market — unlike the ticketing platform's or Meta's self-reported numbers, because it's the only read not sold to you by the party running your ads.

### 3.3 Riskiest Assumption Test (re-ranked)
| # | Assumption | Type | L×I | Cheap test | Falsification threshold |
|---|---|---|---|---|---|
| 1 | Promoters can get clean ticketing data | Surv (S) | **20→softened** | Behavioral export test in discovery | <3/8 on accessible platforms can produce city×day sales in a week |
| 2 | Announcement spike separable from ad lift | Feas (S) | **15** | Vega-E synthetic study | baseline vs incremental not separable w/ usable CIs even w/ geo anchor |
| 3 | Soft-show pain converts to purchase | Value (V) | **15** | Discovery: last soft show walkthrough | ≥7/10 reach for price/inventory levers, shrug at measurement |
| 4 | Buyer is the promoter (not agency/platform) | ICP | 12 | Discovery budget/data mapping | budget+data+pain sit with agency/platform |
| 5 | WTP fits lumpy/seasonal model | Viab | 9 | Present hybrid pricing | only-per-tour, no retainer |

*Note: data access (#1) was the intake keystone; Phase 3 evidence softened it from a hard wall to segment-dependent onboarding friction — see §4/§5.*

---

## 4. Market

### 4.1 Sizing
**Inputs (verified):** global live music ~$40–41B in 2025 (~6–8.5% CAGR); US ~$18.5B; music festivals ~$3–3.8B but high-growth (9–17%+ CAGR); Europe is the dominant live/festival region. **Bottom-up:** addressable = independent/mid promoters + festivals in Europe on accessible ticketing with €100k+ marketing — **est. ~500–2,000 accounts (Fermi, ±50%)** × ~€20–50k ACV → **SOM (3-yr, ~50–100 accounts) ≈ €2–4M.** Boutique-scale, but a bigger ceiling and faster tailwind than the music-label case.

### 4.2 Dynamics
Emerging measurement category in a large, growing market; festivals the fastest-growing segment. **Tailwind:** the LN–Ticketmaster antitrust verdict + API-first ticketing opening the ecosystem; post-cookie measurement crisis. **Headwinds:** seasonality; promoter sophistication; fragmentation.

### 4.3 Geographic priority
Tier 1: DACH + EU electronic/festival scene (Barbara + DICE). Tier 2: UK, Benelux, Nordics. Tier 3: US (bigger, but more Ticketmaster-locked).

---

## 5. Competitive Landscape

### 5.1 Clusters
- **No dedicated causal-measurement player for live surfaced** (medium-high confidence). Served, if at all, by generic geo-lift tools + ticketing dashboards.
- **Conflicted gatekeeper:** CTS Eventim (European major) pushes "data-led audience engagement" — a Ticketmaster-analog leaning into data, structurally conflicted (sells promo + owns data). Independence is the durable wedge.
- **Do-nothing / substitutes (strong):** gut + ticketing dashboard, plus discount/paper/dynamic-pricing.

### 5.2 Data-access reality (the softened keystone)
Measurement needs **aggregate sales by market × day** (the promoter's own data), not fan PII. Ticketing platforms wall *fan identity/emails* (Ticketmaster retains the relationship; DICE withholds emails) — not the aggregate sales counts the product needs. API-first platforms (vivenu, Ticket Fairy, DICE) make extraction easy and sell data-ownership as a feature; third-party APIs expose event/pricing data as a proxy. **Net: segment-dependent onboarding friction, not a hard wall — verify granularity in a pilot.**

### 5.3 Porter's Five Forces (central here)
| Force | Level | Why |
|---|---|---|
| New entrants | Med-High | Methods open-source; a generic geo-lift vendor could verticalize |
| Buyer power | Medium (↓ vs Counterpoint) | Fragmented independents → lower individual power; but price-sensitive, project-based |
| Supplier power | High, easing | Ticketing data-landlords; antitrust + API-first challengers eroding the lock |
| Substitutes | High | Do-nothing + discount/paper/dynamic-pricing |
| Rivalry | Low (today) | Greenfield vertical — temporary |
| (6th) Regulatory | Tailwind | LN–Ticketmaster monopoly verdict + possible break-up opens the ecosystem |

**Verdict: selective, but more attractive than the music-label structure.**

### 5.4 Blue Ocean — ERRC
| Eliminate | Reduce | Raise | Create |
|---|---|---|---|
| Platform self-attribution; announcement-spike credit-grab | Agency-reported ROAS; attribution pillar | Independence; per-market causal precision | Announcement-decomposition; per-market rescue/planning; reactive-MMM + proactive-geo-lift loop |

Passes focus/divergence/tagline. **Pond reframe:** still a niche, but a bigger pond with a favorable current (festival growth + antitrust + softer data wall).

---

## 6. Business Model

### 6.1 Lean Canvas
| Block | Content |
|---|---|
| Customer Segments | Independent/mid promoters + festivals on accessible ticketing, €100k+ marketing, EU electronic beachhead |
| Problem | Caused-vs-announcement blindness; per-market guesswork; can't defend spend |
| Solution | Retrospective MMM + announcement decomposition (M1); geo-lift studies (M2); per-market scorecards |
| UVP | "The only read of your on-sale not sold to you by the company running your ads — or your ticketing" |
| Unfair Advantage | Barbara's electronic/DJ/festival network + causal depth + announcement-decomposition + first-mover in an opening ecosystem; **moat-to-build: cross-tour lift benchmarks** |
| Channels | Barbara's network → agencies (partner?) + festival/promoter events + referrals |
| Revenue | Hybrid: retainer (M1) + per-study (M2) |
| Cost Structure | Founder time; pipeline build; bespoke geo-lift; data plumbing; compute |
| Key Metrics | design partners → pilots → retainer conversion → studies/customer/yr → net retention (incl. seasonal) → hours/study → CAC by channel |

### 6.2 Revenue model
Hybrid **retainer (always-on retrospective MMM) + per-study geo-lift add-ons**, decoupled from spend. The retainer is the retention mechanism *and* the revenue-smoother for a seasonal business.

### 6.3 Unit economics (mid promoter, base case)
| Metric | Cash/warm | Loaded/blended |
|---|---|---|
| Blended ACV | ~€30k | ~€30k |
| Gross margin | 60% | 55% |
| Contribution/yr | ~€18k | ~€16.5k |
| CAC | ~€4k | ~€8–15k (agency channel could cut sharply) |
| Churn | 18% (10–30%, + seasonal) | — |
| LTV (3-yr cap) | ~€54k | ~€50k |
| **LTV/CAC** | ~13 | **~5 (bear ~2)** |
| Payback | ~3 mo | ~10 mo |

**Sensitivity:** LTV/CAC ~2 (bear: 30% churn, 50% GM, €15k CAC) → ~5 (base) → ~13+ (bull/agency channel). Higher floor than Counterpoint. **Pricing paradox: weak** (fee not indexed to spend; value is reallocation, not reduction).

### 6.4 Projections (hypotheses)
| | Year 1 | Year 3 | Year 5 |
|---|---|---|---|
| Customers | handful (pilots) | ~30–40 | ~80–100 |
| Revenue | ~€120k | ~€1–1.3M | ~€2.5–3M |

Boutique by design; seasonal revenue smoothed by the retainer.

---

## 7. Theory of Change
**Skipped** — pure-commercial, no social-impact claim.

---

## 8. Risk Register

### Critical (severity ≥12)
| Risk | Category | L×I | Mitigation |
|---|---|---|---|
| Promoters discount/paper instead of measuring | Market | 15 | Target measurement-minded segment; "defend the spend" framing |
| Announcement spike not separable | Technical | 15 | Vega-E first; aggregate-lift fallback |
| Seasonal/lumpy revenue + off-season churn | Financial | 12 | Retainer central; annual contracts |
| CAC high (agency blocks + fragmentation) | Financial | 12 | Agency-as-reseller; tight ICP |
| Ticketing extraction coarser than hoped | Operational | 12 | API-first/DICE; 3rd-party data APIs |
| Barbara's DJ net doesn't convert | Team | 12 | Test 5 intros early |

### Significant (6–11)
Geo-lift timing vs speed of live (9); delivery doesn't standardize (9); generic vendor verticalizes (8); Eventim/Ticketmaster builds in-house (6); GDPR/ToS (6); founder focus split vs BeeSignal (9).

### Pre-mortem (June 2028, failed)
1. Substitute won (papering/discounting). 2. Spike not separable (CIs too wide). 3. Data/ops drowned across fragmented stacks. 4. DJ network didn't convert + agencies blocked + cold CAC brutal. 5. BeeSignal pulled focus; seasonal revenue never compounded.
**Interaction:** fragmentation + seasonality + bespoke onboarding compound into a stall — but the higher pricing/retention floor gives more margin than Counterpoint.

---

## 9. Execution

### 9.1 MVP
**Build:** retrospective MMM with announcement-decomposition on one design partner's past tours/festival + one planned geo-lift. **Don't build yet:** benchmarks product, automation. **Test of success:** a per-market incremental number with a usable interval the partner agrees is decision-relevant, + a retainer conversion.

### 9.2 Critical path
1. Vega-E identification study (gates). 2. 8–10 promoter discovery (incl. behavioral data-pull). 3. One historical-tour retrospective. 4. One paid pilot + planned geo-lift (if 1–3 pass).

### 9.3 Team
Daniel (causal/product) — strong fit; Barbara (commercial/network) — **closer to E's ICP than to labels**, single-point commercial dependency; data/pipeline engineer — hire after pilot.

### 9.4 Capital
Bootstrappable via services; no round warranted (boutique market).

### 9.5 Go-to-market
- **Wedge:** the "defend the spend" job for measurement-minded promoters under inventory pressure, electronic/festival beachhead.
- **Channels:** Barbara's network → **resolve the agency fork** (convert agencies from blockers to resellers — the CAC + fragmentation fix).
- **First 10:** founder-led, retainer pilots from warm intros.

---

## 10. Decision

### Five-Gate assessment
| Gate | Pass/Fail | Why |
|---|---|---|
| 1. Problem real? | Pass | Soft-show pain concrete and owned |
| 2. Defensible? | Pass (soft) | Empty vertical + antitrust tailwind + viable benchmark moat |
| 3. Unit economics? | Pass-with-pivot | Base LTV/CAC ~5; decouple price (done) + prove retention |
| 4. Team can do it? | Pass | Barbara closer to E's ICP; fast MVP |
| 5. Best use of time? | Founder's call | Opportunity cost vs BeeSignal + vs A/B |

### Recommendation: **PARK → cheap path to GO WITH PIVOTS; validate E first (ahead of Counterpoint).**
Composite 67 / Confidence 41 lands in PARK, but the low confidence is unrun-cheap-test, not bad evidence. E out-scores Counterpoint on every lens except purest differentiation, with a softer keystone and better founder-fit. Point the €0/6-week battery at E.

### Proposed pivots
1. Value-capture: retainer + per-study, decoupled from spend.
2. Segment: accessible-ticketing + inventory-risk promoters/festivals, electronic beachhead.
3. Channel: agencies as resellers.
4. Moat: secure cross-tour benchmark rights.

### Conditions to unlock GO
- Vega-E shows the announcement spike *is* separable with usable intervals.
- Discovery finds measurement-minded promoters who can produce geo×day sales and will pay a retainer.
- A pilot shows off-season retention >85% and standardizable delivery.

### E vs Counterpoint (A)
| | A | E |
|---|---|---|
| Composite / Confidence | 63 / 37 | **67 / 41** |
| #1 risk | Identification (hard binary) | Data access (softer) |
| Pricing paradox | Strong | Weak |
| Market | Small/hard pond | Bigger/faster + tailwind |
| Barbara fit | Weak | Better |
| Moat-to-build | Hard | More viable |
**E is the stronger bet; A's assets (Vega, discovery) transfer; B (gear brands) = potential services cashflow.**

### What would change this
- Vega-E separates the spike → strong GO-WITH-PIVOTS candidate.
- Promoters discount/paper instead of measuring → reconsider.
- A generic geo-lift vendor verticalizes into live → first-mover speed becomes existential.

---

## Appendix A: Sources & citations
1. IFPI / MBW — global recorded music context (cross-ref from Counterpoint report).
2. econmarketresearch / researchandmarkets — global live music ~$40–41B 2025, ~5.6–8.5% CAGR.
3. Mordor — US live music ~$18.5B 2025, ~6.5% CAGR.
4. thebusinessresearchcompany / globalgrowthinsights / grandviewresearch — music festival market ~$3–3.8B, 9–17%+ CAGR.
5. custommarketinsights — Europe dominant live/festival region.
6. skyquestt — CTS Eventim as European major, "data-led audience engagement."
7. NPR / Courthouse News / Crowell & Moring / Variety — LN–Ticketmaster monopoly verdict (Apr 2026); ~80–86% primary ticketing, ~78% amphitheaters; states seek break-up; penalty trial early 2027.
8. Ticket Fairy / proticket — Ticketmaster retains organizer/fan data ("data landlord"); DICE withholds attendee emails but gives artists more fan data.
9. vivenu — API-first, 100% data-ownership positioning.
10. ticketsdata — third-party DICE/Ticketmaster event/pricing APIs.
11. Sellforte / Lifesight / sellforte comparisons — crowded generic mid-market MMM/incrementality landscape (context for differentiation).
12. Triple Whale / Meta — geo-lift as gold standard; Meta always-on Incremental Attribution.

*Confidence flags: live market size — high (multiple converging sources). Antitrust verdict — high. Data-access softening — medium-high (evidence-based but unverified in a real promoter pilot). No vertical competitor — medium-high (absence across searches). Account count — Fermi estimate, low-medium.*

## Appendix B: Assumptions log
| Assumption | Confidence | Sensitivity | Test |
|---|---|---|---|
| Announcement spike separable | Low-medium | Binary on signature VP | Vega-E |
| Promoters buy vs discount/paper | Low-medium | High | Discovery |
| Ticketing data producible (geo×day) | Medium (softened) | High on onboarding | Behavioral data-pull |
| Off-season retention >85% | Unknown | High on LTV | Pilot |
| Agency = channel not blocker | Low | High on CAC | Discovery + pilot |
| Barbara's net → promoter buyers | Medium | High on GTM | 5 intros |
| ~500–2,000 EU accounts | Low-medium | High on TAM | Industry data |

## Appendix C: Pipeline trace
**Applied:** 01,02,03,04,05,07,08,09,11,12,13,14,15,16. **Skipped:** 06 (Lean Canvas used — pre-revenue), 10 (no social dimension).
**Assets reused from Counterpoint (A):** the Vega identification-study design (adapted: streams→ticket sales, cities as natural staggered units — gets easier); the discovery scorecard structure; the DVF spine.
