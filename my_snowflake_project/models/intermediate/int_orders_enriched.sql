-- 2. Intermediate: join and enrich
-- models/intermediate/int_orders_enriched.sql
select
o.order_id,
o.order_date,
o.total_amount,
-- o.status,
c.customer_name,
c.customer_tier
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c
on o.customer_id = c.customer_id