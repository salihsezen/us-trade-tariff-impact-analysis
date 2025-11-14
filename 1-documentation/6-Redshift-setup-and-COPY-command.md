> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*

# US Trade Tariff Impact Analysis (2022–2024)

### 📊 6- Redshift-setup-and-COPY-command.md  

This document describes the complete Redshift Serverless architecture, setup steps, schema design, table structures, COPY loading strategy, and DWH pipeline.  
Formatted as a single, monolithic markdown file with no code blocks inside to avoid splitting.

-------------------------------------------------------------------------------

#1. Redshift Serverless Configuration

• Region: us-east-1  
• Namespace: usa-customs-namespace 
• Workgroup: usa-customs-wg 
• Database: dev  
• Default IAM Role: usa-customs-redshift-role

Purpose: This IAM role gives Redshift permission to load Parquet files from S3 and optionally read Glue Catalog metadata.

Redshift is the single source of truth for all analytics.

-------------------------------------------------------------------------------

#2. Data Warehouse Layering

We follow a 3-layer architecture:

• staging → raw Parquet loads from S3  
• core → fact/dimension star schema  
• marts → business-friendly aggregated tables (optional)

Schemas created:
CREATE SCHEMA IF NOT EXISTS staging;  
CREATE SCHEMA IF NOT EXISTS core;  
CREATE SCHEMA IF NOT EXISTS marts;

OR 

We can give prefixes such as stg_trades,stg_hts_category,fact_trades,dim_hts_category to the tables.

-------------------------------------------------------------------------------

#3. Loading Data from S3 (COPY Strategy)

All data is loaded directly from Parquet files created by Glue.

**Scripts**
"create_staging_tables.sql"

-------------------------------------------------------------------------------


#4. Why Redshift Serverless?

• No cluster administration  
• Auto-scaling compute  
• Highly compatible with S3 + Parquet  
• Perfect for BI workloads  
• Pay-per-second pricing  
• Seamless integration with Glue and IAM  

-------------------------------------------------------------------------------

#5. Redshift Connection Details (for Power BI & QuickSight)

Host: <workgroup>.<account>.us-east-1.redshift-serverless.amazonaws.com  
Port: 5439  
Database: dev  
User: admin or readonly_user  

These details are used across all BI tools and SQL clients.

