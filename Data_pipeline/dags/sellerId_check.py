from google.cloud import storage
import pandas as pd
from io import StringIO

# Set up your GCP credentials (Make sure you are authenticated)
BUCKET_NAME = "ai_chatbot_seller_central"  # Change to your bucket name
FILE_PATH = "reviews_processed.csv"  # Change to your file path in GCS

def get_sellers_by_asin(asin=None, parent_asin=None):
    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(FILE_PATH)

    # Read file into memory
    csv_data = blob.download_as_text()
    df = pd.read_csv(StringIO(csv_data))

    # Check if required columns exist
    required_cols = {"asin", "parent_asin", "seller_id"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns. Expected: {required_cols}")

    # Filter based on ASIN or Parent ASIN
    if asin:
        filtered_df = df[df["asin"] == asin]
    elif parent_asin:
        filtered_df = df[df["parent_asin"] == parent_asin]
    else:
        raise ValueError("Provide either an ASIN or Parent ASIN.")

    # Get unique seller IDs
    seller_ids = filtered_df["seller_id"].unique().tolist()

    return seller_ids

# Example usage
asin_to_search = "B07L6CFNH6"  # Replace with actual ASIN
parent_asin_to_search = None  # Replace with actual Parent ASIN if needed

sellers = get_sellers_by_asin(asin=asin_to_search, parent_asin=parent_asin_to_search)
print(f"Sellers for ASIN {asin_to_search}: {sellers}")
