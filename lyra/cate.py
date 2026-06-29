"""CATE estimators — the meta-learner family + a causal forest (LYRA §8). Promoted from NB 09.

Each is a ``fit(df) → self`` / ``predict_cate(X) → τ̂(x)`` estimator of the heterogeneous effect:
- **SLearner** — one model on [X, T]; simple but regularization shrinks τ̂ toward the ATE.
- **TLearner** — separate per-arm models; each fits the nuisance, not the effect.
- **XLearner** — impute individual effects, regress on x (Künzel 2019); strong with complex surfaces.
- **CausalForest** — `econml.CausalForestDML` (Wager–Athey honest forest); **valid pointwise CIs** for τ(x).
"""

from __future__ import annotations

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor as _GBR


def _xcols(df):
    return [c for c in df.columns if c.startswith("x") and c[1:].isdigit()]


class _CATE:
    estimand = "CATE"

    def __init__(self, base=_GBR, x_cols=None):
        self.base, self.x_cols = base, x_cols

    def _fit_prep(self, df):
        self._cols = self.x_cols or _xcols(df)
        return df[self._cols].to_numpy(float), df["treat"].to_numpy(), df["y"].to_numpy(float)

    def _asX(self, X):
        return X[self._cols].to_numpy(float) if hasattr(X, "columns") else np.asarray(X, float)


class SLearner(_CATE):
    def fit(self, df):
        X, T, y = self._fit_prep(df)
        self.mu = self.base().fit(np.c_[X, T], y); return self

    def predict_cate(self, X):
        X = self._asX(X)
        return self.mu.predict(np.c_[X, np.ones(len(X))]) - self.mu.predict(np.c_[X, np.zeros(len(X))])


class TLearner(_CATE):
    def fit(self, df):
        X, T, y = self._fit_prep(df)
        self.m1 = self.base().fit(X[T == 1], y[T == 1]); self.m0 = self.base().fit(X[T == 0], y[T == 0]); return self

    def predict_cate(self, X):
        X = self._asX(X); return self.m1.predict(X) - self.m0.predict(X)


class XLearner(_CATE):
    def __init__(self, base=_GBR, x_cols=None, e=0.5):
        super().__init__(base, x_cols); self.e = e

    def fit(self, df):
        X, T, y = self._fit_prep(df)
        m1 = self.base().fit(X[T == 1], y[T == 1]); m0 = self.base().fit(X[T == 0], y[T == 0])
        d1 = y[T == 1] - m0.predict(X[T == 1])               # treated: actual − imputed control
        d0 = m1.predict(X[T == 0]) - y[T == 0]               # control: imputed treated − actual
        self.t1 = self.base().fit(X[T == 1], d1); self.t0 = self.base().fit(X[T == 0], d0); return self

    def predict_cate(self, X):
        X = self._asX(X); return self.e * self.t0.predict(X) + (1 - self.e) * self.t1.predict(X)


class CausalForest(_CATE):
    def __init__(self, n_estimators=400, base=_GBR, x_cols=None, random_state=0):
        super().__init__(base, x_cols); self.n_estimators, self.random_state = n_estimators, random_state

    def fit(self, df):
        from econml.dml import CausalForestDML
        X, T, y = self._fit_prep(df)
        self.cf = CausalForestDML(model_y=self.base(), model_t=self.base(), discrete_treatment=True,
                                  n_estimators=self.n_estimators, random_state=self.random_state).fit(y, T, X=X)
        return self

    def predict_cate(self, X):
        return self.cf.effect(self._asX(X))

    def predict_interval(self, X, alpha=0.05):
        return self.cf.effect_interval(self._asX(X), alpha=alpha)
