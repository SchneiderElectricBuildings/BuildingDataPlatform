#:property TargetFramework=net10.0
#:package DotNetEnv@3.2.0

// Get a BDP API access token, reuse it while valid, and call the REST API.
//
// Usage:
//     dotnet call_api.cs

using System.Net.Http.Headers;
using System.Text.Json;

DotNetEnv.Env.NoClobber().Load();

const string ApiBaseUrl = "https://ecostruxure-building-platform-api-uat.se.app";
string tokenUrl = $"https://login.microsoftonline.com/{Environment.GetEnvironmentVariable("BDP_TENANT_ID")}/oauth2/v2.0/token";

using var http = new HttpClient();
string? token = null;
DateTimeOffset expiresAt = DateTimeOffset.MinValue;

// The first call requests a token, the second one reuses it.
Console.WriteLine(await GetSites());
Console.WriteLine(await GetSites());

// Return a valid token, requesting a new one only when needed.
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

async Task<string> GetSites()
{
    using var request = new HttpRequestMessage(HttpMethod.Get, $"{ApiBaseUrl}/api/Sites");
    request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", await GetToken());
    request.Headers.Add("X-Api-Version", "3.0");

    var response = await http.SendAsync(request);
    response.EnsureSuccessStatusCode();
    return await response.Content.ReadAsStringAsync();
}
