import polars as pl
from pydantic import BaseModel, ValidationError
from typing import Optional


# Pydantic model for data validation
class Departure(BaseModel):
    route: str
    destination: str
    departs: str
    gate: Optional[str] = "N/A"


def transform_departures(data: dict):
    """Transforms raw API data into a clean Polars DataFrame."""
    if not data or "DVTrip" not in data or not isinstance(data["DVTrip"], list):
        print("No valid departure data found.")
        return pl.DataFrame() # Return empty DataFrame if no data

    # Use Pydantic to validate each trip
    valid_trips = []
    for trip in data["DVTrip"]:
        try:
            departure = Departure(
                route=trip.get("public_route", "N/A"),
                destination=trip.get("header", "N/A"),
                departs=trip.get("departuretime", "N/A"),
                gate=trip.get("lanegate"),
            )
            valid_trips.append(departure.dict())
        except ValidationError as e:
            print(f"Data validation error for a trip, skipping: {e}")

    if not valid_trips:
        return pl.DataFrame()

    # Convert to Polars DataFrame for any further manipulation
    df = pl.DataFrame(valid_trips)

    # Rename columns for the final display
    df = df.rename({
        "route": "Route",
        "destination": "Destination",
        "departs": "Departs",
        "gate": "Gate",
    })

    return df

