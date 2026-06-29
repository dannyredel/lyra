"""Seed demo experiments — each backed by a Vega/DGP world so the scorecard has a **known truth**.

A simulated experiment and a (future) live one are the *same object* in the registry; here every world
comes from `lyra/dgp`, estimated by the type-correct `lyra` estimator, and certified by the harness.
"""

from __future__ import annotations

from chassis.power import required_n
from chassis.registry import Experiment, Registry
from lyra.dgp import BinaryDGP, ClusteredDGP, InterferenceDGP, RatioDGP, SwitchbackDGP
from lyra.estimators import DiffInMeans
from lyra.estimators_vr import SwitchbackCUPED
from lyra.metrics import ProportionMetric, RatioMetric
from lyra.se import ClusterOLS

CREATED = "2026-05-20"      # fixed dates (no Date.now in this env)


def build() -> tuple[Registry, dict]:
    reg = Registry()
    worlds: dict[str, tuple] = {}     # id → (dgp, estimator, required_n_total)

    def add(exp: Experiment, dgp, estimator, req: int):
        reg.add(exp); worlds[exp.id] = (dgp, estimator, req)

    # 1 · Game A — reward sizing (binary conversion); RUNNING, powered
    r = required_n(mu=0.40, rel_mde=0.05, sigma2=0.0, binary=True, n_guardrail_nim=2)["n_total"]
    add(Experiment("exp_reward_a", "Reward sizing — Game A", "A larger sign-up reward lifts conversion.",
                   "Daniel R.", "reward_a_2026", {"control": .5, "treatment": .5},
                   {"name": "conversion rate", "type": "proportion", "class": "primary", "direction": "up"},
                   "RUNNING", {"dgp": "BinaryDGP", "truth_label": "true risk difference"}, "user",
                   21, 1500, CREATED, CREATED, guardrails=["payout cost", "D7 retention"],
                   guardrail_readouts=[
                       {"name": "payout cost", "effect": 0.011, "ci_low": -0.004, "ci_high": 0.026, "margin": 0.04, "direction": "up"},
                       {"name": "D7 retention", "effect": 0.006, "ci_low": -0.010, "ci_high": 0.022, "margin": 0.05, "direction": "up"}]),
        BinaryDGP(beta=0.5, a0=-0.4), ProportionMetric(), r)

    # 2 · Game B — offer-wall ranking (ratio metric, randomize-by-user / measure-by-session); RUNNING
    r = required_n(mu=0.20, rel_mde=0.06, sigma2=0.16)["n_total"]
    add(Experiment("exp_rank_b", "Offer-wall ranking — Game B", "Re-ranked offers lift conversions per session.",
                   "Sofia M.", "rank_b_2026", {"control": .5, "treatment": .5},
                   {"name": "conv / session", "type": "ratio", "class": "primary", "direction": "up"},
                   "RUNNING", {"dgp": "RatioDGP", "truth_label": "true per-session lift"}, "user",
                   18, 1800, CREATED, CREATED, guardrails=["advertiser ROAS"]),
        RatioDGP(dcr=0.02, cr0=0.20, user_sigma=0.20), RatioMetric(), r)

    # 3 · A/A null — checkout copy (must NOT flag); RUNNING
    r = required_n(mu=0.40, rel_mde=0.05, sigma2=0.0, binary=True)["n_total"]
    add(Experiment("exp_checkout_aa", "Checkout copy — A/A", "Null test: identical experience both arms.",
                   "Emily K.", "checkout_aa_2026", {"control": .5, "treatment": .5},
                   {"name": "conversion rate", "type": "proportion", "class": "primary", "direction": "up"},
                   "RUNNING", {"dgp": "BinaryDGP", "truth_label": "true effect (= 0)"}, "user",
                   21, 1500, CREATED, CREATED),
        BinaryDGP(beta=0.0, a0=-0.4), ProportionMetric(), r)

    # 4 · Geo-cluster promo (cluster-randomized → cluster-robust SE); RUNNING
    add(Experiment("exp_geo_promo", "Market promo — geo clusters", "A market-level promo raises engagement.",
                   "Marcus R.", "geo_promo_2026", {"control": .5, "treatment": .5},
                   {"name": "engagement index", "type": "cluster", "class": "primary", "direction": "up"},
                   "RUNNING", {"dgp": "ClusteredDGP", "truth_label": "true cluster effect"}, "cluster",
                   10, 5, CREATED, CREATED, guardrails=["support tickets"]),
        ClusteredDGP(G=60, n_g=25, beta=0.55, rho_u=0.3, binary_treat=True), ClusterOLS("CV1"), 48)

    # 5 · DECIDED — push cadence (recorded ship decision)
    add(Experiment("exp_push", "Push-notification cadence", "An extra weekly push lifts conversion.",
                   "Sofia M.", "push_2026", {"control": .5, "treatment": .5},
                   {"name": "conversion rate", "type": "proportion", "class": "primary", "direction": "up"},
                   "DECIDED", {"dgp": "BinaryDGP", "truth_label": "true risk difference"}, "user",
                   14, 1600, "2026-04-10", "2026-04-10",
                   decision={"ship": True, "rationale": "Primary +1.9pp (CI excludes 0); guardrails clean.",
                             "checklist": ["results support hypothesis", "no guardrail regression",
                                           "ran ≥ 7 days", "nothing broken in product"]}),
        BinaryDGP(beta=0.35, a0=-0.4), ProportionMetric(),
        required_n(mu=0.40, rel_mde=0.06, sigma2=0.0, binary=True)["n_total"])

    # 6 · DRAFT — pricing test that fails the power gate (underpowered by design)
    add(Experiment("exp_pricing_draft", "Pricing nudge", "A subtle price-anchor nudge raises ARPU.",
                   "Daniel R.", "pricing_2026", {"control": .5, "treatment": .5},
                   {"name": "conversion rate", "type": "proportion", "class": "primary", "direction": "up"},
                   "DRAFT", {"dgp": "BinaryDGP", "truth_label": "true risk difference"}, "user",
                   5, 800, "2026-06-15", "",
                   guardrails=["refund rate"]),
        BinaryDGP(beta=0.2, a0=-0.4), ProportionMetric(),
        required_n(mu=0.40, rel_mde=0.03, sigma2=0.0, binary=True)["n_total"])

    # 7 · Interference money-shot — NAIVE user-level A/B in a shared marketplace (the platform catches it)
    add(Experiment("exp_marketplace_naive", "Marketplace reward — naive A/B",
                   "User-level A/B in a shared-budget market — ignores interference.",
                   "Daniel R.", "mkt_naive_2026", {"control": .5, "treatment": .5},
                   {"name": "conversion (global)", "type": "proportion", "class": "primary", "direction": "up"},
                   "RUNNING", {"dgp": "InterferenceDGP", "interference": True,
                               "truth_label": "global effect (all-treat vs all-control)"}, "user",
                   8, 1500, CREATED, CREATED, guardrails=["advertiser ROAS"]),
        InterferenceDGP(design="user"), DiffInMeans(), 12000)

    # 8 · Interference money-shot — CLUSTER-randomized (interference-safe → certified)
    add(Experiment("exp_marketplace_cluster", "Marketplace reward — geo clusters",
                   "Whole markets randomized — interference-safe estimate of the global effect.",
                   "Daniel R.", "mkt_cluster_2026", {"control": .5, "treatment": .5},
                   {"name": "conversion (global)", "type": "cluster", "class": "primary", "direction": "up"},
                   "RUNNING", {"dgp": "InterferenceDGP", "interference": True,
                               "truth_label": "global effect (all-treat vs all-control)"}, "cluster",
                   8, 1500, CREATED, CREATED, guardrails=["advertiser ROAS"]),
        InterferenceDGP(design="cluster"), ClusterOLS("CV1"), 12000)

    # 9 · Switchback — temporal interference (randomize over time); CUPED variance reduction; certified
    add(Experiment("exp_surge_switchback", "Surge pricing — switchback",
                   "Randomize surge on/off over time within a market (interference-safe in time).",
                   "Marcus R.", "surge_sb_2026", {"control": .5, "treatment": .5},
                   {"name": "GMV per period", "type": "switchback", "class": "primary", "direction": "up"},
                   "RUNNING", {"dgp": "SwitchbackDGP", "truth_label": "switchback ATE"}, "switchback",
                   10, 2200, CREATED, CREATED, guardrails=["courier wait time"]),
        SwitchbackDGP(J=55, H=22, n_bar=20, tau=70, tau_sd=15, sigma_total=320, cv=0.6),
        SwitchbackCUPED(), 20000)

    # 10 · Aggressive discount — the DECISION money-shot: primary WINS but a guardrail regresses → NO SHIP
    r = required_n(mu=0.30, rel_mde=0.05, sigma2=0.0, binary=True, n_guardrail_nim=1)["n_total"]
    add(Experiment("exp_discount_margin", "Aggressive discount — margin guardrail",
                   "A deeper discount lifts conversion — but watch gross margin.",
                   "Sofia M.", "discount_2026", {"control": .5, "treatment": .5},
                   {"name": "conversion rate", "type": "proportion", "class": "primary", "direction": "up"},
                   "RUNNING", {"dgp": "BinaryDGP", "truth_label": "true risk difference"}, "user",
                   21, 1500, CREATED, CREATED, guardrails=["gross margin"],
                   guardrail_readouts=[                     # regressed beyond its −3% margin → blocks the ship
                       {"name": "gross margin", "effect": -0.061, "ci_low": -0.092, "ci_high": -0.030,
                        "margin": 0.03, "direction": "up"}]),
        BinaryDGP(beta=0.45, a0=-0.85), ProportionMetric(), r)

    return reg, worlds
