-- 1. Staging: clean raw data
-- models/staging/stg_orders.sql
select
    order_id,
    customer_id,
    cast(order_date as date) as order_date,
    cast(total_amount as decimal) as total_amount,
    upper(trim(status)) as status
from raw.orders