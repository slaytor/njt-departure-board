import polars as pl
import duckdb

DATA_PATH = "data/departures.parquet"


def save_to_parquet(df: pl.DataFrame):
    """Saves the DataFrame to a Parquet file using DuckDB."""
    if df.is_empty():
        print("DataFrame is empty. Nothing to save.")
        return

    try:
        # Use DuckDB to efficiently write the Parquet file
        con = duckdb.connect()
        con.execute(f"COPY df TO '{DATA_PATH}' (FORMAT PARQUET)")
        con.close()
        print(f"Successfully saved {len(df)} records to {DATA_PATH}")
    except Exception as e:
        print(f"Error saving data to Parquet file: {e}")

