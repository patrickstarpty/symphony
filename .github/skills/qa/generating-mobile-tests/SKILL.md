---
name: generating-mobile-tests
description: "Generates native and cross-platform mobile tests (XCTest, Espresso, Appium) with platform auto-detection and accessibility validation. Use when mobile app structure is stable, or when VoiceOver/TalkBack labels, touch target sizes, or device rotation coverage need verification."
---

# generating-mobile-tests

Generate native and cross-platform mobile tests. Auto-detects platform from project structure (Xcode, Gradle, flutter.yaml). Produces framework-specific code: XCTest (Swift) for iOS, Espresso (Kotlin) for Android, Appium (TypeScript) for cross-platform. Validates accessibility: VoiceOver labels, touch targets.

## Quick Reference

**Phase:** post-coding  
**Platforms:** ios, android  
**Inputs:**
- `platform` (string, optional) — ios | android | cross-platform (auto-detected if omitted)
- `screen_list` (array, required) — screen names to test
- `test_scenarios` (array, required) — user flows: tap, swipe, input, assertions

**Outputs:**
- `test_suites` — generated test files (XCTest, Espresso, or Appium)
- `accessibility_audit` — WCAG violations found
- `platform_detected` — ios | android | flutter

**Depends on:** test-driven-development

## When to Use

Use when mobile app structure is stable. Run before committing mobile tests to verify platform detection and accessibility.

## Instructions

1. Accept `platform`, `screen_list`, and `test_scenarios` from caller inputs.
2. Run `scripts/platform-detector.py` on the project root → outputs `platform_detected` (ios | android | flutter). Use detected platform if `platform` input is omitted.
3. Run `scripts/accessibility-checker.py` on screen list → outputs `accessibility_audit`. Flag each WCAG violation but continue generation; do NOT block test output on violations.
4. Generate platform-specific tests using the matching template:
   - iOS → `ios.liquid` (XCTest / Swift)
   - Android → `android.liquid` (Espresso / Kotlin)
   - Flutter / cross-platform → `appium.liquid` (Appium / TypeScript)
5. Output `test_suites`, `accessibility_audit`, and `platform_detected`.

## Guardrails

- **No XPath fallback.** Use accessibility ID, content-desc, or image matching; XPath only if no alternative.
- **Rotation tests required.** All tests must handle device rotation (portrait/landscape).
- **Accessibility enabled.** Tests must include VoiceOver/TalkBack labels in assertions.
- **No hardcoded coordinates.** Use element identifiers, not pixel coordinates.
- **Touch targets — iOS.** Flag any tappable element < 44×44 pt.
- **Touch targets — Android.** Flag any tappable element < 48×48 dp.

## Consumers

- Mobile QA engineers — extend generated tests with platform-specific edge cases
- CI/CD system — executes generated XCTest, Espresso, or Appium suites

## References

- `appium-patterns.md` — cross-platform element finding, gesture commands
- `xctest-patterns.md` — iOS XCTest API, async patterns, accessibility
- `uiautomator-patterns.md` — Android Espresso, UIAutomator locators
