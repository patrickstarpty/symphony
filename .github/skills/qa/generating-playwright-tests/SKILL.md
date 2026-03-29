---
name: generating-playwright-tests
version: "1.0.0"
description: "Generate Page Object Model tests from HTML pages with stable selectors and accessibility assertions"
category: generation
phase: post-coding
platforms: ["web"]
dependencies: ["test-driven-development"]
soft_dependencies: []
input_schema:
  - name: "page_url"
    type: "string"
    required: true
    description: "URL of page to analyze (http:// or file://)"
  - name: "test_scenarios"
    type: "array"
    required: true
    description: "List of test scenarios describing user flows"
  - name: "output_format"
    type: "string"
    required: false
    default: "ts"
    description: "ts | js"
output_schema:
  - name: "page_objects"
    type: "array"
    description: "Generated Page Object Model classes"
  - name: "test_specs"
    type: "array"
    description: "Generated test spec files"
  - name: "selector_audit"
    type: "object"
    description: "Selector stability analysis"
  - name: "accessibility_issues"
    type: "array"
    description: "Found accessibility violations"
---

# generating-playwright-tests

Generate type-safe Playwright tests using Page Object Model pattern. Analyzes HTML, extracts stable selectors, flags fragile DOM patterns, generates spec files with AAA structure.

## When to Use

Use after HTML/UI is stabilized to generate test scaffolds. Run before committing test files to verify selector stability.

## Instructions

1. Provide page URL and list of test scenarios (user flows, assertions)
2. Run `scripts/page-analyzer.py` to extract page structure, interactive elements, ARIA landmarks
3. Run `scripts/selector-strategy.py` to recommend selectors (data-testid > role > css), flag fragile XPath/nth-child
4. Generate Page Object Model using `page-object.ts.liquid` template
5. Generate spec files using `spec.ts.liquid` template with AAA (Arrange/Act/Assert) structure
6. Output includes selector audit and accessibility violations

## Guardrails

- **Stable selectors only.** Prioritize data-testid > aria-label/role > CSS selectors. Flag any XPath on dynamic content.
- **No hardcoded waits.** Use waitForSelector or loadState instead of sleep().
- **Accessibility checks.** Flag missing form labels, color contrast issues, touch targets < 44pt.
- **No credentials in code.** Flag any test data containing passwords or API keys.
- **Cross-browser ready.** Generated code runs on Chromium, Firefox, WebKit.

## Consumers

- `test-driven-development` — provides test strategy context
- E2E test engineers — extend generated Page Objects and specs

## References

- `playwright-patterns.md` — wait strategies, network mocking, debugging techniques
- `pom-conventions.md` — Page Object structure, method naming conventions
- `web-testing-standards.md` — WCAG A11y, responsive design, cross-browser patterns
