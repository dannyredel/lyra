# Measurement landscape — competitive map

A map of who's doing causal / measurement marketing analytics, clustered under several lenses so you can see the *shape* of the field and find where your niche sits. The punchline up front, because every dimension below points to it:

> **The field has converged on one method consensus (MMM + experiments + attribution, calibrated together) but it is almost entirely horizontal and DTC/e-commerce-shaped. The music/entertainment vertical has only *descriptive* analytics (Chartmetric-class dashboards), no *causal* layer. The intersection of {rigorous causal measurement} × {music/electronic} is empty.**

*Sourcing: companies marked ⭑ are from your seed list (taken as given); ✚ are additions I'm confident about; ✓ were checked against current sources this session. Stats attributed inline.*

---

## The one-paragraph state of the field

The industry has stopped arguing "MMM vs MTA vs experiments" and settled on **triangulation**: MMM for always-on cross-channel budget allocation, incrementality experiments for causal ground truth, MTA for tactical daily optimization — and the mature pattern is to **calibrate the MMM with the experiments** (exactly your architecture). This is now stated almost identically across vendors and analysts (improvado, eMarketer, Measured, Haus). Demand is real and dissatisfaction is high: ~61% of US retail decision-makers use MMM for incrementality (Feedvisor, Dec 2025), yet ~75% of buy-side leaders say their core measurement underperforms (IAB State of Data 2026). MMM is the privacy-era default because it needs no cookies or user IDs. That's the macro tailwind — and it's horizontal.

---

## Dimension 1 — By method (the technical axis)

| Method | What it answers | Players |
|---|---|---|
| **MMM (mix modeling)** | "How should I allocate budget across all channels?" (aggregate, privacy-safe) | Recast⭑✓, Mass Analytics⭑, Proof Analytics⭑, Prescient AI⭑, Lifesight⭑, Sellforte⭑, Forvio⭑, Stella⭑, Recast; **OSS:** Robyn⭑, Google Meridian✚, LightweightMMM⭑, PyMC-Marketing⭑; **enterprise/legacy:** Nielsen✚, Analytic Partners✚, Ekimetrics✚✓, Kantar✚, Ipsos MMA✚ |
| **MTA (multi-touch attribution)** | "Which touchpoints/channels contributed?" (user-level, click-based) | Triple Whale⭑, Northbeam⭑, Rockerbox⭑, Wicked Reports⭑, AdBeacon⭑, ThoughtMetric⭑, Hyros⭑, Voluum⭑, RedTrack⭑, Growify⭑, SegMetrics⭑, AbleCDP⭑ |
| **Geo-lift / incrementality** | "Did this spend *cause* outcomes?" (experiments) | Haus⭑✓, LiftLab⭑, INCRMNTAL⭑, Measured⭑, Lifesight⭑; **OSS:** Meta GeoLift⭑ |
| **Triangulated / unified** | All three, reconciled | Measured⭑✓, Forvio⭑, Stella⭑, Lifesight⭑, Funnel⭑ (data + MMM/MTA), Polar⭑ |
| **Data layer (enabling)** | "Unify all my sources first" | Funnel⭑✓, Sellforte⭑ (upstream), Hex✚ (warehouse-native) |
| **Adjacent: cohort / LTV / CDP** | Retention, LTV, journey | Peel⭑, Lifetimely⭑, ByTheNumbers⭑, Polar⭑, AbleCDP⭑, Angler AI⭑ |
| **Adjacent: mobile MMP** | App-install incrementality | AppsFlyer✚, Adjust✚, Singular✚, Kochava✚ |

**Read:** the MMM and triangulation columns are where the rigor (and your peers) live. The MTA column is the crowded, privacy-fragile, DTC-Shopify swamp. Note the OSS row — almost every commercial MMM is a **wrapper on Robyn / Meridian / PyMC**; the product is the workflow, calibration, and UX, not the math.

---

## Dimension 2 — By buyer & vertical (the go-to-market axis) — *the white-space lens*

| Cluster | Who they sell to | Players |
|---|---|---|
| **DTC / Shopify-native** | E-commerce brands, often <$50M | Triple Whale⭑, Northbeam⭑, Polar⭑, Wicked Reports⭑, AdBeacon⭑, Growify⭑, SegMetrics⭑, Prescient⭑, Peel⭑, Lifetimely⭑, ByTheNumbers⭑ |
| **Mid-market / retail / DTC scale-ups** | Larger DTC + retail | Measured⭑, Rockerbox⭑, Haus⭑, Recast⭑, Lifesight⭑ |
| **Horizontal / channel-agnostic** | Any advertiser | Funnel⭑, Sellforte⭑, Forvio⭑, Stella⭑, INCRMNTAL⭑, LiftLab⭑, Proof⭑, Mass Analytics⭑ |
| **Legacy enterprise & consultancy** | Big brands, CPG, media groups | Nielsen✚, Analytic Partners✚, Ekimetrics✚, Kantar✚, Ipsos MMA✚ |
| **Vertical specialists** | A specific industry | **Almost none in measurement.** Mobile/gaming (the MMPs); that's about it. |
| **Music / entertainment / live** | Labels, promoters, artists | **No causal product. Only descriptive dashboards** (see the music section below). |

**Read:** this is the dimension that matters most for you. Verticalization barely exists in measurement — the field competes on method and DTC sophistication, not industry depth. Even the one media/entertainment example on record (Sky's overhaul) was **a consultancy engagement plus a 30-person in-house team** (Ekimetrics), not a product. Haus itself writes that media/entertainment companies "have several [measurement problems], stacked on top of each other" that make standard tools look inadequate — i.e. the incumbents *know* the vertical is hard and haven't built for it.

---

## Dimension 3 — By data philosophy / privacy posture

| Posture | Mechanism | Durability | Players |
|---|---|---|---|
| **User-level / clickstream** | pixels, S2S, device IDs, CAPI | Fragile (cookie loss, consent, signal decay) | Triple Whale⭑, Northbeam⭑, Hyros⭑, RedTrack⭑, Wicked⭑, AdBeacon⭑, most MTA |
| **Aggregate / experimental** | spend↔outcome at geo/time grain, holdouts | Durable (no IDs needed) | All MMM + geo-lift: Recast⭑, Haus⭑, Measured⭑, INCRMNTAL⭑, Sellforte⭑, Forvio⭑, OSS engines |

**Read:** your approach (aggregate, consent-based first-party, geo/time grain) sits on the **durable** side — the same side the whole field is migrating *toward* post-cookie. INCRMNTAL's entire wedge is "privacy-first, no user-level tracking." You inherit that tailwind for free.

---

## Dimension 4 — Open-source engine vs commercial wrapper (build-vs-buy)

| Layer | Options |
|---|---|
| **OSS modeling engines** | Meta Robyn⭑ (R, ridge), Google Meridian✚ (Python, Bayesian, geo-hierarchical, experiment-calibration built in), LightweightMMM⭑ (being superseded by Meridian), PyMC-Marketing⭑ (fully Bayesian, most flexible), Meta GeoLift⭑ (SCM experiments) |
| **Commercial wrappers** | Recast, Sellforte, Forvio, Stella, Lifesight, Proof, Mass Analytics — sell calibration, workflow, scenario planning, and UX *on top of* the same Bayesian core |

**Read:** the build-vs-buy answer for you is clearly **build on PyMC-Marketing or Meridian** (Meridian even ships experiment-calibration and geo-hierarchical modeling — your exact needs). Your moat is *not* the estimator; it's the music-vertical data plumbing (FUGA/Beatport/promo pools), the cleaner dependent variable, and the announcement-spike decomposition. Don't reinvent the sampler.

---

## Dimension 5 — By wedge / positioning (how they differentiate)

| Wedge | Exemplars | The angle |
|---|---|---|
| **Speed / near-real-time** | Recast⭑, Prescient⭑ | refresh in days not quarters; Recast explicitly models **event/promo "spikes" with pull-forward/pull-back effects** — note: this is *your announcement-spike problem*, already solved generically |
| **Privacy-first** | INCRMNTAL⭑ | no user-level tracking, geo/time experiments only |
| **Experiment gold-standard** | Haus⭑, LiftLab⭑, Measured⭑ | "we measure causation, others guess" |
| **Data-unification first** | Funnel⭑, Sellforte⭑ | own the warehouse/semantic layer, model on top |
| **All-in-one agentic DTC** | Triple Whale⭑, Northbeam⭑ | dashboards + AI copilots for Shopify operators |
| **Unified / triangulation** | Measured⭑, Forvio⭑, Stella⭑ | the "one coherent system" pitch (MMM+exp+attribution) |
| **Enterprise rigor / service** | Nielsen✚, Analytic Partners✚, Ekimetrics✚ | bespoke, consultative, expensive, slow |

**Read:** Recast is the one to study closest — near-real-time Bayesian MMM that *already models promotional/event spikes with pull-forward and pull-back*. That's the generic version of your announcement decomposition. Your differentiation can't be "we invented spike modeling"; it has to be **vertical + cleaner DV + the convergence wedge**.

---

## Dimension 6 — Stack layer (where they sit)

```
DATA / INGESTION ──────► MODELING ENGINE ──────► APPLICATION / REPORTING ──────► FULL-STACK
Funnel, Sellforte,       Robyn, Meridian,         Triple Whale, Northbeam,        Measured, Forvio,
Hex (warehouse)          PyMC, GeoLift (OSS)      Polar (dashboards)              Lifesight, Recast
                         + commercial engines                                     (ingest→model→act)
```

**Read:** you're a **full-stack** play by necessity (the music data plumbing doesn't exist off-the-shelf, so you can't just be a modeling engine on someone's clean warehouse). That's more work but more defensible — the ingestion layer (FUGA/Beatport/promo-pool/ticketing connectors) is itself a moat no horizontal tool will build.

---

## The music vertical — a separate world (your actual adjacent competitors)

These are **not** measurement companies. They're descriptive analytics / monitoring dashboards. Important to map because they're your *do-nothing-plus-a-dashboard* substitute and your reference point for what labels already pay for.

| Tool | What it is | Causal? |
|---|---|---|
| **Chartmetric** ✓ | Industry-standard cross-platform analytics; streaming/social/playlist/radio/Shazam, A&R discovery, audience demographics | No — descriptive |
| **Soundcharts** ✓ | Real-time monitoring + reporting; strong radio airplay (25k+ charts), team workflows for labels | No — descriptive |
| **Songstats** ✓ | Real-time alerts, mobile-first; **broad electronic coverage (Beatport, Traxsource, 1001Tracklists)** — fills a gap Chartmetric/Soundcharts don't | No — descriptive |
| **Viberate** ✚ | Analytics + includes ticketing/live signals; mid-tier | No — descriptive |
| **Next Big Sound / AMP** ✚ | Pandora-owned artist analytics | No — descriptive |
| **Spot On Track / Songkick-data** ✚ | Playlist/chart/airplay tracking | No — descriptive |

**Read — this is the whole thesis in one observation:** music has rich *descriptive* tooling and zero *causal* tooling. Their notion of "campaign effectiveness" is watching numbers move and crediting whatever ran ("a playlist add → 10,000 streams → ~$4,000" — naive, exactly the over-attribution you attack). Songstats' electronic coverage confirms two things at once: electronic is underserved *even within* music analytics, and the Beatport/Traxsource data you need is already being surfaced — so it's gettable. None of them touch incrementality, MMM, geo-lift, or counterfactuals.

---

## The white-space map (the 2×2 that matters)

```
                 CAUSAL RIGOR  →  (descriptive ─────────────► experiment-calibrated causal)
   VERTICAL
   FOCUS
   ↑ music /     Chartmetric, Soundcharts,        ┌───────────────────────────┐
   entertainment Songstats, Viberate,             │   ☆ YOU                    │
                 Next Big Sound                    │   (empty today)            │
                                                   └───────────────────────────┘

   horizontal /  Funnel dashboards,               Recast, Haus, Measured,
   DTC           Triple Whale, Northbeam          Forvio, Sellforte, INCRMNTAL,
                                                   Stella, Lifesight, OSS engines
```

Three of the four quadrants are crowded. **The top-right is empty** — causal rigor applied to the music/entertainment vertical. That's your position. Nobody is there because the horizontal causal players have no reason to verticalize into a comparatively small market, and the music-analytics players have no causal-inference capability (or incentive — descriptive dashboards are a fine business).

---

## What to borrow, per cluster (applied to your niche)

- **From Funnel / Sellforte** — the connector-management UX and the semantic/metric layer (you've already adapted this; their "harmonize-then-compose" split is the right pattern).
- **From Measured / Forvio** — the unified "calibrates ↔ recommends" loop as the *product narrative*, not just architecture. The loop is the credibility story.
- **From Haus / GeoLift** — the **feasibility matrix** (pre-launch power analysis) and the 3-panel geo-lift result format. Best-in-class and you've started this.
- **From Recast** — near-real-time refresh and, critically, **spike modeling with pull-forward/pull-back**. Study their public method writing; your announcement decomposition is a vertical-specific instance of it. Borrow the method, win on the vertical.
- **From INCRMNTAL** — the privacy-first *positioning* (you're aggregate/consent-based; say so loudly — it ages well).
- **From Chartmetric / Soundcharts / Songstats** — the *buyer's existing mental model and price points* (€10–140/mo descriptive tooling). You're not competing on data breadth; you're adding the causal layer they structurally lack. Songstats specifically shows the electronic-data surface you'll plug into.

---

## Open questions this raises

1. **Are Chartmetric/Soundcharts substitutes or future channels?** They own the label relationship and the descriptive data. Partner (causal layer on their data) or compete? Worth a deliberate call.
2. **Does the small market that keeps horizontal players out also keep *you* out?** The reason the quadrant is empty might be that it's not big enough — the SOM work (€2–4M boutique) is the honest counterweight. White space ≠ gold mine.
3. **Could a horizontal player verticalize faster than you can horizontalize?** Recast or Measured *could* point their engine at music in a quarter if a big label asked. Your defense is data plumbing + network (Barbara) + the convergence wedge — speed and relationships, not method.
