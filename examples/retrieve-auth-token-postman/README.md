# Retrieve Auth Token (Postman)

![Postman](https://img.shields.io/badge/Postman-FF6C37?logo=postman&logoColor=white)

> This example ships an API collection in the Postman Collection Format v2.1. That
> format is not Postman-exclusive: it also imports and runs in Insomnia, Bruno,
> Thunder Client, Hoppscotch, and headless.

## Goal

Requests a BDP API access token with the OAuth 2.0 client credentials flow, using
the credential details from the BDP Portal stored in your client's vault, then uses
that token for one REST call, no code to run.

The collection contains two requests:

- `Get Access Token` (`POST` to the Microsoft identity platform token endpoint)
- `List Sites` (REST `/api/Sites`, authorized with the token from the first request)

## Prerequisites

- A REST client that supports the Postman Collection Format v2.1 (desktop app or web)
- Tenant ID, Client ID, Client Secret, and Scopes (See [Retrieve Client Credentials](../../docs/retrieve-client-credentials.md))
- Network: Outbound HTTPS (443) to `login.microsoftonline.com` and `ecostruxure-building-platform-api-uat.se.app`

## Files

| File | Purpose |
| --- | --- |
| `bdp-retrieve-auth-token.json` | The collection with the token request, the verification request, and variables |

## Steps

### 1. Import the collection

Follow [Importing an API Collection File](../../docs/importing-api-collections.md) to
import `bdp-retrieve-auth-token.json` into your client.

### 2. Set your client credentials

Follow [Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md)
to store each value as its own vault secret:

| Vault secret | Portal field |
| --- | --- |
| `BDP_TENANT_ID` | **Tenant ID** |
| `BDP_CLIENT_ID` | **Client ID** |
| `BDP_CLIENT_SECRET` | **View Secret** -> Client Secret |
| `BDP_SCOPES` | **Scopes** |

The `Get Access Token` request already references them as `{{vault:BDP_TENANT_ID}}`,
`{{vault:BDP_CLIENT_ID}}`, `{{vault:BDP_CLIENT_SECRET}}`, and `{{vault:BDP_SCOPES}}`,
so once the secrets exist in your vault, no further edits are needed. Never edit the
committed file to add real values.

### 3. Request a token

Run `Get Access Token`. It sends:

```http
POST https://login.microsoftonline.com/{{vault:BDP_TENANT_ID}}/oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded

client_id={{vault:BDP_CLIENT_ID}}&scope={{vault:BDP_SCOPES}}&client_secret={{vault:BDP_CLIENT_SECRET}}&grant_type=client_credentials
```

A test script stores the `access_token` from the response in the `accessToken`
collection variable.

### 4. Use the token

Run `List Sites`. The collection uses collection-level bearer auth, so every request
except `Get Access Token` sends:

```http
GET https://ecostruxure-building-platform-api-uat.se.app/api/Sites?take={{take}}
Authorization: Bearer {{accessToken}}
X-Api-Version: {{apiVersion}}
```

You can also run the whole collection with your client's runner (Postman calls this
the **Runner**); the requests are already in the right order.

## Expected Outcome

- `Get Access Token` returns HTTP `200`, and both its tests pass.
- The console shows `accessToken set, expires in 3599 seconds` (never the token value).
- `List Sites` returns HTTP `200` with a JSON body.

Expected output sample (body of `Get Access Token`):

```json
{
  "token_type": "Bearer",
  "expires_in": 3599,
  "ext_expires_in": 3599,
  "access_token": "eyJ0eX..."
}
```

## Notes

### Variables

Table - Collection variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `apiVersion` | `3.0` | Value sent in the `X-Api-Version` header |
| `take` | `5` | Page size for `List Sites` |
| `accessToken` | empty | Set by `Get Access Token`, used by the collection bearer auth |

The four client credentials are not collection variables; they are referenced
directly from your client's vault. See
[Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md).

To point the collection at production, edit the URL of `List Sites` to
`https://ecostruxure-building-platform-api.se.app`.

### Built-in OAuth 2.0 helper

Most clients also offer an **OAuth 2.0** authorization type with a
**Client Credentials** grant, which requests and refreshes the token for you. Use
these values if you prefer it over the explicit request:

- Access Token URL: `https://login.microsoftonline.com/{{vault:BDP_TENANT_ID}}/oauth2/v2.0/token`
- Client ID: `{{vault:BDP_CLIENT_ID}}`
- Client Secret: `{{vault:BDP_CLIENT_SECRET}}`
- Scope: `{{vault:BDP_SCOPES}}`
- Client Authentication: Send client credentials in body

The explicit `Get Access Token` request is kept in this collection because it shows
exactly what is sent, and works the same way in every compatible client.

### Token lifetime

Access tokens are short-lived by design (`expires_in`, typically about one hour).
Run `Get Access Token` again when `List Sites` starts failing with `401`.

### Running from CI

Postman Vault is a Postman-app-local feature; `{{vault:...}}` references do not
resolve when the collection runs headless with
[Newman](https://github.com/postmanlabs/newman). For CI, use a copy of the collection
where the vault references are plain variables (`{{BDP_TENANT_ID}}`, and so on), and
pass them at run time instead of storing them:

```bash
newman run bdp-retrieve-auth-token.json \
  --env-var "BDP_TENANT_ID=$BDP_TENANT_ID" \
  --env-var "BDP_CLIENT_ID=$BDP_CLIENT_ID" \
  --env-var "BDP_CLIENT_SECRET=$BDP_CLIENT_SECRET" \
  --env-var "BDP_SCOPES=$BDP_SCOPES"
```

### Common failures

Table - Responses and what they mean

| Response | Meaning |
| --- | --- |
| **400 invalid_request** | `BDP_TENANT_ID` is wrong, or a value is empty |
| **400 unauthorized_client** | `BDP_CLIENT_ID` does not exist in that tenant |
| **400 invalid_scope** | `BDP_SCOPES` is not exactly the value shown in the portal |
| **401 invalid_client** | `BDP_CLIENT_SECRET` is wrong or expired (check **Expires On**) |
| **401** from `List Sites` | `accessToken` empty, expired, or for the wrong scope |
| **403** from `List Sites` | Token valid, but your consumer is not authorized for that data |

The collection test scripts print a matching hint in the console.

See [Troubleshooting](../../docs/troubleshooting.md) for more.

## What's Next

- [REST Quickstart (Postman)](../rest-quickstart-postman/README.md)
- [GraphQL Quickstart (Postman)](../graphql-quickstart-postman/README.md)
- [Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md)
- [Access Model and Permissions](../../docs/access-model-and-permissions.md)
- [Retrieve Auth Token (Python)](../retrieve-auth-token-python/README.md)
