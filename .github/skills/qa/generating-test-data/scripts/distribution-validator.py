#!/usr/bin/env python3
"""Validate statistical distribution of test data.

Usage:
  cat fixtures.json | python distribution-validator.py --field premium_amount --expected-mode 150

Input: JSON fixture array, field name
Output: Distribution analysis + verdict (realistic | synthetic)
"""

import argparse
import json
import statistics
import sys
from typing import Any


def extract_numeric_values(fixtures: list, field: str) -> list:
    """Extract numeric field values."""
    values = []
    for fixture in fixtures:
        value = fixture.get(field)
        if isinstance(value, (int, float)):
            values.append(float(value))
    return sorted(values)


def analyze_distribution(values: list) -> dict:
    """Analyze statistical distribution."""
    if not values:
        return {"error": "No numeric values found"}

    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0,
        "quartile_25": sorted(values)[len(values) // 4],
        "quartile_75": sorted(values)[3 * len(values) // 4],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate distribution of test data")
    parser.add_argument("--field", required=True, help="Field name to analyze")
    parser.add_argument("--expected-mode", type=float, help="Expected central tendency")
    parser.add_argument("--expected-range", type=float, help="Expected std deviation")
    args = parser.parse_args()

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        data = [data]

    values = extract_numeric_values(data, args.field)
    analysis = analyze_distribution(values)

    verdict = "realistic"
    warnings: list = []

    if analysis.get("count", 0) < 5:
        warnings.append("Sample size < 5 (too small for statistical analysis)")

    if args.expected_mode and values:
        distance_from_mode = abs(analysis["mean"] - args.expected_mode)
        if distance_from_mode > args.expected_mode * 0.5:
            warnings.append(f"Mean {analysis['mean']:.2f} far from expected mode {args.expected_mode}")
            verdict = "suspicious"

    if analysis.get("stdev", 0) > 0:
        cv = analysis["stdev"] / analysis["mean"] if analysis["mean"] != 0 else 0
        if cv > 2:
            warnings.append(f"High coefficient of variation {cv:.2f} (possible uniform random)")
            verdict = "synthetic"

    output = {
        "field": args.field,
        "analysis": analysis,
        "verdict": verdict,
        "warnings": warnings,
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
