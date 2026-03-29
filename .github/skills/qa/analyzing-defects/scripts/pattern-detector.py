#!/usr/bin/env python3
"""Detect recurring patterns in defects.

Usage: echo '{"classified_defects": [...], "time_window": "90d"}' | python pattern-detector.py
Output: JSON with patterns and hotspots.
"""

import json
import sys
from collections import defaultdict


def detect_patterns(defects: list) -> list:
    """Identify recurring patterns across defects."""
    component_causes = defaultdict(lambda: defaultdict(int))

    for defect in defects:
        component = defect.get('component', 'unknown')
        cause = defect.get('root_cause', 'unknown')
        component_causes[component][cause] += 1

    patterns = []
    for component, causes in component_causes.items():
        total = sum(causes.values())
        if total >= 5:  # Require ≥5 data points
            dominant_cause = max(causes, key=causes.get)
            patterns.append({
                'component': component,
                'root_cause': dominant_cause,
                'frequency': total,
                'confidence': min(causes[dominant_cause] / total, 1.0)
            })

    return sorted(patterns, key=lambda x: x['frequency'], reverse=True)


def identify_hotspots(defects: list) -> list:
    """Identify components with high defect density."""
    component_defects = defaultdict(int)

    for defect in defects:
        component = defect.get('component', 'unknown')
        component_defects[component] += 1

    if not component_defects:
        return []

    avg = sum(component_defects.values()) / len(component_defects)

    hotspots = [
        {
            'component': comp,
            'defect_count': count,
            'density_multiplier': round(count / avg, 2)
        }
        for comp, count in component_defects.items()
        if count > (avg * 1.5)
    ]

    return sorted(hotspots, key=lambda x: x['defect_count'], reverse=True)


def main():
    data = json.load(sys.stdin)
    defects = data.get('classified_defects', [])

    patterns = detect_patterns(defects)
    hotspots = identify_hotspots(defects)

    output = {
        'patterns': patterns,
        'hotspots': hotspots,
        'pattern_count': len(patterns),
        'hotspot_count': len(hotspots),
        'defect_count': len(defects)
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
