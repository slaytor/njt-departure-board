import os
import polars as pl
import duckdb  # Keep for easy in-memory processing before loading

DB_URL = os.getenv("DATABASE_URL")
TABLE_NAME = "departures"


def save_to_postgres(df: pl.DataFrame):
    if df.is_empty():
        print("DataFrame is empty. Nothing to save.")
        return

    if not DB_URL:
        raise ValueError("DATABASE_URL environment variable is not set.")

    # Polars can write directly to a SQL database
    # The 'if_exists="append"' combined with a primary key on the remote table
    # will cause duplicates to fail, effectively ignoring them.
    df.write_database(
        table_name=TABLE_NAME,
        connection=DB_URL,
        if_exists="append"
    )

    print(f"Wrote {len(df)} records to Postgres.")
