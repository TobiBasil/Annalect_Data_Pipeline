-- int_users_enriched.sql
-- Intermediate layer: add derived/enriched fields on top of the staging model.
-- Business logic (banding, date extraction) belongs here, not in staging or marts.

with stg as (

    select * from {{ ref('stg_users') }}

),

enriched as (

   select
        *,
        case
            when age between 0  and 18 then '0-18'
            when age between 19 and 25 then '19-25'
            when age between 26 and 40 then '26-40'
            else '40+'
        end as age_band,
        YEAR(registration_date) as registration_year,
        MONTH(registration_date) as registration_month

    from stg

)

select * from enriched
