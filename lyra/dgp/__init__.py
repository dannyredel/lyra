"""The DGP zoo — the fidelity ladder + realistic platform worlds (LYRA §5).

Every world is a `DGP` (``sample(n, seed)`` + ``ground_truth()``), so the harness from NB 01 can certify
any estimator against the *right* known truth per world. Built raw in `notebooks/{01_spine,02_dgp_zoo}`,
promoted here. Re-exports keep ``from lyra.dgp import DGPLevel1, covariate_cols`` working.
"""

from lyra.dgp.ladder import DGPLevel0, DGPLevel1, baseline, covariate_cols
from lyra.dgp.outcomes import (BinaryDGP, ClusteredDGP, CountDGP, PrePostDGP, RatioDGP, RevenueDGP,
                               SurvivalDGP)
from lyra.dgp.funnel import FunnelDGP
from lyra.dgp.panel import StaggeredPanelDGP
from lyra.dgp.interference import InterferenceDGP
from lyra.dgp.switchback import SwitchbackDGP
from lyra.dgp.ab import ABDGP
from lyra.dgp.hetero import HeteroDGP

__all__ = [
    "DGPLevel0", "DGPLevel1", "baseline", "covariate_cols",
    "BinaryDGP", "CountDGP", "RevenueDGP", "RatioDGP", "SurvivalDGP", "PrePostDGP", "ClusteredDGP",
    "FunnelDGP", "StaggeredPanelDGP", "InterferenceDGP", "SwitchbackDGP", "ABDGP", "HeteroDGP",
]
