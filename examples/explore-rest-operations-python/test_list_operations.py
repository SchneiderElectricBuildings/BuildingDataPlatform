"""Offline regression tests for effective OpenAPI operation parameters."""

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from list_operations import main, operations


def parameter(name="limit", where="query", required=False):
    return {"name": name, "in": where, "required": required,
            "schema": {"type": "integer"}}


def specification(shared=(), local=()):
    return {
        "openapi": "3.0.3",
        "info": {"title": "Parameter test", "version": "1.0.0"},
        "paths": {
            "/items": {
                "parameters": list(shared),
                "get": {
                    "parameters": list(local),
                    "responses": {"200": {"description": "OK"}},
                },
            },
        },
    }


class OperationsTests(unittest.TestCase):
    def test_path_only_parameter(self):
        spec = specification(shared=[parameter(required=True)])
        self.assertEqual(list(operations(spec))[0]["params"], "limit* (query)")

    def test_operation_only_parameter(self):
        spec = specification(local=[parameter()])
        self.assertEqual(list(operations(spec))[0]["params"], "limit (query)")

    def test_operation_overrides_same_identity(self):
        spec = specification([parameter(required=True)], [parameter()])
        for version in ("3.0.3", "3.1.0"):
            with self.subTest(openapi=version):
                spec["openapi"] = version
                self.assertEqual(list(operations(spec))[0]["params"], "limit (query)")

    def test_same_name_in_different_locations_survives(self):
        spec = specification([parameter(required=True)], [parameter(where="header")])
        self.assertEqual(list(operations(spec))[0]["params"],
                         "limit* (query), limit (header)")

    def test_reference_overrides_use_resolved_identity(self):
        components = {"RequiredLimit": parameter(required=True),
                      "OptionalLimit": parameter()}
        shared_ref = {"$ref": "#/components/parameters/RequiredLimit"}
        local_ref = {"$ref": "#/components/parameters/OptionalLimit"}
        for shared, local in ((shared_ref, parameter()),
                              (parameter(required=True), local_ref),
                              (shared_ref, local_ref)):
            with self.subTest(shared=shared, local=local):
                spec = specification([shared], [local])
                spec["components"] = {"parameters": components}
                self.assertEqual(list(operations(spec))[0]["params"], "limit (query)")

    def test_same_reference_is_emitted_once(self):
        ref = {"$ref": "#/components/parameters/Limit"}
        spec = specification([ref], [ref])
        spec["components"] = {"parameters": {"Limit": parameter()}}
        self.assertEqual(list(operations(spec))[0]["params"], "limit (query)")

    def test_reference_same_name_different_locations_survives(self):
        spec = specification(
            [{"$ref": "#/components/parameters/QueryLimit"}],
            [{"$ref": "#/components/parameters/HeaderLimit"}],
        )
        spec["components"] = {"parameters": {
            "QueryLimit": parameter(required=True),
            "HeaderLimit": parameter(where="header"),
        }}
        self.assertEqual(list(operations(spec))[0]["params"],
                         "limit* (query), limit (header)")

    def test_required_marker_uses_only_effective_parameter(self):
        for shared_required, local_required in ((True, False), (False, True),
                                                (True, None)):
            with self.subTest(shared=shared_required, local=local_required):
                local = parameter(required=local_required)
                if local_required is None:
                    del local["required"]
                spec = specification([parameter(required=shared_required)], [local])
                expected = "limit* (query)" if local_required else "limit (query)"
                self.assertEqual(list(operations(spec))[0]["params"], expected)

    def test_stable_order_and_no_input_mutation(self):
        spec = specification(
            [parameter("offset"), parameter(required=True), parameter("page")],
            [parameter("sort"), parameter(), parameter("filter")],
        )
        original = copy.deepcopy(spec)
        expected = "offset (query), limit (query), page (query), sort (query), filter (query)"
        self.assertEqual(list(operations(spec))[0]["params"], expected)
        self.assertEqual(list(operations(spec))[0]["params"], expected)
        self.assertEqual(spec, original)

    def test_other_methods_and_routes_are_unchanged(self):
        spec = specification([parameter(required=True)], [parameter()])
        item = spec["paths"]["/items"]
        item["get"].update(summary=" List items ", tags=["Items", "Read"])
        for method in ("post", "put", "patch", "delete"):
            item[method] = {"operationId": method + "Items",
                            "responses": {"200": {"description": "OK"}}}
        # These methods and path metadata are not currently included by the explorer.
        for method in ("head", "options", "trace"):
            item[method] = {"responses": {"200": {"description": "OK"}}}
        item["summary"] = "Path summary"
        spec["paths"]["/health"] = {
            "get": {"summary": " Health ", "responses": {"200": {"description": "OK"}}},
        }
        expected = [{"method": "GET", "path": "/items", "summary": "List items",
                     "tags": "Items, Read", "params": "limit (query)"}]
        expected.extend(
            {"method": method.upper(), "path": "/items", "summary": method + "Items",
             "tags": "", "params": "limit* (query)"}
            for method in ("post", "put", "patch", "delete")
        )
        expected.append({"method": "GET", "path": "/health", "summary": "Health",
                         "tags": "", "params": ""})
        self.assertEqual(list(operations(spec)), expected)

    def test_unresolved_references_do_not_remove_named_parameters(self):
        spec = specification([parameter(required=True)], [
            {"$ref": "#/components/parameters/Missing"},
            {"$ref": "https://example.invalid/parameters.json#/Limit"},
        ])
        self.assertEqual(list(operations(spec))[0]["params"], "limit* (query)")


class OutputTests(unittest.TestCase):
    def run_main(self, *options):
        spec = specification([parameter(required=True)], [parameter()])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spec.json"
            path.write_text(json.dumps(spec), encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                code = main([str(path), *options])
        self.assertEqual(code, 0)
        return output.getvalue()

    def test_text_output_shows_only_effective_required_marker(self):
        output = self.run_main()
        self.assertEqual([line.strip() for line in output.splitlines() if "params:" in line],
                         ["params: limit (query)"])
        self.assertIn("1 operation(s)", output)

    def test_markdown_output_is_unchanged(self):
        self.assertEqual(self.run_main("--markdown"),
                         "<!-- generated from spec.json (Parameter test 1.0.0) -->\n\n"
                         "| Method | Path | Purpose |\n"
                         "| --- | --- | --- |\n"
                         "| GET | `/items` |  |\n")


if __name__ == "__main__":
    unittest.main()
