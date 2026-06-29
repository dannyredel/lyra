"""Shared inference types + the duckdb loader over the event log.

The loader is the boundary the estimators read through. For M2 it reads the parquet event log
**directly via duckdb** (the dbt metrics layer is M3); when M3 lands, estimators will point at the
dbt marts instead — same per-user shape, so the estimators don't change.

``real`` mode discipline (EVENT_LOG §4): the loader **never selects ``ground_truth_tau``**. The
oracle (``engine.oracle``) is the only path to truth, and only tests/validation call it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd


@dataclass(slots=True)
class Effect:
    """An estimated treatment effect with a (1-α) interval. The common estimator return type."""

    estimator: str
    point: float
    ci_low: float
    ci_high: float
    se: float
    n_treatment: int
    n_control: int
    p_value: float = float("nan")
    extra: dict | None = None

    def covers(self, truth: float) -> bool:
        return self.ci_low <= truth <= self.ci_high

    def __str__(self) -> str:
        return (f"{self.estimator:<14} {self.point:+.5f}  "
                f"[{self.ci_low:+.5f}, {self.ci_high:+.5f}]  se={self.se:.5f}  "
                f"n=({self.n_treatment},{self.n_control})")


def _events_glob(events_dir: str | Path) -> str:
    return str(Path(events_dir) / "day=*" / "events.parquet").replace("\\", "/")


def user_outcomes(
    events_dir: str | Path,
    experiment_id: str,
    *,
    con: duckdb.DuckDBPyConnection | None = None,
) -> pd.DataFrame:
    """Per-user analysis table for one experiment (the unit a user-level estimator sees).

    Columns: ``user_id``, ``arm`` (control/treatment/holdout — final arm under the monotone ramp),
    ``cluster_id``, ``outcome`` (total conversion margin on the experiment's advertiser, 0 if none),
    ``n_conv``. Includes every assigned user (left join), so the extensive margin is represented.
    Never reads ``ground_truth_tau``.
    """
    glob = _events_glob(events_dir)
    own = con is None
    con = con or duckdb.connect()
    sql = f"""
        WITH ev AS (
            SELECT * FROM read_parquet('{glob}') WHERE experiment_id = ?
        ),
        assign AS (
            SELECT user_id,
                   max(CASE WHEN variant = 'holdout'   THEN 1 ELSE 0 END) AS is_h,
                   max(CASE WHEN variant = 'treatment' THEN 1 ELSE 0 END) AS is_t,
                   any_value(cluster_id) AS cluster_id
            FROM ev WHERE event_type = 'assignment' GROUP BY user_id
        ),
        conv AS (
            SELECT user_id, sum(value) AS outcome, count(*) AS n_conv
            FROM ev WHERE event_type = 'conversion' GROUP BY user_id
        )
        SELECT a.user_id,
               CASE WHEN a.is_h = 1 THEN 'holdout'
                    WHEN a.is_t = 1 THEN 'treatment'
                    ELSE 'control' END AS arm,
               a.cluster_id,
               coalesce(c.outcome, 0.0) AS outcome,
               coalesce(c.n_conv, 0)    AS n_conv
        FROM assign a LEFT JOIN conv c USING (user_id)
    """
    df = con.execute(sql, [experiment_id]).df()
    if own:
        con.close()
    return df


def experiment_assignments(events_dir, experiment_id: str) -> pd.DataFrame:
    """One row per assigned user: ``user_id, arm, cluster_id`` (includes non-converters)."""
    glob = _events_glob(events_dir)
    con = duckdb.connect()
    df = con.execute(
        f"""SELECT user_id,
                   CASE WHEN max(CASE WHEN variant='holdout'   THEN 1 ELSE 0 END)=1 THEN 'holdout'
                        WHEN max(CASE WHEN variant='treatment' THEN 1 ELSE 0 END)=1 THEN 'treatment'
                        ELSE 'control' END AS arm,
                   any_value(cluster_id) AS cluster_id
            FROM read_parquet('{glob}') WHERE event_type='assignment' AND experiment_id=?
            GROUP BY user_id""",
        [experiment_id],
    ).df()
    con.close()
    return df


def experiment_conversions(events_dir, experiment_id: str) -> pd.DataFrame:
    """One row per conversion: ``user_id, day, value`` for an experiment. Never reads tau."""
    glob = _events_glob(events_dir)
    con = duckdb.connect()
    df = con.execute(
        f"""SELECT user_id, CAST(day AS INTEGER) AS day, value
            FROM read_parquet('{glob}') WHERE event_type='conversion' AND experiment_id=?""",
        [experiment_id],
    ).df()
    con.close()
    return df


def user_pre_post(events_dir, experiment_id: str, split_day: int) -> pd.DataFrame:
    """Per-user pre/post split for CUPED: ``user_id, arm, pre, post``.

    ``pre``  = total conversion margin in the **warmup** (day < split_day; pre-treatment, so a clean
    covariate), ``post`` = total margin in the **treatment** period (day >= split_day). Includes
    every assigned user (0 if they never converted in a window).
    """
    glob = _events_glob(events_dir)
    con = duckdb.connect()
    df = con.execute(
        f"""
        WITH ev AS (SELECT * FROM read_parquet('{glob}') WHERE experiment_id = ?),
        assign AS (
            SELECT user_id,
                   CASE WHEN max(CASE WHEN variant='holdout'   THEN 1 ELSE 0 END)=1 THEN 'holdout'
                        WHEN max(CASE WHEN variant='treatment' THEN 1 ELSE 0 END)=1 THEN 'treatment'
                        ELSE 'control' END AS arm
            FROM ev WHERE event_type='assignment' GROUP BY user_id),
        pre AS (
            SELECT user_id, sum(value) v FROM ev
            WHERE event_type='conversion' AND CAST(day AS INTEGER) < ? GROUP BY user_id),
        post AS (
            SELECT user_id, sum(value) v FROM ev
            WHERE event_type='conversion' AND CAST(day AS INTEGER) >= ? GROUP BY user_id)
        SELECT a.user_id, a.arm,
               coalesce(pre.v, 0.0)  AS pre,
               coalesce(post.v, 0.0) AS post
        FROM assign a
        LEFT JOIN pre  USING (user_id)
        LEFT JOIN post USING (user_id)
        """,
        [experiment_id, split_day, split_day],
    ).df()
    con.close()
    return df
