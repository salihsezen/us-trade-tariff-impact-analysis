--Script 1 Create stg_trades table
--DROP TABLE IF EXISTS COPY stg_trades;
CREATE TABLE IF NOT EXISTS dev.public.stg_trades (
    datatype           VARCHAR(100),
    country            VARCHAR(100),
    htsnumber          VARCHAR(20),
    description        VARCHAR(500),
    tradevalue         DOUBLE PRECISION,
    customsdirection   VARCHAR(20),
    datasourcefile     VARCHAR(200)
);

--Script 2 Load stg_trades table from data catalog
COPY stg_trades
--get one file into stg_trades table
--FROM 's3://usa-customs-data-raw-salih-sezen/USA Customs/processed/Imports/year=2023/2023_USA_Imports_HTS6.parquet'
 --get all Imports into stg_trades 
--FROM 's3://usa-customs-data-raw-salih-sezen/USA Customs/processed/Imports/' table
-- get all trades into stg_trades table
FROM 's3://usa-customs-data-raw-salih-sezen/USA Customs/processed/' 
IAM_ROLE 'arn:aws:iam::<Your Account Id>:role/usa-customs-redshift-role'
FORMAT AS PARQUET;

--Script 3 Create dim_hts_category table
--DROP TABLE dimhtscategory_parquet;
CREATE TABLE IF NOT EXISTS dev.public.dim_hts_category (
    htscategorykey VARCHAR(20),
    hts2 VARCHAR(10),
    hts2descriptionlatest VARCHAR(500),
    hts4 VARCHAR(10),
    hts4descriptionlatest VARCHAR(500),
    infoyear INT
);

--Script 2 Load dim_hts_category table from data catalog
COPY dev.public.dim_hts_category
FROM 's3://usa-customs-data-raw-salih-sezen/USA Customs/processed/OtherDatasources/DimHTSCategory/'
IAM_ROLE 'arn:aws:iam::<Your Account Id>:role/usa-customs-redshift-role'
FORMAT AS PARQUET;