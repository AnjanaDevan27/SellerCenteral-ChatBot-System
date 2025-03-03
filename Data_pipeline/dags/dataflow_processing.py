import os
from google.cloud import storage, bigquery
import pandas as pd
from io import BytesIO
import config
from bias_detection import handle_bias
from logging_setup import log_event
import tensorflow_data_validation as tfdv
import tensorflow as tf
from matplotlib import pyplot as plt

# Set GCP credentials dynamically from config.py
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GCP_CREDENTIALS_PATH

def read_csv_from_gcp():
    """Reads a CSV file from GCS and returns it as a Pandas DataFrame."""
    client = storage.Client()
    bucket = client.bucket(config.BUCKET_NAME)
    blob = bucket.blob(config.FILE_NAME)
    content = blob.download_as_string()
    df = pd.read_csv(BytesIO(content))
    handle_bias(df)
    return df

def validate_data_with_tfdv(df):
    """Validates data using TFDV for anomaly detection."""
    
    # Generate statistics from the DataFrame
    stats = tfdv.generate_statistics_from_dataframe(df)
    
    save_path = "visualization.png"
    plt.savefig(save_path)  # Save the plot to the specified path
    print(f"Visualization saved to {save_path}")
    # Visualize the statistics
    print("Dataset Statistics:")
    tfdv.visualize_statistics(stats)

    # Load a predefined schema (if you have one, else we can generate one from the data)
    # Here, we will just generate a schema from the statistics
    schema = tfdv.infer_schema(stats)
    # Perform anomaly detection and compare against the schema
    anomalies = tfdv.validate_statistics(statistics=stats, schema=schema)
    print(anomalies)

    # Display anomalies
    if anomalies:
        print("\nAnomalies detected:")
        for anomaly in anomalies.anomaly_info:
            print(f"Feature: {anomaly.feature_path.step[0]}, "
                  f"Anomaly Type: {anomaly.anomaly_type}, "
                  f"Details: {anomaly.details}")
    else:
        print("\nNo anomalies detected.")

def create_bigquery_dataset():
    """Creates a dataset in BigQuery if it doesn't exist."""
    project_id = "spheric-engine-451615-a8"
    dataset_id = "Amazon_Reviews_original_dataset_v1"
    client = bigquery.Client()
    dataset_ref = client.dataset(dataset_id)

    try:
        client.get_dataset(dataset_ref)  # Check if dataset exists
        print(f" Dataset {dataset_id} already exists.")
    except Exception:
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)
        print(f" Created dataset {dataset_id}.")

def upload_to_bigquery(df):
    """Uploads a Pandas DataFrame to a BigQuery table."""
    project_id = "spheric-engine-451615-a8"
    dataset_id = "Amazon_Reviews_original_dataset_v1"
    table_id = "Amazon_dataset_V1"
    client = bigquery.Client()

    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f" Uploaded {len(df)} rows to {table_ref}")
    log_event(" Data Successfully Processed and Loaded into BigQuery!")
