# Point Group Configuration

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

## Goal

The file you upload in the portal to commission a point group, with a template and a validator that checks it **before** you upload it.

Once commissioned, the `PointGroupReferenceId` and each `PointReferenceId` become the identifiers your connector sends telemetry against, see [dif-telemetry](../dif-telemetry-python/).

No dependencies beyond the standard library.

## Prerequisites

- Python 3.9 or later 
- `SourceId` Issued with your ingress setup, appears in your welcome email
- Portal role  **SourceAdmin** to view the Data Source connection secrets
- Credentials (See [Setup Credentials](../../docs/setup-credentials.md))

## Steps

### 1. Setting up a configuration

Go the the folder and copy the template to a new file, then edit it to supply your own values.

```bash
cd examples/point-group-config-python

cp point_group_config.template.json my_config.json
# edit, then:
python validate_config.py my_config.json
```

> [!NOTE]
> **Windows:** if `python` prints "Python was not found; run without arguments to install from the Microsoft Store", use the Python launcher `py` instead. ex: `py validate_config.py my_config.json`.

#### Expected Outcome

By running it on the unedited template first. It reports the four values you must supply, each by its position in the file, which is the quickest way to see what the skeleton expects.

```bash=
  ERROR   DIF602  $: SourceId still holds the template placeholder '<REPLACE-WITH-BDP-SOURCE-ID>'
  ERROR   DIF603  $: PointGroupReferenceId still holds the template placeholder '<REPLACE-WITH-POINT-GROUP-REF>'
  ERROR   DIF612  Equipments[0]: VendorId still holds the template placeholder '<REPLACE-WITH-VENDOR-ID>'
  ERROR   DIF615  Equipments[0]: LocatedInReferenceId still holds the template placeholder '<REPLACE-WITH-LOCATION-REFERENCE-ID>'

4 issue(s), 4 error(s)
Upload will produce anomalies. Fix the errors first.
```

### 2. Validating your configuration

Add `--json` to emit the findings as JSON for a build step to consume.

Exit code is non-zero when there are **errors**, warnings alone do not fail it, so this drops into a pre-upload check or a CI step unchanged. `my_config.json` is excluded by `.gitignore`, configurations carry site-specific identifiers.

#### Pre-flight checklist

Before uploading, confirm all of the following:

- [ ] `SourceId` is your own source identifier
- [ ] `PointGroupReferenceId` is unique in your data source
- [ ] All `ReferenceId` values are unique across equipment and points
- [ ] Each point has valid `DataType`, `ExactType`, and `UnitExactType`
- [ ] Local validation completes with exit code `0`

Validation command:

```bash
python validate_config.py my_config.json
```

Expected result:

- Exit code `0` if no errors were found
- Non-zero exit code when errors are present
- Optional JSON report with `python validate_config.py my_config.json --json`

#### Expected Outcome

- A configuration file that passes structural validation before portal upload.
- A predictable exit code for local checks and CI integration.
- Reduced anomaly report iteration by catching mechanical errors early.

Expected output sample:

```text
validation complete
errors: 0
warnings: 0
```

## Notes

### Why validate before uploading

Uploading returns an anomaly report, and every round trip through that loop costs you a day or more. Nearly all of the mistakes that cause one are mechanical, a missing field, a `DataType` that is not one of the five allowed, an `ExactType` that is not a URI, and take a second to catch locally.

Every rule has a stable `DIF6xx` code, so you can refer to a finding by code instead of quoting its whole message. The codes belong to this validator; they are not the platform's, so a finding here will not carry the same code in an anomaly report.

A code ending `N` is the namespace advisory for the rule it follows: `DIF617` means `ExactType` is not a URI at all, `DIF617N` means it is a URI but sits outside the accepted namespaces.

## Schema

Here the list of each element at the root and their requirements.

| Field | Required | Notes |
| --- | --- | --- |
| `SourceId` | yes | Matches the source in the portal |
| `PointGroupReferenceId` | yes | Unique across point groups within the data source |
| `ProtocolVersion` | see note | Must be `"1.0"` if present |
| `Version`, `Description` | no | Carried through; the validator accepts them without checking their content |
| `Equipments[]` | yes | Missing or not an array is an error; empty is an error |

The specification's own table marks `ProtocolVersion` required, while the example file in the same specification omits it. The template includes it and the validator accepts either way, checking the value only when it is present. Include it.

Any other top-level field is reported at `INFO` rather than rejected — an unrecognized field is usually a typo, but the platform may accept fields this validator has not been told about, and refusing them outright would be worse than mentioning them.

Here the list of each element part of the array `Equipments[]` and their requirements.

| Field | Required | Notes |
| --- | --- | --- |
| `ReferenceId` | yes | Unique per data source |
| `ExactType` | yes | Brick or Brick Extension class URI |
| `VendorId`, `ProductType`, `Name` | yes | Non-empty |
| `LocatedInReferenceId` | yes | The space the equipment sits in |
| `MonitorsReferenceId` | no | String or `null` |
| `Points[]` | yes | Missing or not an array is an error; empty is a warning |

Here the list of each element part of the array `Points[]` and their requirements.

| Field | Required | Notes |
| --- | --- | --- |
| `ReferenceId` | yes | Unique per data source |
| `ExactType` | yes | Brick class URI |
| `Name` | yes | Non-empty |
| `DataType` | yes | `Boolean`, `Integer`, `Double`, `String` or `DateTimeOffset` |
| `UnitExactType` | yes | QUDT unit URI, use `.../UNITLESS` for dimensionless points |
| `IsWritable` | no | Boolean |

### Vocabularies

Here some important namespaces and where to find their classes. 

| Vocabulary | Namespace | Explorer |
| --- | --- | --- |
| Brick equipment | `https://brickschema.org/schema/Brick#` | [brick:Equipment](https://ontology.brickschema.org/brick/Equipment.html) |
| Brick points | `https://brickschema.org/schema/Brick#` | [brick:Point](https://ontology.brickschema.org/brick/Point.html) |
| Schneider Electric Brick Extension | `https://schneider-electric.com/schema/BrickExtension#` | The supported-type list in the [Ingress API specification](https://exchange.se.com/devportal/?api=bdp-ingress-api-spec-v1-bundle&id=894350) |
| QUDT units | `http://qudt.org/vocab/unit/` | [QUDT units](https://www.qudt.org/doc/DOC_VOCAB-UNITS.html) |

`ExactType` accepts either Brick or the Brick Extension. The extension covers equipment and points Brick does not model, such as access control and several electrical measurements, it has no public ontology browser, so the specification's supported-type list is where you look. `UnitExactType` accepts QUDT only.

A type outside those namespaces is reported as a warning, it is well formed, but the platform is unlikely to resolve it. Use the explorers to find the most specific class that fits, a too-general type is accepted, but it loses exactly the semantics the platform exists to carry.

### `ReferenceId` is one shared namespace

Equipment and points draw `ReferenceId` from the **same** namespace. A duplicate is reported as an error rather than a warning, because it silently rebinds telemetry to the wrong point, which is worse than a rejected upload.

### Every point needs a unit

`UnitExactType` is required on every point, including Boolean and String ones. For anything dimensionless, an on/off status, a mode, an alarm flag, use:

```text
http://qudt.org/vocab/unit/UNITLESS
```

Omitting the field on a status point is the most common mistake in a hand-written configuration, because a status intuitively has no unit. The schema still wants one, and `UNITLESS` is the value that says so explicitly rather than leaving it ambiguous.

### Scope

Structural validation only. It checks that required fields are present and correctly typed, that `DataType` is one of the five allowed values, that `ExactType` and `UnitExactType` are well-formed URIs in the right namespace, and that no `ReferenceId` repeats.

It does **not** confirm that `Temperature_Sensor` is a real Brick class or that `DEG_C` is a real QUDT unit, that needs the full published vocabularies. Namespace and shape are where the errors that cost a round trip actually live.

### Uploading

1. Sites → *your site* → **Point Groups**
2. Click **Update**, locate the configuration file, click **Update** again
3. Wait until the status reads **Check anomaly report**
4. Click the down-arrow icon to **Download Anomaly Report**
5. Confirm there are no **High** severity entries, other levels are informational
6. Click the **Continue** checkbox

A High severity entry means the configuration is rejected in part. Fix and re-upload rather than continuing.

### Project Structure

Here is what each file does. The example is self-contained, it does not import any other files.

| File | Responsibility |
| --- | --- |
| `validate_config.py` | Structural validation with `DIF6xx` codes, non-zero exit on error |
| `point_group_config.template.json` | A skeleton to copy and edit; it reports placeholder errors until you replace the four marked values |
| `README.md` / `SECURITY.md` | Usage and security posture |

## What's Next

- [Providing Data](../../docs/providing-data.md), the full commissioning flow
- [dif-telemetry](../dif-telemetry-python/), sending values against a commissioned point group

