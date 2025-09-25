import requests
import json
from .config import settings

AUTH_URL = "https://pcsdata.njtransit.com/api/BUSDV2/authenticateUser"


def get_token():
    """Authenticates with the NJ Transit API and returns a new token."""
    try:
        response = requests.post(
            AUTH_URL,
            data={"username": settings.njt_username, "password": settings.njt_password}
        )
        response.raise_for_status()

        response_data = response.json()
        new_token = response_data.get("UserToken")

        if not new_token:
            print("Authentication successful but no UserToken found in response.")
            return None

        print("Successfully authenticated and received new token.")
        return new_token

    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error authenticating or parsing JSON from API: {e}")
        return None

