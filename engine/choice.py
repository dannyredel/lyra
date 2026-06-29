"""Discrete-choice model — THIS IS GROUND TRUTH.

Responsibility (T-13): compute agent choice over the shown offer set via MNL / nested logit:

    u_ij = beta_reward * reward_sensitivity_i * reward_shown_j - beta_effort * effort_j
           + match_weight * category_propensity_i[cat_j] + eps_ij
    eps ~ Gumbel (MNL)  |  nested by advertiser (nested logit)

plus an **outside option** (utility 0 + Gumbel) — the agent may complete nothing this round, so
treatment effects can move the *extensive* margin (whether to convert), not just which offer.

Because we set the utility parameters (``config.choice``), we know the TRUE effect of any
treatment exactly. Treatments are defined as shifts to these utility inputs (``reward_shown`` via
``pass_through_delta`` for reward sizing; the ranker for ranking), so the engine can write a
ground-truth effect. When ``logs_propensity`` is set, emit the chosen probability as ``propensity``.

Ground truth, two levels
------------------------
- **Per-conversion** ``ground_truth_tau`` (this module, :func:`expected_margin`): the agent-level,
  single-draw expected-margin lift of the active treatment — a local individual effect written on
  each conversion row. Cheap, exact given the model, useful for HTE later.
- **Experiment-level global ATE** (M2 ``validation``/shadow runs): the honest estimand the recovery
  tests target — the difference in the OEC between an all-treated and an all-control world, which
  *includes* the budget/effort interference. Computed by replaying the engine counterfactually.

Margin convention (the platform's cut): ``value = payout - reward_shown = payout * (1 - pass_through)``.
A richer reward (treatment) lowers per-conversion margin but raises conversion probability — the
real reward-sizing trade-off the experiment measures.
"""

from __future__ import annotations

import numpy as np

from engine.agents import Agent
from engine.config import Config
from engine.offers import Offer


class ChoiceModel:
    """Holds the (ground-truth) utility parameters and turns a choice set into choices/probabilities.

    A choice set is described by parallel arrays the caller builds (reward already includes any
    treatment lever): ``rewards_shown``, ``efforts``, ``category_indices``. This keeps the engine's
    per-tick hot loop vectorised and the lever logic in ``experiments.py``.
    """

    def __init__(self, cfg: Config):
        c = cfg.choice
        self.model = str(c.model)
        self.beta_reward = float(c.beta_reward)
        self.beta_effort = float(c.beta_effort)
        self.match_weight = float(c.match_weight)
        self.nest_lambda = float(c.get("nest_lambda", 1.0))
        if self.model not in ("mnl", "nested_logit"):
            raise ValueError(f"unknown choice.model {self.model!r}")
        if self.model == "nested_logit":
            # Phase-3 vertical; MVP default is mnl (config.choice.model).
            raise NotImplementedError(
                "nested_logit not implemented yet — set choice.model: mnl (MVP default)."
            )

    # --- deterministic utility (the v in u = v + eps) ---
    def utilities(
        self,
        agent: Agent,
        rewards_shown: np.ndarray,
        efforts: np.ndarray,
        category_indices: np.ndarray,
    ) -> np.ndarray:
        """Deterministic utility ``v_j`` for each offer in the shown set (no noise)."""
        match = agent.category_propensity[category_indices]
        return (
            self.beta_reward * agent.reward_sensitivity * rewards_shown
            - self.beta_effort * efforts
            + self.match_weight * match
            + agent.cluster_effect          # shared per-cluster engagement intercept (B-06 → ICC>0)
        )

    # --- choice probabilities incl. the outside option (index -1 conceptually) ---
    def probabilities(self, v: np.ndarray) -> np.ndarray:
        """Softmax over [offers..., outside(=0)]; returns probs of length ``len(v)+1``.

        The last entry is the outside (no-completion) probability.
        """
        ext = np.concatenate([v, [0.0]])
        ext = ext - ext.max()  # numerical stability
        e = np.exp(ext)
        return e / e.sum()

    def sample_choice(
        self,
        agent: Agent,
        rewards_shown: np.ndarray,
        efforts: np.ndarray,
        category_indices: np.ndarray,
        rng: np.random.Generator,
    ) -> tuple[int, float]:
        """Gumbel-max sample over the shown set + outside option.

        Returns ``(idx, propensity)`` where ``idx`` is the chosen offer index into the shown set,
        or ``-1`` for the outside option, and ``propensity`` is the chosen alternative's MNL
        probability (logged for OPE).
        """
        v = self.utilities(agent, rewards_shown, efforts, category_indices)
        probs = self.probabilities(v)
        ext = np.concatenate([v, [0.0]])
        # Gumbel-max trick == sampling from the MNL.
        g = rng.gumbel(size=ext.shape[0])
        k = int(np.argmax(ext + g))
        idx = -1 if k == len(v) else k
        return idx, float(probs[k])

    def expected_margin(
        self,
        agent: Agent,
        rewards_shown: np.ndarray,
        efforts: np.ndarray,
        category_indices: np.ndarray,
        margins: np.ndarray,
    ) -> float:
        """Expected margin from one choice draw: ``sum_j P(pick j) * margin_j`` (outside → 0)."""
        v = self.utilities(agent, rewards_shown, efforts, category_indices)
        probs = self.probabilities(v)[:-1]  # drop outside (margin 0)
        return float(np.dot(probs, margins))
