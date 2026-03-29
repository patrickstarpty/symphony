#!/usr/bin/env python3
"""Scan and sanitize PII in test data.

Usage:
  cat fixtures.json | python pii-sanitizer.py

Input: JSON fixture array
Output: Sanitized JSON + PII audit report
"""

import json
import re
import sys
from typing import Any


PII_PATTERNS = {
    "ssn": (
        r"\b(?!999-99-9999)(?!000-00-0000)\d{3}-\d{2}-\d{4}\b",
        "999-99-9999"
    ),
    "phone": (
        r"\b(?!555-0100)(?!555-0199)[\d]{3}-[\d]{3}-[\d]{4}\b",
        "555-0100"
    ),
    "email_real": (
        r"\b(?!test_|example|localhost)[a-zA-Z0-9._%+-]+@(?!test\.|example\.)[a-zA-Z0-9.-]+\b",
        "test_user@test.example"
    ),
    "credit_card": (
        r"\b(?!4111-1111-1111-1111)(?!5555-5555-5555-5555)\d{4}-?\d{4}-?\d{4}-?\d{4}\b",
        "4111-1111-1111-1111"
    ),
    "license_plate": (
        r"\b[A-Z]{2}[0-9]{5,6}\b",
        "DL123456"
    ),
}


def scan_pii(value: Any) -> list:
    """Scan a value for PII patterns."""
    findings = []
    if not isinstance(value, str):
        return findings

    for pattern_name, (pattern, _) in PII_PATTERNS.items():
        matches = re.finditer(pattern, value, re.IGNORECASE)
        for match in matches:
            findings.append({
                "pattern": pattern_name,
                "found": match.group(0),
                "context": value[:50],
            })
    return findings


def sanitize_pii(obj: Any) -> tuple:
    """Recursively sanitize PII in object."""
    findings: list = []

    if isinstance(obj, dict):
        sanitized: Any = {}
        for key, value in obj.items():
            if isinstance(value, str):
                pii_found = scan_pii(value)
                findings.extend(pii_found)

                sanitized_value = value
                for _pattern_name, (pattern, replacement) in PII_PATTERNS.items():
                    sanitized_value = re.sub(pattern, replacement, sanitized_value, flags=re.IGNORECASE)
                sanitized[key] = sanitized_value
            elif isinstance(value, (dict, list)):
                sanitized[key], nested_findings = sanitize_pii(value)
                findings.extend(nested_findings)
            else:
                sanitized[key] = value
        return sanitized, findings

    elif isinstance(obj, list):
        sanitized_list: list = []
        for item in obj:
            sanitized_item, item_findings = sanitize_pii(item)
            findings.extend(item_findings)
            sanitized_list.append(sanitized_item)
        return sanitized_list, findings

    else:
        return obj, findings


def main() -> None:
    try:
        fixtures = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(fixtures, list):
        fixtures = [fixtures]

    sanitized_fixtures, all_findings = sanitize_pii(fixtures)

    audit_report: dict = {
        "total_fixtures": len(fixtures),
        "pii_findings": len(all_findings),
        "findings_by_pattern": {},
        "details": all_findings,
    }

    for finding in all_findings:
        pattern = finding["pattern"]
        audit_report["findings_by_pattern"][pattern] = \
            audit_report["findings_by_pattern"].get(pattern, 0) + 1

    output = {
        "fixtures": sanitized_fixtures,
        "pii_audit": audit_report,
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
