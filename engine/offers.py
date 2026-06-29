"""Offer / advertiser-campaign model.

Responsibility (T-12): build the offer wall from ``config.offers`` and ``config.market``:
- ``payout`` (advertiser pays per completion), ``difficulty_effort`` (effort a completion costs),
- ``reward_shown = payout * pass_through`` (treatment lever shifts ``pass_through``),
- ``category``, ``budget_cap`` (depletes via ``budget_decrement``; exhaustion permanent unless
  ``offers.refill: daily``).

Offers nest under advertisers (``market.n_advertisers``); experiments live on specific advertisers.

Interference channel (EVENT_LOG §5): budget is held **per offer** and is the shared finite pool.
Treated users (richer reward) complete an offer faster, depleting its ``budget_cap`` sooner, so
control users arriving later find it exhausted — contaminating the control arm. The contamination
grows with treatment allocation, which is the naive-estimator bias the project exposes.
"""

from __future__ import annotations

import string
from dataclasses import dataclass

import numpy as np

from engine.config import Config


def advertiser_ids(n: int) -> list[str]:
    """``adv_A, adv_B, ...`` — letters so experiment configs can reference ``adv_A`` directly."""
    if n <= 26:
        return [f"adv_{string.ascii_uppercase[i]}" for i in range(n)]
    return [f"adv_{i:03d}" for i in range(n)]


@dataclass(slots=True)
class Offer:
    offer_id: str
    advertiser_id: str
    category: str
    category_index: int
    payout: float                # advertiser pays this per completion
    difficulty_effort: float     # effort a completion costs the user
    pass_through: float          # reward_shown = payout * pass_through (baseline/control)
    budget_cap: float            # cumulative payout this offer can spend before going dark
    # --- mutable state ---
    budget_spent: float = 0.0

    @property
    def available(self) -> bool:
        return self.budget_spent < self.budget_cap

    def reward_shown(self, pass_through_delta: float = 0.0) -> float:
        """Reward an agent sees; ``pass_through_delta`` is the treatment lever (0 for control)."""
        return self.payout * (self.pass_through + pass_through_delta)

    def can_afford_completion(self) -> bool:
        """Offer has enough remaining budget to credit one more payout."""
        return self.budget_spent + self.payout <= self.budget_cap


def _sample(spec, n, rng) -> np.ndarray:
    dist = spec["dist"]
    if dist == "lognormal":
        return rng.lognormal(mean=spec["mu"], sigma=spec["sigma"], size=n)
    if dist == "gamma":
        return rng.gamma(shape=spec["shape"], scale=spec["scale"], size=n)
    raise ValueError(f"unsupported offer distribution: {dist!r}")


def build_offers(cfg: Config, rng: np.random.Generator) -> list[Offer]:
    """Construct the offer wall: ``market.n_offers`` offers spread across advertisers/categories."""
    n = int(cfg.market.n_offers)
    n_adv = int(cfg.market.n_advertisers)
    cats = list(cfg.market.categories)
    advs = advertiser_ids(n_adv)

    o = cfg.offers
    payout = _sample(o.payout.as_dict(), n, rng)
    effort = _sample(o.difficulty_effort.as_dict(), n, rng)
    budget = _sample(o.budget_cap.as_dict(), n, rng)
    pass_through = float(o.pass_through_default)

    # Round-robin advertisers so every experiment advertiser (adv_A..adv_D) owns >=1 offer,
    # then assign a category by independent draw.
    cat_idx = rng.integers(0, len(cats), size=n)

    offers: list[Offer] = []
    for i in range(n):
        adv = advs[i % n_adv]
        ci = int(cat_idx[i])
        offers.append(
            Offer(
                offer_id=f"of_{i:03d}",
                advertiser_id=adv,
                category=cats[ci],
                category_index=ci,
                payout=float(payout[i]),
                difficulty_effort=float(effort[i]),
                pass_through=pass_through,
                budget_cap=float(budget[i]),
            )
        )
    return offers


def decrement_budget(offer: Offer, amount: float) -> None:
    """Spend ``amount`` of an offer's budget (a completion's payout). Caller checks affordability."""
    offer.budget_spent += amount


def refill_offers(offers: list[Offer], mode: str) -> None:
    """Daily refill hook: if ``offers.refill == 'daily'`` reset spent budgets; else exhaustion is real."""
    if mode == "daily":
        for off in offers:
            off.budget_spent = 0.0


def offers_by_advertiser(offers: list[Offer]) -> dict[str, list[Offer]]:
    out: dict[str, list[Offer]] = {}
    for off in offers:
        out.setdefault(off.advertiser_id, []).append(off)
    return out
