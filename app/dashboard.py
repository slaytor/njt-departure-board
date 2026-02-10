import streamlit as st
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import sys
from streamlit.errors import StreamlitAPIException

# --- Path Setup for Pipeline Import ---
# Add the parent directory to sys.path so we can import the pipeline module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- Page Configuration ---
st.set_page_config(
    page_title="PABT Departures",
    page_icon="🚌",
    layout="wide"  # Use the full screen width
)

# --- Environment Setup ---
# Inject Streamlit secrets into environment variables so the pipeline config can read them.
# This is necessary because pydantic BaseSettings reads from os.environ.
try:
    # We iterate through secrets and set them as env vars if they match our expected keys
    # This covers NJT_USERNAME, NJT_PASSWORD, DATABASE_URL
    for key, value in st.secrets.items():
        if isinstance(value, str):
            os.environ[key] = value
except (FileNotFoundError, AttributeError):
    # Local development with .env file or no secrets.toml
    pass

# --- Pipeline Imports ---
# Import these AFTER setting os.environ so settings are initialized correctly
try:
    from pipeline.auth import get_token
    from pipeline.extract import fetch_pabt_departures
    from pipeline.transform import transform_departures
    from pipeline.load import save_to_postgres
    from pipeline.config import settings
except ImportError as e:
    st.error(f"Failed to import pipeline modules: {e}")
    st.stop()


# --- Data Loading ---
# This logic checks for the Streamlit cloud secret first,
# then falls back to the local .env variable for local development.
try:
    DB_URL = st.secrets["DATABASE_URL"]
except (StreamlitAPIException, KeyError):
    DB_URL = os.getenv("DATABASE_URL")

TABLE_NAME = "departures"


def run_pipeline_sync():
    """Runs the data pipeline synchronously to fetch fresh data."""
    try:
        # st.toast("Fetching latest data from NJ Transit...", icon="🔄")
        token = get_token()
        if not token:
            st.warning("Could not authenticate with NJ Transit.")
            return

        raw_data = fetch_pabt_departures(token)
        if raw_data:
            clean_df = transform_departures(raw_data)
            if not clean_df.is_empty():
                save_to_postgres(clean_df, settings)
                # st.toast("Data updated successfully!", icon="✅")
            else:
                st.warning("No valid departures found in API response.")
    except Exception as e:
        st.error(f"Pipeline error: {e}")


def load_data_from_db():
    """Queries the database for the latest departure data."""
    try:
        query = f"SELECT * FROM {TABLE_NAME}"
        df = pl.read_database_uri(query=query, uri=DB_URL)

        if df.is_empty():
            return df, None

        last_updated = df["departure_datetime"].min()
        return df, last_updated
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None


# --- Main Application ---
st.title("🚌 Port Authority Bus Terminal Departures")


# --- UI Controls ---
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    time_window = st.number_input(
        "Show departures in the next (minutes):",
        min_value=5,
        max_value=360,
        value=15,
        step=5,
        key="time_filter"
    )


# --- Load Data ---
# Logic: Run pipeline and load DB once per session (page load).
# Store result in session_state to avoid DB hits on UI interaction.
if "departures_df" not in st.session_state:
    with st.spinner('Refreshing departure data...'):
        run_pipeline_sync()
        df, last_upd = load_data_from_db()
        st.session_state["departures_df"] = df
        st.session_state["last_updated"] = last_upd

departures_df = st.session_state.get("departures_df")
last_updated = st.session_state.get("last_updated")


# --- Data Processing and Display ---
if departures_df is not None and not departures_df.is_empty():
    eastern_tz = ZoneInfo("America/New_York")
    now = datetime.now(eastern_tz)
    end_time = now + timedelta(minutes=time_window)

    df_with_tz = departures_df.with_columns(
        pl.col("departure_datetime").dt.convert_time_zone("America/New_York")
    )

    filtered_df = (
        df_with_tz
        .filter(pl.col("departure_datetime").is_between(now, end_time))
        .sort("departure_datetime")
    )

    # Place the first metric in the second column
    col2.metric("Total Departures", len(filtered_df))

    if last_updated:
        st.caption(f"Last Updated: {last_updated.strftime('%Y-%m-%d %I:%M:%S %p')}")

    if not filtered_df.is_empty():
        shown_routes = filtered_df.select("Route Variation", "route_name").unique()

        expanded_df = (
            df_with_tz
            .filter(pl.col("departure_datetime") >= now)
            .join(shown_routes, on=["Route Variation", "route_name"], how="inner")
            .sort("departure_datetime")
            .group_by("Route Variation", "route_name", maintain_order=True)
            .head(3)
        )

        summary_df = (
            expanded_df
            .sort("departure_datetime")
            .group_by("Route Variation", "route_name", maintain_order=True)
            .agg(
                pl.col("Departs").str.join(", "),
                pl.col("Gate").str.join(", ")
            )
            .rename({"Departs": "Next Departures", "Gate": "Gates"})
            .sort("Next Departures")
        )

        col3.metric("Displayed Rows", len(summary_df))

        # Calculate dynamic height based on number of rows
        # 35px is roughly the height of a row + header/padding adjustments
        # We set a max height to prevent it from being infinitely tall if there are 1000 rows
        row_height = 35
        header_height = 40
        calculated_height = (len(summary_df) * row_height) + header_height
        # Clamp the height between a minimum and a maximum
        final_height = max(min(calculated_height, 1200), 200)

        st.dataframe(
            summary_df.select("Route Variation", pl.col("route_name").alias("Route Name"), "Next Departures", "Gates"),
            width=None, # Let Streamlit handle width or use 'use_container_width'
            use_container_width=True,
            hide_index=True,
            height=final_height
        )
    else:
        # This handles the case where the filter results in no data
        st.info("No departures found in the selected time window.")
else:
    st.info("No departure data available.")
