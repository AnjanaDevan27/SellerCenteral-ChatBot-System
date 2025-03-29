import pandas as pd
from google.cloud import bigquery
import logging
# Set up logging (optional; adjust format as needed)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_reviews(asin: str) -> pd.DataFrame:
    """
    Fetches product review data for a given ASIN from BigQuery.
    Adjust the query and table names to match your BigQuery dataset.
    """
    client = bigquery.Client()
    query = f"""
    SELECT parent_asin, rating, title, text, asin, user_id, timestamp, helpful_vote, verified_purchase, Category, seller_id, sentiment_label, sentiment_score
    FROM `spheric-engine-451615-a8.Amazon_Reviews_original_dataset_v4.Amazon_dataset_V4`
    WHERE parent_asin = '{asin}'
    """
    try:
        review_df = client.query(query).to_dataframe()
        logger.info(f"Fetched {len(review_df)} review records for ASIN: {asin}")
    except Exception as e:
        logger.exception(f"Error fetching reviews for ASIN {asin}: {e}")
        review_df = pd.DataFrame()
    return review_df

    