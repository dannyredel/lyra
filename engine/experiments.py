"""Experiment assignment, ramp schedule, and treatment levers.

Responsibility (T-14): from ``config.experiments``:
- Assignment policies (EVENT_LOG §2): ``user`` (sticky on first exposure), ``cluster`` (arm from
  ``cluster_id``), ``holdout`` (carved from treatment per ``incrementality.holdout_share``).
- Ramp: resolve the active treatment ``allocation`` for a given day from ``ramp_schedule``; write
  it on each ``assignment`` (the interference-decay diagnostic groups on this).
- Levers: apply the treatment as a shift to choice-model inputs (e.g. ``pass_through_delta`` for
  reward sizing; ``ranker`` swap for ranking) so ``choice.py`` produces the right ground-truth effect.

A/A experiments hold a constant 50/50 and must NOT flag (``tests/test_aa_null.py``).

Determinism
-----------
- ``user`` assignment is a hash of ``(seed, exp_id, user_id)`` → a uniform in [0,1); the agent is
  treated iff that uniform < the current allocation. Hashing (not an RNG draw) makes assignment
  independent of agent processing order *and* sticky for free — and the ramp simply moves the
  threshold, so an agent treated at 5% stays treated at 20% (monotone ramp, realistic).
- ``cluster`` assignment hashes ``(seed, exp_id, cluster_id)`` so every agent in a cluster shares
  an arm. Holdout is carved from the treatment side by a second independent hash.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from engine.agents import Agent
from engine.config import Config

CONTROL, TREATMENT, HOLDOUT = "control", "treatment", "holdout"


def _uniform_hash(*parts: object) -> float:
    """Stable uniform in [0,1) from the parts (reproducible across processes, order-independent)."""
    h = hashlib.blake2b(digest_size=8)
    for p in parts:
        h.update(str(p).encode())
        h.update(b"\x00")
    return int.from_bytes(h.digest(), "big") / 2**64


@dataclass(slots=True)
class Experiment:
    id: str
    advertiser: str
    type: str
    randomization: str                 # "user" | "cluster"
    lever: dict                        # e.g. {"pass_through_delta": 0.15} or {"ranker": "value_sorted"}
    primary_metric: str | None
    uses_ramp: bool
    logs_propensity: bool
    is_aa: bool
    design: str = "standard"           # "standard" | "budget_split" (separate per-arm budget pools)
    # incrementality holdout (only the target experiment)
    holdout_share: float = 0.0

    @property
    def pass_through_delta(self) -> float:
        """The reward-sizing lever magnitude (0 if this experiment doesn't size rewards)."""
        return float(self.lever.get("pass_through_delta", 0.0)) if self.lever else 0.0


@dataclass(slots=True)
class ExperimentSet:
    experiments: list[Experiment]
    ramp_schedule: list[tuple[int, float]]            # sorted (start_day, share)
    seed: int
    by_advertiser: dict[str, Experiment] = field(default_factory=dict)

    def for_advertiser(self, advertiser_id: str) -> Experiment | None:
        return self.by_advertiser.get(advertiser_id)


def build_experiments(cfg: Config) -> ExperimentSet:
    exp_cfg = cfg.experiments
    ramp = sorted((int(s.start_day), float(s.share)) for s in exp_cfg.ramp_schedule)

    inc = exp_cfg.get("incrementality", {})
    inc_target = inc.get("target_experiment") if inc and inc.get("enabled") else None
    inc_holdout = float(inc.get("holdout_share", 0.0)) if inc_target else 0.0

    experiments: list[Experiment] = []
    by_adv: dict[str, Experiment] = {}
    for e in exp_cfg.list:
        is_aa = str(e.type) == "aa"
        exp = Experiment(
            id=str(e.id),
            advertiser=str(e.advertiser),
            type=str(e.type),
            randomization=str(e.randomization),
            lever=e.get("lever", {}).as_dict() if "lever" in e else {},
            primary_metric=str(e.primary_metric) if "primary_metric" in e else None,
            uses_ramp=bool(e.get("uses_ramp", False)),
            logs_propensity=bool(e.get("logs_propensity", False)),
            is_aa=is_aa,
            design=str(e.get("design", "standard")),
            holdout_share=inc_holdout if str(e.id) == inc_target else 0.0,
        )
        experiments.append(exp)
        by_adv[exp.advertiser] = exp

    return ExperimentSet(experiments=experiments, ramp_schedule=ramp, seed=cfg.seed,
                         by_advertiser=by_adv)


def allocation_for(exp: Experiment, day: int, eset: ExperimentSet) -> float:
    """Treatment share in effect on ``day``. A/A is a constant 50/50; ramped experiments step up."""
    if exp.is_aa or not exp.uses_ramp:
        return 0.5
    share = 0.0
    for start_day, s in eset.ramp_schedule:
        if day >= start_day:
            share = s
        else:
            break
    return share


def arm_for(agent: Agent, exp: Experiment, day: int, eset: ExperimentSet) -> str:
    """Pure arm assignment from the agent's fixed hash vs the day's allocation (the ramp threshold).

    Monotone by construction: allocation only rises over the ramp, so an agent crosses
    control→treatment once and stays treated (a realistic gradual exposure). The holdout is carved
    from the treatment side by a second independent hash (ghost-ads).
    """
    alloc = allocation_for(exp, day, eset)
    key = agent.cluster_id if exp.randomization == "cluster" else agent.user_id
    u = _uniform_hash(eset.seed, exp.id, key)
    if u >= alloc:
        return CONTROL
    if exp.holdout_share > 0.0:
        uh = _uniform_hash(eset.seed, exp.id, "holdout", agent.user_id)
        if uh < exp.holdout_share:
            return HOLDOUT
    return TREATMENT


def assign(agent: Agent, exp: Experiment, day: int, eset: ExperimentSet) -> tuple[str, bool]:
    """Resolve the agent's arm for ``exp`` today and update the sticky cache.

    Returns ``(arm, changed)`` where ``changed`` is True on first assignment or when the ramp flips
    the agent into a new arm — the engine emits an ``assignment`` event exactly when ``changed``.
    """
    arm = arm_for(agent, exp, day, eset)
    changed = agent.assignments.get(exp.id) != arm
    agent.assignments[exp.id] = arm
    return arm, changed


def reward_delta_for(exp: Experiment, arm: str) -> float:
    """Pass-through delta applied to this advertiser's offers for the given arm.

    - treatment → the lever delta (richer reward),
    - holdout → the reward is *suppressed* entirely (ghost ads): handled by the caller as 0 reward,
    - control → no change.
    """
    if arm == TREATMENT:
        return exp.pass_through_delta
    return 0.0
