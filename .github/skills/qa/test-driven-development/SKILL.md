---
name: test-driven-development
description: "Extends the base TDD skill with QA-specific test case matrix generation using equivalence partitioning, boundary analysis, and decision tables. Use when acceptance criteria are available from parsing-requirements and need translation into framework-specific scaffolding (Jest, pytest, Playwright, JUnit)."
---

# test-driven-development (QA Extension)

> **Loading:** This QA extension adds test-case matrix generation on top of the base TDD skill at `.github/skills/test-driven-development/`. If the base skill's test runner configuration, commit rules, or core Red/Green/Refactor steps conflict with this extension, the base skill's instructions take precedence. This extension adds domain patterns, matrix generation techniques, and framework templates only.

## Quick Reference

**Phase:** during-coding  
**Inputs:**
- `acceptance_criteria` (array, required) — from parsing-requirements
- `framework` (string, optional) — jest | pytest | playwright | junit (auto-detected if omitted)

**Outputs:**
- `test_cases` — generated test case matrix
- `test_files` — written test files
- `tdd_log` — Red/Green/Refactor cycle audit trail

**Depends on:** parsing-requirements  
**Extends:** `../test-driven-development/SKILL.md` (QA extension — adds net-new content only)

## When to Use

Invoke during any coding task after `parsing-requirements` has produced structured acceptance criteria. This extension supplements the Superpowers TDD skill — do not replace it. Use this skill when:
- AC have been parsed and need to be translated into a full test case matrix
- Insurance/finance domain test patterns are needed (equivalence partitions for policy/claim data)
- Framework-specific test scaffolding is required (Jest, pytest, Playwright, JUnit)

Do NOT invoke this skill for: configuration-only changes, generated code (protobuf/OpenAPI), pure infrastructure work.

## Instructions

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
2. **Red** → generate test skeleton from the matching template: `jest.test.ts.liquid` (Jest), `pytest.py.liquid` (pytest), `playwright.spec.ts.liquid` (Playwright), or `junit.java.liquid` (JUnit)
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
- **Never contradict base TDD skill** core principles. QA adds, never overrides.
- **One assertion per test** (logical assertion — multiple `expect()` for one behavior is fine).

## Consumers

- `generating-playwright-tests` — receives TDD-driven test strategy for E2E scaffolding
- `generating-api-tests` — receives contract test structure derived from AC matrix
- `generating-mobile-tests` — receives platform-specific test scenarios from AC matrix
- `generating-perf-tests` — receives endpoint coverage to inform load test scope
