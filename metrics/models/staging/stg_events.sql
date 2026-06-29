{{ config(materialized='view') }}

-- Typed view over the raw append-only event log (EVENT_LOG §3).
-- CRITICAL (EVENT_LOG §4): in `real` mode we DROP ground_truth_tau here, so nothing downstream of
-- the metrics layer can ever read the simulator's hidden truth. Only `oracle` mode keeps it
-- (validation/tests use that path).
--
-- hive_partitioning=false → read the file's own typed columns (incl. day as INTEGER) rather than
-- the string day= from the partition path.

select
    event_id,
    cast(ts as timestamp)    as ts,
    cast(day as integer)     as day,
    event_type,
    user_id,
    cluster_id,
    advertiser_id,
    offer_id,
    experiment_id,
    variant,
    cast(allocation   as double) as allocation,
    cast(effort_spent as double) as effort_spent,
    cast(reward_shown as double) as reward_shown,
    cast(value        as double) as value,
    cast(propensity   as double) as propensity
    {% if var('mode') == 'oracle' %}
    , cast(ground_truth_tau as double) as ground_truth_tau
    {% endif %}
from read_parquet(
    '{{ var("event_log_dir") }}/day=*/events.parquet',
    hive_partitioning = false
)
