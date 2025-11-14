-- linguist-detectable=true
-- 1) STAGING CLEAN VIEW
CREATE OR REPLACE VIEW public.vw_stg_trades_clean AS
SELECT
    datatype,
    country,
    LEFT(LPAD(REGEXP_REPLACE(TRIM(SPLIT_PART(htsnumber,'.',1)), '[^0-9]', ''), 6, '0'), 6) AS htsnumber_clean, 
    description,
    tradevalue,
    customsDirection AS direction,
    datasourcefile,
    TRY_CAST(REGEXP_SUBSTR(datasourcefile, '(19|20)\\d{2}') AS INT) AS file_year
FROM public.stg_trades;


-- 2) DIMENSIONS
-- 2a) DIM DATE
DROP TABLE IF EXISTS public.dim_date;
CREATE TABLE public.dim_date
(
  date_key        INT      PRIMARY KEY,      -- YYYYMMDD
  full_date       DATE     NOT NULL,
  calendar_year   INT      NOT NULL,
  calendar_quarter INT     NOT NULL,
  calendar_month  INT      NOT NULL,
  month_name      VARCHAR(10) NOT NULL,
  day_of_month    INT      NOT NULL,
  day_of_week     INT      NOT NULL,
  day_name        VARCHAR(10) NOT NULL
)
DISTSTYLE AUTO;

-- 2018-01-01 .. 2030-12-31 fill dim_date (INSERT after WITH!)
INSERT INTO public.dim_date (
  date_key, full_date, calendar_year, calendar_quarter,
  calendar_month, month_name, day_of_month, day_of_week, day_name
)
WITH RECURSIVE seq(n) AS (
  SELECT 0
  UNION ALL
  SELECT n + 1
  FROM seq
  WHERE n < DATEDIFF(day, '2018-01-01'::date, '2030-12-31'::date)
),
days AS (
  SELECT DATEADD(day, n, '2018-01-01'::date) AS d
  FROM seq
)
SELECT
  CAST(TO_CHAR(d, 'YYYYMMDD') AS INT)      AS date_key,
  d                                        AS full_date,
  EXTRACT(YEAR    FROM d)::INT             AS calendar_year,
  EXTRACT(QUARTER FROM d)::INT             AS calendar_quarter,
  EXTRACT(MONTH   FROM d)::INT             AS calendar_month,
  TO_CHAR(d, 'Mon')                        AS month_name,
  EXTRACT(DAY     FROM d)::INT             AS day_of_month,
  EXTRACT(DOW     FROM d)::INT             AS day_of_week,
  TO_CHAR(d, 'Dy')                         AS day_name
FROM days;


-- 2b) DIM COUNTRY (persistent key: IDENTITY)
CREATE TABLE IF NOT EXISTS public.dim_country
(
  country_key   INT IDENTITY(1,1) PRIMARY KEY,
  country_name  VARCHAR(100) UNIQUE NOT NULL,
  -- forward-looking placeholders:
  gdp_per_capita NUMERIC(18,2),
  population     BIGINT,
  covid_deaths   BIGINT
)
DISTSTYLE AUTO;

-- first Load (skip existing ones)
INSERT INTO public.dim_country (country_name)
SELECT DISTINCT TRIM(country)
FROM public.vw_stg_trades_clean s
LEFT JOIN public.dim_country d
  ON d.country_name = TRIM(s.country)
WHERE d.country_key IS NULL
  AND TRIM(s.country) <> '';

-- 2c) DIM DIRECTION (optional but clean)
CREATE TABLE public.dim_direction (
  direction_key  SMALLINT PRIMARY KEY,
  direction_name VARCHAR(20) UNIQUE NOT NULL
);
-- 2) Stable records
INSERT INTO public.dim_direction(direction_key, direction_name)
VALUES (1,'Imports'), (2,'Exports');

ALTER TABLE public.dim_hts_category RENAME TO stg_hts_category;

-- 2d) DIM HTS CATEGORY

--DROP TABLE IF EXISTS public.dim_hts_category;
--TRUNCATE TABLE public.dim_hts_category;

CREATE TABLE public.dim_hts_category (
  hts6                  VARCHAR(6) NOT NULL,
  infoyear              INT        NOT NULL,
  hts6descriptionlatest VARCHAR(500),
  hts4                  VARCHAR(4),
  hts4descriptionlatest VARCHAR(500),
  hts2                  VARCHAR(2),
  hts2descriptionlatest VARCHAR(500),
  -- Redshift PK not physical but we define it for metadata:
  PRIMARY KEY (hts6, infoyear)
)
DISTSTYLE AUTO
SORTKEY (infoyear, hts6);

-- populate dim_hts_category (hts6 natural key)
INSERT INTO public.dim_hts_category
  (hts6, hts6descriptionlatest, hts4, hts4descriptionlatest, hts2, hts2descriptionlatest, infoyear)
SELECT DISTINCT
  h.hts6,
  h.hts6desc,
  h.hts4,
  c.hts4descriptionlatest,
  h.hts2,
  c.hts2descriptionlatest,
  c.infoyear
FROM (
  SELECT
    LEFT(LPAD(REGEXP_REPLACE(TRIM(SPLIT_PART(htsnumber,'.',1)),'[^0-9]',''),6,'0'),6)    AS hts6,
    LEFT(LPAD(REGEXP_REPLACE(TRIM(SPLIT_PART(htsnumber,'.',1)),'[^0-9]',''),6,'0'),4)    AS hts4,
    LEFT(LPAD(REGEXP_REPLACE(TRIM(SPLIT_PART(htsnumber,'.',1)),'[^0-9]',''),6,'0'),2)    AS hts2,
    TRIM(description)                                                                     AS hts6desc
  FROM public.stg_trades
  WHERE description IS NOT NULL
) h
LEFT JOIN (
  SELECT DISTINCT hts4, hts4descriptionlatest, hts2, hts2descriptionlatest,infoyear
  FROM public.stg_hts_category
) c
  ON c.hts4 = h.hts4;

SELECT COUNT(DISTINCT hts6) , COUNT(DISTINCT hts6) --must be the same
FROM "dim_hts_category"

--3a) FACT TRADES
-- 1) Fact table
DROP TABLE IF EXISTS public.fact_trades;

CREATE TABLE public.fact_trades
(
  trade_id      BIGINT IDENTITY(1,1),        -- permanent surrogate key instead of rownum
  date_key      INTEGER       NOT NULL,       -- YYYYMMDD (last day of year)
  country_key   INTEGER       NOT NULL,       -- dim_country FK
  hts6_key      VARCHAR(10)   NOT NULL,       -- t.htsnumber_clean
  direction_key SMALLINT      NOT NULL,       -- dim_direction FK
  trade_value   NUMERIC(18,2) NOT NULL        -- keep value as is
)
DISTSTYLE AUTO
SORTKEY (date_key, country_key, hts6_key);

-- 2) Load
INSERT INTO public.fact_trades
(
  date_key,
  country_key,
  hts6_key,
  direction_key,
  trade_value
)
SELECT
  -- file_year -> last day of year -> YYYYMMDD (int) 
  CAST(TO_CHAR(TO_DATE(t.file_year::varchar || '1231','YYYYMMDD'),'YYYYMMDD') AS INTEGER) AS date_key,

  -- Country -> dim_country.country_key (modify matching as needed: NAME/CODE) 
  c.country_key,

  -- HTSNumber cleaned version directly as key
  t.htsnumber_clean AS hts6_key,

  -- Direction -> dim_direction.direction_key (e.g. 'Imports'/'Exports') 
  d.direction_key,

  -- keep value as is
  t.tradevalue
FROM public.vw_stg_trades_clean t
LEFT JOIN public.dim_country    c ON UPPER(c.country_name) = UPPER(t.country)
LEFT JOIN public.dim_direction  d ON UPPER(d.direction_name) = UPPER(t.direction);

