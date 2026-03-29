#!/usr/bin/env python3
"""Find new selector in updated code and suggest locator fix.

Usage: echo '{"test_selector": "...", "diff": "...", "framework": "playwright"}' | python locator-updater.py
Output: JSON with suggested new selector.
"""

import json
import sys
import re


def extract_selectors_from_code(code: str, framework: str = 'playwright') -> list:
    """Extract selectors from implementation code."""
    selectors = []

    if framework in ('playwright', 'js', 'typescript'):
        # CSS selectors, data-testid, etc.
        patterns = [
            r"data-testid=['\"]([^'\"]+)['\"]",
            r"querySelector\(['\"]([^'\"]+)['\"]\)",
            r"css: ['\"]([^'\"]+)['\"]",
            r"getByTestId\(['\"]([^'\"]+)['\"]\)",
        ]
    elif framework in ('selenium', 'py', 'python'):
        patterns = [
            r"By\.CSS_SELECTOR, ['\"]([^'\"]+)['\"]",
            r"By\.ID, ['\"]([^'\"]+)['\"]",
            r"By\.CLASS_NAME, ['\"]([^'\"]+)['\"]",
        ]
    else:
        patterns = []

    for pattern in patterns:
        for match in re.finditer(pattern, code):
            selectors.append(match.group(1))

    return list(set(selectors))


def find_new_selector(diff: str, old_selector: str, framework: str) -> str:
    """Find new selector in diff that replaced old one."""
    # Extract added lines (with +)
    added_lines = [
        line[1:] for line in diff.split('\n')
        if line.startswith('+') and not line.startswith('+++')
    ]
    added_code = '\n'.join(added_lines)

    # Find similar new selectors
    new_selectors = extract_selectors_from_code(added_code, framework)

    if not new_selectors:
        return None

    # Return most likely match (first one, or fuzzy match to old)
    # Simple heuristic: prefer selectors that share words with old
    old_words = set(re.findall(r'\w+', old_selector.lower()))

    best_match = None
    best_score = -1

    for selector in new_selectors:
        new_words = set(re.findall(r'\w+', selector.lower()))
        overlap = len(old_words & new_words)
        if overlap > best_score:
            best_match = selector
            best_score = overlap

    return best_match if best_score > 0 else new_selectors[0]


def main():
    data = json.load(sys.stdin)
    test_selector = data.get('test_selector', '')
    diff = data.get('diff', '')
    framework = data.get('framework', 'playwright')

    if not test_selector or not diff:
        json.dump({'error': 'Missing selector or diff'}, sys.stdout)
        return

    new_selector = find_new_selector(diff, test_selector, framework)

    output = {
        'old_selector': test_selector,
        'new_selector': new_selector,
        'confidence': 'high' if new_selector else 'low'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
