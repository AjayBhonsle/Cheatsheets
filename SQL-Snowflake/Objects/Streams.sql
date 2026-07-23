-- Setup Context
CREATE OR REPLACE DATABASE STREAM_DEMO;
CREATE OR REPLACE SCHEMA PUBLIC;
USE DATABASE STREAM_DEMO;
USE SCHEMA PUBLIC;

-- 1. STANDARD STREAM DEMO

-- Create Source & Target Tables
CREATE OR REPLACE TEMPORARY TABLE src_standard (id INT, val STRING);
CREATE OR REPLACE TEMPORARY TABLE tgt_standard (id INT, val STRING);

-- Insert initial data BEFORE stream creation (This baseline won't show in stream)
INSERT INTO src_standard VALUES 
  (1, 'Baseline 1'),
  (2, 'Baseline 2'),
  (3, 'Baseline 3');

-- Create STANDARD Stream
-- Operations logged: Inserts, updates, and deletes (including table truncates).
-- Standard tables, dynamic tables, Apache Iceberg™ tables, directory tables, and views
CREATE OR REPLACE STREAM strm_standard ON TABLE src_standard;

-- Create APPEND-Only Stream 
-- It entirely ignores updates and deletions. This reduces processing overhead, making it highly efficient for continuous Extract, Load, Transform (ELT) pipelines.
-- Standard tables, directory tables, and views
CREATE OR REPLACE STREAM strm_append ON TABLE src_standard APPEND_ONLY = TRUE;


-- DML Operations AFTER stream creation
INSERT INTO src_standard VALUES (4, 'New Row 4'), (5, 'New Row 5');
UPDATE src_standard SET val = 'Updated Baseline 2' WHERE id = 2;
DELETE FROM src_standard WHERE id = 3;


-- View Stream Contents (Shows changes for IDs 2, 3, 4, and 5)
SELECT * FROM strm_standard;
/*
ID	VAL	                 METADATA$ACTION  METADATA$ISUPDATE	METADATA$ROW_ID
2	Updated Baseline 2	 INSERT	          TRUE	            d9b3354d9a4a9b2a6356218b289a9f86f9461d5e
2	Baseline 2	         DELETE	          TRUE	            d9b3354d9a4a9b2a6356218b289a9f86f9461d5e
3	Baseline 3	         DELETE	          FALSE	            be9ea2fccc7a65cc5ff4888140fbdc0966c81512
4	New Row 4	         INSERT	          FALSE	            1881dfd1880d5eccedd60f8611d5bb1fab350987
5	New Row 5	         INSERT	          FALSE	            1672d0f289cb7dcb1f2b10a0a2c18f207204d48d
*/

-- View Stream Contents (Only captures INSERTS for IDs 300 and 400)
SELECT * FROM strm_append;
/*
ID	VAL	             METADATA$ACTION	 METADATA$ISUPDATE	METADATA$ROW_ID
4	New Row 4	    INSERT	             FALSE	            4c5382526edc2fb98c2c8115345831341d86bcaa
5	New Row 5	    INSERT	             FALSE	            86620100355a0f2b10d14baaa3132f1bbf7984ec
*/

-- Consume Stream into Target
MERGE INTO tgt_standard t
USING strm_standard s
ON t.id = s.id
WHEN MATCHED AND s.metadata$action = 'DELETE' AND s.metadata$isupdate = FALSE THEN DELETE
WHEN MATCHED AND s.metadata$action = 'INSERT' AND s.metadata$isupdate = TRUE THEN UPDATE SET t.val = s.val
WHEN NOT MATCHED AND s.metadata$action = 'INSERT' THEN INSERT (id, val) VALUES (s.id, s.val);

-- Verify Target State
SELECT * FROM tgt_standard;
-------------------------------------------------

CREATE OR REPLACE TEMPORARY TABLE tgt_append (id INT, val STRING);

-- Consume Stream to Target
INSERT INTO tgt_append (id, val)
SELECT id, val FROM strm_append;

-- Verify Target State
SELECT * FROM tgt_append;

------------------------------------------------------------------------------ VIEW Streams
-- Supported Views: Works on standard views and secure views (not materialized views).
-- Underlying Tables: All underlying tables must be in the same database.
-- Stream Type: Streams on views are always Standard streams (Append-Only is not supported on views).
-- Inner and Cross join supports no LEFT or RIGHT joins, and no aggregation functions.
-- Union/Union All not supported.

-- 1. Create Base Source Table
CREATE OR REPLACE TABLE src_employees (
    emp_id INT,
    emp_name STRING,
    department STRING,
    salary NUMBER(10,2)
);

-- Baseline Data
INSERT INTO src_employees VALUES 
  (1, 'Alice', 'Engineering', 90000),
  (2, 'Bob', 'HR', 60000);

-- 2. Create View filtering specific data
CREATE OR REPLACE VIEW v_engineering_employees AS
SELECT emp_id, emp_name, salary
FROM src_employees
WHERE department = 'Engineering';

-- 3. Create Stream ON THE VIEW
CREATE OR REPLACE STREAM strm_view_eng ON VIEW v_engineering_employees;

-- 4. Perform DML on Base Table
INSERT INTO src_employees VALUES (3, 'Charlie', 'Engineering', 95000); -- Picked up by stream
INSERT INTO src_employees VALUES (4, 'David', 'Sales', 70000);        -- IGNORED (Filtered out by view)
UPDATE src_employees SET salary = 98000 WHERE emp_id = 1;             -- Picked up by stream

-- 5. Query Stream (Only shows changes relevant to the Engineering view definition)
SELECT * FROM strm_view_eng;

-- EMP_ID  EMP_NAME	SALARY	    METADATA$ROW_ID	                            METADATA$ACTION	 METADATA$ISUPDATE
-- 1	   Alice	98000.00	652c8e670093460decffd67b1b7c22d99e196949	INSERT	         TRUE
-- 3	   Charlie	95000.00	713a62cb3677057cb08a336eef9bddf39c2124db	INSERT	         FALSE
-- 1	   Alice	90000.00	652c8e670093460decffd67b1b7c22d99e196949	DELETE	         TRUE

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------

--- INSERT-ONLY STREAM - can be create on External tables or Iceberge tables

-- Create Stage & External Table pointing to public sample data
-- External tables and Apache Iceberg™ table
-- New row insertions specifically for cloud-backed structures


-- Option A: Official Snowflake Documentation Sample Bucket
CREATE OR REPLACE STAGE my_s3_stage 
  URL='s3://snowflake-docs/';

--alternative 's3://noaa-gsod-pds/2023/';

CREATE OR REPLACE FILE FORMAT my_pipe_format
  TYPE = 'CSV'
  FIELD_DELIMITER = '|'
  SKIP_HEADER = 1;

-- Create External Table pointing to public S3 stage
CREATE OR REPLACE EXTERNAL TABLE ext_src_table (
    file_name STRING AS METADATA$FILENAME,
    row_number INT AS METADATA$FILE_ROW_NUMBER,
    id INT AS (VALUE:c1::INT),
    name STRING AS (VALUE:c2::STRING)
)
LOCATION = @my_s3_stage
FILE_FORMAT = 'my_pipe_format';

-- SELECT top 10 * FROM ext_src_table WHERE FILE_NAME = 'tutorials/dataloading/contacts1.csv';

-- Populate initial metadata BEFORE creating the stream
ALTER EXTERNAL TABLE ext_src_table REFRESH;

-- Create Insert-Only Stream on External Table
CREATE OR REPLACE STREAM strm_insert_only ON EXTERNAL TABLE ext_src_table INSERT_ONLY = TRUE;

-- Target Table
CREATE OR REPLACE TEMPORARY TABLE tgt_external_data (col1 STRING);

-- Refresh metadata to detect newly registered/added files
ALTER EXTERNAL TABLE ext_src_table REFRESH;

-- View Stream Contents
SELECT * FROM strm_insert_only;

-- Consume Stream into Native Table
INSERT INTO tgt_external_data (col1)
SELECT col1 FROM strm_insert_only WHERE metadata$action = 'INSERT';

-- Verify Target Data
SELECT * FROM tgt_external_data;





