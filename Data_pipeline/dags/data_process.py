import os
import pandas as pd
import random
from google.cloud import storage
from io import StringIO
import json
import config
# Set GCP credentials dynamically from config.py
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GCP_CREDENTIALS_PATH

# Google Cloud Storage (GCS) Details
INPUT_FOLDER = "reviews/"  # Folder containing JSONL files 

SELLER_IDS = ["2471521", "2471522", "2471523", "2471524", "2471525"]

# Dictionary to ensure consistent seller ID assignment
parent_asin_seller_map = {}

def assign_seller_id(parent_asin):
    """Assigns a consistent seller ID for each unique parent_asin."""
    if parent_asin not in parent_asin_seller_map:
        parent_asin_seller_map[parent_asin] = random.choice(SELLER_IDS)
    return parent_asin_seller_map[parent_asin]

def list_jsonl_files(bucket_name, folder_name):
    """Lists all JSONL files in the specified GCS folder."""
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix=folder_name))

        jsonl_files = [blob.name for blob in blobs if blob.name.endswith(".jsonl")]
        print(f"Found {len(jsonl_files)} JSONL files in {folder_name}.")
        return jsonl_files
    except Exception as e:
        print(f"Error listing files in GCS: {e}")
        return []

def process_jsonl_from_gcs():
    bucket_name=config.BUCKET_NAME
    jsonl_files = list_jsonl_files(bucket_name, INPUT_FOLDER)
    if not jsonl_files:
        print("No JSONL files found in the bucket.")
        return
    """Reads and processes JSONL files from GCS, assigning seller IDs consistently."""
    client = storage.Client()
    all_data = []

    for jsonl_file in jsonl_files:
        try:
            print(f"Processing {jsonl_file}...")

            # Download JSONL file
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(jsonl_file)
            jsonl_data = blob.download_as_text()

            valid_records = []
            invalid_lines = 0

            # Process each line individually to catch errors
            for line in jsonl_data.strip().split("\n"):
                try:
                    record = json.loads(line)
                    valid_records.append(record)
                except json.JSONDecodeError:
                    invalid_lines += 1  # Count invalid lines

            if invalid_lines > 0:
                print(f"Warning: Skipped {invalid_lines} invalid lines in {jsonl_file}")

            if not valid_records:
                print(f"Skipping {jsonl_file} - No valid data.")
                continue

            df = pd.DataFrame(valid_records)

            # Ensure 'parent_asin' column exists before assigning seller IDs
            if "parent_asin" in df.columns:
                df["seller_id"] = df["parent_asin"].apply(assign_seller_id)
            else:
                print(f"Skipping {jsonl_file} - missing 'parent_asin' column.")

            all_data.append(df)

        except Exception as e:
            print(f"Error processing {jsonl_file}: {e}")

    if not all_data:
        print("No valid data found to merge.")
        return pd.DataFrame()  # Return empty DataFrame if no data

    # Merge all processed data
    merged_df = pd.concat(all_data, ignore_index=True)
    print(f"Merged {len(merged_df)} records from {len(jsonl_files)} files.")
    return merged_df

def save_csv_to_gcs():
    bucket_name=config.BUCKET_NAME
    df = process_jsonl_from_gcs()
    output_file = "processed/reviews_processed.csv"
    """Saves the processed DataFrame as a CSV file in GCS."""
    if df.empty:
        print("No data to save. Skipping CSV upload.")
        return

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(output_file)

        # Convert DataFrame to CSV format
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        # Upload to GCS
        blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")
        print(f"Processed data saved to: gs://{bucket_name}/{output_file}")
    except Exception as e:
        print(f"Error saving CSV to GCS: {e}")

# process_jsonl_from_gcs()
# save_csv_to_gcs()