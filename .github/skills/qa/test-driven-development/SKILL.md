---
name: test-driven-development
description: "Translates parsed acceptance criteria into a rigorous TDD cycle: derive test case matrix using equivalence partitioning, BVA, and decision tables, then enforce Red-Green-Refactor with framework-specific scaffolding. Use when acceptance criteria are available and need systematic translation into failing tests before any implementation code is written."
---

# test-driven-development

> **Domain scope:** `references/insurance-domain-patterns.md` covers insurance-specific patterns (policy, claims, premium). For other domains, apply the same techniques with your own domain knowledge.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.
```

Write code before the test? Delete it. Start over. No exceptions.
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Delete means delete

## Quick Reference

**Phase:** during-coding  
**Inputs:**
- `acceptance_criteria` (array, required) — structured AC from `parsing-requirements`
- `framework` (string, optional) — jest | pytest | playwright | junit (auto-detected if omitted)

**Outputs:**
- `test_cases` — generated test case matrix (write to workpad under `### QA: test-case-matrix`)
- `test_files` — written test files committed to branch
- `tdd_log` — Red/Green/Refactor cycle audit trail

**Depends on:** parsing-requirements  
**Script fallback:** if scripts unavailable, enforce Red/Green/Refactor manually using the cycle steps below — the scripts verify, they don't replace the discipline

**Load before starting:** `rules/tdd-rules.md` — framework detection, exceptions list, coverage requirements

## When to Use

After `parsing-requirements` produces structured AC and before writing any implementation code. Use when:
- AC need translation into a systematic test case matrix
- Framework-specific test scaffolding is required (Jest, pytest, Playwright, JUnit)
- Insurance/finance domain patterns apply (policy lifecycle, claims, premium calculation)

Do NOT invoke for: configuration-only changes, generated code (protobuf/OpenAPI), pure infrastructure work. Check `tdd-rules.md § Exceptions` for full list.

## Step 1 — Build Test Case Matrix from AC

For each acceptance criterion, generate tests using these three techniques:

**Equivalence Partitioning** — group inputs by behavior class, one test per class:
```
AC: "Premium must be ≥ $50/month"
Partitions: {< 50 → reject} {= 50 → accept} {> 50 → accept} {non-numeric → error}
```

**Boundary Value Analysis** — test at and just outside every boundary:
```
AC: "Password must be 8–64 characters"
Tests: 7 chars (fail), 8 chars (pass), 9 chars (pass), 63 chars (pass), 64 chars (pass), 65 chars (fail)
```

**Decision Tables** — enumerate input combinations for multi-condition logic:
```
AC: "Discount: member AND coupon AND order > $100"
member | coupon | >$100 | discount?
  Y    |   Y    |   Y   |   YES
  Y    |   Y    |   N   |   NO
  Y    |   N    |   Y   |   NO
  N    |   Y    |   Y   |   NO
  (... 8 total combinations)
```

Produce the full matrix before writing a single line of test code.

## Step 2 — Red Phase (Write Failing Test)

Detect framework from project files (see `tdd-rules.md § Framework Detection`). Generate from the matching template:
- **Jest** → `templates/jest.test.ts.liquid`
- **pytest** → `templates/pytest.py.liquid`
- **Playwright** → `templates/playwright.spec.ts.liquid`
- **JUnit** → `templates/junit.java.liquid`

Write one test from the matrix. Name it after the behavior: `test_<unit>_<scenario>_<expected>`.

**Good test:**
```typescript
test('rejects premium below minimum threshold', async () => {
  const result = await calculatePremium({ basePremium: 45 });
  expect(result.error).toBe('Premium below minimum of $50/month');
});
```

**Bad test:**
```typescript
test('premium test', async () => {
  const mock = jest.fn().mockReturnValue({ error: 'err' });
  await mock({ basePremium: 45 });
  expect(mock).toHaveBeenCalled();  // tests the mock, not the code
});
```

Requirements: one behavior per test, clear name, real code (no mocks unless unavoidable).

## Step 3 — Verify Red (MANDATORY — Never Skip)

```bash
npm test path/to/test.test.ts   # or pytest path/to/test.py
```

Confirm:
- Test **fails** (not errors — a syntax error is not a failing test)
- Failure message is exactly what you expect
- Fails because the feature is missing, not because of a typo

**Test passes immediately?** You're testing existing behavior, not new behavior. Fix the test.  
**Test errors (not fails)?** Fix the error and re-run until it fails correctly.

Never proceed to Green until you have watched the test fail for the right reason.

## Step 4 — Green Phase (Minimal Implementation)

Write the simplest code that makes the test pass. Nothing more.

**Good:**
```typescript
function calculatePremium(input: { basePremium: number }) {
  if (input.basePremium < 50) {
    return { error: 'Premium below minimum of $50/month' };
  }
  return { premium: input.basePremium };
}
```

**Bad:** Adding configurable thresholds, logging, caching, or any feature the test doesn't require yet. YAGNI.

## Step 5 — Verify Green (MANDATORY)

```bash
npm test   # run full suite, not just the new test
```

Confirm:
- New test passes
- All previously passing tests still pass
- No errors or warnings in output

**New test fails?** Fix implementation, not the test.  
**Other tests fail?** Fix the regression now before continuing.

## Step 6 — Refactor

After green only. Remove duplication, improve names, extract helpers. Tests must stay green throughout. Do not add behavior during refactor.

## Step 7 — Repeat

Take the next test case from the matrix. Return to Step 2. Continue until all matrix test cases are green.

## Step 8 — Rhythm Verification

After completing the matrix, run verification scripts:

```bash
# Confirms test file committed before or with implementation; no implementation-only commits
scripts/tdd-rhythm-checker.sh

# Confirms coverage increased or held steady; flags regression after Refactor
scripts/test-coverage-delta.sh
```

**Script unavailable?** Manually verify: (a) `git log --oneline` shows test commit before or alongside implementation commit, (b) coverage report shows no regression from baseline.

## Domain Patterns (Insurance)

Load `references/insurance-domain-patterns.md` for:
- Policy lifecycle: quote → bind → endorse → renew → cancel
- Claims processing: FNOL → investigation → adjudication → payment
- Premium calculation: rating factors, tiered pricing, minimum premium
- Regulatory compliance: state-specific rules, filing requirements

For non-insurance domains: apply Equivalence Partitioning, BVA, and Decision Tables to your domain's state machines and business rules using the same techniques above.

## Common Rationalizations — All Wrong

| Excuse | Why it's wrong |
|--------|---------------|
| "I'll write tests after to verify it works" | Tests written after pass immediately — you never see them fail. They test what you built, not what's required. |
| "Too simple to test" | Simple code breaks. A 30-second test prevents a 30-minute debug. |
| "Already manually tested all edge cases" | No record, can't re-run, misses cases under pressure. Automated is systematic. |
| "Deleting X hours of work is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. Rewrite with TDD: X more hours, high confidence. |
| "Need to explore first" | Fine — throw away exploration code. Start TDD from scratch. |
| "This is different because..." | It isn't. Delete code. Start over. |

## Output

Write the completed test case matrix to the `## Copilot Workpad` issue comment under:
```
### QA: test-case-matrix
- AC1: [n] test cases → [EP classes / boundaries / decision rows]
- AC2: ...
TDD cycle: [framework] | [n test files written] | rhythm check: PASS/FAIL
```

## Guardrails

- **NEVER write production code without a prior failing test.** No exceptions.
- **NEVER skip Verify Red (Step 3).** A test that was never seen failing proves nothing.
- **NEVER add behavior during Refactor.** Refactor = clean, not extend.
- **No tests for exceptions** listed in `tdd-rules.md § Exceptions` (generated code, pure config).
- **One logical assertion per test.** Multiple `expect()` for one behavior is fine; testing two behaviors in one test is not.

## Consumers

- `generating-playwright-tests` — receives TDD test strategy for E2E scaffolding
- `generating-api-tests` — receives contract test structure from AC matrix
- `generating-mobile-tests` — receives platform-specific test scenarios
- `generating-perf-tests` — receives endpoint coverage to inform load test scope

