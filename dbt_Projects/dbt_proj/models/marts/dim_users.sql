-- dim_users.sql
-- Marts layer: clean dimensional model.
--
-- Deduplication strategy (SCD Type 1):
--   One row per email address, keeping the most recently registered record.
--   A surrogate key (user_id) is generated from the email address so it
--   remains stable across incremental runs.
--
-- Incremental strategy:
--   On each run we merge only rows whose registration_date is newer than the
--   latest value already loaded. The unique_key on user_id ensures that an
--   updated record for the same email replaces the previous one.

{{
    config(
        materialized = 'incremental',
        unique_key   = 'user_id',
        incremental_strategy = 'delete+insert'
    )
}}

with source as (

    select * from {{ ref('int_users_enriched') }}

    {% if is_incremental() %}
    -- Only process records newer than what we already have
    where registration_date > (select max(registration_date) from {{ this }})
    {% endif %}

),

-- Keep the latest record per email (SCD Type 1 — last-write wins)
deduped as (

    select *
    from (
        select
            *,
            row_number() over (
                partition by email
                order by registration_date desc
            ) as _row_num
        from source
    ) ranked
    where _row_num = 1

),

final as (

    select
        -- Surrogate key: deterministic hash of the natural key (email)
        md5(lower(trim(email)))   as user_id,

        name,
        gender,
        city,
        state,
        country,
        email,
        age,
        age_band,
        registration_date,
        registration_year,
        registration_month

    from deduped

)

select * from final
