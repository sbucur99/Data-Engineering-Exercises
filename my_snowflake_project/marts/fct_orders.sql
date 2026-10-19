-- 3. Mart: business-ready fact table
-- models/marts/fct_orders.sql

{{ config(materialized='table') }}    -- transient table by default..
select
    order_id,
    order_date,
    customer_name,
    customer_tier,
    total_amount,
case
when total_amount >= 10000 then 'High Value'
when total_amount >= 1000 then 'Mid Value'
else 'Low Value'
end as order_tier
from {{ ref('int_orders_enriched') }}







-- This model depends on stg_orders AND stg_customers
-- dbt will build both staging models before this mart model
select
    o.order_id,
    o.order_date,
    c.customer_name,
    c.customer_tier,
    o.total_amount
from {{ ref('stg_orders') }} o
join {{ ref('stg_customers') }} c
on o.customer_id = c.customer_id;

-- dbt-generated DAG:
-- raw.orders    ──► stg_orders    ──┐
--                                   ├──► fct_orders
-- raw.customers ──► stg_customers ──┘






-- models/marts/fct_events.sql
{{ config(
    materialized = 'incremental',
    unique_key = 'event_id'
    -- unique_key: if event_id already exists in the table, UPDATE it
    -- if it is new, INSERT it. Without unique_key: always INSERT.
) }}
select
    event_id,
    user_id,
    event_type,
    event_timestamp,
    page_url
from {{ source('raw', 'events') }}  -- public, orders
{% if is_incremental() %}
    -- This WHERE clause runs ONLY on incremental runs (not first build)
    -- {{ this }} = the existing table in the warehouse
    where event_timestamp > (select max(event_timestamp) from {{ this }})
{% endif %}


/*
Snowflake            dbt_model stage 
orders                

picks ups >   model gets the changes
martialization = inccrmental must also be


order timestamp    full load stores timestampe model
*/
-- complete backfill can just run again 
-- but would have to do it in ingestion phase not dbt
-- what about back filling? 

-- source