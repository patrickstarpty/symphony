---
name: test-driven-development
version: "1.0.0-qa"
description: "Enforce TDD Red-Green-Refactor: generate test cases from AC, write failing tests, implement, verify"
category: enforcement
phase: during-coding
platforms: ["all"]
dependencies: ["parsing-requirements"]
extends: "../test-driven-development/SKILL.md"
input_schema:
  - name: "acceptance_criteria"
    type: "array"
    required: true
  - name: "framework"
    type: "string"
    required: false
    description: "jest | pytest | playwright | junit. Auto-detected if omitted."
output_schema:
  - name: "test_cases"
    type: "array"
  - name: "test_files"
    type: "array"
  - name: "tdd_log"
    type: "array"
---

# test-driven-development (QA Extension)

> **Loading:** This extension loads *in addition to* the Superpowers TDD skill at `.github/skills/test-driven-development/`. On conflict, Superpowers wins. This skill only adds net-new content under `## QA Enhancements` headers.

## QA Enhancements

### 1. Test Case Generation from AC

For each acceptance criterion from `parsing-requirements`, generate test cases using:

**Equivalence Partitioning:**
- Group inputs into classes that should produce identical behavior
- One test per equivalence class (valid + invalid partitions)
- Example: age validation → {negative, 0, 1-17, 18-120, 121+}

**Boundary Value Analysis:**
- Test at exact boundaries: min, min+1, max-1, max
- Test one step outside: min-1, max+1
- Example: 8-64 char password → test at 7, 8, 9, 63, 64, 65

**Decision Tables:**
- For multi-condition logic, enumerate input combinations
- Each row = one test case
- Example: discount eligibility (member? coupon? min-order?) → 8 combinations

### 2. Enhanced TDD Flow

1. **Analyze AC** → build test case matrix using techniques above
2. **Red** → generate test skeleton from `templates/<framework>.liquid` (AAA structure)
3. **Verify Red** → run test, confirm expected failure reason (not syntax error)
4. **Green** → write minimum implementation to pass
5. **Verify Green** → run all tests, confirm pass
6. **Refactor** → improve structure, run tests again

### 3. Framework Detection

Auto-detect from project files (see `tdd-rules.md § Framework Detection`). If ambiguous, ask. Generate from matching template in `templates/`.

### 4. Rhythm Verification

Run `scripts/tdd-rhythm-checker.sh` after each cycle to verify:
- Test file committed before or with implementation
- No implementation-only commits
- Red phase was not skipped (test existed before passing)

Run `scripts/test-coverage-delta.sh` to verify:
- Coverage increased or held steady after Green phase
- No coverage regression after Refactor phase

## Domain Patterns

Load `references/insurance-domain-patterns.md` for insurance-specific test patterns:
- Policy lifecycle (quote → bind → endorse → renew → cancel)
- Claims processing (FNOL → investigation → adjudication → payment)
- Premium calculation (rating factors, tiered pricing, minimum premium)
- Regulatory compliance (state-specific rules, filing requirements)

## Guardrails

- **Never skip Red phase.** Writing a test after implementation defeats TDD's design benefit.
- **No tests for exceptions** listed in `tdd-rules.md § Exceptions`.
- **Never contradict Superpowers TDD** core principles. QA adds, never overrides.
- **One assertion per test** (logical assertion — multiple `expect()` for one behavior is fine).
