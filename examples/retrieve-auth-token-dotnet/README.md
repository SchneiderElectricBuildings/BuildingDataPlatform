# Retrieve Auth Token (.NET)

![.NET](https://img.shields.io/badge/.NET-512BD4?logo=dotnet&logoColor=white)

## Goal

Shows how to request a BDP API access token with the OAuth 2.0 client credentials flow, using the credential details from the BDP Portal, and how to use and refresh that token when calling the API.

The folder contains two short scripts:

| Script | What it shows |
| --- | --- |
| `get_token.cs` | The simplest way to request a token and print it |
| `call_api.cs` | A more realistic pattern: get a token, reuse it while it is valid, refresh it when needed, and call `GET /api/Sites` |

## Prerequisites

- .NET SDK 10.0.100 or later (uses file-based apps, no project file needed)
- Tenant ID, Client ID, Client Secret, and Scopes (See [Retrieve Client Credentials](../../docs/retrieve-client-credentials.md))
- Network: Outbound HTTPS (443) to `login.microsoftonline.com` and `ecostruxure-building-platform-api-uat.se.app`

## Steps

### 1. Go to the folder

```bash
cd examples/retrieve-auth-token-dotnet
```


### 2. Set your client credentials

Choose one method.

**Option A:** `.env` file

1. Copy `.env.template` to `.env`.
2. Set your values:

    ```dotenv
    BDP_TENANT_ID=00000000-0000-0000-0000-000000000000
    BDP_CLIENT_ID=00000000-0000-0000-0000-000000000000
    BDP_CLIENT_SECRET=your-client-secret
    BDP_SCOPES=api://.../.default
    ```

**Option B:** environment variables

```bash
# bash
export BDP_TENANT_ID="00000000-0000-0000-0000-000000000000"
export BDP_CLIENT_ID="00000000-0000-0000-0000-000000000000"
export BDP_CLIENT_SECRET="your-client-secret"
export BDP_SCOPES="api://.../.default"
```
or
```powershell
# powershell
$env:BDP_TENANT_ID = "00000000-0000-0000-0000-000000000000"
$env:BDP_CLIENT_ID = "00000000-0000-0000-0000-000000000000"
$env:BDP_CLIENT_SECRET = "your-client-secret"
$env:BDP_SCOPES = "api://.../.default"
```

If both are set, the environment variable wins.

### 3. Request a token

```bash
dotnet get_token.cs
```

The script sends one `POST` to the Microsoft identity platform and prints the `access_token` from the response:

```http
POST https://login.microsoftonline.com/{BDP_TENANT_ID}/oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded

client_id={BDP_CLIENT_ID}&scope={BDP_SCOPES}&client_secret={BDP_CLIENT_SECRET}&grant_type=client_credentials
```

```csharp
var response = await http.PostAsync(
    $"https://login.microsoftonline.com/{Environment.GetEnvironmentVariable("BDP_TENANT_ID")}/oauth2/v2.0/token",
    new FormUrlEncodedContent(new Dictionary<string, string>
    {
        ["client_id"] = Environment.GetEnvironmentVariable("BDP_CLIENT_ID")!,
        ["scope"] = Environment.GetEnvironmentVariable("BDP_SCOPES")!,
        ["client_secret"] = Environment.GetEnvironmentVariable("BDP_CLIENT_SECRET")!,
        ["grant_type"] = "client_credentials",
    }));
response.EnsureSuccessStatusCode();

using var json = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
Console.WriteLine(json.RootElement.GetProperty("access_token").GetString());
```

### 4. Use the token to call the API

```bash
dotnet call_api.cs
```

In a real application you do not request a new token for every call. The script keeps the token and its expiry time, and only requests a new one when there is none yet, or when it expires within the next minute:

```csharp
async Task<string> GetToken()
{
    // Refresh one minute early so a token never expires in the middle of a call.
    if (token is null || DateTimeOffset.UtcNow > expiresAt.AddMinutes(-1))
    {
        Console.WriteLine("requesting a new token");
        var response = await http.PostAsync(tokenUrl, new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["client_id"] = Environment.GetEnvironmentVariable("BDP_CLIENT_ID")!,
            ["scope"] = Environment.GetEnvironmentVariable("BDP_SCOPES")!,
            ["client_secret"] = Environment.GetEnvironmentVariable("BDP_CLIENT_SECRET")!,
            ["grant_type"] = "client_credentials",
        }));
        response.EnsureSuccessStatusCode();

        using var json = JsonDocument.Parse(await response.Content.ReadAsStringAsync());
        token = json.RootElement.GetProperty("access_token").GetString()!;
        expiresAt = DateTimeOffset.UtcNow.AddSeconds(json.RootElement.GetProperty("expires_in").GetInt32());
    }

    return token;
}
```

Every API call asks for the token first, then sends it as a bearer token:

```http
GET https://ecostruxure-building-platform-api-uat.se.app/api/Sites
Authorization: Bearer {access_token}
X-Api-Version: 3.0
```

The script calls `GET /api/Sites` twice: the first call requests a token, the second one reuses it.

## Expected Outcome

- `get_token.cs` prints one long string starting with `eyJ`: your access token.
- `call_api.cs` prints `requesting a new token` **once**, followed by the JSON list of sites, twice.

Expected output sample of `call_api.cs`:

```text
requesting a new token
[{"id": "8f6...c9d", "name": "Example Site", ...}]
[{"id": "8f6...c9d", "name": "Example Site", ...}]
```

If something is wrong, the script stops with the HTTP status of the failing call.

## Notes

### Token lifetime

The token response includes `expires_in`, in seconds (typically about one hour). Keep the token and reuse it until shortly before it expires, as `call_api.cs` does, instead of requesting a token for every call.

### Reusing the token with the other examples

The token printed by `get_token.cs` is a regular BDP API token. You can use it as `BDP_API_TOKEN` in the [REST Quickstart](../rest-quickstart-dotnet/README.md) and [GraphQL Quickstart](../graphql-quickstart-dotnet/README.md). Treat it as a secret: anyone who has it can call the API until it expires.

### Common failures

Table - Responses and what they mean

| Response | Meaning |
| --- | --- |
| **400** from the token endpoint | `BDP_TENANT_ID`, `BDP_CLIENT_ID`, or `BDP_SCOPES` is wrong, or a value is empty |
| **401** from the token endpoint | `BDP_CLIENT_SECRET` is wrong or expired (check **Expires On**) |
| **401** from the API | Token acquired for the wrong scope, or expired |
| **403** from the API | Token valid, but your consumer is not authorized for that data |

The token endpoint response body explains the exact reason in `error_description` (for example `AADSTS700016: Application ... was not found in the directory`).

See [Troubleshooting](../../docs/troubleshooting.md) for more.

## What's Next

- [REST Quickstart (.NET)](../rest-quickstart-dotnet/README.md)
- [GraphQL Quickstart (.NET)](../graphql-quickstart-dotnet/README.md)
- [Access Model and Permissions](../../docs/access-model-and-permissions.md)
- [Retrieve Auth Token (Postman)](../retrieve-auth-token-postman/README.md)
