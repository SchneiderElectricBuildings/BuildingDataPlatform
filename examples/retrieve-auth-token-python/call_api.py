"""Get a BDP API access token, reuse it while valid, and call the REST API.

Usage:
    python call_api.py
"""

import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://ecostruxure-building-platform-api-uat.se.app"
TOKEN_URL = f"https://login.microsoftonline.com/{os.environ['BDP_TENANT_ID']}/oauth2/v2.0/token"

_token = None
_expires_at = 0.0


def get_token():
    """Return a valid token, requesting a new one only when needed."""
    global _token, _expires_at

    # Refresh one minute early so a token never expires in the middle of a call.
    if _token is None or time.time() > _expires_at - 60:
        print("requesting a new token")
        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": os.environ["BDP_CLIENT_ID"],
                "scope": os.environ["BDP_SCOPES"],
                "client_secret": os.environ["BDP_CLIENT_SECRET"],
                "grant_type": "client_credentials",
            },
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()
        _token = body["access_token"]
        _expires_at = time.time() + body["expires_in"]

    return _token


def get_sites():
    response = requests.get(
        f"{API_BASE_URL}/api/Sites",
        headers={
            "Authorization": f"Bearer {get_token()}",
            "X-Api-Version": "3.0",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


# The first call requests a token, the second one reuses it.
print(get_sites())
print(get_sites())
