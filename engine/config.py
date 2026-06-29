"""Load and validate ``config.yaml`` into typed objects; own seed management.

Responsibility (T-10):
- Parse ``config.yaml`` (the single source of truth — no magic numbers anywhere else).
- Validate ranges/enums (e.g. ``meta.mode in {real, oracle}``, distributions well-formed).
- Expose a frozen config object the rest of the engine reads.
- Build the seeded RNG(s) from ``meta.seed`` so a run is reproducible from (config + seed).

Nothing downstream should read ``config.yaml`` directly — go through here.

Design notes
------------
The config is held as nested ``dict``s wrapped in a thin ``Config`` that exposes both attribute
and item access (``cfg.market.n_users_initial`` or ``cfg["market"]["n_users_initial"]``). We keep
the raw dict so new config keys never need a code change to be *readable* — only keys we validate
or default need touching here.

Randomness is split into independent named streams via ``numpy.random.SeedSequence.spawn`` so that,
e.g., adding a churn draw never shifts the agent-sampling stream. A run is reproducible from
``(config.yaml + meta.seed)`` alone.
"""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from typing import Any

import numpy as np
import yaml

# Independent RNG streams. A stream's sequence is pinned to its index here (SeedSequence.spawn is
# order-stable by index), so keep this tuple append-only to preserve reproducibility.
RNG_STREAMS: tuple[str, ...] = (
    "agents",       # population + arrival sampling
    "offers",       # offer-wall construction
    "choice",       # MNL Gumbel/softmax draws
    "assignment",   # experiment arm assignment
    "churn",        # daily churn draws
    "shadow",       # counterfactual shadow runs (M2 ground truth)
    "clusters",     # per-cluster random effect (B-06 cluster-level structure)
)

_VALID_MODES = {"real", "oracle"}
_VALID_CHOICE_MODELS = {"mnl", "nested_logit"}
_VALID_REFILL = {"none", "daily"}
_VALID_WAREHOUSE = {"duckdb", "bigquery"}


class ConfigError(ValueError):
    """Raised when config.yaml violates the contract (bad enum, missing key, bad range)."""


class _Node:
    """Read-only attribute+item view over a nested dict (so ``cfg.market.n_offers`` works)."""

    __slots__ = ("_d",)

    def __init__(self, d: dict[str, Any]):
        object.__setattr__(self, "_d", d)

    def __getattr__(self, name: str) -> Any:
        try:
            return _wrap(self._d[name])
        except KeyError as e:
            raise AttributeError(name) from e

    def __getitem__(self, key: str) -> Any:
        return _wrap(self._d[key])

    def get(self, key: str, default: Any = None) -> Any:
        return _wrap(self._d.get(key, default))

    def __contains__(self, key: str) -> bool:
        return key in self._d

    def __iter__(self):
        return iter(self._d)

    def keys(self):
        return self._d.keys()

    def as_dict(self) -> dict[str, Any]:
        return self._d

    def __repr__(self) -> str:
        return f"_Node({', '.join(self._d)})"


def _wrap(v: Any) -> Any:
    if isinstance(v, dict):
        return _Node(v)
    if isinstance(v, list):
        return [_wrap(x) for x in v]
    return v


class Config(_Node):
    """The frozen run config. Top-level sections are attributes (``cfg.market``, ``cfg.choice``…).

    Also owns RNG construction: ``cfg.rng("agents")`` returns the named, seeded Generator.
    """

    __slots__ = ("_seeds", "path", "_cluster_effects")

    def __init__(self, d: dict[str, Any], path: Path | None = None):
        super().__init__(d)
        seed = int(d["meta"]["seed"])
        children = np.random.SeedSequence(seed).spawn(len(RNG_STREAMS))
        object.__setattr__(self, "_seeds", MappingProxyType(dict(zip(RNG_STREAMS, children))))
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "_cluster_effects", None)

    def cluster_effects(self) -> np.ndarray:
        """Per-cluster random-effect intercepts (length ``market.n_clusters``), sampled once.

        A shared geo/segment "engagement" shock added to every utility for users in that cluster
        (B-06). It induces **within-cluster outcome correlation (ICC > 0)** so the cluster-robust
        estimator has something to correct — randomizing at the cluster but analyzing at the user
        level then overstates precision (the Glovo lesson). ``agents.cluster_effect_sigma = 0``
        disables it (recovers the inert-label behaviour).
        """
        if self._cluster_effects is None:
            n = int(self._d["market"]["n_clusters"])
            sigma = float(self._d.get("agents", {}).get("cluster_effect_sigma", 0.0))
            eff = (self.rng("clusters").normal(0.0, sigma, size=n) if sigma > 0
                   else np.zeros(n))
            object.__setattr__(self, "_cluster_effects", eff)
        return self._cluster_effects

    def rng(self, stream: str) -> np.random.Generator:
        """A fresh Generator for a named stream (see ``RNG_STREAMS``). Same seed → same draws."""
        if stream not in self._seeds:
            raise ConfigError(f"unknown RNG stream {stream!r}; known: {sorted(self._seeds)}")
        return np.random.default_rng(self._seeds[stream])

    @property
    def seed(self) -> int:
        return int(self._d["meta"]["seed"])

    @property
    def mode(self) -> str:
        return str(self._d["meta"]["mode"])

    def with_overrides(self, **sections: Any) -> "Config":
        """Return a deep-copied config with top-level sections shallow-merged with ``sections``.

        Used by M2 shadow runs (e.g. force every agent into one arm) without mutating the original.
        """
        import copy

        d = copy.deepcopy(self._d)
        for section, patch in sections.items():
            if isinstance(d.get(section), dict) and isinstance(patch, dict):
                d[section].update(patch)
            else:
                d[section] = patch
        return Config(d, self.path)


# --------------------------------------------------------------------------- #
# loading + validation
# --------------------------------------------------------------------------- #
def load_config(path: str | Path = "config.yaml") -> Config:
    """Parse and validate ``config.yaml`` into a frozen :class:`Config`."""
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"config not found: {p}")
    with p.open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not isinstance(raw, dict):
        raise ConfigError("config.yaml must be a mapping at the top level")
    _validate(raw)
    return Config(raw, p)


def _require(d: dict, *keys: str, ctx: str = "") -> None:
    for k in keys:
        if k not in d:
            raise ConfigError(f"missing required key {ctx + '.' if ctx else ''}{k}")


def _validate(raw: dict[str, Any]) -> None:
    _require(raw, "meta", "market", "agents", "offers", "choice", "experiments")

    meta = raw["meta"]
    _require(meta, "seed", "horizon_days", "mode", ctx="meta")
    if meta["mode"] not in _VALID_MODES:
        raise ConfigError(f"meta.mode must be one of {_VALID_MODES}, got {meta['mode']!r}")
    if int(meta["horizon_days"]) < 1:
        raise ConfigError("meta.horizon_days must be >= 1")

    market = raw["market"]
    _require(market, "n_users_initial", "n_offers", "n_advertisers", "n_clusters", "categories",
             ctx="market")
    if int(market["n_offers"]) < int(market["n_advertisers"]):
        raise ConfigError("market.n_offers must be >= market.n_advertisers (>=1 offer per adv)")
    cats = market["categories"]
    if not isinstance(cats, list) or not cats:
        raise ConfigError("market.categories must be a non-empty list")

    # dirichlet alpha length must match categories
    cp = raw["agents"].get("category_propensity", {})
    if cp.get("dist") == "dirichlet":
        alpha = cp.get("alpha", [])
        if len(alpha) != len(cats):
            raise ConfigError(
                f"agents.category_propensity.alpha has {len(alpha)} entries but there are "
                f"{len(cats)} market.categories"
            )

    choice = raw["choice"]
    _require(choice, "model", "beta_reward", "beta_effort", "match_weight", ctx="choice")
    if choice["model"] not in _VALID_CHOICE_MODELS:
        raise ConfigError(f"choice.model must be one of {_VALID_CHOICE_MODELS}")

    if raw["offers"].get("refill", "none") not in _VALID_REFILL:
        raise ConfigError(f"offers.refill must be one of {_VALID_REFILL}")

    _validate_experiments(raw["experiments"])

    wh = raw.get("warehouse", {}).get("target", "duckdb")
    if wh not in _VALID_WAREHOUSE:
        raise ConfigError(f"warehouse.target must be one of {_VALID_WAREHOUSE}")


def _validate_experiments(exp: dict[str, Any]) -> None:
    _require(exp, "list", ctx="experiments")
    ramp = exp.get("ramp_schedule", [])
    last = -1
    for step in ramp:
        _require(step, "start_day", "share", ctx="experiments.ramp_schedule[]")
        if last != -1 and step["start_day"] <= last:
            raise ConfigError("experiments.ramp_schedule must have strictly increasing start_day")
        if not (0.0 <= float(step["share"]) <= 1.0):
            raise ConfigError("ramp share must be in [0, 1]")
        last = step["start_day"]

    seen_ids: set[str] = set()
    valid_rand = {"user", "cluster"}
    for e in exp["list"]:
        _require(e, "id", "advertiser", "type", "randomization", ctx="experiments.list[]")
        if e["id"] in seen_ids:
            raise ConfigError(f"duplicate experiment id {e['id']!r}")
        seen_ids.add(e["id"])
        if e["randomization"] not in valid_rand:
            raise ConfigError(
                f"experiment {e['id']}: randomization must be one of {valid_rand}, "
                f"got {e['randomization']!r}"
            )

    inc = exp.get("incrementality", {})
    if inc.get("enabled"):
        _require(inc, "target_experiment", "holdout_share", ctx="experiments.incrementality")
        if inc["target_experiment"] not in seen_ids:
            raise ConfigError(
                f"incrementality.target_experiment {inc['target_experiment']!r} "
                "is not a defined experiment"
            )
        if not (0.0 <= float(inc["holdout_share"]) < 1.0):
            raise ConfigError("incrementality.holdout_share must be in [0, 1)")
