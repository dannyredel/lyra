"""Shared test fixtures.

Provides small, fast, seeded engine runs and the oracle ground truth (the only place
``ground_truth_tau`` / counterfactual truth may be read — EVENT_LOG §4). Keep runs small so CI
stays fast; these tests *are* the causal credibility, so correctness beats speed but we still cap
scale deliberately.

Two regimes (see pm/DECISIONS.md D-11/D-12):
- **isolated** — a single-advertiser world with non-binding effort and a binding daily budget, so
  *budget cannibalization is the only interference channel*. Here the budget-split design recovers
  the global ATE exactly (coverage), while the naive estimator is biased and the bias grows with
  allocation. The clean unit-test regime for the estimators.
- **aa** — a small multi-advertiser world carrying the A/A nulls (user- and cluster-randomized) for
  the false-positive / SRM guards.
"""

from __future__ import annotations

import copy
from types import SimpleNamespace

import pytest

from engine.config import Config, load_config
from engine.market import run
from engine.oracle import global_ate

EXP = "exp_reward_sizing"


def _base() -> Config:
    return load_config("config.yaml")


def iso_cfg(seed: int = 3, share: float = 0.5, design: str = "standard",
            users: int = 9000, days: int = 14) -> Config:
    """Single-advertiser, budget-only interference world (the recovery-test regime).

    One advertiser ⇒ no cross-advertiser effort substitution, so even with the default (binding)
    effort the *only* cross-arm interference is budget cannibalization — which budget-split corrects
    exactly. Binding effort also keeps conversion volume (hence runtime) modest.
    """
    base = _base()
    cfg = base.with_overrides(
        meta={"seed": seed, "horizon_days": days, "mode": "real",
              "project": "vega", "run_name": "test_iso"},
        market={"n_users_initial": users, "daily_arrivals": max(1, users // 80),
                "n_offers": 8, "n_advertisers": 1, "n_clusters": 60,
                "categories": list(base.market.categories)},
        # isolate the BUDGET channel: no cluster random effect here (that's the cluster test's job)
        agents={**base.agents.as_dict(), "cluster_effect_sigma": 0.0},
        offers={**base.offers.as_dict(), "refill": "daily",
                "budget_cap": {"dist": "lognormal", "mu": 3.4, "sigma": 0.5}},
    )
    d = copy.deepcopy(cfg.as_dict())
    d["experiments"]["list"] = [e for e in d["experiments"]["list"] if e["id"] == EXP]
    d["experiments"]["incrementality"] = {"enabled": False, "target_experiment": EXP,
                                           "holdout_share": 0.0}
    d["experiments"]["ramp_schedule"] = [{"start_day": 0, "share": share}]
    for e in d["experiments"]["list"]:
        if e["id"] == EXP:
            e["design"] = design
    return Config(d, cfg.path)


def aa_cfg(seed: int = 5, users: int = 4000, days: int = 10) -> Config:
    """Small multi-advertiser world that keeps the A/A nulls (adv_C user, adv_D cluster)."""
    base = _base()
    return base.with_overrides(
        meta={"seed": seed, "horizon_days": days, "mode": "real",
              "project": "vega", "run_name": "test_aa"},
        market={"n_users_initial": users, "daily_arrivals": max(1, users // 80),
                "n_offers": 24, "n_advertisers": 6, "n_clusters": 60,
                "categories": list(base.market.categories)},
        offers={**base.offers.as_dict(), "refill": "daily",
                "budget_cap": {"dist": "lognormal", "mu": 5.5, "sigma": 0.5}},
    )


@pytest.fixture(scope="session")
def iso(tmp_path_factory) -> SimpleNamespace:
    """Ground-truth ATE + standard runs at low/high allocation + a budget-split run at high alloc."""
    gt = global_ate(iso_cfg(share=0.5), EXP)
    runs: dict[str, str] = {}
    for key, (share, design) in {
        "std_lo": (0.10, "standard"),
        "std_hi": (0.50, "standard"),
        "bsplit_hi": (0.50, "budget_split"),
    }.items():
        d = tmp_path_factory.mktemp(key)
        run(iso_cfg(share=share, design=design), output_dir=str(d))
        runs[key] = str(d)
    return SimpleNamespace(gt=gt, runs=runs, exp=EXP)


@pytest.fixture(scope="session")
def aa(tmp_path_factory) -> SimpleNamespace:
    d = tmp_path_factory.mktemp("aa")
    summary = run(aa_cfg(), output_dir=str(d))
    return SimpleNamespace(events_dir=str(d), summary=summary)


@pytest.fixture(scope="session")
def incr(tmp_path_factory) -> SimpleNamespace:
    """Single-advertiser world with a ghost-ads HOLDOUT carved from treatment (reward withheld).
    Incrementality = treatment vs holdout on conversions."""
    base = iso_cfg(seed=6, share=0.5, users=8000, days=14)
    d = copy.deepcopy(base.as_dict())
    d["experiments"]["incrementality"] = {"enabled": True, "target_experiment": EXP,
                                          "holdout_share": 0.30}
    dd = tmp_path_factory.mktemp("incr")
    run(Config(d, base.path), output_dir=str(dd), compute_tau=False)
    return SimpleNamespace(events_dir=str(dd), exp=EXP)


@pytest.fixture(scope="session")
def cuped(tmp_path_factory) -> SimpleNamespace:
    """Single-advertiser world with a WARMUP: A/A for the first `split` days (pre-period covariate),
    then a 50/50 split. CUPED uses warmup margin as the pre-treatment covariate."""
    split, days = 4, 16
    cfg = iso_cfg(seed=4, share=0.5, users=6000, days=days)
    d = copy.deepcopy(cfg.as_dict())
    d["experiments"]["ramp_schedule"] = [{"start_day": 0, "share": 0.0},
                                         {"start_day": split, "share": 0.5}]
    dd = tmp_path_factory.mktemp("cuped")
    run(Config(d, cfg.path), output_dir=str(dd), compute_tau=False)
    return SimpleNamespace(events_dir=str(dd), split=split, exp=EXP)
