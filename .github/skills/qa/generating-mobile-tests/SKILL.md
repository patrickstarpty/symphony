---
name: generating-mobile-tests
version: "1.0.0"
description: "Generate iOS/Android mobile tests with platform detection and accessibility checks"
category: generation
phase: post-coding
platforms: ["ios", "android"]
dependencies: ["test-driven-development"]
soft_dependencies: []
input_schema:
  - name: "platform"
    type: "string"
    required: false
    description: "ios | android | cross-platform (auto-detect if omitted)"
  - name: "screen_list"
    type: "array"
    required: true
    description: "List of screen names to test"
  - name: "test_scenarios"
    type: "array"
    required: true
    description: "User flows: tap, swipe, input, assertions"
output_schema:
  - name: "test_suites"
    type: "array"
    description: "Generated test files (XCTest, Espresso, or Appium)"
  - name: "accessibility_audit"
    type: "object"
    description: "WCAG A11y violations found"
  - name: "platform_detected"
    type: "string"
    description: "ios | android | flutter"
---

# generating-mobile-tests

Generate native and cross-platform mobile tests. Auto-detects platform from project structure (Xcode, Gradle, flutter.yaml). Produces framework-specific code: XCTest (Swift) for iOS, Espresso (Kotlin) for Android, Appium (TypeScript) for cross-platform. Validates accessibility: VoiceOver labels, touch targets >= 44pt.

## When to Use

Use when mobile app structure is stable. Run before committing mobile tests to verify platform detection and accessibility.

## Instructions

1. Provide list of screen names and test scenarios
2. Run `scripts/platform-detector.py` to identify iOS/Android/Flutter
3. Run `scripts/accessibility-checker.py` to scan for accessibility violations
4. Generate platform-specific tests using corresponding template
5. Output includes accessibility audit and platform detection confidence

## Guardrails

- **No XPath fallback.** Use accessibility ID, content-desc, or image matching; XPath only if no alternative.
- **Rotation tests required.** All tests must handle device rotation (portrait/landscape).
- **Accessibility enabled.** Tests must include VoiceOver/TalkBack labels in assertions.
- **No hardcoded coordinates.** Use element identifiers, not pixel coordinates.
- **Touch targets >= 44pt.** Flag any buttons/clickable < 44x44 dp (iOS) or 48x48 dp (Android).

## Consumers

- `test-driven-development` — provides mobile testing context
- Mobile QA engineers — extend generated tests with platform-specific edge cases

## References

- `appium-patterns.md` — cross-platform element finding, gesture commands
- `xctest-patterns.md` — iOS XCTest API, async patterns, accessibility
- `uiautomator-patterns.md` — Android Espresso, UIAutomator locators
