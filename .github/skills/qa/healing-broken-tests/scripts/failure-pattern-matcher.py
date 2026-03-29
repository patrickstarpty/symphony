#!/usr/bin/env python3
"""Categorize test failures by breakage type.

Usage: echo '{"failures": [...]}' | python failure-pattern-matcher.py
Output: JSON with categorized failures.
"""

import json
import sys
import re


def categorize_failure(failure_log: str) -> dict:
    """Classify failure into locator|expected_value|logic."""
    log_lower = failure_log.lower()

    # Locator failures: element not found, selector not matching
    if any(x in log_lower for x in [
        'element not found', 'no element matching', 'selector',
        'cannot find', 'element does not exist', 'visibility'
    ]):
        return {
            'type': 'locator',
            'confidence': 'high',
            'pattern': next(
                (x for x in ['element not found', 'selector', 'visibility']
                 if x in log_lower), 'element_not_found'
            )
        }

    # Expected value failures: assertion mismatch, value changed
    if any(x in log_lower for x in [
        'expected', 'assertion', 'equal', 'tobe', 'toequal',
        'got', 'received', 'but was'
    ]):
        return {
            'type': 'expected_value',
            'confidence': 'medium',
            'pattern': 'assertion_mismatch'
        }

    # Logic failures: errors, exceptions, type errors
    if any(x in log_lower for x in [
        'error', 'exception', 'typeerror', 'attributeerror',
        'referenceerror', 'syntaxerror', 'undefined', 'null'
    ]):
        return {
            'type': 'logic',
            'confidence': 'low',
            'pattern': 'runtime_error'
        }

    return {
        'type': 'unknown',
        'confidence': 'low',
        'pattern': 'unknown'
    }


def main():
    data = json.load(sys.stdin)
    failures = data.get('failures', [])

    categorized = []
    for failure in failures:
        test_id = failure.get('test_id', '?')
        log = failure.get('log', failure.get('error', ''))

        category = categorize_failure(log)
        categorized.append({
            'test_id': test_id,
            'type': category['type'],
            'confidence': category['confidence'],
            'pattern': category['pattern']
        })

    output = {
        'failures': categorized,
        'summary': {
            'locator': sum(1 for f in categorized if f['type'] == 'locator'),
            'expected_value': sum(1 for f in categorized if f['type'] == 'expected_value'),
            'logic': sum(1 for f in categorized if f['type'] == 'logic')
        }
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
