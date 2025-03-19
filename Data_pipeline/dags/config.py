
GCP_CREDENTIALS_PATH = "/opt/airflow/dags/gcp-credentials.json"
BUCKET_NAME = "ai_chatbot_seller_central"
FILE_NAME = "new_data_sentiment.csv"

# import os
# import json
# from dotenv import load_dotenv

# # Load environment variables from .env
# load_dotenv()

# # Read GCP credentials from .env and save it as a temporary JSON file
# GCP_CREDENTIALS_JSON = os.getenv("GCP_CREDENTIALS_JSON")
# GCP_CREDENTIALS_PATH = "/tmp/gcp-credentials.json"

# # Write JSON string to a temporary file
# if GCP_CREDENTIALS_JSON:
#     with open(GCP_CREDENTIALS_PATH, "w") as f:
#         f.write(GCP_CREDENTIALS_JSON)

# # GCP Storage & BigQuery details
# BUCKET_NAME = os.getenv("BUCKET_NAME")
# FILE_NAME = os.getenv("FILE_NAME")