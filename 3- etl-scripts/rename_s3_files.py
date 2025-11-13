import pandas as pd
import boto3
from io import BytesIO

# Your AWS S3 bucket name and region
S3_BUCKET_NAME = 'usa-customs-data-raw-salih-sezen' # Your S3 bucket name here!
AWS_REGION = 'us-east-1' # Your AWS region here!

# Full S3 path to the mapping table
MAPPING_TABLE_S3_KEY = 'USA Customs/Definitions/Mapping Table.xlsx'

# Initialize S3 client
s3_client = boto3.client('s3', region_name=AWS_REGION)

def rename_s3_files(s3_bucket, mapping_table_s3_key):
    """
    Renames other files in S3 using the mapping table from S3.
    """
    try:
        # Read Mapping Table directly from S3
        print(f"Reading mapping table '{mapping_table_s3_key}' from S3...")
        obj = s3_client.get_object(Bucket=s3_bucket, Key=mapping_table_s3_key)
        
        # obj['Body'] is a stream, use BytesIO for pandas to read it
        mapping_df = pd.read_excel(BytesIO(obj['Body'].read()))
        
        print(f"Read {len(mapping_df)} records from the mapping table.")

        for index, row in mapping_df.iterrows():
            old_file_base_name = row['File'] # e.g., DataWeb-Query-Export (1)
            new_file_name_with_ext = row['Rename'] # e.g., 2024_USA_Exports_HTS6.xlsx

            # Determine the 'Exports' or 'Imports' folder based on DataCategory
            # Assuming row['RowNum'] 1-5 are Exports, 6-10 are Imports
            data_category_folder = 'Exports' if row['RowNum'] <= 5 else 'Imports'
            
            # Construct the old_s3_key. Ensure .xlsx is only added once.
            # Assuming old_file_base_name does NOT include .xlsx in the 'File' column
            # If 'File' column already contains '.xlsx', you might need to adjust this.
            # Based on your previous output, 'DataWeb-Query-Export (1)' seems to be without extension.
            
            # Check if old_file_base_name already ends with .xlsx
            if not old_file_base_name.endswith('.xlsx'):
                old_s3_key = f'USA Customs/{data_category_folder}/{old_file_base_name}.xlsx'
            else:
                old_s3_key = f'USA Customs/{data_category_folder}/{old_file_base_name}' # Use as is if it already has .xlsx

            new_s3_key = f'USA Customs/{data_category_folder}/{new_file_name_with_ext}'

            print(f"Renaming in S3: '{old_s3_key}' -> '{new_s3_key}'")

            try:
                # Check if the old_s3_key actually exists before trying to copy/delete
                s3_client.head_object(Bucket=s3_bucket, Key=old_s3_key)
                
                # Copy the file in S3 (with the new name)
                s3_client.copy_object(
                    Bucket=s3_bucket,
                    CopySource={'Bucket': s3_bucket, 'Key': old_s3_key},
                    Key=new_s3_key
                )
                # Delete the old file
                s3_client.delete_object(Bucket=s3_bucket, Key=old_s3_key)
                print(f"Successfully renamed and deleted old file.")
            except s3_client.exceptions.ClientError as e:
                # Check if the error is due to NoSuchKey
                if e.response['Error']['Code'] == '404':
                    print(f"Warning: '{old_s3_key}' not found. Perhaps it was already renamed or the path is incorrect. Skipping.")
                else:
                    print(f"Error renaming '{old_s3_key}': {e}")
            except Exception as e:
                print(f"An unexpected error occurred during rename for '{old_s3_key}': {e}")

    except s3_client.exceptions.NoSuchKey:
        print(f"Error: Mapping table file not found in S3: '{mapping_table_s3_key}'")
    except Exception as e:
        print(f"General error: {e}")

# Run the script
if __name__ == "__main__":
    rename_s3_files(S3_BUCKET_NAME, MAPPING_TABLE_S3_KEY)
def lambda_handler(event, context):
    rename_s3_files(S3_BUCKET_NAME, MAPPING_TABLE_S3_KEY)
    return {"statusCode": 200, "body": "Rename job completed"}