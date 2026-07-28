# dbt Performance Tuning & Optimization Guide
A single, comprehensive reference covering performance diagnostics, materialization strategies,
concurrency tuning, and optimization checklists for dbt.
---
## 1. Performance Diagnostics & Profiling Workflow
When a dbt execution is running slowly or hitting resource limits, follow this diagnostic workflow:
* **Terminal Execution Logs:** Check model execution durations to identify the long-running
DAG nodes.
* **Data Warehouse Query Profile:** Analyze the query execution tree in Snowflake (or your
target warehouse) to pinpoint bottlenecks like disk spilling, missing cluster pruning, or expensive
join operations.
* **`target/run/` DML/DDL Review:** Inspect the exact compiled DDL/DML statement to evaluate
join strategies, CTE nesting depth, and filter placement.
* **DAG Lineage Analysis (`dbt docs generate`):** Review upstream model dependencies to
identify redundant joins or non-parallel execution paths.
---
## 2. Warehouse Bottleneck Matrix
| Performance Symptom | Primary Cause | Optimization & Testing Strategy |
| :--- | :--- | :--- |
| **Spilling to Remote Disk** | Memory overload during sorting/joining large datasets | Temporarily scale warehouse size up (or auto-scale), pre-filter data upstream, or optimize join keys to fit in-memory execution. |
| **High Queue Time** | Warehouse concurrency limits reached | Increase `threads` in `profiles.yml` up to the warehouse limit, or assign a dedicated, isolated warehouse for dbt orchestration runs. |
| **Full Table Scans** | Missing partition, cluster keys, or missing filter conditions | Configure `cluster_by` or `partition_by` on high-cardinality filter/join columns, and enforce date range filters in test/dev targets. |
| **Long View Execution** | Downstream dependencies repeatedly re-executing heavy view logic | Convert materialization from `view` to `table` or `incremental` to materialize results physically on storage. |
| **Expensive Test Execution** | Running un-filtered `unique` / `not_null` tests on multi-billion row tables | Add `where` clauses to test configs to scan only recent partitions (e.g., last 7 days) instead of full historical data. |
| **High Compilation Latency** | Massive DAG size, deep macro recursion, or excessive `adapter.get_relation` calls | Enable dbt state deferral (`--defer`), refactor deeply nested macros, and leverage dbt artifact parsing caches. |

---
## 3. Incremental Models (`is_incremental()`)
Avoid processing historical data repeatedly by processing only new or updated records during each dbt run.
```sql
{{
config(
materialized='incremental',
unique_key='order_id',
on_schema_change='sync_all_columns'
)
}}
select
order_id,
customer_id,
order_status,
order_date,
updated_at
from {{ ref('stg_orders') }}
{% if is_incremental() %}
-- Process only records updated since the last dbt execution
where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

---
## 4. Ephemeral Models (CTE Inlining)
Eliminate warehouse write I/O overhead by avoiding physical table or view creation for lightweight intermediate transformations.
```sql
{{
config(
materialized='ephemeral'
)
}}
select
order_id,
sum(amount) as total_amount
from {{ ref('stg_payments') }}
where status = 'success'
group by 1
```

---
## 5. Cluster Keys & Partitioning Configuration
Optimize physical data layout on disk to enable partition pruning and eliminate full table scans.
```sql
{{

config(
materialized='incremental',
unique_key='event_id',
cluster_by=['event_date', 'customer_id']
)
}}
select
event_id,
customer_id,
event_type,
event_date
from {{ ref('stg_events') }}
{% if is_incremental() %}
where event_date >= dateadd('day', -3, current_date())
{% endif %}
```

---
## 6. Concurrency & Parallel Execution (profiles.yml)
Maximize warehouse resource utilization by increasing thread parallelism to run non-dependent
DAG nodes concurrently.
```yaml
my_dbt_project:
target: dev
outputs:
dev:
type: snowflake
account: xyz12345.us-east-1
user: dbt_user
role: transformer_role
warehouse: dbt_wh
database: analytics_dev
schema: public
threads: 8 # Maximize concurrent execution of independent models
```

---
## 7. Some Performance Optimization Checklist
* **Filter Early:** Push `WHERE` filters and aggregations upstream into staging or intermediate CTEs before performing joins across large tables.

* **Audit Materialization Types:** Set staging models as view or ephemeral, intermediate
    * **Ephemeral (`materialized='ephemeral'`):** Reduce write I/O for lightweight intermediate models using CTE inlining.
    * **Incremental (`is_incremental()`):** Avoid reprocessing full historical data by processing only new/updated records.
    * **Tables/Views:** Keep staging as view or ephemeral, and reserve heavy facts/marts for table or incremental.

* **Choose the Right Incremental Strategy:** Match the `incremental_strategy` (`merge`, `delete+insert`, or `append`) to your warehouse engine and update patterns to reduce write amplification.

* **Consolidate CTEs:** Minimize redundant CTE chaining that limits query engine optimizer rewrites.

* **Align Join Data Types:** Ensure join keys match data types across tables to prevent implicit casting overhead during hash joins.

* **Check Source Freshness:** Run `dbt source freshness` before full execution to prevent running downstream pipeline models on missing or stale raw data.

* **Selectively Run Modified Models:** Use dbt state selection (`dbt run --select state:modified+`) in CI/CD to build only changed models and their downstream dependents.

* **Explicit Column Selection:** Avoid `SELECT *` in staging/intermediate models to minimize I/O overhead and leverage columnar warehouse scanning.

* **Optimize Window Functions:** Keep `PARTITION BY` and `ORDER BY` clauses consistent across window functions to avoid redundant data re-shuffling.

* **Configure Test Filters:** Apply `where` clauses to dbt data tests on large tables (e.g., test only the last 7 days) to avoid expensive full-table scans during validation.

* **Avoid `dbt seed` for Large Datasets:** Reserve `dbt seed` for small mapping tables (< 1,000 rows); use native bulk copy tools for larger static datasets.

* **Disable Heavy Tests in Production Runs:** Separate `dbt run` and `dbt test` in your CI/CD pipelines, or use `--exclude` flags to skip expensive data integrity tests during time-sensitive orchestration runs.

* **Leverage Ephemeral Testing (`store_failures`):** Use `store_failures: true` selectively during debugging so failed test records are saved to a schema without re-running full model transformations.

* **Benchmark Execution Durations:** Track model execution metrics via `target/manifest.json` and `target/run_results.json` over time to detect performance degradation early.

* **Limit Dry Run & Dev Data Scopes:** Use `{{ target.name }}` environments or `limit` blocks in Jinja (`{% if target.name == 'dev' %} where event_date >= current_date() - 7 {% endif %}`) to enforce minimal data volumes during testing.

* **Avoid Heavy Regex in Data Quality Tests:** Replace complex regex assertions with lookup tables or lightweight SQL string functions where possible to reduce CPU load during test execution.

* **Batch Unit Tests on Edge Cases:** Keep dbt Unit Tests (`models: ... unit_tests:`) focused strictly on complex logic edge cases using static mock inputs rather than running them against live warehouse tables.