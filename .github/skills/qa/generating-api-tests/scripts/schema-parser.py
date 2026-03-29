#!/usr/bin/env python3
"""Parse OpenAPI 3.x, Swagger 2.0, GraphQL schemas; extract endpoints and schemas.

Usage:
  python schema-parser.py --schema openapi.json --output endpoints.json

Output: JSON with extracted endpoints, parameters, request/response schemas.
Accepts JSON-format OpenAPI specs. For YAML, convert to JSON first.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class EndpointParameter:
    name: str
    in_: str
    required: bool = False
    schema_ref: str = ""


@dataclass
class EndpointSchema:
    path: str
    method: str
    summary: str = ""
    parameters: list = field(default_factory=list)
    request_body_schema: str = ""
    response_schema: str = ""
    auth_required: bool = False


def parse_openapi(spec: dict) -> list:
    """Extract endpoints from OpenAPI 3.x spec."""
    endpoints = []

    paths = spec.get("paths", {})
    for path_str, path_item in paths.items():
        for method_str, operation in path_item.items():
            if method_str.startswith("x-") or not isinstance(operation, dict):
                continue

            endpoint = EndpointSchema(
                path=path_str,
                method=method_str.lower(),
                summary=operation.get("summary", ""),
            )

            for param in operation.get("parameters", []):
                endpoint.parameters.append(
                    asdict(EndpointParameter(
                        name=param.get("name", ""),
                        in_=param.get("in", ""),
                        required=param.get("required", False),
                        schema_ref=param.get("schema", {}).get("$ref", ""),
                    ))
                )

            request_body = operation.get("requestBody", {})
            if request_body:
                content = request_body.get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    endpoint.request_body_schema = schema.get("$ref", "")

            responses = operation.get("responses", {})
            if "200" in responses:
                response = responses["200"]
                content = response.get("content", {})
                if "application/json" in content:
                    schema = content["application/json"].get("schema", {})
                    endpoint.response_schema = schema.get("$ref", "")

            security = operation.get("security", [])
            endpoint.auth_required = len(security) > 0

            endpoints.append(endpoint)

    return endpoints


def parse_graphql(sdl: str) -> list:
    """Parse GraphQL SDL; extract queries and mutations."""
    endpoints = []

    for match in re.finditer(r'type\s+Query\s*\{([^}]+)\}', sdl):
        query_body = match.group(1)
        for fld in re.finditer(r'(\w+)\s*\([^)]*\)\s*:\s*([^,}\n]+)', query_body):
            name, return_type = fld.groups()
            endpoints.append(EndpointSchema(
                path=f"/graphql (query {name})",
                method="post",
                summary=f"GraphQL query: {name}",
                response_schema=return_type.strip(),
            ))

    for match in re.finditer(r'type\s+Mutation\s*\{([^}]+)\}', sdl):
        mutation_body = match.group(1)
        for fld in re.finditer(r'(\w+)\s*\([^)]*\)\s*:\s*([^,}\n]+)', mutation_body):
            name, return_type = fld.groups()
            endpoints.append(EndpointSchema(
                path=f"/graphql (mutation {name})",
                method="post",
                summary=f"GraphQL mutation: {name}",
                response_schema=return_type.strip(),
            ))

    return endpoints


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse API schema and extract endpoints")
    parser.add_argument("--schema", required=True, help="OpenAPI JSON or GraphQL SDL file")
    parser.add_argument("--output", default="endpoints.json", help="Output JSON file")
    args = parser.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Schema file not found: {args.schema}", file=sys.stderr)
        sys.exit(1)

    with open(schema_path) as f:
        if schema_path.suffix in ('.yaml', '.yml'):
            # Minimal YAML → JSON for simple flat OpenAPI specs (no anchors/aliases)
            print("Warning: YAML schemas require manual conversion to JSON for full support", file=sys.stderr)
            content_str = f.read()
            # Try treating as JSON after stripping YAML comments
            lines = [l for l in content_str.splitlines() if not l.strip().startswith('#')]
            try:
                content = json.loads('\n'.join(lines))
            except json.JSONDecodeError:
                print("Use JSON format for OpenAPI spec: convert with 'python -c \"import json,sys; ...' or yq", file=sys.stderr)
                sys.exit(1)
            endpoints = parse_openapi(content)
        elif schema_path.suffix == '.json':
            content = json.load(f)
            endpoints = parse_openapi(content)
        elif schema_path.suffix == '.graphql':
            sdl = f.read()
            endpoints = parse_graphql(sdl)
        else:
            print(f"Unsupported schema format: {schema_path.suffix}", file=sys.stderr)
            sys.exit(1)

    audit = {
        "total_endpoints": len(endpoints),
        "auth_required_count": sum(1 for e in endpoints if e.auth_required),
        "endpoints": [asdict(e) for e in endpoints],
    }

    with open(args.output, 'w') as f:
        json.dump(audit, f, indent=2)

    print(f"Schema parsing complete: {args.output}")


if __name__ == "__main__":
    main()
