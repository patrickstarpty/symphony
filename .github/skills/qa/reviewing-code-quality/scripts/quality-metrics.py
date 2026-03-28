#!/usr/bin/env python3
"""Extract code quality metrics from diff.

Usage: echo '{"diff": "...", "language": "typescript"}' | python quality-metrics.py
Output: JSON with function lengths, complexity, nesting depth, duplication flags.
"""

import json
import sys
import re
from collections import defaultdict


def analyze_python_code(code: str) -> dict:
    """Analyze Python code metrics."""
    lines = code.split('\n')
    functions = []
    current_func = None
    indent_stack = []
    max_nesting = 0

    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Track indentation (proxy for nesting)
        while indent_stack and indent_stack[-1] >= indent:
            indent_stack.pop()
        indent_stack.append(indent)
        max_nesting = max(max_nesting, len(indent_stack))

        # Detect function definition
        if re.match(r'^\s*(async\s+)?def\s+\w+', line):
            if current_func:
                current_func['end_line'] = i - 1
                functions.append(current_func)
            func_match = re.search(r'def\s+(\w+)', line)
            current_func = {
                'name': func_match.group(1) if func_match else 'unknown',
                'start_line': i,
                'lines': 1
            }
        elif current_func:
            current_func['lines'] += 1

    if current_func:
        functions.append(current_func)

    return {
        'language': 'python',
        'functions': functions,
        'max_nesting': min(max_nesting, 5),  # cap at 5 for reasonableness
        'quality_issues': []
    }


def analyze_typescript_code(code: str) -> dict:
    """Analyze TypeScript code metrics."""
    lines = code.split('\n')
    functions = []
    current_func = None
    bracket_depth = 0
    max_nesting = 0

    for i, line in enumerate(lines):
        # Track bracket depth for nesting
        bracket_depth += line.count('{') - line.count('}')
        bracket_depth = max(bracket_depth, 0)  # prevent negative
        max_nesting = max(max_nesting, bracket_depth)

        # Detect function definition
        if re.search(r'\bfunction\s+\w+|^\s*\w+\s*\([^)]*\)\s*(?::|=>)', line):
            if current_func:
                functions.append(current_func)
            func_name = re.search(r'\b(?:function\s+)?(\w+)\s*\(', line)
            current_func = {
                'name': func_name.group(1) if func_name else 'anonymous',
                'start_line': i,
                'lines': 1
            }
        elif current_func:
            current_func['lines'] += 1

    if current_func:
        functions.append(current_func)

    return {
        'language': 'typescript',
        'functions': functions,
        'max_nesting': min(max_nesting, 5),
        'quality_issues': []
    }


def flag_quality_issues(metrics: dict) -> list:
    """Flag quality issues based on metrics."""
    issues = []

    for func in metrics.get('functions', []):
        if func.get('lines', 0) > 30:
            issues.append({
                'severity': 'major',
                'type': 'function_too_long',
                'function': func['name'],
                'lines': func['lines'],
                'suggestion': 'Extract to smaller functions (target: <30 lines)'
            })

        if func.get('lines', 0) > 50:
            issues.append({
                'severity': 'critical',
                'type': 'function_too_long',
                'function': func['name'],
                'lines': func['lines'],
                'suggestion': 'Break into multiple functions (<30 lines each)'
            })

    if metrics.get('max_nesting', 0) > 3:
        issues.append({
            'severity': 'major',
            'type': 'deep_nesting',
            'depth': metrics['max_nesting'],
            'suggestion': 'Reduce nesting depth to ≤3 using early returns or extraction'
        })

    return issues


def main():
    data = json.load(sys.stdin)
    diff = data.get('diff', '')
    language = data.get('language', 'unknown').lower()

    # Extract code additions from diff
    code_additions = '\n'.join(
        line[1:] for line in diff.split('\n')
        if line.startswith('+') and not line.startswith('+++')
    )

    if language == 'python':
        metrics = analyze_python_code(code_additions)
    elif language in ('typescript', 'javascript', 'ts', 'js'):
        metrics = analyze_typescript_code(code_additions)
    else:
        metrics = {
            'language': 'unknown',
            'functions': [],
            'max_nesting': 0,
            'quality_issues': []
        }

    # Flag issues
    metrics['quality_issues'] = flag_quality_issues(metrics)

    output = {
        'stage2_code_quality': {
            'metrics': metrics,
            'verdict': 'REQUEST_CHANGES' if metrics['quality_issues'] else 'APPROVE'
        }
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
