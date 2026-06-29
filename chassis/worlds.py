"""World factory — turn a *create-experiment* spec into a runnable (DGP, estimator, metric, sizing).

When a user creates an experiment, they pick a **design** + a **true effect** (this is a simulator). This
maps that to a concrete `lyra` DGP + estimator + the metric spec + the required N, so the lifecycle
(DRAFT power-gate → RUNNING scorecard certified vs the planted truth → DECIDE) is fully real across the
**full design space**: A/B · cluster · switchback · interference (naive vs cluster-safe).
"""

from __future__ import annotations

import math

from lyra.dgp import ABDGP, ClusteredDGP, InterferenceDGP, SwitchbackDGP
from lyra.estimators import DiffInMeans
from lyra.estimators_vr import SwitchbackCUPED
from lyra.metrics import MeanMetric, ProportionMetric
from lyra.power import required_n
from lyra.se import ClusterOLS

_GLOBAL_TRUTH = "global effect (all-treat vs all-control)"


def build_world(spec: dict) -> dict:
    """Returns dgp / est / metric / required / design / world. `world` is the Experiment.world dict."""
    design = spec.get("design", "ab")
    mu = float(spec.get("mu", 0.2))
    eff = float(spec.get("true_effect", 0.01))
    q = min(0.95, max(0.05, float(spec.get("q_control", 0.5))))
    rel_mde = float(spec.get("rel_mde", 0.05))

    if design == "ab":
        binary = spec.get("metric_type", "proportion") == "proportion"
        sigma2 = mu * (1 - mu) if binary else float(spec.get("sigma2", 1.0))
        dgp = ABDGP(mu=mu, effect=eff, binary=binary, sigma=math.sqrt(sigma2), q_control=q)
        est = ProportionMetric() if binary else MeanMetric()
        metric = {"name": "conversion rate" if binary else "value",
                  "type": "proportion" if binary else "continuous", "class": "primary", "direction": "up"}
        req = required_n(mu, rel_mde, sigma2, binary=binary, q_control=q,
                         alpha=float(spec.get("alpha", 0.05)), power=float(spec.get("power", 0.8)),
                         two_sided=bool(spec.get("two_sided", True)),
                         n_comparisons=int(spec.get("n_comparisons", 1)), n_success=int(spec.get("n_success", 1)),
                         n_guardrail_nim=int(spec.get("n_guardrail_nim", 0)), rho=float(spec.get("rho", 0.0)))["n_total"]
        return _world(dgp, est, metric, req, "user", "true risk difference" if binary else "true mean difference")

    if design == "cluster":
        G, n_g = int(spec.get("G", 60)), int(spec.get("n_g", 25))
        dgp = ClusteredDGP(G=G, n_g=n_g, beta=eff, rho_u=0.3, binary_treat=True)
        metric = {"name": "engagement index", "type": "cluster", "class": "primary", "direction": "up"}
        return _world(dgp, ClusterOLS("CV1"), metric, G * n_g, "cluster", "true cluster effect")

    if design == "switchback":
        J, H, n_bar = int(spec.get("J", 50)), int(spec.get("H", 20)), int(spec.get("n_bar", 18))
        dgp = SwitchbackDGP(J=J, H=H, n_bar=n_bar, tau=eff, tau_sd=abs(eff) * 0.2,
                            sigma_total=float(spec.get("sigma_total", 320.0)), cv=0.6)
        metric = {"name": "GMV per period", "type": "switchback", "class": "primary", "direction": "up"}
        return _world(dgp, SwitchbackCUPED(), metric, J * H * n_bar, "switchback", "switchback ATE")

    if design == "interference":
        sub = spec.get("interference_design", "cluster")          # "user" (naive) | "cluster" (safe)
        G, n_g = int(spec.get("G", 40)), int(spec.get("n_g", 300))
        dgp = InterferenceDGP(G=G, n_g=n_g, beta=float(spec.get("boost", 0.6)), design=sub)
        est = DiffInMeans() if sub == "user" else ClusterOLS("CV1")
        metric = {"name": "conversion (global)", "type": "proportion" if sub == "user" else "cluster",
                  "class": "primary", "direction": "up"}
        return _world(dgp, est, metric, G * n_g, "user" if sub == "user" else "cluster",
                      _GLOBAL_TRUTH, interference=True)

    raise ValueError(f"unknown design '{design}'")


def _world(dgp, est, metric, required, design, truth_label, interference=False):
    world = {"dgp": dgp.name, "truth_label": truth_label}
    if interference:
        world["interference"] = True
    return {"dgp": dgp, "est": est, "metric": metric, "required": int(required),
            "design": design, "truth_label": truth_label, "world": world}
