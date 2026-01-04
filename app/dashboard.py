import streamlit as st
import polars as pl
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
from streamlit.errors import StreamlitAPIException

# --- Page Configuration ---
st.set_page_config(
    page_title="PABT Departures",
    page_icon="🚌",
)


# --- Data Loading ---
# This logic checks for the Streamlit cloud secret first,
# then falls back to the local .env variable for local development.
try:
    DB_URL = st.secrets["DATABASE_URL"]
except (StreamlitAPIException, KeyError):
    DB_URL = os.getenv("DATABASE_URL")

TABLE_NAME = "departures"


@st.cache_data(ttl=60)
def load_data():
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
departures_df, last_updated = load_data()


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

        st.dataframe(
            summary_df.select("Route Variation", pl.col("route_name").alias("Route Name"), "Next Departures", "Gates"),
            width='stretch',
            hide_index=True,
            height=800
        )
    else:
        # This handles the case where the filter results in no data
        st.info("No departures found in the selected time window.")
else:
    st.info("No departure data available.")
