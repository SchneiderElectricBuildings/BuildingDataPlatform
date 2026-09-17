# REST Quickstart (Postman)

![Postman](https://img.shields.io/badge/Postman-FF6C37?logo=postman&logoColor=white)

## Goal

Makes the same authenticated REST calls as
[REST Quickstart (Python)](../rest-quickstart-python/README.md), but from Postman,
with no code to run.

The collection contains three requests:

- `List Organizations`
- `List Sites`
- `List Buildings by Site` (requires a `siteId`)

## Prerequisites

- Postman (desktop app or web, v10 or later)
- API token (See [Setup Credentials](../../docs/setup-credentials.md) )
- Network: Outbound HTTPS (443) to `ecostruxure-building-platform-api-uat.se.app`

## Files

| File | Purpose |
| --- | --- |
| `BDP-REST-Quickstart.postman_collection.json` | The collection with the three requests |
| `BDP-REST-Quickstart.postman_environment.template.json` | Environment template, token left empty |

## Steps

### 1. Import the collection

In Postman: **Import** -> **Files** -> select
`examples/rest-quickstart-postman/BDP-REST-Quickstart.postman_collection.json`.

### 2. Import and select the environment

Import `BDP-REST-Quickstart.postman_environment.template.json` the same way, then
select **BDP - UAT (template)** in the environment selector (top right).

### 3. Set your token

Open the environment, and paste your token into `BDP_API_TOKEN`:

- Put it in the **Current value** column only.
- Leave **Initial value** empty so the token is never shared or exported.

The collection uses collection-level bearer auth, so every request sends:

```text
Authorization: Bearer {{BDP_API_TOKEN}}
```

### 4. Send a request

Run `List Sites`. Then either:

- run `List Buildings by Site` directly, because `List Sites` stores the first site id
  into the `siteId` environment variable, or
- set `siteId` yourself to any site GUID you are entitled to.

You can also run the whole collection with the **Runner**.

## Expected Outcome

- HTTP `200` with a JSON body.
- The `status is 200` test passes in the **Test Results** tab.
- `List Sites` writes a value into the `siteId` environment variable.

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
| `baseUrl` | `https://ecostruxure-building-platform-api-uat.se.app` | API host, no `/api` suffix |
| `apiVersion` | `3.0` | Value sent in the `X-Api-Version` header |
| `take` | `5` | Page size |
| `skip` | `0` | Page offset |
| `siteId` | empty | Required by `List Buildings by Site` |
| `BDP_API_TOKEN` | empty | Bearer token, set it in the environment |

Point the collection at production by changing `baseUrl` to
`https://ecostruxure-building-platform-api.se.app`.

### Authentication

Auth is defined once at collection level and inherited by every request, which keeps
the token in a single place. Tokens are short-lived by design; re-copy a fresh token
when requests start failing with `401`.

### `X-Api-Version`

Every REST operation declares this header. The collection sends `{{apiVersion}}`,
which defaults to `3.0`. `2.0` is also accepted; other values return
`400 Unsupported API Version was requested`.

### Running from CI

The collection also runs headless with [Newman](https://github.com/postmanlabs/newman),
passing the token as an environment variable instead of storing it in a file:

```bash
newman run BDP-REST-Quickstart.postman_collection.json \
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

The collection test script prints a matching hint in the Postman console.

See [Troubleshooting](../../docs/troubleshooting.md) for the 403 distinction.

## What's Next

- [Access Model and Permissions](../../docs/access-model-and-permissions.md)
- [Consuming Data](../../docs/consuming-data.md)
- [Explore REST operations from the OpenAPI bundle](../explore-rest-operations-python/README.md)
- [REST Quickstart (Python)](../rest-quickstart-python/README.md)
