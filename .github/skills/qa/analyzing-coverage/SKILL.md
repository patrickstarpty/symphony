---
name: analyzing-coverage
version: "1.0.0"
description: "Interpret coverage gaps, assess risk, suggest which untested paths matter most"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: []
soft_dependencies: ["scoring-risk"]
input_schema:
  - name: "coverage_data"
    type: "object"
    required: true
  - name: "threshold"
    type: "number"
    required: false
    description: "Default: 80"
  - name: "component_criticality"
    type: "string"
    required: false
    description: "critical | high | medium | low"
output_schema:
  - name: "summary"
    type: "object"
    description: "Lines, branches, functions percentages"
  - name: "verdict"
    type: "string"
  - name: "gaps"
    type: "array"
    description: "Uncovered paths with risk and suggestions"
---

# analyzing-coverage

Interpret coverage reports beyond "is the number above threshold." Assess which uncovered paths carry the most risk and suggest where to add tests.

## When to Use

After test execution completes (post-coding). Feeds into `generating-qa-report` (Coverage dimension) and optionally enriches `validating-acceptance-criteria`.

## Instructions

1. Parse coverage data using `scripts/coverage-report.py`:
   - Accepts Istanbul (JSON), JaCoCo (XML), coverage.py (JSON), lcov formats
   - Outputs standardized JSON: `{lines: N, branches: N, functions: N, files: [...]}`

2. Compare line/branch/function against threshold (default 80%, override via input or `scoring-risk` P3 dynamic thresholds).

3. Per uncovered file, assess risk:
   - **Critical:** Error handling, security-sensitive, payment/auth logic
   - **High:** User-facing features, data mutation, API endpoints
   - **Medium:** Business logic, internal services
   - **Low:** Utilities, helpers, formatters

4. Run `scripts/coverage-gap-analyzer.py` for specific untested paths — identifies uncovered branches, error handlers, edge cases.

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
- **P3 enhancement:** When `scoring-risk` output is available, use dynamic thresholds (critical=95%, high=85%, medium=80%, low=70%).
