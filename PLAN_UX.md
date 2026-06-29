# PLAN_UX.md — Lyra platform UX redesign (product-demo edition)

> Goal: turn the working chassis into a **product demo that tells a story** to two audiences — **recruiters**
> (skim in 60s, "wow, this is a real platform across industries") and **data scientists** (drill in, "the
> methods are correct and validated"). Pretend Lyra is a SaaS sold to clients in *different industries*.

## 0. Audience & the two-speed experience
- **Recruiter / skim path:** land on a **Home** with 3–5 industry **study-case cards** → click one → read a
  short, well-designed brief (what industry, what's being tested, why it's hard, the result) → optionally
  "Create / view this experiment." No jargon up front.
- **DS / depth path:** the brief expands into the method + the DGP + the validation; the create **wizard**
  lets them play with the data-generating process and see plots move; the scorecard shows the certified-vs-truth badge.

## 1. Research synthesis — what to adopt (Confidence · GrowthBook · Statsig · Eppo)
| Source | What they do | What we adopt |
|---|---|---|
| **Eppo** | Create flow = Define → **Allocation** → **Primary metric** (required) → **Guardrails** → **Scorecard**. **"Protocols"** = reusable templates standardizing metrics + analysis + decision criteria per use-case. | A **multi-step wizard** (not one long form) + **study cases = Protocols/templates** that pre-fill it. |
| **Statsig** | Hypothesis → variants/groups → allocation → targeting → primary/secondary/guardrail metrics → scorecard (CUPED, sequential). | Wizard step order; primary vs guardrail metric roles; CUPED/sequential surfaced on the scorecard (we have these). |
| **GrowthBook** | Nav: Feature Flags · **Data & Metrics** · Experimentation · **Insights** · Product Analytics. "See the SQL behind every query" (transparency). | A **transparency angle** — but ours is better: "see the **DGP** behind every experiment" (we can show ground truth). |
| **Confidence** | `ZTest`/`TTest`, `multiple_difference` (Bonferroni), **non-inferiority margins**, **GST**, power/sample-size. A **bootcamp** (teaching). | The **teaching framing** — each study case explains the method. We already have the stats; lean into the *education*. |

**Our unique angle (keep front-and-center):** *every experiment runs on a simulator with a known ground
truth, so the platform can **certify** each result.* No real platform (Eppo/Statsig/GB) can do this — it's
the whole pitch. Frame it as **"Lyra Verified."**

## 2. Information architecture (new nav)
```
Home          ← NEW: study-case gallery + the pitch (default landing)
Experiments   ← the registry (existing) + the wizard
Metrics       ← governed catalog (existing)
Decisions     ← portfolio ship rule (existing)
Assignment    ← deterministic bucketing + SRM (existing)
[How it works]← NEW (optional): one page explaining the simulator/DGP + "Lyra Verified"
```

## 3. Home / study-case gallery (the new landing)
- A tight hero: "An experimentation platform you can **trust** — every result certified against a known
  ground truth." One line on the simulator superpower.
- **3–5 study-case cards**, each: an **industry tag** (Adtech · On-demand · Marketplace · E-commerce ·
  Performance marketing), a one-line question, the **methods** it showcases (chips: interference / switchback
  / CATE / incrementality), and a status (live demo vs template).
- Click a card → a **brief panel** (notebook/Quarto feel): *The business* · *The experiment* · *Why it's
  hard* · *The DGP (how we simulate it)* · *The result / what Lyra shows*. Two CTAs: **"View live experiment"**
  (jump to the seeded scorecard) and **"Create this experiment"** (pre-fill the wizard with the template).
- Small portfolio strip: N experiments · % certified · designs covered.

## 4. The study cases (industry × DGP × method) — these ARE the templates
| # | Industry | Question | Design | DGP | Methods shown | Maps to |
|---|---|---|---|---|---|---|
| 1 | **Rewarded UA / mobile adtech** (Almedia/Freecash) | Does a bigger sign-up reward lift conversion without blowing payout cost? | A/B proportion + guardrails | `ABDGP` (+ agent flavor) | metrics · CUPED · guardrail decision | Game A |
| 2 | **On-demand (delivery/rideshare)** | Does surge pricing raise GMV? Why you *can't* A/B users. | Switchback (temporal) | `SwitchbackDGP` | switchback · cluster-robust · CUPED · power floor | Surge |
| 3 | **Two-sided marketplace / shared budget** | Real lift or just **cannibalization**? | Cluster vs naive | `InterferenceDGP` | interference money-shot · cluster-robust | Marketplace |
| 4 | **E-commerce feature change** | Does the new checkout lift conversion? + the A/A trust check | A/B proportion | `ABDGP` | proportion · SRM · A/A · sequential | Checkout |
| 5 | **Performance marketing (ads)** | Does the ad **cause** conversions or take credit? | Ghost-ad / PSA holdout | ghost-ads sim + **Criteo real data** | incrementality · ITT/CACE · real-data validation | NB 12 |
| 6 *(opt)* | **Personalization / targeting** | *Who* should we treat? | Heterogeneous + policy | `HeteroDGP` | CATE · uplift/RATE · policy | NB 09/10 |

Show 5 on Home (1–5); #6 optional. Each card's brief explains the **DGP in plain language** (the user's
"explain the DGP" ask) + why ground truth matters.

## 5. Create-experiment wizard (multi-step, replaces the one big form)
Stepper with 4 steps (back/next; a sticky summary rail on the right):
1. **Design** — pick the type (A/B · cluster · switchback · marketplace), name, hypothesis, owner. Short
   blurb per type. *(Templates from §4 land here pre-filled.)*
2. **Metrics** — pick the **primary** metric from the governed catalog (cards), add **guardrails** (+ NIM
   margins), set allocation. Mirrors Eppo/Statsig.
3. **Simulate (the DGP playground)** — set the **true effect** + structural params, with **live interactive
   plots** (§6). This is the differentiator: "you author the world; watch the data react." Explains the DGP.
4. **Power & review** — the SSC power-gate + a summary of the whole design → **Create draft** (then Launch).

Keep the current single-form as a fallback "advanced" toggle if cheap.

## 6. Interactive DGP playground (the visual "wow")
Plots that **recompute live** as sliders move (client-side, fast):
- **A/B:** effect-size + baseline → an **outcome-distribution** plot (control vs treatment densities) + the
  **power curve** (already have) → "what your data will look like."
- **Cluster:** G × n_g → a **cluster means** scatter (between vs within variance) + the cluster-robust CI width.
- **Switchback:** τ + periods → a **time series** with treatment toggling on/off (the canonical switchback strip).
- **Marketplace:** cannibalization boost → the **naive-uplift-decays-with-allocation** curve + the true global
  effect line (the money-shot, interactive).
- **CATE (if #6):** τ(x) surface as a histogram that re-shapes with the heterogeneity slider.
Implementation: small client-side generators in JS (like `power.js`) so it's instant; no backend round-trip.

## 7. Cleanup (do alongside)
- Consistent card/section spacing; a real **logo/wordmark**; tighten the Ocean tokens.
- Empty/loading/error states (the loading hang is fixed; add skeletons).
- "Lyra Verified" badge component reused on Home + scorecard.
- Mobile-ish responsiveness for the Home cards (recruiters open on laptops/phones).
- Kill dead code; ensure static-demo degradation is graceful on every new screen.

## 8. Phasing (suggested build order)
- **Phase 1 — Home + study cases (highest recruiter value):** Home gallery + the 5 study-case briefs +
  "view live / create" CTAs + a "How it works" blurb. *Mostly content + one new screen; big payoff.*
- **Phase 2 — Create wizard:** refactor the form into the 4-step stepper (Design → Metrics → Simulate → Review).
- **Phase 3 — Interactive DGP plots:** the live client-side generators in the Simulate step (+ on the briefs).
- **Phase 4 — Polish:** logo, spacing, skeletons, responsiveness, copy pass.

Each phase is shippable on its own. Recommend Phase 1 first (the story), then 2+3 (the interactivity).
