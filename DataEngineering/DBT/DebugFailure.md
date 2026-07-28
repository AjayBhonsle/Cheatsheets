# dbt Troubleshooting & Debugging Guide

A comprehensive, single-reference guide for identifying, debugging, and resolving model, test, and execution failures in dbt.

---

## 1. Failure Debugging Workflow

When `dbt build` or `dbt run` fails, follow this 4-step diagnostic flow:

1. **Terminal Output:** Check the terminal summary for the exact model name, failure cause, and file paths.
2. **target/compiled/:** Inspect raw SELECT queries with all Jinja, macros, and ref() functions resolved.
3. **Warehouse Query History:** Execute compiled SQL directly in your data warehouse (e.g., Snowflake) to reproduce row-level errors or compilation bugs.
4. **target/run/ & logs/dbt.log:** Review the exact DDL/DML statements (CREATE TABLE, MERGE, test SELECT COUNT(*)) executed on the database, or check verbose execution trace logs in dbt.log.

> Note on dbt.log: Log entries are continuously appended across runs (not overwritten). Once dbt.log reaches ~10MB, dbt automatically rotates it to dbt.log.1 and starts a fresh log file. Use --debug to output maximum log details.

---

## 2. Complete Execution & Code Reference

### Terminal Output Example

10:15:02  1 of 3 START sql incremental model analytics.fct_orders .................. [RUN]
10:15:04  1 of 3 ERROR creating sql incremental model analytics.fct_orders ......... [ERROR in 2.12s]
10:15:04  
10:15:04  Completed with 1 error and 0 warnings:
10:15:04  
10:15:04  Database Error in model fct_orders (models/marts/fct_orders.sql)
10:15:04    001003 (42000): SQL compilation error:
10:15:04    invalid identifier 'ORD_DATE'
10:15:04    compiled code at target/compiled/my_project/models/marts/fct_orders.sql
10:15:04  
10:15:04  Done. PASS=0 WARN=0 ERROR=1 SKIP=0 TOTAL=1

---

## 3. Compiled SQL vs Executed DDL (target/compiled vs target/run)

### Source File Example (models/marts/fct_orders.sql)

select 
    order_id, 
    customer_id, 
    ord_date 
from {{ ref('stg_orders') }}

---

### target/compiled/

* What it contains: Pure SELECT SQL queries.
* What dbt does: Resolves all Jinja templates, macros, environment variables, and ref() / source() functions into plain SQL.
* Purpose: Allows you to isolate and test the core business logic or query performance without executing DDL/DML on your warehouse.

#### Model Compiled Code (target/compiled/my_project/models/marts/fct_orders.sql)

select 
    order_id, 
    customer_id, 
    ord_date 
from raw_db.analytics_staging.stg_orders

#### Test Compiled Code (target/compiled/my_project/models/marts/schema.yml/not_null_fct_orders_order_id.sql)

select order_id
from raw_db.analytics_marts.fct_orders
where order_id is null

---

### target/run/

* What it contains: The complete DDL/DML wrapper statements (CREATE TABLE, CREATE VIEW, INSERT INTO, MERGE, or test assertions).
* What dbt does: Wraps the compiled SELECT query into the exact SQL statement sent to your data warehouse based on the model's materialization type.
* Purpose: Helps debug warehouse-level permissions, table creation issues, schema locks, or incremental merge logic.

#### Model Executed DDL (target/run/my_project/models/marts/fct_orders.sql)

create or replace table raw_db.analytics_marts.fct_orders as (
    select 
        order_id, 
        customer_id, 
        ord_date 
    from raw_db.analytics_staging.stg_orders
);

#### Test Executed Wrapper (target/run/my_project/models/marts/schema.yml/not_null_fct_orders_order_id.sql)

select
    count(*) as failures,
    count(*) != 0 as should_warn,
    count(*) != 0 as should_error
from (
    select order_id
    from raw_db.analytics_marts.fct_orders
    where order_id is null
) dbt_internal_test

---

### Key Differences Summary

| Feature | target/compiled/ | target/run/ |
| :--- | :--- | :--- |
| SQL Type | Pure SELECT statements | Full DDL / DML (CREATE, MERGE, INSERT) |
| Jinja Resolution | Resolves ref(), source(), & macros | Resolves materialization wrappers |
| Best Used For | Debugging SQL syntax & business logic | Debugging database execution & privileges |

---

## 4. Run SQL in Warehouse

Paste and execute the compiled SQL directly in your Snowflake query editor to see the exact row-level or syntax error.

---

## 5. Re-run with Debug

Run dbt build --select model_name --debug to output detailed logs in terminal and inspect logs/dbt.log.