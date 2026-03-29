# QA Verification Skills — Comprehensive Design

**Date:** 2026-03-28
**Author:** Patrick (QA CoE)
**Status:** Implemented (last updated 2026-03-29)

**Revisions:**
- 2026-03-28 — Initial draft
- 2026-03-29 — Post-implementation updates: TDD strategy, frontmatter standard, pipeline guide, quality review fixes
**JIRA:** Create QA verification skills for AI-assisted delivery readiness
**Parent spec:** [QA Ecosystem Design](2026-03-27-qa-skills-plugins-hooks-design.md)
**Upstream:** [Orchestrator](2026-03-26-ai-native-sdlc-orchestrator-design.md), [QA Agent](2026-03-25-qa-agent-system-design.md)

---

## 1. Objective

Implementation-ready SKILL.md specifications for all 16 QA verification skills (P1→P2→P3), plus rules and evals. Implementation plan sequences P1 as quick win; design covers everything.

**Delivers:** 16 SKILL.md specs, 2+ rules files, eval test cases per skill, script/reference/template inventories.

**Scope:** Central-team quality patterns (how to evaluate/generate/enforce), not project-level configuration (what thresholds/frameworks to use). Project config flows through WORKFLOW.md and hook profiles.

**Success criteria:** All skills follow `name`+`description`-only frontmatter (Anthropic standard), gerund naming, ## When to Use / ## Instructions / ## Guardrails / ## Consumers / ## Output sections, eval coverage, workpad output destinations. See `README.md` in `.github/skills/qa/` for pipeline navigation.

> **Frontmatter note:** The YAML blocks in §4–§6 of this spec include extended fields (version, category, phase, input_schema, output_schema) for documentation purposes only. The actual SKILL.md files follow the Anthropic standard: only `name` (max 64 chars) and `description` (max 1024 chars) are valid frontmatter fields. All schema/dependency metadata lives in `## Quick Reference` body sections.

## 2. Skill Catalog

| # | Skill | Cat | Phase | P |
|---|-------|-----|-------|---|
| 1 | `parsing-requirements` | analysis | pre | 1 |
| 2 | `test-driven-development` | enforcement | during | 1 |
| 3 | `analyzing-coverage` | evaluation | post | 1 |
| 4 | `validating-acceptance-criteria` | evaluation | post | 1 |
| 5 | `classifying-test-failures` | evaluation | post | 1 |
| 6 | `generating-qa-report` | evaluation | post | 1 |
| 7 | `generating-test-data` | generation | during | 2 |
| 8 | `generating-playwright-tests` | generation | post | 2 |
| 9 | `generating-api-tests` | generation | post | 2 |
| 10 | `generating-mobile-tests` | generation | post | 2 |
| 11 | `generating-perf-tests` | generation | post | 2 |
| 12 | `scoring-risk` | analysis | pre | 3 |
| 13 | `reviewing-code-quality` | evaluation | post | 3 |
| 14 | `selecting-regressions` | execution | post | 3 |
| 15 | `healing-broken-tests` | execution | post | 3 |
| 16 | `analyzing-defects` | analysis | post | 3 |

> **Delivery column (P):** Internal implementation order only. Users see skills as a unified QA suite — the P labels do NOT appear in skill descriptions or instructions. Skills can be invoked independently of delivery phase.

### Dependency Graph

```
scoring-risk (P3) ──▶ dynamic thresholds ──────────────────────────────┐
                                                                       │
parsing-requirements ──▶ test-driven-development ──▶ generating-* (P2) │
       │                       │                          │            │
       │                       ▼                          ▼            ▼
       │              generating-test-data (P2)   selecting-regressions (P3)
       │
       ▼                    ┌── analyzing-coverage ──┐
validating-acceptance ◀─────┤                        ├──▶ generating-qa-report
  -criteria                 └── classifying-test     │         │
       │                          -failures ─────────┘         │
       └───────────────────────────────────────────────────────┘
                                                               │
                     ┌─────────────────────────────────────────┘
                     ▼                                    ▼
         reviewing-code-quality (P3)     healing-broken-tests (P3)
                                                   │
                                                   ▼
                                         analyzing-defects (P3)
                                                   │
                                                   ▼
                                             Knowledge Base
```

**Edge legend:** solid arrows = hard dependency (skill requires upstream output). Dotted lines in the table below indicate soft dependencies (enriches output when available, works without).

| From | To | Type | What flows |
|------|----|------|------------|
| parsing-requirements | test-driven-development | hard | AC list, testability annotations |
| parsing-requirements | validating-acceptance-criteria | hard | Structured AC for evidence mapping |
| test-driven-development | generating-test-data | soft | Test strategy context, schema hints |
| test-driven-development | generating-playwright-tests | hard | Test plan, component list |
| test-driven-development | generating-api-tests | hard | Test plan, endpoint inventory |
| test-driven-development | generating-mobile-tests | hard | Test plan, screen inventory |
| test-driven-development | generating-perf-tests | soft | Endpoint list, SLA context |
| analyzing-coverage | validating-acceptance-criteria | soft | Coverage gaps enrich AC scoring |
| analyzing-coverage | generating-qa-report | hard | Coverage dimension scores |
| classifying-test-failures | generating-qa-report | hard | Pass Rate dimension scores |
| validating-acceptance-criteria | generating-qa-report | hard | Acceptance dimension scores |
| scoring-risk | selecting-regressions | hard | Risk scores for test prioritization |
| scoring-risk | analyzing-coverage | soft | Dynamic thresholds (P3 enhancement) |
| generating-\* | selecting-regressions | soft | New test IDs expand selection pool |
| generating-qa-report | reviewing-code-quality | hard | QA verdict + dimension data |
| generating-qa-report | healing-broken-tests | soft | Prioritizes which failures to heal |
| classifying-test-failures | healing-broken-tests | hard | Failure classification + logs |
| healing-broken-tests | analyzing-defects | hard | Healed vs unhealed pattern data |
| classifying-test-failures | analyzing-defects | hard | Raw failure taxonomy |
| generating-qa-report | analyzing-defects | hard | Aggregate quality trends |

### Workflow Narrative

**Pre-coding → `parsing-requirements`** extracts structured acceptance criteria from the JIRA/Linear ticket. This is the pipeline entry point — nothing runs without parsed ACs.

**During-coding → `test-driven-development`** enforces Red-Green-Refactor rhythm. It consumes the AC list to ensure tests map to requirements. When available, `generating-test-data` (P2) provides domain-realistic fixtures.

**Post-coding (evaluation) → three parallel evaluations run independently:**
- `analyzing-coverage` interprets coverage reports and assesses risk per gap
- `classifying-test-failures` retries failures and classifies root causes
- `validating-acceptance-criteria` maps ACs to test evidence (optionally enriched by coverage data)

**Post-coding (report) → `generating-qa-report`** aggregates all three evaluation dimensions (Pass Rate, Coverage, Acceptance) into a single QA verdict. This is the quality gate decision point.

**Post-coding (generation, P2) →** the `generating-*` skills (Playwright, API, mobile, perf) produce platform-specific tests using the test strategy from TDD. These run in parallel per platform.

**Post-coding (optimization, P3) →** two branches fork from the QA report:
- `reviewing-code-quality` feeds the Code Reviewer agent (cross-model objectivity)
- `healing-broken-tests` auto-repairs tests broken by intentional changes, feeding `analyzing-defects` which writes patterns to the Knowledge Base

**Pre-coding (P3) → `scoring-risk`** runs before coding to produce dynamic thresholds that tighten coverage requirements for critical components and feed `selecting-regressions` with risk-weighted prioritization.

## 3. File Structure

```
.github/skills/qa/
├── parsing-requirements/         # P1 ─────────────────────────
│   ├── SKILL.md
│   ├── scripts/{extract-ac.py, ambiguity-detector.py}
│   ├── references/ambiguity-signals.md
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── test-driven-development/      # P1 — QA standalone TDD (§3.1)
│   ├── SKILL.md
│   ├── scripts/{tdd-rhythm-checker.sh, test-coverage-delta.sh}
│   ├── references/{test-design-techniques.md, insurance-domain-patterns.md, testing-anti-patterns.md}
│   ├── templates/{jest.test.ts, pytest.py, playwright.spec.ts, junit.java}.liquid
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── analyzing-coverage/           # P1
│   ├── SKILL.md
│   ├── scripts/{coverage-report.py, coverage-gap-analyzer.py}
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── validating-acceptance-criteria/ # P1
│   ├── SKILL.md
│   ├── scripts/ac-evidence-mapper.py
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── classifying-test-failures/    # P1
│   ├── SKILL.md
│   ├── scripts/{retry-failures.sh, classify-failure.py}
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── generating-qa-report/         # P1
│   ├── SKILL.md
│   ├── templates/qa-report.md.liquid
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── generating-test-data/         # P2 ─────────────────────────
│   ├── SKILL.md
│   ├── scripts/{data-generator.py, pii-sanitizer.py, distribution-validator.py}
│   ├── references/{insurance-data-schemas.md, pii-patterns.md}
│   ├── templates/{fixture.json, factory.ts, factory.py}.liquid
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── generating-playwright-tests/  # P2
│   ├── SKILL.md
│   ├── scripts/{selector-strategy.py, page-analyzer.py}
│   ├── references/{playwright-patterns.md, pom-conventions.md, web-testing-standards.md}
│   ├── templates/{page-object.ts, spec.ts, fixture.ts}.liquid
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── generating-api-tests/         # P2
│   ├── SKILL.md
│   ├── scripts/{schema-parser.py, endpoint-analyzer.py}
│   ├── references/{api-testing-patterns.md, schema-validation-rules.md}
│   ├── templates/{rest.test.ts, graphql.test.ts, pytest-api.py}.liquid
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── generating-mobile-tests/      # P2
│   ├── SKILL.md
│   ├── scripts/{platform-detector.py, accessibility-checker.py}
│   ├── references/{appium-patterns.md, xctest-patterns.md, uiautomator-patterns.md}
│   ├── templates/{appium.test.ts, xctest.swift, espresso.kt}.liquid
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── generating-perf-tests/        # P2
│   ├── SKILL.md
│   ├── scripts/{load-profile-calculator.py, baseline-collector.py}
│   ├── references/{perf-testing-patterns.md, insurance-load-profiles.md}
│   ├── templates/{k6.test.js, locust.py, gatling.scala}.liquid
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── scoring-risk/                 # P3 ─────────────────────────
│   ├── SKILL.md
│   ├── scripts/{change-scope-analyzer.py, component-criticality.py, defect-density-calculator.py}
│   ├── references/{risk-scoring-model.md, component-registry.md}
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── reviewing-code-quality/       # P3
│   ├── SKILL.md
│   ├── scripts/{spec-compliance-checker.py, quality-metrics.py}
│   ├── references/{review-checklist.md, code-quality-standards.md}
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── selecting-regressions/        # P3
│   ├── SKILL.md
│   ├── scripts/{change-impact-analyzer.py, dependency-graph-walker.py, test-selector.py}
│   ├── references/regression-strategies.md
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── healing-broken-tests/         # P3
│   ├── SKILL.md
│   ├── scripts/{failure-pattern-matcher.py, locator-updater.py, diff-correlator.py}
│   ├── references/{common-breakage-patterns.md, auto-fix-strategies.md}
│   └── evals/{test-prompts.yaml, assertions.yaml}
├── analyzing-defects/            # P3
│   ├── SKILL.md
│   ├── scripts/{root-cause-classifier.py, pattern-detector.py, knowledge-base-writer.py}
│   ├── references/{defect-taxonomy.md, root-cause-categories.md}
│   └── evals/{test-prompts.yaml, assertions.yaml}
└── rules/
    ├── qa-standards.md           # P1
    ├── tdd-rules.md              # P1
    ├── security-standards.md     # P2
    ├── review-guidelines.md      # P3
    ├── platform/{typescript,python,java,go}.md  # P2
    └── README.md                 # Pipeline navigation guide (Path A / B / C)
```

Note: A `.github/skills/qa/.gitignore` file is also present in the directory.

### 3.1 QA TDD Strategy

The QA `test-driven-development` skill at `.github/skills/qa/test-driven-development/` is a **standalone skill** — it is NOT an extension of the Superpowers TDD skill at `.github/skills/test-driven-development/`. It incorporates the full TDD discipline (Iron Law, Red-Green-Refactor, mandatory Verify Red) directly, and adds the QA-specific layer on top.

**Why standalone (not extension):**
- An extension that says "Superpowers wins on conflict" creates ambiguous precedence and requires agents to load two skills simultaneously
- The QA TDD skill needs to be self-contained and fully operable without knowledge of which other skills are loaded
- The combined skill is more robust: Iron Law + test case matrix generation + domain patterns in one place

**What QA TDD owns exclusively (not in Superpowers):**

| Capability | Detail |
|------------|--------|
| Iron Law | `NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST` — identical philosophy, now in this skill |
| Test case matrix | Equivalence partitioning, BVA, decision tables derived from structured AC |
| Domain patterns | `references/insurance-domain-patterns.md` — policy lifecycle, claims, premium calc; other domains: apply same techniques with own domain knowledge |
| Framework templates | `jest.test.ts.liquid`, `pytest.py.liquid`, `playwright.spec.ts.liquid`, `junit.java.liquid` |
| Rhythm verification | `scripts/tdd-rhythm-checker.sh`, `scripts/test-coverage-delta.sh` |
| Anti-rationalization | 6 common excuses + why each is wrong (inline in SKILL.md) |
| Workpad output | Test case matrix written to `## Copilot Workpad` / `### QA: test-case-matrix` |
| Script fallback | Manual verification steps when scripts unavailable |

**Interaction with Superpowers TDD:** When both are loaded in the same session, they are complementary. Superpowers covers discipline enforcement at a deep level (red flags checklist, debugging integration). QA TDD covers the systematic AC-to-test derivation pipeline. No precedence conflict because they address different concerns.

---

## 4. P1 Skills — Core Evaluation

### 4.1 parsing-requirements

```yaml
---
name: parsing-requirements
version: "1.0.0"
description: "Parse issue description into structured AC, detect ambiguities, flag missing information"
category: analysis
phase: pre-coding
platforms: ["all"]
dependencies: []
input_schema:
  - name: "issue_description"
    type: "string"
    required: true
  - name: "issue_metadata"
    type: "object"
    required: false
output_schema:
  - name: "acceptance_criteria"
    type: "array"
  - name: "ambiguities"
    type: "array"
  - name: "missing"
    type: "array"
---
```

**Skill justification:** Requires LLM judgment to detect semantic ambiguity and assess testability — a regex can extract bullet points but cannot determine "should handle edge cases appropriately" is untestable.

**Instructions:**
1. Extract observable behavior statements from issue description
2. Assess testability per statement
3. Run `scripts/ambiguity-detector.py` — flags vague verbs ("appropriate", "properly"), missing thresholds ("large number"), undefined terms ("etc.") (fallback: scan manually for vague verbs in references/ambiguity-signals.md)
4. Run `scripts/extract-ac.py` — regex + heuristic AC extraction from Markdown/JIRA format (fallback: parse AC manually — look for Given/When/Then, bullet lists, or numbered criteria)
5. Output JSON: `acceptance_criteria[]`, `ambiguities[]`, `missing[]`

**Scripts:**
| Script | Purpose |
|--------|---------|
| `extract-ac.py` | Regex + heuristic AC extraction from Markdown/JIRA/Given-When-Then formats → JSON array |
| `ambiguity-detector.py` | Pattern matching for vague verbs, missing thresholds, undefined terms, implicit assumptions |

**Output example:**
```json
{
  "acceptance_criteria": [
    {"id": "AC-1", "text": "Password must be 8-64 characters", "testable": true},
    {"id": "AC-2", "text": "Should handle edge cases appropriately", "testable": false, "ambiguity": "vague: 'appropriately' undefined"}
  ],
  "ambiguities": ["AC-2: 'appropriately' needs concrete definition"],
  "missing": ["No error message specification", "No rate limiting mentioned"]
}
```

**Guardrails:** Never invent requirements. Flag ambiguity, don't resolve it. Zero extractable ACs → output `missing` rather than fabricating.

**Consumers:** test-driven-development, validating-acceptance-criteria, scoring-risk (P3).

**Output:** Write to workpad under `### QA: parsing-requirements` — AC count, ambiguities list, missing items.

### 4.2 test-driven-development (Standalone QA TDD)

```yaml
---
name: test-driven-development
description: "Translates parsed acceptance criteria into a rigorous TDD cycle: derive test case matrix using equivalence partitioning, BVA, and decision tables, then enforce Red-Green-Refactor with framework-specific scaffolding. Use when acceptance criteria are available and need systematic translation into failing tests before any implementation code is written."
# Spec-only fields (not in actual SKILL.md):
# version: "2.0.0"
# category: enforcement  
# phase: during-coding
# dependencies: [parsing-requirements]
# input: acceptance_criteria (array, required), framework (string, optional: jest|pytest|playwright|junit)
# output: test_cases (matrix), test_files (written), tdd_log (RGR audit trail)
---
```

**Architecture change from original spec:** Redesigned from extension → standalone. Incorporates Superpowers TDD Iron Law and RGR discipline directly. See §3.1 for rationale.

**Core structure:**
1. **Iron Law** — NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
2. **Step 1** — Build test case matrix from AC (EP, BVA, Decision Tables with worked examples)
3. **Steps 2–7** — Red → Verify Red (mandatory) → Green → Verify Green → Refactor → Repeat
4. **Step 8** — Rhythm verification scripts
5. **Domain Patterns** — Insurance domain + non-insurance fallback guidance
6. **Anti-rationalization table** — 6 common excuses + rebuttals

**QA additions vs base TDD discipline:**

| Added by QA TDD | Detail |
|-----------------|--------|
| Test case matrix | EP, BVA, decision tables derived from structured AC — systematic, not ad hoc |
| Worked examples | Insurance-domain examples (premium threshold, password policy) for each technique |
| Framework templates | `jest.test.ts.liquid`, `pytest.py.liquid`, `playwright.spec.ts.liquid`, `junit.java.liquid` |
| Rhythm scripts | `tdd-rhythm-checker.sh` (git ordering), `test-coverage-delta.sh` (coverage delta) |
| Script fallback | Manual verification steps when scripts unavailable |
| Workpad output | Test case matrix → `### QA: test-case-matrix` in issue workpad |

**Rules reference:** Load `rules/tdd-rules.md` before starting — framework detection, exceptions list.

**Guardrails:** NEVER write production code without prior failing test. NEVER skip Verify Red. NEVER add behavior during Refactor. No tests for exceptions in tdd-rules.md § Exceptions.

**Consumers:** generating-playwright-tests, generating-api-tests, generating-mobile-tests, generating-perf-tests.

### 4.3 analyzing-coverage

```yaml
---
name: analyzing-coverage
version: "1.0.0"
description: "Interpret coverage gaps, assess risk, suggest which untested paths matter most"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: []
soft_dependencies: ["scoring-risk"]
input_schema:
  - name: "coverage_data"
    type: "object"
    required: true
  - name: "threshold"
    type: "number"
    required: false
    description: "Default: 80"
  - name: "component_criticality"
    type: "string"
    required: false
    description: "critical | high | medium | low"
output_schema:
  - name: "summary"
    type: "object"
    description: "Lines, branches, functions percentages"
  - name: "verdict"
    type: "string"
  - name: "gaps"
    type: "array"
    description: "Uncovered paths with risk and suggestions"
---
```

**Skill justification:** The `coverage-delta-check` hook runs coverage and checks a number. This skill *interprets* — 75% on a payment module is more concerning than 75% on a utility helper.

**Instructions:**
0. Generate coverage report if absent: `npm test --coverage` (Jest/Vitest), `pytest --cov=src` (Python), `mvn test jacoco:report` (Java), `go test ./... -coverprofile=coverage.out` (Go). Output empty → verdict 'unavailable', stop.
1. Parse coverage data (Istanbul/JaCoCo/coverage.py/lcov → standardized JSON)
2. Compare line/branch/function against threshold
3. Per uncovered file: assess risk (error handling? security-sensitive? user-facing?)
4. Run `scripts/coverage-gap-analyzer.py` for specific untested paths
5. Suggest concrete test cases for high-risk gaps
6. Output verdict, summary, gap analysis with risk scores

**Scripts:** `coverage-report.py` (parse multi-tool output → standard JSON), `coverage-gap-analyzer.py` (identify gaps, categorize by risk).

**Rules reference:** Load `rules/qa-standards.md` — default thresholds, mandatory error path coverage.

**Guardrails:** Don't inflate coverage with trivial tests. Coverage is a signal, not a goal. No data → clear "unavailable" verdict, not silent failure.

When scoring-risk output is available, use its recommended_thresholds instead of the default 80%. Without it, apply defaults from rules/qa-standards.md.

**Output:** Write to workpad under `### QA: coverage` — verdict, percentages, threshold used, top gaps.

### 4.4 validating-acceptance-criteria

```yaml
---
name: validating-acceptance-criteria
version: "1.0.0"
description: "Map AC to test evidence, score SATISFIED/PARTIAL/UNMET per criterion"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: ["parsing-requirements"]
soft_dependencies: ["analyzing-coverage"]
input_schema:
  - name: "acceptance_criteria"
    type: "array"
    required: true
  - name: "test_results"
    type: "object"
    required: true
  - name: "git_diff"
    type: "string"
    required: true
output_schema:
  - name: "criteria"
    type: "array"
    description: "Per-AC status + evidence"
  - name: "satisfied"
    type: "number"
  - name: "partial"
    type: "number"
  - name: "unmet"
    type: "number"
  - name: "verdict"
    type: "string"
---
```

**Skill justification:** No deterministic command can assess whether code semantically satisfies natural-language AC. Pure LLM judgment.

**Instructions:**
1. Per AC: search test names/descriptions for semantic alignment, search diff for implementing logic, run `scripts/ac-evidence-mapper.py` for keyword matching
2. Score: **SATISFIED** (test exists + passes), **PARTIAL** (code exists but no test, or test skipped/failing), **UNMET** (no evidence)
3. Any PARTIAL/UNMET → FAIL verdict
4. Output evidence map for reviewer traceability

**Scripts:** `ac-evidence-mapper.py` — keyword extraction from AC, fuzzy match against test names and code identifiers.

**Rules reference:** Load `rules/qa-standards.md` — AC traceability requirements.

**Guardrails:** Keyword match ≠ coverage — read test body. PARTIAL is not a soft pass. Never SATISFIED on code-only evidence without tests.

**Output:** Write to workpad under `### QA: acceptance-criteria` — verdict, satisfied/partial/unmet counts, per-AC evidence.

### 4.5 classifying-test-failures

```yaml
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
```

**Skill justification:** Retry logic is deterministic, but *classification* (real assertion failure vs timing-dependent flaky vs connection timeout) requires judgment.

**Instructions:**
1. Run `scripts/retry-failures.sh` per failed test (up to retry_count)
2. Classify: **real-bug** (consistent assertion error, same trace), **flaky** (passes on retry or different errors), **env-issue** (ECONNREFUSED, ETIMEDOUT, OOM, port conflict)
3. Run `scripts/classify-failure.py` for pattern-based error matching
4. Only real-bugs count toward FAIL; flaky reported but don't block; env-issues reported with remediation

**Scripts:** `retry-failures.sh` (re-run failed tests with framework-specific filter flags), `classify-failure.py` (error pattern matching: connection errors → env, assertion errors → real-bug).

**Guardrails:** Max 2 retries in P1. Passing on retry = flaky, not fixed. Identical assertion across all retries = real bug, not timing.

**Future enhancement (not yet available):** Historical pass rate analysis via Knowledge Base replaces simple retry heuristics.

**Rules reference:** Load `rules/qa-standards.md` — test independence requirements.

**Output:** Write to workpad under `### QA: failures` — verdict, real_bugs/flaky/env_issues counts, per-failure classification.

### 4.6 generating-qa-report

```yaml
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
```

**Instructions:**
1. Collect outputs from the three evaluation skills
2. Apply gate policy: **strict** = all dimensions must PASS; **advisory** = report only, no block
3. Generate markdown from `templates/qa-report.md.liquid`: verdict, dimension table (Pass Rate/Coverage/Acceptance), test summary, coverage gaps, AC traceability matrix
4. Output markdown + structured verdict for programmatic consumption

**Report template:**
```markdown
## QA Evaluation Report
**Issue:** PAY-123  |  **Evaluator:** QA Agent (Gemini 3 Pro)  |  **Verdict: PASS ✓**

| Dimension | Score | Threshold | Status |
|-----------|-------|-----------|--------|
| Pass Rate | 100% (42/42) | 100% | ✓ |
| Coverage | 85% lines | 80% | ✓ |
| Acceptance | 4/4 AC | 100% | ✓ |
```

**Guardrails:** Reproducible given same inputs. Never omit a failing dimension. Advisory mode still states what would fail under strict.

**Output:** Write to workpad under `### QA: report` — OVERALL verdict, dimension table, gate mode. On FAIL: list which dimension(s) failed and required action.

---

## 5. P2 Skills — Generation & Platform Expansion

### 5.1 generating-test-data

```yaml
---
name: generating-test-data
version: "1.0.0"
description: "Generate synthetic test data with domain awareness, realistic distribution, zero PII"
category: generation
phase: during-coding
platforms: ["all"]
dependencies: []
soft_dependencies: ["test-driven-development"]
input_schema:
  - name: "schema"
    type: "object"
    required: true
    description: "JSON Schema, TS interface, DB schema, or OpenAPI schema"
  - name: "count"
    type: "number"
    required: false
  - name: "domain"
    type: "string"
    required: false
    description: "insurance (default, schemas in references/) | any domain with own schema reference"
  - name: "distribution"
    type: "string"
    required: false
    description: "balanced | edge-heavy | happy-path | realistic"
  - name: "format"
    type: "string"
    required: false
    description: "json | csv | sql-insert | factory-function"
output_schema:
  - name: "data"
    type: "array"
  - name: "factory_code"
    type: "string"
  - name: "validation_report"
    type: "object"
    description: "PII scan + distribution analysis"
---
```

**Skill justification:** A script generates random data. This skill generates *domain-realistic* data — claim amounts follow typical distributions, policy dates respect business rules, edge cases target known failure modes.

**Instructions:**
1. Parse schema (JSON Schema, TS interface, DB DDL, OpenAPI)
2. Load `references/insurance-data-schemas.md` if domain specified
3. Run `scripts/pii-sanitizer.py` — verify no real PII patterns in seed data
4. Generate per distribution profile (balanced/edge-heavy/happy-path/realistic)
5. Run `scripts/distribution-validator.py` — verify generated data matches profile
6. Optionally generate factory functions from templates
7. Final PII scan on all output

**Scripts:** `data-generator.py` (schema → JSON), `pii-sanitizer.py` (SSN/phone/email/CC pattern detection), `distribution-validator.py` (histogram analysis, boundary value presence, null ratio).

**References:** `insurance-data-schemas.md` (policy, claim, customer schemas), `pii-patterns.md` (PII regex patterns).

**Templates:** `fixture.json.liquid`, `factory.ts.liquid` (faker patterns), `factory.py.liquid` (factory_boy patterns).

**Guardrails:** Never use real customer data. PII scan mandatory. Obviously fake PII ("Jane Doe", "555-0100"). Insurance policy numbers must not match real formats.

**Domain scope:** `references/insurance-data-schemas.md` covers insurance entities. For other domains (financial, healthcare, retail), provide a custom schema reference file in `references/` and pass the domain name — the generation technique is domain-agnostic.

### 5.2 generating-playwright-tests

```yaml
---
name: generating-playwright-tests
version: "1.0.0"
description: "Generate Playwright E2E scripts with Page Object Model, robust selectors, accessibility assertions"
category: generation
phase: post-coding
platforms: ["playwright"]
dependencies: ["test-driven-development"]
input_schema:
  - name: "test_cases"
    type: "array"
    required: true
  - name: "app_url"
    type: "string"
    required: true
  - name: "existing_page_objects"
    type: "array"
    required: false
  - name: "auth_strategy"
    type: "string"
    required: false
    description: "storageState | login-fixture | none"
output_schema:
  - name: "spec_files"
    type: "array"
  - name: "page_objects"
    type: "array"
  - name: "fixtures"
    type: "array"
---
```

**Instructions:**
1. Filter test case matrix for E2E-appropriate cases (user workflows, not unit logic)
2. Analyze existing Page Objects for reuse
3. Run `scripts/page-analyzer.py` — extract page structure, forms, interactive elements
4. Run `scripts/selector-strategy.py` — recommend selectors: data-testid > role > text > CSS
5. Generate Page Objects, spec files, and auth fixtures from templates

**Scripts:** `selector-strategy.py` (selector recommendation, fragile selector flagging), `page-analyzer.py` (HTML structure extraction → page map).

**References:** `playwright-patterns.md`, `pom-conventions.md`, `web-testing-standards.md`.

**Guardrails:** No styling-based selectors (.btn-primary). Flag pages lacking data-testid. No hardcoded credentials. Every test needs a meaningful assertion. Must run with `npx playwright test` out of the box.

### 5.3 generating-api-tests

```yaml
---
name: generating-api-tests
version: "1.0.0"
description: "Generate API tests (REST/GraphQL) with schema validation, edge cases, contract testing"
category: generation
phase: post-coding
platforms: ["rest", "graphql"]
dependencies: ["test-driven-development"]
input_schema:
  - name: "api_spec"
    type: "object"
    required: true
    description: "OpenAPI/Swagger or GraphQL schema"
  - name: "test_cases"
    type: "array"
    required: false
  - name: "base_url"
    type: "string"
    required: true
  - name: "auth_config"
    type: "object"
    required: false
output_schema:
  - name: "test_files"
    type: "array"
  - name: "contract_tests"
    type: "array"
  - name: "edge_case_tests"
    type: "array"
---
```

**Instructions:**
1. Parse API spec (OpenAPI 3.x, Swagger 2.0, GraphQL introspection)
2. Run `scripts/schema-parser.py` → endpoints, schemas, status codes
3. Run `scripts/endpoint-analyzer.py` → classify by risk (auth=high, payment=critical, CRUD=medium)
4. Per endpoint: generate happy path (2xx + schema validation), error tests (400/401/404), edge cases (empty arrays, max-length, injection payloads), contract tests (strict schema matching)
5. GraphQL: query depth tests, fragment spreads, mutation idempotency

**Scripts:** `schema-parser.py` (OpenAPI/Swagger/GraphQL SDL → endpoint catalog), `endpoint-analyzer.py` (risk classification by endpoint type).

**References:** `api-testing-patterns.md`, `schema-validation-rules.md`.

**Templates:** `rest.test.ts.liquid`, `graphql.test.ts.liquid`, `pytest-api.py.liquid`.

**Guardrails:** No hardcoded auth tokens. Verify base_url is not production. Strict schema validation by default. Rate limit tests excluded from CI fast-path.

### 5.4 generating-mobile-tests

```yaml
---
name: generating-mobile-tests
version: "1.0.0"
description: "Generate mobile tests for iOS (XCTest) and Android (Espresso) with cross-platform support"
category: generation
phase: post-coding
platforms: ["appium", "xctest", "espresso"]
dependencies: ["test-driven-development"]
input_schema:
  - name: "test_cases"
    type: "array"
    required: true
  - name: "platform"
    type: "string"
    required: true
    description: "ios | android | cross-platform"
  - name: "framework"
    type: "string"
    required: false
    description: "appium | xctest | espresso. Auto-detected."
  - name: "device_config"
    type: "object"
    required: false
output_schema:
  - name: "test_files"
    type: "array"
  - name: "page_objects"
    type: "array"
  - name: "device_matrix"
    type: "array"
---
```

**Instructions:**
1. Run `scripts/platform-detector.py` — detect from project files (Podfile → iOS, build.gradle → Android)
2. Select selector strategy per platform: iOS (accessibility ID > label > predicate), Android (resource-id > content-description > UiSelector), Appium (accessibility id > XPath last resort)
3. Generate screen objects and test files from platform templates
4. Run `scripts/accessibility-checker.py` — verify VoiceOver labels, touch targets ≥ 44pt
5. Generate device matrix recommendation

**Scripts:** `platform-detector.py`, `accessibility-checker.py`.

**References:** `appium-patterns.md`, `xctest-patterns.md`, `uiautomator-patterns.md`.

**Templates:** `appium.test.ts.liquid`, `xctest.swift.liquid`, `espresso.kt.liquid`.

**Guardrails:** No XPath unless no alternative. Include rotation tests for form screens. Test with accessibility enabled. No hardcoded coordinates.

### 5.5 generating-perf-tests

```yaml
---
name: generating-perf-tests
version: "1.0.0"
description: "Generate performance tests (K6/Locust/Gatling) with realistic load profiles and SLA thresholds"
category: generation
phase: post-coding
platforms: ["k6", "locust", "gatling"]
dependencies: []
soft_dependencies: ["test-driven-development"]
input_schema:
  - name: "target_endpoints"
    type: "array"
    required: true
  - name: "load_profile"
    type: "object"
    required: true
    description: "Ramp-up, steady-state VUs, duration, think time"
  - name: "sla_thresholds"
    type: "object"
    required: false
    description: "p95 latency, error rate, throughput"
  - name: "framework"
    type: "string"
    required: false
    description: "k6 | locust | gatling. Default: k6."
  - name: "domain"
    type: "string"
    required: false
output_schema:
  - name: "test_files"
    type: "array"
  - name: "load_profile_visualization"
    type: "string"
  - name: "baseline_config"
    type: "object"
---
```

**Skill justification:** A script generates boilerplate load tests. This skill designs *realistic load profiles* — understanding that users browse 5 pages per form submission, login happens once per session, peak occurs during open enrollment.

**Instructions:**
1. Classify endpoints by load pattern (read-heavy, write-heavy, mixed)
2. Run `scripts/load-profile-calculator.py` → framework-specific stage definitions
3. Load `references/insurance-load-profiles.md` for domain-specific traffic patterns
4. Generate scripts with realistic think times, session management, data parameterization, SLA assertions
5. Run `scripts/baseline-collector.py` → baseline measurement config

**Scripts:** `load-profile-calculator.py` (human-readable profile → K6 stages/Locust steps/Gatling injection), `baseline-collector.py` (single-user latency, cold-start, resource utilization config).

**References:** `perf-testing-patterns.md`, `insurance-load-profiles.md` (open enrollment 10x surge, post-disaster claims spike, renewal batch, daily quote patterns).

**Templates:** `k6.test.js.liquid`, `locust.py.liquid`, `gatling.scala.liquid`.

**Guardrails:** Never target production without explicit confirmation. Always include think times. Define SLA thresholds *before* running. Synthetic data only.

**Domain scope:** `insurance-load-profiles.md` provides insurance-specific load patterns (open enrollment surge, post-disaster claims spike). For other domains, define load profiles via the `load_profile` and `target_sla` inputs — the insurance reference is a default, not a requirement.

---

## 6. P3 Skills — Advanced & Self-Improving

### 6.1 scoring-risk

```yaml
---
name: scoring-risk
version: "1.0.0"
description: "Score issue risk from change scope, component criticality, defect history — feed dynamic thresholds"
category: analysis
phase: pre-coding
platforms: ["all"]
dependencies: []
input_schema:
  - name: "git_diff"
    type: "string"
    required: true
  - name: "issue_metadata"
    type: "object"
    required: false
  - name: "component_registry"
    type: "object"
    required: false
  - name: "defect_history"
    type: "object"
    required: false
    description: "From Knowledge Base MCP"
output_schema:
  - name: "risk_score"
    type: "number"
    description: "0-100"
  - name: "risk_level"
    type: "string"
    description: "critical | high | medium | low"
  - name: "factors"
    type: "array"
  - name: "recommended_thresholds"
    type: "object"
---
```

**Why P3:** Requires historical defect data (Knowledge Base MCP, P2) and component criticality registry built over time.

**Risk scoring model:**
| Factor | Weight | What It Measures |
|--------|--------|-----------------|
| Change scope | 0–25 | Files changed, lines delta |
| Component criticality | 0–35 | payment > auth > business logic > utility |
| Defect history | 0–25 | Historical defect density for affected files |
| Complexity delta | 0–15 | Cyclomatic complexity increase |

**Risk → thresholds:**
| Level | Score | Coverage | Gate |
|-------|-------|----------|------|
| critical | 75–100 | ≥95% | strict + mandatory review |
| high | 50–74 | ≥85% | strict |
| medium | 25–49 | ≥80% | advisory |
| low | 0–24 | ≥70% | advisory |

**Scripts:** `change-scope-analyzer.py`, `component-criticality.py`, `defect-density-calculator.py`.

**Guardrails:** Advisory only — adjusts thresholds, never auto-approves. Without defect history, factor defaults to 0 (neutral). Component registry maintained by humans, not auto-generated.

### 6.2 reviewing-code-quality

```yaml
---
name: reviewing-code-quality
version: "1.0.0"
description: "Two-stage review: spec compliance first, then code quality"
category: evaluation
phase: post-coding
platforms: ["all"]
dependencies: ["generating-qa-report"]
input_schema:
  - name: "git_diff"
    type: "string"
    required: true
  - name: "qa_report"
    type: "object"
    required: true
    description: "All QA gates must pass first"
  - name: "spec_references"
    type: "array"
    required: false
  - name: "review_focus"
    type: "array"
    required: false
output_schema:
  - name: "stage1_spec_compliance"
    type: "object"
  - name: "stage2_code_quality"
    type: "object"
  - name: "verdict"
    type: "string"
    description: "APPROVE | REQUEST_CHANGES | COMMENT"
  - name: "comments"
    type: "array"
    description: "Line-level review comments"
---
```

**Two stages (inspired by Superpowers spec-compliance → code-quality subagent pattern):**

1. **Spec compliance** — verify each spec requirement has implementation in the diff. If stage 1 fails → REQUEST_CHANGES, skip stage 2. Uses `scripts/spec-compliance-checker.py`.
2. **Code quality** — readability, SOLID, performance (N+1 queries, missing caching), pattern consistency. Uses `scripts/quality-metrics.py` (cyclomatic complexity, function length, nesting depth, duplication).

**Consumed by Code Reviewer agent (Claude Sonnet 4.6)** for cross-model objectivity.

**Guardrails:** Never approve a diff failing stage 1. Comments must be actionable (not "could be better"). Don't nitpick linter-catchable style issues.

### 6.3 selecting-regressions

```yaml
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
  - name: "dependency_graph"
    type: "object"
    required: false
  - name: "risk_score"
    type: "object"
    required: false
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
```

**Instructions:**
1. `scripts/change-impact-analyzer.py` → changed files + direct dependents
2. `scripts/dependency-graph-walker.py` → transitive dependencies
3. Map affected modules to tests (naming convention, import analysis, config mapping)
4. `scripts/test-selector.py` → prioritize by risk score and failure history
5. If risk=critical/high, add full regression as fallback

**Guardrails:** Never skip critical-path tests (auth, payments). Low confidence → warn + suggest full suite. Shared infrastructure changes → full regression. Additive — when in doubt, include.

### 6.4 healing-broken-tests

```yaml
---
name: healing-broken-tests
version: "1.0.0"
description: "Auto-repair tests broken by intentional code changes — update selectors, fixtures, expected values"
category: execution
phase: post-coding
platforms: ["all"]
dependencies: ["classifying-test-failures"]
soft_dependencies: ["generating-qa-report"]
input_schema:
  - name: "broken_tests"
    type: "array"
    required: true
  - name: "git_diff"
    type: "string"
    required: true
  - name: "intent"
    type: "string"
    required: true
    description: "Intended change description (from issue/PR)"
output_schema:
  - name: "healed_tests"
    type: "array"
  - name: "unhealed_tests"
    type: "array"
  - name: "patches"
    type: "array"
  - name: "confidence"
    type: "string"
    description: "high (locator) | medium (expected value) | low (logic)"
---
```

**Prerequisites:** This skill requires:
1. CI integration feeding failure records (not manually entered)
2. Knowledge Base with ≥10 defect records for confidence scoring

**Without this infrastructure:** Use `classifying-test-failures` only. Fix tests manually based on classification output. Do not attempt auto-healing without CI + Knowledge Base.

**Breakage classification and repair:**
| Type | Detection | Repair | Confidence |
|------|-----------|--------|------------|
| Locator change | "element not found" | `scripts/locator-updater.py` finds new selector | High |
| Expected value | "expected X got Y" | Update assertion to match new intentional behavior | Medium |
| Logic change | TypeError, AttributeError | Flag for human review — needs intent understanding | Low |

**Scripts:** `failure-pattern-matcher.py` (categorize breakage type), `locator-updater.py` (find new selector from updated code), `diff-correlator.py` (map failures to specific diff hunks).

**Guardrails:** Never auto-heal a test detecting a real bug. High-confidence auto-apply; medium/low require human review. Never change test logic (conditionals, loops) — only update data. Healed test must pass; if not, report as unhealed.

### 6.5 analyzing-defects

```yaml
---
name: analyzing-defects
version: "1.1.0"
description: "Analyze defect root causes, identify patterns, feed insights into Knowledge Base"
category: analysis
phase: post-coding
platforms: ["all"]
dependencies: ["classifying-test-failures", "generating-qa-report", "healing-broken-tests"]
input_schema:
  - name: "defect_data"
    type: "array"
    required: true
    description: "Defect records: issue ID, root cause, component, resolution"
  - name: "time_window"
    type: "string"
    required: false
    description: "30d | 90d | all. Default: 90d."
  - name: "scope"
    type: "string"
    required: false
    description: "team | component | project | organization"
output_schema:
  - name: "patterns"
    type: "array"
  - name: "root_cause_distribution"
    type: "object"
    description: "logic | integration | data | config | concurrency"
  - name: "hotspots"
    type: "array"
    description: "Components with disproportionate defect density"
  - name: "recommendations"
    type: "array"
  - name: "knowledge_base_updates"
    type: "array"
    description: "Proposed updates for human review"
---
```

**Instructions:**
1. `scripts/root-cause-classifier.py` — categorize defects (logic, integration, data, config, concurrency)
2. `scripts/pattern-detector.py` — time-series analysis, frequency by component, trend detection, clustering
3. Identify hotspot components (high defect density relative to code size/change frequency)
4. Generate actionable recommendations (increased thresholds, targeted testing, architecture changes)
5. `scripts/knowledge-base-writer.py` — prepare Knowledge Base updates for human review

**Guardrails:** Patterns require ≥5 data points for statistical significance. Recommendations must be specific and actionable. Knowledge Base updates always proposed for human review, never auto-committed. Sanitize sensitive data before writing.

---

## 7. Rules Files

Declarative quality standards injected into agent context. Complement skills (procedural) with principles (declarative).

### 7.1 qa-standards.md (P1)

- **Test Quality:** Every public function tested, tests independent, AAA structure, descriptive naming
- **Coverage:** ≥80% line coverage default, error handling mandatory for Critical/High components
- **Acceptance:** Every AC traceable to ≥1 test, untestable ACs flagged not skipped
- **Test Data:** No real customer data, realistic distribution, obviously fake PII

### 7.2 tdd-rules.md (P1)

- **Cycle:** Failing test → minimum implementation → refactor (5 steps)
- **Enforcement:** Test files before implementation files, no implementation-only commits
- **Exceptions:** Config files, DB migrations, third-party wrappers

### 7.3 P2+ Rules

| File | Scope |
|------|-------|
| `security-standards.md` | Input validation, auth testing, secrets management, OWASP Top 10 coverage |
| `platform/typescript.md` | Strict mode, type assertions, any-type restrictions, async patterns |
| `platform/python.md` | Type hints, docstrings, venv rules, import ordering |
| `platform/java.md` | Annotations, exception handling, Stream API testing, Spring test slicing |
| `platform/go.md` | Table-driven tests, error conventions, goroutine testing, race detector |
| `review-guidelines.md` (P3) | Two-stage process, comment quality, cross-model protocol |

### 7.4 Rules Connectivity

Skills explicitly load rules files at runtime via `**Load before starting:**` directives:

| Rules File | Loaded by |
|------------|-----------|
| `qa-standards.md` | analyzing-coverage, validating-acceptance-criteria, classifying-test-failures, test-driven-development |
| `tdd-rules.md` | test-driven-development |
| `review-guidelines.md` | reviewing-code-quality |
| `security-standards.md` | reviewing-code-quality, generating-api-tests |

Rules files are declarative (principles); skills are procedural (steps). Together they provide both "what the standard is" and "how to apply it."

## 8. Eval Framework

Each skill ships with `evals/test-prompts.yaml` + `evals/assertions.yaml` (anthropics/skills 4-mode pattern).

### 8.1 Test Cases Per Skill

| Skill | # | Focus |
|-------|----|-------|
| parsing-requirements | 4 | Clear AC, ambiguity detection, missing info, empty description |
| test-driven-development | 3 | Simple feature, multi-AC, boundary value |
| analyzing-coverage | 3 | High PASS, low FAIL, critical component medium |
| validating-acceptance-criteria | 4 | All SATISFIED, mixed, keyword-match-wrong-body, zero tests |
| classifying-test-failures | 3 | Real bug, flaky, env issue |
| generating-qa-report | 3 | All-pass, mixed-fail, advisory-mode |
| generating-test-data | 4 | Insurance domain, PII pass, edge-heavy distribution, factory output |
| generating-playwright-tests | 3 | Form page, auth flow, accessibility assertions |
| generating-api-tests | 4 | REST happy path, GraphQL edges, contract validation, errors |
| generating-mobile-tests | 3 | iOS XCTest, Android Espresso, cross-platform Appium |
| generating-perf-tests | 3 | K6 ramp-up, Locust spike, insurance load profile |
| scoring-risk | 3 | Critical component, low-risk utility, high defect history |
| reviewing-code-quality | 4 | Spec-compliant, spec deviation, high-quality, poor quality |
| selecting-regressions | 3 | Narrow change, broad infra change, cross-module |
| healing-broken-tests | 3 | Locator (high), expected value (medium), logic (unhealed) |
| analyzing-defects | 3 | Pattern detection, hotspot, insufficient data |

### 8.2 Concrete Examples

**parsing-requirements — tc-001:**
```yaml
test_cases:
  - id: "pr-tc-001"
    description: "Password validation with one ambiguous criterion"
    input:
      issue_description: |
        Add password validation to the signup form.
        - Password must be 8-64 characters
        - Must contain at least one uppercase letter and one number
        - Should display appropriate error messages
        - Must not allow previously breached passwords (HaveIBeenPwned API)
    expected:
      acceptance_criteria_count: 4
      testable_count: 3
      ambiguity_flags: ["AC-3: 'appropriate' is vague"]
```
```yaml
assertions:
  - test_case: "pr-tc-001"
    checks:
      - { field: "acceptance_criteria", operator: "length_equals", value: 4 }
      - { field: "acceptance_criteria[2].testable", operator: "equals", value: false }
      - { field: "ambiguities[0]", operator: "contains", value: "appropriate" }
```

**classifying-test-failures — tc-001:**
```yaml
test_cases:
  - id: "cf-tc-001"
    description: "Three failures: real bug + flaky + env issue"
    input:
      failed_tests:
        - { name: "test_payment_retry", error: "AssertionError: Expected 3 got 0" }
        - { name: "test_ws_reconnect", error: "Timeout: 5000ms" }
        - { name: "test_db_rollback", error: "ECONNREFUSED 127.0.0.1:5432" }
      test_command: "npm test"
      retry_count: 2
    expected:
      real_bugs: 1
      flaky: 1
      env_issues: 1
      verdict: "FAIL"
```

### 8.3 Running Evals (Future CLI)

```bash
symphony skill eval parsing-requirements                    # single skill
symphony skill eval --dir .github/skills/qa/               # all QA skills
symphony skill eval parsing-requirements --benchmark --runs 5  # variance analysis
```

Not yet implemented. Evals can run manually until CLI exists.

## 9. Implementation Notes

- **SKILL.md < 500 lines.** Heavy logic in scripts/, domain knowledge in references/.
- **P1 scripts: Python stdlib only.** P2+ may add minimal deps in per-skill `requirements.txt`.
- **Templates use Liquid** (.liquid) — already used in GitHub Actions, readable by non-developers.
- **Migration path:** `.github/skills/qa/<skill>/` → `symphony-qa-core/skills/<skill>/` when plugin is packaged. File move, no content changes.
- **Knowledge Base degradation (P2+):** `scoring-risk` without history → defect factor defaults to 0. `selecting-regressions` without dep graph → filename matching (low confidence). `analyzing-defects` without history → current batch only.
- **Frontmatter standard:** Only `name` and `description` allowed in SKILL.md frontmatter (Anthropic standard). All schema, dependency, and version metadata lives in `## Quick Reference` body sections. The extended YAML in this spec is documentation-only.
- **Workpad output:** All evaluation skills (parsing-requirements, test-driven-development, analyzing-coverage, validating-acceptance-criteria, classifying-test-failures, generating-qa-report) write structured output to the issue `## Copilot Workpad` under a `### QA: <skill>` heading.
- **Script fallbacks:** Every skill that calls a Python/shell script includes a `**Script unavailable:**` fallback describing how to perform the equivalent step manually. Skills are usable even without a fully configured scripts/ environment.
- **Domain scope:** Insurance-specific reference files are defaults, not requirements. All skills are designed domain-agnostically; insurance schemas and patterns are the provided starting point. Teams bring their own domain references for other industries.
- **Pipeline entry point:** `README.md` in `.github/skills/qa/` provides a pipeline navigation guide with three paths (Full Pipeline, Report-Only, Test Generation), skill map by phase, output convention, and rules directory map.
- **Rules connectivity:** Skills explicitly load relevant rules files via `**Load before starting:**` directives. See §7.4 for the full connectivity table.

## 10. Open Questions

1. ~~**TDD extension loading order**~~ **RESOLVED** (§3.1): QA TDD redesigned as standalone skill. Incorporates Superpowers TDD Iron Law + RGR discipline directly. No extension/loading-order concern.
2. **Eval runner** — CLI doesn't exist yet. Evals included from P1 to document expected behavior.
3. ~~**Script deps**~~ **RESOLVED**: stdlib-only for all phases. P2 scripts use stdlib replacements (no pydantic/faker/lxml). Script fallback guidance added to all skills for environments where scripts are unavailable.
4. **Knowledge Base schema** — P3 skills assume generic query interface. Finalize during P2 implementation.
5. **Template maintenance** — QA CoE maintains core templates; teams override via WORKFLOW.md.
6. **Insurance domain knowledge** — Authored by business SMEs, not generated. QA CoE leads with business team input.
7. ~~**Frontmatter standard clarified**~~ **RESOLVED**: anthropics/skills standard allows only name + description in frontmatter. Extended YAML in this spec is documentation-only. All SKILL.md files validated against this standard.
