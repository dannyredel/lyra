"""The daily tick loop — orchestrates one simulated day.

Responsibility (T-16): for each tick = one simulated day, drive the world and emit events in the
causally-consistent order required by EVENT_LOG §2:

    arrival → assignment → impression → conversion → budget_decrement → churn

Per tick: create arrivals, route active agents into offer walls, run ``choice.py`` over the shown
set, credit conversions + decrement advertiser budgets, draw churn. Stops at ``meta.horizon_days``.
At end of run, self-check aggregate outputs against ``config.calibration`` anchors.

Does NOT compute experiment results — only emits the log.

Simplifications (stated, per CLAUDE.md "calibrate, don't fantasize"):
- An ``impression`` is logged for the offer an agent *engages with* each round (the engaged
  impression), not for every offer rendered — keeps the log laptop-scale while preserving the
  ghost-ads counterfactual (holdout agents get an impression but no conversion/reward).
- The offer wall each round is every available+affordable offer; choice includes an outside option,
  so treatment moves the extensive margin (convert-or-not), not just which offer.
- ``ground_truth_tau`` on a conversion is the agent-level, single-draw expected-margin lift of the
  active treatment on that experiment (a local individual effect). The headline estimand — the
  global ATE that recovery tests target — comes from counterfactual shadow runs (``shadow_runs``).
"""

from __future__ import annotations

import numpy as np

from engine import agents as agents_mod
from engine import experiments as exp_mod
from engine.choice import ChoiceModel
from engine.config import Config, load_config
from engine.emit import EventEmitter
from engine.experiments import CONTROL, HOLDOUT, TREATMENT

MAX_ROUNDS_PER_DAY = 8       # cap completions/agent/day (prevents pathological loops)
_RECENT_REWARD_DECAY = 0.5


class _OfferArrays:
    """Vectorised view of the offer wall for the hot loop (parallel numpy arrays by offer index)."""

    def __init__(self, cfg: Config, offers):
        self.offers = offers
        self.n = len(offers)
        self.offer_id = [o.offer_id for o in offers]
        self.advertiser = [o.advertiser_id for o in offers]
        self.payout = np.array([o.payout for o in offers])
        self.effort = np.array([o.difficulty_effort for o in offers])
        self.cat_idx = np.array([o.category_index for o in offers])
        self.pass_through = np.array([o.pass_through for o in offers])
        self.cap = np.array([o.budget_cap for o in offers])
        self.base_reward = self.payout * self.pass_through
        self.base_margin = self.payout - self.base_reward
        self.spent = np.zeros(self.n)

    def caps_dict(self) -> dict[str, float]:
        return {oid: float(c) for oid, c in zip(self.offer_id, self.cap)}


class _SplitBudgets:
    """Per-arm budget pools for ``budget_split`` experiments — the correct fix for budget
    cannibalization. Each arm draws from its own pool sized to its user share, so per-user budget
    (hence scarcity) is preserved and the cross-arm contamination that biases the naive estimator
    disappears. Recovers the global ATE (LinkedIn budget-split).
    """

    def __init__(self, n_offers: int, split_exps: list, exp_offer_idx: dict):
        self.exps = split_exps
        self.idx = {e.id: exp_offer_idx[e.id] for e in split_exps if e.id in exp_offer_idx}
        self.is_split = np.zeros(n_offers, dtype=bool)
        for ix in self.idx.values():
            self.is_split[ix] = True
        self.spent_t = np.zeros(n_offers)
        self.spent_c = np.zeros(n_offers)
        self.cap_t = np.zeros(n_offers)
        self.cap_c = np.zeros(n_offers)

    @property
    def active(self) -> bool:
        return bool(self.exps)

    def begin_day(self, day: int, eset, oa: "_OfferArrays", refill_daily: bool) -> None:
        for e in self.exps:
            ix = self.idx.get(e.id)
            if ix is None:
                continue
            alloc = exp_mod.allocation_for(e, day, eset)
            self.cap_t[ix] = oa.cap[ix] * alloc
            self.cap_c[ix] = oa.cap[ix] * (1.0 - alloc)
            if refill_daily:
                self.spent_t[ix] = 0.0
                self.spent_c[ix] = 0.0


def run(
    cfg: Config | str,
    output_dir: str | None = None,
    *,
    force_arm: dict[str, str] | None = None,
    srm_tolerance: float = 0.02,
    write: bool = True,
    compute_tau: bool = True,
    verbose: bool = False,
) -> dict:
    """Run the full simulation, emit the event log, and return a summary.

    ``force_arm`` maps ``experiment_id -> arm`` to override assignment for *every* agent — used by
    the M2 shadow runs to materialise the all-treated / all-control counterfactual worlds.
    ``write=False`` skips parquet output (invariants + metrics only) for fast shadow runs.
    ``compute_tau=False`` skips the per-conversion ground-truth-tau computation (the hot path) —
    safe whenever the log's ``ground_truth_tau`` column won't be read (shadow/oracle runs, and
    analysis runs whose truth comes from shadow ATE rather than per-conversion tau).
    """
    if isinstance(cfg, str):
        cfg = load_config(cfg)
    force_arm = force_arm or {}

    out_dir = output_dir or str(cfg.output.event_log_dir)
    horizon = int(cfg.meta.horizon_days)
    refill = str(cfg.offers.refill)
    protection = float(cfg.agents.churn_reward_protection)

    # --- build the world (seeded) ---
    offers = _build_offers(cfg)
    oa = _OfferArrays(cfg, offers)
    eset = exp_mod.build_experiments(cfg)
    choice = ChoiceModel(cfg)
    offer_exp = [eset.for_advertiser(adv) for adv in oa.advertiser]          # exp or None per offer
    exp_offer_idx: dict[str, np.ndarray] = {}
    for i, e in enumerate(offer_exp):
        if e is not None:
            exp_offer_idx.setdefault(e.id, []).append(i)
    exp_offer_idx = {k: np.array(v) for k, v in exp_offer_idx.items()}

    split_exps = [e for e in eset.experiments if e.design == "budget_split"]
    split = _SplitBudgets(oa.n, split_exps, exp_offer_idx)

    rng_agents = cfg.rng("agents")
    rng_choice = cfg.rng("choice")
    rng_churn = cfg.rng("churn")

    population = agents_mod.build_population(cfg, rng_agents)
    next_index = len(population)

    emitter = EventEmitter(out_dir, mode=cfg.mode, budget_caps=oa.caps_dict(),
                           srm_tolerance=srm_tolerance, write=write,
                           randomization={e.id: e.randomization for e in eset.experiments})

    metrics = _MetricsAccumulator()

    for day in range(horizon):
        metrics._cur_day = day
        if refill == "daily":
            oa.spent[:] = 0.0
            emitter.reset_budgets()
        if split.active:
            split.begin_day(day, eset, oa, refill_daily=(refill == "daily"))

        # 1) arrivals
        if day > 0:
            newcomers = agents_mod.arrivals(cfg, rng_agents, day, next_index)
            next_index += len(newcomers)
            for a in newcomers:
                emitter.emit("arrival", day=day, user_id=a.user_id, cluster_id=a.cluster_id)
            population.extend(newcomers)
        else:
            for a in population:
                emitter.emit("arrival", day=day, user_id=a.user_id, cluster_id=a.cluster_id)

        # 2) active agents act (shuffled for fair budget ordering)
        active = [a for a in population if a.alive]
        order = rng_choice.permutation(len(active))
        for k in order:
            _agent_day(active[k], day, oa, choice, eset, exp_offer_idx, offer_exp,
                       emitter, rng_choice, rng_churn, protection, force_arm, metrics, split,
                       compute_tau)

        emitter.flush_day(day)
        metrics.note_day(day, len(active))
        if verbose:
            print(f"  day {day:02d}: active={len(active):>6}  conv={metrics.conversions:>7}  "
                  f"margin={metrics.total_margin:,.0f}")

    summary = emitter.finalize()
    summary["metrics"] = metrics.report(cfg)
    summary["calibration"] = _calibration_check(cfg, metrics)
    return summary


def _agent_day(agent, day, oa, choice, eset, exp_offer_idx, offer_exp,
               emitter, rng_choice, rng_churn, protection, force_arm, metrics, split,
               compute_tau=True):
    agent.recent_reward *= _RECENT_REWARD_DECAY
    agent.reset_day()

    # --- assignment (entering the wall): emit on first assignment or ramp arm-flip ---
    for exp in eset.experiments:
        if exp.id in force_arm:
            arm = force_arm[exp.id]
            changed = agent.assignments.get(exp.id) != arm
            agent.assignments[exp.id] = arm
            alloc = 1.0 if arm == TREATMENT else 0.0
        else:
            arm, changed = exp_mod.assign(agent, exp, day, eset)
            alloc = exp_mod.allocation_for(exp, day, eset)
        if changed:
            emitter.emit("assignment", day=day, user_id=agent.user_id, cluster_id=agent.cluster_id,
                         advertiser_id=exp.advertiser, experiment_id=exp.id, variant=arm,
                         allocation=alloc)

    consumed: set[int] = set()
    reward_today = 0.0

    for _ in range(MAX_ROUNDS_PER_DAY):
        # availability: budget for one more completion, affordable effort, not already used today
        avail = (oa.spent + oa.payout <= oa.cap) & (oa.effort <= agent.effort_remaining)
        if split.active:
            # override split offers with arm-specific pool availability
            for e in split.exps:
                ix = split.idx.get(e.id)
                if ix is None:
                    continue
                arm = agent.assignments.get(e.id)
                pool_spent = split.spent_c[ix] if arm == CONTROL else split.spent_t[ix]
                pool_cap = split.cap_c[ix] if arm == CONTROL else split.cap_t[ix]
                avail[ix] = (pool_spent + oa.payout[ix] <= pool_cap) & (oa.effort[ix] <= agent.effort_remaining)
        if consumed:
            avail[list(consumed)] = False
        idxs = np.flatnonzero(avail)
        if idxs.size == 0:
            break

        reward = _reward_vector(agent, oa, exp_offer_idx, offer_exp)
        margins = oa.payout - reward

        chosen_local, propensity = choice.sample_choice(
            agent, reward[idxs], oa.effort[idxs], oa.cat_idx[idxs], rng_choice
        )
        if chosen_local == -1:        # outside option → done for the day
            break
        gi = int(idxs[chosen_local])
        exp = offer_exp[gi]
        arm = agent.assignments.get(exp.id) if exp is not None else None
        logs_prop = exp.logs_propensity if exp is not None else False

        # --- engaged impression ---
        emitter.emit("impression", day=day, user_id=agent.user_id, cluster_id=agent.cluster_id,
                     advertiser_id=oa.advertiser[gi], offer_id=oa.offer_id[gi],
                     experiment_id=(exp.id if exp else None), variant=arm,
                     effort_spent=float(oa.effort[gi]), reward_shown=float(reward[gi]),
                     propensity=(propensity if logs_prop else None))

        # --- ghost-ads holdout: reward withheld (reward_shown already 0 in the reward vector), but
        #     the agent may still complete ORGANICALLY. The conversion carries reward_shown=0, so
        #     incrementality = treatment vs holdout measures the reward's causal lift (EVENT_LOG §5,
        #     D-14). Holdout's low pick-probability falls out of the 0 reward in the choice model.

        # --- conversion + budget decrement ---
        tau = (_ground_truth_tau(agent, oa, exp, exp_offer_idx, choice, avail)
               if (exp and compute_tau) else None)
        value = float(margins[gi])
        emitter.emit("conversion", day=day, user_id=agent.user_id, cluster_id=agent.cluster_id,
                     advertiser_id=oa.advertiser[gi], offer_id=oa.offer_id[gi],
                     experiment_id=(exp.id if exp else None), variant=arm,
                     effort_spent=float(oa.effort[gi]), reward_shown=float(reward[gi]),
                     value=value, propensity=(propensity if logs_prop else None),
                     ground_truth_tau=tau)
        emitter.emit("budget_decrement", day=day, advertiser_id=oa.advertiser[gi],
                     offer_id=oa.offer_id[gi], value=float(oa.payout[gi]))

        if split.active and split.is_split[gi]:
            if arm == CONTROL:
                split.spent_c[gi] += float(oa.payout[gi])
            else:
                split.spent_t[gi] += float(oa.payout[gi])
        else:
            oa.spent[gi] += float(oa.payout[gi])
        agent.effort_remaining -= float(oa.effort[gi])
        reward_today += float(reward[gi])
        agent.lifetime_completions += 1
        agent.lifetime_effort += float(oa.effort[gi])
        consumed.add(gi)
        metrics.note_conversion(value, exp.id if exp else None, arm)

    agent.recent_reward += reward_today

    # --- churn ---
    p = agents_mod.churn_probability(agent, protection)
    if rng_churn.random() < p:
        agent.alive = False
        emitter.emit("churn", day=day, user_id=agent.user_id, cluster_id=agent.cluster_id)


def _reward_vector(agent, oa, exp_offer_idx, offer_exp) -> np.ndarray:
    """Reward shown to this agent per offer, applying each experiment's lever for the agent's arm."""
    reward = oa.base_reward.copy()
    for exp_id, idxs in exp_offer_idx.items():
        arm = agent.assignments.get(exp_id)
        if arm == TREATMENT:
            exp = offer_exp[idxs[0]]
            reward[idxs] = oa.payout[idxs] * (oa.pass_through[idxs] + exp.pass_through_delta)
        elif arm == HOLDOUT:
            reward[idxs] = 0.0
    return reward


def _ground_truth_tau(agent, oa, exp, exp_offer_idx, choice, avail) -> float:
    """Agent-level local effect: E[margin | treated] − E[margin | control] over the available wall."""
    idxs = np.flatnonzero(avail)
    if idxs.size == 0:
        return 0.0
    eidx = exp_offer_idx.get(exp.id)
    # control rewards/margins
    reward_c = oa.base_reward.copy()
    if eidx is not None:
        reward_c[eidx] = oa.base_reward[eidx]
    reward_t = reward_c.copy()
    if eidx is not None:
        reward_t[eidx] = oa.payout[eidx] * (oa.pass_through[eidx] + exp.pass_through_delta)
    margin_c = oa.payout - reward_c
    margin_t = oa.payout - reward_t
    em_c = choice.expected_margin(agent, reward_c[idxs], oa.effort[idxs], oa.cat_idx[idxs],
                                  margin_c[idxs])
    em_t = choice.expected_margin(agent, reward_t[idxs], oa.effort[idxs], oa.cat_idx[idxs],
                                  margin_t[idxs])
    return float(em_t - em_c)


def _build_offers(cfg: Config):
    from engine import offers as offers_mod
    return offers_mod.build_offers(cfg, cfg.rng("offers"))


# --------------------------------------------------------------------------- #
# metrics + calibration
# --------------------------------------------------------------------------- #
class _MetricsAccumulator:
    def __init__(self):
        self.conversions = 0
        self.total_margin = 0.0
        self.active_user_days = 0
        self.by_exp_arm: dict[tuple, dict] = {}
        self.conv_per_day: dict[int, int] = {}
        self.active_per_day: dict[int, int] = {}

    def note_conversion(self, value, exp_id, arm):
        self.conversions += 1
        self.total_margin += value
        self.conv_per_day[self._cur_day] = self.conv_per_day.get(self._cur_day, 0) + 1
        if exp_id is not None:
            d = self.by_exp_arm.setdefault((exp_id, arm), {"n": 0, "margin": 0.0})
            d["n"] += 1
            d["margin"] += value

    _cur_day = 0

    def note_day(self, day, n_active):
        self.active_user_days += n_active
        self.active_per_day[day] = n_active
        self._cur_day = day

    def report(self, cfg) -> dict:
        return {
            "conversions": self.conversions,
            "total_margin": self.total_margin,
            "active_user_days": self.active_user_days,
            "margin_per_active_user_day": (
                self.total_margin / self.active_user_days if self.active_user_days else 0.0
            ),
            "by_exp_arm": {f"{e}/{a}": v for (e, a), v in sorted(self.by_exp_arm.items())},
        }


def _calibration_check(cfg, metrics) -> dict:
    """Self-check market health and warn on collapse (the failure mode at mis-scaled budgets).

    Catches: no conversions; non-positive margin; **market collapse** (last-day conversions far
    below peak, i.e. budgets exhausted and never refilled); **population collapse** (active users
    crater beyond expected churn). These are the symptoms that the budget/scale calibration is off.
    """
    rep = metrics.report(cfg)
    warnings: list[str] = []
    cpd = metrics.conv_per_day
    apd = metrics.active_per_day
    if rep["conversions"] == 0:
        warnings.append("no conversions emitted — choice/offer params likely miscalibrated")
    if rep["margin_per_active_user_day"] <= 0:
        warnings.append("non-positive margin per active user — check pass_through / payout")
    if cpd:
        peak = max(cpd.values())
        last = cpd.get(max(cpd), 0)
        if peak and last < 0.2 * peak:
            warnings.append(
                f"market collapse: last-day conversions {last} << peak {peak} "
                f"(budgets exhausted? raise offers.budget_cap or use refill: daily)"
            )
    if apd:
        peak_a = max(apd.values())
        last_a = apd.get(max(apd), 0)
        if peak_a and last_a < 0.1 * peak_a:
            warnings.append(f"population collapse: active {last_a} << peak {peak_a}")
    return {
        "ok": not warnings,
        "warnings": warnings,
        "conv_first_day": cpd.get(min(cpd), 0) if cpd else 0,
        "conv_last_day": cpd.get(max(cpd), 0) if cpd else 0,
        "active_first_day": apd.get(min(apd), 0) if apd else 0,
        "active_last_day": apd.get(max(apd), 0) if apd else 0,
        **rep,
    }
