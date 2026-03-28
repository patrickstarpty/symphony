---
name: selecting-regressions
version: "1.0.0"
description: "Select relevant regression tests from change impact analysis — run only affected tests"
category: execution
phase: post-coding
platforms: ["all"]
dependencies: ["scoring-risk"]
soft_dependencies: ["generating-playwright-tests", "generating-api-tests", "generating-mobile-tests", "generating-perf-tests"]
input_schema:
  - name: "git_diff"
    type: "string"
    required: true
  - name: "test_catalog"
    type: "object"
    required: true
    description: "Inventory of all available tests with metadata"
  - name: "dependency_graph"
    type: "object"
    required: false
    description: "From Knowledge Base MCP or build system"
  - name: "risk_score"
    type: "object"
    required: false
    description: "From scoring-risk skill"
output_schema:
  - name: "selected_tests"
    type: "array"
    description: "Ordered by priority"
  - name: "skipped_tests"
    type: "array"
    description: "With justification"
  - name: "estimated_time"
    type: "number"
  - name: "confidence"
    type: "string"
    description: "high (full graph) | medium (heuristic) | low (filename only)"
---

# selecting-regressions

Select regression tests for the change using change impact analysis. Minimize test execution time while maintaining confidence.

## When to Use

Invoke after coding phase completes but before running tests. Determines which tests to prioritize.

## Instructions

1. Run `scripts/change-impact-analyzer.py` on git diff
   - Output: directly and transitively affected files

2. Run `scripts/dependency-graph-walker.py` to expand transitive dependencies
   - Input: dependency graph (if available from Knowledge Base MCP)
   - Output: full set of affected modules

3. Map affected modules to test files using:
   - Test naming conventions (`src/foo.ts` → `src/__tests__/foo.test.ts`)
   - Import analysis (`import { X } from 'module'`)
   - Config mappings (if available)

4. Run `scripts/test-selector.py`
   - Input: affected tests, risk score (if available), test history
   - Output: prioritized test list with estimated runtime

5. Apply guardrails:
   - Risk=critical/high → add full regression suite as fallback
   - Shared infrastructure change → full suite
   - New code with no dependencies → only new tests
   - Low confidence → warn and recommend full suite

## Confidence Levels

| Level | Condition | Action |
|-------|-----------|--------|
| high | Full dependency graph available + complete test metadata | Trust selection; run selected tests only |
| medium | Heuristic detection (file matching) + partial test metadata | Run selection + smoke test suite |
| low | Filename matching only; no graph | Warn; recommend full test suite |

## Consumers

- CI/CD system — executes selected test list
- QA Evaluator — decides whether to run full suite vs selection

## Guardrails

- Never skip critical-path tests (auth, payments, policy approval)
- Low confidence → warn + suggest full suite
- Shared infrastructure changes (deps, config, middleware) → full regression
- Additive: when in doubt, include a test
- Max 15 min execution time; if exceeded, recommend sampling strategy
