---
name: analyzing-defects
description: "Analyzes defect root causes, identifies recurring patterns and component hotspots, and proposes Knowledge Base updates. Use when logic, integration, data, config, or concurrency defect patterns need investigation after classifying failures and generating QA reports."
---

# analyzing-defects

Analyze root causes of test failures and defects. Identify patterns and hotspots. Propose Knowledge Base updates for human review.

## Quick Reference

**Phase:** post-coding  
**Inputs:**
- `defect_data` (array, required) — defect records: issue ID, root cause, component, resolution
- `time_window` (string, optional) — 30d | 90d | all (default: 90d)
- `scope` (string, optional) — team | component | project | organization

**Outputs:**
- `patterns` — recurring defect patterns with trend data
- `root_cause_distribution` — breakdown by logic | integration | data | config | concurrency
- `hotspots` — components with above-average defect density
- `recommendations` — specific, actionable improvement suggestions
- `knowledge_base_updates` — proposed KB entries (always for human review)

**Depends on:** classifying-test-failures, generating-qa-report, healing-broken-tests

## When to Use

Invoke after `classifying-test-failures`, `healing-broken-tests`, and `generating-qa-report` complete. Aggregates defect data to drive organizational learning.

## Instructions

1. Receive failure records from `classifying-test-failures` and healed/unhealed from `healing-broken-tests`
2. Run `scripts/root-cause-classifier.py`
   - Categorize each defect: logic | integration | data | config | concurrency
3. Run `scripts/pattern-detector.py`
   - Time-series analysis (freq by root cause, trend)
   - Component clustering (which components have defects)
   - Pattern recognition (recurring issues)
4. Identify hotspots (components with defect density > org average)
5. Generate recommendations:
   - Increase test coverage for hotspot components
   - Architectural changes (if pattern suggests design flaw)
   - Process improvements (if pattern suggests workflow issue)
6. Run `scripts/knowledge-base-writer.py`
   - Format proposals for Knowledge Base (patterns, hotspots, recommendations)
   - Always proposed for human review, never auto-committed
7. Output knowledge_base_updates for review

## Root Cause Categories

| Category | Examples | Prevention |
|----------|----------|-----------|
| Logic | Off-by-one, null handling, state management | Stronger typing, peer review |
| Integration | API contract breaking, async timing, dependency mismatch | Contract testing, integration tests |
| Data | Missing validation, schema mismatch, bad state | Test data factories, schema validation |
| Config | Wrong env vars, hardcoded values, missing settings | Config validation, environment tests |
| Concurrency | Race conditions, deadlock, stale references | Proper locking, async/await patterns |

## Pattern Examples

- **"Password validation never rejects special chars"** → Pattern: validation bypass (logic)
- **"Payment API breaks on amount > 1000"** → Pattern: numeric boundary (data)
- **"Tests pass locally, fail on CI"** → Pattern: environment difference (config)
- **"Flaky tests in parallel execution"** → Pattern: shared state (concurrency)

## Hotspot Identification

A hotspot is a component with defect density significantly above org average.

**Calculation:**
```
org_avg_density = total_defects / total_components
component_density = component_defects / component_age_days
is_hotspot = component_density > (org_avg_density * 1.5)
```

## Guardrails

- Patterns require ≥5 data points for statistical significance
- Recommendations must be specific and actionable
- Never commit Knowledge Base updates; always propose for human review
- Sanitize sensitive data before writing (remove user IDs, passwords, PII)
- Distinguish between local team and org-level patterns
