#!/usr/bin/env python3
"""Mechanical documentation-coverage check over a generated OpenAPI document.

Measures presence, not quality: missing summaries, thin descriptions,
undescribed parameters and schema properties, absent error responses,
unregistered tags, duplicate operation IDs, placeholder examples,
deprecations without replacement guidance. Presence is the floor —
the documentation rubric is the bar.

Accepts JSON directly. For YAML it shells out to `node` with the target
repository's own `yaml` package (pass --repo so `require('yaml')` resolves).

Usage:
    python3 doc_coverage.py <spec.(json|yaml|yml)> [--repo <repo-root>]
                            [--operation <operationId> ...]

Exit codes: 0 no gaps, 1 gaps found, 2 usage/load error.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
PLACEHOLDER_EXAMPLES = {"string", "foo", "bar", "baz", "test", "example", "abc", "xyz", "lorem"}
THIN_DESCRIPTION_CHARS = 100
REPLACEMENT_HINTS = ("instead", "replaced", "use ", "migrate", "see ")

YAML_BRIDGE = (
    "const fs=require('fs');const {parse}=require('yaml');"
    "process.stdout.write(JSON.stringify(parse(fs.readFileSync(process.argv[1],'utf8'))))"
)


def load_spec(path: Path, repo: Path):
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    proc = subprocess.run(
        ["node", "-e", YAML_BRIDGE, str(path.resolve())],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "YAML load via node failed (is --repo a checkout with node_modules/yaml?):\n"
            + proc.stderr.strip()
        )
    return json.loads(proc.stdout)


def deref(spec, node, seen=None):
    """Resolve a local $ref one level; returns (resolved_node, ref_name_or_None)."""
    if isinstance(node, dict) and isinstance(node.get("$ref"), str):
        ref = node["$ref"]
        if ref.startswith("#/"):
            target = spec
            for part in ref[2:].split("/"):
                if not isinstance(target, dict) or part not in target:
                    return node, None
                target = target[part]
            return target, ref.rsplit("/", 1)[-1]
    return node, None


def is_placeholder(value) -> bool:
    return isinstance(value, str) and value.strip().lower() in PLACEHOLDER_EXAMPLES


def collect_refs(spec, node, refs, depth=0):
    """Collect names of component schemas reachable from node."""
    if depth > 40:
        return
    if isinstance(node, dict):
        resolved, name = deref(spec, node)
        if name:
            if name in refs:
                return
            refs.add(name)
            collect_refs(spec, resolved, refs, depth + 1)
            return
        for value in node.values():
            collect_refs(spec, value, refs, depth + 1)
    elif isinstance(node, list):
        for item in node:
            collect_refs(spec, item, refs, depth + 1)


def walk_properties(spec, schema, gaps, context, depth=0, seen=None):
    """Check inline (non-$ref) properties of a schema; $refs are handled once
    per component schema by check_schema, so stop at them here."""
    if depth > 20 or not isinstance(schema, dict):
        return
    seen = seen if seen is not None else set()
    node_id = id(schema)
    if node_id in seen:
        return
    seen.add(node_id)

    if "$ref" in schema:
        return
    for combinator in ("allOf", "oneOf", "anyOf"):
        for member in schema.get(combinator, []) or []:
            walk_properties(spec, member, gaps, context, depth + 1, seen)
    if isinstance(schema.get("items"), dict):
        walk_properties(spec, schema["items"], gaps, context, depth + 1, seen)

    for prop_name, prop in (schema.get("properties") or {}).items():
        if not isinstance(prop, dict):
            continue
        prop_context = f"{context}.{prop_name}"
        if "$ref" in prop:
            continue
        has_description = bool(str(prop.get("description") or "").strip())
        # description may ride on an allOf wrapper around a ref
        if not has_description and not any(k in prop for k in ("allOf", "oneOf", "anyOf")):
            gaps.append(f"property '{prop_context}' has no description")
        if is_placeholder(prop.get("example")):
            gaps.append(f"property '{prop_context}' has placeholder example {prop.get('example')!r}")
        walk_properties(spec, prop, gaps, prop_context, depth + 1, seen)


def check_operation(spec, method, url, op, path_item, registered_tags):
    gaps = []
    op_id = op.get("operationId")
    if not op_id:
        gaps.append("missing operationId")

    summary = str(op.get("summary") or "").strip()
    if not summary:
        gaps.append("missing summary")

    description = str(op.get("description") or "").strip()
    if not description:
        gaps.append("missing description")
    else:
        if len(description) < THIN_DESCRIPTION_CHARS:
            gaps.append(f"thin description ({len(description)} chars)")
        if summary and description.lower() == summary.lower():
            gaps.append("description merely restates the summary")

    if op.get("deprecated") and not any(h in description.lower() for h in REPLACEMENT_HINTS):
        gaps.append("deprecated without replacement guidance in the description")

    for tag in op.get("tags") or []:
        if tag not in registered_tags:
            gaps.append(f"tag '{tag}' not registered with a description in the document tag list")

    parameters = list(path_item.get("parameters") or []) + list(op.get("parameters") or [])
    for param in parameters:
        param, _ = deref(spec, param)
        if not isinstance(param, dict):
            continue
        pname = param.get("name", "<unnamed>")
        if not str(param.get("description") or "").strip():
            gaps.append(f"parameter '{pname}' ({param.get('in', '?')}) has no description")
        if is_placeholder(param.get("example")):
            gaps.append(f"parameter '{pname}' has placeholder example {param.get('example')!r}")

    body = op.get("requestBody")
    if body:
        body, _ = deref(spec, body)
        for media in (body.get("content") or {}).values():
            schema = media.get("schema")
            if isinstance(schema, dict):
                # $ref schemas are checked once in the schema section
                walk_properties(spec, schema, gaps, "body")

    responses = op.get("responses") or {}
    has_success = any(str(code).startswith("2") for code in responses)
    has_error = any(str(code)[:1] in ("4", "5") for code in responses)
    if not has_success:
        gaps.append("no 2xx response documented")
    if not has_error:
        gaps.append("no error responses documented")
    for code, response in responses.items():
        response, _ = deref(spec, response)
        if isinstance(response, dict) and not str(response.get("description") or "").strip():
            gaps.append(f"response {code} has no description")

    return gaps


def check_schema(spec, name, schema):
    gaps = []
    walk_properties(spec, schema, gaps, name)
    return gaps


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("spec", help="generated OpenAPI document (.json/.yaml/.yml)")
    parser.add_argument("--repo", default=".", help="repo root whose node_modules resolves 'yaml'")
    parser.add_argument(
        "--operation", action="append", default=[],
        help="limit to these operationIds (repeatable)",
    )
    args = parser.parse_args(argv)

    spec_path = Path(args.spec)
    if not spec_path.is_file():
        print(f"ERROR: no such file: {spec_path}", file=sys.stderr)
        return 2
    try:
        spec = load_spec(spec_path, Path(args.repo))
    except Exception as exc:
        print(f"ERROR: failed to load spec: {exc}", file=sys.stderr)
        return 2

    registered_tags = {
        t.get("name"): str(t.get("description") or "").strip()
        for t in spec.get("tags") or []
        if isinstance(t, dict)
    }
    registered_tags = {name for name, desc in registered_tags.items() if desc}

    wanted = set(args.operation)
    op_reports = []          # (label, gaps)
    op_id_locations = {}     # operationId -> [labels]
    reachable_schema_refs = set()
    checked = 0

    for url, path_item in sorted((spec.get("paths") or {}).items()):
        if not isinstance(path_item, dict):
            continue
        for method in sorted(path_item.keys() & HTTP_METHODS):
            op = path_item[method]
            if not isinstance(op, dict):
                continue
            op_id = op.get("operationId")
            label = f"{method.upper()} {url}" + (f" — {op_id}" if op_id else "")
            if op_id:
                op_id_locations.setdefault(op_id, []).append(label)
            if wanted and op_id not in wanted:
                continue
            checked += 1
            gaps = check_operation(spec, method, url, op, path_item, registered_tags)
            collect_refs(spec, {"b": op.get("requestBody"), "r": op.get("responses"),
                                "p": op.get("parameters")}, reachable_schema_refs)
            if gaps:
                op_reports.append((label, gaps))

    for op_id, labels in sorted(op_id_locations.items()):
        if len(labels) > 1 and (not wanted or op_id in wanted):
            op_reports.append((f"operationId '{op_id}'", [f"duplicated across: {', '.join(labels)}"]))

    schema_reports = []
    schemas = (spec.get("components") or {}).get("schemas") or {}
    for name in sorted(reachable_schema_refs & schemas.keys()):
        gaps = check_schema(spec, name, schemas[name])
        if gaps:
            schema_reports.append((name, gaps))

    missing = wanted - op_id_locations.keys()
    for op_id in sorted(missing):
        op_reports.append((f"operationId '{op_id}'", ["not found in the document"]))

    total = 0
    if op_reports:
        print("Operations")
        for label, gaps in op_reports:
            print(f"  {label}")
            for gap in gaps:
                print(f"    - {gap}")
                total += 1
    if schema_reports:
        print("Schemas (reachable from checked operations)")
        for name, gaps in schema_reports:
            print(f"  {name}")
            for gap in gaps:
                print(f"    - {gap}")
                total += 1

    print(
        f"Summary: {checked} operation(s) checked, {len(op_reports)} with gaps, "
        f"{len(schema_reports)} schema(s) with gaps, {total} gap(s) total."
    )
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
