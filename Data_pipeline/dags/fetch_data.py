import os
import requests
import logging
import gzip
from google.cloud import storage
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import config
# Set GCP credentials dynamically from config.py
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GCP_CREDENTIALS_PATH

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Dataset URLs (replace with the correct Hugging Face URL)
DATASET_URLS = [
    "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/review_categories/Health_and_Personal_Care.jsonl.gz",
    "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/review_categories/All_Beauty.jsonl.gz",
    "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/review_categories/Musical_Instruments.jsonl.gz",
    "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/review_categories/Appliances.jsonl.gz",
    "https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/raw/review_categories/Amazon_Fashion.jsonl.gz"
]

BUCKET_NAME = "ai_chatbot_seller_central"

def create_retry_session():
    """Creates a session with retry logic."""
    session = requests.Session()
    retry = Retry(
        total=5,  # Total number of retries
        backoff_factor=1,  # Factor for delay between retries
        status_forcelist=[500, 502, 503, 504]  # Retry on server errors
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def upload_to_gcs_from_url():
    for url in DATASET_URLS:
        bucket_name=config.BUCKET_NAME
        """Download, extract in-memory, and upload directly to GCS."""
        filename = url.split("/")[-1]  # Extract file name (e.g., All_Beauty.jsonl.gz)
        jsonl_filename = filename.replace(".gz", "")  # Extracted JSONL filename

        logging.info(f"Downloading dataset: {filename}")

        session = create_retry_session()  # Use session with retries
        try:
            response = session.get(url, stream=True, timeout=300)  # Set timeout to 300 seconds for large files
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading {filename}: {e}")
            return

        # Check if the content length matches the expected size
        content_length = response.headers.get('Content-Length')
        if content_length:
            logging.info(f"Content-Length for {filename}: {content_length} bytes")

        # Initialize GCS client and bucket
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"reviews/{jsonl_filename}")  # Store inside 'reviews/' folder in GCS

        try:
            # Read the gzip file as a stream and upload to GCS directly
            with gzip.GzipFile(fileobj=response.raw, mode="rb") as gzipped_file:
                blob.upload_from_file(gzipped_file, content_type="application/jsonl", rewind=True, size=1024 * 1024 * 50)  # 50MB chunks
            logging.info(f"Uploaded {jsonl_filename} to GCS successfully.")
        except Exception as e:
            logging.error(f"Error uploading {jsonl_filename} to GCS: {e}")
# upload_to_gcs_from_url()
# if __name__ == "__main__":
#     for url in DATASET_URLS:
#         upload_to_gcs_from_url(url, BUCKET_NAME)
