import requests

DEPARTURE_URL = "https://pcsdata.njtransit.com/api/BUSDV2/getBusDV"


def fetch_pabt_departures(token: str):
    """Fetches raw departure data for Port Authority Bus Terminal (PABT)."""
    if not token:
        print("Authentication token is missing. Cannot fetch data.")
        return None

    try:
        # The API seems to limit the response to ~60 minutes regardless of the 'time' parameter.
        # We request 90 minutes just in case, but rely on the database accumulation for history.
        response = requests.post(
            DEPARTURE_URL,
            data={
                "token": token,
                "stop": "PABT",
                "time": 90
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching departure data: {e}")
        return None
