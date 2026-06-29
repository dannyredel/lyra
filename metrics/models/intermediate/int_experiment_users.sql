{{ config(materialized='view') }}

-- One row per (experiment, user): the per-user analysis table the marts aggregate.
-- Mirrors `inference/base.user_outcomes` but in SQL — the metrics layer, not pandas.
--   arm     = final arm (holdout > treatment > control precedence; ramp may re-emit assignments)
--   outcome = total conversion margin on the experiment's advertiser (0 if the user never converted)
-- Never references ground_truth_tau (dropped upstream in real mode).

with assign as (
    select
        experiment_id,
        user_id,
        max(case when variant = 'holdout'   then 1 else 0 end) as is_holdout,
        max(case when variant = 'treatment' then 1 else 0 end) as is_treatment,
        any_value(cluster_id)                                  as cluster_id
    from {{ ref('stg_events') }}
    where event_type = 'assignment'
    group by experiment_id, user_id
),

conv as (
    select
        experiment_id,
        user_id,
        sum(value)  as outcome,
        count(*)    as n_conv
    from {{ ref('stg_events') }}
    where event_type = 'conversion'
    group by experiment_id, user_id
)

select
    a.experiment_id,
    a.user_id,
    a.cluster_id,
    case
        when a.is_holdout   = 1 then 'holdout'
        when a.is_treatment = 1 then 'treatment'
        else 'control'
    end                              as arm,
    coalesce(c.outcome, 0.0)         as outcome,
    coalesce(c.n_conv, 0)            as n_conv
from assign a
left join conv c
    on a.experiment_id = c.experiment_id
   and a.user_id       = c.user_id
