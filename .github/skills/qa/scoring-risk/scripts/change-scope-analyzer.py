#!/usr/bin/env python3
"""Analyze change scope: files changed, lines delta, blast radius.

Usage: echo '<git_diff_text>' | python change-scope-analyzer.py
Output: JSON with scope score (0-25) and factors.
"""

import json
import sys
import re


def parse_diff(diff_text: str) -> dict:
    """Parse unified diff format and extract metrics."""
    files = {}
    current_file = None
    additions = 0
    deletions = 0

    for line in diff_text.split('\n'):
        # File header: +++ b/path/to/file or --- a/path/to/file
        if line.startswith('+++'):
            current_file = line.replace('+++ b/', '').strip()
            if current_file and current_file not in files:
                files[current_file] = {'additions': 0, 'deletions': 0}
        elif line.startswith('---') and not line.startswith('--- a/'):
            continue
        elif line.startswith('-') and not line.startswith('---'):
            deletions += 1
            if current_file and current_file in files:
                files[current_file]['deletions'] += 1
        elif line.startswith('+') and not line.startswith('+++'):
            additions += 1
            if current_file and current_file in files:
                files[current_file]['additions'] += 1

    return {
        'files_changed': len(files),
        'total_additions': additions,
        'total_deletions': deletions,
        'total_lines_delta': additions + deletions,
        'files': files
    }


def calculate_scope_score(metrics: dict) -> int:
    """Calculate scope points (0-25) from change metrics.

    Heuristic:
    - 1-3 files, <50 lines → 5 points (small fix)
    - 4-10 files, 50-200 lines → 10 points (feature)
    - 11-30 files, 200-500 lines → 15 points (module refactor)
    - 30+ files, 500+ lines → 25 points (major refactor/infra change)
    """
    files = metrics['files_changed']
    lines = metrics['total_lines_delta']

    if files <= 3 and lines < 50:
        return 5
    elif files <= 10 and lines < 200:
        return 10
    elif files <= 30 and lines < 500:
        return 15
    else:
        return 25


def identify_blast_radius(files: dict) -> list:
    """Identify files modified that suggest broad impact."""
    blast_files = []
    high_risk_patterns = [
        r'package\.json|requirements\.txt|pyproject\.toml',  # deps
        r'tsconfig\.json|babel\.config\.js|setup\.cfg',      # config
        r'\.env\.|secrets\.',                                 # secrets (bad)
        r'utils\.ts?|helpers\.py|shared/',                   # shared code
        r'middleware/|interceptors/',                         # global middleware
    ]

    for filename in files.keys():
        for pattern in high_risk_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                blast_files.append(filename)
                break

    return blast_files


def main():
    diff_text = sys.stdin.read()

    if not diff_text.strip():
        json.dump({
            'scope_score': 0,
            'files_changed': 0,
            'total_lines_delta': 0,
            'blast_radius': [],
            'confidence': 'low'
        }, sys.stdout, indent=2)
        return

    metrics = parse_diff(diff_text)
    scope_score = calculate_scope_score(metrics)
    blast_radius = identify_blast_radius(metrics['files'])

    output = {
        'scope_score': scope_score,
        'files_changed': metrics['files_changed'],
        'total_additions': metrics['total_additions'],
        'total_deletions': metrics['total_deletions'],
        'total_lines_delta': metrics['total_lines_delta'],
        'blast_radius': blast_radius,
        'blast_radius_count': len(blast_radius),
        'confidence': 'high' if metrics['files_changed'] > 0 else 'low'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
