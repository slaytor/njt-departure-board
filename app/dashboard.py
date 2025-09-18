import streamlit as st
import duckdb
import os
from datetime import datetime

# ... (page config is the same) ...

DATA_FILE = "data/departures.parquet"


def load_data():
    """Loads departure data from the Parquet file."""
    if not os.path.exists(DATA_FILE):
        st.warning("Data file not found. Please run the pipeline first.")
        return None, None # Return None for the dataframe

    try:
        con = duckdb.connect()
        # --- CHANGE THIS LINE ---
        # from: df = con.execute(f"SELECT * FROM '{DATA_FILE}'").fetchdf()
        # to:
        df = con.execute(f"SELECT * FROM '{DATA_FILE}'").pl()
        # --- END CHANGE ---
        con.close()

        last_updated_ts = os.path.getmtime(DATA_FILE)
        last_updated_dt = datetime.fromtimestamp(last_updated_ts)
        return df, last_updated_dt
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None


# --- Main Application ---
# ... (rest of the file is the same) ...
st.title("🚌 Port Authority Bus Terminal Departures")

departures_df, last_updated = load_data()

if last_updated:
    st.caption(f"Last Updated: {last_updated.strftime('%Y-%m-%d %I:%M:%S %p')}")

# Check if the dataframe is not None and not empty
if departures_df is not None and not departures_df.is_empty():
    st.dataframe(departures_df, use_container_width=True, hide_index=True)
else:
    st.info("No departure data available.")
