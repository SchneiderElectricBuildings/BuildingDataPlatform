# Retrieve Auth Token (Python)

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

## Goal

Shows how to request a BDP API access token with the OAuth 2.0 client credentials flow, using the credential details from the BDP Portal, and how to use and refresh that token when calling the API.

The folder contains two short scripts:

| Script | What it shows |
| --- | --- |
| `get_token.py` | The simplest way to request a token and print it |
| `call_api.py` | A more realistic pattern: get a token, reuse it while it is valid, refresh it when needed, and call `GET /api/Sites` |

## Prerequisites

- Python 3.9 or later
- Tenant ID, Client ID, Client Secret, and Scopes (See [Retrieve Client Credentials](../../docs/retrieve-client-credentials.md))
- Network: Outbound HTTPS (443) to `login.microsoftonline.com` and `ecostruxure-building-platform-api-uat.se.app`

## Steps

### 1. Go to the folder

```bash
cd examples/retrieve-auth-token-python
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your client credentials

Choose one method.

**Option A:** `.env` file

1. Copy `.env.template` to `.env`.
2. Set your values:

    ```dotenv
    BDP_TENANT_ID=00000000-0000-0000-0000-000000000000
    BDP_CLIENT_ID=00000000-0000-0000-0000-000000000000
    BDP_CLIENT_SECRET=your-client-secret
    BDP_SCOPES=api://.../.default
    ```

**Option B:** environment variables

```bash
# bash
export BDP_TENANT_ID="00000000-0000-0000-0000-000000000000"
export BDP_CLIENT_ID="00000000-0000-0000-0000-000000000000"
export BDP_CLIENT_SECRET="your-client-secret"
export BDP_SCOPES="api://.../.default"
```
or
```powershell
# powershell
$env:BDP_TENANT_ID = "00000000-0000-0000-0000-000000000000"
$env:BDP_CLIENT_ID = "00000000-0000-0000-0000-000000000000"
$env:BDP_CLIENT_SECRET = "your-client-secret"
$env:BDP_SCOPES = "api://.../.default"
```

If both are set, the environment variable wins.

### 4. Request a token

```bash
python get_token.py
```

The script sends one `POST` to the Microsoft identity platform and prints the `access_token` from the response:

```http
POST https://login.microsoftonline.com/{BDP_TENANT_ID}/oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded

client_id={BDP_CLIENT_ID}&scope={BDP_SCOPES}&client_secret={BDP_CLIENT_SECRET}&grant_type=client_credentials
```

```python
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
```

### 5. Use the token to call the API

```bash
python call_api.py
```

In a real application you do not request a new token for every call. The script keeps the token and its expiry time, and only requests a new one when there is none yet, or when it expires within the next minute:

```python
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
```

Every API call asks for the token first, then sends it as a bearer token:

```http
GET https://ecostruxure-building-platform-api-uat.se.app/api/Sites
Authorization: Bearer {access_token}
X-Api-Version: 3.0
```

The script calls `GET /api/Sites` twice: the first call requests a token, the second one reuses it.

## Expected Outcome

- `get_token.py` prints one long string starting with `eyJ`: your access token.
- `call_api.py` prints `requesting a new token` **once**, followed by the JSON list of sites, twice.

Expected output sample of `call_api.py`:

```text
requesting a new token
[{"id": "8f6...c9d", "name": "Example Site", ...}]
[{"id": "8f6...c9d", "name": "Example Site", ...}]
```

If something is wrong, the script stops with the HTTP status of the failing call.

## Notes

### Token lifetime

The token response includes `expires_in`, in seconds (typically about one hour). Keep the token and reuse it until shortly before it expires, as `call_api.py` does, instead of requesting a token for every call.

### Reusing the token with the other examples

The token printed by `get_token.py` is a regular BDP API token. You can use it as `BDP_API_TOKEN` in the [REST Quickstart](../rest-quickstart-python/README.md) and [GraphQL Quickstart](../graphql-quickstart-python/README.md). Treat it as a secret: anyone who has it can call the API until it expires.

### Common failures

Table - Responses and what they mean

| Response | Meaning |
| --- | --- |
| **400** from the token endpoint | `BDP_TENANT_ID`, `BDP_CLIENT_ID`, or `BDP_SCOPES` is wrong, or a value is empty |
| **401** from the token endpoint | `BDP_CLIENT_SECRET` is wrong or expired (check **Expires On**) |
| **401** from the API | Token acquired for the wrong scope, or expired |
| **403** from the API | Token valid, but your consumer is not authorized for that data |

The token endpoint response body explains the exact reason in `error_description` (for example `AADSTS700016: Application ... was not found in the directory`).

See [Troubleshooting](../../docs/troubleshooting.md) for more.

## What's Next

- [REST Quickstart (Python)](../rest-quickstart-python/README.md)
- [GraphQL Quickstart (Python)](../graphql-quickstart-python/README.md)
- [Access Model and Permissions](../../docs/access-model-and-permissions.md)
- [Retrieve Auth Token (Postman)](../retrieve-auth-token-postman/README.md)
