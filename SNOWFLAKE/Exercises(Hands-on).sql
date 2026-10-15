--I’ve assumed a layout for sales.csv and customers.json since I haven’t seen them,
-- so adjust the column names to match your files.

-- Beginner
/*
Hands-On Exercises 
1. Create a database retail_db and a schema q3_sales. 
2. Create a Virtual Warehouse named retail_wh with size SMALL, auto-suspend = 300 seconds,
auto-resume = TRUE. 
3. Create a permanent table products with columns: product_id, product_name, price. 
4. Insert 5 rows of sample data into products. 
5. Query all rows where price > 100.
*/

CREATE DATABASE retail_db;
CREATE SCHEMA retail_db.q3_sales;

CREATE WAREHOUSE retail_wh
  WAREHOUSE_SIZE = 'SMALL' AUTO_SUSPEND = 300 AUTO_RESUME = TRUE;

USE WAREHOUSE retail_wh;
USE SCHEMA retail_db.q3_sales;

CREATE TABLE products (product_id INT, product_name STRING, price NUMBER(10,2));
INSERT INTO products VALUES
  (1,'Keyboard',49.99),(2,'Monitor',189.00),(3,'Laptop',999.00),
  (4,'Mouse',19.50),(5,'Desk',249.00);
SELECT * FROM products WHERE price > 100;

-- SMALL burns 2 credits/hour while running, so let it auto-suspend.



--Intermediate
/*
1.Create a file format my_csv_format for CSV files (skip 1 header row). 
2.Create an internal stage my_stage and upload the sample file sales.csv. 
3.Load the staged file into a Snowflake table sales_fact. 
4.Use the VARIANT data type to load and query a JSON file customers.json. Extract customer
names from the nested JSON. 
5.Create a Stream on sales_fact and query new rows after inserting additional data. 6.Create a Task that runs every 5 minutes to MERGE new rows from the stream into a summary
table. 

*/

-- 1. file format
CREATE FILE FORMAT my_csv_format TYPE = CSV SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"';



-- 2. internal stage
CREATE STAGE my_stage;
-- Upload from SnowSQL. PUT doesn’t work in Snowsight worksheets, 
-- so there you’d use the stage’s “+ Files” button instead.
powershell:
snowsql -a HBQVCEE-EV36349 -u SBUCUR99 -d retail_db -s q3_sales -w retail_wh

PUT file://C:\temp\sales.csv @my_stage;
PUT file://C:\temp\customers.json @my_stage;
LIST @my_stage;

-- See schema.....

-- 3. load (assumes columns: sale_id, region, product, amount, sale_date)
CREATE TABLE sales_fact (sale_id INT, region STRING, product STRING, amount NUMBER(10,2), sale_date DATE);

COPY INTO sales_fact FROM @my_stage/sales.csv.gz
  FILE_FORMAT = (FORMAT_NAME = my_csv_format);



-- 4. JSON into VARIANT (assumes {"customer":{"name":"Ann","address":{"city":"Austin"}}, "orders":[...]})
CREATE FILE FORMAT my_json_format TYPE = JSON STRIP_OUTER_ARRAY = TRUE;
CREATE TABLE customers_raw (v VARIANT);

COPY INTO customers_raw FROM @my_stage/customers.json.gz
  FILE_FORMAT = (FORMAT_NAME = my_json_format);

SELECT v:customer.name::STRING AS customer_name,
       v:customer.address.city::STRING AS city
FROM customers_raw;

-- STRING makes it stricter but not required



-- 5. stream (append-only is enough for inserts and keeps the merge simple)
CREATE STREAM sales_stream ON TABLE sales_fact APPEND_ONLY = TRUE;
INSERT INTO sales_fact VALUES (9001,'EAST','Laptop',999.00,'2026-10-01'),
                              (9002,'WEST','Mouse',19.50,'2026-10-02');

SELECT * FROM sales_stream;   -- shows the 2 new rows plus METADATA$ columns



-- 6. task: summary table + merge every 5 minutes
CREATE TABLE sales_summary (region STRING, total_amount NUMBER(12,2), order_count INT);
CREATE TASK sales_merge_task
  WAREHOUSE = retail_wh
  SCHEDULE = '5 MINUTE'
  WHEN SYSTEM$STREAM_HAS_DATA('sales_stream')
AS
MERGE INTO sales_summary t
USING (SELECT region, SUM(amount) AS amt, COUNT(*) AS cnt
       FROM sales_stream GROUP BY region) s
ON t.region = s.region
WHEN MATCHED THEN UPDATE SET t.total_amount = t.total_amount + s.amt,
                             t.order_count  = t.order_count + s.cnt
WHEN NOT MATCHED THEN INSERT VALUES (s.region, s.amt, s.cnt);

ALTER TASK sales_merge_task RESUME;   -- tasks are created suspended


/*
The WHEN SYSTEM$STREAM_HAS_DATA clause skips the run (and the warehouse spin-up) when 
there’s nothing new, which saves credits. Run ALTER TASK sales_merge_task SUSPEND; 
when you finish testing, or it keeps polling every 5 minutes.
*/



--Advanced

/*
Hands-On Exercises 
1.Create a table orders_raw and a Snowpipe orders_pipe that auto-ingests from an external S3 stage. 
2.Query the Snowpipe metadata to verify successful ingestions. 
3.Use Time Travel to recover a table dropped accidentally. 
4.Clone the sales_fact table as sales_clone and demonstrate that the clone initially uses no
extra storage. 
5.Create a Masking Policy to hide email addresses unless the user has the HR_ROLE. Test with two
different roles. 
6.Create a Row Access Policy that allows a user to see only rows for their assigned region. 
*/

-- 1. S3 + Snowpipe (needs an AWS account and bucket)
CREATE STORAGE INTEGRATION s3_int
  TYPE = EXTERNAL_STAGE STORAGE_PROVIDER = 'S3' ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::<account-id>:role/<role>'
  STORAGE_ALLOWED_LOCATIONS = ('s3://<bucket>/orders/');
DESC INTEGRATION s3_int;   -- put STORAGE_AWS_IAM_USER_ARN + STORAGE_AWS_EXTERNAL_ID in the IAM role's trust policy
CREATE STAGE orders_stage URL = 's3://<bucket>/orders/'
  STORAGE_INTEGRATION = s3_int FILE_FORMAT = (FORMAT_NAME = my_csv_format);
CREATE TABLE orders_raw (order_id INT, customer_id INT, amount NUMBER(10,2), order_ts TIMESTAMP_NTZ);
CREATE PIPE orders_pipe AUTO_INGEST = TRUE AS
  COPY INTO orders_raw FROM @orders_stage;
SHOW PIPES;   -- copy notification_channel (an SQS ARN) into the bucket's S3 event notifications

-- 2. verify ingestion
SELECT SYSTEM$PIPE_STATUS('orders_pipe');
SELECT file_name, status, row_count, first_error_message
FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(
  TABLE_NAME => 'ORDERS_RAW', START_TIME => DATEADD(HOUR, -24, CURRENT_TIMESTAMP)));

-- 3. recover a dropped table
DROP TABLE sales_summary;
UNDROP TABLE sales_summary;

-- 4. clone and storage
CREATE TABLE sales_clone CLONE sales_fact;

SELECT table_name, active_bytes, retained_for_clone_bytes
FROM retail_db.INFORMATION_SCHEMA.TABLE_STORAGE_METRICS
WHERE table_schema = 'Q3_SALES' AND table_name IN ('SALES_FACT','SALES_CLONE');

-- The clone should show about 0 active_bytes because it owns no partitions yet. 
-- Run UPDATE sales_clone SET amount = amount + 1; and re-run the query to watch it start owning storage.

-- 5. masking policy, tested with two roles
CREATE TABLE employees_pii (id INT, name STRING, email STRING, region STRING);
INSERT INTO employees_pii VALUES (1,'Ann','ann@corp.com','EAST'), (2,'Bob','bob@corp.com','WEST');
CREATE ROLE HR_ROLE;
CREATE ROLE ANALYST_ROLE;
CREATE MASKING POLICY email_mask AS (val STRING) RETURNS STRING ->
  CASE WHEN CURRENT_ROLE() = 'HR_ROLE' THEN val
       ELSE '*****@' || SPLIT_PART(val, '@', 2) END;
ALTER TABLE employees_pii MODIFY COLUMN email SET MASKING POLICY email_mask;
GRANT USAGE ON WAREHOUSE retail_wh TO ROLE HR_ROLE;
GRANT USAGE ON WAREHOUSE retail_wh TO ROLE ANALYST_ROLE;
GRANT USAGE ON DATABASE retail_db TO ROLE HR_ROLE;
GRANT USAGE ON DATABASE retail_db TO ROLE ANALYST_ROLE;
GRANT USAGE ON SCHEMA retail_db.q3_sales TO ROLE HR_ROLE;
GRANT USAGE ON SCHEMA retail_db.q3_sales TO ROLE ANALYST_ROLE;
GRANT SELECT ON TABLE employees_pii TO ROLE HR_ROLE;
GRANT SELECT ON TABLE employees_pii TO ROLE ANALYST_ROLE;
GRANT ROLE HR_ROLE TO USER SBUCUR99;
GRANT ROLE ANALYST_ROLE TO USER SBUCUR99;
USE ROLE HR_ROLE;      SELECT * FROM employees_pii;   -- real emails
USE ROLE ANALYST_ROLE; SELECT * FROM employees_pii;   -- *****@corp.com
USE ROLE ACCOUNTADMIN;

-- 6. row access policy: each role sees only its region
CREATE TABLE region_map (role_name STRING, region STRING);
INSERT INTO region_map VALUES ('HR_ROLE','EAST'), ('ANALYST_ROLE','WEST');
CREATE ROW ACCESS POLICY region_rap AS (r STRING) RETURNS BOOLEAN ->
  CURRENT_ROLE() = 'ACCOUNTADMIN'
  OR EXISTS (SELECT 1 FROM region_map m
             WHERE m.role_name = CURRENT_ROLE() AND m.region = r);
ALTER TABLE employees_pii ADD ROW ACCESS POLICY region_rap ON (region);
USE ROLE HR_ROLE;      SELECT * FROM employees_pii;   -- EAST row only
USE ROLE ANALYST_ROLE; SELECT * FROM employees_pii;   -- WEST row only
USE ROLE ACCOUNTADMIN;

-- The ACCOUNTADMIN exception keeps you from locking yourself out while testing. In a real setup, map users or roles to regions in the mapping table and drop that exception.
-- When you’re done for the day, run ALTER WAREHOUSE retail_wh SUSPEND; and suspend the task so the trial credits last.




/*
Do you need to create a schema before creating a stage and uploading a file?
You need a database and schema context, but you don't necessarily have to create them yourself. Snowflake has built-in databases and schemas in some setups, and you may already have one selected. A named stage is created inside a schema. 


A typical workflow is:

Step 1 — Database
Create one if needed.



Step 2 — Schema
Create one if needed.



Step 3 — Stage
Create a named internal stage to hold the file.



Step 4 — Upload
Upload the local file into the stage.



Step 5 — Load
Use COPY INTO to load the staged file into a table.



Example: create everything and load a CSV
-- 1. Create a database
CREATE DATABASE banking_db;

-- 2. Create a schema
CREATE SCHEMA banking_db.ingestion;

-- 3. Create a named internal stage
CREATE STAGE banking_db.ingestion.transaction_stage
    FILE_FORMAT = (
        TYPE = CSV
        SKIP_HEADER = 1
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    );

-- 4. Create the destination table
CREATE TABLE banking_db.ingestion.transactions (
    transaction_id VARCHAR,
    customer_id VARCHAR,
    amount NUMBER(10,2)
);


For a local CSV file, use SnowSQL or another supported client that can upload local files with PUT:
PUT file:///path/to/transactions.csv
    @banking_db.ingestion.transaction_stage
    AUTO_COMPRESS = TRUE;


Then load the staged file:
COPY INTO banking_db.ingestion.transactions
FROM @banking_db.ingestion.transaction_stage
FILE_FORMAT = (
    TYPE = CSV
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
);


The file path above is a placeholder; replace it with the path on the machine running your 
Snowflake client. The PUT command uploads a local file to an internal stage. For an external 
stage backed by S3, Azure, or Google Cloud Storage, you upload the file to that cloud storage 
location instead. 


Do you always need to create a named stage?
No. Snowflake also provides a user stage (@~) and a table stage (@%table_name) automatically. 
For a regular project involving multiple files or tables, though, a named stage is often easier 
to manage and share. 

Snowflake Documentation

The practical takeaway: You don't create micro-partitions or manage their placement yourself. 
For file ingestion, you generally need an accessible database and schema, a suitable stage, 
and a destination table—then upload and load the file.
*/