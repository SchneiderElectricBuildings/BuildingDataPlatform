# Retrieve Auth Token (Python)

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

## Goal

Requests a BDP API access token with the OAuth 2.0 client credentials flow, using
the credential details from the BDP Portal, then uses that token for one REST call to
prove it is accepted.

## Prerequisites

- Python 3.9 or later (standard library only, nothing to install)
- Tenant ID, Client ID, Client Secret, and Scopes (See [Retrieve Client Credentials](../../docs/retrieve-client-credentials.md))
- Network: Outbound HTTPS (443) to `login.microsoftonline.com` and `ecostruxure-building-platform-api-uat.se.app`

## Steps

### 1. Go to the folder

```bash
cd examples/retrieve-auth-token-python
```

### 2. Set your client credentials

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

### 3. Request a token

```bash
python get_token.py
```

The script:

1. Sends a `POST` to `https://login.microsoftonline.com/{BDP_TENANT_ID}/oauth2/v2.0/token`.
2. Reads `access_token` from the response.
3. Calls `GET /api/Sites?take=5` with `Authorization: Bearer {access_token}`.

Options:

```bash
# only request the token, skip the GET /api/Sites check
python get_token.py --no-verify

# write only the token to stdout, to reuse it with the other examples
python get_token.py --print-token
```

For example, to feed the [REST Quickstart](../rest-quickstart-python/README.md):

```bash
# bash
export BDP_API_TOKEN="$(python get_token.py --print-token)"
```
or
```powershell
# powershell
$env:BDP_API_TOKEN = python get_token.py --print-token
```

## Expected Outcome

- Exit code `0` when a token is acquired and the API accepts it.
- The token type and lifetime, with the token value masked.
- A compact list of sites returned with that token.

Expected output sample:

```text
POST https://login.microsoftonline.com/00000000-0000-0000-0000-000000000000/oauth2/v2.0/token
token: acquired
  token_type: Bearer
  expires_in: 3599 seconds
  access_token: eyJ0eX...a1B2
GET https://ecostruxure-building-platform-api-uat.se.app/api/Sites?take=5
status: 200
items: 2
  - 8f6...c9d | Example Site
  - 9ab...72e | North Campus
```

## Notes

### The call itself (minimal)

If you strip everything down, requesting a token is just:

1. Build the token URL with your tenant ID
2. Build a form body with `client_id`, `scope`, `client_secret`, and `grant_type=client_credentials`
3. Send a `POST` and read `access_token` from the JSON response

This is the smallest possible version of the call logic:

```python
import json
import urllib.parse
import urllib.request

form = urllib.parse.urlencode({
    "client_id": "YOUR_CLIENT_ID",
    "scope": "YOUR_SCOPES",
    "client_secret": "YOUR_CLIENT_SECRET",
    "grant_type": "client_credentials",
}).encode("utf-8")

request = urllib.request.Request(
    "https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/v2.0/token",
    data=form,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    method="POST",
)

with urllib.request.urlopen(request, timeout=30) as response:
    access_token = json.loads(response.read())["access_token"]
```

Then use the token like any other BDP API token:

```python
request = urllib.request.Request(
    "https://ecostruxure-building-platform-api-uat.se.app/api/Sites",
    headers={
        "Authorization": f"Bearer {access_token}",
        "X-Api-Version": "3.0",
        "Accept": "application/json",
    },
    method="GET",
)
```

That is the core network logic in `get_token.py`, without settings loading, argument
parsing, or error mapping.

### Token lifetime

The response includes `expires_in`, in seconds (typically about one hour). Cache the
token and request a new one shortly before it expires, instead of requesting a token
for every call.

### Common failures

Table - Responses and what they mean

| Response | Meaning |
| --- | --- |
| **400 invalid_request** | `BDP_TENANT_ID` is wrong, or a value is empty |
| **400 unauthorized_client** | `BDP_CLIENT_ID` does not exist in that tenant |
| **400 invalid_scope** | `BDP_SCOPES` is not exactly the value shown in the portal |
| **401 invalid_client** | `BDP_CLIENT_SECRET` is wrong or expired (check **Expires On**) |
| **401** from the API | Token acquired for the wrong scope |
| **403** from the API | Token valid, but your consumer is not authorized for that data |

See [Troubleshooting](../../docs/troubleshooting.md) for more.

## What's Next

- [REST Quickstart (Python)](../rest-quickstart-python/README.md)
- [GraphQL Quickstart (Python)](../graphql-quickstart-python/README.md)
- [Access Model and Permissions](../../docs/access-model-and-permissions.md)
- [Retrieve Auth Token (.NET)](../retrieve-auth-token-dotnet/README.md)
