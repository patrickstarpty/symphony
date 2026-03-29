#!/usr/bin/env python3
"""Select regression tests to run based on impact analysis and risk.

Usage: echo '{"affected_modules": [...], "risk_score": {...}, "test_catalog": {...}}' | python test-selector.py
Output: JSON with prioritized test selection.
"""

import json
import sys
from typing import Optional


def prioritize_tests(
    affected_modules: list,
    test_catalog: dict,
    risk_score: Optional[dict] = None
) -> dict:
    """Prioritize tests based on affected modules and risk."""

    selected = []
    skipped = []
    total_estimated_time = 0

    # Critical path tests (always run)
    critical_patterns = ['auth', 'payment', 'security', 'policy']

    risk_level = risk_score.get('risk_level', 'medium') if risk_score else 'medium'

    for test in test_catalog.get('tests', []):
        test_id = test.get('id')
        test_module = test.get('module', '')
        test_time = test.get('estimated_time_ms', 1000)
        tags = test.get('tags', [])

        # Always include critical path tests
        if any(t in tags for t in critical_patterns):
            selected.append(test)
            total_estimated_time += test_time
            continue

        # Include tests for affected modules (check both directions:
        # exact match, test module prefixes an affected path, or affected path prefixes test module)
        if test_module in affected_modules or any(
            m.startswith(test_module) or test_module.startswith(m)
            for m in affected_modules
        ):
            selected.append(test)
            total_estimated_time += test_time
            continue

        # For critical/high risk, add related smoke tests
        if risk_level in ('critical', 'high'):
            if 'smoke' in tags:
                selected.append(test)
                total_estimated_time += test_time
                continue

        # Everything else gets skipped
        skipped.append({
            'id': test_id,
            'module': test_module,
            'reason': 'not affected by change'
        })

    # If total time is high, recommend sampling
    confidence = 'high'
    note = None
    if total_estimated_time > 15 * 60 * 1000:  # >15 min
        confidence = 'medium'
        note = f"Estimated time {total_estimated_time / 1000 / 60:.1f} min. Consider sampling or parallel execution."

    if risk_level == 'low' and not affected_modules:
        confidence = 'low'
        note = 'No affected modules detected. Recommend full regression suite.'

    return {
        'selected_tests': [{'id': t.get('id'), 'module': t.get('module')} for t in selected],
        'skipped_tests': skipped,
        'total_tests': len(test_catalog.get('tests', [])),
        'selected_count': len(selected),
        'estimated_time_ms': total_estimated_time,
        'estimated_time_min': round(total_estimated_time / 1000 / 60, 1),
        'confidence': confidence,
        'note': note,
        'risk_level': risk_level
    }


def main():
    data = json.load(sys.stdin)
    affected_modules = data.get('transitive_affected', data.get('directly_affected_files', []))
    test_catalog = data.get('test_catalog', {})
    risk_score = data.get('risk_score')

    result = prioritize_tests(affected_modules, test_catalog, risk_score)

    json.dump(result, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
