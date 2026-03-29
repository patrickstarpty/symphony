---
name: classifying-test-failures
description: "Classifies test failures as real bugs, flaky tests, or environment issues via retry analysis and error pattern matching. Use when test execution has failures and a Pass Rate verdict is needed, or before healing broken tests to determine which failures require fixing."
---

# classifying-test-failures

Classify test failures into actionable categories: real bugs that need fixing, flaky tests that need stabilization, and environment issues that need infrastructure attention.

## Quick Reference

**Phase:** post-coding  
**Inputs:**
- `failed_tests` (array, required) — list of failing test names/paths
- `test_command` (string, required) — command to re-run individual tests
- `retry_count` (number, optional) — default 2

**Outputs:**
- `classifications` — per-test category (real-bug | flaky | env-issue) with retry data
- `real_bugs` / `flaky` / `env_issues` — counts per category
- `verdict` — PASS (zero real-bugs) | FAIL

## When to Use

Post-coding, when test execution has failures. Feeds the Pass Rate dimension into `generating-qa-report`. Also consumed by `healing-broken-tests` (P3).

## Instructions

1. Run `scripts/retry-failures.sh` for each failed test (up to retry_count, default 2):
   - Re-runs each failed test in isolation
   - Captures exit code and stderr for each attempt

2. Classify based on retry results and error patterns:
   - **real-bug:** Consistent assertion error with identical stack trace across all retries
   - **flaky:** Passes on retry, or fails with different error messages across retries
   - **env-issue:** Error matches environment patterns (connection refused, timeout, OOM, port conflict)

3. Run `scripts/classify-failure.py` for pattern-based error matching as a secondary signal.

4. Determine verdict:
   - **PASS:** Zero real-bugs (flaky and env-issues reported but don't block)
   - **FAIL:** One or more real-bugs

5. Output:
   ```json
   {
     "classifications": [
       {
         "test": "test_payment_retry",
         "category": "real-bug",
         "error": "AssertionError: Expected 3 got 0",
         "retries": 2,
         "consistent": true
       },
       {
         "test": "test_ws_reconnect",
         "category": "flaky",
         "error": "Timeout: 5000ms",
         "retries": 2,
         "passed_on_retry": true
       }
     ],
     "real_bugs": 1,
     "flaky": 1,
     "env_issues": 0,
     "verdict": "FAIL"
   }
   ```

## Guardrails

- **Max 2 retries in P1.** Don't burn CI time with excessive retries.
- **Passing on retry = flaky, not fixed.** Don't silently promote to passing.
- **Identical assertion across all retries = real bug.** Don't classify as flaky just because it's intermittent.
- **P3 enhancement:** Historical pass rate analysis via Knowledge Base replaces simple retry heuristics.
