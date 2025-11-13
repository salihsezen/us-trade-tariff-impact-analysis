> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*

# US Trade Tariff Impact Analysis (2022–2024)

### 📊 Evaluating the Real Impact of Trump-Era Tariffs Using U.S. Customs Data

---

## 🧭 Overview  

This project investigates whether the **Trump-era tariffs** imposed on U.S. trade partners were economically justified or politically biased.  
Using official datasets from the **U.S. International Trade Commission (USITC)** for **2022–2024**, we measure trade balances between the United States and major countries, comparing actual trade data with applied tariff rates.

The analysis is structured around **three core disciplines**:

1. **Data Engineering & Cloud Services (AWS)** – End-to-end data ingestion, transformation, and orchestration using AWS S3, Glue, Lambda, and Redshift.  
2. **Data Warehousing & Data Modeling** – Building analytical models and a star schema optimized for large-scale querying and country/category-level insights.  
3. **Business Intelligence Development** – Creating interactive dashboards in AWS QuickSight and Power BI for deep-dive visualization and policy evaluation.

By combining these disciplines, the project delivers a complete data lifecycle — from raw data ingestion to cloud-based data warehousing and interactive visualization.  
Contextual enrichment (GDP, population, distance, COVID impact, migration) ensures a holistic interpretation of whether current tariff policies align with real trade dynamics.

---

## 🎯 Objectives  

| Phase | Goal |
|-------|------|
| **Situation** | The Trump administration imposed tariffs on several nations to correct perceived trade deficits. This project evaluates whether those tariffs were economically justified. |
| **Task** | Analyze U.S. Customs import/export data (2022–2024), clean and model it through AWS-based ETL pipelines, and assess trade balances by country and HTS category. |
| **Action** | Extract over **800K trade records** from [USITC DataWeb](https://dataweb.usitc.gov/trade/search/GenImp/HTS), process them by year and trade type (Import/Export) at **HTS-6** detail, integrate economic and geographic data (GDP, distance, population), and model in **AWS Redshift** for BI analytics via **QuickSight**. |
| **Result (Preliminary Findings)** | The analysis highlights **post-COVID trade contraction** and **global production shifts**: <br> • Global trade volumes declined by ~18–22%. <br> • Manufacturing migration from China to India and ASEAN countries redistributed ~12–15% of U.S. imports. <br> • Market instability caused ~25% contraction in export predictability, reducing U.S. trade growth by ~20%. <br> • Tariff rates, however, remained mostly static, with some unjustified surcharges on surplus countries (e.g., Turkey 2024, UK 2023). <br><br>*(These figures serve as placeholders pending finalized Redshift + QuickSight analysis.)* |

---

## 🧩 Data Architecture  

**AWS Services Used**
- Amazon S3 – Raw and processed data lake ('usa-customs-data-raw-salih-sezen')
- AWS Glue – ETL processing for Excel ingestion and transformation
- AWS Lambda – S3 file renaming and orchestration
- AWS Glue Crawler – Schema inference and Data Catalog
- Amazon Redshift – Analytical data warehouse
- AWS QuickSight – Visualization and dashboarding layer

---

## 🧮 Data Engineering Workflow  

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

## 🧠 Analytical Focus  

- **Policy Validity:** Were tariffs aligned with measurable deficits?  
- **Economic Fairness:** Which nations were over-tariffed despite U.S. surpluses?  
- **Supply Chain Shift:** How did post-COVID production relocation affect imports?  
- **Geoeconomic Factors:** GDP, population, and proximity correlations.  
- **Temporal Trends:** Category-wise recovery rates after 2020.

---

## 🧰 Tech Stack  

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

## 📁 Repository Structure  

us-trade-tariff-analysis/
├── README.md
├── 1- documentation/
│ ├── s3-upload-guide.md
│ ├── glue-job-setup.md
│ ├── redshift-setup.md
│ ├── quick-sight-dashboard-plan.md
│ └── project_report.md
├── 2- data-sources/USA Customs/
│ ├── Dataset1-2.jpg
│ ├── Definitions/
│ │ ├── Mapping Table.xlsx
│ ├── Exports/
│ │ ├── DataWeb-Query-Export (1-5).xlsx
│ ├── Imports/
│ │ └── DataWeb-Query-Export (6-10).xlsx
│ └── additional-datasources/
│ │ └── final_dim_country_clean.xlsx
├── 3- etl-scripts/
│ ├── rename_s3_files.py
│ ├── process_exports.py
│ ├── process_imports.py
│ ├── create_dim_hts_category.py
│ ├── integrate_country_data.py
│ └── integrate_tariff_data.py
├── 4- data-warehousing-and-data-modeling/
│ ├── redshift_schema.sql
│ └── data_model_diagram.png
├── 5- analysis/
│ └── 
└── assets/
├── diagrams/
├── screenshots/
└── dashboards/


---

## 🧾 Future Enhancements  

- Incremental ETL automation using AWS Glue Workflows  
- ML-based anomaly detection for trade irregularities  
- Forecasting simulations for tariff policy changes  
- QuickSight API integration for real-time dashboard refresh  

---

## 🏁 Result Summary *(Template)*  

Preliminary findings suggest that **post-COVID global trade instability significantly altered tariff relevance**:

- Global import/export contraction ≈ 20% overall.  
- Manufacturing relocation from China to India/ASEAN shifted ~12–15% of U.S. imports.  
- European market instability caused ~25% trade volatility, cutting U.S. export growth by ~20%.  
- Tariffs remained largely static, out of sync with real-world trade data.  
- QuickSight visualizations highlight regions (e.g., Turkey, U.K., South Korea) where U.S. surpluses coexist with high tariffs.

These placeholders will be replaced by **empirical Redshift results** and **BI-derived policy metrics** once final dashboards are deployed.

> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*
