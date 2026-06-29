"""The two parallel interfaces — the core architectural decision (LYRA §3).

Promoted from the raw build in ``notebooks/01_spine``. Estimators **guess**; DGPs **know**. Their
symmetry *is* the architecture: build the loop once and every method added later earns a
"certified: yes/no" badge for free.

Designed against the *hardest* shapes so we never refactor at Phase 3:
- **CATE** → ``point``/``ci`` may be ``np.ndarray``;
- **always-valid** → ``ci`` may be a confidence *sequence*;
- **switchback** → estimators may read a design from ``config``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

import numpy as np


@dataclass
class EstimatorResult:
    """What every estimator returns. Scalar ATE today; arrays/sequences allowed for CATE/always-valid."""

    estimator: str
    point: float | np.ndarray
    ci: tuple[float, float] | np.ndarray | None = None
    se: float | np.ndarray | None = None
    estimand: str = "ATE"
    p_value: float = float("nan")
    diagnostics: dict = field(default_factory=dict)
    method_metadata: dict = field(default_factory=dict)

    def covers(self, truth: float) -> bool:
        """Does the (scalar) CI cover a known truth? — the harness's coverage check."""
        if self.ci is None or np.ndim(self.point) != 0:
            raise ValueError("covers() is for scalar results with a (lo, hi) CI")
        lo, hi = self.ci
        return bool(lo <= truth <= hi)

    @property
    def ci_low(self):
        return self.ci[0] if self.ci is not None else None

    @property
    def ci_high(self):
        return self.ci[1] if self.ci is not None else None


@dataclass
class GroundTruth:
    """What a DGP knows that an estimator can't see — the validation oracle."""

    ate: float
    cate: Any = None                 # callable X→effect, or per-unit vector
    per_period_effect: np.ndarray | None = None
    extra: dict = field(default_factory=dict)


@runtime_checkable
class Estimator(Protocol):
    name: str
    estimand: str
    requires: set[str]

    def estimate(self, data, config: dict | None = ...) -> EstimatorResult: ...


@runtime_checkable
class DGP(Protocol):
    name: str

    def sample(self, n: int, seed: int): ...
    def ground_truth(self) -> GroundTruth: ...
