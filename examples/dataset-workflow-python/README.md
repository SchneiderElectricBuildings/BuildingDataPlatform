# Dataset Workflow (Python)

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

## Goal

Create a dataset from selected building data, confirm that it was created, and retrieve all commissioned measurement values represented by that dataset.

No dependencies beyond the Python standard library.

## Prerequisites

- Python 3.9 or later
- API token (see [Setup Credentials](../../docs/setup-credentials.md))
- Network: outbound HTTPS (443) to `ecostruxure-building-platform-api-uat.se.app`

## Steps

### 1. Go to the folder and set your token

```bash
cd examples/dataset-workflow-python
cp .env.template .env
```

Set `BDP_API_TOKEN` in `.env`, or export it in your shell as described in
[Setup Credentials](../../docs/setup-credentials.md).

### 2. Build the dataset document interactively

Run one command to explore the resources available to your credentials and create `dataset.json`:

```bash
python dataset_workflow.py build dataset.json
```

The script first lists all accessible buildings. Select one or more by entering their numbers, such as `1,3`, or enter `all`. It then does the same for floors, rooms/spaces, and commissioned measurement values. Press Enter to skip an optional category.

The REST API calls rooms `spaces`. The script follows every result page and writes each selected resource ID into the correct JSON member array. You do not need to type, remember, or copy any ID.

#### Expected Outcome

```text
Dataset JSON builder
Choose resources by number. You never need to type or remember an ID.

Buildings (2)
    1. Headquarters | 4a6...849
    2. Research center | 914...18c
Select numbers separated by commas, or 'all' (required): 1

Floors in Headquarters (2)
    1. Ground floor | d2f...05a
    2. First floor | c52...3fd
Select numbers separated by commas, or 'all' (Enter to skip): 1

...

Dataset name [Sample Dataset]: Meeting room dashboard
Expiration (UTC) [2026-10-16T12:00:00Z]:

Created dataset.json with 4 selected member(s).
```

The generated file is ready to inspect or edit:


```json
{
  "name": "Meeting room dashboard",
  "expiresOn": "2026-10-16T12:00:00Z",
  "members": {
    "buildings": ["4a69071c-0e9e-48e1-83b1-08dee815a849"],
    "floors": ["d2f87591-91e7-4ee6-ab68-d7421026c05a"],
    "spaces": ["48ae6a25-03e4-48ec-a205-e75ebbc8589c"],
    "measurementValues": ["811da9be-694f-45da-a895-c884cdcac30d"]
  }
}
```

#### Notes

The script calls `GET /api/Buildings`, then retrieves floors, spaces, and measurement values for your selections. It writes the selected IDs to `dataset.json`; it does not create the dataset until Step 4.

### 3. Validate the dataset document

The builder validates the file automatically. Run validation again after any manual edits:

```bash
python dataset_workflow.py validate dataset.json
```

`expiresOn` must be a future ISO 8601 UTC date, for example
`2027-12-31T23:59:59.000Z`. You can remove member arrays you do not need. Valid member
types are `buildings`, `floors`, `spaces`, `devices`, and `measurementValues`.

### 4. Create the dataset

```bash
python dataset_workflow.py create dataset.json
```

The response includes the new dataset `id`. Keep it for the retrieval step.

#### Expected Outcome

```text
Created dataset:
{
  "id": "2af...912",
  "name": "Sample Dataset",
  "expiresOn": "2027-12-31T23:59:59Z",
  "members": { ... }
}
```
#### Notes

The script reads `dataset.json` and sends its contents as the body of this request:

```http
POST https://ecostruxure-building-platform-api-uat.se.app/api/DataSets
Authorization: Bearer <BDP_API_TOKEN>
Content-Type: application/json
Accept: application/json
X-Api-Version: 3.0

{
  "name": "Meeting room dashboard",
  "expiresOn": "2027-12-31T23:59:59Z",
  "members": {
    "buildings": ["4a69071c-0e9e-48e1-83b1-08dee815a849"],
    "floors": ["d2f87591-91e7-4ee6-ab68-d7421026c05a"],
    "spaces": ["48ae6a25-03e4-48ec-a205-e75ebbc8589c"],
    "measurementValues": ["811da9be-694f-45da-a895-c884cdcac30d"]
  }
}
```

`POST /api/DataSets` creates a named, expiring collection from those member IDs. The bearer token identifies the consumer and controls which resources it can include. On success, the API returns the created dataset with its new `id`; invalid or inaccessible member IDs are rejected.


### 5. List all datasets

```bash
python dataset_workflow.py list
```

For a consumer with no previous datasets, the list contains only the dataset just created:

```text
Datasets (1)
  2af...912 | Sample Dataset
```

If more appear, they were already available to the same consumer credentials.

### 6. Retrieve all data from the dataset

```bash
python dataset_workflow.py retrieve YOUR_DATASET_ID
```


#### Expected Outcome

- Every commissioned measurement value covered by the dataset is printed as JSON.
- The final line reports the total number retrieved.
- Exit code `0` indicates that every request completed successfully.

#### Notes

This calls `/api/DataSets/{dataSetId}/MeasurementValues` with `commissionedStatus=Commissioned`, follows all pages, and prints the complete JSON array.

### Why datasets are useful

A dataset gives a consumer a named, expiring boundary around just the buildings, floors, rooms, devices, and measurements needed for a use case. Instead of repeatedly walking the full spatial hierarchy and applying the same filters, an application can retrieve the selected measurements through one stable dataset ID. This is useful for dashboards, analytics jobs, exports, and integrations that should operate on a curated scope. 

Including a parent entity can bring its related measurement values into the result. A dataset containing a building, floor, space, and individual measurement may therefore return more measurements than the explicitly listed `measurementValues` alone.


### Files in this folder

| File | Responsibility |
| --- | --- |
| `dataset_workflow.py` | Interactively builds JSON, creates and lists datasets, and retrieves all measurement pages |
| `dataset.template.json` | Optional dataset request-body reference for non-interactive use |
| `.env.template` | Local bearer-token configuration template |
| `README.md` / `SECURITY.md` | Usage and security posture |

## What's Next

- [Consuming Data](../../docs/consuming-data.md)
- [Access Model and Permissions](../../docs/access-model-and-permissions.md)
- [REST Quickstart (Python)](../rest-quickstart-python/README.md)
- [Troubleshooting](../../docs/troubleshooting.md)