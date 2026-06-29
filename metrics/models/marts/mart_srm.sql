{{ config(materialized='table') }}

-- Sample Ratio Mismatch — a trustworthiness guardrail (EVENT_LOG §6.6).
-- Realized treatment share vs the intended allocation, tested at the RANDOMIZATION UNIT.
--
-- The metrics layer doesn't know the config's randomization type, so we **detect it from the data**:
-- if a cluster never contains more than one arm, the experiment was cluster-randomized, and SRM must
-- be checked at the cluster level (user-level share legitimately varies when whole clusters flip
-- arm). Otherwise it's user-randomized and we use a user-level chi-square (1 d.o.f.).
--
-- Ramped experiments (allocation changes over the run) are reported informationally — their
-- cumulative share lags the latest allocation — so the hard check applies to constant-allocation
-- experiments (the A/A nulls). This mirrors engine/emit.py's unit-aware SRM report.

with arms as (
    select
        experiment_id,
        user_id,
        cluster_id,
        case when arm in ('treatment', 'holdout') then 1 else 0 end as treated
    from {{ ref('int_experiment_users') }}
),

-- is the experiment cluster-randomized? (arm ~constant within each cluster)
cluster_purity as (
    select
        experiment_id,
        count(*)                                          as n_clusters,
        sum(case when n_arms > 1 then 1 else 0 end)       as mixed_clusters
    from (
        select experiment_id, cluster_id, count(distinct treated) as n_arms
        from arms group by experiment_id, cluster_id
    ) t
    group by experiment_id
),

cluster_level as (
    select
        experiment_id,
        count(*)                                          as n_units,
        sum(c_treated)                                    as n_treat_units,
        avg(c_treated::double)                            as realized_cluster
    from (
        select experiment_id, cluster_id, max(treated) as c_treated
        from arms group by experiment_id, cluster_id
    ) t
    group by experiment_id
),

user_level as (
    select
        experiment_id,
        count(*)                                          as n_total,
        sum(treated)                                      as n_treat,
        count(*) - sum(treated)                           as n_control,
        avg(treated::double)                              as realized_user
    from arms group by experiment_id
),

intended as (
    select
        experiment_id,
        avg(allocation)                as intended_share,
        count(distinct allocation) > 1 as ramped
    from {{ ref('stg_events') }}
    where event_type = 'assignment'
    group by experiment_id
)

select
    u.experiment_id,
    -- detected randomization unit
    case when p.mixed_clusters * 20 < p.n_clusters then 'cluster' else 'user' end as unit,
    u.n_treat,
    u.n_control,
    u.n_total,
    i.intended_share,
    i.ramped,
    case when p.mixed_clusters * 20 < p.n_clusters
         then c.realized_cluster else u.realized_user end as realized_share,
    -- chi-square at the randomization unit (user-level for user designs; cluster-level otherwise)
    case when p.mixed_clusters * 20 < p.n_clusters
         then pow(c.n_treat_units - i.intended_share * c.n_units, 2)
                / nullif(i.intended_share * c.n_units, 0)
            + pow((c.n_units - c.n_treat_units) - (1 - i.intended_share) * c.n_units, 2)
                / nullif((1 - i.intended_share) * c.n_units, 0)
         else pow(u.n_treat - i.intended_share * u.n_total, 2)
                / nullif(i.intended_share * u.n_total, 0)
            + pow(u.n_control - (1 - i.intended_share) * u.n_total, 2)
                / nullif((1 - i.intended_share) * u.n_total, 0)
    end as chi_square,
    case
        when i.ramped then true                                   -- informational only
        when p.mixed_clusters * 20 < p.n_clusters then
            -- cluster-level: chi2 with 1 d.o.f., ~|z|>3.3 threshold
            (pow(c.n_treat_units - i.intended_share * c.n_units, 2)
                / nullif(i.intended_share * c.n_units, 0)
            + pow((c.n_units - c.n_treat_units) - (1 - i.intended_share) * c.n_units, 2)
                / nullif((1 - i.intended_share) * c.n_units, 0)) < 11.0
        else
            (pow(u.n_treat - i.intended_share * u.n_total, 2)
                / nullif(i.intended_share * u.n_total, 0)
            + pow(u.n_control - (1 - i.intended_share) * u.n_total, 2)
                / nullif((1 - i.intended_share) * u.n_total, 0)) < 11.0
    end as srm_ok
from user_level u
join cluster_level c using (experiment_id)
join cluster_purity p using (experiment_id)
join intended i using (experiment_id)
order by u.experiment_id
