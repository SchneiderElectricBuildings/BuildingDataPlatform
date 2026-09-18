# Setup Credentials

## Goal
Set up and store BDP credentials securely so every guide and example in `publish/` can run without rewriting setup steps.

## Prerequisites

- **Portal access**: UAT - `https://ecostruxure-building-platform-uat.se.app/`
- **Correct role**:  PartnerViewer/PartnerAdmin for consumer credentials, SourceAdmin for data source credentials
- **Shell access**: PowerShell, Bash, or equivalent

## Steps

1. Identify which flow you are running.

   - REST or GraphQL examples use `BDP_API_TOKEN`.
   - Event Hub streaming examples use `BDP_EVENTHUB_CONNECTION_STRING`.
   - DIF provider examples use `BDP_DIF_CONNECTION_STRING`.

2. Retrieve credentials from the portal.

   Navigate the portal <https://ecostruxure-building-platform-uat.se.app> to retrieve credentials. Here is where to find each credential:

   | Credential | Portal path | Used by |
   | --- | --- | --- |
   | API token | Credentials -> System -> API Token | REST and GraphQL |
   | Event Hub connection string | Partners -> your partner -> your consumer -> Event Hubs -> Primary Connection String | Event Hub consumer |
   | IoT Hub connection string | Data Sources -> your company -> your source -> Connections -> Primary Connection String | DIF telemetry ingress |

3. Choose your preferred setup method.

   You can use either shell environment variables or a local `.env` file. Use the method that best fits your workflow.

   - Method A: Set environment variables in your shell.

      ```powershell
      $env:BDP_API_TOKEN = "eyJ..."
      $env:BDP_EVENTHUB_CONNECTION_STRING = "Endpoint=sb://...;EntityPath=..."
      $env:BDP_DIF_CONNECTION_STRING = "HostName=...;DeviceId=...;SharedAccessKey=..."
      ```

      ```bash
      export BDP_API_TOKEN="eyJ..."
      export BDP_EVENTHUB_CONNECTION_STRING="Endpoint=sb://...;EntityPath=..."
      export BDP_DIF_CONNECTION_STRING="HostName=...;DeviceId=...;SharedAccessKey=..."
      ```

   - Method B: Use a local `.env` file (when provided by the example).

   Copy `.env.template` to `.env`, fill values, and keep `.env` out of version control.

4. Use your chosen method consistently for the session.

   Avoid mixing partial values across methods in the same run.

5. Validate each credential, depending on your chosen flow, with the matching quick check.

   - API token: `examples/graphql-quickstart-python/introspect.py`
   - Event Hub: `examples/eventhub-consumer-python/consume.py`
   - DIF ingress: `examples/dif-telemetry-python/send_telemetry.py --dry-run`

> [!TIP]
> Having trouble with credentials? It is usually a configuration problem, not a code problem. If you are stuck, check the [Troubleshooting](troubleshooting.md). If that doesn't help, refer to the [Support](https://github.com/SchneiderElectricBuildings/BuildingDataPlatform#support) section to know how to reach us.

## Expected Outcome

- Required environment variables are set for your chosen scenario.
- At least one scenario-specific credential check succeeds.
- Credentials are not hardcoded in scripts, command history snippets, or tracked files.

## Notes

- Tokens are short-lived by design. If calls suddenly return `401`, refresh the token from the portal and rerun.
- Do not pass credentials as command-line arguments, arguments leak into shell history and process lists.
- Keep credentials out of logs and screenshots.
- If a credential is valid but no data arrives, check subscription rule and site authorization before debugging code.

## What's Next

- [For access model and permission behavior](access-model-and-permissions.md)
- [For read access patterns](consuming-data.md)
- [For runtime failures](troubleshooting.md)
- [For GUI REST clients such as Postman](setup-credentials-api-clients.md)
