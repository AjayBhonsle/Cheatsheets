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
| Performance Symptom | Primary Cause | Optimization Strategy |
| :--- | :--- | :--- |
| **Spilling to Remote Disk** | Memory overload during sorting/joining large datasets | Increase
warehouse size temporarily, pre-filter data upstream, or optimize join keys. |
| **High Queue Time** | Warehouse concurrency limits reached | Adjust `threads` in
`profiles.yml` or allocate a dedicated warehouse for dbt runs. |
| **Full Table Scans** | Missing partition or cluster keys | Implement cluster keys / partitioning on
high-cardinality filtering and join columns. |
| **Long View Execution** | Downstream dependencies querying heavy logic repeatedly | Switch
materialization from `view` to `table` or `incremental`. |
---
## 3. Incremental Models (`is_incremental()`)
Avoid processing historical data repeatedly by processing only new or updated records during
each dbt run.
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
Eliminate warehouse write I/O overhead by avoiding physical table or view creation for
lightweight intermediate transformations.
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
## 7. Performance Optimization Checklist
* **Filter Early:** Push `WHERE` filters and aggregations upstream into staging or intermediate
CTEs before performing joins across large tables.
* **Audit Materialization Types:** Set staging models as view or ephemeral, intermediate

models as ephemeral, and heavy facts or marts as incremental or table.
* **Consolidate CTEs:** Minimize redundant CTE chaining that limits query engine optimizer
rewrites.
* **Align Join Data Types:** Ensure join keys match data types across tables to prevent implicit
casting overhead during hash joins.
* **Check Source Freshness:** Run `dbt source freshness` before full execution to prevent
running downstream pipeline models on missing or stale raw data.