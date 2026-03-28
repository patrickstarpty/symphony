#!/usr/bin/env python3
"""Classify test failure errors by pattern matching.

Usage: echo '{"failures": [...]}' | python classify-failure.py
Input: JSON with failures array of {test, error} objects.
Output: JSON with classifications.
"""

import json
import re
import sys

ENV_PATTERNS = [
    (r"ECONNREFUSED", "Connection refused — service not running"),
    (r"ETIMEDOUT", "Connection timeout — network or service issue"),
    (r"ECONNRESET", "Connection reset — service crashed or restarted"),
    (r"EADDRINUSE", "Port already in use — cleanup needed"),
    (r"ENOMEM|OOM|out of memory", "Out of memory — resource constraint"),
    (r"ENOSPC", "No disk space — cleanup needed"),
    (r"EPERM|EACCES|permission denied", "Permission denied — filesystem issue"),
    (r"docker.*not found|container.*not running", "Docker container not available"),
    (r"could not connect to.*database", "Database connection failed"),
    (r"redis.*connection.*refused", "Redis not available"),
]

FLAKY_PATTERNS = [
    (r"timeout.*\d+ms|timed?\s*out", "Timeout — possibly flaky under load"),
    (r"race\s*condition|data\s*race", "Race condition detected"),
    (r"stale\s*element|element.*detached", "DOM element detached — timing issue"),
    (r"socket\s*hang\s*up", "Socket hang up — intermittent network"),
]

REAL_BUG_PATTERNS = [
    (r"AssertionError|AssertError|assert.*fail", "assertion"),
    (r"Expected.*(?:got|received|but was)", "assertion"),
    (r"TypeError|ReferenceError|AttributeError", "type_error"),
    (r"NameError|ImportError|ModuleNotFoundError", "import_error"),
    (r"NullPointerException|null.*reference", "null_reference"),
    (r"IndexError|ArrayIndexOutOfBoundsException", "bounds_error"),
    (r"KeyError|NoSuchElementException", "missing_key"),
]


def classify(error: str) -> tuple[str, str]:
    """Return (category, reason) for an error string."""
    for pattern, reason in ENV_PATTERNS:
        if re.search(pattern, error, re.IGNORECASE):
            return ("env-issue", reason)

    for pattern, reason in FLAKY_PATTERNS:
        if re.search(pattern, error, re.IGNORECASE):
            return ("flaky", reason)

    for pattern, reason in REAL_BUG_PATTERNS:
        if re.search(pattern, error, re.IGNORECASE):
            return ("real-bug", reason)

    return ("unknown", "No matching pattern — manual review needed")


def main():
    data = json.load(sys.stdin)
    failures = data.get("failures", [])

    classifications = []
    for f in failures:
        test = f.get("test", "unknown")
        error = f.get("error", "")
        category, reason = classify(error)
        classifications.append({
            "test": test,
            "category": category,
            "reason": reason,
            "error_snippet": error[:200],
        })

    counts = {"real-bug": 0, "flaky": 0, "env-issue": 0, "unknown": 0}
    for c in classifications:
        counts[c["category"]] = counts.get(c["category"], 0) + 1

    json.dump({
        "classifications": classifications,
        "real_bugs": counts["real-bug"],
        "flaky": counts["flaky"],
        "env_issues": counts["env-issue"],
        "unknown": counts["unknown"],
    }, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
