# The Music Marketing Ecosystem — Actors, Stack & Convergence

*A living research map for the causal-measurement venture (Ideas A / E / B).*
*Drafted 2026-06-22. Status: working document — figures flagged as VERIFIED / DATED / ESTIMATE throughout.*

---

## 0. Why this document exists

We are **not** committing to an ICP. We are mapping the stakeholders and structure of the (electronic-leaning) music-marketing world so that when we *do* pick a wedge, we understand who the buyers, data sources, gatekeepers and substitutes actually are. Two patterns emerged that reshape the whole thesis:

1. **Convergence.** The same operators increasingly own the streaming-attribution problem (Idea A) *and* the ticket-attribution problem (Idea E). The walls between recorded-music, live, and sales are coming down — at the company level and at the platform level.
2. **The dependent variable is not always Spotify streams.** In electronic/DJ music, the outcome that matters is often **Beatport downloads/sales**, **DJ support**, or **ticket sales** — several of which are *causally cleaner* than passive streams.

Both patterns *expand* the opportunity and argue for a measurement engine that is **outcome-agnostic** (streams OR downloads OR tickets) rather than Spotify-only.

---

## 1. The stack — four layers

Music marketing sits on a stack. Measurement-need (and budget) concentrates at specific layers.

```
   LAYER                     ACTORS                              MEASUREMENT NEED
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ 4. LIVE / EVENTS     festivals, promoters, venues,           HIGH — Idea E   │
 │                      channel-labels' event arms              (ticket sales)  │
 ├────────────────────────────────────────────────────────────────────────────┤
 │ 3. DISTRIBUTION /    Spotify, YouTube, Apple;                 MEDIUM — these  │
 │    TRANSACTION       Beatport (DJ sales + now tickets)        grade own       │
 │                                                              homework; also  │
 │                                                              a DATA SOURCE   │
 ├────────────────────────────────────────────────────────────────────────────┤
 │ 2. CURATION /        channel-labels & tastemaker brands       HIGHEST — the   │
 │    TASTEMAKING       (selected., Monstercat, MrSuicideSheep,  richest buyer   │
 │                      Lilly Era…) — playlist brands            seam; the A↔E   │
 │                                                              bridge          │
 ├────────────────────────────────────────────────────────────────────────────┤
 │ 1. SUPPLY /          producers, beatmakers, BeatStars,        LOW (today) —   │
 │    CREATION          sample/AI-tool marketplaces             fragmented,     │
 │                                                              tiny budgets    │
 └────────────────────────────────────────────────────────────────────────────┘
```

The crucial finding: **a handful of scaled electronic brands now touch all four layers at once** — which is exactly why "independent causal measurement across streaming + sales + live" has a natural home in this scene.

---

## 2. Actor archetypes

### 2.1 Channel-labels / tastemaker brands  ← richest buyer seam
**Audience-first, label-second companies that were a YouTube channel (or blog/playlist) *before* they were a label.** They manufacture attention, then monetise it across releases, then expand into events. Their entire asset is attention they create — and they cannot cleanly attribute what it produces. That is our wedge.

The defining quote (Monstercat's founder): *people don't need labels anymore, so a modern label has to be "a platform and marketing tool they can't find on their own."* These are **marketing machines that acquired labels**, not labels that added marketing.

**The maturity ladder (this is the key mental model):**

| Tier | Examples | Scale | Marketing function? | Relationship to us |
|---|---|---|---|---|
| **T1 — Scaled** | selected., Monstercat, Seeking Blue (MrSuicideSheep), Lowly Palace (Trap Nation) | Billions of streams; M-scale subscriber bases; real org charts | **Yes — named PM / Brand & Comms roles, paid campaigns, budget** | **Plausible paying buyers; the A↔E bridge** |
| **T2 — Micro** | Lilly Era, Electro Posé-scale | ~1B streams or less; founder + tiny team | No — runs on sweat-equity content + curator instinct | **Teardown / design partner / benchmark corpus** — below the retainer floor |

> **The switch that turns this segment from "interesting" to "buyer" is the appearance of a named marketing function with a budget.** selected.'s org chart shows it (Product Manager + Brand & Communications Manager running campaigns); Lilly Era's doesn't.

**Verified scale signals (with freshness flags):**
- **selected.** (Berlin, founded 2013 by Nick Scheerbart & Nico Pinkowski as a YouTube channel; Klaus Eickemeyer & Michael Rank joined 2015 to build a "full-scale music company"). Crossed **6B+ streams in 2025**; runs "two of the biggest playlist brands on all streaming services"; roster incl. Joel Corry, Sonny Fodera, Avaion. Has a **Product Manager** and a **Brand & Communications Manager** with explicit campaign mandates. *[VERIFIED via selectedbase.com About, self-reported]*
- **Monstercat** (Waterloo, Canada, 2011). Self-describes as "the convergence of an independent label, tech startup and media company." 2M+ YouTube subs *[DATED ~2014]*; active label (latest comp "Uncaged," June 2026). Heavy live arm (see §3).
- **MrSuicideSheep / Seeking Blue** (Vancouver, 2010). 12M+ YouTube, 760k SoundCloud, 314k Spotify *[DATED ~2025]*. Runs a 24/7 YouTube livestream off its back catalogue. Label formed ~2 yrs in.
- **Trap/Chill/Rap Nation / Lowly Palace** (Andre Benz, 2012). ~20M combined subscribers; Trap Nation ~5B views; LA office, full-time staff *[DATED ~2017 — almost certainly understated now]*.
- **Lilly Era** (UK / 97 Music Group, founder James Carter; also runs Serotonin Records). ~1B Spotify streams; ~85–95 releases/yr (≈ one every 4 days); YouTube per-track views in the low hundreds → YouTube is a secondary mirror, Spotify playlists are the engine. *[VERIFIED via site + our own release-count extraction; founder via LinkedIn]*

**Adjacent cluster (same archetype, surfaced via LinkedIn "people also viewed" — leads, not verified scale):** Get The Sound (Paris), Electro Posé (Paris), Inside Records (Paris), Soave Records (Rotterdam), Tribal Music Group (Oss, NL — notably self-classified as *Marketing Services*). The cluster skews **France + Netherlands + Germany/UK** — a real, enumerable European tastemaker-label scene.

### 2.2 Artists
The pull, often, *is* the audience — not the label. Worked example: **Coldabank** (~903k Spotify monthly listeners). His **selected.** release "Something Stronger" ≈ **82.9M** streams; his **Lilly Era** release "Lie To Me" ≈ **104k** — an ~**800× gap for the same artist**. *[VERIFIED via Spotify screenshot]*

Implication: a release's streams are dominated by which *artist* and which *brand/playlist* carried it, not by the micro-label's marketing. This (a) sharpens the org-vs-paid problem and (b) makes the **artist** (esp. a 6–7-figure-monthly-listener act deciding what moved *their* numbers) a credible alternative buyer.

### 2.3 Distribution / transaction platforms
The "grade-their-own-homework" incumbents our independence wedge is defined against — **and** potential data sources:
- **Spotify / YouTube / Apple** — passive-stream outcome; self-reported attribution.
- **Beatport** — the DJ/electronic marketplace; a *different and often better* dependent variable (see §4).

### 2.4 Supply / creation (marketplaces)
- **BeatStars** (Austin, 2008; founder Abe Batshon). Beat/instrumental marketplace; **$400M+ paid to creators**, 11M+ beats, ~1.5M downloads/month; publishing arm w/ Believe (formerly Sony). The "Old Town Road" origin platform. Customer = the **producer**, not the label — a distinct, upstream stakeholder. Sells producers a self-serve ad system ("BeatStars Promote") and preaches the same daily-release content treadmill. *[VERIFIED via MBW/Wikipedia; some figures 2024–25]*
- Relevance to us: **low near-term** (budgets tiny, fragmented across millions of producers), but it completes the supply side and shows the "I promote but can't tell what worked" pain exists even at the individual-producer layer.

---

## 3. Convergence — the meta-trend (A ↔ E ↔ sales collapsing into one operator)

This is the most important strategic finding. Multiple independent signals point the same way:

**At the company level — channel-labels are migrating into live:**
- **Monstercat:** recurring **Tomorrowland stage** ("Monstercat takeover," through 2025–26); a touring events arm (venues + festivals worldwide via Songkick/Bandsintown); branded club nights (Monstercat × Blacklist, Melkweg Amsterdam; Ubbi Dubbi festival); 24/7 Twitch radio since 2014.
- **selected.:** "Selected Sessions" — cinematic destination DJ sets (Medellín w/ Disclosure, Iceland w/ Aaron Hibell, Belgrade w/ Dom Dolla) — event-as-content.
- **Lilly Era:** micro-mirror — location DJ sets + curated events (Mallorca, Austria).

→ **The same operator owns both the streaming-attribution problem (A) and the ticket-attribution problem (E).** A scaled channel-label deciding whether its festival stage or branded club night actually *sold tickets* (net of artist draw) is *literally* the Idea-E buyer — and already trusts data. This is the first concrete actor that unifies both verticals under one roof.

**At the platform level — the marketplace is fusing music + tickets:**
- **Beatport Tickets** (launched **Oct 2025**, w/ ticketing tech provider Weeztix/Eventix): a ticketing platform *exclusively for dance-music events*, letting **labels, promoters and venues** sell tickets via Beatportal. 2026 roadmap: shows appear on **artist/label profile pages** with **custom playlists attached to ticket pages** ("previews of the music featured at shows"). → an incumbent is literally stitching catalogue data to ticket sales — the exact A↔E adjacency, validated.

**At the structure level — the industry has been converging for 15+ years:**
- The **360 deal** already bundles recorded music + touring + merch + sponsorship under one rights-holder (labels take ~10–20% of ticket/performance revenue on the argument that "our marketing sells the tickets" — a claim *nobody can currently verify*, which is our wedge).
- Macro framing (Orphiq, 2026): the year is "about the convergence of several shifts" — streaming maturation + live exceeding pre-pandemic levels (global live ~$35B 2026) + independents capturing more share.
- Electronic specifically (IMS Business Report 2026): global electronic industry **$15.1B**; Ibiza club ticketing a record **€160M in 2025**; Indonesia +77% electronic listeners; AI creation tools +651% since 2023 → $333M, 63M MAU. *[VERIFIED via Beatportal/IMS]*

**Why-now tailwind (cross-ref Idea E):** the Live Nation–Ticketmaster antitrust case — a 2026 summary-judgment/trial decision on whether they must split — is cracking open the live/ticketing data ecosystem that API-first players (Beatport Tickets, DICE, vivenu, Ticket Fairy) are rushing into.

> **Strategic consequence:** build the measurement engine **outcome-agnostic and cross-domain** from day one. The defensible position is not "Spotify attribution for labels" but "independent causal measurement of whatever marketing is supposed to move — streams, downloads, or tickets — for the converging electronic-music operator."

---

## 4. The dependent variable is not always Spotify streams

A core methodological insight for the electronic vertical: **the outcome we model should be chosen for causal cleanliness, not defaulted to streams.** Candidate dependent variables, ranked by signal quality:

| Dependent variable | What it is | Causal cleanliness | Notes |
|---|---|---|---|
| **Ticket sales** (Idea E) | Dated, geo-located purchases | **Highest** | Discrete, high-intent, natural geo experiments |
| **Beatport downloads/sales** | A pro DJ pays $1.49–$2.49 to own a track for sets | **High** | Deliberate paid act; ~25–30× Spotify's per-unit value; first-week sales drive chart position |
| **DJ support / chart adds** | A track entering respected DJs' charts / promo-pool feedback | Medium-high | A leading indicator unique to this scene |
| **Spotify streams** | Passive plays (30s threshold) | **Lower** | Playlist/algorithm-confounded; the noisy default |

**Why Beatport-as-DV is genuinely sharp:**
- It's a **download store for working DJs**, not a passive stream — "a Beatport sale generates more revenue than thousands of streams," and the platform pays **~25× Spotify** *[VERIFIED, MBW/Billboard]*. Higher intent = lower noise.
- **First-week *sales* determine chart position** — "streaming-style slow-build rollouts do not translate." So the outcome is a sharp, time-boxed sales spike, ideal for event-study / lift methods.
- Labels **already instrument it weekly.** Practitioners literally keep spreadsheets of *Track × Week × Streams × Saves × Beatport sales × chart notes*, and reason causally across DVs: *"If Beatport sales drop but Spotify streams hold → your DJ/download audience is dropping. If Spotify rises but Beatport is stagnant → you're turning listeners into fans, not customers."* That is folk-MMM across two dependent variables — and exactly the job we'd systematise.
- Beatport sells labels the very promo levers whose lift is unmeasured: **Hype** (accelerator for labels <$25k/yr sales: "84% more traffic, 40% more sales" — *vendor-reported*), store **exclusivity** windows, editorial/chart placement, DJ promo pools. Each is a treatment whose incremental effect nobody isolates.
- Beatport scale: ~36M users, 465K DJ customers, 11M tracks, 75K label partnerships; owned by LiveStyle (re-acquired May 2025); expanded into open-format genres (hip-hop/R&B/Latin) Sept 2025. *[VERIFIED; user/customer figures self-reported]*

**Modelling implication:** the engine needs a **pluggable outcome layer** and likely a **multi-outcome view** (a release's marketing can lift Beatport sales, Spotify streams, and ticket demand differently). For the electronic beachhead, Beatport sales + DJ support may be the *primary* DV with streams secondary — the inverse of the mainstream-label default.

---

## 5. Data access — how we actually get the dependent variable

The single most important clarification in this whole investigation: **we never touch a locked DSP API. The data comes from the layer where the client already owns it, with the client's authorization.** Two channels are often confused — they are completely different doors:

| Channel | What it is | Status for us |
|---|---|---|
| **Public DSP Web API** (e.g. Spotify Web API) | Third-party *apps* querying the platform's catalog | **Closed / irrelevant.** 250k-MAU wall (May 2025) + Feb 2026 lockdown + "no-replication" clause. We don't use this. |
| **DDEX sales/usage reports (DSRs)** | The B2B supply-chain channel: the DSP reports streams/sales *back down the delivery pipe* to whoever distributed the music | **The real source.** This is how distributors get the numbers. |

### Why FUGA can "access" and a stranger can't — and why it still needs first-party consent
FUGA isn't reading all of Spotify. **FUGA receives a label's data because FUGA *delivered* that label's music** — the DSRs flow back to the distributor of record as a contractual byproduct of being the pipe. Its access is **scoped to its own delivered catalog**, not a master key. Its real advantage isn't privilege; it's that **FUGA already did the painful normalization** — collecting DSRs from dozens of DSPs in dozens of formats and standardizing them into one clean daily *Track × territory × platform* feed with an API on top ("a daily retrieval job pulls Spotify/iTunes/Deezer reports and matches every line to the catalogue").

So **we still need first-party authorization in every case.** Two shapes:
1. **Client-delegated access (realistic path):** the label is the distributor's customer; the label grants *us* access to *their* account — via the distributor's Analytics API with the client's credentials/OAuth, a white-label sub-account, or simply a client-run export handed over. We're an authorized agent reading *one client's* data, not a platform reading everyone's.
2. **Become a distributor (heavy path):** deliver the music ourselves → receive DSRs directly like FUGA. Turns a measurement product into a distribution company. Avoid.

### The consent-tiered access ladder
The gate is always the same — **client consent, not a technical wall:**

| Tier | Client's distributor / source | How we ingest | Quality |
|---|---|---|---|
| **Best** | FUGA, Revelator, IDOL/LabelCamp, LabelGrid | Client-authorized **Analytics API** / sub-account | Clean, daily, automated, geo-resolved |
| **Workable** | DistroKid, TuneCore, CD Baby (no official API) | Client-run **manual CSV export**, handed over | Lagged/unofficial, but fine for retrospective MMM |
| **Always available** | Spotify-for-Artists, Apple-for-Artists, Beatport dashboards | Client's own first-party export | Varies; Apple's Shazam + retention are a strong *organic-demand* signal |

### Distributor API ranking (the streams-side keystone)
| Platform | Streams-data API? | Notes |
|---|---|---|
| **FUGA** | **Yes — purpose-built** | "Unfiltered daily data from all major DSPs via the Analytics API"; read-only reporting API (xml/json) + webhooks. Gold standard. |
| **Revelator** | **Yes — API-first** | Public self-serve docs + sandbox; streaming/download data by release/DSP/market, CSV export; runs daily royalty advances off the pipeline. *(Note: public client disputes re payout freezes — irrelevant to read-only analytics, but a partner-trust flag.)* |
| **IDOL / LabelCamp** | Yes (advertised) | "API integrations" for large Merlin-label catalogs. Verify hands-on. |
| **LabelGrid** | Yes — "open API" + sandbox | Smaller-label-friendly; purpose-built for label ops. |
| **DistroKid / TuneCore / CD Baby** | **No official API** | Artist-tier. Manual export only; an unofficial reverse-engineered DistroKid wrapper exists but is non-viable for a product. TuneCore "Trends" is explicitly unofficial/lagged. |

### Consequences for the venture
1. **The Spotify lockdown does not block us** — we're never the third-party app hitting the public API. If anything it *widens the moat* by killing cheap-data scraper competitors (Chartmetric/Soundcharts-style), who may not even clear the 250k-MAU bar themselves.
2. **The sharper client qualifier is "who is their distributor?"** — not "how big are they?" A label on FUGA/Revelator is API-integrable; a label on DistroKid means manual CSV. And the axes correlate: scaled tastemaker-labels (selected.-tier) run on FUGA-class infrastructure; the micro-tier (Lilly Era) on artist-tier tools — **so data-accessibility and buyer-readiness line up on the same axis.**
3. **The keystone test is cheap and specific:** confirm with FUGA/Revelator that a label can authorize an *external analytics partner* to read its data (OAuth/sub-account) **without** us becoming a sub-distributor — and that granularity is true daily × territory × track. *[NEEDS VERIFICATION — vendor docs describe API access for the account holder; the "authorize a third-party vendor" path is the precise unknown.]*

---

## 6. The independent variables — how releases are campaigned

This is the **X-matrix** of the MMM: the marketing inputs whose lift we'd estimate. The core finding: **a release is run as a multi-week campaign *system*, not a drop — and the channels are deliberately sequenced to be interdependent.** That interdependence is the central modelling problem (and the opportunity).

### The campaign skeleton (phases, not a launch day)
A release runs ~8–12 weeks in three phases, with timelines dictated by fixed lead-time constraints:

| Phase | Window | Job | Lead-time constraints |
|---|---|---|---|
| **Pre-release** | 4–6 wk out | Prime audience, signal algorithms | Spotify editorial needs track ~7 wk out; press 3–4 wk; ad creative 2–3 wk to test |
| **Launch week** | release day ±7 | Concentrate engagement (the first-7-day signal) | pre-saves convert on day 1; algorithmic triggers fire here |
| **Sustained** | 4–8 wk post | Keep momentum, repurpose, feed next release | algo playlists (Discover Weekly/Release Radar) keep compounding |

### The four channel groups (= how clean the spend variable is)
| Group | Examples | Capturable as MMM spend? |
|---|---|---|
| **Paid** | Meta / TikTok Spark Ads / YouTube pre-roll; Spotify Ad Studio / Marquee / Discovery Mode; PR firms; radio plugging; pitching layers (SubmitHub, One Submit) | **Yes — clean spend + dates** |
| **Owned / organic** | Short-form video (8–30 pieces per release); pre-saves/smart-links (Hypeddit, HearNow); email; **the label's own channel/playlist push** | **Mostly no** — effort, not priced; the big unobserved confounder |
| **Earned** | Editorial playlists; press/blogs; DJ support/radio/chart adds | Partly — placement is observable, "cost" isn't |
| **Algorithmic (triggered, not bought)** | Discover Weekly, Release Radar, Radio | **No — it's an *outcome* of the first-7-day save rate**, not an input |

### The electronic-specific levers (the beachhead — denser with loggable, paid, label-controlled inputs)
- **Promo pools / DJ servicing** — the signature lever. Pay a service to deliver pre-release tracks to thousands of vetted DJs and collect feedback/charts. Platforms: **Inflyte, Label Worx (PromoWorx), Reaktion, 8DPromo, Promo Push.** Paid campaigns *with built-in feedback telemetry* (downloads, feedback, plays) — a clean treatment variable. (Label Worx self-reports 37,200+ labels, 20,000+ tracks/month.)
- **Beatport pre-orders** — 28-day pre-order sales count toward first-week chart eligibility → a timing lever with a chart consequence.
- **Beatport exclusivity windows** — top store placements reserved for exclusives.
- **Beatport Hype** — $10/mo accelerator for labels <~$15k/yr; placement among similar-size labels, free of major-label competition.
- **Remix contests** — via LabelRadar × Beatport; a content *and* discovery engine (community produces a release's worth of derivative tracks).
- DJ charts, Traxsource, Bandcamp, specialist dance radio.

### Release-type taxonomy
| Type | Campaign shape |
|---|---|
| **Single (waterfall)** | Workhorse — sequential singles each rolled into the prior, building toward an EP/album |
| **EP** | Lead single carries Phases 1–2; later phases spotlight remaining tracks |
| **Album** | Longest arc; multiple lead singles; video as anchor |
| **Remix / remix package** | Extends a track's life; contest winners become official releases |
| **Curated compilation ("Selected"-style)** | The channel-label format — the *label brand* is the product, not one artist |
| **DJ mix / classic re-boost** | Paid media + editorial to revive current or catalogue tracks |

### Campaign intensity tiers (budget-gated — relevant to the spend-floor question)
- **£500–1,000:** playlist pitching + some blog coverage; limited ads.
- **£1,500–3,000:** integrated across streaming, press and ads — realistic chance of *triggering algorithmic playlists*. **Measurable paid budget effectively starts here.**
- Rule of thumb: focused spend on 2–3 channels beats scattered spend on 5.

### Why this matters for the model (the hard part)
1. **Naive attribution is structurally wrong — which is the opportunity.** The graph isn't `streams = β·adspend`. It's `organic content + pre-saves → first-7-day engagement → algorithmic trigger → streams`, with paid *amplifying winners* mid-funnel ("paid converts better once press + playlists are in place"). Ignoring the mediation misattributes algorithmic lift to whatever paid channel was running — exactly the confounding our causal toolkit exists for, and exactly what folk-MMM spreadsheets can't handle.
2. **A large part of the X-matrix is unobservable as spend.** Paid social, Beatport Hype, promo-pool campaigns, pre-orders, ad platforms = loggable. Short-form content volume, owned-playlist placement, and — for a channel-label — **their own brand-channel push** = major inputs with no price tag. For selected.-type operators the channel push is likely the *largest* driver and the hardest to quantify, confounding everything else.
3. **The electronic beachhead is more measurable on the input side too.** Its signature levers are paid, discrete, label-controlled, and several self-report feedback — a cleaner input set than the all-organic indie-pop playbook. Electronic-first is identification-friendlier on *both* the output (Beatport sales/tickets) and input (promo pools, Beatport levers) sides — not just a network-fit for Barbara.

*Source note: most campaign-side sources are marketing/educational content from PR firms, promo services and platforms — treat tactics as directional industry consensus, vendor stats as self-reported.*

---

## 7. Stakeholder → relationship-to-us summary

| Stakeholder | Buyer? | Data source (via consent) | Gatekeeper/blocker? | Substitute? |
|---|---|---|---|---|
| T1 channel-labels (selected., Monstercat…) | **Yes (primary)** | own data, usually via FUGA-class API | — | in-house gut + dashboards |
| T2 micro channel-labels (Lilly Era…) | teardown/partner | own data, often artist-tier (manual CSV) | — | curator instinct |
| Artists (Coldabank-type) | possible (pivot) | own Spotify/Apple-for-Artists export | — | manager intuition |
| Promoters / festivals / venues | **Yes (Idea E)** | own ticket data | agency | discount/paper/dynamic pricing |
| Beatport | partner/source | **strong DV source** (DJ sales, label dash) | could build in-house | its own analytics |
| Distributors (FUGA, Revelator, IDOL, LabelGrid) | — | **the streams keystone** (client-authorized API) | could build in-house | their own dashboards |
| Spotify / YouTube | — | DSR via distributor, *not* public API | platform power | self-reported attribution |
| BeatStars / producers | low near-term | source (producer-level) | — | "BeatStars Promote" |
| Agencies | channel **or** blocker | — | **pivotal fork** | they report their own ROAS |

---

## 8. Open questions / next research

1. **Refresh the stale scale numbers** — live 2026 subs/streams/monthly-listeners for selected., Monstercat, Seeking Blue, Trap Nation (current figures here skew 2014–2025).
2. **Map the European tastemaker-label cluster** properly (Soave, Electro Posé, Get The Sound, Inside, + German/UK peers) with Spotify-scale, not LinkedIn followers.
3. **Quantify the A↔E bridge operators** — which channel-labels run their own ticketed events at measurable scale (Monstercat first).
4. **The distributor keystone test** — confirm with FUGA / Revelator that a label can authorize an *external analytics partner* to read its data via API/sub-account **without** us becoming a sub-distributor, at daily × territory × track granularity.
5. **Beatport-as-DV feasibility** — can a label actually export Track × Week × Beatport-sales × geo? (the Beatport-edition data keystone).
6. **The spend-logging keystone (input-side)** — *the live next probe.* How do labels actually **record** marketing spend/exposure per release? Is there a structured per-release ledger we could ingest, or does it live scattered across ad dashboards, promo-pool reports, invoices and inboxes? This is the X-matrix equivalent of the distributor keystone — and it determines how much of §6 is observable.
7. **Agency fork** — in this scene, are agencies blockers or resellers? (decisive for CAC).
8. **Sizing** — where is the spend-floor line on the maturity ladder? (Campaign research suggests the integrated-paid tier starts ~£1.5k/release — refine against label cadence.)

*Done since last revision: §6 — the campaign/release independent-variable side (channel mix, phases, electronic levers, release types) is now mapped.*

---

## Appendix — source confidence flags
- **VERIFIED (self-reported):** selected. About page (founders, 6B streams, team roles); Beatport scale & Beatport Tickets launch; BeatStars payouts; Coldabank Spotify figures; Lilly Era site + our own release extraction.
- **VERIFIED (third-party press):** MBW, Billboard, Variety, IMS/Beatportal, Orphiq, Wikipedia.
- **DATED (needs refresh):** subscriber/stream counts for Monstercat, MrSuicideSheep, Trap Nation (2014–2025 vintage).
- **LEAD (unverified):** LinkedIn "people also viewed" cluster — directional similarity signal, not a confirmed map.
- **VENDOR-REPORTED (treat as marketing):** Beatport Hype "+84% traffic / +40% sales."
- **NEEDS VERIFICATION (the keystone):** distributor APIs (FUGA, Revelator, IDOL, LabelGrid) confirmed from vendor docs/marketing for the *account holder*; the "label authorizes an external analytics partner" path, and true daily × territory × track granularity, are the precise unknowns to test in a call.
- **DIRECTIONAL (campaign side, §6):** release-campaign tactics, phases and budget tiers are drawn from PR-firm / promo-service / platform educational content — industry consensus, not audited; vendor volumes (Label Worx, promo-service testimonials) are self-reported.
