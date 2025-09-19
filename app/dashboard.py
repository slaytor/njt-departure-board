# app/dashboard.py
import streamlit as st
import duckdb
import polars as pl
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# --- Page Configuration ---
st.set_page_config(
    page_title="PABT Departures",
    page_icon="🚌",
    layout="wide"
)


# --- Data Loading ---
DB_URL = st.secrets["DATABASE_URL"] # Streamlit handles secrets this way
TABLE_NAME = "departures"


@st.cache_data(ttl=60)
def load_data():
    try:
        # Polars can read directly from a SQL query
        query = f"SELECT * FROM {TABLE_NAME}"
        df = pl.read_database_uri(query=query, uri=DB_URL)

        # --- START DEBUGGING ---
        st.write("--- Inside load_data() ---")
        st.write(f"Successfully connected and ran query. Found {len(df)} rows.")
        st.write("First 3 rows of data from DB:")
        st.write(df.head(3))
        st.write("--------------------------")
        # --- END DEBUGGING ---

        # Get the latest update time from the data itself
        last_updated = df["departure_datetime"].max()
        return df, last_updated
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None


# --- Main Application ---
st.title("🚌 Port Authority Bus Terminal Departures")


# --- UI Controls ---
col1, col2, col3 = st.columns([1, 2, 3])

with col1:
    time_window = st.number_input(
        "Show departures in the next (minutes):",
        min_value=5,
        max_value=180,
        value=15,
        step=5
    )


# --- Load Data ---
departures_df, last_updated = load_data()


# --- Data Processing and Display ---
if departures_df is not None and not departures_df.is_empty():
    eastern_tz = ZoneInfo("America/New_York")
    now = datetime.now(eastern_tz)
    end_time = now + timedelta(minutes=time_window)

    # Convert, filter, and sort data
    sorted_df = (
        departures_df
        .with_columns(pl.col("departure_datetime").dt.convert_time_zone("America/New_York"))
        .filter(pl.col("departure_datetime").is_between(now, end_time))
        .sort("departure_datetime")
    )

    # Display the count of filtered rows
    col1.metric("Current Departures", len(sorted_df))
    if last_updated:
        st.caption(f"Last Updated: {last_updated.strftime('%Y-%m-%d %I:%M:%S %p')}")

    # Reorder the columns for display
    display_df = sorted_df.select(
        "Departs",
        "Route",
        "Destination",
        "Gate"
    )

    # Extend the display box
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=800
    )
else:
    st.info("No departure data available.")
