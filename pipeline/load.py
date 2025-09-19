import polars as pl
import psycopg2
import psycopg2.extras


TABLE_NAME = "departures"


def save_to_postgres(df: pl.DataFrame, settings):
    """
    Connects to Postgres and performs an idempotent bulk insert.
    """
    if df.is_empty():
        print("DataFrame is empty. Nothing to save.")
        return

    db_url = settings.database_url
    if not db_url:
        raise ValueError("Database URL not found in settings.")

    # Get column names and convert dataframe to a list of tuples
    cols = df.columns
    data_to_insert = list(df.iter_rows())

    # The column names for the ON CONFLICT clause must match the PRIMARY KEY you created
    conflict_cols = '"Route", "Destination", "departure_datetime"'

    # Prepare the SQL query
    insert_query = f"""
        INSERT INTO {TABLE_NAME} ({", ".join(f'"{col}"' for col in cols)})
        VALUES %s
        ON CONFLICT ({conflict_cols}) DO NOTHING;
    """

    conn = None
    try:
        conn = psycopg2.connect(db_url)
        with conn.cursor() as cursor:
            psycopg2.extras.execute_values(
                cursor, insert_query, data_to_insert
            )
            print(f"Successfully inserted or ignored {cursor.rowcount} records.")
        conn.commit()
    except Exception as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
