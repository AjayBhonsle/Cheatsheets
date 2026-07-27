------------------------------------------------------
-- Step 1: Create the log table with job_name
------------------------------------------------------
CREATE OR REPLACE TABLE execution_log (
    log_id INT,
    job_name VARCHAR(100),
    log_timestamp TIMESTAMP_NTZ,
    status VARCHAR(10)  -- 'SUCCESS' or 'FAILURE'
);

------------------------------------------------------
-- Step 2: Insert sample data
------------------------------------------------------
INSERT INTO execution_log (log_id, job_name, log_timestamp, status) VALUES
-- ETL_LOAD: 5 consecutive failures (SHOULD appear)
(1,  'ETL_LOAD', '2024-01-01 08:00:00', 'SUCCESS'),
(2,  'ETL_LOAD', '2024-01-01 09:00:00', 'SUCCESS'),
(3,  'ETL_LOAD', '2024-01-01 10:00:00', 'FAILURE'),
(4,  'ETL_LOAD', '2024-01-01 11:00:00', 'FAILURE'),
(5,  'ETL_LOAD', '2024-01-01 12:00:00', 'FAILURE'),
(6,  'ETL_LOAD', '2024-01-01 13:00:00', 'FAILURE'),
(7,  'ETL_LOAD', '2024-01-01 14:00:00', 'FAILURE'),
-- REPORT_GEN: 5 consecutive failures (SHOULD appear)
(8,  'REPORT_GEN', '2024-01-01 08:00:00', 'SUCCESS'),
(9,  'REPORT_GEN', '2024-01-01 09:00:00', 'FAILURE'),
(10, 'REPORT_GEN', '2024-01-01 10:00:00', 'FAILURE'),
(11, 'REPORT_GEN', '2024-01-01 11:00:00', 'FAILURE'),
(12, 'REPORT_GEN', '2024-01-01 12:00:00', 'FAILURE'),
(13, 'REPORT_GEN', '2024-01-01 13:00:00', 'FAILURE'),
-- DATA_SYNC: mixed results, no 5-streak (should NOT appear)
(14, 'DATA_SYNC', '2024-01-01 08:00:00', 'SUCCESS'),
(15, 'DATA_SYNC', '2024-01-01 09:00:00', 'FAILURE'),
(16, 'DATA_SYNC', '2024-01-01 10:00:00', 'FAILURE'),
(17, 'DATA_SYNC', '2024-01-01 11:00:00', 'SUCCESS'),
(18, 'DATA_SYNC', '2024-01-01 12:00:00', 'FAILURE'),
(19, 'DATA_SYNC', '2024-01-01 13:00:00', 'FAILURE'),
-- BACKUP_JOB: 3 consecutive failures then SUCCESS (should NOT appear)
--   This proves the query requires truly consecutive failures,
--   not just a count of failures in recent runs
(20, 'BACKUP_JOB', '2024-01-01 08:00:00', 'SUCCESS'),
(21, 'BACKUP_JOB', '2024-01-01 09:00:00', 'SUCCESS'),
(22, 'BACKUP_JOB', '2024-01-01 10:00:00', 'FAILURE'),
(23, 'BACKUP_JOB', '2024-01-01 11:00:00', 'FAILURE'),
(24, 'BACKUP_JOB', '2024-01-01 12:00:00', 'FAILURE'),
(25, 'BACKUP_JOB', '2024-01-01 13:00:00', 'SUCCESS'),
(26, 'BACKUP_JOB', '2024-01-01 14:00:00', 'FAILURE'),
(27, 'BACKUP_JOB', '2024-01-01 15:00:00', 'FAILURE');

SELECT * FROM execution_log;

------------------------------------------------------
-- Step 3: Find jobs with 5+ CONSECUTIVE failures
-- Gap-and-island: within each job, the difference between
-- overall row_number and failure-only row_number stays constant
-- for consecutive failure rows, forming a "group".
------------------------------------------------------
;
WITH ordered_log AS (
    SELECT log_id, job_name,
           log_timestamp,
           status,
           ROW_NUMBER() OVER (PARTITION BY job_name ORDER BY log_timestamp) AS rn,
           ROW_NUMBER() OVER (PARTITION BY job_name, status ORDER BY log_timestamp) AS status_rn
    FROM execution_log
    Order by 1
),
failure_groups AS (
    SELECT job_name,
           log_timestamp,
           rn - status_rn AS grp
    FROM ordered_log
    WHERE status = 'FAILURE'
) -- SELECT * FROM failure_groups;
,
streaks AS (
    SELECT job_name,
           grp,
           COUNT(*) AS consecutive_failures,
           MIN(log_timestamp) AS streak_start,
           MAX(log_timestamp) AS streak_end
    FROM failure_groups
    GROUP BY job_name, grp
     HAVING COUNT(*) >= 5
)
-- SELECT * FROM streaks;
SELECT job_name,
       consecutive_failures,
       streak_start,
       streak_end
FROM streaks
ORDER BY job_name, streak_start;


----------------------------------------------
-- ordered_log
--LOG_ID JOB_NAME	LOG_TIMESTAMP	STATUS	RN	STATUS_RN
--1	    ETL_LOAD	2024-01-01 08:00:00.000	SUCCESS	1	1
--2	    ETL_LOAD	2024-01-01 09:00:00.000	SUCCESS	2	2
--3	    ETL_LOAD	2024-01-01 10:00:00.000	FAILURE	3	1
--4	    ETL_LOAD	2024-01-01 11:00:00.000	FAILURE	4	2
--5	    ETL_LOAD	2024-01-01 12:00:00.000	FAILURE	5	3
--6	    ETL_LOAD	2024-01-01 13:00:00.000	FAILURE	6	4
--7	    ETL_LOAD	2024-01-01 14:00:00.000	FAILURE	7	5
--8	    REPORT_GEN	2024-01-01 08:00:00.000	SUCCESS	1	1
--9	    REPORT_GEN	2024-01-01 09:00:00.000	FAILURE	2	1
--10	REPORT_GEN	2024-01-01 10:00:00.000	FAILURE	3	2
--11	REPORT_GEN	2024-01-01 11:00:00.000	FAILURE	4	3
--12	REPORT_GEN	2024-01-01 12:00:00.000	FAILURE	5	4
--13	REPORT_GEN	2024-01-01 13:00:00.000	FAILURE	6	5
--14	DATA_SYNC	2024-01-01 08:00:00.000	SUCCESS	1	1
--15	DATA_SYNC	2024-01-01 09:00:00.000	FAILURE	2	1
--16	DATA_SYNC	2024-01-01 10:00:00.000	FAILURE	3	2
--17	DATA_SYNC	2024-01-01 11:00:00.000	SUCCESS	4	2
--18	DATA_SYNC	2024-01-01 12:00:00.000	FAILURE	5	3
--19	DATA_SYNC	2024-01-01 13:00:00.000	FAILURE	6	4
--20	BACKUP_JOB	2024-01-01 08:00:00.000	SUCCESS	1	1
--21	BACKUP_JOB	2024-01-01 09:00:00.000	SUCCESS	2	2
--22	BACKUP_JOB	2024-01-01 10:00:00.000	FAILURE	3	1
--23	BACKUP_JOB	2024-01-01 11:00:00.000	FAILURE	4	2
--24	BACKUP_JOB	2024-01-01 12:00:00.000	FAILURE	5	3
--25	BACKUP_JOB	2024-01-01 13:00:00.000	SUCCESS	6	3
--26	BACKUP_JOB	2024-01-01 14:00:00.000	FAILURE	7	4
--27	BACKUP_JOB	2024-01-01 15:00:00.000	FAILURE	8	5
----------------------------------------------
---filter_groups
-- JOB_NAME	    LOG_TIMESTAMP	          GRP
-- ETL_LOAD	    2024-01-01 10:00:00.000	  2
-- ETL_LOAD	    2024-01-01 11:00:00.000	  2
-- ETL_LOAD	    2024-01-01 12:00:00.000	  2
-- ETL_LOAD	    2024-01-01 13:00:00.000	  2
-- ETL_LOAD	    2024-01-01 14:00:00.000	  2
-- REPORT_GEN	2024-01-01 09:00:00.000	  1
-- REPORT_GEN	2024-01-01 10:00:00.000	  1
-- REPORT_GEN	2024-01-01 11:00:00.000	  1
-- REPORT_GEN	2024-01-01 12:00:00.000	  1
-- REPORT_GEN	2024-01-01 13:00:00.000	  1
-- DATA_SYNC	2024-01-01 09:00:00.000	  1
-- DATA_SYNC	2024-01-01 10:00:00.000	  1
-- DATA_SYNC	2024-01-01 12:00:00.000	  2
-- DATA_SYNC	2024-01-01 13:00:00.000	  2
-- BACKUP_JOB	2024-01-01 10:00:00.000	  2
-- BACKUP_JOB	2024-01-01 11:00:00.000	  2
-- BACKUP_JOB	2024-01-01 12:00:00.000	  2
-- BACKUP_JOB	2024-01-01 14:00:00.000	  3
-- BACKUP_JOB	2024-01-01 15:00:00.000	  3
----------------------------------------------
-- JOB_NAME	    GRP	CONSECUTIVE_FAILURES	STREAK_START	         STREAK_END
-- REPORT_GEN	1	5	                    2024-01-01 09:00:00.000	 2024-01-01 13:00:00.000
-- ETL_LOAD	    2	5	                    2024-01-01 10:00:00.000	 2024-01-01 14:00:00.000
----------------------------------------------
-- Final Result
-- JOB_NAME	    CONSECUTIVE_FAILURES	STREAK_START	         STREAK_END
-- ETL_LOAD	    5	                    2024-01-01 10:00:00.000	 2024-01-01 14:00:00.000
-- REPORT_GEN	5	                    2024-01-01 09:00:00.000	 2024-01-01 13:00:00.000
--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------



--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------

-- Step 3: Find jobs failing for the LAST 3 consecutive executions
-- Logic: rank each job's runs from most recent (rn=1) backwards.
--   Check if rn=1, rn=2, rn=3 are ALL 'FAILURE'.
--   Past failures that were followed by a success don't count.
WITH ranked AS (
    SELECT log_id, job_name,
           log_timestamp,
           status,
            ROW_NUMBER() OVER (PARTITION BY job_name ORDER BY log_timestamp DESC) AS rn,
            CASE WHEN status = 'FAILURE' THEN 1 ELSE 0 END AS IsFailure
    FROM execution_log
    QUALIFY (ROW_NUMBER() OVER (PARTITION BY job_name ORDER BY log_timestamp DESC) )<=3 -- Consider only last 3 rows
    ORDER BY 1 
)
SELECT job_name,
       SUM(IsFailure) AS trailing_consecutive_failures
FROM ranked
GROUP BY job_name
HAVING failure_count >= 3  -- ensure job has at least 3 runs




--------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------
-- NON Snowflake Script - Snowflake does not support INTERVAL arithmetic with ROW_NUMBER() directly.

WITH consecutive_groups AS (
    SELECT 
        job_id,
        run_date,
        status,
        run_date - INTERVAL '1 day' * ROW_NUMBER() OVER (PARTITION BY job_id, status ORDER BY run_date) AS grp
    FROM job_logs
)
SELECT DISTINCT job_id
FROM consecutive_groups
WHERE status = 'Failed'
GROUP BY job_id, grp
HAVING COUNT(*) >= 3;
