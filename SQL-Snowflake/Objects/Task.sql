-- Setup Context
CREATE OR REPLACE DATABASE TASK_DEMO;
CREATE OR REPLACE SCHEMA PUBLIC;
USE DATABASE TASK_DEMO;
USE SCHEMA PUBLIC;

-- Create Warehouse (Tasks require an active warehouse to run)
-- CREATE OR REPLACE WAREHOUSE COMPUTE_WH WITH WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;

-- 1. SETUP SOURCE & TARGET TABLES

-- Standard Source & Target
CREATE OR REPLACE TABLE src_orders (order_id INT, status STRING, amount NUMBER(10,2));
CREATE OR REPLACE TABLE tgt_orders (order_id INT, status STRING, amount NUMBER(10,2));

-- Append-Only Source & Audit Target
CREATE OR REPLACE TABLE src_logs (log_id INT, msg STRING);
CREATE OR REPLACE TABLE tgt_logs_audit (log_id INT, msg STRING, ingested_at TIMESTAMP_NTZ);

-- Populate baseline data BEFORE streams
INSERT INTO src_orders VALUES (101, 'PENDING', 150.00), (102, 'COMPLETED', 200.00);
INSERT INTO src_logs VALUES (1, 'System Boot');

-- 2. CREATE STREAMS
CREATE OR REPLACE STREAM strm_orders ON TABLE src_orders;

-- Append-Only Stream for logs table
CREATE OR REPLACE STREAM strm_logs ON TABLE src_logs APPEND_ONLY = TRUE;

-- 3. CREATE STREAM-TRIGGERED TASKS (SCHEDULED PIPELINE)
-- Task 1: Root Task (Runs every 1 minute ONLY IF the orders stream has data)
CREATE OR REPLACE TASK tsk_process_orders
  WAREHOUSE = COMPUTE_WH
  SCHEDULE = '1 MINUTE'
  WHEN SYSTEM$STREAM_HAS_DATA('strm_orders')
AS
  MERGE INTO tgt_orders t
  USING strm_orders s
  ON t.order_id = s.order_id
  WHEN MATCHED AND s.metadata$action = 'DELETE' AND s.metadata$isupdate = FALSE THEN DELETE
  WHEN MATCHED AND s.metadata$action = 'INSERT' AND s.metadata$isupdate = TRUE THEN UPDATE SET t.status = s.status, t.amount = s.amount
  WHEN NOT MATCHED AND s.metadata$action = 'INSERT' THEN INSERT (order_id, status, amount) VALUES (s.order_id, s.status, s.amount);


-- Task 2: Child Task in DAG (Executes automatically AFTER tsk_process_orders completes)
CREATE OR REPLACE TASK tsk_process_logs
  WAREHOUSE = COMPUTE_WH
  AFTER tsk_process_orders
  WHEN SYSTEM$STREAM_HAS_DATA('strm_logs')
AS
  INSERT INTO tgt_logs_audit (log_id, msg, ingested_at)
  SELECT log_id, msg, CURRENT_TIMESTAMP()
  FROM strm_logs;


-- 4. RESUME TASKS (Tasks are created in SUSPENDED state by default)
-- Child tasks must be resumed before root tasks
ALTER TASK tsk_process_logs RESUME;
ALTER TASK tsk_process_orders RESUME;

-- 5. TEST AUTOMATION (Insert/Update Data to Trigger Tasks)
-- DML changes post-stream creation
INSERT INTO src_orders VALUES (103, 'PENDING', 350.00);
UPDATE src_orders SET status = 'SHIPPED' WHERE order_id = 101;
INSERT INTO src_logs VALUES (2, 'User Login Failed');

-- Check stream contents before task execution
SELECT * FROM strm_orders;
SELECT * FROM strm_logs;

-- (Wait 1 minute for the scheduled task execution...)

-- Execute Root Task manually for instant verification without waiting
EXECUTE TASK tsk_process_orders;


-- 6. VERIFY PIPELINE RESULTS & MONITORING
-- Check Target Tables
SELECT * FROM tgt_orders;
-- ORDER_ID	 STATUS	    AMOUNT
-- 101	     SHIPPED	150.00
-- 103	     PENDING	350.00

SELECT * FROM tgt_logs_audit;
--LOG_ID	MSG	                INGESTED_AT
--2	        User Login Failed	2026-07-22 07:22:05.792

-- Monitor Task Execution History
SELECT *
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    TASK_NAME => 'TSK_PROCESS_ORDERS',
    SCHEDULED_TIME_RANGE_START => DATEADD('HOUR', -1, CURRENT_TIMESTAMP())
));

-- 7. CLEANUP (Always suspend tasks when testing is finished)
ALTER TASK tsk_process_orders SUSPEND;
ALTER TASK tsk_process_logs SUSPEND;


--------------------- Optimized way to create TASK using USER_MANAGED/Serverless
-- Automatically resizes compute resources based on workload requirements.
-- Billed directly for exact compute used by task execution (more cost-effective for short/frequent runs).
-- 
CREATE OR REPLACE TASK tsk_managed_pipeline
  USER_TASK_MANAGED_INITIAL_WAREHOUSE_SIZE = 'XSMALL'
  SCHEDULE = '5 MINUTE'
  USER_TASK_TIMEOUT_MS = 1800000            -- 30 minute execution limit
  SUSPEND_TASK_AFTER_NUM_FAILURES = 3       -- Auto-suspend after 3 failures
  WHEN SYSTEM$STREAM_HAS_DATA('strm_orders')
AS
  MERGE INTO tgt_orders t USING strm_orders s ON t.order_id = s.order_id
  WHEN NOT MATCHED THEN INSERT (order_id, status, amount) VALUES (s.order_id, s.status, s.amount);

-- 3. Resume Task
ALTER TASK tsk_managed_pipeline RESUME;