"""Request a BDP API access token with the OAuth 2.0 client credentials flow.

The script reads the client credentials retrieved from the BDP Portal, requests an
access token from the Microsoft identity platform, then uses that token for one
REST call (GET /api/Sites) to prove it is accepted.

Usage:
    python get_token.py
    python get_token.py --no-verify
    python get_token.py --print-token
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TENANT_ID_ENV = "BDP_TENANT_ID"
CLIENT_ID_ENV = "BDP_CLIENT_ID"
CLIENT_SECRET_ENV = "BDP_CLIENT_SECRET"
SCOPES_ENV = "BDP_SCOPES"
REQUIRED_VARS = (TENANT_ID_ENV, CLIENT_ID_ENV, CLIENT_SECRET_ENV, SCOPES_ENV)

TOKEN_URL_TEMPLATE = "https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
UAT_BASE_URL = "https://ecostruxure-building-platform-api-uat.se.app"

# With --print-token, stdout carries only the token so it can be captured by a shell.
info_stream = sys.stdout


def log(message: str) -> None:
    print(message, file=info_stream)


def read_dotenv(dotenv_path: Path) -> dict[str, str]:
    """Return the key/value pairs of a dotenv file, or an empty dict when absent."""
    values: dict[str, str] = {}
    try:
        with dotenv_path.open(encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ("\"", "'"):
                    value = value[1:-1]
                values[name.strip()] = value
    except OSError:
        return {}
    return values


def resolve_settings() -> dict[str, str]:
    """Read settings from env first, then fall back to .env in script/cwd directory."""
    script_dir_env = Path(__file__).with_name(".env")
    cwd_env = Path.cwd() / ".env"

    dotenv_values = read_dotenv(script_dir_env)
    # Support running from a directory different from this script's folder.
    if script_dir_env.resolve() != cwd_env.resolve():
        for name, value in read_dotenv(cwd_env).items():
            dotenv_values.setdefault(name, value)

    settings: dict[str, str] = {}
    for name in REQUIRED_VARS:
        value = os.environ.get(name) or dotenv_values.get(name)
        if value:
            settings[name] = value
    return settings


def mask(value: str) -> str:
    """Show only the edges of a secret value."""
    if len(value) <= 12:
        return "***"
    return f"{value[:6]}...{value[-4:]}"


def request_token(tenant_id: str, client_id: str, client_secret: str,
                  scopes: str, timeout: int) -> dict:
    url = TOKEN_URL_TEMPLATE.format(tenant_id=urllib.parse.quote(tenant_id, safe=""))
    form = urllib.parse.urlencode({
        "client_id": client_id,
        "scope": scopes,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=form,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def print_token_error(code: int, body: str) -> None:
    """Map Microsoft identity platform errors to actionable hints."""
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {}

    error = payload.get("error", "")
    description = (payload.get("error_description") or "").splitlines()
    description = description[0] if description else ""

    hints = {
        "invalid_client": "client secret is wrong or expired. Check BDP_CLIENT_SECRET "
                          "and the credential 'Expires On' date in the portal.",
        "unauthorized_client": "client ID not found in this tenant. Check BDP_CLIENT_ID "
                               "and BDP_TENANT_ID.",
        "invalid_scope": "scope is not valid. Copy BDP_SCOPES exactly from the portal.",
        "invalid_request": "request rejected. Check BDP_TENANT_ID and that every value is set.",
    }

    if error in hints:
        print(f"HTTP {code} {error}: {hints[error]}", file=sys.stderr)
    else:
        print(f"HTTP {code}: {error or body[:400].strip()}", file=sys.stderr)
    if description:
        print(f"  {description}", file=sys.stderr)


def call_sites(base_url: str, token: str, api_version: str, timeout: int) -> int:
    url = f"{base_url.rstrip('/')}/api/Sites?take=5"
    log(f"GET {url}")

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "X-Api-Version": api_version,
            "Accept": "application/json",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        if exc.code == 401:
            print("HTTP 401: the API rejected the token. Check BDP_SCOPES.", file=sys.stderr)
        elif exc.code == 403:
            print("HTTP 403: token accepted, but your consumer is not authorized "
                  "for this data.", file=sys.stderr)
        else:
            print(f"HTTP {exc.code}: {body[:400].strip()}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"network error: {exc.reason}", file=sys.stderr)
        return 1

    log(f"status: {status}")
    try:
        payload = json.loads(body) if body else []
    except json.JSONDecodeError:
        payload = []
    items = payload if isinstance(payload, list) else payload.get("items", [])
    if isinstance(items, list):
        log(f"items: {len(items)}")
        for item in items[:5]:
            if isinstance(item, dict):
                log(f"  - {item.get('id', '-')} | {item.get('name', '-')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    global info_stream

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="only request the token, skip the GET /api/Sites check",
    )
    parser.add_argument(
        "--print-token",
        action="store_true",
        help="write only the access token to stdout (other output goes to stderr); "
             "treat the output as a secret",
    )
    parser.add_argument(
        "--base-url",
        default=UAT_BASE_URL,
        help="REST API host used for the verification call",
    )
    parser.add_argument("--api-version", default="3.0", choices=("2.0", "3.0"))
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args(argv)

    if args.print_token:
        info_stream = sys.stderr

    settings = resolve_settings()
    missing = [name for name in REQUIRED_VARS if name not in settings]
    if missing:
        print(
            f"missing {', '.join(missing)}. Set them in your environment or in a .env "
            "file in this folder (see docs/retrieve-client-credentials.md)",
            file=sys.stderr,
        )
        return 2

    log(f"POST {TOKEN_URL_TEMPLATE.format(tenant_id=settings[TENANT_ID_ENV])}")

    try:
        token_response = request_token(
            settings[TENANT_ID_ENV],
            settings[CLIENT_ID_ENV],
            settings[CLIENT_SECRET_ENV],
            settings[SCOPES_ENV],
            args.timeout,
        )
    except urllib.error.HTTPError as exc:
        print_token_error(exc.code, exc.read().decode("utf-8", errors="replace"))
        return 1
    except urllib.error.URLError as exc:
        print(f"network error: {exc.reason}", file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print("token endpoint returned a non-JSON response", file=sys.stderr)
        return 1

    access_token = token_response.get("access_token")
    if not access_token:
        print("token endpoint response has no access_token", file=sys.stderr)
        return 1

    log("token: acquired")
    log(f"  token_type: {token_response.get('token_type', '-')}")
    log(f"  expires_in: {token_response.get('expires_in', '-')} seconds")
    log(f"  access_token: {mask(access_token)}")

    exit_code = 0
    if not args.no_verify:
        exit_code = call_sites(args.base_url, access_token, args.api_version, args.timeout)

    if args.print_token and exit_code == 0:
        print(access_token)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
