# Documentation Summary

Use this page as a fast map before you dive into the full guides. It explains what each
section covers, when to read it, and where to go next.

## Recommended reading order

1. [Setup Credentials](setup-credentials.md)
2. [Access Model and Permissions](access-model-and-permissions.md)
3. [Consuming Data](consuming-data.md) or [Providing Data](providing-data.md), based on your workflow
4. [Troubleshooting](troubleshooting.md) when results are unexpected

## Guide-by-guide overview

Table – What each guide gives you

| Guide | What you will find | Best time to read |
| --- | --- | --- |
| [Access Model and Permissions](access-model-and-permissions.md) | Account activation, access model, context behavior, and role boundaries | Before debugging empty or partial results |
| [Setup Credentials](setup-credentials.md) | Secure retrieval, storage, and rotation for API, Event Hub, and IoT Hub credentials | Right after account activation |
| [Setup Credentials for API Clients](setup-credentials-api-clients.md) | Storing an API token in Postman/Insomnia/Bruno-style vault or secret variables | Before running an API collection example |
| [Importing an API Collection File](importing-api-collections.md) | Generic import steps for Postman Collection Format v2.1 files | Before running any API collection example |
| [Consuming Data](consuming-data.md) | Decision path for REST, GraphQL, and streaming, plus entry points to examples and specs | When your app reads data from BDP |
| [Event Hub Message Payload](eventhub-message-payload.md) | Message structure, field groups, and design trade-offs for telemetry consumers | When building a streaming consumer or optimizing payload size |
| [Providing Data](providing-data.md) | DIF onboarding, point-group commissioning flow, and semantic modeling requirements | When your app sends data into BDP |
| [Environments](environments.md) | List of endpoints for the different environments and their status | Before accessing any environment |
| [Troubleshooting](troubleshooting.md) | Common failure patterns and quick checks for auth, permissions, empty results, and stream issues | When a request succeeds but output is missing or incorrect |

## References and examples

Table – Supporting material by purpose

| Need | Go to |
| --- | --- |
| OpenAPI bundles and schema files in this repository | [OpenAPI Bundles](openapi-bundles.md) |
| Published API specifications on Schneider Electric Exchange | [README API specifications](../README.md#api-specifications) |
| Runnable consumer and provider examples | [Examples Overview](../examples/README.md) |

## Start from your goal

Table – Fast path by task

| If you need to... | Start here | Then continue with |
| --- | --- | --- |
| Validate access and understand visibility rules | [Setup Credentials](setup-credentials.md) | [Access Model and Permissions](access-model-and-permissions.md) and [Consuming Data](consuming-data.md) |
| Build a REST or GraphQL consumer | [Consuming Data](consuming-data.md) | [OpenAPI Bundles](openapi-bundles.md) and relevant examples |
| Start a telemetry stream consumer | [Consuming Data](consuming-data.md) | [Event Hub Message Payload](eventhub-message-payload.md), [Starter Pack](../README.md#examples), and [Troubleshooting](troubleshooting.md) |
| Send data with Data Integration Framework (DIF) | [Providing Data](providing-data.md) | [Setup Credentials](setup-credentials.md) and provider examples |
| Diagnose failed or empty responses | [Troubleshooting](troubleshooting.md) | The guide referenced by the matching symptom |
