-- top_3_recent_users_per_state.sql
-- Analytical view: the 3 most recently registered users for every state.
--
-- Implementation notes:
--   • Uses ROW_NUMBER() window function partitioned by state and ordered by
--     registration_date descending so rank 1 = most recent.

with ranked_users as (

    select
        user_id,
        name,
        email,
        state,
        registration_date,
        registration_year,
        registration_month,

        row_number() over (
            partition by state
            order by registration_date desc
        ) as recency_rank

    from {{ ref('dim_users') }}

)

select
    state,
    recency_rank,
    user_id,
    name,
    email,
    registration_date,
    registration_year,
    registration_month

from ranked_users
where recency_rank <= 3
order by state, recency_rank
