# staging/

Typed views over the raw parquet event log (`events/day=*/events.parquet`). One staging model per
event type (or a single wide `stg_events`), casting columns per EVENT_LOG §3.

**Critical (EVENT_LOG §4):** in `real` mode the staging model **drops `ground_truth_tau`** so
nothing downstream of metrics can read it. Gate it on `var('mode')`:

```sql
select
    event_id, ts, day, event_type, user_id, cluster_id,
    advertiser_id, offer_id, experiment_id, variant, allocation,
    effort_spent, reward_shown, value, propensity
    {% if var('mode') == 'oracle' %}, ground_truth_tau{% endif %}
from read_parquet('{{ var("event_log_dir") }}/day=*/events.parquet', hive_partitioning = true)
```

Only `validation/` and `tests/` (oracle path) ever see truth.

Planned models: `stg_events.sql`, then `stg_assignments`, `stg_impressions`, `stg_conversions`,
`stg_budget_decrements`, `stg_churn` as needed. (T-20)
