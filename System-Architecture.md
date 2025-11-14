```mermaid
flowchart LR

%% ---------- COLOR PALETTE ----------
%% S3: Orange, Glue: Purple, Redshift: Red, BI: Blue/Green, IAM: Grey

classDef s3 fill:#f7d7a4,stroke:#c48c00,stroke-width:1px,color:#000
classDef glue fill:#e3d2ff,stroke:#7e3ff2,stroke-width:1px,color:#000
classDef redshift fill:#ffb8b8,stroke:#d94848,stroke-width:1px,color:#000
classDef bi fill:#c8e8ff,stroke:#3e8ed0,stroke-width:1px,color:#000
classDef iam fill:#e6e6e6,stroke:#8d8d8d,stroke-width:1px,color:#000
classDef local fill:#fff3c9,stroke:#cc9a00,stroke-width:1px,color:#000


%% ---------- LOCAL LAYER ----------
subgraph LOCAL["Local Machine / Raw Files"]
  A1[Excel Raw Files<br>(_exports, imports, hts2, hts4_)]
  A2[Mapping Table.xlsx]
end
class LOCAL,A1,A2 local


%% ---------- S3 RAW LAYER ----------
subgraph S3RAW["S3 – Raw Layer"]
  B1[(usa-customs-data-raw-salih-sezen)]
  B2[USA Customs/Exports/]
  B3[USA Customs/Imports/]
  B4[USA Customs/Definitions/]
end
class S3RAW,B1,B2,B3,B4 s3

A1 --> B2
A1 --> B3
A2 --> B4


%% ---------- LAMBDA (RENAME) ----------
subgraph LAMBDA["Lambda – File Rename"]
  L1[rename_s3_files.py<br>(copy → delete → clean names)]
end
class L1 glue

B4 --> L1
L1 --> B2
L1 --> B3


%% ---------- GLUE ETL ----------
subgraph GLUE["AWS Glue ETL – Processing Layer"]
  G1[process_exports_excel.py<br>Excel → Parquet]
  G2[process_imports_excel.py<br>Excel → Parquet]
  G3[create_dim_hts_category.py]
end
class G1,G2,G3 glue

B2 --> G1
B3 --> G2
B4 --> G3


%% ---------- S3 PROCESSED ----------
subgraph S3PROC["S3 – Processed (Parquet)"]
  P1[(Processed/Exports/)]
  P2[(Processed/Imports/)]
  P3[(OtherDatasources/DimHTSCategory/)]
end
class P1,P2,P3 s3

G1 --> P1
G2 --> P2
G3 --> P3


%% ---------- GLUE CRAWLERS ----------
subgraph CRAWLERS["Glue Crawlers + Catalog"]
  C1[Exports/Imports Crawler]
  C2[DimHTSCategory Crawler]
  CAT[(Glue Data Catalog)]
end
class C1,C2,CAT glue

P1 --> C1 --> CAT
P2 --> C1
P3 --> C2 --> CAT


%% ---------- REDSHIFT ----------
subgraph REDSHIFT["Amazon Redshift Serverless – DWH"]
  R1[(staging tables)]
  R2[(core.fact_trades)]
  R3[(core.dim_country)]
  R4[(core.dim_hts_category)]
  R5[(core.dim_direction)]
  R6[(core.dim_date)]
end
class R1,R2,R3,R4,R5,R6 redshift

CAT --> R1
P1 --> R1
P2 --> R1
P3 --> R4


%% ---------- BI LAYER ----------
subgraph BI["Analytics & BI Layer"]
  Q1[Amazon QuickSight]
  PBI[Power BI Desktop]
end
class Q1,PBI bi

R2 --> Q1
R2 --> PBI
R3 --> Q1
R3 --> PBI
R4 --> Q1
R4 --> PBI


%% ---------- IAM ----------
subgraph IAM["IAM Roles"]
  IAM1[usa-customs-glue-role]
  IAM2[usa-customs-redshift-role]
  IAM3[aws-quicksight-service-role]
end
class IAM1,IAM2,IAM3 iam

IAM1 -.-> GLUE
IAM1 -.-> CRAWLERS
IAM2 -.-> REDSHIFT
IAM3 -.-> Q1
```
