"""Experiment registry + lifecycle **state machine** (LYRA §2 layer 2, §3).

The "create experiment" flow is a state machine, not a button: `DRAFT → RUNNING → STOPPED → ANALYZED →
DECIDED`. Recording the *decision* (not just the stats) at DECIDED is what makes it a platform. Steal:
DoorDash Curie's explicit lifecycle; the Etsy decision-checklist; Microsoft Flywheel's Entrance/Exit reviews.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict

STATES = ["DRAFT", "RUNNING", "STOPPED", "ANALYZED", "DECIDED"]
TRANSITIONS: dict[str, list[str]] = {
    "DRAFT": ["RUNNING"],
    "RUNNING": ["STOPPED"],
    "STOPPED": ["ANALYZED", "RUNNING"],   # resume or analyze
    "ANALYZED": ["DECIDED", "RUNNING"],   # decide or keep collecting
    "DECIDED": [],
}


@dataclass
class Experiment:
    id: str
    name: str
    hypothesis: str
    owner: str
    salt: str
    allocations: dict                      # {"control": .5, "treatment": .5}
    metric: dict                           # {"name","type","class","direction"}  (a MetricSpec)
    state: str = "DRAFT"
    # backing: which Vega/DGP world produces this experiment's events (the ground-truth source)
    world: dict = field(default_factory=dict)   # {"dgp","estimator","params","truth_label"}
    design: str = "user"                   # "user" | "cluster"
    days: int = 21
    n_per_day: int = 1500
    created: str = ""                      # ISO date (passed in; no Date.now in this env)
    started: str = ""
    decision: dict = field(default_factory=dict)   # filled at DECIDED: {ship, rationale, checklist}
    guardrails: list = field(default_factory=list)
    # guardrail readouts for the ship rule (NB 08): [{name, effect, ci_low, ci_high, margin, direction}]
    guardrail_readouts: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class Registry:
    """In-memory experiment store (Postgres/Supabase later — LYRA §13). Enforces the state machine."""

    def __init__(self):
        self._store: dict[str, Experiment] = {}

    def add(self, exp: Experiment) -> Experiment:
        self._store[exp.id] = exp
        return exp

    def get(self, exp_id: str) -> Experiment:
        return self._store[exp_id]

    def all(self) -> list[Experiment]:
        return list(self._store.values())

    def transition(self, exp_id: str, to_state: str, decision: dict | None = None) -> Experiment:
        exp = self._store[exp_id]
        if to_state not in TRANSITIONS[exp.state]:
            raise ValueError(f"illegal transition {exp.state} → {to_state} "
                             f"(allowed: {TRANSITIONS[exp.state]})")
        exp.state = to_state
        if to_state == "DECIDED" and decision:
            exp.decision = decision
        return exp
