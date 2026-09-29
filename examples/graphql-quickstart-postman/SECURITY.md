# Security: GraphQL Quickstart (Postman)

This scenario ships a Postman Collection Format v2.1 file that makes one REST token
check and two GraphQL introspection requests. All requests use HTTPS and the same
bearer token.

## Credential Management

- Store the token in the client's vault as `BDP_API_TOKEN`.
- The committed collection contains only `{{vault:BDP_API_TOKEN}}`, never a real token.
- Do not replace the vault reference with a committed token or export a populated
  environment file.
- Postman Vault references are local to the Postman app and are not resolved by Newman.
  Use a runtime environment variable for CI instead.

## Network Security

The collection connects only to the BDP UAT REST and GraphQL endpoints over HTTPS on
port 443. Certificate validation should remain enabled.

## Data Handling

The collection requests schema metadata and a token-validation response. It does not
write API responses to the repository or execute response content.

See [SECURITY.md](../../SECURITY.md) at the repository root for vulnerability reporting.
