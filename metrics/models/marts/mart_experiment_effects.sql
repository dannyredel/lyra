{{ config(materialized='table') }}

-- The experiment readout: the naive treatment effect (difference in means, treatment − control)
-- with a Welch standard error and a 95% CI — computed in pure SQL over the event log.
--
-- This is the same quantity `inference/naive.py` returns; having it here makes "the metrics layer
-- computes the readout" literally true (it's a dbt deliverable, not a pandas script). The
-- interference-aware corrections (budget-split, cluster-robust) stay in the Python inference
-- library, where the design/estimator logic lives. Holdout users are excluded.

with arms as (
    select experiment_id, arm, n_users, mean_outcome, var_outcome
    from {{ ref('mart_experiment_readout') }}
    where arm in ('treatment', 'control')
),

wide as (
    select
        experiment_id,
        max(case when arm = 'treatment' then n_users      end) as n_t,
        max(case when arm = 'treatment' then mean_outcome end) as mean_t,
        max(case when arm = 'treatment' then var_outcome  end) as var_t,
        max(case when arm = 'control'   then n_users      end) as n_c,
        max(case when arm = 'control'   then mean_outcome end) as mean_c,
        max(case when arm = 'control'   then var_outcome  end) as var_c
    from arms
    group by experiment_id
)

select
    experiment_id,
    n_t,
    n_c,
    mean_t - mean_c                                            as effect,
    sqrt(var_t / n_t + var_c / n_c)                            as se,
    (mean_t - mean_c) - 1.959964 * sqrt(var_t / n_t + var_c / n_c) as ci_low,
    (mean_t - mean_c) + 1.959964 * sqrt(var_t / n_t + var_c / n_c) as ci_high,
    -- significant at 95% iff the CI excludes zero
    not ((mean_t - mean_c) - 1.959964 * sqrt(var_t / n_t + var_c / n_c) <= 0
         and (mean_t - mean_c) + 1.959964 * sqrt(var_t / n_t + var_c / n_c) >= 0) as significant
from wide
order by experiment_id
