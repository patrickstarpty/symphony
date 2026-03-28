#!/usr/bin/env python3
"""Analyze which modules are directly affected by a change.

Usage: echo '<git_diff>' | python change-impact-analyzer.py
Output: JSON with directly affected files.
"""

import json
import sys
import re


def parse_changed_files(diff_text: str) -> list:
    """Extract file paths from unified diff."""
    files = set()

    for line in diff_text.split('\n'):
        # Detect file headers: +++ b/path/to/file or --- a/path/to/file
        if line.startswith('+++ b/'):
            files.add(line.replace('+++ b/', '').strip())
        elif line.startswith('--- a/'):
            files.add(line.replace('--- a/', '').strip())

    return sorted(list(files))


def identify_test_files(changed_files: list) -> list:
    """Identify corresponding test files for changed source files."""
    test_files = []

    for filepath in changed_files:
        # Skip if already a test file
        if re.search(r'(__tests__|\.test\.|\.spec\.)', filepath):
            test_files.append(filepath)
            continue

        # Generate probable test paths
        patterns = [
            (r'src/(.*?)(\.ts$|\.js$|\.py$)', r'src/__tests__/\1.test\2'),
            (r'src/(.*?)(\.ts$|\.js$|\.py$)', r'src/\1.spec\2'),
            (r'lib/(.*?)(\.ts$|\.js$)', r'lib/__tests__/\1.test\2'),
            (r'(.*?)(\.ts$|\.js$)', r'\1.test\2'),
        ]

        for pattern, replacement in patterns:
            match = re.search(pattern, filepath)
            if match:
                test_path = re.sub(pattern, replacement, filepath)
                test_files.append(test_path)

    return list(set(test_files))


def main():
    diff_text = sys.stdin.read()

    changed_files = parse_changed_files(diff_text)
    test_files = identify_test_files(changed_files)

    output = {
        'directly_affected_files': changed_files,
        'probable_test_files': test_files,
        'file_count': len(changed_files),
        'confidence': 'high' if changed_files else 'low'
    }

    json.dump(output, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
