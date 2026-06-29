"""Thin shared helpers for the lab notebooks — *style + config builders only*.

Deliberately minimal: the notebooks are meant to make the system legible, so all the engine /
inference calls stay visible in the notebook cells. This module only carries (1) a consistent
matplotlib style + the Notion colour palette (matching the study-guide HTML), (2) small config
builders for the demo scales, and (3) one generic forest-plot helper. Nothing here computes an
estimate or hides a mechanism.

The config builders mirror ``tests/conftest.py`` on purpose — tests stay self-contained for CI, and
the notebooks re-state the scales so you can see exactly what world each figure was run in.
"""

from __future__ import annotations

import copy
import os
import pathlib
import sys

# --- make the repo importable + cwd = repo root (so 'config.yaml'/'events/' resolve) ------------
def use_repo_root() -> pathlib.Path:
    root = pathlib.Path.cwd()
    while not (root / "config.yaml").exists() and root != root.parent:
        root = root.parent
    os.chdir(root)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return root


# --- Notion colour palette (same hexes as paper-library/study) ---------------------------------
BLUE, GREEN, PINK = "#6ea8fe", "#3fb68b", "#e9548a"
PURPLE, ORANGE, GRAY = "#9d7bff", "#e08c4f", "#8a93a6"
INK, MUTED = "#2b2f38", "#8a93a6"


def set_style() -> None:
    import matplotlib as mpl

    mpl.rcParams.update({
        "figure.figsize": (8, 4.5), "figure.dpi": 110,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#e7e9ee", "grid.linewidth": 0.8,
        "axes.edgecolor": "#c7ccd6", "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.titleweight": "600",
        "font.size": 11, "axes.titlesize": 13, "legend.frameon": False,
    })


# --- config builders ---------------------------------------------------------------------------
def world_cfg(seed: int = 7, users: int = 3000, days: int = 10, budget_mu: float = 6.0):
    """Small *multi-advertiser* realistic market (NB01 world tour, NB03 A/A nulls)."""
    from engine.config import load_config

    base = load_config("config.yaml")
    return base.with_overrides(
        meta={"seed": seed, "horizon_days": days, "mode": "real",
              "project": "vega", "run_name": "nb_world"},
        market={"n_users_initial": users, "daily_arrivals": max(1, users // 40),
                "n_offers": 30, "n_advertisers": 8, "n_clusters": 60,
                "categories": list(base.market.categories)},
        offers={**base.offers.as_dict(), "refill": "daily",
                "budget_cap": {"dist": "lognormal", "mu": budget_mu, "sigma": 0.7}},
    )


def market_cfg(seed: int = 11, users: int = 9000, days: int = 22, budget_mu: float = 6.2):
    """*Multi-advertiser* realistic market with strong, clean budget cannibalization (NB02 primary).

    This is the regime where the naive estimator's bias grows visibly and monotonically with
    allocation. Effort is the base (binding) value; the cannibalization comes from per-offer daily
    budgets binding on the experiment advertiser. Budget-split removes *most* of the bias here (a
    second channel — cross-advertiser effort substitution — leaves a residual; the single-advertiser
    ``iso_cfg`` is where budget-split recovers exactly).
    """
    from engine.config import load_config

    base = load_config("config.yaml")
    return base.with_overrides(
        meta={"seed": seed, "horizon_days": days, "mode": "real",
              "project": "vega", "run_name": "nb_market"},
        market={"n_users_initial": users, "daily_arrivals": max(1, users // 75),
                "n_offers": 50, "n_advertisers": 12, "n_clusters": 80,
                "categories": list(base.market.categories)},
        offers={**base.offers.as_dict(), "refill": "daily",
                "budget_cap": {"dist": "lognormal", "mu": budget_mu, "sigma": 0.7}},
    )


def iso_cfg(seed: int = 3, share: float = 0.5, design: str = "standard",
            users: int = 8000, days: int = 10, budget_mu: float = 3.2,
            effort_mu: float | None = 2.5):
    """*Single-advertiser* budget-only interference world (NB02 clean money shot).

    One advertiser ⇒ no cross-advertiser effort substitution, so budget cannibalization is the only
    cross-arm channel and the budget-split design recovers the global ATE exactly.

    Defaults pick a *strong, clean, fast* regime: non-binding effort (``effort_mu=2.5`` ⇒ high demand
    ⇒ the budget binds hard ⇒ strong cannibalization) with a small daily budget (``budget_mu=3.2`` ⇒
    few total conversions ⇒ fast). Set ``effort_mu=None`` to use the base (binding) effort, which
    mirrors the smaller-effect regime in ``tests/conftest.py::iso_cfg``.
    """
    from engine.config import Config, load_config

    base = load_config("config.yaml")
    agents = base.agents.as_dict()
    if effort_mu is not None:
        agents = {**agents,
                  "effort_budget_per_day": {"dist": "lognormal", "mu": effort_mu, "sigma": 0.3}}
    cfg = base.with_overrides(
        meta={"seed": seed, "horizon_days": days, "mode": "real",
              "project": "vega", "run_name": "nb_iso"},
        market={"n_users_initial": users, "daily_arrivals": max(1, users // 80),
                "n_offers": 8, "n_advertisers": 1, "n_clusters": 60,
                "categories": list(base.market.categories)},
        agents=agents,
        offers={**base.offers.as_dict(), "refill": "daily",
                "budget_cap": {"dist": "lognormal", "mu": budget_mu, "sigma": 0.5}},
    )
    d = copy.deepcopy(cfg.as_dict())
    d["experiments"]["list"] = [e for e in d["experiments"]["list"]
                                if e["id"] == "exp_reward_sizing"]
    d["experiments"]["incrementality"] = {"enabled": False,
                                           "target_experiment": "exp_reward_sizing",
                                           "holdout_share": 0.0}
    d["experiments"]["ramp_schedule"] = [{"start_day": 0, "share": share}]
    for e in d["experiments"]["list"]:
        e["design"] = design
    return Config(d, cfg.path)


def fixed_alloc(cfg, share: float, design: str = "standard"):
    """Return a copy of ``cfg`` with a constant allocation and the given design (no ramp)."""
    from engine.config import Config

    d = copy.deepcopy(cfg.as_dict())
    d["experiments"]["ramp_schedule"] = [{"start_day": 0, "share": share}]
    for e in d["experiments"]["list"]:
        if e["id"] == "exp_reward_sizing":
            e["design"] = design
    return Config(d, cfg.path)


# --- one generic plot helper -------------------------------------------------------------------
def forest(ax, effects: list, labels: list, truth: float | None = None, colors=None):
    """Forest plot of Effect objects (point + 95% CI) — used in NB03."""
    import numpy as np

    y = np.arange(len(effects))[::-1]
    colors = colors or [BLUE] * len(effects)
    for yi, eff, c in zip(y, effects, colors):
        ax.plot([eff.ci_low, eff.ci_high], [yi, yi], color=c, lw=2.4, solid_capstyle="round")
        ax.plot(eff.point, yi, "o", color=c, ms=8, zorder=3)
    if truth is not None:
        ax.axvline(truth, color=GREEN, ls="--", lw=1.6, label=f"ground truth = {truth:+.4f}")
        ax.legend(loc="best")
    ax.axvline(0, color=GRAY, lw=1, alpha=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel("treatment effect (margin per user)")
