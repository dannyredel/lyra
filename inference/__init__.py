"""Vega inference library — the crown jewel.

A standalone, importable, unit-tested package of causal estimators. Each estimator ships with a
recovery test asserting it covers the simulator's known ``ground_truth_tau`` at its nominal rate
(see ``tests/``). Estimators read ONLY what a real platform would see — in ``real`` mode they
never read ``ground_truth_tau``.

Estimators (config ``inference.estimators``):
  naive · cuped · cluster · budget_split · anytime_valid · incrementality · ope   (+ hte, switchback)

Add an estimator in this order: module here → recovery test → wire into the metrics readout.
"""
