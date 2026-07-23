/********************************************************************************
* THE ULTIMATE SNOWFLAKE BIBLE: 35+ COMPONENTS (PURPOSE & BEST PRACTICES)
* Formatted for: Quick reference, Deep-dive Interview Prep, and Easy Copy-Paste
********************************************************************************/

-- ==============================================================================
-- SECTION 1: NETWORK & SECURITY (The Foundation)
-- ==============================================================================

-- 1. NETWORK RULE
-- Purpose: Defines allowed/blocked network locations (IPs or Domains).
-- Best Practice: Use the 'EGRESS' mode to strictly control where Snowflake sends data.
CREATE OR REPLACE NETWORK RULE api_egress_rule
  TYPE = HOST_PORT VALUE_LIST = ('api.service.com:443') MODE = EGRESS;

-- 2. SECURITY INTEGRATION
-- Purpose: Enables external authentication (OAuth, SAML, SCIM).
-- Best Practice: Always use for API integrations to avoid handling raw client secrets in code.
CREATE OR REPLACE SECURITY INTEGRATION oauth_generic_int
  TYPE = API_AUTHENTICATION AUTH_TYPE = OAUTH2
  OAUTH_CLIENT_ID = 'id' OAUTH_CLIENT_SECRET = 'secret'
  OAUTH_TOKEN_ENDPOINT = 'https://api.service.com/token' ENABLED = TRUE;

-- 3. SECRET
-- Purpose: Securely stores credentials (Passwords, OAuth Tokens, or Private Keys).
-- Best Practice: Never hardcode strings; fetch these inside UDFs or Procedures.
CREATE OR REPLACE SECRET api_oauth_secret
  TYPE = OAUTH2 API_AUTHENTICATION = oauth_generic_int REFRESH_TOKEN = 'token';

-- 4. EXTERNAL ACCESS INTEGRATION
-- Purpose: The "bridge" allowing Snowflake code to hit the public internet.
-- Best Practice: Limit access to specific UDFs/Roles to prevent unauthorized data exfiltration.
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION api_bridge_int
  ALLOWED_NETWORK_RULES = (api_egress_rule)
  ALLOWED_AUTHENTICATION_SECRETS = (api_oauth_secret) ENABLED = TRUE;


-- ==============================================================================
-- SECTION 2: STORAGE & INTEROPERABILITY
-- ==============================================================================

-- 5. STORAGE INTEGRATION
-- Purpose: Connects Snowflake to S3/GCS/Azure without using secret keys.
-- Best Practice: Use IAM Roles for "Keyless" authentication—most secure method.
CREATE OR REPLACE STORAGE INTEGRATION s3_int
  TYPE = EXTERNAL_STAGE STORAGE_PROVIDER = 'S3' ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123:role/snowflake'
  STORAGE_ALLOWED_LOCATIONS = ('s3://my-bucket/');

-- 6. EXTERNAL VOLUME
-- Purpose: Required for Iceberg tables to define where data lives in your cloud.
-- Best Practice: Separate volumes for different environments (Dev vs Prod).
CREATE OR REPLACE EXTERNAL VOLUME iceberg_vol
   STORAGE_LOCATIONS = ((NAME = 's3-us' STORAGE_PROVIDER = 'S3'
   STORAGE_BASE_URL = 's3://iceberg-bucket/' STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123:role/iceberg'));

-- 7. EXTERNAL STAGE
-- Purpose: Points to a specific folder/path in your cloud storage.
-- Best Practice: Always use a Storage Integration rather than CREDENTIALS.
CREATE OR REPLACE STAGE ext_stage_s3 URL = 's3://my-bucket/' STORAGE_INTEGRATION = s3_int;

-- 8. INTERNAL STAGE
-- Purpose: Stores files locally within Snowflake managed storage.
-- Best Practice: Use 'Named Stages' for repeatable ETL; avoid 'Table Stages' for production.
CREATE OR REPLACE STAGE my_int_stage DIRECTORY = (ENABLE = TRUE);


-- ==============================================================================
-- SECTION 3: FILE FORMATS & ADVANCED TABLES
-- ==============================================================================

-- 9-14. FILE FORMATS (CSV, JSON, PARQUET, AVRO, ORC, XML)
-- Purpose: Defines how Snowflake should parse files in a stage.
-- Best Practice: Set 'TRIM_SPACE = TRUE' and 'NULL_IF' to ensure clean data ingestion.
CREATE OR REPLACE FILE FORMAT fmt_csv TYPE = 'CSV' SKIP_HEADER = 1 TRIM_SPACE = TRUE;
CREATE OR REPLACE FILE FORMAT fmt_json TYPE = 'JSON' STRIP_OUTER_ARRAY = TRUE;

-- 15. EXTERNAL TABLE
-- Purpose: Queries data directly from S3/Azure without importing it.
-- Best Practice: Use for "cold" data or discovery; for performance, load into standard tables.
CREATE OR REPLACE EXTERNAL TABLE ext_table_raw (id INT AS (value:id::int))
  LOCATION = @ext_stage_s3 FILE_FORMAT = fmt_json;

-- 16. ICEBERG TABLE
-- Purpose: High-performance table that stores data in open Apache Iceberg format.
-- Best Practice: Use for "Data Lakehouse" architectures where other tools (Spark) need access.
CREATE OR REPLACE ICEBERG TABLE iceberg_sales
  EXTERNAL_VOLUME = 'iceberg_vol' CATALOG = 'SNOWFLAKE'
  BASE_LOCATION = 'sales/' AS SELECT * FROM source_table;


-- ==============================================================================
-- SECTION 4: INGESTION PIPELINES (Snowpipe)
-- ==============================================================================

-- 17. NOTIFICATION INTEGRATION
-- Purpose: Sends/Receives alerts for Snowpipe errors or Task completions.
-- Best Practice: Configure for 'OUTBOUND' to SNS/PubSub to alert engineering teams of failures.
CREATE OR REPLACE NOTIFICATION INTEGRATION pipe_notif
  TYPE = QUEUE NOTIFICATION_PROVIDER = 'AWS_SNS' ENABLED = TRUE
  AWS_SNS_TOPIC_ARN = 'arn:aws:sns:...' AWS_SNS_ROLE_ARN = 'arn:aws:iam:...';

-- 18. SNOWPIPE
-- Purpose: Automated, serverless, near-real-time data loading.
-- Best Practice: Use 'AUTO_INGEST = TRUE' to trigger loads the second a file hits S3.
CREATE OR REPLACE PIPE raw_pipe AUTO_INGEST = TRUE ERROR_INTEGRATION = pipe_notif
  AS COPY INTO target_table FROM @ext_stage_s3 FILE_FORMAT = (FORMAT_NAME = fmt_json);


-- ==============================================================================
-- SECTION 5: DATA PIPELINE ORCHESTRATION (CDC & Logic)
-- ==============================================================================

-- 19. STREAM
-- Purpose: Tracks Change Data Capture (CDC) - inserts, updates, deletes on a table.
-- Best Practice: Consume streams in Tasks to ensure "Exactly-Once" processing.
CREATE OR REPLACE STREAM landing_stream ON TABLE raw_landing;

-- 20. TASK
-- Purpose: Schedules SQL logic or Stored Procedures (Standard Orchestration).
-- Best Practice: Use 'WHEN SYSTEM$STREAM_HAS_DATA' to save costs and only run if needed.
CREATE OR REPLACE TASK tsk_process
  WAREHOUSE = 'COMPUTE_WH' SCHEDULE = '5 MINUTE'
  WHEN SYSTEM$STREAM_HAS_DATA('landing_stream')
  AS INSERT INTO silver SELECT * FROM landing_stream;

-- 21. TASK GRAPH (DAG)
-- Purpose: Creates dependencies (Parent -> Child tasks).
-- Best Practice: Use 'AFTER' clause to build complex pipelines instead of one giant script.
CREATE OR REPLACE TASK tsk_child AFTER tsk_process AS CALL sp_aggregate_data();

-- 22. DYNAMIC TABLE
-- Purpose: Declarative pipeline—you write the SELECT, Snowflake manages the refresh.
-- Best Practice: Use for JOINs and Aggregations; it replaces complex Stream/Task logic.
CREATE OR REPLACE DYNAMIC TABLE gold_analytics
  TARGET_LAG = '1 MINUTE' WAREHOUSE = 'COMPUTE_WH'
  AS SELECT category, SUM(amount) FROM silver GROUP BY 1;


-- ==============================================================================
-- SECTION 6: PERFORMANCE & OPTIMIZATION
-- ==============================================================================

-- 23. CLUSTERING KEY
-- Purpose: Physically re-orders data to speed up range/filter queries on large tables.
-- Best Practice: Only cluster tables over 1TB; use columns frequently used in WHERE/JOIN.
ALTER TABLE large_fact_table CLUSTER BY (transaction_date, region_id);

-- 24. SEARCH OPTIMIZATION SERVICE (SOS)
-- Purpose: Speeds up "point-lookups" (finding 1 row in a billion).
-- Best Practice: High cost; only use for highly selective columns like Email or UUID.
ALTER TABLE massive_table ADD SEARCH OPTIMIZATION ON EQUALITY(user_email);

-- 25. MATERIALIZED VIEW
-- Purpose: Pre-computes and stores a query result for speed.
-- Best Practice: Use only on slowly-changing data to avoid high background refresh costs.
CREATE OR REPLACE MATERIALIZED VIEW mv_summary AS SELECT date, sum(val) FROM fact GROUP BY 1;


-- ==============================================================================
-- SECTION 7: GOVERNANCE & PRIVACY
-- ==============================================================================

-- 26. MASKING POLICY
-- Purpose: Redacts or obfuscates PII (emails, SSNs) based on user role.
-- Best Practice: Apply at the 'Tag' level to automatically mask PII across the account.
CREATE OR REPLACE MASKING POLICY email_mask AS (val string) RETURNS string ->
  CASE WHEN CURRENT_ROLE() = 'ADMIN' THEN val ELSE '****@****.com' END;

-- 27. ROW ACCESS POLICY
-- Purpose: Filters rows based on the user's attributes (e.g., Sales Rep sees only their region).
-- Best Practice: Use a mapping table inside the policy for dynamic, scalable security.
CREATE OR REPLACE ROW ACCESS POLICY region_policy AS (reg string) RETURNS BOOLEAN ->
  CURRENT_ROLE() = 'ADMIN' OR reg = 'NORTH_AMERICA';

-- 28. TAGGING
-- Purpose: Assigns metadata to objects for classification or cost tracking.
-- Best Practice: Tag everything with 'Cost_Center' and 'Data_Privacy_Level'.
CREATE OR REPLACE TAG cost_center;
ALTER TABLE sales_table SET TAG cost_center = 'finance';


-- ==============================================================================
-- SECTION 8: EXTENSIBILITY & LOGIC
-- ==============================================================================

-- 29. UDF (User Defined Function)
-- Purpose: Custom scalar or table logic (Python/SQL/Java).
-- Best Practice: Use for logic that returns a value; keep them deterministic for speed.
CREATE OR REPLACE FUNCTION py_clean(s string) RETURNS string LANGUAGE PYTHON
  RUNTIME_VERSION = '3.8' HANDLER = 'run' AS $$
def run(s): return s.strip().lower()
$$;

-- 30. STORED PROCEDURE
-- Purpose: Administrative tasks, DDL operations, or complex multi-step logic.
-- Best Practice: Use for "DO" operations (Truncate, Load, Grant); UDFs for "SELECT".
CREATE OR REPLACE PROCEDURE pr_truncate_load() RETURNS STRING LANGUAGE SQL
  AS $$ BEGIN TRUNCATE TABLE temp; RETURN 'Success'; END; $$;


-- ==============================================================================
-- SECTION 9: DATA LIFECYCLE & COST CONTROL
-- ==============================================================================

-- 31. ZERO-COPY CLONE
-- Purpose: Creates an instant copy of a database/table without storage cost.
-- Best Practice: Use for 'Blue-Green' deployments or safe testing of production data.
CREATE OR REPLACE TABLE dev_table CLONE prod_table;

-- 32. TIME TRAVEL
-- Purpose: Restores data from the past (up to 90 days).
-- Best Practice: Set 'DATA_RETENTION_TIME_IN_DAYS = 0' for transient tables to save cost.
SELECT * FROM table_name AT(OFFSET => -3600); -- 1 hour ago

-- 33. FAIL-SAFE
-- Purpose: 7-day emergency recovery by Snowflake (starts after Time Travel ends).
-- Best Practice: Remember this is non-configurable and costs storage; avoid for temp tables.

-- 34. RESOURCE MONITOR
-- Purpose: Sets hard credit limits on Warehouses to prevent overspending.
-- Best Practice: Set at least two triggers: one to Notify (80%) and one to Suspend (100%).
CREATE OR REPLACE RESOURCE MONITOR global_limit CREDIT_QUOTA = 100
  TRIGGERS ON 100 PERCENT DO SUSPEND;

-- 35. SEQUENCE
-- Purpose: Generates unique, auto-incrementing numbers.
-- Best Practice: Use 'NOORDER' for performance in high-concurrency inserts.
CREATE OR REPLACE SEQUENCE global_id_seq NOORDER;

