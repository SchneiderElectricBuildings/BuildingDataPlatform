# REST Quickstart (Postman)

![Postman](https://img.shields.io/badge/Postman-FF6C37?logo=postman&logoColor=white)

> This example ships an API collection in the Postman Collection Format v2.1. That
> format is not Postman-exclusive: it also imports and runs in Insomnia, Bruno,
> Thunder Client, Hoppscotch, and headless.

## Goal

Makes one authenticated REST call to the BDP API using a Postman Collection, with the token stored in your client's vault and the rest of the request built from collection variables, no code to run.

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

Follow [Importing an API Collection File](../../docs/importing-api-collections.md) to import `bdp-rest-quickstart.json` into your client.

### 2. Set your token

Follow [Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md) to store your token as a vault secret named `BDP_API_TOKEN`. The collection's authorization already references it as `{{vault:BDP_API_TOKEN}}`, so once the secret exists in your vault, no further edits are needed. Never edit the committed file to add a real token.

The collection uses collection-level bearer auth, so every request sends:

```text
Authorization: Bearer {{vault:BDP_API_TOKEN}}
```

### 3. List sites

Open `List Sites` and click **Send**. The response lists the sites your token is entitled to see. Each site's `id` identifies that site; you will use one of these IDs to request its buildings in the next step. Copy the `id` of the site you want to use, and paste it into the collection's **Variables** tab as the value for `siteId`.

### 4. List buildings for a site

Open `List Buildings by Site`. This GET request returns the buildings belonging to one site, using the site's ID as part of the URL path:

```text
https://ecostruxure-building-platform-api-uat.se.app/api/sites/{{siteId}}/buildings
```

The `{{siteId}}` placeholder in the URL will be replaced with the actual site ID stored in the collection variable. The value you save there will be used for subsequent requests that reference `{{siteId}}`. The response contains the buildings for that site. Depending on the site you choose, the response may vary, but it will generally be a JSON array of building objects.


### 5. Automatic site ID setting

Postman provides the capability to execute scripts before or after a request. You can use this feature to automatically set the site ID for you after you list sites. In `List Sites`, open **Scripts > Post-response** to see the script that runs automatically after the response arrives:

```javascript
if (pm.response.code === 200) {
    const body = pm.response.json();
    const items = Array.isArray(body) ? body : (body.items || []);
    if (items.length > 0 && items[0].id) {
        pm.collectionVariables.set('siteId', items[0].id);
        console.log('siteId set to ' + items[0].id);
    }
}
```

For a successful response containing at least one site, the script reads the first site's `id` and saves it as the **collection variable** `siteId`. Collection variables are shared by requests in this collection, so no Postman environment needs to be selected.

When you click **Send** on `List Buildings by Site`, Postman replaces `{{siteId}}` in the URL with that saved value. This lets you chain the two requests without copying and pasting IDs. To list buildings for a different site, replace `siteId` in the collection's **Variables** tab with another ID from the `List Sites` response. Running `List Sites` again overwrites it with the first returned site's ID.

If `List Sites` returns no sites, the script does not update `siteId`; do not send the buildings request until you have a valid site ID. If you already have an environment variable named `siteId`, remove or rename it so it does not override the collection variable.

You can also run the whole collection with your client's runner (Postman calls this the **Runner**).

## Expected Outcome

- HTTP `200` with a JSON body.
- The `status is 200` test passes in the test results panel.
- `List Sites` writes the first returned site's ID into the `siteId` collection variable.
- `List Buildings by Site` returns the buildings for that site.

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
| `take` | `5` | Page size for organizations and sites |
| `skip` | `0` | Page offset for organizations and sites |
| `siteId` | empty | Site ID in the URL path of `List Buildings by Site`; set automatically by `List Sites` |

The host is set directly in each request's URL
(`https://ecostruxure-building-platform-api-uat.se.app`), not a variable. To point the
collection at production, edit the URL of each request to
`https://ecostruxure-building-platform-api.se.app`.

The token is not a collection variable; it is referenced directly from your client's vault as `{{vault:BDP_API_TOKEN}}` in the collection's Authorization tab. See [Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md).

### Authentication

Auth is defined once at collection level and inherited by every request, which keeps the token in a single place. Tokens are short-lived by design; re-copy a fresh token when requests start failing with `401`.

### `X-Api-Version`

Every REST operation declares this header. The collection sends `{{apiVersion}}`, which defaults to `3.0`. `2.0` is also accepted; other values return
`400 Unsupported API Version was requested`.

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
