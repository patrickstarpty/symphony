#!/usr/bin/env python3
"""Detect iOS, Android, or Flutter from project structure.

Usage:
  python platform-detector.py --project-dir . --output platform.json

Output: JSON with detected platform, confidence, framework version.
"""

import argparse
import json
import sys
from pathlib import Path


def detect_platform(project_dir: str) -> dict:
    """Detect platform from project files."""
    project_path = Path(project_dir)

    result: dict = {
        "platform": None,
        "confidence": 0.0,
        "detected_files": [],
        "ios_indicators": [],
        "android_indicators": [],
        "flutter_indicators": [],
    }

    ios_files = [
        "ios/Runner.xcworkspace",
        "ios/Runner.xcodeproj",
        "Podfile",
        "ios/Podfile.lock",
    ]
    for f in ios_files:
        if (project_path / f).exists():
            result["ios_indicators"].append(f)
            result["detected_files"].append(f)

    android_files = [
        "android/app/build.gradle",
        "android/settings.gradle",
        "android/build.gradle",
        "android/gradle.properties",
    ]
    for f in android_files:
        if (project_path / f).exists():
            result["android_indicators"].append(f)
            result["detected_files"].append(f)

    flutter_files = [
        "pubspec.yaml",
        "pubspec.lock",
        "flutter.yaml",
    ]
    for f in flutter_files:
        if (project_path / f).exists():
            result["flutter_indicators"].append(f)
            result["detected_files"].append(f)

    ios_count = len(result["ios_indicators"])
    android_count = len(result["android_indicators"])
    flutter_count = len(result["flutter_indicators"])

    if flutter_count > 0:
        result["platform"] = "flutter"
        result["confidence"] = 0.95 if flutter_count >= 2 else 0.7
    elif ios_count > android_count:
        result["platform"] = "ios"
        result["confidence"] = min(0.95, ios_count / 4.0)
    elif android_count > 0:
        result["platform"] = "android"
        result["confidence"] = min(0.95, android_count / 4.0)
    else:
        result["platform"] = "unknown"
        result["confidence"] = 0.0

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect mobile platform")
    parser.add_argument("--project-dir", default=".", help="Project directory path")
    parser.add_argument("--output", default="platform.json", help="Output JSON file")
    args = parser.parse_args()

    result = detect_platform(args.project_dir)

    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Platform detection complete: {args.output}")
    print(f"Detected: {result['platform']} (confidence: {result['confidence']:.2%})")


if __name__ == "__main__":
    main()
