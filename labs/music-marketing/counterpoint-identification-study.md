# Counterpoint — Identification Study (Vega Synthetic-Data Study)

**Date:** 2026-06-20
**Status:** Design spec — pre-implementation
**Owner:** Daniel (modelling)
**Gates:** the entire venture. If the estimator cannot recover effects we *plant ourselves*, it cannot be trusted on a label's real, messier data → KILL or rescope.

> **One-line purpose.** Before talking to a single customer or ingesting a single real export, prove (or disprove) that a hierarchical Bayesian MMM + geo-lift calibration can recover known channel effects and the organic→paid multiplier under realistic music-industry data pathologies. This is a parameter-recovery / simulation-based-calibration study: we control the ground truth, so "did we get it back?" is unambiguous.

---

## 0. Why synthetic data, and why first

The product's central claim is **one *defensible* per-release number** — incremental streams net of organic baseline, and marginal ROAS by channel. "Defensible" is a statistical property: low bias, honest uncertainty, and intervals tight enough to drive a decision.

On real data we can never check that, because we don't know the truth. On synthetic data we do. So we:

1. Write a data-generating process (DGP) that bakes in the four pathologies that make music hard: **collinearity** (channels co-launch), **short panels** (12-week campaigns, not 2-year histories), **thin per-release data** (rescued only by roster pooling), and **endogeneity** (bigger releases get more budget).
2. Plant known parameters.
3. Run our estimator.
4. Measure recovery (bias, coverage, interval width, decision accuracy) across a grid of scenarios.

If recovery fails on data we built to be recoverable, real data has no chance.

---

## 1. The main challenge, restated

The validation flagged identification-under-scarcity as the #1 risk (severity 20/25). Concretely, three things conspire:

- **Collinearity.** A release's Meta, TikTok, Spotify and plugger spend all ramp together at launch. When regressors move together, their individual coefficients are weakly identified — the data can't tell you *which* channel did the work.
- **Scarcity.** A campaign is ~8–12 weeks of real signal. Standard MMM guidance wants 78–104 weeks and ~10 observations per variable. A single release is far below that. The bet is that **partial pooling across a roster** borrows strength to compensate.
- **Endogeneity.** Spend is not randomly assigned. Labels back releases they expect to succeed, so spend correlates with the organic baseline → naive estimates are upward-biased. The proposed fix is a **geo-lift anchor**: randomized holdouts give one channel exogenous variation that disciplines the rest of the joint posterior.

The study tests whether the proposed method (hierarchical MMM + geo anchor) survives all three at once.

---

## 2. Hypotheses (each with a falsification threshold)

These map directly onto the killer assumptions. The study is a battery of falsification tests, not a fishing expedition.

| # | Hypothesis | Falsification threshold (study fails the hypothesis if…) |
|---|---|---|
| **H1 — Recovery** | The estimator recovers planted channel marginal-ROAS with acceptable bias | median \|relative bias\| > 25% in the realistic cell |
| **H2 — Honest uncertainty** | 80% credible intervals have ~nominal frequentist coverage | empirical coverage outside [0.70, 0.90] (esp. <0.5 = overconfident) |
| **H3 — Decision-usefulness** | The 80% CI is tight enough to classify each channel above/below the label's break-even bar | channel-classification accuracy < 80% |
| **H4 — Pooling pays** | Hierarchical pooling beats single-release estimation | roster-pooled RMSE not materially < single-release RMSE (<20% reduction) |
| **H5 — Multiplier identifiable** | The organic→paid multiplier κ is recoverable | when true κ = 0.8, the κ posterior 80% CI includes 0 in >20% of sims |
| **H6 — Collinearity boundary** | There exists an operating region of inter-channel correlation ρ where H1–H3 hold | H1–H3 fail at every ρ tested (no viable operating region) |
| **H7 — Endogeneity handled** | With the baseline model + geo anchor, spend↔baseline correlation does not bias ROAS beyond threshold | bias with endogeneity-on exceeds 2× the endogeneity-off bias |
| **H8 — Calibration value** | Adding a geo-lift anchor tightens and de-biases the MMM | geo anchor reduces neither interval width (<15%) nor bias |

**The product claim lives in H3.** H1/H2 can pass while H3 fails (correct on average, honest about uncertainty, but intervals too wide to *act* on). H3 is the one that says "we can sell a number."

---

## 3. Data sources & simulated schema

The synthetic tables mirror exactly what real onboarding would ingest, so the simulator doubles as a schema spec for the data pipeline.

| Source | Real-world origin | Role | Key fields | Pathology it injects |
|---|---|---|---|---|
| **Meta Ads** | Meta Ads Manager export | Paid channel | release_id, territory, date, spend, impressions, link_clicks | Clean geo-targeting → good geo-lift candidate |
| **TikTok Ads** | TikTok Ads Manager export | Paid channel | release_id, territory, date, spend, impressions, clicks | Clean geo-targeting; faster adstock decay |
| **Spotify Ad Studio / Campaign Kit** | Spotify ad platform | Paid channel **and** outcome platform | release_id, (coarse) territory, date, spend, self-reported "intent streams" | **Coarse geo** (limits geo-lift); self-reported lift is a *biased signal*, not truth |
| **Playlist pluggers** | Invoices / plugger reports | Paid channel | release_id, date, spend, placements | Opaque, lumpy, slow adstock |
| **Spotify for Artists (S4A)** | S4A export | **Outcome** | release_id, territory, date, streams, listeners, saves, **source_of_stream** (editorial / algorithmic / own-playlist / other) | The dependent variable; source-of-stream lets us see the spillover channel |
| **Distribution backend** | Aggregator's DSP royalty data | Outcome (cross-DSP) | release_id, territory, date, streams_by_dsp | Multi-DSP truth beyond Spotify |
| **Release metadata** | Internal | Controls | release_id, artist, genre, release_date, prior_fanbase, priority_flag | Drives baseline + endogeneity |
| **Geo experiments** | Designed holdouts | Identification | release_id, channel, territory, arm (treat/holdout), window | Exogenous variation — the anchor |

**Note the dual role of Spotify.** It is simultaneously (a) a *paid channel* with coarse geo and a self-serving lift number, and (b) the *outcome platform* (streams via S4A, including source-of-stream). The study must keep these strictly separate: Spotify's self-reported lift is treated as an unreliable input feature, never as ground truth. Ground truth for the outcome is the S4A/distribution stream count.

---

## 4. The data-generating process

For release `r`, territory `g`, day `t` (t = 0…83 from launch):

```
streams[r,g,t]  ~  NegBinomial( mean = μ[r,g,t] , dispersion = φ )

μ[r,g,t]  =  baseline[r,g,t]  +  paid[r,g,t]  +  spillover[r,g,t]

# --- Organic baseline (would-have-happened-anyway) ---
baseline[r,g,t] = b[r,g] · exp(-t / τ) · season[t] · (1 + Σ editorial_shocks)
   b[r,g]       = fanbase[r] · territory_share[g]

# --- Paid contribution, per channel c, with carryover + diminishing returns ---
paid[r,g,t]     = Σ_c  β[r,c] · Hill( adstock[r,g,t,c] ; k_c , s_c )
   adstock[r,g,t,c] = spend[r,g,t,c] + θ_c · adstock[r,g,t-1,c]
   Hill(a;k,s)      = a^s / (a^s + k^s)            # saturating, ∈ [0,1]

# --- Organic→paid multiplier (the music-specific estimand) ---
spillover[r,g,t]   = κ · paidStock[r,g,t]          # algorithmic amplification of paid
   paidStock[r,g,t] = paid[r,g,t] + λ · paidStock[r,g,t-1]   # half-life ≈ -ln2 / ln(λ)
```

**Hierarchy (partial pooling — the scarcity rescue):**
```
log β[r,c]  =  β0_c  +  u[r,c] ,     u[r,c] ~ Normal(0, σ_c²)
```
Release-level effects are shrunk toward the roster mean `β0_c`. This is the entire bet of H4: a thin single release borrows strength from the roster.

**Spend, collinearity, endogeneity (the pathologies):**
```
log B[r]        = μ_B + γ · z[r] + ε[r]            # z[r] = std. expected organic ⇒ ENDOGENEITY
shares[r,·]     ~ Dirichlet(α)                     # channel mix
spend[r,g,t,c]  = B[r] · shares[r,c] · w[t] · geo_share[g]
```
The shared launch ramp `w[t]` (high at t=0, decaying) is applied across all channels, which is what induces the cross-channel spend correlation ρ. We tune ρ by mixing a shared ramp with channel-specific jitter.

**Geo-lift anchor (the identification lever):**
For a designated **geo-anchorable** channel `c*` (Meta or TikTok — Spotify's coarse geo usually disqualifies it) and a random subset of (release, territory) cells, set `spend[r,g,t,c*] = 0` during a randomized holdout window. Because the holdout is assigned at random (orthogonal to baseline), it provides exogenous variation that identifies `β[·,c*]`, which then propagates through the joint posterior to discipline the collinear channels. How that experimental signal is estimated and fed in — the three method families and the pooled-experiments design — is in §6.1.

**The estimand.** True marginal ROAS for channel c (incremental streams per extra €, including spillover) is the spend-derivative of μ at the campaign-mean adstock:
```
mROAS_c = (1 + κ_eff) · β[r,c] · Hill'(ā_c; k_c, s_c) · (∂adstock/∂spend)
```
where `Hill'` is the Hill slope at the operating point and `κ_eff` folds in the spillover carryover. This closed form gives us the planted truth to recover.

---

## 5. Statistical assumptions & distributions

All "truth" parameters are drawn from these. (Tune to taste; these are defensible starting values for a mid distributor.)

| Quantity | Distribution / value | Rationale |
|---|---|---|
| Roster size N (releases) | scenario ∈ {10, 25, 50, 100} | Tests the pooling/scarcity tradeoff |
| Territories G | {DE, NL, UK, US, FR} (5) | DACH-first ICP; extensible |
| Campaign window | 84 days, daily | Realistic release-cycle length |
| Channels | Meta, TikTok, Spotify Ad Studio, Pluggers | The ICP's real mix |
| Per-release budget B[r] | LogNormal(median €2k, σ s.t. p90 ≈ €8k); ×15 for the 10% `priority_flag` releases | Skewed; a few priority releases dominate spend |
| Channel mix α (Dirichlet) | (Meta 0.40, TikTok 0.30, Spotify 0.20, Pluggers 0.10) | Typical indie allocation |
| Inter-channel corr ρ | scenario ∈ {0.3, 0.6, 0.9} | **The collinearity dial** |
| Adstock retention θ_c | Meta 0.50, TikTok 0.35, Spotify 0.45, Pluggers 0.60 | Pluggers slow, TikTok fast |
| Hill half-sat k_c | scaled to each channel's median daily adstock | Diminishing returns kick in mid-campaign |
| Hill shape s_c | ~ Uniform(1, 3) | Mild-to-moderate S-curve |
| **True marginal ROAS** (streams/€) | Meta 9, TikTok 14, Spotify 4, Pluggers 2.5 | Two channels above the bar, two below — see below |
| **Break-even bar** | 6 streams/€ | The label's decision threshold (downstream-value-derived) |
| Multiplier κ | scenario ∈ {0, 0.3, 0.8} | Tests whether the headline music estimand is recoverable |
| Spillover half-life (λ) | ~14 days | Algorithmic/playlist amplification persistence |
| Organic baseline fanbase[r] | LogNormal(median 1,500 daily streams) | Pre-existing demand |
| Baseline decay τ | 21 days | Post-launch organic decay |
| Editorial shocks | arrivals ~ Poisson(0.02/day); magnitude ~ LogNormal (can dwarf paid) | Exogenous playlist adds — a big confounder |
| NB overdispersion φ | s.t. Var = μ + μ²/φ, φ ≈ 10 | Real stream counts are overdispersed |
| Endogeneity γ | scenario ∈ {0, 0.5} | corr(log budget, expected organic) |
| Geo anchor | scenario ∈ {none; hold out Meta in 2 of 5 territories on 40% of releases} | **The identification lever** |

**Planted truth, by design:** Meta (9) and TikTok (14) are *above* the break-even bar (6); Spotify (4) and Pluggers (2.5) are *below*. The estimator's real job (H3) is to **classify each channel correctly relative to the bar**, under collinearity and endogeneity. Recovering the exact ROAS matters less than getting "keep / cut" right.

---

## 6. The estimator under test

Identical in structure to the DGP (so any failure is identification, not misspecification — we also run a **misspecified** variant to test robustness):

- **Likelihood:** Negative-Binomial on daily streams.
- **Mean:** baseline (with fanbase + decay + seasonality + editorial controls) + Σ Hill(adstock) + κ·spillover.
- **Hierarchy:** `log β[r,c] = β0_c + u[r,c]`, non-centered parameterization; roster hyperpriors on β0_c, σ_c, θ_c, k_c.
- **Priors:** weakly-informative, half-Normal on positive params; θ_c ~ Beta; κ ~ Half-Normal(0.5).
- **Geo module:** an experimental estimate of `β[·,c*]` from randomized holdouts, injected as an informative prior on that channel (the calibration loop). See §6.1 for the method choice — it is not arbitrary. Run with and without to isolate H8.
- **Inference:** NUTS (NumPyro / PyMC). Check R-hat < 1.01, ESS, divergences.

We deliberately fit **(a) single-release** (no pooling), **(b) roster-pooled, no geo**, and **(c) roster-pooled + geo anchor** to attribute the gains (H4, H8).

### 6.1 Geo-lift module — method families & design

The geo anchor is load-bearing (the KILL illustration in §9 shows the MMM is under-identified without it), so the method choice deserves to be explicit. Three families are on the table, and they are **not** interchangeable here:

| Family | Methods | Needs | Fit for Counterpoint |
|---|---|---|---|
| **A. Cross-unit / panel** | DiD; Synthetic Control; **Synthetic DiD**; **staggered DiD** (Callaway–Sant'Anna, Sun–Abraham, Borusyak, dCDH) | *Many* comparable control units; identification via parallel-trends / donor weighting | ⚠️ **Weak** — we have ~5 territories. A thin donor pool makes SC/SDID weights unstable and a single staggered-DiD panel fragile |
| **B. Single-series counterfactual** | **CausalImpact (BSTS)** — Bayesian *structural* state-space + spike-and-slab control selection; **CausalArima** — reduced-form ARIMA counterfactual; ITS | *Few* units, a decent pre-period; identification via the time-series model being right | 🟢 **Strong** — tolerates few geos by forecasting the treated geo's counterfactual from its pre-period + control geos + untreated channels |
| **C. Marketing-native geo-experiment tooling** | **Meta GeoLift** (augmented synthetic control under the hood); **Google Trimmed Match + TBR** (time-based regression) | Purpose-built for ad geo holdouts: design + power + analysis in one frame | 🟢 **Strong & native** — built for exactly this job; uses A/B machinery but is its own design-first family |

**Two corrections worth carrying forward:**
- **CausalImpact ≠ ARIMA.** CausalImpact is **BSTS** (state-space: local level/trend + seasonality + spike-and-slab regression on controls). **CausalArima** (Menchetti et al.) is the separate, reduced-form ARIMA counterpart. Keep them distinct — BSTS's spike-and-slab control selection behaves very differently from ARIMA's autocorrelation structure when there are many candidate control geos.
- **CausalArima is in-family but de-prioritized here.** It's a legitimate Family-B option, but BSTS/TBR handle the many-candidate-controls and structural-seasonality setting more gracefully for release data; CausalArima stays as a robustness cross-check, not the workhorse.

**The design (this is the calibration loop):** *don't* run one big staggered-DiD panel across the roster. Instead —

1. **Per-release randomized holdout** on a clean-geo channel (Meta or TikTok): zero out the channel in a random subset of territories for a randomized window → each release × channel becomes its own small geo-experiment.
2. **Analyze each experiment with a few-geo-tolerant estimator** — TBR or CausalImpact/BSTS — to get a release-level lift with an interval.
3. **Hierarchically pool the experiment-level lifts** across the roster (a random-effects meta-analysis) → a roster-level posterior on that channel's effect.
4. **Feed that posterior as the informative MMM prior** on `β[·,c*]`, which propagates through the joint posterior to discipline the collinear channels.

This "many small experiments, meta-analyzed" frame is far more robust with 5 geos than a single TWFE/staggered panel. Staggered-DiD (and only the heterogeneity-robust variants — never vanilla TWFE) is the right tool *only* if you instead go the single-panel route; Meta GeoLift / augmented-SC serve as a robustness cross-check on any release that happens to have enough comparable geos.

**The coarse-Spotify constraint bites here.** Meta and TikTok hold out cleanly by geo; **Spotify Ad Studio's coarse geo means it can rarely be the anchored channel** — which is exactly why Spotify came out as the un-classifiable channel in the §9 case study. The study should treat "which channels are geo-anchorable" as a first-class input, not an afterthought.

---

## 7. Simulation protocol (Monte Carlo)

```
for scenario in grid( N × ρ × κ × endogeneity × geo_anchor ):       # ~144 cells
    for m in 1..M (M = 200):
        truth   = draw_truth(scenario)
        data    = simulate_DGP(truth, scenario)
        for estimator in {single, pooled, pooled+geo}:
            post = fit(estimator, data)
            record( bias, RMSE, CI_coverage_80, CI_width_80,
                    channel_classification_accuracy, sign_error,
                    kappa_excludes_zero )
aggregate → recovery curves
```

**Headline plots:**
- CI width vs roster size N (does pooling buy tightness?) — H4.
- Bias vs ρ, with/without geo anchor (where does collinearity break us, and does the anchor save it?) — H6, H8.
- Coverage vs N (is the uncertainty honest?) — H2.
- Channel-classification accuracy heatmap over (ρ × geo) — H3, the money plot.

---

## 8. Decision rules (what the study concludes)

| Outcome | Condition | Action |
|---|---|---|
| 🟢 **GO** | In the realistic cell (N≥50, ρ≤0.6, κ≥0.3, geo anchor on, endogeneity on): classification accuracy >80%, median \|rel. bias\|<25%, coverage ∈[0.7,0.9], κ-CI excludes 0 at κ=0.8 | Feasibility risk drops sharply → proceed to paid pilot on real back-data |
| 🟡 **RESCOPE** | Channel-level fails **but** total-incremental-lift recovers (<25% bias, CI excludes 0) | Pivot the product to **aggregate lift only** ("paid drove X incremental streams"), drop per-channel ROAS claims |
| 🔴 **KILL** | Even in the best cell (N=100, ρ=0.3, geo anchor): CIs span the bar for ≥half the channels, OR coverage <0.5 (overconfident), OR pooling gives no lift over single-release | The "defensible number" doesn't exist under scarcity → stop |

The RESCOPE branch is important: it's the difference between "we have no product" and "we have a smaller, still-real product." Don't collapse it into KILL.

---

## 9. Fake case study — "Tonband Collective"

> **ILLUSTRATIVE / FABRICATED.** Every number below is invented to show the *format* of inputs and outputs and what GO vs KILL look like. None is empirical.

**The roster.** Tonband Collective — a Berlin indie distributor, ~50 releases/yr, ~€350k annual ad budget, electronic/indie-pop, territories DE/NL/UK/US/FR. Synthetic roster: N=50, ρ=0.6, endogeneity γ=0.5, geo anchor on Meta in DE+NL for 40% of releases.

**The anchor release.** *Nachtform* by KARI — synth-pop single, launched March 2026, a **priority release** with a €38k push (Meta €16k, TikTok €11k, Spotify Ad Studio €7k, plugger €4k). Prior fanbase ~3,000 daily streams. Editorial: added to "New Music Friday DE" on day 3 (a big exogenous shock we must not credit to paid).

**Planted truth for *Nachtform*:** Meta 9, TikTok 14, Spotify 4, Pluggers 2.5 streams/€; κ = 0.8; bar = 6.

**Illustrative GO recovery** (pooled + geo anchor):

| Channel | True mROAS | Posterior median | 80% CI | Above bar (6)? | Correct? |
|---|---|---|---|---|---|
| Meta | 9 | 8.6 | [6.9, 10.4] | Yes | ✅ |
| TikTok | 14 | 13.1 | [9.8, 16.7] | Yes | ✅ |
| Spotify | 4 | 4.3 | [2.1, 6.9] | **straddles 6** | ⚠️ ambiguous |
| Pluggers | 2.5 | 2.8 | [1.0, 5.2] | No | ✅ |
| κ (multiplier) | 0.80 | 0.74 | [0.31, 1.22] | excludes 0 | ✅ |

→ Classification correct on 3/4 channels; the coarse-geo, low-spend **Spotify channel is the one we can't cleanly classify** — an honest, useful finding the study surfaces in advance.

**Illustrative KILL recovery** (single-release or pooled-no-geo, ρ=0.9):

| Channel | True | Median | 80% CI | Verdict |
|---|---|---|---|---|
| Meta | 9 | 7.2 | [2.1, 15.8] | spans bar |
| TikTok | 14 | 11.0 | [3.0, 22.4] | spans bar |
| Spotify | 4 | 5.1 | [0.4, 12.0] | spans bar |
| Pluggers | 2.5 | 3.0 | [0.2, 9.1] | spans bar |

→ Every interval straddles the break-even bar. We cannot tell the label which channel to keep. **No defensible number** → without the geo anchor, the product fails.

**What the case study teaches before any sales call:** the geo anchor is not optional — it's load-bearing; and Spotify-as-channel (coarse geo, low spend) will be the chronically hard one, which should shape both the product's confidence labelling and the pricing of geo-lift add-ons.

---

## 10. Implementation skeleton

```python
# --- simulator ---
def simulate_roster(N, rho, kappa, gamma, geo_anchor, seed):
    truth = draw_truth(N, kappa)                  # β[r,c], θ_c, k_c, fanbase, ...
    spend = draw_spend(truth, rho, gamma)         # co-launch ramp ⇒ collinearity; γ ⇒ endogeneity
    if geo_anchor: spend = apply_holdouts(spend, channel="meta", terr=["DE","NL"], frac=0.40)
    adstock   = geometric_adstock(spend, truth.theta)
    paid      = hill(adstock, truth.k, truth.s) @ truth.beta
    spillover = kappa * algo_carryover(paid, lam=0.95)     # half-life ≈ 14d
    baseline  = organic(truth.fanbase, tau=21) * seasonality() * editorial_shocks()
    mu        = baseline + paid + spillover
    streams   = negbinom(mu, phi=10)
    return tables(streams, spend, geo_anchor), truth      # → the 8 source tables of §3

# --- estimator (NumPyro/PyMC) ---
def model(data):
    beta0 = sample("beta0", HalfNormal(...), dims="channel")
    sigma = sample("sigma", HalfNormal(...), dims="channel")
    u     = sample("u", Normal(0,1), dims=("release","channel"))   # non-centered
    beta  = deterministic("beta", exp(beta0 + sigma*u))
    theta = sample("theta", Beta(2,2), dims="channel")
    kappa = sample("kappa", HalfNormal(0.5))
    # ... adstock, hill, spillover identical to DGP ...
    if data.has_geo: 
        # DiD/synthetic-control estimate on holdouts → informative prior on beta[:, meta]
        ...
    mu = baseline_model(data) + paid + spillover
    sample("streams", NegativeBinomial(mu, phi), obs=data.streams)

# --- harness ---
for cell in grid: 
    for m in range(200):
        data, truth = simulate_roster(**cell, seed=m)
        for est in ["single","pooled","pooled_geo"]:
            post = fit(model, data, est)
            metrics.append(score(post, truth))   # bias, coverage, width, classification
```

---

## 11. Deliverables & what this gates

1. The simulator (`vega/`) — reusable for power analysis on real pilots later.
2. Recovery report: the four headline plots + the GO/RESCOPE/KILL verdict.
3. A one-page "confidence-labelling rulebook" derived from the coverage results — i.e., the conditions (roster size, channel, geo availability) under which the product is allowed to state a per-channel number vs. only an aggregate one.

**This study gates the paid pilot.** Run it (≈2–3 weeks of focused work, ~€0) before spending any customer's data or any sales cycle. Pair it with the 10 discovery conversations so the demand and feasibility questions resolve in parallel.

---

### Open design choices to settle before coding
- **Break-even bar.** I set it at 6 streams/€ as a placeholder; the real bar is a downstream-value question (royalty + retained-fan LTV per stream). Pin this down — it defines what "works" means.
- **Multiplier mechanism.** I modelled spillover as algorithmic carryover proportional to paid contribution. An alternative is a threshold/trigger model (algorithmic boost only fires above a streams velocity). Worth simulating both — they have different identifiability.
- **Outcome variable.** Streams here; could be saves or new-listeners (cleaner causal target, less playlist-padding noise). Saves may identify better.
