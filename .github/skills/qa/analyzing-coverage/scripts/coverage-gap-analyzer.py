#!/usr/bin/env python3
"""Analyze coverage gaps and categorize by risk.

Usage: echo '{"files": [...], "threshold": 80}' | python coverage-gap-analyzer.py
Input: JSON with standardized coverage files array and threshold.
Output: JSON with gaps categorized by risk.
"""

import json
import re
import sys

# Path patterns indicating higher risk
CRITICAL_PATTERNS = [
    r"(?:payment|billing|charge|refund|transaction)",
    r"(?:auth|login|session|token|credential|password|oauth)",
    r"(?:encrypt|decrypt|hash|sign|verify|secret)",
]

HIGH_PATTERNS = [
    r"(?:api|endpoint|route|controller|handler)",
    r"(?:user|account|profile|registration)",
    r"(?:claim|policy|premium|underwriting)",
    r"(?:mutation|write|update|delete|create)",
]

MEDIUM_PATTERNS = [
    r"(?:service|repository|domain|model|entity)",
    r"(?:validation|sanitize|parse|transform)",
]

LOW_PATTERNS = [
    r"(?:util|helper|format|convert|constant|config)",
    r"(?:logger|debug|trace|metric)",
    r"(?:type|interface|enum|dto|schema)",
]


def classify_risk(filepath: str) -> str:
    """Classify file risk based on path patterns."""
    path_lower = filepath.lower()
    for pattern in CRITICAL_PATTERNS:
        if re.search(pattern, path_lower):
            return "critical"
    for pattern in HIGH_PATTERNS:
        if re.search(pattern, path_lower):
            return "high"
    for pattern in MEDIUM_PATTERNS:
        if re.search(pattern, path_lower):
            return "medium"
    return "low"


def main():
    data = json.load(sys.stdin)
    files = data.get("files", [])
    threshold = data.get("threshold", 80)

    gaps = []
    for f in files:
        path = f.get("path", "")
        lines = f.get("lines", 100)

        if lines < threshold:
            risk = classify_risk(path)
            gap = {
                "file": path,
                "coverage": lines,
                "shortfall": round(threshold - lines, 1),
                "risk": risk,
            }
            gaps.append(gap)

    # Sort: critical first, then by shortfall descending
    risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps.sort(key=lambda g: (risk_order.get(g["risk"], 4), -g["shortfall"]))

    json.dump({
        "gaps": gaps,
        "total_below_threshold": len(gaps),
        "critical_gaps": sum(1 for g in gaps if g["risk"] == "critical"),
        "high_gaps": sum(1 for g in gaps if g["risk"] == "high"),
    }, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
