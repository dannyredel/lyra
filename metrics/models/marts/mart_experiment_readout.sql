{{ config(materialized='table') }}

-- Per (experiment, arm) summary — the building block for the experiment readouts.
--   n_users, mean/sum outcome (margin per user), mean conversions per user.

select
    experiment_id,
    arm,
    count(*)              as n_users,
    avg(outcome)          as mean_outcome,
    sum(outcome)          as total_outcome,
    avg(n_conv)           as mean_conversions,
    sum(n_conv)           as total_conversions,
    var_samp(outcome)     as var_outcome
from {{ ref('int_experiment_users') }}
group by experiment_id, arm
order by experiment_id, arm
