import pandas as pd
from google.cloud import bigquery
import logging
# Set up logging (optional; adjust format as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_metadata(asin: str) -> pd.DataFrame:
    """
    Fetches product metadata for a given ASIN from BigQuery.
    Adjust the query and table names as necessary.
    """
    client = bigquery.Client()
    query = f"""
    SELECT parent_asin, main_category, title, average_rating, rating_number, features, description, price, store, categories, bought_together
    FROM `spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v4.meta_data`
    WHERE parent_asin = '{asin}'
    """
    try:
        meta_df = client.query(query).to_dataframe()
        logger.info(f"Fetched {len(meta_df)} metadata records for ASIN: {asin}")
    except Exception as e:
        logger.exception(f"Error fetching metadata for ASIN {asin}: {e}")
        meta_df = pd.DataFrame()
    return meta_df