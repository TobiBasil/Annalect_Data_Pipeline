-- tests/assert_email_format_valid.sql
-- Singular test: returns any row in stg_users whose email does not match
-- a basic RFC-5321-compatible pattern.
--
-- A non-empty result set means the test FAILS.

select email
from {{ ref('stg_users') }}
where email not like '%@%.%'
   or email like '%@%@%'
   or trim(email) != email
