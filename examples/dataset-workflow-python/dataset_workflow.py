"""Discover entities, create a dataset, and retrieve its measurement values.

Usage:
    python dataset_workflow.py build dataset.json
    python dataset_workflow.py validate dataset.json
    python dataset_workflow.py create dataset.json
    python dataset_workflow.py list
    python dataset_workflow.py retrieve DATASET_ID
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

TOKEN_ENV = "BDP_API_TOKEN"
UAT_BASE_URL = "https://ecostruxure-building-platform-api-uat.se.app"
PAGE_SIZE = 100
MEMBER_TYPES = ("buildings", "floors", "spaces", "devices", "measurementValues")


def token_from_dotenv(dotenv_path: Path) -> str | None:
    try:
        with dotenv_path.open(encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                name, value = line.split("=", 1)
                if name.strip() == TOKEN_ENV:
                    return value.strip().strip("\"'") or None
    except OSError:
        return None
    return None


def resolve_token() -> str | None:
    """Load the API token from the environment or a nearby .env file."""
    token = os.environ.get(TOKEN_ENV)
    if token:
        return token

    script_env = Path(__file__).with_name(".env")
    token = token_from_dotenv(script_env)
    if token:
        return token

    cwd_env = Path.cwd() / ".env"
    if script_env.resolve() != cwd_env.resolve():
        return token_from_dotenv(cwd_env)
    return None


class ApiClient:
    """Send authenticated JSON requests to the BDP REST API."""

    def __init__(self, base_url: str, token: str, api_version: str, timeout: int):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.api_version = api_version
        self.timeout = timeout

    def request(self, method: str, path: str, query: dict[str, object] | None = None,
                body: object | None = None) -> object:
        """Send one request with the bearer token and required API version header."""
        url = f"{self.base_url}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)

        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "X-Api-Version": self.api_version,
        }
        if data is not None:
            headers["Content-Type"] = "application/json"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            return json.loads(response_body) if response_body else {}

    def get_all(self, path: str, query: dict[str, object] | None = None) -> list[object]:
        """Follow take/skip pagination until every item has been retrieved."""
        items: list[object] = []
        skip = 0
        while True:
            page_query = dict(query or {})
            page_query.update({"take": PAGE_SIZE, "skip": skip})
            page = self.request("GET", path, page_query)
            if not isinstance(page, list):
                raise ValueError(f"expected an array from {path}")
            items.extend(page)
            if len(page) < PAGE_SIZE:
                return items
            skip += len(page)


def print_entities(label: str, entities: list[object]) -> None:
    print(f"\n{label} ({len(entities)})")
    for entity in entities:
        if isinstance(entity, dict):
            print(f"  {entity.get('id', '-')} | {entity.get('name', '-')}")
        else:
            print(f"  {entity}")


def choose_entities(label: str, entities: list[object], required: bool = False) -> list[dict]:
    """Show numbered API results and return the entities selected by the user."""
    choices = [entity for entity in entities
               if isinstance(entity, dict) and entity.get("id")]
    print(f"\n{label} ({len(choices)})")
    for index, entity in enumerate(choices, start=1):
        print(f"  {index:>3}. {entity.get('name') or '(unnamed)'} | {entity['id']}")

    if not choices:
        if required:
            raise ValueError(f"no {label.lower()} are available")
        return []

    while True:
        suffix = " (required)" if required else " (Enter to skip)"
        answer = input(f"Select numbers separated by commas, or 'all'{suffix}: ").strip()
        if not answer and not required:
            return []
        if answer.lower() == "all":
            return choices
        try:
            indexes = list(dict.fromkeys(int(value.strip()) for value in answer.split(",")))
        except ValueError:
            print("Enter numbers separated by commas, 'all', or Enter to skip.")
            continue
        if indexes and all(1 <= index <= len(choices) for index in indexes):
            return [choices[index - 1] for index in indexes]
        print(f"Choose values from 1 to {len(choices)}.")


def prompt_value(label: str, default: str) -> str:
    value = input(f"{label} [{default}]: ").strip()
    return value or default


def unique_entities(entities: list[dict]) -> list[dict]:
    return list({entity["id"]: entity for entity in entities}.values())


def build_dataset_document(client: ApiClient, output_path: Path) -> None:
    """Guide the user through BDP resources and write selected IDs as dataset JSON."""
    print("Dataset JSON builder")
    print("Choose resources by number. You never need to type or remember an ID.")

    buildings = choose_entities(
        "Buildings", client.get_all("/api/Buildings"), required=True
    )

    selected_floors: list[dict] = []
    for building in buildings:
        floors = client.get_all(f"/api/Buildings/{building['id']}/Floors")
        selected_floors.extend(choose_entities(
            f"Floors in {building.get('name') or building['id']}", floors
        ))

    selected_spaces: list[dict] = []
    for floor in selected_floors:
        spaces = client.get_all(f"/api/Floors/{floor['id']}/Spaces")
        selected_spaces.extend(choose_entities(
            f"Rooms/spaces on {floor.get('name') or floor['id']}", spaces
        ))

    selected_measurements: list[dict] = []
    for building in buildings:
        measurements = client.get_all(
            f"/api/Buildings/{building['id']}/MeasurementValues",
            {"commissionedStatus": "Commissioned"},
        )
        selected_measurements.extend(choose_entities(
            f"Measurement values in {building.get('name') or building['id']}",
            measurements,
        ))

    default_expiration = (
        datetime.now(timezone.utc) + timedelta(days=30)
    ).isoformat(timespec="seconds").replace("+00:00", "Z")
    name = prompt_value("Dataset name", "Sample Dataset")
    expires_on = prompt_value("Expiration (UTC)", default_expiration)

    selections = {
        "buildings": buildings,
        "floors": unique_entities(selected_floors),
        "spaces": unique_entities(selected_spaces),
        "measurementValues": unique_entities(selected_measurements),
    }
    members = {
        member_type: [entity["id"] for entity in entities]
        for member_type, entities in selections.items()
        if entities
    }
    payload = {"name": name, "expiresOn": expires_on, "members": members}
    validate_dataset(payload)

    if output_path.exists():
        overwrite = input(f"{output_path} already exists. Overwrite it? [y/N]: ").strip()
        if overwrite.lower() not in ("y", "yes"):
            print("No file was written.")
            return
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"\nCreated {output_path} with {sum(map(len, members.values()))} selected member(s).")


def discover(client: ApiClient, building_id: str) -> None:
    """List a building's floors, spaces, and measurement values."""
    floors = client.get_all(f"/api/Buildings/{building_id}/Floors")
    print_entities("Floors", floors)

    for floor in floors:
        if not isinstance(floor, dict) or not floor.get("id"):
            continue
        spaces = client.get_all(f"/api/Floors/{floor['id']}/Spaces")
        floor_name = floor.get("name") or floor["id"]
        print_entities(f"Rooms/spaces on {floor_name}", spaces)

    measurements = client.get_all(
        f"/api/Buildings/{building_id}/MeasurementValues"
    )
    print_entities("Measurement values", measurements)


def load_dataset(path: Path) -> dict[str, object]:
    """Read and validate a dataset request body from disk."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc

    return validate_dataset(payload)


def validate_dataset(payload: object) -> dict[str, object]:
    """Check required fields, expiration, member types, and member UUIDs."""
    if not isinstance(payload, dict):
        raise ValueError("dataset document must be a JSON object")
    required = ("name", "expiresOn", "members")
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError("missing required field(s): " + ", ".join(missing))
    unknown_fields = sorted(set(payload) - set(required))
    if unknown_fields:
        raise ValueError("unknown top-level field(s): " + ", ".join(unknown_fields))
    if not isinstance(payload["name"], str) or not payload["name"].strip():
        raise ValueError("name must be a non-empty string")
    expires_on = payload["expiresOn"]
    if not isinstance(expires_on, str):
        raise ValueError("expiresOn must be a future ISO 8601 date")
    try:
        expiration = datetime.fromisoformat(expires_on.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("expiresOn must be a future ISO 8601 date") from exc
    if expiration.tzinfo is None:
        raise ValueError("expiresOn must include a timezone, such as Z")
    if expiration <= datetime.now(timezone.utc):
        raise ValueError("expiresOn must be in the future")

    members = payload["members"]
    if not isinstance(members, dict):
        raise ValueError("members must be a JSON object")
    unknown = sorted(set(members) - set(MEMBER_TYPES))
    if unknown:
        raise ValueError("unknown member type(s): " + ", ".join(unknown))
    for member_type, identifiers in members.items():
        if not isinstance(identifiers, list):
            raise ValueError(f"members.{member_type} must be an array")
        for identifier in identifiers:
            try:
                uuid.UUID(identifier)
            except (AttributeError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"members.{member_type} contains a non-UUID value: {identifier!r}"
                ) from exc
    return payload


def create_dataset(client: ApiClient, path: Path) -> None:
    """Create a dataset with POST /api/DataSets."""
    payload = load_dataset(path)
    created = client.request("POST", "/api/DataSets", body=payload)
    print("Created dataset:")
    print(json.dumps(created, indent=2, ensure_ascii=False))


def list_datasets(client: ApiClient) -> None:
    """List every dataset visible to the current consumer."""
    datasets = client.get_all("/api/DataSets")
    print_entities("Datasets", datasets)


def retrieve_data(client: ApiClient, dataset_id: str) -> None:
    """Retrieve all commissioned measurement values in a dataset."""
    measurements = client.get_all(
        f"/api/DataSets/{dataset_id}/MeasurementValues",
        {"commissionedStatus": "Commissioned"},
    )
    print(json.dumps(measurements, indent=2, ensure_ascii=False))
    print(f"\nRetrieved {len(measurements)} commissioned measurement value(s).")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=UAT_BASE_URL)
    parser.add_argument("--api-version", default="3.0", choices=("2.0", "3.0"))
    parser.add_argument("--timeout", type=int, default=30)
    commands = parser.add_subparsers(dest="command", required=True)

    build_parser = commands.add_parser(
        "build", help="interactively select resources and write dataset JSON"
    )
    build_parser.add_argument("file", type=Path, nargs="?", default=Path("dataset.json"))
    discover_parser = commands.add_parser("discover", help="list IDs for a building")
    discover_parser.add_argument("building_id")
    validate_parser = commands.add_parser("validate", help="validate a dataset JSON file")
    validate_parser.add_argument("file", type=Path)
    create_parser = commands.add_parser("create", help="create a dataset from JSON")
    create_parser.add_argument("file", type=Path)
    commands.add_parser("list", help="list every dataset")
    retrieve_parser = commands.add_parser(
        "retrieve", help="retrieve every commissioned measurement value in a dataset"
    )
    retrieve_parser.add_argument("dataset_id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "validate":
        try:
            load_dataset(args.file)
        except ValueError as exc:
            print(f"validation error: {exc}", file=sys.stderr)
            return 2
        print(f"valid dataset document: {args.file}")
        return 0

    token = resolve_token()
    if not token:
        print(
            f"set {TOKEN_ENV} in your environment or add it to a .env file in this folder",
            file=sys.stderr,
        )
        return 2

    client = ApiClient(args.base_url, token, args.api_version, args.timeout)
    try:
        if args.command == "build":
            build_dataset_document(client, args.file)
        elif args.command == "discover":
            discover(client, args.building_id)
        elif args.command == "create":
            create_dataset(client, args.file)
        elif args.command == "list":
            list_datasets(client)
        elif args.command == "retrieve":
            retrieve_data(client, args.dataset_id)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {body[:1000]}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"network error: {exc.reason}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())