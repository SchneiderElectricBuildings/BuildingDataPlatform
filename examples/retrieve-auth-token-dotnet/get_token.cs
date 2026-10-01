#:property TargetFramework=net10.0
#:package DotNetEnv@3.2.0

// Request a BDP API access token and print it.
//
// Usage:
//     dotnet get_token.cs

using System.Text.Json;

DotNetEnv.Env.NoClobber().Load();

using var http = new HttpClient();

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
