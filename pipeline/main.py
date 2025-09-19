from .auth import get_token
from .extract import fetch_pabt_departures
from .transform import transform_departures
from .load import save_to_postgres


def run_pipeline():
    """Executes the full data pipeline."""
    print("Starting the NJ Transit data pipeline...")

    # 1. Authenticate and get token
    token = get_token()

    # 2. Extract data from API
    raw_data = fetch_pabt_departures(token)

    if raw_data:
        # 3. Transform and validate data
        clean_df = transform_departures(raw_data)

        # 4. Load data to Parquet file
        save_to_postgres(clean_df)

    print("Pipeline run finished.")


if __name__ == "__main__":
    run_pipeline()
