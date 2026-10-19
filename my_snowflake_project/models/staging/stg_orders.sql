-- This SELECT statement is the entire model.
-- dbt creates analytics.stg_orders from it.
SELECT
    order_id,
    customer_id,
    order_date,
    total_amount
FROM PUBLIC.orders
WHERE order_id is not null


-- for the Source yml incremental loading?

-- models/staging/stg_orders.sql
select 
    order_id, 
    customer_id, 
    order_date,
    total_amount
from 
    {{ source('raw', 'orders') }}
-- 'raw' = the source name defined in YAML
-- 'orders' = the table name within that source
-- dbt resolves to: prod_db.raw.orders


/*
in between automating Airflow
use this to understand whether data loading
properly

every 24 hrs or something can do alert-freshness check


dbt source freshness

# Checks loaded_at_field for all sources
# Returns WARN or ERROR if data is stale
# Run this in your pipeline to detect upstream failures early

test
seeds
documentation


dbt Cloud: create a job with a cron schedule, and enable the 
“Run source freshness” option (or add dbt source freshness as a step). 
Cloud can also show freshness on the job and send notifications.

Airflow
*/