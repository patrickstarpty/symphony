---
name: generating-playwright-tests
description: "Generates type-safe Playwright tests using Page Object Model with stable selectors and accessibility assertions. Use when HTML/UI is stabilized and E2E scaffolding is needed, or when fragile selectors, hardcoded waits, or missing WCAG accessibility checks are present."
---

# generating-playwright-tests

Generate type-safe Playwright tests using Page Object Model pattern. Analyzes HTML, extracts stable selectors, flags fragile DOM patterns, generates spec files with AAA structure.

## Quick Reference

**Phase:** post-coding  
**Platforms:** web  
**Inputs:**
- `page_url` (string, required) — URL to analyze (http:// or file://)
- `test_scenarios` (array, required) — user flows to cover
- `output_format` (string, optional) — ts | js (default: ts)

**Outputs:**
- `page_objects` — generated Page Object Model classes
- `test_specs` — generated spec files
- `selector_audit` — selector stability analysis
- `accessibility_issues` — WCAG violations found

**Depends on:** test-driven-development

## When to Use

Use after HTML/UI is stabilized to generate test scaffolds. Run before committing test files to verify selector stability.

## Instructions

1. Provide page URL and list of test scenarios (user flows, assertions)
2. Run `scripts/page-analyzer.py` to extract page structure, interactive elements, ARIA landmarks
3. Run `scripts/selector-strategy.py` to recommend selectors (data-testid > role > css), flag fragile XPath/nth-child
4. Generate Page Object Model using `page-object.ts.liquid` template
5. Generate spec files using `spec.ts.liquid` template with AAA structure
6. Output includes selector audit and accessibility violations

## Guardrails

- **Stable selectors only.** Prioritize data-testid > aria-label/role > CSS selectors. Flag any XPath on dynamic content.
- **No hardcoded waits.** Use waitForSelector or loadState instead of sleep().
- **Accessibility checks.** Flag missing form labels, color contrast issues, touch targets < 44pt.
- **No credentials in code.** Flag any test data containing passwords or API keys.
- **Cross-browser ready.** Generated code runs on Chromium, Firefox, WebKit.

## Consumers

- CI/CD system — executes generated Playwright specs in E2E pipeline
- E2E test engineers — extend generated Page Objects and specs

## References

- `playwright-patterns.md` — wait strategies, network mocking, debugging techniques
- `pom-conventions.md` — Page Object structure, method naming conventions
- `web-testing-standards.md` — WCAG A11y, responsive design, cross-browser patterns
