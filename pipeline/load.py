import polars as pl
import psycopg2
import psycopg2.extras


TABLE_NAME = "departures"


def save_to_postgres(df: pl.DataFrame, settings):
    """
    Connects to Postgres, ensures the table exists, and performs an idempotent bulk insert.
    """
    if df.is_empty():
        print("DataFrame is empty. Nothing to save.")
        return

    db_url = settings.database_url
    if not db_url:
        raise ValueError("Database URL not found in settings.")

    conn = None
    try:
        conn = psycopg2.connect(db_url)
        with conn.cursor() as cursor:
            # Create the table if it doesn't exist, defining the schema and primary key
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    "Route" VARCHAR,
                    "Destination" VARCHAR,
                    "Departs" VARCHAR,
                    "Gate" VARCHAR,
                    "departure_datetime" TIMESTAMPTZ,
                    "Route Variation" VARCHAR,
                    "route_name" VARCHAR,
                    PRIMARY KEY ("Route", "Destination", "departure_datetime")
                );
            """)

            # Prepare data and query for the insert
            cols = df.columns
            data_to_insert = list(df.iter_rows())
            conflict_cols = '"Route", "Destination", "departure_datetime"'
            insert_query = f"""
                INSERT INTO {TABLE_NAME} ({", ".join(f'"{col}"' for col in cols)})
                VALUES %s
                ON CONFLICT ({conflict_cols}) DO NOTHING;
            """

            # Use execute_values for an efficient bulk insert
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
