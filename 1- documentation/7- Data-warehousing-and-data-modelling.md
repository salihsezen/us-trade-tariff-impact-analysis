> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*

# US Trade Tariff Impact Analysis (2022–2024)

### 📊 7- Data-warehousing-and-data-modelling.md 

This document describes the complete Redshift Serverless architecture, setup steps, schema design, table structures, COPY loading strategy, and DWH pipeline.  
Formatted as a single, monolithic markdown file with no code blocks inside to avoid splitting.

-------------------------------------------------------------------------------
#1. Data Warehouse Layering

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

#2. Dimension Tables (core schema)

3.1 dim_country  
Columns:  
country_key (identity), country_name, country_code, region, subregion, latest_tariff_rate, optional macro indicators like gdp_per_capita or population.  
Purpose: Enriched metadata for country-level analytics.

3.2 dim_hts_category  
Columns:  
hts6_key (identity), hts6, hts6_description_latest, hts4, hts4_description_latest, hts2, hts2_description_latest,  infoyear.
Purpose: Product hierarchy supporting HTS2→HTS4→HTS6 drilldown.

3.3 dim_direction  
Static lookup with values Import, Export.  
direction_key and direction_name.

3.4 dim_date  
Columns: date_key (YYYYMMDD), full_date, calendar_year, calendar_quarter, calendar_month, month_name,day_of_month,day_of_week,day_name.  
We use the year-end (e.g. 20221231) as date_key to prevent duplication.

-------------------------------------------------------------------------------

#3. Fact Table Design (core.fact_trades)

Fact grain: Country × HTS6 × Year × Direction  

Columns:  
trade_id (identity), country_key, hts6_key, direction_key, date_key, trade_value.

trade_value is the FAS Value(Exports) and General Customs Value(Imports) from USITC.

-------------------------------------------------------------------------------

#4. Loading Data from Staging Tables

**Scripts**
"Data-warehousing-and-data-modelling.sql"


-------------------------------------------------------------------------------


#5. Summary

Redshift contains the final star-schema layer:

• fact_trades  
• dim_country  
• dim_hts_category  
• dim_direction  
• dim_date  

And the pipeline is:

Raw Excel in S3 → Glue Transform → Parquet Processed → Redshift Staging → Redshift Core → BI Layer (Power BI / QuickSight)

This is the project’s authoritative data warehouse architecture.

-------------------------------------------------------------------------------
