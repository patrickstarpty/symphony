#!/usr/bin/env python3
"""Map acceptance criteria to test evidence using keyword extraction and fuzzy matching.

Usage: echo '{"criteria": [...], "test_names": [...], "diff_files": [...]}' | python ac-evidence-mapper.py
Input: JSON with criteria array, test_names array, diff_files array.
Output: JSON with mappings per AC.
"""

import json
import re
import sys
from collections import defaultdict


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text, ignoring stop words."""
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "must", "need", "to", "of",
        "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "and", "or", "but", "not", "no", "if", "then", "when", "that", "this",
        "it", "its", "they", "them", "their", "we", "our", "you", "your",
    }
    # Split on non-alphanumeric, lowercase
    words = re.findall(r"[a-z]+", text.lower())
    return {w for w in words if w not in stop_words and len(w) > 2}


def normalize_test_name(name: str) -> str:
    """Convert test name patterns to space-separated words."""
    # camelCase → space-separated
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    # snake_case → space-separated
    name = name.replace("_", " ").replace("-", " ")
    return name.lower()


def match_score(ac_keywords: set[str], target_keywords: set[str]) -> float:
    """Calculate overlap score between keyword sets."""
    if not ac_keywords or not target_keywords:
        return 0.0
    intersection = ac_keywords & target_keywords
    return len(intersection) / len(ac_keywords)


def main():
    data = json.load(sys.stdin)
    criteria = data.get("criteria", [])
    test_names = data.get("test_names", [])
    diff_files = data.get("diff_files", [])

    # Pre-process test names
    test_keyword_map = {}
    for name in test_names:
        normalized = normalize_test_name(name)
        test_keyword_map[name] = extract_keywords(normalized)

    # Pre-process diff files
    file_keyword_map = {}
    for path in diff_files:
        filename = path.split("/")[-1].split(".")[0]
        normalized = normalize_test_name(filename)
        file_keyword_map[path] = extract_keywords(normalized)

    mappings = []
    for ac in criteria:
        ac_keywords = extract_keywords(ac.get("text", ""))
        ac_id = ac.get("id", "?")

        # Find matching tests
        matched_tests = []
        for test_name, test_keywords in test_keyword_map.items():
            score = match_score(ac_keywords, test_keywords)
            if score >= 0.3:  # 30% keyword overlap threshold
                matched_tests.append({"name": test_name, "score": round(score, 2)})

        matched_tests.sort(key=lambda t: t["score"], reverse=True)

        # Find matching diff files
        matched_files = []
        for filepath, file_keywords in file_keyword_map.items():
            score = match_score(ac_keywords, file_keywords)
            if score >= 0.2:  # Lower threshold for files
                matched_files.append({"path": filepath, "score": round(score, 2)})

        matched_files.sort(key=lambda f: f["score"], reverse=True)

        mappings.append({
            "id": ac_id,
            "keywords": sorted(ac_keywords),
            "matched_tests": matched_tests[:5],
            "matched_files": matched_files[:5],
            "has_test_evidence": len(matched_tests) > 0,
            "has_code_evidence": len(matched_files) > 0,
        })

    json.dump({"mappings": mappings}, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
