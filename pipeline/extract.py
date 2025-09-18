import requests

DEPARTURE_URL = "https://pcsdata.njtransit.com/api/BUSDV2/getBusDV"


def fetch_pabt_departures(token: str):
    """Fetches raw departure data for Port Authority Bus Terminal (PABT)."""
    if not token:
        print("Authentication token is missing. Cannot fetch data.")
        return None

    try:
        response = requests.post(
            DEPARTURE_URL,
            data={"token": token, "stop": "PABT"}
        )
        response.raise_for_status()
        print(response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching departure data: {e}")
        return None
