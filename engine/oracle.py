"""Oracle — the ground-truth global ATE via counterfactual shadow runs.

Only possible because *we authored the data-generating process*: to get the true effect of an
experiment's treatment on the OEC, replay the engine twice on the same seed — once with **every**
agent forced to control, once with every agent forced to treatment — and difference the OEC. That
difference is the **global ATE**: the all-treated vs all-control world gap, which *includes* the
budget/effort interference. It is the estimand the recovery tests target.

This is NOT part of the emitted log and estimators never call it (it would be cheating). It lives
here, in the engine package, as the simulator's oracle power; only ``tests/`` and ``validation/``
use it. ``meta.mode`` is irrelevant — shadow runs read their own in-memory metrics, never the log.

OEC definition (per assigned user, on the experiment's advertiser)
-----------------------------------------------------------------
``OEC = (total conversion margin on the experiment's advertiser) / (users assigned to the experiment)``.
The naive/corrected estimators in ``inference/`` compute the *same* per-user margin so the numbers
are directly comparable — the whole point is that the naive arm-contrast drifts from this ATE under
interference while the corrected design recovers it.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.config import Config, load_config
from engine.experiments import CONTROL, TREATMENT
from engine.market import run


@dataclass(slots=True)
class GroundTruth:
    experiment_id: str
    ate: float            # global ATE on per-user margin (treatment world − control world)
    oec_treatment: float
    oec_control: float
    n_assigned: int


def _oec(summary: dict, experiment_id: str) -> tuple[float, int]:
    """Per-assigned-user margin on the experiment's advertiser in a (forced) shadow world."""
    by_arm = summary["metrics"]["by_exp_arm"]
    margin = sum(v["margin"] for k, v in by_arm.items() if k.startswith(experiment_id + "/"))
    n = summary["srm"].get(experiment_id, {}).get("total", 0)
    return (margin / n if n else 0.0), n


def global_ate(cfg: Config | str, experiment_id: str) -> GroundTruth:
    """Run the all-control and all-treatment shadow worlds; return the global ATE.

    Fast path: ``write=False`` skips parquet output (metrics + invariants only).
    """
    if isinstance(cfg, str):
        cfg = load_config(cfg)

    s_control = run(cfg, force_arm={experiment_id: CONTROL}, write=False, compute_tau=False)
    s_treat = run(cfg, force_arm={experiment_id: TREATMENT}, write=False, compute_tau=False)

    oec_c, n_c = _oec(s_control, experiment_id)
    oec_t, n_t = _oec(s_treat, experiment_id)
    return GroundTruth(
        experiment_id=experiment_id,
        ate=oec_t - oec_c,
        oec_treatment=oec_t,
        oec_control=oec_c,
        n_assigned=max(n_c, n_t),
    )
