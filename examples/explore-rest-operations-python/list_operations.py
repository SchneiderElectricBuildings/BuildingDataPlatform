"""Print the operation table from a downloaded BDP OpenAPI specification.

The Exchange developer portal is a JavaScript application behind sign-in, so the
specification cannot be fetched by a script. Download it by hand — the portal offers JSON
and YAML — and this reads that file.

You get every operation and its parameters without clicking through the portal, derived
from the specification rather than transcribed from it, so it cannot drift the way a
hand-written list does. ``--markdown`` emits the same content as a table you can paste
into your own design notes.

Shared parameters declared once and referenced with ``$ref`` are resolved, so a header
like ``X-Api-Version`` appears on every operation it applies to instead of being
invisible.

Usage:
    python list_operations.py bdp-api-spec-v3-bundle.json
    python list_operations.py bdp-api-spec-v3-bundle.json --markdown
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

METHODS = ("get", "post", "put", "patch", "delete")


def load(path: Path) -> dict:
    # utf-8-sig, not utf-8: a spec saved by a Windows tool usually carries a BOM, and
    # json.loads rejects it with an error that reads like the file is corrupt.
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError:
            raise SystemExit("PyYAML is needed to read a YAML spec: pip install pyyaml")
        return yaml.safe_load(text)
    return json.loads(text)


def resolve(spec: dict, node):
    """Follow a local ``$ref`` to the component it names.

    Real specs put shared query parameters in ``components/parameters`` and reference
    them, so an unresolved node has no ``name`` and the parameter list reads as a row
    of ``None``. Only local refs are followed; a remote one is left as-is rather than
    fetched.
    """
    if not isinstance(node, dict):
        return {}
    ref = node.get("$ref")
    if not ref or not ref.startswith("#/"):
        return node
    target = spec
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(target, dict) or part not in target:
            return node
        target = target[part]
    return target if isinstance(target, dict) else node


def operations(spec: dict):
    for route, item in (spec.get("paths") or {}).items():
        shared = item.get("parameters") or []
        for method in METHODS:
            operation = item.get(method)
            if not operation:
                continue
            # Operation parameters override path parameters by resolved (name, in).
            # Replacing a dict value preserves the parameter's first-seen position.
            parameters = {}
            for raw in list(shared) + list(operation.get("parameters") or []):
                p = resolve(spec, raw)
                name = p.get("name")
                if not name:
                    continue
                where = p.get("in", "")
                mark = "*" if p.get("required") else ""
                parameters[(name, where)] = f"{name}{mark}" + (f" ({where})" if where else "")
            yield {
                "method": method.upper(),
                "path": route,
                "summary": (operation.get("summary")
                            or operation.get("operationId") or "").strip(),
                "tags": ", ".join(operation.get("tags") or []),
                "params": ", ".join(parameters.values()),
            }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--markdown", action="store_true",
                        help="emit the operation list as a markdown table")
    args = parser.parse_args(argv)

    if not args.spec.exists():
        print(f"spec not found: {args.spec}", file=sys.stderr)
        return 1

    spec = load(args.spec)
    info = spec.get("info") or {}
    servers = [s.get("url") for s in (spec.get("servers") or []) if s.get("url")]
    rows = sorted(operations(spec), key=lambda r: (r["tags"], r["path"], r["method"]))

    if args.markdown:
        print(f"<!-- generated from {args.spec.name} "
              f"({info.get('title', '?')} {info.get('version', '?')}) -->\n")
        print("| Method | Path | Purpose |")
        print("| --- | --- | --- |")
        for row in rows:
            print(f"| {row['method']} | `{row['path']}` | {row['summary']} |")
        return 0

    print(f"{info.get('title', 'API')}  version {info.get('version', '?')}")
    for url in servers:
        print(f"  server: {url}")
    print(f"  {len(rows)} operation(s)\n")

    width = max((len(r['path']) for r in rows), default=10)
    for row in rows:
        print(f"  {row['method']:<7}{row['path']:<{width}}  {row['summary']}")
        if row["params"]:
            print(f"  {'':<7}{'':<{width}}  params: {row['params']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
