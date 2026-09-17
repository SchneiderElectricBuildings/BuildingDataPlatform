# EcoStruxure&trade; Building Data Platform - Developer Starter Pack

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?logo=node.js&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-512BD4?logo=dotnet&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?logo=postman&logoColor=white)

This starter pack gives partners and independent software vendors a practical path to build on the **EcoStruxure&trade; - Building Data Platform** (BDP).

BDP is a cloud platform that stores semantically described building data from Schneider Electric and third-party systems, and exposes that data through REST, GraphQL, and streaming APIs. REST operations are under `/api/`, and GraphQL requests use `/graphql`.

- **Consume data**: REST &middot; GraphQL &middot; Azure Event Hubs (streaming)
- **Provide data**: Use the Data Integration Framework (DIF) over Azure IoT Hub
- **Model semantics**: [Brick Ontology](https://brickschema.org/) (equipment, points) &middot; REC (sites, buildings, levels, rooms) &middot; [QUDT](https://github.com/qudt/qudt-public-repo) (units)
- **Authenticate**: Bearer token &middot; Event Hub connection string &middot; IoT Hub SAS

---

## Documentation

Use this page as the home page, then use the documentation summary for the full map of guides and workflows.

- Start here: [Setup Credentials](docs/setup-credentials.md)
- Then understand access behavior: [Access Model and Permissions](docs/access-model-and-permissions.md)
- Explore our documentation by starting with [Documentation Summary](docs/README.md)


---

## Examples

The starter pack includes runnable examples for both consumers (read data) and providers (send data). Each example is self-contained, reads credentials from environment variables when needed, and exits with a meaningful code.

For the full catalog and quick-start guidance, see
[Examples Overview](examples/README.md).

> [!NOTE]
> **Time to first query: ~10 minutes**, assuming you have received your welcome email.

### For Data consumers

| Scenario | Language | What it helps you validate |
| --- | --- | --- |
| GraphQL Quickstart | [Python](examples/graphql-quickstart-python/) - [Node.js](examples/graphql-quickstart-nodejs/) - [.NET](examples/graphql-quickstart-dotnet/) | Token validity and GraphQL schema visibility for your entitlements |
| Explore REST Operations | [Python](examples/explore-rest-operations-python/) | OpenAPI operation discovery and client scaffolding entry points |
| REST Quickstart | [Python](examples/rest-quickstart-python/) - [Node.js](examples/rest-quickstart-nodejs/) - [.NET](examples/rest-quickstart-dotnet/) - [Postman](examples/rest-quickstart-postman/) | First authenticated REST call and response handling |
| Event Hub Consumer | [Python](examples/eventhub-consumer-python/) | Event Hub connectivity and incoming telemetry flow |

### For Data providers

| Scenario | Language | What it helps you validate |
| --- | --- | --- |
| Point Group Configuration | [Python](examples/point-group-config-python/) | Point-group commissioning file validity before upload |
| Data Integration Framework (DIF) Telemetry Ingress | [Python](examples/dif-telemetry-python/) | Protocol-conformant telemetry payload submission |

---

## Tools

This starter pack includes utility tools to help with common tasks: reference data synchronization and interactive equipment configuration. See more details about on [tools overviews](tools/README.md).

| Tool | Language | Purpose |
| --- | --- | --- |
| [Bricks & QUDT Reference Data Sync](tools/brick-qudt-sync/) | .NET | Download BrickSchema and QUDT ontology data locally for semantic modeling |
| [Equipment Wizard TUI](tools/equipment-wizard-tui/) | .NET | Interactive terminal wizard to generate equipment and sensor configuration JSON files |

---

## API specifications

The specifications are published on Schneider Electric Exchange, which also hosts the only supported interactive explorer (the **Try it** button):

- [REST API (v3): OpenAPI specification](https://exchange.se.com/devportal/?api=bdp-api-spec-v3-bundle&id=122362)
- [GraphQL API (v1): schema and reference](https://exchange.se.com/devportal/?api=bdp-graphql-api-spec-v1&id=122362)
- [Ingress API (v1): OpenAPI specification](https://exchange.se.com/devportal/?api=bdp-ingress-api-spec-v1-bundle&id=894350)

Platform status: <https://ecostruxurebuildingdataplatform.statuspage.io/>

---

## Support

**For permission, access, or data configuration issues:**
Reply to your welcome email, or contact your Schneider Electric representative. Include the environment, the consumer or data source name, the request you made and the response you got, the answer usually depends on configuration only Schneider Electric can see.

**For issues with examples or documentation:**
Please [open a GitHub issue](https://github.com/SchneiderElectricBuildings/BuildingDataPlatform/issues) with a clear description of the problem, including any error messages or examples of what's unclear.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting and for the credential-handling practices every example follows.

## License

Copyright &copy; 2026 Schneider Electric. All rights reserved.

The examples and documentation in this starter pack are released under the [MIT License](LICENSE), so you are free to use, copy, and modify them in your own projects, including commercial ones.
