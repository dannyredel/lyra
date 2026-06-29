"""Off-policy evaluation — score a new ranking policy from logs of the old one.

Responsibility (Phase 2, B-10): IPS and doubly-robust estimators
(``inference.ope.estimators``) that reweight logged choices by ``propensity`` to estimate the
value of a counterfactual ranking policy, validated against simulator ground truth. The "causal
inference in AI products" signal; shares the counterfactual-logging substrate with the eval funnel.

Requires ``logs_propensity: true`` on the experiment (Game B). Refs: Dudík/Langford/Li (DR 2011);
Swaminathan & Joachims (self-normalized, 2015).
"""

from __future__ import annotations

# TODO(B-10): implement ips(...), doubly_robust(...), policy_value(...).
