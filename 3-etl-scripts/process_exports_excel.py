import pandas as pd
import boto3
import os
from io import BytesIO
import re

# ========= AWS SETTINGS ========= #
S3_BUCKET = "usa-customs-data-raw-salih-sezen"
AWS_REGION = "us-east-1"
s3 = boto3.client("s3", region_name=AWS_REGION)

RAW_FOLDER = "USA Customs"
PROCESSED_FOLDER = f"{RAW_FOLDER}/processed"
OUTPUT_FOLDER = f"{PROCESSED_FOLDER}/OtherDatasources"

# ========= HELPERS ========= #

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
    """Reads Excel from S3 and ensures the correct sheet (2nd or 'FAS Value') is selected"""
    obj = s3.get_object(Bucket=S3_BUCKET, Key=s3_key)
    content = BytesIO(obj["Body"].read())
    xl = pd.ExcelFile(content, engine="openpyxl")

    preferred_sheet = "FAS Value" if category == "Exports" else "General Customs Value"

    if preferred_sheet in xl.sheet_names:
        sheet_name = preferred_sheet
    elif len(xl.sheet_names) > 1:
        sheet_name = xl.sheet_names[1]
    else:
        sheet_name = xl.sheet_names[0]

    print(f"[INFO] Reading {s3_key} -> sheet: {sheet_name}")
    df = xl.parse(sheet_name)
    df.columns = [str(c).strip().replace("\n", " ") for c in df.columns]
    return df


def detect_column(df, possible_names):
    for col in df.columns:
        for pattern in possible_names:
            if pattern.lower() in str(col).lower():
                return col
    return None


def _write_parquet_to_s3(df: pd.DataFrame, s3_key: str):
    """Writes a clean, Redshift/Athena-compatible Parquet file to S3 (keeps spaces in path)"""
    buf = BytesIO()

    df = df.replace({pd.NA: None}).fillna({
        "HTS2DescriptionLatest": "Unknown",
        "HTS4DescriptionLatest": "Unknown"
    })

    df = df.astype({
        "HTSCategoryKey": "string",
        "HTS2": "string",
        "HTS2DescriptionLatest": "string",
        "HTS4": "string",
        "HTS4DescriptionLatest": "string",
        "InfoYear": "int32"
    })

    df.to_parquet(buf, index=False, engine="pyarrow")
    buf.seek(0)

    # 🔹 boşluklu path'i KORU — rename yok
    safe_key = s3_key

    s3.upload_fileobj(buf, S3_BUCKET, safe_key)
    print(f"[OK] Written: s3://{S3_BUCKET}/{safe_key} ({len(df)} rows)")


# ========= MAIN ========= #

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
        code_files = [k for k in files if (level in os.path.basename(k)) and k.endswith(".xlsx")]

        for key in code_files:
            fname = os.path.basename(key)
            try:
                df = read_excel_from_s3(key, category)

                hts_col = detect_column(df, ["HTS Number", "HTS", "Code"])
                desc_col = detect_column(df, ["Description", "Desc", "Product"])

                if not hts_col or not desc_col:
                    print(f"[WARN] Skipping {fname}: missing HTS or Description columns.")
                    continue

                df = df.rename(columns={hts_col: "HTSNumber", desc_col: "Description"})

                # Year from filename or column
                if "Year" not in df.columns:
                    m = re.search(r"(\d{4})", fname)
                    df["Year"] = int(m.group(1)) if m else 0
                else:
                    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(0).astype(int)

                df["HTSNumber"] = df["HTSNumber"].astype(str).str.replace(".0", "", regex=False).str.strip()
                df["Description"] = df["Description"].astype(str).str.strip()
                df["Level"] = level

                all_frames.append(df)
                print(f"[OK] Loaded {fname} ({len(df)} rows)")

            except Exception as e:
                print(f"[ERR] {fname}: {e}")

    if not all_frames:
        print("[WARN] No HTS hierarchy files found.")
        return

    df_all = pd.concat(all_frames, ignore_index=True)
    df_all = df_all.dropna(subset=["HTSNumber"])
    if "Year" not in df_all.columns:
        df_all["Year"] = 0

    # Split by level
    df_hts2 = df_all[df_all["Level"] == "HTS2"].copy()
    df_hts4 = df_all[df_all["Level"] == "HTS4"].copy()

    # Normalize HTS numbers
    df_hts2["HTSNumber"] = df_hts2["HTSNumber"].apply(lambda x: str(x).split(".")[0].zfill(2))
    df_hts4["HTSNumber"] = df_hts4["HTSNumber"].apply(lambda x: str(x).split(".")[0].zfill(4))

    # Latest Year per HTS
    df_hts2 = (
        df_hts2.sort_values("Year", ascending=False)
        .drop_duplicates(subset=["HTSNumber"], keep="first")
        .rename(columns={"HTSNumber": "HTS2", "Description": "HTS2DescriptionLatest"})
    )

    df_hts4 = (
        df_hts4.sort_values("Year", ascending=False)
        .drop_duplicates(subset=["HTSNumber"], keep="first")
        .rename(columns={"HTSNumber": "HTS4", "Description": "HTS4DescriptionLatest"})
    )

    # Derive HTS2 from HTS4
    df_hts4["HTS2"] = df_hts4["HTS4"].str[:2]

    # Merge HTS4 → HTS2
    df_dim = pd.merge(df_hts4, df_hts2, on="HTS2", how="left", suffixes=("", "_y"))
    df_dim["HTS2DescriptionLatest"] = df_dim["HTS2DescriptionLatest"].fillna("Unknown")
    df_dim["HTS4DescriptionLatest"] = df_dim["HTS4DescriptionLatest"].fillna("Unknown")

    df_dim["InfoYear"] = df_dim[["Year", "Year_y"]].max(axis=1).astype(int)

    # Final formatting
    df_dim["HTSCategoryKey"] = df_dim["HTS4"].astype(str)
    df_dim = df_dim[
        ["HTSCategoryKey", "HTS2", "HTS2DescriptionLatest",
         "HTS4", "HTS4DescriptionLatest", "InfoYear"]
    ].reset_index(drop=True)

    # ✅ Write to S3 (as folder for Athena/Redshift)
    out_key = f"{OUTPUT_FOLDER}/DimHTSCategory/part-0000.parquet"
    _write_parquet_to_s3(df_dim, out_key)
    print("=== ✅ DimHTSCategory created successfully ===")


if __name__ == "__main__":
    process_dim_hts_category()
