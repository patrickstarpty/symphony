#!/usr/bin/env python3
"""Calculate defect density from historical defect data (Knowledge Base).

Usage: echo '{"files": [...], "defect_history": {...}}' | python defect-density-calculator.py
Output: JSON with defect_score (0-25) and history summary.

Graceful degradation: No history available → score = 0 (neutral).
"""

import json
import sys
from collections import defaultdict


def calculate_defect_score(files: list, defect_history: dict) -> int:
    """Calculate defect points (0-25) from historical density.

    Heuristic:
    - No history → 0 (neutral, don't penalize unknowns)
    - <1 defect per 1000 lines → 5 points
    - 1-2 defects per 1000 lines → 10 points
    - 2-5 defects per 1000 lines → 15 points
    - >5 defects per 1000 lines → 25 points (hotspot)
    """
    if not defect_history or not files:
        return 0

    total_defects = 0

    for filepath in files:
        # Normalize path for lookup
        normalized = filepath.lstrip('./')

        file_defects = defect_history.get(normalized, {})
        if isinstance(file_defects, dict):
            total_defects += file_defects.get('count', 0)
        else:
            total_defects += file_defects

    if total_defects == 0:
        return 0

    # Estimate density (defects per file is rough proxy)
    density = total_defects / max(len(files), 1)

    if density < 1:
        return 5
    elif density < 2:
        return 10
    elif density < 5:
        return 15
    else:
        return 25


def main():
    data = json.load(sys.stdin)
    files = data.get('files', [])
    defect_history = data.get('defect_history', {})

    defect_score = calculate_defect_score(files, defect_history)

    # Summarize history for transparency
    file_summaries = {}
    for filepath in files:
        normalized = filepath.lstrip('./')
        if normalized in defect_history:
            file_summaries[normalized] = defect_history[normalized]

    output = {
        'defect_score': defect_score,
        'total_defects': sum(
            d.get('count', 0) if isinstance(d, dict) else d
            for d in defect_history.values()
        ) if defect_history else 0,
        'affected_files_with_history': len(file_summaries),
        'file_summaries': file_summaries,
        'confidence': 'high' if defect_history else 'low'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
