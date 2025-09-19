from dotenv import load_dotenv

load_dotenv()

from .auth import get_token
from .extract import fetch_pabt_departures
from .transform import transform_departures
from .load import save_to_postgres
from .config import settings


def run_pipeline():
    """Executes the full data pipeline."""
    print("Starting the NJ Transit data pipeline...")

    token = get_token()
    raw_data = fetch_pabt_departures(token)

    if raw_data:
        clean_df = transform_departures(raw_data)
        save_to_postgres(clean_df, settings)

    print("Pipeline run finished.")


if __name__ == "__main__":
    run_pipeline()
