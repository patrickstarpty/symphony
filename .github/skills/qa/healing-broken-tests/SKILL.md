---
name: healing-broken-tests
version: "1.0.0"
description: "Auto-repair tests broken by intentional code changes — update selectors, fixtures, expected values"
category: execution
phase: post-coding
platforms: ["all"]
dependencies: ["classifying-test-failures"]
soft_dependencies: ["generating-qa-report"]
input_schema:
  - name: "broken_tests"
    type: "array"
    required: true
  - name: "git_diff"
    type: "string"
    required: true
  - name: "intent"
    type: "string"
    required: true
    description: "Intended change description (from issue/PR)"
output_schema:
  - name: "healed_tests"
    type: "array"
  - name: "unhealed_tests"
    type: "array"
  - name: "patches"
    type: "array"
  - name: "confidence"
    type: "string"
    description: "high (locator) | medium (expected value) | low (logic)"
---

# healing-broken-tests

Auto-repair tests broken by intentional code changes. Categorizes breakage type and applies high-confidence fixes only.

## When to Use

Invoke after test failures classified but before reporting to QA gates. Fixes broken tests caused by intentional changes so they don't block the quality gate.

## Instructions

1. Receive list of failing tests from `classifying-test-failures`
2. Run `scripts/failure-pattern-matcher.py` on failure logs
   - Categorize by breakage type: locator | expected_value | logic
3. Run `scripts/diff-correlator.py`
   - Map each failure to specific diff hunks
   - Identify if breakage was intentional (related to PR goal)
4. For high-confidence failures:
   - Run `scripts/locator-updater.py` → find new selector in updated code
   - Update assertion values from diff
5. Apply patches to test files
6. Re-run healed tests to verify they pass
7. Output `healed_tests` (now passing) and `unhealed_tests` (flagged for human review)

## Breakage Types and Repair Strategy

| Type | Detection | Repair | Confidence |
|------|-----------|--------|------------|
| Locator change | "element not found" + Element selector in diff changed | Find new selector in updated code | High |
| Expected value | "expected X got Y" + Return value changed intentionally | Update assertion to match new intentional behavior | Medium |
| Logic change | TypeError, AttributeError, assertion logic broken | Flag for human review — needs intent understanding | Low |

## Confidence Levels

- **High:** Locator updates are mechanical; apply automatically if healed test passes
- **Medium:** Expected value updates require Intent validation; apply with human review
- **Low:** Logic changes; always flag for human review. Never auto-heal.

## Consumers

- CI/CD system — re-run healed tests to verify
- `analyzing-defects` — ingests healed vs unhealed pattern data
- QA report — counts healed tests as resolved, unhealed as true failures

## Guardrails

- Never auto-heal a test detecting a real bug
- High-confidence (locator) can auto-apply if healed test passes
- Medium/low require human review
- Never change test logic (conditionals, loops)
- Only update data: selectors, expected values, fixtures
- If patch fails re-run, report as unhealed
