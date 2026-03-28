#!/usr/bin/env python3
"""Format pattern insights for Knowledge Base updates.

Usage: echo '{"patterns": [...], "hotspots": [...]}' | python knowledge-base-writer.py
Output: JSON with proposed Knowledge Base updates (for human review).
"""

import json
import sys
from datetime import datetime


def generate_updates(patterns: list, hotspots: list) -> list:
    """Generate proposed Knowledge Base entries."""
    updates = []

    # Pattern entries
    for pattern in patterns:
        updates.append({
            'type': 'pattern',
            'component': pattern['component'],
            'title': f"Recurring {pattern['root_cause']} issues in {pattern['component']}",
            'description': f"Detected {pattern['frequency']} instances of {pattern['root_cause']} failures",
            'frequency': pattern['frequency'],
            'recommendation': generate_recommendation(pattern['root_cause']),
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'pending_review'
        })

    # Hotspot entries
    for hotspot in hotspots:
        updates.append({
            'type': 'hotspot',
            'component': hotspot['component'],
            'title': f"{hotspot['component']} is a defect hotspot",
            'description': f"Defect density {hotspot['density_multiplier']}x org average ({hotspot['defect_count']} defects)",
            'density': hotspot['density_multiplier'],
            'recommendation': "Increase test coverage, review architecture, consider refactoring",
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'pending_review'
        })

    return updates


def generate_recommendation(root_cause: str) -> str:
    """Generate specific recommendation based on root cause."""
    recommendations = {
        'logic': "Review implementation logic, add boundary testing, improve code review for this component",
        'integration': "Add integration tests, verify API contracts, test async timing",
        'data': "Strengthen validation rules, add schema tests, expand test data coverage",
        'config': "Add environment-specific tests, centralize configuration, validate on startup",
        'concurrency': "Add concurrency tests, review locking strategy, test under load",
    }
    return recommendations.get(root_cause, "Review and improve test coverage for this component")


def main():
    data = json.load(sys.stdin)
    patterns = data.get('patterns', [])
    hotspots = data.get('hotspots', [])

    updates = generate_updates(patterns, hotspots)

    output = {
        'knowledge_base_updates': updates,
        'update_count': len(updates),
        'note': 'All updates require human review before committing to Knowledge Base',
        'status': 'pending_review'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
