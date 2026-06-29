"""Agent (user) population — the simulated side of the market.

Responsibility (T-11): sample N agents at creation from the seeded distributions in
``config.agents``:
- ``effort_budget_per_day`` (the shared resource that drives cannibalization),
- ``reward_sensitivity`` (elasticity of choice w.r.t. ``reward_shown``),
- ``category_propensity`` (Dirichlet over ``market.categories``),
- ``churn_hazard`` (lowered by recent rewards via ``churn_reward_protection``).

Each agent also carries a ``cluster_id`` (geo/segment) used by cluster-randomized designs.
New agents arrive each tick (``market.daily_arrivals``).

The agent carries both **fixed traits** (sampled once, the ground-truth "who they are") and
**mutable per-run state** (alive flag, today's remaining effort, recent-reward memory for churn
protection, sticky experiment-arm assignments, and pre-period tallies CUPED will use). The engine
mutates state; nothing here computes choices or effects.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from engine.config import Config


@dataclass(slots=True)
class Agent:
    # --- identity ---
    user_id: str
    cluster_id: str
    arrival_day: int
    # --- fixed traits (ground-truth "who they are") ---
    effort_budget_per_day: float
    reward_sensitivity: float            # multiplies the reward term in utility (elasticity)
    category_propensity: np.ndarray      # length == len(market.categories), sums to 1
    base_churn_hazard: float
    cluster_effect: float = 0.0          # shared per-cluster utility intercept (B-06; induces ICC)
    # --- mutable per-run state ---
    alive: bool = True
    effort_remaining: float = 0.0        # reset each tick to effort_budget_per_day
    recent_reward: float = 0.0           # exponentially-decayed reward memory (churn protection)
    assignments: dict[str, str] = field(default_factory=dict)  # exp_id -> "control"/"treatment"/"holdout"
    # --- pre-period tallies (CUPED covariates, M4) ---
    lifetime_completions: int = 0
    lifetime_effort: float = 0.0

    def reset_day(self) -> None:
        """Refresh per-tick state at the start of a day."""
        self.effort_remaining = self.effort_budget_per_day


# --------------------------------------------------------------------------- #
# sampling
# --------------------------------------------------------------------------- #
def _sample_trait(spec, n: int, rng: np.random.Generator) -> np.ndarray:
    """Draw ``n`` values from a distribution spec (``{dist: ..., <params>}``)."""
    dist = spec["dist"]
    if dist == "lognormal":
        return rng.lognormal(mean=spec["mu"], sigma=spec["sigma"], size=n)
    if dist == "gamma":
        return rng.gamma(shape=spec["shape"], scale=spec["scale"], size=n)
    if dist == "beta":
        return rng.beta(a=spec["a"], b=spec["b"], size=n)
    if dist == "normal":
        return rng.normal(loc=spec["mu"], scale=spec["sigma"], size=n)
    raise ValueError(f"unsupported trait distribution: {dist!r}")


def _sample_agents(
    cfg: Config,
    rng: np.random.Generator,
    n: int,
    start_index: int,
    arrival_day: int,
) -> list[Agent]:
    a = cfg.agents
    n_clusters = int(cfg.market.n_clusters)
    n_cats = len(cfg.market.categories)

    effort = _sample_trait(a.effort_budget_per_day.as_dict(), n, rng)
    sens = _sample_trait(a.reward_sensitivity.as_dict(), n, rng)
    hazard = _sample_trait(a.churn_hazard.as_dict(), n, rng)

    cp_spec = a.category_propensity.as_dict()
    if cp_spec["dist"] != "dirichlet":
        raise ValueError("agents.category_propensity must be a dirichlet")
    propensity = rng.dirichlet(alpha=np.asarray(cp_spec["alpha"], dtype=float), size=n)

    clusters = rng.integers(0, n_clusters, size=n)
    cluster_eff = cfg.cluster_effects()   # per-cluster shared intercept (B-06)

    agents: list[Agent] = []
    for i in range(n):
        idx = start_index + i
        c = int(clusters[i])
        agents.append(
            Agent(
                user_id=f"u_{idx:07d}",
                cluster_id=f"c_{c:04d}",
                arrival_day=arrival_day,
                effort_budget_per_day=float(effort[i]),
                reward_sensitivity=float(sens[i]),
                category_propensity=propensity[i].astype(float),
                base_churn_hazard=float(np.clip(hazard[i], 0.0, 1.0)),
                cluster_effect=float(cluster_eff[c]),
            )
        )
    return agents


def build_population(cfg: Config, rng: np.random.Generator) -> list[Agent]:
    """The initial cohort present on day 0 (``market.n_users_initial``)."""
    n = int(cfg.market.n_users_initial)
    return _sample_agents(cfg, rng, n, start_index=0, arrival_day=0)


def arrivals(
    cfg: Config, rng: np.random.Generator, day: int, next_index: int
) -> list[Agent]:
    """New agents arriving on ``day`` (``market.daily_arrivals``); ids continue from ``next_index``."""
    n = int(cfg.market.daily_arrivals)
    return _sample_agents(cfg, rng, n, start_index=next_index, arrival_day=day)


def update_churn_memory(agent: Agent, reward_today: float, decay: float = 0.5) -> None:
    """Exponentially decay recent-reward memory and add today's reward (drives churn protection)."""
    agent.recent_reward = decay * agent.recent_reward + reward_today


def churn_probability(agent: Agent, protection: float) -> float:
    """Daily churn hazard, lowered by recent rewards: ``hazard * (1 - protection * tanh(recent))``."""
    shield = 1.0 - protection * np.tanh(agent.recent_reward)
    return float(np.clip(agent.base_churn_hazard * shield, 0.0, 1.0))
