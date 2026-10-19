# Data Integration Framework (DIF) Telemetry Ingress

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)

## Goal

Sends telemetry into the platform as a data provider, over the Data Integration Framework.
Validates the message locally before sending it.

No dependencies beyond the standard library.

## Prerequisites

Table – Prerequisites

| Item | Notes |
| --- | --- |
| Python | 3.9 or later |
| Portal role | **SourceAdmin**, to view the Data Source connection secrets |
| Site | A site (building, level, space) authorized for your Data Source |
| Point group | Commissioned for that site, with at least one point, see [point-group-config](../point-group-config-python/) |
| Connection string | See [Setup Credentials](../../docs/setup-credentials.md) |
| Network | Outbound HTTPS (443) to `graph-bdpdif-uat.azure-devices.net` |

Providers collect credentials under **Data Sources**, not under a partner's Consumers or
Event Hubs.

## Steps

```bash
export BDP_DIF_CONNECTION_STRING="HostName=...;DeviceId=...;SharedAccessKey=..."

python send_telemetry.py \
   --source-id YOUR_SOURCE_ID \
   --point-group YOUR_POINT_GROUP_REFERENCE_ID \
   --point YOUR_POINT_REFERENCE_ID --value 0
```

> [!NOTE]
> **Windows:** if `python` prints "Python was not found; run without arguments to install from the Microsoft Store", use the Python launcher `py` instead. ex: `py send_telemetry.py ...`.

All three values are yours and none of them is guessable. `SourceId` comes from
**Data Sources → *your company* → *your source*** in the portal, the point group and
point reference ids are the ones you chose when you commissioned the point group, in
[point-group-config](../point-group-config-python/).

Sending against identifiers that are not yours is the failure described above: the
message is delivered, discarded downstream, and the response looks identical.

`--dry-run` prints the message without sending it. `--point` and `--value` repeat,
pairwise, to batch several measurements into one request, up to the **4 KB** message
limit, which is roughly ten readings. See
[Limits](../../docs/providing-data.md#limits) for the message size, rate and connection
ceilings. `.env.template` names the variables this example reads.

## Expected Outcome

- A well-formed telemetry payload is produced from your source and point-group identifiers.
- `--dry-run` prints payload structure for safe inspection before send.
- A send request returns a transport-level acknowledgment when authentication is valid.

Expected output sample:

```text
dry-run: payload validated
notificationType=TimeSeries
timeseries count=1
```

## Notes

### The one thing to understand first

**A 2xx confirms delivery, not ingestion.** The response comes from Azure IoT Hub, which
acknowledges that it received the message. Ingestion happens downstream of that
acknowledgment.

If the `SourceId`, `PointGroupReferenceId` or `PointReferenceId` does not match a
commissioned point group authorized for the site, the message is discarded downstream and
the response is unchanged.

So confirm a new connector from the portal rather than from the response, and build that
check into your commissioning process. Once the identifiers are right, the same 2xx is a
reliable delivery signal.

### Message shape

Table – Message fields

| Field | Notes |
| --- | --- |
| `ProtocolVersion` | `"1.0"` |
| `SourceId` | UUID, must match the SourceId in your source details |
| `PointGroupReferenceId` | Must match the commissioned point group, unique within the data source |
| `NotificationType` | `"TimeSeries"`, the only value currently supported |
| `GeneratedAt` | ISO 8601 UTC with a `Z` suffix, when your connector built the message |
| `Timeseries[]` | `PointReferenceId`, `Timestamp`, `Value` |

`Value` may be boolean, integer, number, string or an ISO 8601 date-time, and must match
the type and unit the point was defined with.

The script checks what the protocol defines: required fields are present,
`NotificationType` is a value the protocol allows, each `Value` is one of the permitted
types and is finite, and the serialized message fits inside 4 KB. Whether a
`PointReferenceId` exists, and whether your value suits the point it names, depend on the
commissioned model and are confirmed in the portal.

### Authentication

A SAS token in the `Authorization` header, generated from the connection string and valid
for `--expiry` seconds (default 3600). The endpoint is Azure IoT Hub, so
`api-version=2020-09-30` is required.

The token is generated per run and never written to disk.

### When it returns 401

Almost always one of three things:

1. **DeviceId casing.** It is case sensitive in the URL *and* inside the SAS token, and
   the two must match the portal exactly. A mismatch reads like a bad key.
2. **The SAS token expired.** Tokens are short-lived by design, generate one per run, or
   refresh before expiry in a long-running connector.
3. **Wrong shared access key** for that device.

### Production connectors

Prefer the **Azure IoT SDK** over raw HTTPS. This example uses HTTPS because it has no
dependencies and shows the protocol plainly, but the HTTPS abstractions carry significant
per-message overhead at telemetry volumes.

### Project Structure

Here is what each file does. The example is self-contained, it does not import any other files.

| File | Responsibility |
| --- | --- |
| `send_telemetry.py` | The complete example, local validation, SAS token generation, send, and `--dry-run` |
| `.env.template` | Names the environment variables, copy to `.env` and fill in |
| `README.md` / `SECURITY.md` | Usage and security posture |

## What's Next

- [Providing Data, roles, commissioning, and the full flow](../../docs/providing-data.md)
- [point-group-config, the file that has to be commissioned first](../point-group-config-python/) 
- [Ingress API (v1) on Exchange](https://exchange.se.com/devportal/?api=bdp-ingress-api-spec-v1-bundle&id=894350)
