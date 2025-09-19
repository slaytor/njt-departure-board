from datetime import datetime
import polars as pl
from pydantic import BaseModel, Field, ValidationError # Import Field
from typing import Optional
from zoneinfo import ZoneInfo


class Departure(BaseModel):
    departs: str = Field(alias='departuretime')
    route: str = Field(alias='public_route')
    destination: str = Field(alias='header')
    gate: Optional[str] = Field(alias='lanegate', default="N/A")
    sched_dep_time: Optional[str]

    class Config:
        # This allows Pydantic to find our fields even if not all API fields are defined
        extra = 'ignore'


def transform_departures(data: dict):
    """Transforms raw API data into a clean Polars DataFrame."""
    if not data or "DVTrip" not in data or not isinstance(data["DVTrip"], list):
        print("No valid departure data found.")
        return pl.DataFrame()

    valid_trips = []
    for trip in data["DVTrip"]:
        try:
            # Pydantic will now use the aliases to find the correct data
            departure = Departure.model_validate(trip)
            valid_trips.append(departure.model_dump())
        except ValidationError as e:
            print(f"Data validation error for a trip, skipping: {e}")

    if not valid_trips:
        return pl.DataFrame()

    df = pl.DataFrame(valid_trips)

    # Filter out any rows where the scheduled time is missing
    df = df.filter(pl.col("sched_dep_time").is_not_null())

    # Parse the full timestamp string from the API
    df = df.with_columns(
        pl.col("sched_dep_time")
          .str.to_datetime(format="%m/%d/%Y %I:%M:%S %p", strict=False)
          .dt.replace_time_zone("America/New_York")
          .alias("departure_datetime")
    )

    # We can now use our clean Pydantic field names
    df = df.select(
        pl.col("departs").alias("Departs"),
        pl.col("route").alias("Route"),
        pl.col("destination").alias("Destination"),
        pl.col("gate").alias("Gate"),
        pl.col("departure_datetime")
    )

    return df
