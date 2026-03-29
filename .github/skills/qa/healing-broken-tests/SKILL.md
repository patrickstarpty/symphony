---
name: healing-broken-tests
description: "Auto-repairs tests broken by intentional code changes by updating selectors, fixture values, and expected assertions. Use when test failures are classified and some are caused by deliberate behavior changes rather than real bugs, before QA gate reporting."
---

# healing-broken-tests

Auto-repair tests broken by intentional code changes. Categorizes breakage type and applies high-confidence fixes only.

## Quick Reference

**Phase:** post-coding  
**Inputs:**
- `broken_tests` (array, required) — failing test names/paths
- `git_diff` (string, required)
- `intent` (string, required) — intended change description from issue/PR

**Outputs:**
- `healed_tests` — tests now passing after repair
- `unhealed_tests` — flagged for human review
- `patches` — applied changes per test
- `confidence` — high (locator) | medium (expected value) | low (logic)

**Depends on:** classifying-test-failures  
**Works better with:** generating-qa-report

## When to Use

Invoke after test failures classified but before reporting to QA gates. Fixes broken tests caused by intentional changes so they don't block the quality gate.

## Prerequisites

This skill requires supporting infrastructure to operate. Before invoking:

1. **CI integration:** Failure records must be fed from CI output (not manually entered). Without CI data, `classifying-test-failures` cannot produce the input this skill needs.
2. **Knowledge Base populated:** Defect history (≥10 records) improves healing confidence. Without it, all classifications default to "Low" confidence requiring human review.

**Without this infrastructure:** Use `classifying-test-failures` only. Fix tests manually based on the classification output. Do not attempt auto-healing without CI + Knowledge Base.

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
   **Script unavailable:** for locator changes, search the updated code for the new element identifier (data-testid, aria-label) and update the selector manually. For expected value changes, read the diff and update the assertion to match the new intentional behavior.
5. Apply patches to test files
6. Re-run healed tests to verify they pass
7. Output `healed_tests` (now passing) and `unhealed_tests` (flagged for human review)

## Breakage Types and Repair Strategy

| Type | Detection | Repair | Confidence |
|------|-----------|--------|------------|
| Locator change | "element not found" + Element selector in diff changed | Find new selector in updated code | High |
| Expected value | "expected X got Y" + Return value changed intentionally | Update assertion to match new intentional behavior | Medium |
| Logic change | TypeError, AttributeError, assertion logic broken | Flag for human review — needs intent understanding | Low |

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
