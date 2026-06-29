# Counterpoint — Technical & Business Proposal

*Independent causal marketing measurement for the music industry.*
Working title — rename freely. Version 1.0. Confidential.

---

## 0. Executive summary

Independent labels, distributors and label-services companies spend heavily on paid acquisition for releases, then justify the spend with "momentum" no one can measure. A streamed play earns a rights-holder roughly €0.004; a bought play costs €0.05–0.15. Every ad platform grades its own homework, and attributed streams routinely sum to more than the streams that actually happened.

Counterpoint is the independent, cross-platform measurement layer for music. It separates the streams a campaign *caused* from the organic baseline that would have happened anyway, attributes incremental lift across channels, and recommends reallocation — at the level of a roster, not a single release.

The methodological core is an adaptation of **triangulation** (the practice of combining marketing-mix modelling, attribution, and incrementality testing so each calibrates the others, as articulated in Funnel's *Triangulation Tango*). The adaptation matters: triangulation as practised in e-commerce leans on user-level multi-touch attribution that **does not exist in music**, because the "conversion" happens inside a DSP walled garden. Counterpoint therefore rebalances the triad — heavier on a roster-level hierarchical MMM and geo-lift incrementality, lighter on attribution — and adds music-specific estimands (organic baseline, organic-to-paid multiplier, fan-LTV bridge, recoupment).

The buyer is the aggregator, because pooling many small releases is the only way to clear the data-scale threshold causal methods require, and because the aggregator already holds the first-party data a third party can no longer get from Spotify directly.

This document covers the problem, the measurement framework, the system architecture, the product, the business model, and an explicit list of assumptions to stress-test.

---

## 1. The problem, precisely

**The unit economics are upside-down by design.** Paid streams cost 10–40× what they earn back in royalties. The entire industry tolerates this on the thesis that paid pushes trigger durable organic momentum — algorithmic placement (Discover Weekly, Release Radar), playlist adds, and lasting fans. That thesis may well be true. It is simply never measured.

**Attribution is structurally over-counted.** Meta, TikTok, Spotify's Campaign Kit and the playlist plugger each claim the same plays. Summed, their attributed streams exceed actual streams. A label allocating a six-figure annual budget is doing so on five conflicting, self-reported ROAS figures.

**The causal question has no honest answer today:** *did this spend cause anything, or would it have happened anyway?* Decomposing observed streams into (a) organic baseline, (b) incremental paid effect, and (c) paid-induced organic spillover is a causal-inference problem, not a dashboarding problem. No music tool currently treats it as one.

---

## 2. Why the method is solved everywhere except music

Causal measurement is mature in adjacent sectors and absent here:

- **General / e-commerce MMM & incrementality** — commoditised, including open source (Google Meridian, Meta Robyn, PyMC-Marketing) and a crowded vendor field (Recast, Prescient, Northbeam, Fospha, Sellforte, Mutinex, plus Funnel's measurement module).
- **Podcast attribution** — solved and consolidated (Podscribe, Magellan; Podsights/Chartable absorbed into Spotify).
- **Music** — every tool is *descriptive*. Chartmetric and Soundcharts report what happened; un:hurd automates campaigns on heuristics; Spotify's Campaign Kit reports its own lift. No independent, cross-platform, causal product exists.

Two structural facts protect the gap. First, a **scale threshold**: incrementality needs spend variation and observation volume (the industry rule of thumb is ~€50k/month) that no single small release has. Second, a **data lockdown**: since Spotify closed its API in early 2026 (deep data gated behind a 250k-MAU wall, and a prohibition on using its data to train models), a solo analytics tool cannot acquire the raw data — but a label or distributor already holds it as first-party data. The buyer is the data source.

---

## 3. The customer (ICP)

**Music aggregators: labels, distributors, label-services companies.** They pool dozens-to-hundreds of releases, carry real ad budgets, and own the streaming and ad data flowing through their own pipes. Pooling across the catalogue is what makes per-release causal inference statistically feasible; first-party ownership is what makes the data obtainable. Both reasons point at the aggregator and away from the individual artist.

Indicative annual digital ad spend by segment (reconstructed from per-release and per-label benchmarks — directional, to be validated in discovery):

| Segment | Profile | Annual digital ad spend |
|---|---|---|
| Indie | small label, ~5–15 releases/yr | ~€30–80k |
| Label / Distributor | mid, ~30–80 releases/yr | ~€150–600k |
| Catalog / Enterprise | distributor / services co, 100+ | ~€1M+ |

For scale calibration: even Funnel's *smallest* self-serve measurement band starts at ~€5–6M/year of ad spend. Our entire market sits below their entry point — which is exactly why this is an underserved niche and why our pricing cannot be a thin percentage of spend (see §9).

Rejected ICPs: **Series A B2B SaaS** (below the causal-payoff threshold, saturated category above it) and **podcast sponsorship** (real, but already won by incumbents with data moats we lack).

---

## 4. The measurement framework — music triangulation

### 4.1 Why triangulate, and why the standard triad must change

Triangulation combines three measurement methodologies so each compensates for the others' weaknesses: MMM for the macro/strategic picture and untrackable channels; attribution for micro/operational granularity; incrementality testing as the causal gold standard used to calibrate the rest. The insight worth borrowing is the *calibration loop* — the models inform and correct one another rather than competing as rival "sources of truth."

The insight worth **changing** is the role of attribution. In e-commerce, multi-touch attribution (MTA) rests on user-level tracking from click to on-site conversion. In music, the conversion — a stream or save — happens inside Spotify/Apple, not on a page you can pixel. The click-to-stream handoff (ad → smart link → DSP) is precisely where tracking dies. **User-level MTA is therefore largely unavailable in music.** Counterpoint's triad is rebalanced accordingly:

| Pillar | Music instantiation | Role | Decision level |
|---|---|---|---|
| Marketing-mix modelling | Roster-level hierarchical Bayesian MMM | Strategic mix across releases & channels; baseline, saturation, marginal ROAS | Tactical / strategic |
| Incrementality | Geo-lift experiments (staggered DiD, synthetic control) | Causal ground truth; calibrates the MMM | Strategic validation |
| Signal layer (MTA substitute) | Source-of-stream (S4A), smart-link click-through, UTM data | Partial, aggregate operational granularity | Operational |

The practical consequence: with the attribution pillar weak, **the MMM ↔ incrementality calibration loop carries more of the load**, and the geo-lift studies are not optional garnish — they are the spine of credibility.

### 4.2 Roster-level hierarchical MMM (the core technical contribution)

Standard MMM fits one advertiser. Counterpoint fits a *portfolio of small releases simultaneously*, with partial pooling so that data-poor releases borrow strength from the catalogue. This is what beats the scale threshold.

For release *i*, territory *g*, day *t*, model an outcome *y* (streams, or saves, or net-new listeners):

```
y[i,g,t] = baseline[i,g,t]
         + Σ_c  β[c,i] · Hill( Adstock( spend[c,i,g,t] ; θ[c,i] ) ; κ[c,i] )
         + γ · X[i,g,t]            # controls
         + ε[i,g,t]

baseline[i,g,t] = f( release_age[i,t], seasonality[g,t], trend, editorial_flags, price/promo )

# Partial pooling — release effects drawn from artist/genre/roster hyperpriors
β[c,i]  ~ Normal( μ_β[c, artist(i)] , σ_β[c] )
μ_β[c, a] ~ Normal( μ_β[c, genre(a)] , · )    # nested hierarchy
θ[c,i]  (adstock geometric decay), κ[c,i] (Hill saturation)  ~ pooled priors per channel
```

Notes that matter for identification and that I want stress-tested:

- **Adstock + saturation** per channel (geometric decay; Hill or logistic saturation) are dynamic, not constant — adstock half-lives and saturation points shift as channels and audiences evolve.
- **Pooling structure** (release ⊂ artist ⊂ genre ⊂ roster, crossed with territory) is the lever. Too much pooling masks heterogeneity; too little starves small releases. The right shrinkage is an empirical question per customer.
- **Collinearity** between channels launched together is the central threat to clean coefficients — daily data gives ~365 points/release/territory but channels co-move. Territory variation and staggered timing are how we break it.
- **Estimation**: PyMC / NumPyro, full-Bayes where feasible, with posterior predictive checks and ELPD/LOO for model comparison.

### 4.3 Geo-lift incrementality (causal ground truth)

Where randomisation is possible — Meta and TikTok support geo-targeting; Spotify's ad targeting is coarser — we run **staggered or randomised campaign launches across matched territories** and estimate the average treatment effect on the treated:

- **Callaway–Sant'Anna** staggered difference-in-differences for multi-territory, multi-period rollouts.
- **Synthetic control / SynthDiD / augmented SC** using untreated territories (or untreated comparable releases) as donors when randomisation isn't clean.
- Output: incremental streams/saves attributable to the push, with credible intervals — the "gold standard" snapshot that the always-on MMM is calibrated against.

This is a direct application of the experimentation engine already designed under **Lyra** (the experimentation platform) and **Vega** (the DGP/simulation layer): Vega generates synthetic counterfactual rosters to validate estimators and power-analyse designs before they run; Lyra orchestrates the live tests. Counterpoint is, in effect, Lyra/Vega pointed at music.

### 4.4 The calibration loop (the triangulation engine)

The geo-lift ATTs are not a parallel report — they are fed back to discipline the MMM. Two mechanisms:

1. **Bayesian priors.** A clean geo-lift estimate for channel *c* becomes an informative prior on that channel's MMM response. If the observational model disagrees, it is pulled toward the experimental truth; if they agree or the experiment is inconclusive, the prior is weak and the data dominates.
2. **Multi-objective calibration.** Treat MMM hyperparameter choices (adstock form, saturation family, regularisation, pooling depth) as decision variables in an optimisation that minimises *both* statistical error (MAPE / ELPD) *and* the distance between MMM-implied channel ROAS and the experimental ATTs. The fitted model is the one that is simultaneously well-calibrated statistically and consistent with the experiments.

**Automated test recommendation.** The system flags where the next experiment is worth running: channels with high posterior variance, or where the MMM and the signal layer disagree most. Humans still design and launch the test — fully automated cross-platform experimentation does not exist, and that human-in-the-loop step is also our recurring services revenue.

### 4.5 Music-specific estimands (beyond standard triangulation)

These are the outputs that make the framework music-native rather than a generic MMM with a new label:

- **Organic baseline** — the counterfactual momentum a release would have had with no paid push. Everything else is measured net of this.
- **Incremental lift** — streams/saves caused by each channel, with intervals.
- **Organic-to-paid multiplier and half-life** — the algorithmic-spillover phenomenon unique to streaming platforms: paid streams trigger Discover Weekly / Release Radar placement that produces *organic* streams which then decay over a measurable half-life. This is the quantity that determines whether paid acquisition is rational despite negative direct royalties. It has no analogue in Funnel's e-commerce framework.
- **Saturation curves & marginal ROAS** per channel — for allocation: where does the next euro go.
- **Fan-LTV bridge** — map acquisition source → retained-listener cohort (28-day repeats, saves, follows) → downstream value (catalogue streams, live, merch). Reframes the metric from cost-per-stream to **cost-per-retained-fan**.
- **Recoupment / advance-risk** — forecast net return on a release or signing under the fitted response curves plus LTV; risk-adjusted, for A&R capital allocation.

---

## 5. System architecture & the human factor

### 5.1 Data inputs (all first-party to the customer)

- **Streaming / revenue**: daily streams and revenue per track × territory, from the distribution backend / DSP reports.
- **Ad spend & delivery**: per channel × territory × day, from the customer's own Meta / TikTok / Spotify / YouTube ad accounts.
- **Source-of-stream & playlist events**: Spotify-for-Artists exports (editorial / algorithmic / external split; playlist adds).
- **Signal layer**: smart-link (Linkfire / Feature.fm) click logs and UTM-tagged campaign clicks.
- **Treatment metadata**: the release and campaign calendar — the timing variable that powers staggered designs.
- Optional enrichment: licensed Chartmetric / Soundcharts.

### 5.2 Layers

1. **Ingestion & harmonisation** — normalise spend, impressions and outcomes onto a common release × territory × day grid; accurate cost-matching across sources is the unglamorous prerequisite that makes everything downstream possible.
2. **Modelling** — hierarchical MMM (PyMC/NumPyro); geo-lift estimators (Callaway–Sant'Anna, SynthDiD, synthetic control); the calibration optimiser; Vega for simulation/power analysis.
3. **Output** — per-release scorecards, portfolio allocation, geo-lift study readouts.

### 5.3 Automation vs human-in-the-loop

The always-on MMM refresh should run daily without intervention — anything that needs manual effort erodes adoption. But experiment *design* stays human: choosing territories, durations and spend splits, and interpreting results, is judgement work, and it is also where the services margin lives. The honest framing (and a selling point) is that we are not promising push-button causal truth; we are promising a system that **becomes less wrong over time**, disciplined by recurring experiments.

---

## 6. The product surface, by decision level

- **Operational** (signal layer): day-to-day campaign read — which creatives/links are converting clicks to streams.
- **Tactical / strategic** (MMM): the per-release scorecard (organic baseline vs incremental by channel, with intervals), the saturation/marginal-ROAS curves, and the portfolio allocation recommendation.
- **Strategic validation** (geo-lift): the independent lift number a label can defend to a partner or board — the thing Spotify's self-reported lift structurally cannot be.

---

## 7. Expansion ladder

One first-party pipeline, rising order of margin and moat:

1. **Causal playlist valuation** — does an editorial add cause durable listener gain or a three-day bump? Event-study / synthetic control around the add date. The channel everyone calls hardest to attribute.
2. **Real-vs-bought momentum** — an A&R signal separating organic traction from paid-inflated traction, to direct the next marketing tranche.
3. **Fan-LTV by acquisition source** — cost-per-retained-fan, not cost-per-stream.
4. **Tour & merch geo-routing** — causal demand modelling to route tours and size markets; live carries the highest willingness-to-pay.
5. **Recoupment & advance-risk modelling** — structured causal forecasting for A&R capital; the premium, least-crowded tier.

---

## 8. Measurement maturity ladder (where labels are, where they go)

Adapting the maturity framing to music, most labels sit at stage 1–2:

1. **Platform-reported only** — Spotify Marquee lift, in-app Meta/TikTok ROAS. Grading the platforms' own homework.
2. **Descriptive dashboards** — Chartmetric / Soundcharts; cost-per-stream roll-ups in spreadsheets.
3. **Ad-hoc attribution** — smart-link click tracking, UTM hygiene.
4. **Occasional holdout** — a single geo-lift on one priority release, run once.
5. **Music triangulation (Counterpoint)** — always-on roster MMM, calibrated by recurring geo-lift, with fan-LTV and allocation.

The pitch is not "jump to stage 5." It is: wherever you are, the next durable milestone is triangulation, and the fastest route is to seed it with one or two real incrementality tests rather than chasing perfect attribution that music will never provide.

---

## 9. Business model

**Two-axis pricing, calibrated (not copied) from Funnel.** A flat base (the always-on model + scorecards) plus intensity set by annual ad spend under measurement; geo-lift studies as premium add-ons; a hard floor. We deliberately drop the connector-breadth axis — data is first-party, so we don't compete on integrations.

Pricing ladder (annual; implied take is **internal only**, never published):

| Tier | Annual ad spend | Annual price | Implied take (mid) |
|---|---|---|---|
| Indie | up to €60k | €6k (floor) | ~10–20% |
| Emerging | €60–150k | €13k | ~12% |
| Label | €150–400k | €24k | ~9% |
| Distributor | €400k–1M | €42k | ~6% |
| Catalog | €1M–2.5M | €72k | ~4% |
| Enterprise | €2.5M+ | custom (€96k+) | <4% |

Add-ons: onboarding pilot €8–15k one-time; geo-lift study €4–6k each.

**Why our take is 10–40× Funnel's (~0.1–0.6%):** our customers spend 10–100× less, while the work (build a model, run a test) costs roughly the same regardless of their budget. So we price on **value + a floor**, not a percentage — defensible the way all specialist analytics is, but it must be sold on ROI, never on "% of your spend."

**Revenue trajectory (base case):** ~€110k Year 1 (services-first), ~€2.3M Year 5 (~90 customers, ~60% of revenue from the Label/Distributor/Catalog bands where unit economics work). Two founders reach ~€120k each in gross pay around Year 3–4 and ~€200–375k by Year 5; a 3–6× ARR exit implies ~€3.5–7M each. Profitable boutique, not a venture rocket. *(Live figures in the companion simulator.)*

**Go-to-market:** services-first. Land 2–3 design-partner labels, fit on 12–24 months of their data, run one geo-lift, deliver the readout; productise once the third engagement looks like the first two. The commercial co-founder's label network is the single biggest accelerant — it collapses the slowest part of this market, the sales cycle.

---

## 10. Assumptions to stress-test (the agenda for the next pass)

Ranked roughly by how much they'd hurt if wrong:

1. **Willingness to pay at music scale.** A 4–15% take of ad spend is far above e-commerce norms. Will a label paying €30k for measurement see ROI clearly enough, or will it read as "you want 9% of my budget"? The mid/upper bands depend on demonstrated reallocation value.
2. **Geo-lift feasibility in music.** Meta/TikTok geo-targeting works; Spotify's is coarse and it controls placement. Can we actually construct clean treatment/control territory splits often enough for the calibration loop to function? If not, the whole triangulation spine weakens.
3. **The organic-to-paid multiplier is real and estimable.** The entire economic case for paid acquisition rests on algorithmic spillover. If it's small, noisy, or unidentifiable from the data labels can give us, the value proposition shrinks.
4. **Data access reliability.** Will labels actually share royalty/streaming and ad-account data, at the granularity and cadence the models need? Onboarding friction here could kill unit economics.
5. **Identification under collinearity.** Channels launched together, on small per-release samples, threaten clean coefficients even with pooling. How much does territory variation + staggered timing really buy us?
6. **Sales cycle & churn.** Labels buy slowly and cheaply; how long from intro to paid pilot, and does always-on measurement retain or churn after the first "interesting" readout?
7. **Delivery cost per engagement.** Each geo-lift is partly bespoke human work. What's the true loaded cost per study, and does it scale sublinearly as the pipeline standardises?
8. **Spotify platform risk.** If Spotify makes its native lift reporting good and free, how much does "independent + cross-platform" actually hold as differentiation?
9. **Services→product transition.** The known failure mode for measurement startups. What's the trigger to productise, and what stays bespoke forever?

---

## 11. Companion assets

- **Concept page** — visual pitch + before/after dashboard (the Acme worked example).
- **Concept brief** — problem → market → competitive map → ICP → MVP → UVP → business case → ask.
- **Business model simulator** — live revenue, profit, founder pay, exit, with the spend-band pricing and internal implied-take ladder.

---

*Methodological framing for triangulation and the calibration loop is adapted, in our own terms and re-purposed for music, from Funnel's "Triangulation Tango." All market figures are directional and pre-validation; the assumptions in §10 are the model, and testing them is the next job. This is a planning document, not financial or investment advice.*
