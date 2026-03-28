---
name: generating-qa-report
version: "1.0.0"
description: "Aggregate evaluation dimensions into structured QA Report for issue workpad"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: ["analyzing-coverage", "validating-acceptance-criteria", "classifying-test-failures"]
input_schema:
  - name: "coverage_result"
    type: "object"
    required: true
  - name: "acceptance_result"
    type: "object"
    required: true
  - name: "failure_result"
    type: "object"
    required: true
  - name: "issue_id"
    type: "string"
    required: true
  - name: "gate_policy"
    type: "string"
    required: false
    description: "strict | advisory (default: advisory)"
output_schema:
  - name: "report_markdown"
    type: "string"
  - name: "verdict"
    type: "string"
  - name: "dimensions"
    type: "array"
---

# generating-qa-report

Aggregate the three evaluation dimensions (Pass Rate, Coverage, Acceptance) into a single QA Report. This is the quality gate decision point.

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
