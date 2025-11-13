> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*

# US Trade Tariff Impact Analysis (2022–2024)

### 📊 1- AWS-rules-and-informations.md
# AWS Rules and Informations  
_us-trade-tariff-analysis_

This document summarizes the **non-negotiable rules**, **initial setup decisions**, and **high-level service overview** for the `us-trade-tariff-analysis` project.

---

## 1. Global Rules for This Project

### 1.1 Single Region Rule

- **Region used:** `us-east-1`
- **Rule:** All core services **must live in the same region**:
  - S3 buckets that store raw/processed/curated data
  - AWS Glue (Jobs, Crawlers, Data Catalog)
  - Amazon Redshift (Serverless workgroup / namespace)
  - Amazon QuickSight (SPICE datasets connected to Redshift)
  - AWS Lambda functions
- **Why this matters:**
  - Avoids cross-region data transfer costs and latency
  - Ensures Glue → S3 → Redshift → QuickSight integrations work smoothly
  - Simplifies IAM permissions and troubleshooting

> If you ever create a new service for this project, **first check that it is in `us-east-1`.**

---

### 1.2 Naming Conventions

**General pattern:**
- Resources: `us-trade-<component>-<environment> or <name>`
- Example environments: `dev`, `prod` (for now single env = `dev` is enough)

**Examples used in this project:**
- **S3 bucket (raw + processed + curated):**  
  `usa-customs-data-raw-salih-sezen`
- **Redshift (Serverless):**
  - Workgroup: `us-trade-wg-dev`
  - Namespace: `us-trade-ns-dev`
  - Database: `us_trade_dwh`
- **Glue jobs:**  
  `process_exports_excel`, `process_imports_excel`, `create_dim_hts_category`
- **Glue crawlers:**  
  `combine_export_import_crawler`, `create_dim_hts_category-crawler`
- **IAM roles:**  
  `usa-customs-glue-role`, `usa-customs-redshift-role`, `usa-customs-lambda-role`, `aws-quicksight-service-role-v0`

> Keep names **short, descriptive and consistent**. Future you will thank you.

---

### 1.3 Folder / Layering Rules (Data Zones)

All data lives in **one S3 bucket** but is separated by **prefix (folder) and layer**.

**Bucket:**  
`usa-customs-data-raw-salih-sezen`

**Main layout:**

```text
usa-customs-data-raw-salih-sezen
└── USA Customs/
    ├── Definitions/
    │   ├── Mapping Table.xlsx
    ├── Exports/
    │   ├── 2022_USA_Exports_HTS6.xlsx
    │   ├── 2023_USA_Exports_HTS6.xlsx
    │   └── 2024_USA_Exports_HTS6.xlsx
    ├── Imports/
    │   ├── 2022_USA_Imports_HTS6.xlsx
    │   ├── 2023_USA_Imports_HTS6.xlsx
    │   └── 2024_USA_Imports_HTS6.xlsx
    └── processed/
            ├── Exports/year=(2022..2024)/(2022..2024)_USA_Exports_HTS6.parquet
            ├── Imports/year=(2022..2024)/(2022..2024)_USA_Imports_HTS6.parquet
            └── OtherDatasources/DimHTSCategory/part-0000.parquet

```

#### Rules

**Raw Zone**  
`/Exports` + `/Imports` → direct downloads, renamed via mapping table.

**Processed Zone/Curated Zone**  
`/Processed/parquet` → Glue ETL Parquet outputs (typed + cleaned). Fact/Dim outputs ready for Redshift DWH.

---

## 2. AWS Services Used (High-Level Overview)

---

### 2.1 AWS Identity and Access Management (IAM)

**Purpose:** Manage authentication & permissions for all services.

Used for:
- Glue Jobs → S3 + Glue Catalog  
- Redshift → S3 COPY permissions  
- QuickSight → Connect to Redshift & S3 (optional)  

**Principle:** Least privilege.

---

### 2.2 Amazon S3

Primary **data lake** of the project.

Stores:
- Raw USITC Trade Data  
- Mapping Table + reference files  
- Processed Parquet outputs from Glue  
- Curated Parquet Fact/Dim datasets  

**Key decisions:**
- One bucket, structured folders (raw → processed → curated)  
- Everything analytically queried → **Parquet**  

---

### 2.3 AWS Glue

Serverless **ETL + Metadata** service.

Used for:
- Python Shell or PySpark Glue Jobs:
  - Cleaning Excel files  
  - Converting to Parquet  
  - Building dim_hts_category  
  - Building dim_country  
- Glue Crawlers:
  - Automatically infer schema  
  - Populate Glue Data Catalog  

---

### 2.4 Amazon Redshift (Serverless)

**Main Data Warehouse (DWH)** of the project.

Used for:
- Storing Fact & Dimension tables:
  - fact_trades  
  - dim_hts_category  
  - dim_country  
  - dim_direction  
  - dim_date  
- Connecting BI tools (QuickSight, Power BI)  
- Performing analytic SQL at scale  

Data is loaded from S3 → Redshift using:
- COPY command  
- Or CTAS / MERGE patterns  

---

### 2.5 Amazon QuickSight

Used for **visualization** & dashboards.

Connects to:
- Redshift (`us_trade_dwh`)

Used for dashboards on:
- Trade Volume & Balance  
- Tariff Impact per Country & Category  
- YoY / MoM trends  
- Anomalies & comparisons  

---

### 2.6 AWS Lambda + CloudWatch + EventBridge

**Lambda** is optional for:
- Triggering Glue Jobs  
- Light ETL tasks  
- File validation or housekeeping  

**CloudWatch Logs** used for:
- Glue job logs  
- Lambda logs  
- Debugging  
- Monitoring ETL failures  

**Event Bridge** used for:
- Scheduling Glue Jobs (daily/weekly cron expressions)
- Triggering ETL pipelines when new files land in S3
- Routing Glue Job success/failure events to notifications or Lambda
- Creating event-driven orchestration across S3 → Glue → Redshift
- JSON event patterns to filter S3 PUT events, Glue job status events, etc.

---

