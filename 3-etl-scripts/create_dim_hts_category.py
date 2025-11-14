import pandas as pd
import boto3
import os
from io import BytesIO
import re

# ========== AWS SETTINGS ========== v4
S3_BUCKET = "usa-customs-data-raw-salih-sezen"
AWS_REGION = "us-east-1"
s3 = boto3.client("s3", region_name=AWS_REGION)

RAW_FOLDER = "USA Customs"
PROCESSED_FOLDER = f"{RAW_FOLDER}/processed"
OUTPUT_FOLDER = f"{PROCESSED_FOLDER}/OtherDatasources"  # ✅ yeni hedef klasör

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

def read_excel_from_s3(s3_key: str, category: str) -> pd.DataFrame:
    """Read Excel and pick correct sheet: 'FAS Value' or 'General Customs Value'."""
    obj = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
    content = BytesIO(obj["Body"].read())

    preferred_sheet = "FAS Value" if category == "Exports" else "General Customs Value"
    xl = pd.ExcelFile(content, engine="openpyxl")

    sheet_name = preferred_sheet if preferred_sheet in xl.sheet_names else xl.sheet_names[0]
    df = xl.parse(sheet_name)
    df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]
    return df

def detect_column(df, possible_names):
    """Find the first matching column name from a list of possibilities."""
    for col in df.columns:
        for pattern in possible_names:
            if pattern.lower() in str(col).lower():
                return col
    return None

def _write_parquet_to_s3(df: pd.DataFrame, s3_key: str):
    buf = BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    s3.upload_fileobj(buf, S3_BUCKET, s3_key)
    print(f"[OK] Written: s3://{S3_BUCKET}/{s3_key} ({len(df)} rows)")

# ========== MAIN PROCESS ==========
def process_dim_hts_category():
    print("=== Building unified DimHTSCategory (HTS2 + HTS4) ===")

    data_sources = [
        ("Exports", "HTS2"),
        ("Exports", "HTS4"),
        ("Imports", "HTS2"),
        ("Imports", "HTS4"),
    ]

    all_frames = []

    for category, level in data_sources:
        prefix = f"{RAW_FOLDER}/{category}/"
        files = list_s3_objects(prefix)
        code_files = [k f]()_
