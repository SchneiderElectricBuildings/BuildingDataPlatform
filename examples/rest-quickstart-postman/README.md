# REST Quickstart (Postman)

![Postman](https://img.shields.io/badge/Postman-FF6C37?logo=postman&logoColor=white)

> This example ships an API collection in the Postman Collection Format v2.1. That
> format is not Postman-exclusive: it also imports and runs in Insomnia, Bruno,
> Thunder Client, Hoppscotch, and headless.

## Goal

Makes the same authenticated REST calls as
[REST Quickstart (Python)](../rest-quickstart-python/README.md), but from an API
collection file, with no code to run.

The collection contains three requests:

- `List Organizations`
- `List Sites`
- `List Buildings by Site` (requires a `siteId`)

## Prerequisites

- A REST client that supports the Postman Collection Format v2.1 (desktop app or web)
- API token (See [Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md) )
- Network: Outbound HTTPS (443) to `ecostruxure-building-platform-api-uat.se.app`

## Files

| File | Purpose |
| --- | --- |
| `bdp-rest-quickstart.json` | The collection with the three requests and variables |

## Steps

### 1. Import the collection

Follow [Importing an API Collection File](../../docs/importing-api-collections.md) to
import `bdp-rest-quickstart.json` into your client.

### 2. Set your token

Follow [Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md)
to store your token as a vault secret named `BDP_API_TOKEN`. The collection's
authorization already references it as `{{vault:BDP_API_TOKEN}}`, so once the secret
exists in your vault, no further edits are needed. Never edit the committed file to add
a real token.

The collection uses collection-level bearer auth, so every request sends:

```text
Authorization: ******
```

### 3. Send a request

Run `List Sites`. Then either:

- run `List Buildings by Site` directly, because `List Sites` stores the first site id
  into the `siteId` variable, or
- set `siteId` yourself to any site GUID you are entitled to.

You can also run the whole collection with your client's runner (Postman calls this
the **Runner**).

## Expected Outcome

- HTTP `200` with a JSON body.
- The `status is 200` test passes in the test results panel.
- `List Sites` writes a value into the `siteId` variable.

Expected output sample (body of `List Sites`):

```json
[
  { "id": "8f6...c9d", "name": "Example Site" },
  { "id": "9ab...72e", "name": "North Campus" }
]
```

## Notes

### Variables

Table - Collection variables

| Variable | Default | Meaning |
| --- | --- | --- |
| `apiVersion` | `3.0` | Value sent in the `X-Api-Version` header |
| `take` | `5` | Page size |
| `skip` | `0` | Page offset |
| `siteId` | empty | Required by `List Buildings by Site` |

The host is set directly in each request's URL
(`https://ecostruxure-building-platform-api-uat.se.app`), not a variable. To point the
collection at production, edit the URL of each request to
`https://ecostruxure-building-platform-api.se.app`.

The token is not a collection variable; it is referenced directly from your client's
vault as `{{vault:BDP_API_TOKEN}}` in the collection's Authorization tab. See
[Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md).

### Authentication

Auth is defined once at collection level and inherited by every request, which keeps
the token in a single place. Tokens are short-lived by design; re-copy a fresh token
when requests start failing with `401`.

### `X-Api-Version`

Every REST operation declares this header. The collection sends `{{apiVersion}}`,
which defaults to `3.0`. `2.0` is also accepted; other values return
`400 Unsupported API Version was requested`.

### Running from CI

Postman Vault is a Postman-app-local feature; the `{{vault:BDP_API_TOKEN}}` reference
does not resolve when the collection runs headless with
[Newman](https://github.com/postmanlabs/newman). For CI, use a copy of the collection
where the authorization value is a plain variable, `{{BDP_API_TOKEN}}`, and pass it at
run time instead of storing it:

```bash
newman run bdp-rest-quickstart.json \
  --env-var "BDP_API_TOKEN=$BDP_API_TOKEN"
```

### Common failures

Table - Responses and what they mean

| Response | Meaning |
| --- | --- |
| **401** | Token expired or malformed |
| **403** with a JSON body | Token valid, but your consumer is not authorized for that data |
| **403** returning an HTML error page | Refused in front of the API, request did not reach the API |
| **400 Unsupported API Version** | `X-Api-Version` is not `2.0` or `3.0` |
| **200** with an empty result | Subscription rule is missing, or filters out everything |

The collection test script prints a matching hint in the console.

See [Troubleshooting](../../docs/troubleshooting.md) for the 403 distinction.

## What's Next

- [Importing an API Collection File](../../docs/importing-api-collections.md)
- [Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md)
- [Access Model and Permissions](../../docs/access-model-and-permissions.md)
- [Consuming Data](../../docs/consuming-data.md)
- [Explore REST operations from the OpenAPI bundle](../explore-rest-operations-python/README.md)
- [REST Quickstart (Python)](../rest-quickstart-python/README.md)
