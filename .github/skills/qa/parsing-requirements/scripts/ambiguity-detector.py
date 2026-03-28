#!/usr/bin/env python3
"""Detect ambiguity signals in acceptance criteria text.

Usage: echo '{"criteria": [...]}' | python ambiguity-detector.py
Input: JSON with "criteria" array of {id, text} objects.
Output: JSON with "flags" array of {id, signal, category, suggestion}.
"""

import json
import re
import sys

VAGUE_VERBS = [
    ("appropriate", "Define specific behavior or values"),
    ("proper", "Specify exact requirements"),
    ("correct", "Define expected output precisely"),
    ("good", "Quantify with measurable criteria"),
    ("nice", "Specify visual/UX requirements"),
    ("fast", "Define latency threshold (e.g., <200ms p95)"),
    ("efficient", "Define resource budget (memory, CPU, time)"),
    ("secure", "List specific security requirements (OWASP)"),
    ("robust", "Define failure scenarios and expected handling"),
    ("user-friendly", "Specify usability criteria or standards"),
    ("intuitive", "Define expected user workflow steps"),
    ("reasonable", "Provide specific numeric bounds"),
    ("adequate", "Provide specific numeric bounds"),
    ("sufficient", "Provide specific numeric bounds"),
    ("handle.*gracefully", "Define error response format and status codes"),
]

MISSING_THRESHOLDS = [
    (r"\blarge\s+(?:number|amount|volume)\b", "Specify exact quantity or range"),
    (r"\bmany\b", "Specify exact count"),
    (r"\bquickly\b", "Specify time threshold"),
    (r"\bsoon\b", "Specify time threshold"),
    (r"\boften\b", "Specify frequency"),
    (r"\bmost\b", "Specify percentage or count"),
    (r"\bsome\b", "Specify exact count or percentage"),
    (r"\bfew\b", "Specify exact count"),
    (r"\bseveral\b", "Specify exact count"),
    (r"\bminimal\b", "Specify exact threshold"),
]

UNDEFINED_TERMS = [
    (r"\betc\.?\b", "List all items explicitly"),
    (r"\band\s+so\s+on\b", "List all items explicitly"),
    (r"\bsimilar\b", "Define similarity criteria"),
    (r"\bsuch\s+as\b.*$", "Provide exhaustive list or define boundary"),
    (r"\brelated\b", "Define the relationship explicitly"),
    (r"\bas\s+needed\b", "Define trigger conditions"),
    (r"\bif\s+(?:necessary|applicable)\b", "Define when it applies"),
]


def detect(criteria: list[dict]) -> list[dict]:
    flags = []
    for ac in criteria:
        ac_id = ac.get("id", "?")
        text = ac.get("text", "")
        text_lower = text.lower()

        for pattern, suggestion in VAGUE_VERBS:
            if re.search(rf"\b{pattern}\b", text_lower):
                flags.append({
                    "id": ac_id,
                    "signal": pattern.replace(".*", " "),
                    "category": "vague_verb",
                    "suggestion": suggestion,
                })

        for pattern, suggestion in MISSING_THRESHOLDS:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                flags.append({
                    "id": ac_id,
                    "signal": match.group(0) if match else pattern,
                    "category": "missing_threshold",
                    "suggestion": suggestion,
                })

        for pattern, suggestion in UNDEFINED_TERMS:
            if re.search(pattern, text_lower):
                match = re.search(pattern, text_lower)
                flags.append({
                    "id": ac_id,
                    "signal": match.group(0) if match else pattern,
                    "category": "undefined_term",
                    "suggestion": suggestion,
                })

    return flags


def main():
    data = json.load(sys.stdin)
    criteria = data.get("criteria", [])
    flags = detect(criteria)
    json.dump({"flags": flags, "total": len(flags)}, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
