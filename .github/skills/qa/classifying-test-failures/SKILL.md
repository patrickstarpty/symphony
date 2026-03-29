---
name: classifying-test-failures
version: "1.0.0"
description: "Classify failures as real-bug, flaky, or environment-issue via retry and pattern analysis"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: []
input_schema:
  - name: "failed_tests"
    type: "array"
    required: true
  - name: "test_command"
    type: "string"
    required: true
  - name: "retry_count"
    type: "number"
    required: false
    description: "Default: 2"
output_schema:
  - name: "classifications"
    type: "array"
  - name: "real_bugs"
    type: "number"
  - name: "flaky"
    type: "number"
  - name: "env_issues"
    type: "number"
  - name: "verdict"
    type: "string"
    description: "PASS if zero real-bugs"
---

# classifying-test-failures

Classify test failures into actionable categories: real bugs that need fixing, flaky tests that need stabilization, and environment issues that need infrastructure attention.

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
