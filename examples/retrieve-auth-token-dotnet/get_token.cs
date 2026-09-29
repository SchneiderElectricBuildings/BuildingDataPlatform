#:property TargetFramework=net10.0
#:property PublishAot=false
#:package DotNetEnv@3.2.0

using DotNetEnv;
using System.Net.Http.Headers;
using System.Text.Json;

const string TenantIdEnv = "BDP_TENANT_ID";
const string ClientIdEnv = "BDP_CLIENT_ID";
const string ClientSecretEnv = "BDP_CLIENT_SECRET";
const string ScopesEnv = "BDP_SCOPES";
string[] requiredVars = [TenantIdEnv, ClientIdEnv, ClientSecretEnv, ScopesEnv];

var tokenErrorHints = new Dictionary<string, string>(StringComparer.Ordinal)
{
    ["invalid_client"] = "client secret is wrong or expired. Check BDP_CLIENT_SECRET and the credential 'Expires On' date in the portal.",
    ["unauthorized_client"] = "client ID not found in this tenant. Check BDP_CLIENT_ID and BDP_TENANT_ID.",
    ["invalid_scope"] = "scope is not valid. Copy BDP_SCOPES exactly from the portal.",
    ["invalid_request"] = "request rejected. Check BDP_TENANT_ID and that every value is set.",
};

if (!TryParseOptions(args, out Options options, out string? parseError, out bool showHelp))
{
    Console.Error.WriteLine(parseError);
    PrintUsage();
    return 2;
}

if (showHelp)
{
    PrintUsage();
    return 0;
}

if (options.ApiVersion is not ("2.0" or "3.0"))
{
    Console.Error.WriteLine("--api-version must be 2.0 or 3.0");
    return 2;
}

if (options.TimeoutSeconds <= 0)
{
    Console.Error.WriteLine("--timeout must be a positive integer");
    return 2;
}

// With --print-token, stdout carries only the token so it can be captured by a shell.
TextWriter info = options.PrintToken ? Console.Error : Console.Out;

// NoClobber keeps variables already set in the environment.
Env.NoClobber().Load();

var settings = requiredVars.ToDictionary(name => name, Environment.GetEnvironmentVariable);
string[] missing = settings.Where(kv => string.IsNullOrWhiteSpace(kv.Value)).Select(kv => kv.Key).ToArray();
if (missing.Length > 0)
{
    Console.Error.WriteLine($"missing {string.Join(", ", missing)}. Set them in your environment or in a .env file in this folder (see docs/retrieve-client-credentials.md)");
    return 2;
}

string tokenUrl = $"https://login.microsoftonline.com/{Uri.EscapeDataString(settings[TenantIdEnv]!)}/oauth2/v2.0/token";
info.WriteLine($"POST {tokenUrl}");

try
{
    using var http = new HttpClient { Timeout = TimeSpan.FromSeconds(options.TimeoutSeconds) };

    using var tokenRequest = new HttpRequestMessage(HttpMethod.Post, tokenUrl)
    {
        Content = new FormUrlEncodedContent(new Dictionary<string, string>
        {
            ["client_id"] = settings[ClientIdEnv]!,
            ["scope"] = settings[ScopesEnv]!,
            ["client_secret"] = settings[ClientSecretEnv]!,
            ["grant_type"] = "client_credentials",
        }),
    };
    tokenRequest.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

    using HttpResponseMessage tokenResponse = await http.SendAsync(tokenRequest);
    string tokenBody = await tokenResponse.Content.ReadAsStringAsync();

    if (!tokenResponse.IsSuccessStatusCode)
    {
        PrintTokenError((int)tokenResponse.StatusCode, tokenBody);
        return 1;
    }

    string? accessToken;
    string tokenType;
    string expiresIn;
    try
    {
        using JsonDocument document = JsonDocument.Parse(tokenBody);
        JsonElement root = document.RootElement;
        accessToken = root.TryGetProperty("access_token", out JsonElement tokenElement) ? tokenElement.GetString() : null;
        tokenType = root.TryGetProperty("token_type", out JsonElement typeElement) ? typeElement.ToString() : "-";
        expiresIn = root.TryGetProperty("expires_in", out JsonElement expiresElement) ? expiresElement.ToString() : "-";
    }
    catch (JsonException)
    {
        Console.Error.WriteLine("token endpoint returned a non-JSON response");
        return 1;
    }

    if (string.IsNullOrEmpty(accessToken))
    {
        Console.Error.WriteLine("token endpoint response has no access_token");
        return 1;
    }

    info.WriteLine("token: acquired");
    info.WriteLine($"  token_type: {tokenType}");
    info.WriteLine($"  expires_in: {expiresIn} seconds");
    info.WriteLine($"  access_token: {Mask(accessToken)}");

    int exitCode = 0;
    if (!options.NoVerify)
    {
        exitCode = await CallSites(http, options.BaseUrl, accessToken, options.ApiVersion);
    }

    if (options.PrintToken && exitCode == 0)
    {
        Console.Out.WriteLine(accessToken);
    }

    return exitCode;
}
catch (TaskCanceledException)
{
    Console.Error.WriteLine("network error: request timed out");
    return 1;
}
catch (HttpRequestException ex)
{
    Console.Error.WriteLine($"network error: {ex.Message}");
    return 1;
}


async Task<int> CallSites(HttpClient http, string baseUrl, string token, string apiVersion)
{
    string url = $"{baseUrl.TrimEnd('/')}/api/Sites?take=5";
    info.WriteLine($"GET {url}");

    using var request = new HttpRequestMessage(HttpMethod.Get, url);
    request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
    request.Headers.Add("X-Api-Version", apiVersion);
    request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

    using HttpResponseMessage response = await http.SendAsync(request);
    string body = await response.Content.ReadAsStringAsync();
    int status = (int)response.StatusCode;

    if (!response.IsSuccessStatusCode)
    {
        if (status == 401)
        {
            Console.Error.WriteLine("HTTP 401: the API rejected the token. Check BDP_SCOPES.");
        }
        else if (status == 403)
        {
            Console.Error.WriteLine("HTTP 403: token accepted, but your consumer is not authorized for this data.");
        }
        else
        {
            Console.Error.WriteLine($"HTTP {status}: {Snippet(body)}");
        }
        return 1;
    }

    info.WriteLine($"status: {status}");

    try
    {
        using JsonDocument document = JsonDocument.Parse(string.IsNullOrWhiteSpace(body) ? "[]" : body);
        JsonElement root = document.RootElement;
        JsonElement items = root;
        if (root.ValueKind == JsonValueKind.Object && root.TryGetProperty("items", out JsonElement nested))
        {
            items = nested;
        }

        if (items.ValueKind == JsonValueKind.Array)
        {
            info.WriteLine($"items: {items.GetArrayLength()}");
            foreach (JsonElement item in items.EnumerateArray().Take(5))
            {
                if (item.ValueKind != JsonValueKind.Object)
                {
                    continue;
                }
                string id = item.TryGetProperty("id", out JsonElement idElement) ? idElement.ToString() : "-";
                string name = item.TryGetProperty("name", out JsonElement nameElement) ? nameElement.ToString() : "-";
                info.WriteLine($"  - {id} | {name}");
            }
        }
    }
    catch (JsonException)
    {
        // The token was accepted; an unexpected body shape is not a failure here.
    }

    return 0;
}

void PrintTokenError(int status, string body)
{
    string error = string.Empty;
    string description = string.Empty;
    try
    {
        using JsonDocument document = JsonDocument.Parse(body);
        JsonElement root = document.RootElement;
        if (root.TryGetProperty("error", out JsonElement errorElement))
        {
            error = errorElement.GetString() ?? string.Empty;
        }
        if (root.TryGetProperty("error_description", out JsonElement descriptionElement))
        {
            description = (descriptionElement.GetString() ?? string.Empty)
                .Split(['\r', '\n'], StringSplitOptions.RemoveEmptyEntries)
                .FirstOrDefault() ?? string.Empty;
        }
    }
    catch (JsonException)
    {
        // Non-JSON error body, fall through to the raw snippet.
    }

    if (tokenErrorHints.TryGetValue(error, out string? hint))
    {
        Console.Error.WriteLine($"HTTP {status} {error}: {hint}");
    }
    else
    {
        Console.Error.WriteLine($"HTTP {status}: {(error.Length > 0 ? error : Snippet(body))}");
    }

    if (description.Length > 0)
    {
        Console.Error.WriteLine($"  {description}");
    }
}

static string Snippet(string body) =>
    (body.Length <= 400 ? body : body[..400]).Trim().Replace("\n", " ", StringComparison.Ordinal);

static string Mask(string value) =>
    value.Length <= 12 ? "***" : $"{value[..6]}...{value[^4..]}";

void PrintUsage()
{
    Console.WriteLine("Usage:");
    Console.WriteLine("  dotnet get_token.cs -- [OPTIONS]");
    Console.WriteLine();
    Console.WriteLine("Options:");
    Console.WriteLine("  --no-verify              only request the token, skip the GET /api/Sites check");
    Console.WriteLine("  --print-token            write only the access token to stdout (treat it as a secret)");
    Console.WriteLine("  --base-url <url>         REST API host for the check (default: UAT host)");
    Console.WriteLine("  --api-version 2.0|3.0    (default: 3.0)");
    Console.WriteLine("  --timeout <seconds>      (default: 30)");
    Console.WriteLine("  --help                   show this help message");
}

bool TryParseOptions(string[] args, out Options options, out string? error, out bool showHelp)
{
    options = new Options();
    error = null;
    showHelp = false;

    for (int i = 0; i < args.Length; i++)
    {
        string arg = args[i];
        switch (arg)
        {
            case "--help":
            case "-h":
                showHelp = true;
                continue;
            case "--no-verify":
                options.NoVerify = true;
                continue;
            case "--print-token":
                options.PrintToken = true;
                continue;
        }

        if (arg is not ("--base-url" or "--api-version" or "--timeout"))
        {
            error = $"unknown option: {arg}";
            return false;
        }

        if (i + 1 >= args.Length)
        {
            error = $"missing value for {arg}";
            return false;
        }

        string value = args[++i];
        switch (arg)
        {
            case "--base-url":
                options.BaseUrl = value;
                break;
            case "--api-version":
                options.ApiVersion = value;
                break;
            case "--timeout":
                if (!int.TryParse(value, out int timeout))
                {
                    error = "--timeout must be an integer";
                    return false;
                }
                options.TimeoutSeconds = timeout;
                break;
        }
    }

    return true;
}

sealed class Options
{
    public bool NoVerify { get; set; }
    public bool PrintToken { get; set; }
    public string BaseUrl { get; set; } = "https://ecostruxure-building-platform-api-uat.se.app";
    public string ApiVersion { get; set; } = "3.0";
    public int TimeoutSeconds { get; set; } = 30;
}
