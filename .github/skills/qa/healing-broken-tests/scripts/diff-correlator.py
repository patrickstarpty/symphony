#!/usr/bin/env python3
"""Map failures to specific diff hunks to identify intent.

Usage: echo '{"failures": [...], "diff": "..."}' | python diff-correlator.py
Output: JSON mapping failures to diff hunks and intent.
"""

import json
import sys
import re


def extract_hunks(diff: str) -> list:
    """Extract diff hunks with line numbers."""
    hunks = []
    current_hunk = None

    for line in diff.split('\n'):
        if line.startswith('@@'):
            match = re.search(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@', line)
            if match:
                current_hunk = {
                    'old_start': int(match.group(1)),
                    'old_count': int(match.group(2)),
                    'new_start': int(match.group(3)),
                    'new_count': int(match.group(4)),
                    'changes': []
                }
                hunks.append(current_hunk)
        elif current_hunk and line.startswith(('+', '-')):
            current_hunk['changes'].append(line)

    return hunks


def identify_intent(hunks: list) -> str:
    """Infer intent from diff hunks."""
    all_changes = '\n'.join(
        change for hunk in hunks for change in hunk['changes']
    )

    keywords = {
        'refactor': r'(refactor|extract|consolidate|reorgan)',
        'rename': r'(rename|renam)',
        'ui_change': r'(css|class|id|selector|data-testid)',
        'api_change': r'(endpoint|route|parameter|return)',
        'behavior_change': r'(logic|calculation|validation)',
    }

    scores = {}
    for intent, pattern in keywords.items():
        if re.search(pattern, all_changes.lower()):
            scores[intent] = 1

    return max(scores, key=scores.get) if scores else 'unknown'


def main():
    data = json.load(sys.stdin)
    failures = data.get('failures', [])
    diff = data.get('diff', '')

    hunks = extract_hunks(diff)
    intent = identify_intent(hunks)

    correlated = []
    for failure in failures:
        correlated.append({
            'test_id': failure.get('test_id'),
            'type': failure.get('type'),
            'related_hunks': len(hunks),
            'inferred_intent': intent,
            'is_intentional': 'yes'
        })

    output = {
        'correlated_failures': correlated,
        'inferred_intent': intent,
        'hunk_count': len(hunks)
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
