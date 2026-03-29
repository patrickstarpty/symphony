#!/usr/bin/env python3
"""Classify defects by root cause category.

Usage: echo '{"failures": [...]}' | python root-cause-classifier.py
Output: JSON with classified defects.
"""

import json
import sys
import re


CATEGORY_PATTERNS = {
    'logic': [
        r'(null|undefined|none)',
        r'(off.by.one|boundary|edge.case)',
        r'(state.management|mutation)',
        r'(conditional|if.else)',
    ],
    'integration': [
        r'(api|endpoint|contract)',
        r'(async|promise|timeout)',
        r'(dependency|import)',
        r'(mock|stub)',
    ],
    'data': [
        r'(validation|sanitiz)',
        r'(schema|format)',
        r'(type|casting)',
        r'(boundary|range)',
    ],
    'config': [
        r'(environment|env)',
        r'(config|setting)',
        r'(constant|hardcoded)',
    ],
    'concurrency': [
        r'(race|concurrent)',
        r'(lock|mutex)',
        r'(stale|reference)',
        r'(parallel)',
    ],
}


def classify_defect(error_log: str, component: str = '') -> str:
    """Classify defect into category."""
    text = (error_log + ' ' + component).lower()

    scores = {}
    for category, patterns in CATEGORY_PATTERNS.items():
        matches = sum(1 for p in patterns if re.search(p, text))
        scores[category] = matches

    if not scores or max(scores.values()) == 0:
        return 'unknown'

    return max(scores, key=scores.get)


def main():
    data = json.load(sys.stdin)
    failures = data.get('failures', [])

    classified = []
    for failure in failures:
        error = failure.get('error', '')
        component = failure.get('component', '')
        category = classify_defect(error, component)

        classified.append({
            'defect_id': failure.get('id', failure.get('test_id')),
            'component': component,
            'root_cause': category,
            'error_snippet': error[:100]
        })

    summary = {}
    for defect in classified:
        cause = defect['root_cause']
        summary[cause] = summary.get(cause, 0) + 1

    output = {
        'classified_defects': classified,
        'root_cause_distribution': summary,
        'total': len(classified)
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
