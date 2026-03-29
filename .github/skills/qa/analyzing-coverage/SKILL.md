---
name: analyzing-coverage
description: "Interprets coverage reports by risk-ranking uncovered paths and producing a Pass/Fail verdict. Use when test execution is complete and coverage data is available (Istanbul, JaCoCo, coverage.py, lcov), or when gaps need risk-weighted analysis before the QA report."
---

# analyzing-coverage

Interpret coverage reports beyond "is the number above threshold." Assess which uncovered paths carry the most risk and suggest where to add tests.

## Quick Reference

**Phase:** post-coding  
**Inputs:**
- `coverage_data` (object, required) — Istanbul, JaCoCo, coverage.py, or lcov format
- `threshold` (number, optional) — default 80
- `component_criticality` (string, optional) — critical | high | medium | low

**Outputs:**
- `summary` — lines, branches, functions percentages
- `verdict` — PASS | FAIL
- `gaps` — uncovered paths with risk rating and test suggestions

**Works better with:** scoring-risk (enables dynamic per-component thresholds)

**Load before starting:** `rules/qa-standards.md` — default thresholds (80% line, mandatory error path coverage)

## When to Use

After test execution completes (post-coding). Feeds into `generating-qa-report` (Coverage dimension) and optionally enriches `validating-acceptance-criteria`.

## Instructions

0. **Generate coverage report if not already present.** Run the appropriate command for the project:
   - JavaScript/TypeScript: `npm test -- --coverage` (Jest) or `npx vitest run --coverage`
   - Python: `pytest --cov=src --cov-report=json`
   - Java/Kotlin: `mvn test jacoco:report` or `./gradlew test jacocoTestReport`
   - Go: `go test ./... -coverprofile=coverage.out`
   If output file is missing or empty after running, output `verdict: "unavailable"` and stop.

1. Parse coverage data using `scripts/coverage-report.py`:
   - Accepts Istanbul (JSON), JaCoCo (XML), coverage.py (JSON), lcov formats
   - Outputs standardized JSON: `{lines: N, branches: N, functions: N, files: [...]}`
   **Script unavailable:** open the coverage HTML report in browser or read the JSON/XML directly — look for lines/branches/functions percentages.

2. Compare line/branch/function against threshold (default 80%, override via input or dynamic thresholds from scoring-risk).

3. Per uncovered file, assess risk:
   - **Critical:** Error handling, security-sensitive, payment/auth logic
   - **High:** User-facing features, data mutation, API endpoints
   - **Medium:** Business logic, internal services
   - **Low:** Utilities, helpers, formatters

4. Run `scripts/coverage-gap-analyzer.py` for specific untested paths — identifies uncovered branches, error handlers, edge cases.
   **Script unavailable:** manually review uncovered lines in the coverage report, prioritize gaps in files touched by this PR.

5. Suggest concrete test cases for high-risk gaps (description only, not code).

6. Output:
   ```json
   {
     "summary": {"lines": 85.2, "branches": 72.1, "functions": 91.0},
     "verdict": "PASS",
     "gaps": [
       {"file": "src/payments/retry.ts", "risk": "critical", "uncovered": "catch block L45-52", "suggestion": "Test payment timeout retry logic"}
     ]
   }
   ```

## Guardrails

- **Coverage is a signal, not a goal.** Don't suggest trivial tests to inflate numbers.
- **No data → "unavailable" verdict.** Never silently pass when coverage data is missing.
- **Don't inflate.** Suggesting tests for getters/setters/toString to hit threshold is an anti-pattern.
- **When `scoring-risk` output is available, use dynamic thresholds (critical=95%, high=85%, medium=80%, low=70%). Otherwise use default 80%.**

## Output

Write coverage results to the `## Copilot Workpad` issue comment:
```markdown
### QA: coverage
verdict: PASS | FAIL | unavailable
lines: X% | branches: X% | functions: X%
threshold: X% (from scoring-risk or default 80%)
gaps: [file: reason: suggestion] for each high-risk gap
```

## Consumers

- `generating-qa-report` — receives Coverage dimension verdict and gap list
