/*
This script loads using SCD Type 2 and Type 3 with example
 */

-- ============================================================================
-- 1. SETUP: TABLES, INITIAL BASELINE & SEPARATE STREAMS
-- ============================================================================

CREATE OR REPLACE TRANSIENT TABLE src_employee (
    emp_id INT,
    name STRING,
    department STRING
);

-- Seed baseline data directly into the source table
INSERT INTO src_employee VALUES 
    (1, 'Alice', 'HR'),
    (2, 'Bob', 'IT'),
    (3, 'Charlie', 'Finance'),
    (4, 'David', 'Sales');

-- Create TWO dedicated streams so each SCD logic can consume independently
CREATE OR REPLACE STREAM str_employee_changes_scd2 ON table src_employee;
CREATE OR REPLACE STREAM str_employee_changes_scd3 ON table src_employee;

-- Create Target Table for SCD Type 2 (Using '9999-12-31' for active rows)
CREATE OR REPLACE TRANSIENT TABLE tgt_scd2 (
    emp_id INT, name STRING, department STRING, is_current BOOLEAN, start_date DATE, end_date DATE
);
INSERT INTO tgt_scd2 VALUES 
    (1, 'Alice', 'HR', TRUE, '2026-01-01', '9999-12-31'),
    (2, 'Bob', 'IT', TRUE, '2026-01-01', '9999-12-31'),
    (3, 'Charlie', 'Finance', TRUE, '2026-01-01', '9999-12-31'),
    (4, 'David', 'Sales', TRUE, '2026-01-01', '9999-12-31');

-- Create Target Table for SCD Type 3
CREATE OR REPLACE TRANSIENT TABLE tgt_scd3 (
    emp_id INT, name STRING, current_department STRING, previous_department STRING
);
INSERT INTO tgt_scd3 VALUES 
    (1, 'Alice', 'HR', NULL),
    (2, 'Bob', 'IT', NULL),
    (3, 'Charlie', 'Finance', NULL),
    (4, 'David', 'Sales', NULL);


-- ============================================================================
-- 2. SIMULATE DEMO MUTATIONS (Insert, Update, Delete)
-- ============================================================================

-- INSERT 2 new employees
INSERT INTO src_employee VALUES 
    (5, 'Eve', 'Marketing'),
    (6, 'Frank', 'Support');

-- UPDATE 2 existing employees' departments
UPDATE src_employee SET department = 'Data Science' WHERE emp_id = 1; 
UPDATE src_employee SET department = 'DevOps' WHERE emp_id = 2;       

-- DELETE 2 existing employees
DELETE FROM src_employee WHERE emp_id = 3; 
DELETE FROM src_employee WHERE emp_id = 4; 

SELECT * FROM str_employee_changes_scd2;
SELECT * FROM str_employee_changes_scd3;

-- ============================================================================
-- 3. EXECUTE SCD TYPE 2 MERGE (Consumes str_employee_changes_scd2)
-- ============================================================================
MERGE INTO tgt_scd2 t
USING (
    SELECT emp_id, name, department, 
           CASE WHEN METADATA$ACTION = 'DELETE' THEN 'DELETE' ELSE 'UPDATE' END AS stream_action
    FROM str_employee_changes_scd2
    WHERE (METADATA$ACTION = 'INSERT' AND METADATA$ISUPDATE = TRUE)
       OR (METADATA$ACTION = 'DELETE' AND METADATA$ISUPDATE = FALSE) 
    
    UNION ALL
    
    SELECT emp_id, name, department, 'INSERT' AS stream_action
    FROM str_employee_changes_scd2
    WHERE METADATA$ACTION = 'INSERT'
) s
ON t.emp_id = s.emp_id 
AND t.is_current = TRUE 
AND s.stream_action IN ('UPDATE', 'DELETE')
WHEN MATCHED THEN
  UPDATE SET t.is_current = FALSE, t.end_date = CURRENT_DATE()
WHEN NOT MATCHED AND s.stream_action = 'INSERT' THEN
  INSERT (emp_id, name, department, is_current, start_date, end_date)
  VALUES (s.emp_id, s.name, s.department, TRUE, CURRENT_DATE(), '9999-12-31');

SELECT * FROM tgt_scd2;

-- ============================================================================
-- 4. EXECUTE SCD TYPE 3 MERGE (Consumes str_employee_changes_scd3)
-- ============================================================================
MERGE INTO tgt_scd3 t
USING (
    SELECT emp_id, name, department, METADATA$ACTION AS stream_action
    FROM str_employee_changes_scd3 
    WHERE NOT (METADATA$ACTION = 'DELETE' AND METADATA$ISUPDATE = TRUE)
) s
ON t.emp_id = s.emp_id
WHEN MATCHED AND s.stream_action = 'DELETE' THEN
  UPDATE SET t.current_department = 'DELETED', t.previous_department = t.current_department
WHEN MATCHED AND s.stream_action = 'INSERT' AND t.current_department != s.department THEN
  UPDATE SET t.previous_department = t.current_department, t.current_department = s.department
WHEN NOT MATCHED AND s.stream_action = 'INSERT' THEN
  INSERT (emp_id, name, current_department, previous_department)
  VALUES (s.emp_id, s.name, s.department, NULL);

SELECT * FROM tgt_scd3;

-- ============================================================================
-- 5. VERIFY FINAL TARGET RESULTS & STREAMS (Both streams are now empty)
-- ============================================================================
SELECT * FROM tgt_scd2 ORDER BY emp_id, start_date;
SELECT * FROM tgt_scd3 ORDER BY emp_id;
