#!/usr/bin/env python3
"""Check if diff implementation covers all acceptance criteria.

Usage: echo '{"diff": "...", "acceptance_criteria": [...]}' | python spec-compliance-checker.py
Output: JSON with stage1_spec_compliance verdict.
"""

import json
import sys
import re


def extract_ac_keywords(ac_text: str) -> list:
    """Extract keywords from AC for searching in diff."""
    # Remove common words and split on word boundaries
    stopwords = {'the', 'a', 'an', 'is', 'are', 'must', 'should', 'will', 'when', 'then', 'given'}
    words = re.findall(r'\b\w+\b', ac_text.lower())
    return [w for w in words if w not in stopwords and len(w) > 3]


def search_diff_for_ac(diff_text: str, ac_text: str, keywords: list) -> bool:
    """Search diff for evidence of AC implementation."""
    diff_lower = diff_text.lower()

    # Look for exact phrase match
    if ac_text.lower() in diff_lower:
        return True

    # Look for significant keyword matches (>50% of keywords)
    matches = sum(1 for kw in keywords if kw in diff_lower)
    if matches >= len(keywords) * 0.5 and len(keywords) > 0:
        return True

    # Look for variable/function name related to AC
    # e.g., "password validation" → search for "password" or "validate"
    for keyword in keywords:
        if re.search(rf'\b{keyword}s?\b', diff_lower):
            return True

    return False


def check_compliance(diff_text: str, criteria: list) -> dict:
    """Check if diff covers all acceptance criteria."""
    if not criteria:
        return {
            'verdict': 'UNKNOWN',
            'details': 'No acceptance criteria provided',
            'covered': [],
            'uncovered': []
        }

    covered = []
    uncovered = []

    for ac in criteria:
        ac_id = ac.get('id', '?')
        ac_text = ac.get('text', '')

        if not ac_text.strip():
            continue

        keywords = extract_ac_keywords(ac_text)
        is_covered = search_diff_for_ac(diff_text, ac_text, keywords)

        record = {
            'id': ac_id,
            'text': ac_text[:100],  # truncate for output
            'covered': is_covered
        }

        if is_covered:
            covered.append(record)
        else:
            uncovered.append(record)

    verdict = 'PASS' if len(uncovered) == 0 else 'FAIL'

    return {
        'verdict': verdict,
        'coverage_ratio': f"{len(covered)}/{len(criteria)}",
        'covered': covered,
        'uncovered': uncovered
    }


def main():
    data = json.load(sys.stdin)
    diff = data.get('diff', '')
    criteria = data.get('acceptance_criteria', [])

    result = check_compliance(diff, criteria)

    output = {
        'stage1_spec_compliance': result
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
