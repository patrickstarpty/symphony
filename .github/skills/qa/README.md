# QA Skills — Pipeline Guide

16 skills covering the full quality lifecycle: pre-coding → during-coding → post-coding./

> **Domain:** All skills work across domains. Insurance-specific examples and schemas are provided as defaults. For other domains, supply your own schema references and apply the same techniques.

---

## Start Here — Which Path?

```
┌─────────────────────────────────────┐
│ Do you have an issue with AC to work on? │
└───────────────┬─────────────────────┘
                │
       ┌────────▼────────┐
       │ Yes → Path A    │  Full pipeline (new feature / bug fix)
       │ No  → Path B    │  Report-only (existing test suite audit)
       └─────────────────┘
```

---

## Path A — Full Pipeline (New Feature / Bug Fix)

```
Issue → parsing-requirements
          ↓
        test-driven-development  ← [start coding here]
          ↓ (during coding)
        [commit + push]
          ↓ (post-coding)
        ┌──────────────────────────────────┐
        │ Run 3 evaluators IN PARALLEL     │
        │  analyzing-coverage              │
        │  validating-acceptance-criteria  │
        │  classifying-test-failures       │
        └──────────────┬───────────────────┘
                       ↓
                 generating-qa-report
                       ↓
               PASS? → reviewing-code-quality → PR
               FAIL? → fix gaps → re-run evaluators
```

### When to invoke each skill

| Trigger | Skill to invoke |
|---------|----------------|
| Issue assigned, before any code | `parsing-requirements` |
| AC parsed, ready to write tests | `test-driven-development` |
| Tests written, implementation complete | `analyzing-coverage` + `validating-acceptance-criteria` + `classifying-test-failures` (run all three) |
| All three evaluators complete | `generating-qa-report` |
| QA report shows PASS | `reviewing-code-quality` |
| Risk-based coverage threshold needed | `scoring-risk` (invoke at issue start, before coding) |
| Test failures need root cause | `classifying-test-failures` → `healing-broken-tests` |
| Defect patterns need analysis | `analyzing-defects` |

---

## Path B — Report-Only (Existing Test Suite Audit)

```
Existing test suite
    ↓
  analyzing-coverage          ← check coverage gaps
  validating-acceptance-criteria  ← map tests to AC (if AC exist)
  classifying-test-failures   ← diagnose any failing tests
    ↓
  generating-qa-report        ← produce verdict
```

Use this path when: auditing a legacy codebase, reviewing test quality before a release, or onboarding a new project.

---

## Path C — Test Generation (No Existing Tests)

```
HTML / API schema / Mobile app
    ↓
  generating-test-data         ← create realistic fixtures first
    ↓
  generating-playwright-tests  (web)
  generating-api-tests         (REST / GraphQL)
  generating-mobile-tests      (iOS / Android)
  generating-perf-tests        (load / stress)
    ↓
  test-driven-development      ← apply TDD discipline to generated scaffolding
```

---

## Skill Map by Phase

### Pre-coding
| Skill | Purpose |
|-------|---------|
| `parsing-requirements` | Extract structured AC, detect ambiguity |
| `scoring-risk` | Calibrate coverage thresholds by risk level |

### During-coding
| Skill | Purpose |
|-------|---------|
| `test-driven-development` | EP / BVA / decision tables → failing tests → implementation |

### Post-coding — Evaluation
| Skill | Purpose |
|-------|---------|
| `analyzing-coverage` | Interpret coverage reports, flag untested risk areas |
| `validating-acceptance-criteria` | Map test evidence to AC: SATISFIED / PARTIAL / UNMET |
| `classifying-test-failures` | Classify failures: real-bug / flaky / env-issue |
| `generating-qa-report` | Aggregate 3-dimension verdict (Pass Rate + Coverage + Acceptance) |

### Post-coding — Generation
| Skill | Purpose |
|-------|---------|
| `generating-test-data` | Synthetic domain-realistic fixtures (PII-safe) |
| `generating-playwright-tests` | Web E2E (Page Object Model) |
| `generating-api-tests` | REST / GraphQL suites from schema |
| `generating-mobile-tests` | iOS (XCTest) / Android (Espresso) / cross-platform (Appium) |
| `generating-perf-tests` | Load / spike / soak scripts (K6, Locust, Gatling) |

### Post-coding — Analysis & Healing
| Skill | Purpose |
|-------|---------|
| `reviewing-code-quality` | Spec compliance + code quality: APPROVE / REQUEST_CHANGES / COMMENT |
| `selecting-regressions` | Minimal regression set from change impact |
| `healing-broken-tests` | Auto-repair locator / expected-value breakages (requires CI + Knowledge Base) |
| `analyzing-defects` | Root causes, hotspots, Knowledge Base proposals |

---

## Output Convention

All skills write their output to the `## Copilot Workpad` comment on the Linear issue under a `### QA: <skill-name>` heading:

```markdown
## Copilot Workpad

### QA: parsing-requirements
[structured AC JSON or summary]

### QA: test-case-matrix
[EP classes / boundaries / decision rows per AC]

### QA: coverage
verdict: PASS | lines: 87% | gaps: [...]

### QA: acceptance-criteria
verdict: PASS | satisfied: 4 | partial: 1 | unmet: 0

### QA: failures
verdict: PASS | real_bugs: 0 | flaky: 1 | env_issues: 0

### QA: report
OVERALL: PASS ✅  (or FAIL ❌ with gate breakdown)
```

---

## Rules & Standards

Global quality standards are in `rules/`. Skills reference them where relevant:

| File | Used by |
|------|---------|
| `rules/qa-standards.md` | All evaluation skills (coverage thresholds, AC traceability, test data rules) |
| `rules/tdd-rules.md` | `test-driven-development` (framework detection, exceptions) |
| `rules/review-guidelines.md` | `reviewing-code-quality` |
| `rules/security-standards.md` | `reviewing-code-quality`, `generating-api-tests` |
