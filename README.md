> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*

# US Trade Tariff Impact Analysis (2022–2024)

### 📊 Evaluating the Real Impact of Trump-Era Tariffs Using U.S. Customs Data

---

##1 🧭 Overview  

This project investigates whether the **Trump-era tariffs** imposed on U.S. trade partners were economically justified or politically biased.  
Using official datasets from the **U.S. International Trade Commission (USITC)** for **2022–2024**, we measure trade balances between the United States and major countries, comparing actual trade data with applied tariff rates.

The analysis is structured around **three core disciplines**:

1. **Data Engineering & Cloud Services (AWS)** – End-to-end data ingestion, transformation, and orchestration using AWS S3, Glue, Lambda, and Redshift.  
2. **Data Warehousing & Data Modeling** – Building analytical models and a star schema optimized for large-scale querying and country/category-level insights.  
3. **Business Intelligence Development** – Creating interactive dashboards in AWS QuickSight and Power BI for deep-dive visualization and policy evaluation.

By combining these disciplines, the project delivers a complete data lifecycle — from raw data ingestion to cloud-based data warehousing and interactive visualization.  
Contextual enrichment (GDP, population, distance, COVID impact, migration) ensures a holistic interpretation of whether current tariff policies align with real trade dynamics.

---

##2 🎯 Objectives  

| Phase | Goal |
|-------|------|
| **Situation** | The Trump administration imposed tariffs on several nations to correct perceived trade deficits. This project evaluates whether those tariffs were economically justified. |
| **Task** | Analyze U.S. Customs import/export data (2022–2024), clean and model it through AWS-based ETL pipelines, and assess trade balances by country and HTS category. |
| **Action** | Extract over **800K trade records** from [USITC DataWeb](https://dataweb.usitc.gov/trade/search/GenImp/HTS), process them by year and trade type (Import/Export) at **HTS-6** detail, integrate economic and geographic data (GDP, distance, population), and model in **AWS Redshift** for BI analytics via **QuickSight**. |
| **Result (Preliminary Findings)** | The analysis highlights **post-COVID trade contraction** and **global production shifts**: <br> • Global trade volumes declined by ~18–22%. <br> • Manufacturing migration from China to India and ASEAN countries redistributed ~12–15% of U.S. imports. <br> • Market instability caused ~25% contraction in export predictability, reducing U.S. trade growth by ~20%. <br> • Tariff rates, however, remained mostly static, with some unjustified surcharges on surplus countries (e.g., Turkey 2024, UK 2023). <br><br>*(These figures serve as placeholders pending finalized Redshift + QuickSight analysis.)* |

---

##3 🧩 Data Architecture  

**AWS Services Used**
- Amazon S3 – Raw and processed data lake ('usa-customs-data-raw-salih-sezen')
- AWS Glue – ETL processing for Excel ingestion and transformation
- AWS Lambda – S3 file renaming and orchestration
- AWS Glue Crawler – Schema inference and Data Catalog
- Amazon Redshift – Analytical data warehouse
- AWS QuickSight – Visualization and dashboarding layer

---

##4 🧮 Data Engineering Workflow  

1. **Data Acquisition**
   - Source: [USITC Trade Data](https://dataweb.usitc.gov/trade/search/GenImp/HTS)
   - Pulled by year and trade type at HTS-6 granularity to prevent truncation.

2. **Data Preparation**
   - Automated file renaming using 'rename_s3_files.py' (boto3).
   - Excel reading, cleaning, and type normalization via AWS Glue.
   - Hierarchical 'dim_category' (HTS-2 → HTS-4 → HTS-6) creation.

3. **Data Modeling**
   - Star Schema:
     - 'fact_trade' – core transaction table (values, tariffs, countries, categories, years)
     - 'dim_country', 'dim_hts_category', 'dim_date', 'dim_direction'
   - Implemented in Amazon Redshift.

4. **Data Enrichment**
   - External data integrations:
     - 🌍 Country codes and geographic distances
     - 💰 GDP per capita, total GDP, growth rates
     - 🦠 COVID-19 mortality and recovery data
     - 🧳 Migration population and Green Card applications
     - 📈 Birth rates and credit indices

5. **Visualization & Insights**
   - PowerBI / QuickSight dashboards for:
     - Exports / Imports Analysis
	 - Trade Balance Analysis
     - Tariff impact correlation
     - Time-series anomaly detection
     - Geographic and category heatmaps

---

##5 🧠 Analytical Focus  

- **Policy Validity:** Were tariffs aligned with measurable deficits?  
- **Economic Fairness:** Which nations were over-tariffed despite U.S. surpluses?  
- **Supply Chain Shift:** How did post-COVID production relocation affect imports?  
- **Geoeconomic Factors:** GDP, population, and proximity correlations.  
- **Temporal Trends:** Category-wise recovery rates after 2020.

---

##6 🧰 Tech Stack  

| Layer | Technology |
|-------|-------------|
| Storage | AWS S3 |
| ETL / ELT | AWS Glue (PySpark / Python Shell) |
| Transformation | Pandas, PyArrow, Boto3 |
| Data Warehouse | Amazon Redshift |
| Automation | AWS Lambda, Glue Crawler |
| Visualization | Power BI, AWS QuickSight |
| Version Control | GitHub |

---

##7 📁 Repository Structure  

us-trade-tariff-analysis/
├── README.md
├── 1- documentation/
│ ├── 1-AWS-rules-and-informations.md
│ ├── 2-IAM-roles-and-policies-setup.md
│ ├── 3-S3-upload-guide.md
│ ├── 4-Glue-job-setup.md
│ ├── 5-Glue-crawler-setup.md
│ ├── 6-Redshift-setup-and-COPY-command.md
│ ├── 7-Data-warehousing-and-data-modelling.md
│ └── 8-PowerBI-QuickSight-connection-setup.md
├── 2- data-sources/USA Customs/
│ ├── Dataset1-2.jpg
│ ├── Definitions/
│ │ ├── Mapping Table.xlsx
│ ├── Exports/
│ │ ├── DataWeb-Query-Export (1-5).xlsx
│ ├── Imports/
│ │ └── DataWeb-Query-Export (6-10).xlsx
│ └── additional-datasources/
│ │ ├── dim_hts_category_short_preserve.xlsx
│ │ └── dim_country_clean.xlsx
├── 3- etl-scripts/
│ ├── rename_s3_files.py
│ ├── process_exports.py
│ ├── process_imports.py
│ ├── create_dim_hts_category.py
│ ├── (future)integrate_country_data.py
│ └── (future)integrate_tariff_data.py
├── 4- data-warehousing-and-data-modeling/
│ ├── create_staging_tables.sql
│ ├── create_fact_and_dim_tables.sql
│ ├── power_bi_star_data_model.jpg
│ ├── fact_trades.jpg
│ ├── dim_country.jpg
│ ├── dim_date.jpg
│ ├── dim_direction.jpg
│ └── dim_hts_category.jpg
├── 5-business-intelligence-and-analysis/
│ └── power_bi_star_data_model.jpg
└── 6-screen-shots
  ├── 1- S3-Region-Bucket-Folders.jpg
  ├── 2- IAM-roles-and-policies-setup.jpg
  ├── 3- S3-upload-data-sources.jpg
  ├── 4.1- Rename-files.jpg
  ├── 4.2- process_exports_excel.py.jpg
  ├── 4.3- process_imports_excel.py.jpg
  ├── 4.4- create_dim_hts_category.jpg
  ├── 5.1- export-import-crawler.jpg
  ├── 5.2- dim-hts-category-crawler.jpg
  ├── 8.1- Redshift-work-group-info.jpg
  ├── 8.2- QuickSight-connection.jpg
  ├── 8.3- PowerBI-connection.jpg
  ├── 8.4- PowerBI-connection-Redshift-dwh-tables.jpg
  └── 8.5- PowerBI-connection-Redshift-loading.jpg

---

##8 🧾 Future Enhancements  

- Incremental ETL automation using AWS Glue Workflows  
- ML-based anomaly detection for trade irregularities  
- Forecasting simulations for tariff policy changes  
- QuickSight API integration for real-time dashboard refresh  

---

##9 🏁 Result Summary *(Template and Draft)*  
---
# Note:
**The findings below are illustrative placeholders included for demonstration purposes.
**Final and authoritative results will be obtained after Part 2: Business Intelligence Dashboards are fully developed and the complete analytical evaluation is performed.**
**This section is currently in a template draft state.**
---

Preliminary findings indicate that **post-COVID global trade instability has significantly altered the importance of customs duties**:

- The most imported product group was Nuclear Reactors, Boilers, Machinery, and Mechanical Equipment, at $521 billion, while the most exported product group was Mineral Fuels, Oils, and Products, at $319 billion.  
- At the same time, we found that the tariff rates applied by the US remain excessively low for many countries, considering the US trade deficit with those countries.
- Global import/export contraction ≈ 20% overall.  
- Manufacturing relocation from China to India/ASEAN shifted ~12–15% of U.S. imports.  
- European market instability caused ~25% trade volatility, cutting U.S. export growth by ~20%.  
- Significant deviations were found in the fair calculation of tariffs, showing inconsistencies with real-world trade data.
- Power BI visualizations highlight regions where the US has a surplus (e.g., Turkey, United Kingdom, South Korea) and the high tariffs in these regions.
- Political instability in countries affects credit ratings ...
- Countries with a GDP per capita above $10,000 ...
- In countries with a population under 10 million and a birth rate below 10, ...
...

These placeholders will be replaced by **empirical Redshift results** and **BI-derived policy metrics** once final dashboards are deployed.

> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*
