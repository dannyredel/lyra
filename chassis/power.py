"""The DRAFT power-gate — re-exported from `lyra.power` (promoted in NB 08).

The sample-size / MDE / gate logic now lives in the engine (`lyra/power.py`) so the chassis and the
notebooks share one definition. Kept here as a thin alias for existing imports.
"""

from lyra.power import mde, power_gate, required_n, test_and_roll_size  # noqa: F401
