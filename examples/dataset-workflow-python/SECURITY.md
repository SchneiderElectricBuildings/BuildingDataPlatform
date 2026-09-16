# Security: Dataset Workflow (Python)

`dataset_workflow.py` makes authenticated HTTPS requests to discover entities, create a
dataset, and retrieve measurement values.

## Credential Management

The script reads `BDP_API_TOKEN` from the process environment or a local `.env` file. It
does not accept the token as a command-line argument or print it. `.env` is excluded by
the repository `.gitignore`; never add credentials to `dataset.json`.

Tokens are short-lived. Retrieve a fresh one from **Credentials -> System -> API Token**
in the portal when a request returns `401`.

## Data Handling

- `dataset.json` contains resource identifiers. Review it before sharing or committing.
- The `retrieve` command prints complete measurement-value responses to standard output.
  Treat redirected output as building data and store it according to your organization's
  data-handling requirements.
- Use the shortest practical dataset expiration date and include only required members.

## Network Security

The script makes outbound HTTPS requests only. TLS verification uses Python's standard
library defaults and is never disabled. Use `--base-url` only with a trusted BDP host.

## Input Validation

The `validate` command checks the document shape, accepted member names, and UUID syntax
before any request is made. Server-side authorization remains authoritative: knowing an
entity ID does not grant access to it.

## Compliance

See [SECURITY.md](../../SECURITY.md) at the repository root for vulnerability reporting.