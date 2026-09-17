# Security: REST Quickstart (Postman)

This scenario ships a Postman collection that makes authenticated HTTPS `GET` requests
to the REST API. It handles one bearer token, held by Postman.

## Credential Management

Credential used:

- `BDP_API_TOKEN`

The token lives in a Postman environment variable, never in the collection file. Two
rules keep it out of the repository and out of shared workspaces:

- Store the token in the **Current value** column only. Postman does not sync or export
  current values.
- Leave **Initial value** empty. Initial values are shared with the team and included in
  exports.

The committed environment file is a template with an empty, `secret`-typed
`BDP_API_TOKEN`. Never commit an export that contains a real token.

For CI, pass the token at run time instead of storing it:
`newman run ... --env-var "BDP_API_TOKEN=$BDP_API_TOKEN"`.

For how access configuration affects what valid credentials can see, read
[Access Model and Permissions](../../docs/access-model-and-permissions.md).

## Network Security

Outbound HTTPS only:

- UAT: `https://ecostruxure-building-platform-api-uat.se.app`
- Production: `https://ecostruxure-building-platform-api.se.app`

Keep Postman's **SSL certificate verification** setting enabled; the collection never
asks for it to be disabled.

## Input Validation

The collection contains three read-only `GET` requests against fixed paths. Only
`baseUrl`, `apiVersion`, paging values, and `siteId` are variable, so a mistyped
variable cannot redirect a call to an unintended operation on the host.

A collection pre-request script fails the call early with an explicit message when
`BDP_API_TOKEN` is empty, instead of producing an unexplained `401`.

## Logging Practices

Test scripts print status hints only. The token is referenced as `{{BDP_API_TOKEN}}`
and never written to the console or to a response body.

Postman stores request and response history locally; clear it if a response contained
sensitive data.

## Threat Model

### Data Flow Diagram

```mermaid
flowchart LR
    subgraph local["Developer machine (trusted)"]
        E["BDP_API_TOKEN<br/>(Postman environment, current value)"]
        S["Postman collection<br/>(client)"]
        E -->|"1 resolve variable"| S
        S -->|"2 HTTPS request"| API["BDP REST API<br/>(service)"]
        API -->|"3 JSON response"| S
        S -->|"4 show body and tests"| OUT["Postman UI<br/>(console)"]
    end
```

Trust boundaries are crossed only once, at the HTTPS API call.

### STRIDE Analysis

Table - STRIDE

| Category | Threat | Mitigation | Status |
| --- | --- | --- | --- |
| **Spoofing** | Token stolen and reused | Token kept in current value only, rotate when exposed | Mitigated (process) |
| **Tampering** | Request changed in transit | HTTPS/TLS with certificate verification enabled | Mitigated |
| **Repudiation** | Request source disputes | Platform-side logging and local Postman history | Accepted |
| **Information Disclosure** | Token exported or synced with the collection | Empty initial value, template environment, no token in collection file | Mitigated |
| **Denial of Service** | Endpoint unavailable or slow | Postman request timeout setting, manual retry | Accepted |
| **Elevation of Privilege** | Calling unintended endpoints | Fixed request paths, only host and filters are variable | Mitigated |

## Compliance

See [SECURITY.md](../../SECURITY.md) at the repository root for vulnerability reporting.
