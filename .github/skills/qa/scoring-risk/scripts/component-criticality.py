#!/usr/bin/env python3
"""Determine component criticality from file paths and registry.

Usage: echo '{"files": ["src/payments/processor.ts"], "registry": {...}}' | python component-criticality.py
Output: JSON with criticality_score (0-35) and component tier.
"""

import json
import sys
import re


DEFAULT_REGISTRY = {
    "payment": {"tier": "critical", "score": 35},
    "auth": {"tier": "critical", "score": 30},
    "security": {"tier": "critical", "score": 30},
    "policy": {"tier": "high", "score": 20},
    "claim": {"tier": "high", "score": 20},
    "customer": {"tier": "high", "score": 20},
    "api": {"tier": "high", "score": 20},
    "database": {"tier": "high", "score": 20},
    "util": {"tier": "low", "score": 10},
    "helper": {"tier": "low", "score": 10},
    "test": {"tier": "low", "score": 5},
}


def detect_component(filepath: str, registry: dict) -> dict:
    """Detect component from filepath using registry and heuristics."""
    filepath_lower = filepath.lower()

    # Direct registry lookup
    for component, config in registry.items():
        if re.search(rf'/{component}s?/', filepath_lower) or filepath_lower.startswith(component):
            return config

    # Fallback: directory-based detection
    parts = filepath_lower.split('/')
    if len(parts) > 1:
        dir_name = parts[1]  # assume src/component/...
        for key, config in DEFAULT_REGISTRY.items():
            if dir_name.startswith(key):
                return config

    # Default to low criticality
    return DEFAULT_REGISTRY.get("util", {"tier": "low", "score": 10})


def calculate_max_criticality(files: list, registry: dict) -> dict:
    """Return the highest criticality component found."""
    scores = []

    for filepath in files:
        component = detect_component(filepath, registry)
        scores.append({
            'file': filepath,
            'tier': component.get('tier', 'low'),
            'score': component.get('score', 10)
        })

    if not scores:
        return {
            'criticality_score': 10,
            'tier': 'low',
            'components': [],
            'confidence': 'low'
        }

    max_score = max(scores, key=lambda x: x['score'])

    return {
        'criticality_score': max_score['score'],
        'tier': max_score['tier'],
        'components': scores,
        'confidence': 'medium' if len(scores) > 0 else 'low'
    }


def main():
    data = json.load(sys.stdin)
    files = data.get('files', [])
    registry = data.get('registry', DEFAULT_REGISTRY)

    result = calculate_max_criticality(files, registry)
    json.dump(result, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
