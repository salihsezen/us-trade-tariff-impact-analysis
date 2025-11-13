> “Data doesn’t lie — but policy often does.”  
> — *Project Lead: Salih Sezen*

# US Trade Tariff Impact Analysis (2022–2024)

### 📊 3- S3-upload-guide.md
**Screen Shot:**
"6- screen-shots/3- S3-upload-data-sources.jpg"

This document explains where files are uploaded inside S3, why these folders exist, and how Glue, Redshift and BI tools use them across the pipeline.

---

# 1. S3 Bucket Structure (Authoritative Layout)

Bucket name:

    usa-customs-data-raw-salih-sezen

Main project folder:

    USA Customs/

Final layout:

    usa-customs-data-raw-salih-sezen
    └── USA Customs/
        ├── Definitions/
        │   ├── Mapping Table.xlsx
        │
        ├── Exports/
        │   ├── 2022_USA_Exports_HTS6.xlsx
        │   ├── 2023_USA_Exports_HTS6.xlsx
        │   ├── 2024_USA_Exports_HTS6.xlsx
        │   ├── Exports_HTS2_Codes.xlsx
        │   └── Exports_HTS4_Codes.xlsx
        │
        ├── Imports/
        │   ├── 2022_USA_Imports_HTS6.xlsx
        │   ├── 2023_USA_Imports_HTS6.xlsx
        │   ├── 2024_USA_Imports_HTS6.xlsx
        │   ├── Imports_HTS2_Codes.xlsx
        │   └── Imports_HTS4_Codes.xlsx
        │
        ├── Processed/
            └── parquet/
                ├── Exports/year=(2022..2024)/(2022..2024)_USA_Exports_HTS6.parquet
                ├── Imports/year=(2022..2024)/(2022..2024)_USA_Imports_HTS6.parquet
                ├── OtherDatasources/DimHTSCategory/part-0000.parquet
                └── (future dims)


---

# 2. Local Folder → S3 Mapping

Local structure:

    data-sources/
    └── USA Customs/
        ├── Definitions/
        ├── Exports/
        └── Imports/

Every file in this structure maps **1:1** to the S3 layout shown above.

---

# 3. Folder Purposes

## 3.1 Definitions  
S3 path:

    USA Customs/Definitions/

Purpose:  
Reference files that enrich, categorize, or support data transformations.  
They are not fact tables.

Files include:
- Mapping Table.xlsx  
- Country List.xlsx  
- Tariff Rates by Country.xlsx  
- HTS2 Description.xlsx  
- HTS4 Description.xlsx  
- Any future metadata file

Used by:
- rename_s3_files.py  
- build_dim_hts_category.py  
- build_dim_country.py

---

## 3.2 Exports  
S3 path:

    USA Customs/Exports/

Purpose:  
Raw export transaction data from https://dataweb.usitc.gov after renaming.

Expected filenames:

    2022_USA_Exports_HTS6.xlsx
    2023_USA_Exports_HTS6.xlsx
    2024_USA_Exports_HTS6.xlsx

Used by Glue job:

    exports_to_parquet.py

---

## 3.3 Imports  
S3 path:

    USA Customs/Imports/

Purpose:  
Raw import transaction data.

Expected filenames:

    2022_USA_Imports_HTS6.xlsx
    2023_USA_Imports_HTS6.xlsx
    2024_USA_Imports_HTS6.xlsx

Used by Glue job:

    imports_to_parquet.py

---

## 3.4 Processed (Parquet Output)  and Curated (If we need)
S3 path:

    USA Customs/Processed/parquet/

Purpose:  
Optimized analytical storage.  
Glue writes all transformed Parquet outputs here.

Folders:

    Exports/year=(2022..2024)/
    Imports/year=(2022..2024)/
    OtherDatasources/DimHTSCategory/


---


# 4. How to Upload Files to S3 (Manual)

Steps:

1. Open AWS Console → S3  
2. Go to bucket:  

        usa-customs-data-raw-salih-sezen

3. Navigate to the correct folder (Definitions / Exports / Imports)  
4. Click **Upload**  
5. Drop files  
6. No special settings required  
7. Upload

---

# 5. How to Upload Using AWS CLI

    aws s3 sync "data-sources/USA Customs/Definitions/" \
        "s3://usa-customs-data-raw-salih-sezen/USA Customs/Definitions/"

    aws s3 sync "data-sources/USA Customs/Exports/" \
        "s3://usa-customs-data-raw-salih-sezen/USA Customs/Exports/"

    aws s3 sync "data-sources/USA Customs/Imports/" \
        "s3://usa-customs-data-raw-salih-sezen/USA Customs/Imports/"

---

# 6. Quality Check After Upload

Verify:

- File counts match local folders
- Files open correctly in S3 console
- Mapping Table.xlsx exists at:

      USA Customs/Definitions/Mapping Table.xlsx

This file is required for renaming and ETL consistency.

---

# 7. Summary

- All raw data → Exports / Imports  
- All metadata → Definitions  
- All ETL output → Processed/parquet  
- All star-schema curated files → Curated/  
- Redshift COPY commands always read from Processed or Curated zones  
- Glue never writes into raw folders  
- You never manually touch Processed or Curated folders  

This ensures a clean data lake → ETL → DWH → BI pipeline.

---
