## 1. String & Text Data Types

| Data Type | Max Size / Limit | Storage Behavior | Best Use Case & Production Notes |
| :--- | :--- | :--- | :--- |
| **`VARCHAR`** (or `STRING`, `TEXT`) | **16 MB** (Uncompressed) | Variable. Consumes space for actual characters stored. | Default choice for all text data. Length parameter e.g., `VARCHAR(50)` is **for validation only**; Snowflake does not save storage by limiting length. |
| **`CHAR`** (or `CHARACTER`) | **16 MB** | Synonym for `VARCHAR(1)`. Pads with spaces up to length 1. | Legacy compatibility. Avoid using for multi-character text data. |

> **Production Tip:** Always use generic `VARCHAR` or `STRING` without fixed lengths unless strictly enforcing schema constraints. Snowflake auto-compresses text columns efficiently on micro-partitions regardless of declared length.

---

## 2. Numeric Data Types

| Data Type | Precision / Scale | Storage Behavior | Best Use Case & Production Notes |
| :--- | :--- | :--- | :--- |
| **`NUMBER(p, s)`** (or `INT`, `DECIMAL`) | Max Precision: 38<br>Default: `NUMBER(38,0)` | **Exact numeric**. No rounding errors. | Financial data, currency, metrics, primary keys, and exact counting. |
| **`FLOAT`** (or `DOUBLE`, `REAL`) | 64-bit IEEE 754 floating point | **Approximate numeric**. Fast computations, subject to rounding inaccuracies. | Scientific calculations, ML features, coordinates, and continuous measurements where microscopic precision errors are acceptable. |

> **Production Tip:** Use `NUMBER(38, 0)` for IDs/Keys and `NUMBER(18, 4)` for currency/financials. Never use `FLOAT` for accounting or monetary calculations.

---

## 3. Date, Time & Timestamp Data Types

| Data Type | Description | Best Use Case & Production Notes |
| :--- | :--- | :--- |
| **`DATE`** | Holds YYYY-MM-DD. | Partitioning keys, daily reporting, birth dates. |
| **`TIME`** | Holds HH:MI:SS with fractional seconds. | Time-of-day analytics without dates (e.g., store operating hours). |
| **`TIMESTAMP_NTZ`** | **No Timezone**. Stores wall-clock time as provided. | Local system logs, staging tables where timezone conversion occurs downstream. |
| **`TIMESTAMP_LTZ`** | **Local Timezone**. Converts input to UTC for storage; displays in user's session timezone. | **Default choice for most ETL tables**. Best for global user dashboards and automatic timezone handling. |
| **`TIMESTAMP_TZ`** | **With Timezone**. Stores UTC time *along with* the explicitly provided UTC offset. | Compliance, audit logs, and transaction systems where preserving original transaction timezone is required. |

---

## 4. Semi-Structured Data Types

| Data Type | Operations | Storage & Optimization | Best Use Case |
| :--- | :--- | :--- | :--- |
| **`VARIANT`** | Holds JSON, Avro, ORC, Parquet, or XML up to 16 MB. | Snowflake extracts nested paths into virtual columns for columnar performance. | Raw staging layers, landing zone for API JSON payloads, dynamic attributes. |
| **`OBJECT`** | Key-Value pairs (like Python `dict`). | Fast lookup for key-based lookup data inside rows. | Storing key-value tags or configs within a record. |
| **`ARRAY`** | Ordered list of elements (like Python `list`). | Optimized for indexing and lateral flattening. | Multi-valued attributes (e.g., user tags, dynamic list of order IDs). |

> **Production Tip:** Use `FLATTEN()` to explode `ARRAY` or `VARIANT` data into relational rows for downstream analytical modeling.

---

## 5. Geospatial & Special Data Types

| Data Type | Representation | Best Use Case |
| :--- | :--- | :--- |
| **`GEOGRAPHY`** | Earth-as-a-sphere (WGS 84 ellipsoid). Calculates distances in meters using geodesic curves. | Real-world global spatial queries, delivery route distance calculations, store locator radii. |
| **`GEOMETRY`** | Flat, Euclidean (X, Y) Cartesian plane. | CAD drawings, game maps, indoor mapping, localized planar spatial analysis. |
| **`VECTOR`** | Array of floating-point numbers (128 to 4096 dimensions). | **Cortex Search / AI / LLM embeddings**. Used for similarity searches (`VECTOR_COSINE_SIMILARITY`). |
| **`BOOLEAN`** | `TRUE`, `FALSE`, or `NULL`. | Flags, active status, soft deletes. |
| **`BINARY`** | Raw binary data up to 16 MB. | Storing small files, images, or encrypted binary payloads.