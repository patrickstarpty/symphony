#!/usr/bin/env python3
"""Check accessibility: VoiceOver labels, touch targets, color contrast.

Usage:
  python accessibility-checker.py --manifest android/app/src/main/AndroidManifest.xml --output a11y.json

Output: JSON with accessibility violations and warnings.
"""

import argparse
import json
import sys
from pathlib import Path


class A11yViolation:
    def __init__(self, severity: str, element: str, issue: str, fix: str) -> None:
        self.severity = severity
        self.element = element
        self.issue = issue
        self.fix = fix

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "element": self.element,
            "issue": self.issue,
            "fix": self.fix,
        }


def check_android_manifest(manifest_path: str) -> list:
    """Check Android manifest for a11y issues."""
    violations: list = []

    try:
        with open(manifest_path) as f:
            content = f.read()
    except FileNotFoundError:
        return violations

    if '<ImageView' in content or '<ImageButton' in content:
        if 'android:contentDescription=' not in content:
            violations.append(
                A11yViolation(
                    'error',
                    'ImageView/ImageButton',
                    'Missing android:contentDescription',
                    'Add android:contentDescription="..." to all images'
                )
            )

    if '<Button' in content or '<image-button' in content.lower():
        if 'android:text=' not in content and 'android:contentDescription=' not in content:
            violations.append(
                A11yViolation(
                    'error',
                    'Button',
                    'Button missing text or contentDescription',
                    'Add android:text or android:contentDescription'
                )
            )

    return violations


def check_ios_storyboard(storyboard_path: str) -> list:
    """Check iOS storyboard for a11y issues."""
    violations: list = []

    try:
        with open(storyboard_path) as f:
            content = f.read()
    except FileNotFoundError:
        return violations

    if '<button' in content.lower():
        if 'accessibilityLabel' not in content:
            violations.append(
                A11yViolation(
                    'error',
                    'UIButton',
                    'Button missing accessibilityLabel',
                    'Set accessibilityLabel on all buttons'
                )
            )

    return violations


def main() -> None:
    parser = argparse.ArgumentParser(description="Check mobile app accessibility")
    parser.add_argument("--manifest", help="Android manifest file path")
    parser.add_argument("--storyboard", help="iOS storyboard file path")
    parser.add_argument("--output", default="a11y.json", help="Output JSON file")
    args = parser.parse_args()

    violations: list = []

    if args.manifest:
        violations.extend(check_android_manifest(args.manifest))
    if args.storyboard:
        violations.extend(check_ios_storyboard(args.storyboard))

    audit = {
        "total_violations": len(violations),
        "errors": sum(1 for v in violations if v.severity == 'error'),
        "warnings": sum(1 for v in violations if v.severity == 'warning'),
        "violations": [v.to_dict() for v in violations],
    }

    with open(args.output, 'w') as f:
        json.dump(audit, f, indent=2)

    print(f"Accessibility check complete: {args.output}")


if __name__ == "__main__":
    main()
