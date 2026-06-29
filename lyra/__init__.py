"""Lyra — the experimentation platform layer (pivot, 2026-06-04; see LYRA.md).

This package holds the platform's architectural spine — the two parallel **Protocols** (`Estimator`
*guesses*, `DGP` *knows*) and the **Monte-Carlo harness** that closes the loop
``sim → assign → estimate → compare-to-truth → coverage/power``. The existing `engine/` (Vega L3
marketplace) and `inference/` estimators slot in behind these contracts; this package adds the lower
rungs of the DGP fidelity ladder (L0/L1) and the harness that certifies every estimator.
"""
