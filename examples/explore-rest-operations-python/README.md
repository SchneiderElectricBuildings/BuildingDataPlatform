# Explore REST Operations

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

## Goal

Reads the BDP REST API OpenAPI specification and prints every operation with its
parameters, so your operation list comes from the bundle itself rather than from a
transcribed list that can drift.

No dependencies beyond the standard library.

## Prerequisites

- Python 3.9 or later
- OpenAPI Bundle file (see [OpenAPI Bundles](../../docs/openapi-bundles.md) for how to get it)

## Steps

### 1. Go to the folder

```bash
cd examples/explore-rest-operations-python
```

### 2. Run the script

```bash
python list_operations.py bdp-api-spec-v3-bundle-3.0.json
python list_operations.py bdp-api-spec-v3-bundle-3.0.json --markdown
```

#### Expected Outcome

That prints both servers, every operation, and each operation's parameters with their
location and whether they are required. `$ref`-ed shared parameters are resolved, so
headers like `X-Api-Version` appear on every operation they apply to.

Operation parameters override path-level parameters with the same `(name, in)` after
local `$ref` resolution. Parameters keep their first-seen order: overrides retain the
path-level position, and operation-only parameters follow in declaration order.

`--markdown` emits a table you can paste into your own design notes.

The portal offers the specification as JSON or YAML. JSON needs nothing beyond the
standard library, a `.yaml` or `.yml` file additionally needs `pip install pyyaml`.


- A generated operation list from the REST OpenAPI bundle.
- Parameter visibility including resolved shared parameters.
- A reproducible source for client-scaffolding decisions.

Expected output sample:

```text
GET /api/Sites
	- X-Api-Version (header, required)
GET /api/Buildings
	- siteId (query, required)
	- X-Api-Version (header, required)
```

## Notes

### Authentication

This script does not call the API. It reads a local specification file only.

### The `X-Api-Version` header

The header appears because the script resolves `$ref`-ed shared parameters from
`components.parameters` and merges them into each operation row.

Every REST operation declares `X-Api-Version` required, with a default of `3.0`.
Versions `2.0` and `3.0` are supported.

When you later call REST endpoints, send `3.0` explicitly instead of relying on defaults.

### Endpoints

| Environment | Base URL |
| --- | --- |
| UAT | `https://ecostruxure-building-platform-api-uat.se.app` |
| Production | `https://ecostruxure-building-platform-api.se.app` |

The OpenAPI `servers` values are base hosts. REST operations themselves are under
`/api/...` paths.

### Operation groups

Table – REST v3 operation groups

| Group | Retrieves |
| --- | --- |
| Buildings, Floors, Spaces | The spatial hierarchy, by site or organization |
| Devices, DeviceGroups | Equipment, with on-demand read and write commands |
| Measurements | Current values, historical series, and write-back |
| DataSets | Consumer-defined collections of entities |
| EventHubs | The streaming endpoints available to your consumer |
| Sources, Organizations, Sites | Provenance and tenancy |

Which of these your credentials can reach depends on the API types selected when your
consumer was created, Current Value, Historical, On Demand, Streaming, and on its
authorization level. **Read** covers almost every case, **Write** is granted only where
writing back is genuinely required.


### Project Structure

Here is what each file does. The example is self-contained, it does not import any other files.

| File | Responsibility |
| --- | --- |
| `list_operations.py` | Parses the OpenAPI bundle, resolves `$ref`-ed parameters, prints operations as text or markdown |
| `test_list_operations.py` | Standard-library regression tests for parameter merging and output |
| `README.md` / `SECURITY.md` | Usage and security posture |

There is no `.env.template` here: `list_operations.py` reads a specification file and
never calls the API, so it needs no credential at all.

## Tests

From this example's folder, run the offline tests with the standard library:

```bash
python -m unittest -v
```

## What's Next

- [Run a simple REST call in Python](../rest-quickstart-python/README.md)
- [Run a simple REST call in .NET](../rest-quickstart-dotnet/README.md)
- [Compare API families and mappings](../../docs/consuming-data.md)
- [Troubleshoot auth and access results](../../docs/troubleshooting.md)
