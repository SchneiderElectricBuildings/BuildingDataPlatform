# Security: REST Quickstart (Postman)

This scenario ships an API collection (Postman Collection Format v2.1) that makes
authenticated HTTPS `GET` requests to the REST API. It handles one bearer token, held
by whichever compatible client you use.

## Credential Management

Credential used:

- `BDP_API_TOKEN`

The token is stored as a vault secret named `BDP_API_TOKEN`, never as a plain
collection variable. Requests reference it directly as `{{vault:BDP_API_TOKEN}}`. See
[Setup Credentials for API Clients](../../docs/setup-credentials-api-clients.md)
for the exact steps, two rules apply regardless of client:

- Store the token in secret/vault storage only, never as a plain collection or
  environment variable value.
- Never export or commit a copy of the collection with a real token value filled in.

Postman Vault is a Postman-app-local feature; `{{vault:BDP_API_TOKEN}}` does not
resolve under Newman or other CI runners. For CI, use a copy of the collection with a
plain `{{BDP_API_TOKEN}}` variable and pass the token at run time instead:
`newman run ... --env-var "BDP_API_TOKEN=$BDP_API_TOKEN"`.

For how access configuration affects what valid credentials can see, read
[Access Model and Permissions](../../docs/access-model-and-permissions.md).

## Network Security

Outbound HTTPS only:

- UAT: `https://ecostruxure-building-platform-api-uat.se.app`
- Production: `https://ecostruxure-building-platform-api.se.app`

Keep your client's certificate verification setting enabled; the collection never asks
for it to be disabled.

## Input Validation

The collection contains three read-only `GET` requests against fixed, literal URLs.
Only `apiVersion`, paging values, and `siteId` are variable, so a mistyped variable
cannot redirect a call to an unintended host or operation.

The Authorization value references a vault secret; a missing or empty secret produces
a `401` from the API rather than sending a malformed request.

## Logging Practices

Test scripts print status hints only. The token is referenced as
`{{vault:BDP_API_TOKEN}}` and never written to the console or to a response body.

Most clients store request and response history locally; clear it if a response
contained sensitive data.

## Threat Model

### Data Flow Diagram

```mermaid
flowchart LR
    subgraph local["Developer machine (trusted)"]
        E["BDP_API_TOKEN<br/>(client vault secret)"]
        S["API collection<br/>(client)"]
        E -->|"1 resolve variable"| S
        S -->|"2 HTTPS request"| API["BDP REST API<br/>(service)"]
        API -->|"3 JSON response"| S
        S -->|"4 show body and tests"| OUT["Client UI<br/>(console)"]
    end
```

Trust boundaries are crossed only once, at the HTTPS API call.

### STRIDE Analysis

Table - STRIDE

| Category | Threat | Mitigation | Status |
| --- | --- | --- | --- |
| **Spoofing** | Token stolen and reused | Token kept in vault storage only, rotate when exposed | Mitigated (process) |
| **Tampering** | Request changed in transit | HTTPS/TLS with certificate verification enabled | Mitigated |
| **Repudiation** | Request source disputes | Platform-side logging and local client history | Accepted |
| **Information Disclosure** | Token exported or synced with the collection | Vault-only storage, no token value in collection file | Mitigated |
| **Denial of Service** | Endpoint unavailable or slow | Client request timeout setting, manual retry | Accepted |
| **Elevation of Privilege** | Calling unintended endpoints | Fixed, literal request URLs; only filters and paging are variable | Mitigated |

## Compliance

See [SECURITY.md](../../SECURITY.md) at the repository root for vulnerability reporting.
