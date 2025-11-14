> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*

# US Trade Tariff Impact Analysis (2022–2024)

### 📊 4- Glue-job-setup.md 


This document explains every AWS Glue job used in this project, what each script does, all input/output locations, and why the entire pipeline depends heavily on Parquet conversion.  
Everything is written in one place to keep this guide simple, repeatable, and future-proof.

---

# 1. Purpose of AWS Glue in This Project

Glue is responsible for:

1. Renaming messy DataWeb excel files in S3 according to the Mapping Table.
2. Converting Excel → Parquet with proper schema and data types.
3. Cleaning, standardizing, and enriching transaction tables (Exports/Imports).
4. Producing dimension tables (dim_country, dim_hts_category).
5. Generating curated Parquet datasets ready for Redshift COPY.

We use Glue for ETL because:
- Excel is slow, inconsistent, and has no typed columns.
- Parquet is fast, compressed, columnar, and ideal for DWH ingestion.
- Glue automatically manages Spark compute at scale.
- Glue writes fully optimized output compatible with Redshift, Athena, and QuickSight.

All Glue jobs live in:

    "3- etl-scripts/"

---

# 2. Glue Jobs Overview (Full List)

The complete job list:

1. rename_s3_files.py  - lambda_function.py
2. process_exports_excel.py  
3. process_imports_excel.py 
4. create_dim_hts_category.py 
5. (future) build_fact_trades.py  
6. (future) generate_curated_layers.py

Below is the full explanation for each.

---

# 3. Job 1 — rename_s3_files.py  
(Type: Lambda function)

**Screen Shot:**
"6- screen-shots/4.1- Rename-files.jpg"

**Note:**
We could have used Glue ETL Job here, but we used Lambda to make a difference and automate this renaming process.

**Goal:**  
Rename the raw DataWeb files in S3 using `Mapping Table.xlsx` to produce consistent, meaningful filenames.

**Input:**  
    USA Customs/Definitions/Mapping Table.xlsx  
    USA Customs/Exports/DataWeb-Query-Export (X).xlsx  
    USA Customs/Imports/DataWeb-Query-Export (X).xlsx

**Output:**  
Clean names such as:

    USA Customs/Exports/2022_USA_Exports_HTS6.xlsx
    USA Customs/Imports/2024_USA_Imports_HTS6.xlsx

**Logic summary:**
- Read mapping table from S3.
- Determine whether file belongs to Exports or Imports based on RowNum.
- Rename S3 object (copy → delete original).
- Ensure file count consistency.

This job runs once per dataset upload cycle.

---

# 4. Job 2 — exports_to_parquet.py  
(Type: Glue Spark Job)

**Screen Shot:**
"6- screen-shots/4.2- process_exports_excel.py.jpg"

**Goal:**  
Convert raw export Excel files into clean Parquet tables.

**Input S3 folder:**  
    USA Customs/Exports/

**Output S3 folder:**  
    USA Customs/Processed/Exports/

**Process steps:**
- Read Excel sheets (“FAS Value” tab).
- Remove garbage header rows.
- Drop total/summary rows.
- Standardize column names:
  - `Country`, `Year`, `HTSNumber`, `Description`, `TradeValue`
- Add new column:
  - `Direction = 'Export'`
- Convert data types:
  - `Year → INT`
  - `HTSNumber → STRING`
  - `TradeValue → BIGINT/DECIMAL`
- Write Parquet partitioned by year:

      /year=2022/2022_USA_Exports_HTS6*.parquet

**Purpose in pipeline:**
- Acts as the base data for building fact_trades.
- Ensures transaction-level data is strongly typed.

---

# 5. Job 3 — process_imports_excel.py 
(Type: Glue Spark Job)

**Screen Shot:**
"6- screen-shots/4.3- process_imports_excel.py.jpg"

**Goal:**  
Same logic as exports job but for imports.

**Input S3 folder:**  
    USA Customs/Imports/

**Output S3 folder:**  
    USA Customs/Processed/Imports/

**Process steps:**
- Read Excel sheets (“General Customs Value” tab).
- Remove garbage header rows.
- Drop total/summary rows.
- Standardize column names:
  - `Country`, `Year`, `HTSNumber`, `Description`, `TradeValue`
- Add new column:
  - `Direction = 'Export'`
- Convert data types:
  - `Year → INT`
  - `HTSNumber → STRING`
  - `TradeValue → BIGINT/DECIMAL`
- Write Parquet partitioned by year:

      /year=2022/2022_USA_Imports_HTS6*.parquet

**Purpose in pipeline:**
- Acts as the base data for building fact_trades.
- Ensures transaction-level data is strongly typed.

---

# 6. Job 4 — create_dim_hts_category.py  
(Type: Glue Spark Job)

**Screen Shot:**
"6- screen-shots/4.4- create_dim_hts_category.jpg"

**Goal:**  
Create the hierarchical HTS dimension table (HTS2 → HTS4 → HTS6).

**Inputs:**  
Placed under Definitions:

    HTS2 Description.xlsx
    HTS4 Description.xlsx
    (optionally HTS6 mapping sheets if available)

**Output S3 folder:**  
    USA Customs/processed/OtherDatasources/DimHTSCategory/

**Process steps:**
- Read HTS2, HTS4, HTS6 mapping sheets.
- Clean column names.
- Extract “latest description” per HTS code.
- Build hierarchy:
  - hts6_key
  - hts6
  - hts6_description_latest
  - hts4
  - hts4_description_latest
  - hts2
  - hts2_description_latest
- Deduplicate by hts6.
- Write final Parquet dataset.
		/part-0000.parquet
		
**Purpose:**  
Used by Redshift to build `core.dim_hts_category` and enable drill-down from high → low HTS levels.

---

# 7. Why We Use Parquet (Critical Design Decision)

This entire project depends on converting Excel → Parquet because:

- **Columnar format** → only reads necessary columns.
- **Compression** → 5x–10x smaller than Excel/CSV.
- **Strong typing** → numeric/date types preserved correctly.
- **Redshift-native** → COPY supports Parquet directly.
- **Glue/Athena-native** → Glue Crawlers detect proper schema.
- **BI performance** → QuickSight and Power BI benefit from typed warehouse tables.

Without Parquet, Redshift COPY would be slow, error-prone, and expensive.

---

# 8. Summary

Glue provides the ETL backbone of this project:

- Raw Excel files renamed → standardized filenames  
- Transactional data → cleaned, typed Parquet  
- HTS category hierarchy → fully built  
- Country dimension → enriched and standardized  
- All outputs → downstream Redshift COPY-ready Parquet  

This ensures a professional, reliable, high-performance data lake → DWH → BI pipeline.

---
