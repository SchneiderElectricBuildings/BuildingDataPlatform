# Examples Overview

Use this section to quickly find the example that matches your goal and role.

You will find consumer-focused and provider-focused scenarios, each built as a small runnable path that validates one concrete outcome.

Across scenarios, the examples demonstrate practical implementation patterns:
environment-based credentials, explicit failure messages, CI-friendly execution, and scenario-local security and setup guidance.

## Example Pattern

The examples follow a scenario-first pattern:

- Start from a concrete outcome you want to validate.
- Use the smallest script that proves that outcome.
- Fail with explicit, actionable errors when credentials, configuration, or access are wrong.
- Keep setup and run guidance inside each scenario folder so details stay local to the implementation.

## Available Scenarios

For Data consumers

| Scenario | Language | For | What it helps you validate |
| --- | --- | --- | --- |
| [GraphQL Quickstart (Python)](graphql-quickstart-python/) | Python | Data consumers | Token validity and GraphQL schema visibility for your entitlements |
| [GraphQL Quickstart (Node.js)](graphql-quickstart-nodejs/) | Node.js | Data consumers | Token validity and GraphQL schema visibility for your entitlements |
| [GraphQL Quickstart (.NET)](graphql-quickstart-dotnet/) | .NET | Data consumers | Token validity and GraphQL schema visibility for your entitlements |
| [Explore REST Operations](explore-rest-operations-python/) | Python | Data consumers | OpenAPI operation discovery and client scaffolding entry points |
| [REST Quickstart (Python)](rest-quickstart-python/) | Python | Data consumers | First authenticated REST call and response handling (Python) |
| [REST Quickstart (Node.js)](rest-quickstart-nodejs/) | Node.js | Data consumers | First authenticated REST call and response handling (Node.js) |
| [REST Quickstart (.NET)](rest-quickstart-dotnet/) | .NET | Data consumers | First authenticated REST call and response handling (.NET) |
| [REST Quickstart (Postman)](rest-quickstart-postman/) | API collection | Data consumers | First authenticated REST call without writing code (Postman-compatible collection) |
| --- | --- | --- | --- |
| [Event Hub Consumer](eventhub-consumer-python/) | Python | Streaming consumers | Event Hub connectivity and incoming telemetry flow |
| --- | --- | --- | --- |
| [Point Group Configuration](point-group-config-python/) | Python | Data providers | Point-group commissioning file validity before upload |
| [Data Integration Framework (DIF) Telemetry Ingress](dif-telemetry-python/) | Python | Data providers | Protocol-conformant telemetry payload submission |



## Conventions Across Examples

- Credentials are loaded from environment variables when a scenario calls an API.
- Scenario scripts terminate with meaningful exit behavior suitable for smoke
  testing and CI.
- Errors are written to identify the failure layer quickly.
- Security notes are documented per scenario in each local `SECURITY.md`.

## Related Guidance

- [Access Model and Permissions](../docs/access-model-and-permissions.md)
- [Setup Credentials](../docs/setup-credentials.md)
- [Consuming Data](../docs/consuming-data.md)
- [Providing Data](../docs/providing-data.md)
- [Repository Security](../SECURITY.md)
