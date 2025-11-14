import pandas as pd
import boto3
import os
from io import BytesIO
from typing import Optional

# ========== AWS & S3 ==========
S3_BUCKET = "usa-customs-data-raw-salih-sezen"
AWS_REGION = "us-east-1"
s3 = boto3.client("s3", region_name=AWS_REGION)

RAW_FOLDER = "USA Customs"
PROCESSED_FOLDER = f"{RAW_FOLDER}/processed"
METADATA_FOLDER = f"{PROCESSED_FOLDER}/metadata"

# ========== HELPERS ==========
def list_s3_objects(prefix: str):
    out = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=S3_BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj.get("Key")
            if key and not key.endswith("/"):
                out.append(key)
    return out

def read_excel_from_s3(s3_key: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    obj = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
    return pd.read_excel(BytesIO(obj["Body"].read()), sheet_name=sheet_name, engine="openpyxl")

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip().replace("\n", " ").replace("  ", " ") for c in df.columns]
    return df

def _clean_trade_df(df: pd.DataFrame, value_col_name: str, file_name: str, category: str) -> pd.DataFrame:
    rename_map = {
        "Data Type": "DataType",
        "Country": "Country",
        "Year": "Year",
        "HTS Number": "HTSNumber",
        "Description": "Description",
        value_col_name: "TradeValue",
    }
    df = df.rename(columns=rename_map)

    keep_cols = ["DataType", "Country", "Year", "HTSNumber", "Description", "TradeValue"]
    df = df[[c for c in keep_cols if c in df.columns]]

    if "Country" in df.columns:
        df = df.dropna(subset=["Country"])
    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df = df.dropna(subset=["Year"])

    if "TradeValue" in df.columns:
        m_total = df["TradeValue"].astype(str).str.contains("Total", case=False, na=False)
        df = df[~m_total]
        vals = pd.to_numeric(df["TradeValue"].astype(str).str.replace(",", "", regex=False), errors="coerce")
        df = df[~vals.isna()].copy()
        df["TradeValue"] = vals[~vals.isna()]

    if "HTSNumber" in df.columns:
        df["HTSNumber"] = df["HTSNumber"].astype(str).str.strip()

    df["Year"] = df["Year"].astype("Int64")
    df["CustomsDirection"] = category
    df["DataSourceFile"] = file_name
    return df

def _write_parquet_to_s3(df: pd.DataFrame, s3_key: str):
    buf = BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    s3.upload_fileobj(buf, S3_BUCKET, s3_key)

# ========== IMPORTS ==========
def process_hts6_imports():
    category = "Imports"
    sheet_name = "General Customs Value"
    value_col_name = "General Customs Value"

    raw_prefix = f"{RAW_FOLDER}/{category}/"
    files = list_s3_objects(raw_prefix)
    hts6_files = [k for k in files if "HTS6" in os.path.basename(k) and k.endswith(".xlsx")]

    if not hts6_files:
        print(f"[WARN] No HTS6 files for {category} under s3://{S3_BUCKET}/{raw_prefix}")
        return

    for key in hts6_files:
        fname = os.path.basename(key)
        try:
            df = read_excel_from_s3(key, sheet_name=sheet_name)
            df = _normalize_columns(df)
            df = _clean_trade_df(df, value_col_name=value_col_name, file_name=fname, category=category)

            out_base = f"{PROCESSED_FOLDER}/{category}/"
            for year, grp in df.groupby("Year"):
                # Remove Year from the file (to avoid conflict with partition)
                if "Year" in grp.columns:
                    grp = grp.drop(columns=["Year"])
                out_key = f"{out_base}year={int(year)}/{fname.replace('.xlsx', '.parquet')}"
                _write_parquet_to_s3(grp, out_key)
                print(f"[OK] {out_key} ({len(grp)} rows)")

        except Exception as e:
            print(f"[ERR] Processing {key}: {e}")

def process_code_imports():
    category = "Imports"
    raw_prefix = f"{RAW_FOLDER}/{category}/"
    files = list_s3_objects(raw_prefix)

    for level in ("HTS2", "HTS4"):
        code_files = [k for k in files if (level in os.path.basename(k)) and k.endswith(".xlsx")]
        if not code_files:
            print(f"[WARN] No {level} code files for {category}")
            continue

        frames = []
        for key in code_files:
            try:
                df = read_excel_from_s3(key)
                df = _normalize_columns(df)
                df = df.rename(columns={"HTS Number": "HTSNumber"})
                cols = [c for c in ["HTSNumber", "Description"] if c in df.columns]
                if cols:
                    df = df[cols]
                if "HTSNumber" in df.columns:
                    df["HTSNumber"] = df["HTSNumber"].astype(str).str.strip()
                frames.append(df)
            except Exception as e:
                print(f"[ERR] Reading code file {key}: {e}")

        if frames:
            all_df = pd.concat(frames, ignore_index=True).dropna(how="all")
            if "HTSNumber" in all_df.columns:
                all_df = all_df.drop_duplicates(subset=["HTSNumber"], keep="first")
            out_key = f"{METADATA_FOLDER}/Imports_{level}_Codes.parquet"
            _write_parquet_to_s3(all_df, out_key)
            print(f"[OK] {out_key} ({len(all_df)} rows)")

if __name__ == "__main__":
    process_hts6_imports()
    process_code_imports()
    print("🚀 Imports processing complete.")
