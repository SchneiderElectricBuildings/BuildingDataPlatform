"""Request a BDP API access token and print it.

Usage:
    python get_token.py
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

tenant_id = os.environ["BDP_TENANT_ID"]

response = requests.post(
    f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
    data={
        "client_id": os.environ["BDP_CLIENT_ID"],
        "scope": os.environ["BDP_SCOPES"],
        "client_secret": os.environ["BDP_CLIENT_SECRET"],
        "grant_type": "client_credentials",
    },
    timeout=30,
)
response.raise_for_status()

print(response.json()["access_token"])
