#!/usr/bin/env python3
"""Classify endpoints, generate edge case test scenarios.

Usage:
  cat endpoints.json | python endpoint-analyzer.py --output scenarios.json

Output: JSON with CRUD classification, edge case scenarios for each endpoint.
"""

import json
import sys
from dataclasses import dataclass, field, asdict


@dataclass
class EdgeCaseScenario:
    name: str
    description: str
    inputs: dict
    expected_status: int = 200


@dataclass
class EndpointAnalysis:
    path: str
    method: str
    operation_type: str
    risk_level: str
    edge_cases: list = field(default_factory=list)


def classify_operation(method: str, path: str) -> str:
    """Classify endpoint as CRUD, auth, or custom."""
    method_upper = method.upper()

    if method_upper == "GET":
        return "READ"
    elif method_upper == "POST":
        return "CREATE"
    elif method_upper in ("PUT", "PATCH"):
        return "UPDATE"
    elif method_upper == "DELETE":
        return "DELETE"
    else:
        return "CUSTOM"


def classify_risk_level(path: str, operation: str) -> str:
    """Classify endpoint risk: auth=high, payment=critical, CRUD=medium."""
    path_lower = path.lower()

    if "auth" in path_lower or "login" in path_lower:
        return "high"
    elif "payment" in path_lower or "billing" in path_lower:
        return "critical"
    elif "claim" in path_lower or "policy" in path_lower:
        return "high"
    elif operation in ("DELETE", "UPDATE"):
        return "medium"
    else:
        return "low"


def generate_edge_cases(endpoint: dict) -> list:
    """Generate common edge case scenarios."""
    cases = [
        EdgeCaseScenario(
            name="Happy path",
            description="Normal, valid request with valid inputs",
            inputs={"valid": True},
            expected_status=200 if endpoint["method"].upper() != "DELETE" else 204,
        ),
    ]

    if endpoint["method"].upper() == "GET":
        cases.extend([
            EdgeCaseScenario(
                name="Not found",
                description="Resource does not exist",
                inputs={"id": "nonexistent"},
                expected_status=404,
            ),
            EdgeCaseScenario(
                name="Empty query results",
                description="Query returns empty array",
                inputs={"filter": "never_matches"},
                expected_status=200,
            ),
        ])
    elif endpoint["method"].upper() in ("POST", "PUT", "PATCH"):
        cases.extend([
            EdgeCaseScenario(
                name="Missing required field",
                description="Request body missing required field",
                inputs={"missing_field": True},
                expected_status=400,
            ),
            EdgeCaseScenario(
                name="Invalid data type",
                description="Field has wrong data type",
                inputs={"email": 12345},
                expected_status=400,
            ),
            EdgeCaseScenario(
                name="Null values",
                description="Optional fields are null",
                inputs={"optional_field": None},
                expected_status=200,
            ),
        ])
    elif endpoint["method"].upper() == "DELETE":
        cases.append(
            EdgeCaseScenario(
                name="Delete nonexistent",
                description="Attempt to delete non-existent resource",
                inputs={"id": "nonexistent"},
                expected_status=404,
            )
        )

    if endpoint.get("auth_required"):
        cases.extend([
            EdgeCaseScenario(
                name="Missing authorization",
                description="Request without auth token",
                inputs={"auth": False},
                expected_status=401,
            ),
            EdgeCaseScenario(
                name="Invalid token",
                description="Request with malformed auth token",
                inputs={"auth": "invalid_token"},
                expected_status=401,
            ),
        ])

    return cases


def main() -> None:
    try:
        endpoints_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    analyses = []
    for endpoint in endpoints_data.get("endpoints", []):
        operation_type = classify_operation(endpoint["method"], endpoint["path"])
        risk_level = classify_risk_level(endpoint["path"], operation_type)
        edge_cases = generate_edge_cases(endpoint)

        analysis = EndpointAnalysis(
            path=endpoint["path"],
            method=endpoint["method"],
            operation_type=operation_type,
            risk_level=risk_level,
            edge_cases=[asdict(ec) for ec in edge_cases],
        )
        analyses.append(analysis)

    output = {
        "total_endpoints": len(analyses),
        "high_risk_count": sum(1 for a in analyses if a.risk_level in ("high", "critical")),
        "analyses": [asdict(a) for a in analyses],
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
