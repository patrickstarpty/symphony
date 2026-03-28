#!/usr/bin/env python3
"""Parse coverage reports from multiple tools into standardized JSON.

Usage: python coverage-report.py <format> < coverage_data
Formats: istanbul, jacoco, coverage-py, lcov
Output: Standardized JSON to stdout.
"""

import json
import re
import sys
import xml.etree.ElementTree as ET


def parse_istanbul(data: dict) -> dict:
    """Parse Istanbul/NYC JSON coverage format."""
    total_lines = 0
    covered_lines = 0
    total_branches = 0
    covered_branches = 0
    total_functions = 0
    covered_functions = 0
    files = []

    for filepath, file_data in data.items():
        s = file_data.get("s", {})
        b = file_data.get("b", {})
        f = file_data.get("f", {})

        file_lines = len(s)
        file_covered = sum(1 for v in s.values() if v > 0)
        file_branches = sum(len(arr) for arr in b.values())
        file_branch_covered = sum(1 for arr in b.values() for v in arr if v > 0)
        file_funcs = len(f)
        file_func_covered = sum(1 for v in f.values() if v > 0)

        total_lines += file_lines
        covered_lines += file_covered
        total_branches += file_branches
        covered_branches += file_branch_covered
        total_functions += file_funcs
        covered_functions += file_func_covered

        if file_lines > 0:
            pct = round(file_covered / file_lines * 100, 1)
            files.append({"path": filepath, "lines": pct})

    return {
        "lines": round(covered_lines / total_lines * 100, 1) if total_lines else 0,
        "branches": round(covered_branches / total_branches * 100, 1) if total_branches else 0,
        "functions": round(covered_functions / total_functions * 100, 1) if total_functions else 0,
        "files": sorted(files, key=lambda f: f["lines"]),
    }


def parse_lcov(text: str) -> dict:
    """Parse LCOV .info format."""
    total_lines = 0
    covered_lines = 0
    total_branches = 0
    covered_branches = 0
    total_functions = 0
    covered_functions = 0
    files = []
    current_file = None
    file_total = 0
    file_covered = 0

    for line in text.strip().split("\n"):
        if line.startswith("SF:"):
            current_file = line[3:]
            file_total = 0
            file_covered = 0
        elif line.startswith("LF:"):
            file_total = int(line[3:])
            total_lines += file_total
        elif line.startswith("LH:"):
            file_covered = int(line[3:])
            covered_lines += file_covered
        elif line.startswith("BRF:"):
            total_branches += int(line[4:])
        elif line.startswith("BRH:"):
            covered_branches += int(line[4:])
        elif line.startswith("FNF:"):
            total_functions += int(line[4:])
        elif line.startswith("FNH:"):
            covered_functions += int(line[4:])
        elif line.startswith("end_of_record"):
            if current_file and file_total > 0:
                pct = round(file_covered / file_total * 100, 1)
                files.append({"path": current_file, "lines": pct})

    return {
        "lines": round(covered_lines / total_lines * 100, 1) if total_lines else 0,
        "branches": round(covered_branches / total_branches * 100, 1) if total_branches else 0,
        "functions": round(covered_functions / total_functions * 100, 1) if total_functions else 0,
        "files": sorted(files, key=lambda f: f["lines"]),
    }


def parse_coverage_py(data: dict) -> dict:
    """Parse coverage.py JSON format."""
    totals = data.get("totals", {})
    files_data = data.get("files", {})
    files = []

    for filepath, file_data in files_data.items():
        summary = file_data.get("summary", {})
        pct = summary.get("percent_covered", 0)
        files.append({"path": filepath, "lines": round(pct, 1)})

    return {
        "lines": round(totals.get("percent_covered", 0), 1),
        "branches": round(totals.get("percent_covered_branches", 0), 1),
        "functions": 0,  # coverage.py doesn't track function coverage
        "files": sorted(files, key=lambda f: f["lines"]),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: coverage-report.py <istanbul|jacoco|coverage-py|lcov>", file=sys.stderr)
        sys.exit(1)

    fmt = sys.argv[1]
    raw = sys.stdin.read()

    if fmt == "istanbul":
        data = json.loads(raw)
        result = parse_istanbul(data)
    elif fmt == "lcov":
        result = parse_lcov(raw)
    elif fmt == "coverage-py":
        data = json.loads(raw)
        result = parse_coverage_py(data)
    elif fmt == "jacoco":
        # JaCoCo XML parsing
        root = ET.fromstring(raw)
        counters = {}
        for counter in root.findall(".//counter"):
            ctype = counter.get("type", "").lower()
            missed = int(counter.get("missed", 0))
            covered = int(counter.get("covered", 0))
            if ctype in counters:
                counters[ctype]["missed"] += missed
                counters[ctype]["covered"] += covered
            else:
                counters[ctype] = {"missed": missed, "covered": covered}

        def pct(key):
            c = counters.get(key, {"missed": 0, "covered": 0})
            total = c["missed"] + c["covered"]
            return round(c["covered"] / total * 100, 1) if total else 0

        result = {
            "lines": pct("line"),
            "branches": pct("branch"),
            "functions": pct("method"),
            "files": [],
        }
    else:
        print(f"Unknown format: {fmt}", file=sys.stderr)
        sys.exit(1)

    json.dump(result, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
