# Executive Blueprint: Ad-Driven Customer Revenue & Profit Data Pipeline

A comprehensive, non-technical architectural blueprint designed to demonstrate to leadership and panel stakeholders how raw advertising, e-commerce, and financial data are safely ingested, validated, transformed, and monitored to deliver true Customer Revenue and Net Profit insights.

---

## 1. Core Architecture Pattern: The Medallion Architecture

To guarantee accuracy, auditability, and clear separation of concerns, the pipeline follows the industry-standard **Medallion Architecture**. Raw data moves through three progressive refinement stages before reaching executive dashboards.

```
+------------------+      +--------------------+      +-----------------------+      +---------------------------+
|   DATA SOURCES   | ---> |   BRONZE LAYER     | ---> |     SILVER LAYER      | ---> |        GOLD LAYER         |
| (Ads, Store, ERP)|      | (Raw Landing Zone) |      | (Cleaned & Attributed)|      | (Business Metrics & Profit) |
+------------------+      +--------------------+      +-----------------------+      +---------------------------+
```

---

## 2. End-to-End Pipeline Architecture & Flow

```
+-----------------------------------------------------------------------------------+
| 1. DATA INGESTION & SCHEDULING LAYER                                              |
|    • Frequency: Scheduled Batch Ingestion (e.g., Daily at 1:00 AM UTC)            |
|    • Sources: Digital Ad Platforms, E-Commerce Storefront, ERP / Finance          |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 2. RAW LANDING ZONE & PRE-LOAD VALIDATION (Bronze Layer)                         |
|    • Operational Checks: File arrival checks, schema matching, corruption tests   |
|    • Storage: Raw, immutable historical log entries for auditing                  |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 3. CLEANSING, ATTRIBUTION & IN-FLIGHT VALIDATION (Silver Layer)                   |
|    • Quality Rules: Key completeness, non-negative checks, duplicate removal      |
|    • Exception Handling: Failed records routed to Dead-Letter Queue (DLQ)         |
|    • Business Logic: Ad-to-order attribution & Net Profit calculations            |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 4. BUSINESS AGGREGATION LAYER (Gold Layer)                                        |
|    • Processing: Pre-aggregated metrics by Campaign, Channel, Region, and Date     |
|    • KPIs: Revenue, Cost, ROAS, CAC, Customer Lifetime Value (LTV), Net Profit    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 5. SERVING, MONITORING & GOVERNANCE LAYER                                         |
|    • Reporting: Executive Power BI / Tableau Dashboards                          |
|    • Observability: Real-time SLA tracking, volume anomaly & failure alerts       |
|    • Governance: Role-Based Access Control (RBAC) & PII masking                   |
+-----------------------------------------------------------------------------------+
```

---

## 3. Detailed Stage Breakdown

### Stage 1: Data Ingestion & Execution Frequency
Data collection operates on automated schedules managed by centralized workflow orchestrators:
* **Digital Ad Platforms (Google Ads, Meta Ads, TikTok, etc.):** * *Data Collected:* Daily campaign impressions, ad clicks, tracking parameters, and marketing spend.
  * *Frequency:* **Hourly or Daily Batch Sync** (aligns with API rate limits and spend reporting windows).
* **E-Commerce / Sales System:**
  * *Data Collected:* Order IDs, customer profiles, line items, transaction amounts, payment dates, and UTM click tags.
  * *Frequency:* **Daily Batch at Midnight** (captures the complete prior day's order volume).
* **ERP / Finance Systems:**
  * *Data Collected:* Product Cost of Goods Sold (COGS), warehouse fulfillment costs, shipping fees, and merchant processing charges.
  * *Frequency:* **Daily or Weekly Sync** (matches accounting update cycles).

---

### Stage 2: Raw Landing Zone & Pre-Load Validation (Bronze Layer)
* **Immutable Audit Trail:** Holds raw data feeds exactly as received from source systems without modification.
* **Pre-Load Validation Checks:**
  * **File Arrival Check:** Verifies expected files arrive within specified SLA time windows.
  * **Structural Integrity:** Confirms file format (CSV/JSON/Parquet), encoding, and header structures match expected parameters.
  * **File Size Anomalies:** Flags unexpectedly small (0 KB) or abnormally large files before processing begins.

---

### Stage 3: Cleansing, Attribution & In-Flight Validation (Silver Layer)
Raw data is cleansed, validated, and enriched into structured, business-usable information:
* **In-Flight Data Validation Rules:**
  * **Null & Identity Verification:** Enforces that Order IDs, Customer IDs, and Ad Click IDs are present.
  * **Boundary Checks:** Rejects impossible values (e.g., negative ad spend, negative order amounts, future transaction dates).
  * **Deduplication:** Ensures repeated ad clicks or duplicate order webhook receipts are stripped out.
* **Error Handling & Dead-Letter Queue (DLQ):**
  * Records failing quality checks are quarantined into a **Dead-Letter Queue (DLQ)** for investigation without stopping the main pipeline flow.
* **Core Business Calculations:**
  * **Customer Identity Matching:** Links marketing tracking parameters (e.g., `UTM` tags or Click IDs) to customer profiles and purchase history.
  * **Attribution Modeling:** Connects specific ad campaigns to customer purchases.
  * **Net Profit Calculation:** Subtracts product base costs, shipping, merchant fees, and allocated ad spend from gross order revenue:

$$	ext{Net Profit} = 	ext{Order Revenue} - (	ext{Product Base Cost} + 	ext{Shipping/Fees} + 	ext{Attributed Ad Spend})$$

---

### Stage 4: Business Aggregation (Gold Layer)
Data is summarized into business-ready reporting models optimized for fast dashboard performance:
* **Return on Ad Spend (ROAS):** Evaluates campaign profitability by comparing ad-generated revenue against ad spend.
* **Customer Acquisition Cost (CAC):** Measures marketing spend divided by the number of new customers acquired per channel.
* **Customer Lifetime Value (LTV):** Tracks long-term revenue and net profit generated by ad-acquired customers over time.
* **Net Profit Margin (%):** Calculates the percentage of gross ad revenue converted into true profit after all operational expenses.

---

### Stage 5: Serving, Monitoring & Governance

#### A. Pipeline Monitoring & Observability
* **Execution Audit Logging:** Tracks pipeline start/end times, total records read, records successfully loaded, and records sent to DLQ.
* **Volume Anomaly Detection:** Triggers alerts if daily order or ad spend volume drops/spikes by more than $20\%$ compared to rolling averages.
* **Real-time Alerting:** Sends instant notifications (Slack, Microsoft Teams, PagerDuty, or Email) to data engineers and business owners upon job failure or SLA breach.

#### B. Data Governance & Security
* **Role-Based Access Control (RBAC):** Marketing teams view campaign metrics and ROAS, while executive and finance teams access detailed margin and profit figures.
* **PII Masking:** Customer names, emails, and phone numbers are dynamically masked or hashed to comply with privacy regulations (GDPR/CCPA).





## 3. Detailed Pipeline Stage Breakdown

### Stage 1: Data Ingestion & Execution Frequency
Data collection operates on automated schedules managed by centralized workflow orchestrators:
* **Digital Ad Platforms (Google Ads, Meta Ads, TikTok, etc.):**
  * *Data Collected:* Daily campaign impressions, ad clicks, tracking parameters, and marketing spend.
  * *Frequency:* **Hourly or Daily Batch Sync** (aligns with API rate limits and spend reporting windows).
* **E-Commerce / Sales System:**
  * *Data Collected:* Order IDs, customer profiles, line items, transaction amounts, payment dates, and UTM click tags.
  * *Frequency:* **Daily Batch at Midnight** (captures the complete prior day's order volume).
* **ERP / Finance Systems:**
  * *Data Collected:* Product Cost of Goods Sold (COGS), warehouse fulfillment costs, shipping fees, and merchant processing charges.
  * *Frequency:* **Daily or Weekly Sync** (matches accounting update cycles).

---

### Stage 2: Raw Landing Zone & Pre-Load Validation (Bronze Layer)
* **Immutable Audit Trail:** Holds raw data feeds exactly as received from source systems without modification.
* **Pre-Load Validation Checks:**
  * **File Arrival Check:** Verifies expected files arrive within specified SLA time windows.
  * **Structural Integrity:** Confirms file format (CSV/JSON/Parquet), encoding, and header structures match expected parameters.
  * **File Size Anomalies:** Flags unexpectedly small (0 KB) or abnormally large files before processing begins.

---

### Stage 3: Cleansing, Attribution & In-Flight Validation (Silver Layer)
Raw data is cleansed, validated, and enriched into structured, business-usable information:
* **In-Flight Data Validation Rules:**
  * **Null & Identity Verification:** Enforces that Order IDs, Customer IDs, and Ad Click IDs are present.
  * **Boundary Checks:** Rejects impossible values (e.g., negative ad spend, negative order amounts, future transaction dates).
  * **Deduplication:** Ensures repeated ad clicks or duplicate order webhook receipts are stripped out.
* **Error Handling & Dead-Letter Queue (DLQ):**
  * Records failing quality checks are quarantined into a **Dead-Letter Queue (DLQ)** for investigation without stopping the main pipeline flow.
* **Core Business Calculations:**
  * **Customer Identity Matching:** Links marketing tracking parameters (e.g., `UTM` tags or Click IDs) to customer profiles and purchase history.
  * **Attribution Modeling:** Connects specific ad campaigns to customer purchases.
  * **Net Profit Calculation:** Subtracts product base costs, shipping, merchant fees, and allocated ad spend from gross order revenue:

$$\text{Net Profit} = \text{Order Revenue} - (\text{Product Base Cost} + \text{Shipping/Fees} + \text{Attributed Ad Spend})$$

---

### Stage 4: Business Aggregation (Gold Layer)
Data is summarized into business-ready reporting models optimized for fast dashboard performance:
* **Return on Ad Spend (ROAS):** Evaluates campaign profitability by comparing ad-generated revenue against ad spend.
* **Customer Acquisition Cost (CAC):** Measures marketing spend divided by the number of new customers acquired per channel.
* **Customer Lifetime Value (LTV):** Tracks long-term revenue and net profit generated by ad-acquired customers over time.
* **Net Profit Margin (%):** Calculates the percentage of gross ad revenue converted into true profit after all operational expenses.

---

## 4. Production Best Practices & Architectural Considerations

### 1. Handling Ad Attribution Delays (Rolling Lookback Windows)
* **The Challenge:** Digital ad platforms routinely update conversion figures and attribution data retroactively up to 7–28 days after an ad click occurs. Furthermore, a customer might click an ad today but complete an order 5 days later.
* **Best Practice:** Implement a **7-day or 14-day rolling re-processing window** in the Silver layer. Daily scheduled runs re-read and update the last 14 days of ad spend and attribution logic to ensure late conversions are accurately captured without doing a full historical reload.

### 2. Late-Arriving Data, Cancellations & Order Returns
* **The Challenge:** Customers cancel orders, request refunds, or initiate returns days after the initial transaction, which inflates gross revenue figures if unhandled.
* **Best Practice:** Capture refund/return events from the e-commerce system and model them using **Slowly Changing Dimensions (SCD Type 2)** or transactional delta tables (`MERGE` statements). Update order status flags and reflect negative financial adjustments in net revenue metrics.

### 3. Currency Standardizing
* **The Challenge:** Ad platforms may charge spend in USD or EUR, while customers place orders in local currencies (INR, GBP, etc.).
* **Best Practice:** Convert all monetary amounts (Ad Spend, Gross Revenue, COGS, Shipping Fees) to a standardized **Base Reporting Currency** using daily official exchange rate lookup tables applied at the exact transaction or spend timestamp.

### 4. Schema Drift Protection & PII Governance
* **Schema Drift Protection:** Store raw API responses as semi-structured payloads (`VARIANT` in Snowflake or JSON in S3) in the Bronze layer. Parse required fields downstream dynamically to protect ingestion pipelines from breaking due to schema changes.
* **PII Governance:** Hash sensitive customer identity attributes (e.g., lowercased emails) using deterministic `SHA-256` hashing during ingestion to allow cross-system joining while protecting customer privacy.

---

## 5. Granular Pipeline Health & Observability Dashboard

A dedicated operational dashboard designed for Data Engineering and Operations teams to track execution health, source connectivity, data reconciliation, and SLA performance.

---

### Dashboard Section A: High-Level Pipeline Operational KPIs

| KPI / Metric | Description & Granularity | Target SLA / Threshold | Operational Impact |
| :--- | :--- | :--- | :--- |
| **Pipeline Overall Health Status** | Real-time visual indicator (`GREEN`, `YELLOW`, `RED`) summarizing end-to-end status for the day. | `GREEN` (100% core DAGs completed) | Provides instant status visibility for on-call data engineers and stakeholders. |
| **Daily Execution Date & Schedule** | Tracks execution date, trigger day/time vs. actual completion timestamp. | Completed prior to 06:00 AM business SLA | Ensures downstream BI dashboards are fully refreshed before business hours. |
| **End-to-End Runtime Duration** | Total elapsed processing time across all stages (Ingestion $\rightarrow$ Bronze $\rightarrow$ Silver $\rightarrow$ Gold). | $< 45$ minutes total duration | Flags performance degradation, resource bottlenecks, or unexpected query queuing. |
| **Active Source System Count** | Number of external data sources connected vs. expected for the current day (e.g., 5 of 5 connected). | 100% active connectivity | Prevents incomplete downstream business reporting caused by silent API failures. |

---

### Dashboard Section B: Granular Source-to-Target Data Reconciliation Matrix

Tracks exact row counts and variance across every pipeline layer for the day to guarantee zero unexplained data drop-off.

| Source System / Layer | Source Record Count | Ingested Count (Bronze) | Cleaned Count (Silver) | Target Count (Gold Aggregated) | Variance (%) | Health Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Google Ads API** | 142,500 | 142,500 | 142,100 | 1,250 (Aggregated Campaign Rows) | 0.00% | `HEALTHY` |
| **Meta Ads API** | 98,200 | 98,200 | 97,950 | 850 (Aggregated Campaign Rows) | 0.00% | `HEALTHY` |
| **E-Commerce Orders** | 45,310 | 45,310 | 45,280 | 45,280 (Order Fact Rows) | 0.00% | `HEALTHY` |
| **ERP Base Product Costs** | 12,000 | 12,000 | 12,000 | 12,000 (Product Dimension Rows) | 0.00% | `HEALTHY` |
| **Shipping & Gateway Fees** | 45,310 | 45,310 | 45,100 | 45,100 (Fee Fact Rows) | -0.46% (Refunds) | `WARNING` |

---

### Dashboard Section C: Data Quality, Exception & Anomaly Metrics

| Metric | Description / Calculation | Warning Threshold | Automated Action Triggered |
| :--- | :--- | :--- | :--- |
| **Dead-Letter Queue (DLQ) Count** | Records failing schema or validation rules (e.g., null primary keys, corrupt payloads). | $> 0.5\%$ of daily raw volume | Quarantines failed rows and sends an immediate Slack/Teams alert with payload samples. |
| **Volume Anomaly Ratio** | Compares current day row count against 30-day rolling average for the same day of the week. | Variance $> \pm 20\%$ | Triggers automated alert and holds downstream table refresh for engineering approval. |
| **Unattributed Revenue Rate** | Percentage of daily completed orders that could not be mapped to any marketing campaign/UTM. | $> 5.0\%$ of daily order volume | Flags records for review by marketing analytics team. |
| **Duplicate Event Count** | Number of repeated webhook notifications or duplicate API payloads identified and removed. | $> 1.0\%$ of raw count | Alerts on upstream source retries or duplicated webhook broadcasts. |
"""