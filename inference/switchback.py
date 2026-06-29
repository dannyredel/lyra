"""Switchback estimator — region-time randomization (Phase 3, Glovo vertical).

Responsibility (B-20): randomize on region-time units, aggregate to the randomization unit before
testing, handle carryover / optimal switch duration. Not in the Almedia MVP; here so the spine is
visibly vertical-agnostic.

Refs: DoorDash switchback posts (2018/2019); Bojinov & Simchi-Levi (2021/23); Netflix design-based
CS covers switchback too.
"""

from __future__ import annotations

# TODO(B-20): implement estimate(df, unit=region_time, alpha).
