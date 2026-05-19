-- stg_users.sql
-- Staging layer: rename fields to snake_case, enforce types, basic cleaning only.
-- No business logic lives here — this model is a faithful typed representation
-- of the seed data with consistent column naming.


with source as (

    select * from {{ ref('clean_users') }}

),

staged as (

    select
        name as name,
        lower(trim(gender)) as gender,
        initcap(trim(city)) as city,
        initcap(trim(state)) as state,
        initcap(trim(country)) as country,
        lower(trim(email)) as email,
        to_number(age) as age,
        to_timestamp(registration_date) as registration_date

    from source

)

select * from staged
