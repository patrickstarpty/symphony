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

## Hotspot Identification

A hotspot is any component where `defect_density > 1.5× org_average`. Density = defects ÷ component_age_days.

## Consumers

- Knowledge Base maintainers — review proposed KB updates before committing
- `scoring-risk` — historical defect patterns inform future risk score calibration
- Human QA leads — review hotspot list for architectural or process decisions

## Guardrails

- **Patterns require ≥5 data points** for statistical significance.
- **NEVER auto-commit Knowledge Base updates.** Always propose for human review.
- **Sanitize before writing.** Remove user IDs, passwords, and PII from all KB proposals.
- **Distinguish scope.** Separate team-level patterns from org-level patterns in output.
