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