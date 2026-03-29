---
name: generating-qa-report
description: "Aggregates Pass Rate, Coverage, and Acceptance dimensions into a structured QA Report with overall PASS/FAIL verdict. Use when all three P1 evaluation skills (analyzing-coverage, validating-acceptance-criteria, classifying-test-failures) have produced outputs and a quality gate decision needs to be written to the issue workpad."
---

# generating-qa-report

Aggregate the three evaluation dimensions (Pass Rate, Coverage, Acceptance) into a single QA Report. This is the quality gate decision point.

## Quick Reference

**Phase:** post-coding  
**Inputs:**
- `coverage_result` (object, required) — from analyzing-coverage
- `acceptance_result` (object, required) — from validating-acceptance-criteria
- `failure_result` (object, required) — from classifying-test-failures
- `issue_id` (string, required)
- `gate_policy` (string, optional) — strict | advisory (default: advisory)

**Outputs:**
- `report_markdown` — formatted QA Report for issue workpad
- `verdict` — PASS | FAIL
- `dimensions` — per-dimension scores and statuses

**Depends on:** analyzing-coverage, validating-acceptance-criteria, classifying-test-failures

## When to Use

After all three P1 evaluation skills have produced their outputs. This is the final aggregation step before the verdict is written to the issue workpad.

## Instructions

1. Collect outputs from the three evaluation skills:
   - **Pass Rate** from `classifying-test-failures`: verdict + real_bugs count
   - **Coverage** from `analyzing-coverage`: verdict + summary percentages
   - **Acceptance** from `validating-acceptance-criteria`: verdict + satisfied/partial/unmet counts

2. Apply gate policy:
   - **strict:** ALL three dimensions must PASS → overall PASS. Any FAIL → overall FAIL.
   - **advisory** (default): Report all dimensions. No blocking — verdict is informational.

3. Generate markdown report from `templates/qa-report.md.liquid`:
   - Header: issue ID, evaluator, overall verdict
   - Dimension table: score, threshold, status per dimension
   - Details: test summary, coverage gaps, AC traceability matrix
   - Advisory note: if advisory mode, state what would fail under strict

4. Output markdown + structured verdict for programmatic consumption.

## Gate Policy Behavior

| Policy | PASS condition | FAIL behavior |
|--------|---------------|---------------|
| strict | All 3 dimensions PASS | Blocks issue transition |
| advisory | Report only | Warns but does not block |

## Guardrails

- **Reproducible given same inputs.** Same dimension results → same report, always.
- **Never omit a failing dimension.** Even in advisory mode, all dimensions are shown.
- **Advisory mode still states what would fail under strict.** Visibility is non-negotiable.
- **Don't editorialize.** Report facts, don't add subjective commentary.

## Consumers

- Issue workpad (written as markdown comment)
- `reviewing-code-quality` (P3) — QA gates must pass before code review
- `healing-broken-tests` (P3) — prioritizes which failures to address
- `analyzing-defects` (P3) — aggregate quality trends
