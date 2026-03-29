# QA Skills, Plugins, MCPs & Hooks — Design Spec

**Date:** 2026-03-27
**Author:** Patrick (QA CoE — Center of Excellence)
**Status:** Draft (v2 — post-audit)
**Parent specs:** [Orchestrator Design](2026-03-26-ai-native-sdlc-orchestrator-design.md), [QA Agent System](2026-03-25-qa-agent-system-design.md)
**References:** [obra/superpowers](https://github.com/obra/superpowers), [anthropics/skills](https://github.com/anthropics/skills), [everything-claude-code](https://github.com/affaan-m/everything-claude-code)

---

## 1. Problem Statement

The orchestrator design (§4–7) defines agent roles and quality gates. The QA agent spec (§3–5) defines evaluation dimensions and a skill hub taxonomy. What is missing is the **concrete implementation design** for the QA ecosystem components that agents consume:

1. **Skills** — Reusable prompt+script bundles that encode QA expertise (TDD, code review, test generation, etc.)
2. **Hooks** — Event-driven automations that enforce quality at tool-use boundaries (pre-commit lint, post-edit typecheck, etc.)
3. **MCPs** — External service integrations that connect agents to QA infrastructure (coverage tools, SAST scanners, test runners)
4. **Plugins** — Distributable packages that bundle skills + hooks + MCPs + rules into installable units per team/platform

This spec defines the architecture, catalog, and implementation plan for all four component types, organized around the three SDLC intervention points from the QA agent spec (§3): **pre-coding**, **during-coding**, and **post-coding**.

### 1.1 Design Boundary: Skills vs Hooks

A critical design principle governs the separation between skills and hooks:

- **Skills** encode QA *expertise and judgment* — things an LLM needs instructions, examples, and guardrails to do well. Skills are agent-invoked (explicit).
- **Hooks** automate *deterministic commands* — running a linter, type checker, or test suite. Hooks are system-enforced (implicit, fire on tool-use events).

If the component's value is "run a shell command and parse the output," it's a **hook**. If the component's value is "apply QA methodology and make nuanced decisions," it's a **skill**.

## 2. Design Principles

Derived from reference repo analysis (obra/superpowers, anthropics/skills, everything-claude-code):

| Principle | Source | Application |
|-----------|--------|-------------|
| **Resident identity + on-demand skills** | Superpowers (session-start hook injects meta-skill) | Agent.md is always in context; skills loaded JIT via L1→L2→L3 |
| **Two-stage verification** | Superpowers (spec-compliance → code-quality subagents) | Post-coding review always runs spec-first, then quality |
| **Hook-driven quality gates** | ECC (PreToolUse/PostToolUse hooks with env-var profiles) | Hooks enforce quality at tool boundaries, configurable per team |
| **Skill = SKILL.md + scripts/ + references/** | Anthropics/skills (progressive disclosure, <500 line SKILL.md) | Skills are self-contained; heavy logic in scripts/, not prompts |
| **Specialized reviewer agents per domain** | ECC (28 agents: code-reviewer, security-reviewer, db-reviewer, etc.) | QA uses domain-specific review agents, not one monolithic reviewer |
| **Eval-driven skill development** | Anthropics/skills (4-mode: create → eval → improve → benchmark) | Every skill ships with eval test cases and success criteria |
| **Environment-variable hook profiles** | ECC (ECC_HOOK_PROFILE=minimal\|standard\|strict) | Teams configure hook strictness without editing hook code |
| **Gerund naming convention** | Anthropic/Superpowers/ECC (writing-plans, requesting-code-review, systematic-debugging) | All skill names use gerund-phrase or noun-compound pattern, 2–3 words, kebab-case |

## 3. Component Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Symphony QA Ecosystem                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      Plugins (Distributable)                  │   │
│  │                                                               │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │ symphony │  │ symphony │  │ symphony │  │ symphony │    │   │
│  │  │ -qa-core │  │ -qa-web  │  │ -qa-     │  │ -qa-     │    │   │
│  │  │          │  │          │  │ mobile   │  │ security │    │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │   │
│  │       │              │              │              │          │   │
│  └───────┼──────────────┼──────────────┼──────────────┼──────────┘   │
│          │              │              │              │               │
│  ┌───────▼──────────────▼──────────────▼──────────────▼──────────┐   │
│  │                     Skills (SKILL.md)                          │   │
│  │                  Encode QA expertise & judgment                 │   │
│  │                                                                │   │
│  │  Pre-coding          During-coding     Post-coding             │   │
│  │  ├─ parsing-         ├─ test-driven-   ├─ analyzing-           │   │
│  │  │  requirements     │  development    │  coverage             │   │
│  │  │                   │  (extend        ├─ validating-          │   │
│  │  │                   │   existing)     │  acceptance-criteria  │   │
│  │  │                   │                 ├─ classifying-         │   │
│  │  │                   │                 │  test-failures        │   │
│  │  │                   │                 └─ generating-          │   │
│  │  │                   │                    qa-report            │   │
│  └──┼───────────────────┼────────────────────────────────────────┘   │
│     │                   │                                            │
│  ┌──▼───────────────────▼────────────────────────────────────────┐   │
│  │                     Hooks (hooks.json)                         │   │
│  │               Automate deterministic commands                  │   │
│  │                                                                │   │
│  │  SessionStart    PreToolUse      PostToolUse       Stop        │   │
│  │  ├─ load-qa-     ├─ block-       ├─ typecheck     ├─ update-  │   │
│  │  │  context       │  commit-if    ├─ lint-check    │  workpad  │   │
│  │  ├─ inject-tdd   │  tests-fail   └─ coverage-     └─ generate │   │
│  │  │  rules        ├─ security-      delta-check      -summary  │   │
│  │  └─ load-ac       │  scan-pre                                  │   │
│  │                   └─ lint-before                                │   │
│  │                      -commit                                   │   │
│  └────────────────────────────┬───────────────────────────────────┘   │
│                               │                                       │
│  ┌────────────────────────────▼───────────────────────────────────┐   │
│  │                     MCPs (External Services)                   │   │
│  │                                                                │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐                 │   │
│  │  │ coverage  │  │ sast-     │  │ tracker-  │                 │   │
│  │  │ -service  │  │ scanner   │  │ bridge    │                 │   │
│  │  └───────────┘  └───────────┘  └───────────┘                 │   │
│  │                                                                │   │
│  │  P2+: ┌───────────┐  ┌───────────┐                           │   │
│  │       │ test-      │  │ knowledge │                           │   │
│  │       │ infra      │  │ -base     │                           │   │
│  │       └───────────┘  └───────────┘                           │   │
│  └────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 4. Skills Design

### 4.1 Skill Standard Structure

Aligned with anthropics/skills spec. Each skill is a directory under `skill-hub/` (long-term) or `.github/skills/qa/` (quick win):

```
<skill-name>/
├── SKILL.md              # Required: YAML frontmatter + instructions (<500 lines)
├── scripts/              # Deterministic automation (shell, Python)
├── references/           # Domain knowledge, loaded on-demand (L3)
├── templates/            # Code scaffolding templates
├── evals/                # Eval test cases (from anthropics/skills pattern)
│   ├── test-prompts.yaml # 2-3 realistic test prompts
│   └── assertions.yaml   # Expected outcomes for grading
└── knowledge/            # Skill-specific knowledge files
```

### 4.2 SKILL.md Format

```markdown
---
name: "skill-name"
version: "1.0.0"
description: "One-line description (used for L1 catalog)"
category: "analysis | generation | evaluation | enforcement"
phase: "pre-coding | during-coding | post-coding"
platforms: ["all"] # or ["playwright", "appium", "jest", etc.]
dependencies: []   # Other skills this requires
input_schema:
  - name: "issue_context"
    type: "object"
    required: true
output_schema:
  - name: "report"
    type: "object"
---

# [Skill Name]

## When to Use
[Trigger conditions — when should the agent invoke this skill]

## Instructions
[Step-by-step procedure, max 500 lines]
[Reference scripts/ for heavy logic]
[Reference references/ for domain knowledge]

## Examples
[2-3 concrete examples with input → output]

## Guardrails
[What this skill must NOT do]
```

### 4.3 Three-Level Loading (L1 → L2 → L3)

Consistent with orchestrator spec §6.2 context engineering principles:

| Level | What Loads | When | Token Cost |
|-------|-----------|------|------------|
| **L1** | `name` + `description` from SKILL.md frontmatter | Always in agent context (skill catalog) | ~20 tokens/skill |
| **L2** | Full SKILL.md content | When agent decides to invoke the skill | ~500–2000 tokens |
| **L3** | scripts/ + references/ + templates/ | When SKILL.md references them during execution | Variable |

### 4.4 Naming Convention

All skill names follow the convention observed across Anthropic, Superpowers, and Everything-Claude-Code:

- **Gerund-phrase** pattern (activity-oriented): `analyzing-coverage`, `validating-acceptance-criteria`
- **Kebab-case**, lowercase, 2–4 words
- Plain English preferred over jargon
- Name describes what the **agent does**, not what the component is

> **Note:** The QA agent spec (§5) and orchestrator spec (§4.3) use agent-noun naming (`test-runner`, `coverage-analyzer`) which is appropriate for Python class names. SKILL.md directory names use the gerund convention. The mapping is documented in §12.

### 4.5 Skill Catalog — P1 (Quick Win)

#### 4.5.1 parsing-requirements

```yaml
name: parsing-requirements
category: analysis
phase: pre-coding
description: "Parse issue description into structured acceptance criteria, detect ambiguities, and flag missing information"
```

**Purpose:** Extract structured AC from free-text issue descriptions. Detect ambiguity (vague verbs, missing boundary conditions, undefined terms). Output machine-parseable AC list that downstream skills consume.

**Why this is a skill (not a hook):** Requires LLM judgment to detect semantic ambiguity, assess testability, and identify missing requirements. A regex script can extract bullet points but cannot determine that "should handle edge cases appropriately" is untestable.

**Scripts:**
- `scripts/extract-ac.py` — Regex + heuristic AC extraction from Markdown/JIRA formatted descriptions
- `scripts/ambiguity-detector.py` — Pattern matching for known ambiguity signals ("appropriate", "should handle", "etc.", missing numeric thresholds)

**Output:**
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

#### 4.5.2 test-driven-development (extend existing)

```yaml
name: test-driven-development
category: enforcement
phase: during-coding
description: "Enforce TDD Red-Green-Refactor rhythm: generate test cases from AC, write failing tests, implement, verify"
```

**Purpose:** The complete TDD methodology skill. Extends the existing `.github/skills/test-driven-development/SKILL.md` from Superpowers with QA-specific enhancements.

**Why this absorbs test-case-matrix and test-skeleton-gen:** These were previously separate skills, but they are inseparable steps in one TDD workflow. An agent never generates a test case matrix without then generating test skeletons, and never generates skeletons without then enforcing Red→Green→Refactor. Splitting them into 3 skills created artificial boundaries that break the flow.

**Enhanced TDD flow (absorbs former test-case-matrix + test-skeleton-gen + tdd-enforce):**
1. **Analyze AC** → Generate test case matrix from acceptance criteria (equivalence partitioning, BVA, decision tables)
2. **Red** → Generate test skeletons that compile but fail (import from expected module path)
3. **Verify Red** → Run tests, confirm they fail for the expected reason
4. **Green** → Write minimum implementation code to pass tests
5. **Verify Green** → Run all tests, confirm they pass
6. **Refactor** → Improve code structure while keeping tests green

**References:**
- `references/test-design-techniques.md` — Equivalence partitioning, BVA, decision tables, state transition
- `references/insurance-domain-patterns.md` — Common insurance domain test patterns
- `references/testing-anti-patterns.md` — What NOT to do (already exists in Superpowers)

**Templates:**
- `templates/jest.test.ts.liquid` — Jest/TypeScript test skeleton
- `templates/pytest.py.liquid` — pytest skeleton
- `templates/playwright.spec.ts.liquid` — Playwright E2E skeleton
- `templates/junit.java.liquid` — JUnit 5 skeleton

**Scripts:**
- `scripts/tdd-rhythm-checker.sh` — Analyzes git diff sequence to verify Red→Green→Refactor ordering
- `scripts/test-coverage-delta.sh` — Compares coverage before and after each implementation step

**Enforcement Rules:**
1. Before writing implementation code, at least one new test file must exist
2. New test must be executed and shown to fail before implementation
3. After implementation, all tests must pass
4. Refactoring changes must not break passing tests

> **Naming note:** The orchestrator spec §4.3 lists `test-driven-development` as a Developer skill. This is the same skill, extended with QA-specific enhancements. No alias needed.

#### 4.5.3 analyzing-coverage

```yaml
name: analyzing-coverage
category: evaluation
phase: post-coding
description: "Analyze code coverage against thresholds — interpret gaps, assess risk, suggest which untested paths matter most"
```

**Purpose:** Goes beyond running a coverage tool (that's deterministic — hooks handle it). This skill interprets coverage results: which gaps are risky? Which untested paths are likely to contain bugs? Should the threshold be adjusted based on the component's criticality?

**Why this is a skill (not a hook):** The hook `coverage-delta-check` runs the coverage command and reports numbers. This skill *interprets* those numbers — deciding that 75% branch coverage on a payment module is more concerning than 75% on a utility helper.

**Scripts:**
- `scripts/coverage-report.py` — Runs coverage tool and parses output
- `scripts/coverage-gap-analyzer.py` — Identifies specific untested paths and suggests test cases for them

**Output:**
```json
{
  "summary": {
    "lines": { "covered": 850, "total": 1000, "pct": 85.0 },
    "branches": { "covered": 120, "total": 160, "pct": 75.0 },
    "functions": { "covered": 95, "total": 100, "pct": 95.0 }
  },
  "threshold": 80,
  "verdict": "PASS",
  "gaps": [
    { "file": "src/auth/mfa.ts", "uncovered_lines": [23, 45, 67], "risk": "high", "suggestion": "Missing test for MFA timeout path — this is a security-sensitive code path" }
  ]
}
```

#### 4.5.4 validating-acceptance-criteria

```yaml
name: validating-acceptance-criteria
category: evaluation
phase: post-coding
description: "Verify implementation satisfies each acceptance criterion — map AC to test evidence, score SATISFIED/PARTIAL/UNMET"
```

**Purpose:** The most nuanced evaluation dimension. Maps each AC to evidence: test that exercises it, code that implements it, or manual verification note. Requires LLM judgment to determine whether "password validation" in a test name actually covers AC-1 ("Password must be 8-64 characters").

**Why this is a skill (not a hook):** No deterministic command can assess whether code semantically satisfies a natural-language acceptance criterion. This is pure LLM judgment.

**Input:** Parsed AC list (from parsing-requirements) + git diff + test results
**Method:**
1. For each AC, search test names/descriptions for matching keywords
2. For each AC, search code diff for implementing logic
3. Score each AC: SATISFIED (test exists + passes), PARTIAL (code exists, no test), UNMET (no evidence)

**Output:**
```json
{
  "criteria": [
    { "id": "AC-1", "text": "Password 8-64 chars", "status": "SATISFIED", "evidence": ["validator.test.ts:TC-001..TC-004"] },
    { "id": "AC-2", "text": "Error message on invalid", "status": "PARTIAL", "evidence": ["code: validator.ts:50-55"], "missing": "No test for error message content" }
  ],
  "satisfied": 3,
  "partial": 1,
  "unmet": 0,
  "verdict": "FAIL",
  "reason": "AC-2 has no test coverage for error message content"
}
```

#### 4.5.5 classifying-test-failures

```yaml
name: classifying-test-failures
category: evaluation
phase: post-coding
description: "Classify test failures as real-bug, flaky, or environment-issue — retry and analyze error patterns"
```

**Purpose:** Prevents false FAIL verdicts from flaky tests or environment issues. From QA agent spec §4 flaky detection.

**Why this is a skill (not a hook):** Requires judgment to distinguish a real assertion failure from a timing-dependent flaky test from a database connection timeout. The retry logic is deterministic (hook-like), but the classification decision is not.

**Method:**
1. Retry failed tests up to 2 times (P1)
2. If test passes on retry → classify as `flaky` (report but don't fail gate)
3. If test fails consistently → classify as `real-bug`
4. If test fails with connection/timeout/resource errors → classify as `env-issue`
5. P3: Historical pass rate analysis from defect-analyzer knowledge base

**Scripts:**
- `scripts/retry-failures.sh` — Re-runs only failed tests
- `scripts/classify-failure.py` — Error pattern matching for env vs real bug

#### 4.5.6 generating-qa-report

```yaml
name: generating-qa-report
category: evaluation
phase: post-coding
description: "Aggregate all evaluation dimensions into structured QA Report markdown for issue workpad"
```

**Purpose:** Combines outputs from analyzing-coverage, validating-acceptance-criteria, and classifying-test-failures into a single report. This is what appears in the issue workpad. Ensures consistent report format across all teams.

**Output (Markdown for workpad):**
```markdown
## QA Evaluation Report
**Issue:** PAY-123 — Add password validation
**Evaluator:** QA Agent (Gemini 3 Pro)
**Date:** 2026-03-27T14:30:00Z

### Verdict: PASS ✓

### Dimensions
| Dimension | Score | Threshold | Policy | Status |
|-----------|-------|-----------|--------|--------|
| Pass Rate | 100% (42/42) | 100% | strict | ✓ |
| Coverage | 85% lines, 75% branches | 80% lines | strict | ✓ |
| Acceptance | 4/4 AC satisfied | 100% | strict | ✓ |

### Test Results
- 42 tests passed, 0 failed, 1 skipped
- Duration: 12.5s
- Flaky tests: 0
- Environment issues: 0

### Coverage Gaps (advisory)
- `src/auth/mfa.ts` lines 23, 45, 67 — MFA timeout path untested (risk: high)

### Notes
- All acceptance criteria verified with test evidence
- Branch coverage (75%) below recommended 80% but above minimum threshold
```

### 4.6 Skill Catalog — P2 (Generation & Platform Expansion)

| Skill Name | Category | Description |
|-----------|----------|-------------|
| `generating-test-data` | generation | M7: Generate synthetic test data with insurance domain awareness, realistic distribution, no real PII |
| `generating-playwright-tests` | generation | Generate Playwright E2E test scripts from test case matrix + Knowledge Base patterns |
| `generating-api-tests` | generation | Generate API test scripts (REST/GraphQL) with schema validation and edge cases |
| `generating-mobile-tests` | generation | Generate Appium/XCTest/UIAutomator2 test scripts for iOS and Android |
| `generating-perf-tests` | generation | Generate K6/Locust performance test scripts with realistic load profiles |

### 4.7 Skill Catalog — P3 (Advanced & Self-Improving)

| Skill Name | Category | Description |
|-----------|----------|-------------|
| `scoring-risk` | analysis | M4: Score issue risk level based on change scope, component criticality, historical defect data. Feeds dynamic coverage thresholds. |
| `reviewing-code-quality` | evaluation | Two-stage review: spec compliance first, then code quality. Consumed by Code Reviewer agent. |
| `selecting-regressions` | execution | M6: Select relevant regression tests based on change impact analysis |
| `healing-broken-tests` | execution | M5: Auto-repair broken tests caused by intentional code changes (locator/selector updates) |
| `analyzing-defects` | analysis | M8: Analyze defect root causes, identify patterns, feed back into Knowledge Base |

## 5. Hooks Design

### 5.1 Hook Architecture

Hooks are event-driven scripts that fire at agent tool-use boundaries. They automate **deterministic commands** — things that don't require LLM judgment. Running a linter, type checker, or test suite on file edit are hooks, not skills.

Inspired by everything-claude-code's hooks.json pattern with environment-variable profiles.

```
hooks/
├── hooks.json                    # Hook event registry
├── session-start/
│   ├── load-qa-context.sh        # Inject project QA standards into context
│   ├── inject-tdd-rules.sh       # Load TDD enforcement rules
│   └── load-acceptance-criteria.sh  # Pre-load AC from tracker
├── pre-tool-use/
│   ├── block-commit-if-tests-fail.sh
│   ├── security-scan-pre-commit.sh
│   └── lint-before-commit.sh
├── post-tool-use/
│   ├── typecheck-on-edit.sh      # After file edit: run type checker
│   ├── lint-on-edit.sh           # After file edit: run linter
│   └── coverage-delta-check.sh   # After file edit: check incremental coverage
└── stop/
    ├── generate-qa-summary.sh    # When agent completes: summarize QA status
    └── update-workpad.sh         # Write QA status to tracker workpad
```

> **Why no during-coding "skills" for lint/typecheck/coverage?** These were previously defined as both skills AND hooks, creating duplication. Running `tsc --noEmit`, `eslint`, or a coverage command is a deterministic operation — the right mechanism is a hook that fires automatically on PostToolUse, not a skill the agent must explicitly invoke.

### 5.2 hooks.json Schema

```json
{
  "hooks": {
    "SessionStart": [
      {
        "id": "load-qa-context",
        "script": "hooks/session-start/load-qa-context.sh",
        "description": "Load project QA standards and test configuration",
        "profile": ["minimal", "standard", "strict"],
        "timeout_ms": 10000
      },
      {
        "id": "inject-tdd-rules",
        "script": "hooks/session-start/inject-tdd-rules.sh",
        "description": "Inject TDD enforcement rules into agent context",
        "profile": ["standard", "strict"],
        "timeout_ms": 5000
      },
      {
        "id": "load-acceptance-criteria",
        "script": "hooks/session-start/load-acceptance-criteria.sh",
        "description": "Pre-load acceptance criteria from issue tracker",
        "profile": ["standard", "strict"],
        "timeout_ms": 15000,
        "env": {
          "TRACKER_API_URL": "$TRACKER_API_URL",
          "ISSUE_ID": "$SYMPHONY_ISSUE_ID"
        }
      }
    ],

    "PreToolUse": [
      {
        "id": "block-commit-if-tests-fail",
        "script": "hooks/pre-tool-use/block-commit-if-tests-fail.sh",
        "description": "Block git commit if project tests are failing",
        "tool_filter": ["bash:git commit", "bash:git push"],
        "profile": ["standard", "strict"],
        "action_on_fail": "block",
        "timeout_ms": 120000
      },
      {
        "id": "security-scan-pre-commit",
        "script": "hooks/pre-tool-use/security-scan-pre-commit.sh",
        "description": "Scan for hardcoded secrets before commit",
        "tool_filter": ["bash:git commit"],
        "profile": ["strict"],
        "action_on_fail": "block",
        "timeout_ms": 30000
      },
      {
        "id": "lint-before-commit",
        "script": "hooks/pre-tool-use/lint-before-commit.sh",
        "description": "Run linter on staged files before commit",
        "tool_filter": ["bash:git commit"],
        "profile": ["strict"],
        "action_on_fail": "warn",
        "timeout_ms": 30000
      }
    ],

    "PostToolUse": [
      {
        "id": "typecheck-on-edit",
        "script": "hooks/post-tool-use/typecheck-on-edit.sh",
        "description": "Run type checker on edited file",
        "tool_filter": ["edit", "write"],
        "profile": ["standard", "strict"],
        "timeout_ms": 30000
      },
      {
        "id": "lint-on-edit",
        "script": "hooks/post-tool-use/lint-on-edit.sh",
        "description": "Run linter on edited file",
        "tool_filter": ["edit", "write"],
        "profile": ["strict"],
        "timeout_ms": 30000
      },
      {
        "id": "coverage-delta-check",
        "script": "hooks/post-tool-use/coverage-delta-check.sh",
        "description": "Check coverage delta after implementation changes",
        "tool_filter": ["edit", "write"],
        "profile": ["strict"],
        "timeout_ms": 60000,
        "debounce_ms": 10000
      }
    ],

    "Stop": [
      {
        "id": "generate-qa-summary",
        "script": "hooks/stop/generate-qa-summary.sh",
        "description": "Generate QA summary when agent phase completes",
        "profile": ["minimal", "standard", "strict"],
        "timeout_ms": 30000
      },
      {
        "id": "update-workpad",
        "script": "hooks/stop/update-workpad.sh",
        "description": "Write QA status to tracker issue workpad",
        "profile": ["standard", "strict"],
        "timeout_ms": 15000,
        "env": {
          "TRACKER_API_URL": "$TRACKER_API_URL",
          "ISSUE_ID": "$SYMPHONY_ISSUE_ID"
        }
      }
    ]
  }
}
```

### 5.3 Hook Profiles

Aligned with orchestrator spec §7.3 Team Onboarding Profiles and §27 Maturity Model:

| Profile | Active Hooks | Use Case |
|---------|-------------|----------|
| **minimal** | SessionStart (load context), Stop (summary + workpad) | Teams at Maturity Level 1; observability only, no blocking |
| **standard** | minimal + PreToolUse (block commit if tests fail), PostToolUse (typecheck on edit) | Teams at Maturity Level 2–3; core quality enforcement |
| **strict** | All hooks active including coverage delta, security scan, lint on edit | Teams at Maturity Level 4+; full quality enforcement |

Configuration via WORKFLOW.md:

```yaml
# WORKFLOW.md
hooks:
  profile: standard  # minimal | standard | strict
  overrides:
    # Enable specific hooks from a stricter profile
    "security-scan-pre-commit": true
    # Disable specific hooks from current profile
    "typecheck-on-edit": false
```

### 5.4 Hook Data Flow

```
Agent invokes tool (e.g., Edit file)
    │
    ▼
PreToolUse hooks fire (if tool matches filter)
    │
    ├── action_on_fail: "block" → tool execution prevented, feedback to agent
    ├── action_on_fail: "warn" → warning injected into agent context, tool proceeds
    └── action_on_fail: "log" → logged only, no agent feedback
    │
    ▼
Tool executes
    │
    ▼
PostToolUse hooks fire (if tool matches filter)
    │
    ├── Results injected into agent context as feedback
    ├── Debounced to avoid excessive runs (configurable per hook)
    └── Long-running hooks run async, results available next turn
```

### 5.5 Hook Environment Variables

Each hook receives standard environment variables from the orchestrator:

```bash
# Standard variables (always available)
SYMPHONY_ISSUE_ID        # Current issue identifier (e.g., PAY-123)
SYMPHONY_PHASE           # Current phase (e.g., development, qa-evaluation)
SYMPHONY_ROLE            # Current agent role (e.g., developer, qa-evaluator)
SYMPHONY_WORKSPACE       # Workspace root path
SYMPHONY_HOOK_PROFILE    # Active profile (minimal|standard|strict)

# Tool-specific variables (available for tool-filtered hooks)
SYMPHONY_TOOL_NAME       # Tool that triggered the hook (e.g., edit, bash)
SYMPHONY_TOOL_INPUT      # Tool input (file path for edit, command for bash)
SYMPHONY_TOOL_OUTPUT     # Tool output (for PostToolUse only)

# Project-specific variables (from WORKFLOW.md)
TRACKER_API_URL          # Tracker API endpoint
TRACKER_API_TOKEN        # Tracker auth token (from secrets)
```

## 6. MCP Server Design

### 6.1 MCP Architecture

MCPs (Model Context Protocol servers) provide external service access to agents. They expose tools that agents can invoke for deterministic operations that are better handled by dedicated infrastructure than LLM reasoning.

```
Agent Context
    │
    ▼
MCP Tool Call (e.g., coverage_service.run_coverage)
    │
    ▼
MCP Server (local process or remote service)
    │
    ▼
External Service (Istanbul, JaCoCo, Semgrep, JIRA API, etc.)
```

### 6.2 MCP Server Catalog — P1

#### 6.2.1 coverage-service MCP

```json
{
  "name": "coverage-service",
  "description": "Code coverage collection and analysis",
  "tools": [
    {
      "name": "run_coverage",
      "description": "Run coverage tool for the project and return coverage report",
      "input": { "workspace_path": "string", "threshold": "number" },
      "output": { "summary": "object", "per_file": "array", "verdict": "string" }
    },
    {
      "name": "get_uncovered_lines",
      "description": "Get specific uncovered lines for a file",
      "input": { "file_path": "string" },
      "output": { "uncovered_lines": "array", "uncovered_branches": "array" }
    },
    {
      "name": "compare_coverage",
      "description": "Compare coverage between base branch and current branch",
      "input": { "base_branch": "string" },
      "output": { "delta": "object", "new_uncovered": "array" }
    }
  ],
  "transport": "stdio",
  "command": "python",
  "args": ["mcps/coverage-service/server.py"]
}
```

**Backends:** Istanbul (JS/TS), JaCoCo (Java), coverage.py (Python), lcov (C/C++), tarpaulin (Rust), cover (Go). Auto-detected from project config.

#### 6.2.2 sast-scanner MCP

```json
{
  "name": "sast-scanner",
  "description": "Static Application Security Testing",
  "tools": [
    {
      "name": "scan_project",
      "description": "Run SAST scan on project, return findings categorized by severity",
      "input": { "workspace_path": "string", "scan_scope": "full|changed" },
      "output": { "findings": "array", "summary": "object" }
    },
    {
      "name": "scan_dependencies",
      "description": "Scan dependencies for known vulnerabilities",
      "input": { "workspace_path": "string" },
      "output": { "vulnerabilities": "array", "summary": "object" }
    },
    {
      "name": "scan_secrets",
      "description": "Detect hardcoded secrets in codebase",
      "input": { "workspace_path": "string", "scan_scope": "full|changed" },
      "output": { "secrets_found": "array" }
    }
  ],
  "transport": "stdio",
  "command": "python",
  "args": ["mcps/sast-scanner/server.py"]
}
```

**Backends:** Semgrep (multi-language SAST), Snyk (dependency vulnerabilities), Trivy (container + dependency), gitleaks (secrets).

#### 6.2.3 tracker-bridge MCP

```json
{
  "name": "tracker-bridge",
  "description": "Issue tracker integration for QA workflows",
  "tools": [
    {
      "name": "get_acceptance_criteria",
      "description": "Fetch structured acceptance criteria from issue",
      "input": { "issue_id": "string" },
      "output": { "criteria": "array", "raw_description": "string" }
    },
    {
      "name": "update_workpad",
      "description": "Update QA section of issue workpad",
      "input": { "issue_id": "string", "content": "string" },
      "output": { "success": "boolean" }
    },
    {
      "name": "post_qa_verdict",
      "description": "Post QA verdict and transition issue state",
      "input": { "issue_id": "string", "verdict": "PASS|FAIL", "report": "string" },
      "output": { "success": "boolean", "new_state": "string" }
    }
  ],
  "transport": "stdio",
  "command": "python",
  "args": ["mcps/tracker-bridge/server.py"],
  "env": {
    "TRACKER_TYPE": "$TRACKER_TYPE",
    "TRACKER_API_URL": "$TRACKER_API_URL",
    "TRACKER_API_TOKEN": "$TRACKER_API_TOKEN"
  }
}
```

**Backends:** JIRA REST API, Linear GraphQL API (via TrackerAdapter from orchestrator spec §8).

### 6.3 MCP Server Catalog — P2+

#### 6.3.1 test-infrastructure MCP (P2)

```json
{
  "name": "test-infrastructure",
  "description": "Test execution infrastructure management — remote browsers, device farms, cloud providers",
  "tools": [
    {
      "name": "run_e2e_tests",
      "description": "Execute E2E tests on remote browser/device infrastructure",
      "input": { "workspace_path": "string", "platform": "string", "browser": "string|null" },
      "output": { "results": "object", "screenshots": "array", "videos": "array" }
    },
    {
      "name": "get_test_history",
      "description": "Get historical pass/fail data for specific tests (flaky detection)",
      "input": { "test_ids": "array" },
      "output": { "history": "array" }
    }
  ],
  "transport": "stdio",
  "command": "python",
  "args": ["mcps/test-infrastructure/server.py"]
}
```

> **Why deferred from P1:** In P1, agents run tests directly via shell commands (`npm test`, `pytest`). This MCP adds value in P2+ when we need Selenium Grid, device farms, BrowserStack — infrastructure that requires configuration and session management beyond a shell command.

#### 6.3.2 knowledge-base MCP (P2)

```json
{
  "name": "knowledge-base",
  "description": "QA Knowledge Base — RAG-powered retrieval of standards, patterns, and domain knowledge",
  "tools": [
    {
      "name": "search_patterns",
      "description": "Search for relevant automation patterns and standards",
      "input": { "query": "string", "category": "standards|patterns|domain|history" },
      "output": { "results": "array", "relevance_scores": "array" }
    },
    {
      "name": "get_defect_history",
      "description": "Get historical defect data for a component or file",
      "input": { "component": "string" },
      "output": { "defects": "array", "common_patterns": "array" }
    }
  ],
  "transport": "stdio",
  "command": "python",
  "args": ["mcps/knowledge-base/server.py"]
}
```

### 6.4 MCP Configuration in WORKFLOW.md

```yaml
# WORKFLOW.md
mcps:
  coverage-service:
    enabled: true
    config:
      tool: auto-detect   # or explicit: istanbul | jacoco | coverage.py
      threshold: 80

  sast-scanner:
    enabled: true
    config:
      engines: [semgrep, gitleaks]
      severity_filter: [critical, high]

  tracker-bridge:
    enabled: true
    # Config from environment variables

  test-infrastructure:
    enabled: false    # P2 feature

  knowledge-base:
    enabled: false    # P2 feature
```

## 7. Plugin Design

### 7.1 Plugin Architecture

Plugins are distributable packages that bundle skills + hooks + MCPs + rules into installable units. Inspired by everything-claude-code's `.claude-plugin/plugin.json` pattern.

```
symphony-qa-<name>/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── skills/
│   └── <skill-name>/
│       └── SKILL.md
├── hooks/
│   └── hooks.json
├── mcps/
│   └── <mcp-name>/
│       ├── server.py
│       └── mcp.json
├── agents/
│   └── <agent-name>.md       # Agent role definitions (if plugin defines agents)
├── rules/
│   └── <rule-file>.md        # CLAUDE.md-style guidelines
├── knowledge/
│   └── <domain>/             # Domain knowledge files
├── evals/
│   └── <test-cases>.yaml     # Plugin-level eval test cases
└── README.md
```

### 7.2 plugin.json Schema

```json
{
  "name": "symphony-qa-core",
  "version": "1.0.0",
  "description": "Core QA skills for Symphony orchestrator — evaluation, coverage, TDD enforcement",
  "author": "QA CoE",
  "license": "proprietary",

  "skills": [
    "skills/parsing-requirements",
    "skills/test-driven-development",
    "skills/analyzing-coverage",
    "skills/validating-acceptance-criteria",
    "skills/classifying-test-failures",
    "skills/generating-qa-report"
  ],

  "hooks": "hooks/hooks.json",

  "mcpServers": [
    { "name": "coverage-service", "config": "mcps/coverage-service/mcp.json" },
    { "name": "tracker-bridge", "config": "mcps/tracker-bridge/mcp.json" }
  ],

  "agents": [
    "agents/qa-evaluator.md"
  ],

  "rules": [
    "rules/qa-standards.md",
    "rules/tdd-rules.md"
  ],

  "compatibility": {
    "symphony": ">=1.0.0",
    "copilot-cli": ">=2.0.0"
  },

  "config_schema": {
    "hook_profile": { "type": "string", "enum": ["minimal", "standard", "strict"], "default": "standard" },
    "coverage_threshold": { "type": "number", "default": 80 },
    "gate_policy": { "type": "string", "enum": ["strict", "advisory"], "default": "advisory" }
  }
}
```

### 7.3 Plugin Catalog

#### symphony-qa-core (P1)

**Contents:** Core QA skills required by every team.

| Component | Included |
|-----------|----------|
| **Skills** | parsing-requirements, test-driven-development, analyzing-coverage, validating-acceptance-criteria, classifying-test-failures, generating-qa-report |
| **Hooks** | load-qa-context, inject-tdd-rules, load-acceptance-criteria, block-commit-if-tests-fail, typecheck-on-edit, generate-qa-summary, update-workpad |
| **MCPs** | coverage-service, tracker-bridge |
| **Agents** | qa-evaluator.md |
| **Rules** | qa-standards.md, tdd-rules.md |

#### symphony-qa-web (P2)

| Component | Included |
|-----------|----------|
| **Skills** | generating-playwright-tests, generating-api-tests, generating-perf-tests, generating-test-data (web schemas) |
| **MCPs** | test-infrastructure (Selenium Grid / BrowserStack config) |
| **Knowledge** | Web testing patterns, Playwright POM patterns, API testing patterns |
| **Dependencies** | symphony-qa-core |

#### symphony-qa-mobile (P2)

| Component | Included |
|-----------|----------|
| **Skills** | generating-mobile-tests (iOS + Android) |
| **MCPs** | test-infrastructure (device farm config) |
| **Knowledge** | Mobile testing patterns, Appium patterns, device matrix |
| **Dependencies** | symphony-qa-core |

#### symphony-qa-security (P2)

| Component | Included |
|-----------|----------|
| **Skills** | (security review guidance) |
| **Hooks** | security-scan-pre-commit (strict profile), lint-before-commit |
| **MCPs** | sast-scanner |
| **Agents** | security-agent.md |
| **Rules** | security-standards.md |
| **Dependencies** | symphony-qa-core |

#### symphony-qa-advanced (P3)

| Component | Included |
|-----------|----------|
| **Skills** | scoring-risk, reviewing-code-quality, selecting-regressions, healing-broken-tests, analyzing-defects |
| **MCPs** | knowledge-base |
| **Knowledge** | Historical defect patterns, component risk maps |
| **Dependencies** | symphony-qa-core |

### 7.4 Plugin Installation & Distribution

```
# Install plugin (copies to .github/symphony-plugins/)
symphony plugin install symphony-qa-core

# Configure plugin for project
symphony plugin configure symphony-qa-core \
  --hook-profile=standard \
  --coverage-threshold=80 \
  --gate-policy=advisory

# List installed plugins
symphony plugin list

# Update plugin
symphony plugin update symphony-qa-core

# Plugin resolution order (later overrides earlier):
#   1. Plugin defaults (plugin.json config_schema defaults)
#   2. Global config (symphony.yml)
#   3. Project config (WORKFLOW.md)
#   4. Environment variables
```

### 7.5 Plugin Versioning & Governance

Aligns with orchestrator spec §26 AI Governance Integration:

1. New plugin versions require QA CoE review before distribution
2. AI Governance approves agent.md files within plugins (same workflow as §26.2)
3. Plugin versions are pinned in WORKFLOW.md to prevent breaking changes:

```yaml
# WORKFLOW.md
plugins:
  symphony-qa-core: "1.2.0"     # Pinned version
  symphony-qa-web: "~1.0"       # Compatible minor versions
  symphony-qa-security: "^1.0"  # Compatible major versions
```

## 8. Rules Design

Rules are CLAUDE.md-style guidelines injected into agent context. They complement skills (procedural) with principles (declarative).

### 8.1 Rule Categories

```
rules/
├── qa-standards.md              # Universal QA principles
├── tdd-rules.md                 # TDD enforcement rules
├── security-standards.md        # Security coding standards (P2)
├── review-guidelines.md         # Code review standards (P3)
└── platform/
    ├── typescript.md            # TypeScript-specific rules (P2)
    ├── python.md                # Python-specific rules (P2)
    ├── java.md                  # Java-specific rules (P2)
    └── go.md                    # Go-specific rules (P2)
```

### 8.2 qa-standards.md (P1)

```markdown
# QA Standards

## Test Quality
- Every public function must have at least one test
- Tests must be independent — no shared mutable state between tests
- Test names must describe the behavior being tested, not the implementation
- Prefer arrange-act-assert structure

## Coverage
- New code must have ≥80% line coverage (project default, configurable)
- Coverage of error handling paths is mandatory for Critical/High severity components
- Coverage below threshold blocks merge in strict profile

## Acceptance Criteria
- Every AC must be traceable to at least one test
- "Untestable" ACs must be flagged for human review, not silently skipped

## Test Data
- Never use real customer data in tests
- Synthetic data must have realistic distribution (not all edge cases, not all happy paths)
- PII fields must use obviously fake data (e.g., "Jane Doe", "555-0100")
```

### 8.3 tdd-rules.md (P1)

```markdown
# TDD Rules

## Cycle
1. Write a failing test before writing implementation code
2. Run the test and verify it fails for the expected reason
3. Write the minimum code to make the test pass
4. Run all tests and verify they pass
5. Refactor while keeping all tests green

## Enforcement
- Implementation files must not be created before their corresponding test files
- A commit that adds implementation without tests is a quality violation
- If you didn't watch the test fail, you don't know if it tests the right thing

## Exceptions
- Configuration files (YAML, JSON, env) do not require unit tests
- Database migrations do not require unit tests (integration tests cover them)
- Third-party library wrappers may use integration tests instead of unit tests
```

## 9. Integration: How Components Work Together

### 9.1 Pre-Coding Flow

```
Issue arrives (Todo state)
    │
    ▼
[Hook: SessionStart] load-qa-context → inject project QA standards
[Hook: SessionStart] load-acceptance-criteria → fetch AC from tracker
    │
    ▼
Requirements Analyst Agent activates
    │
    └── [Skill] parsing-requirements → structured AC + ambiguity flags
    │
    ▼
Developer Agent activates
    │
    ├── [Hook: SessionStart] inject-tdd-rules → TDD enforcement active
    └── [Skill] test-driven-development → test cases from AC → failing test skeletons
```

### 9.2 During-Coding Flow

```
Developer Agent implementing (TDD cycle active)
    │
    ├── Agent edits file
    │   ├── [Hook: PostToolUse] typecheck-on-edit → type errors reported
    │   ├── [Hook: PostToolUse] lint-on-edit → lint violations reported (strict)
    │   └── [Hook: PostToolUse] coverage-delta-check → coverage delta reported (strict)
    │
    ├── Agent runs git commit
    │   ├── [Hook: PreToolUse] block-commit-if-tests-fail → blocks if tests red
    │   ├── [Hook: PreToolUse] security-scan-pre-commit → blocks if secrets found (strict)
    │   └── [Hook: PreToolUse] lint-before-commit → warns on lint violations (strict)
    │
    └── [Skill: test-driven-development] monitors Red→Green→Refactor rhythm
```

### 9.3 Post-Coding Flow

```
Developer Agent completes → orchestrator advances to QA Evaluation phase
    │
    ▼
QA Evaluator Agent activates (cross-model: Gemini 3 Pro)
    │
    ├── Dimension 1: Pass Rate
    │   ├── Agent runs project test command (shell)
    │   └── [Skill: classifying-test-failures] classify failures → real-bug/flaky/env
    │
    ├── Dimension 2: Coverage
    │   ├── [MCP: coverage-service] run_coverage → coverage data
    │   └── [Skill: analyzing-coverage] interpret gaps, assess risk, compare to threshold
    │
    ├── Dimension 3: Acceptance
    │   └── [Skill: validating-acceptance-criteria] map AC to test evidence
    │
    ├── [Skill: generating-qa-report] aggregate into QA Report
    ├── [MCP: tracker-bridge] update_workpad with report
    └── [MCP: tracker-bridge] post_qa_verdict (PASS/FAIL)
    │
    ▼
If PASS → Code Reviewer Agent activates
    │
    └── (P3: [Skill: reviewing-code-quality] two-stage review)
    │
    ▼
If PASS → Security Agent activates (parallel, event-triggered on pr.created)
    │
    └── [MCP: sast-scanner] scan_project + scan_dependencies + scan_secrets
    │
    ▼
[Hook: Stop] generate-qa-summary → final QA status
[Hook: Stop] update-workpad → write to tracker
```

### 9.4 Component Interaction Matrix

| Component | Invoked By | Invokes | Data Flow |
|-----------|-----------|---------|-----------|
| **Skills** | Agent (explicit invocation) | Scripts, other skills | Input→Output via JSON |
| **Hooks** | Orchestrator (event-driven, automatic) | Shell scripts | Env vars → stdout/stderr → agent context |
| **MCPs** | Agent (tool call) or Skills (via script) | External services | Tool input → tool output JSON |
| **Plugins** | Orchestrator (install-time registration) | Registers skills + hooks + MCPs | plugin.json manifest |

## 10. Eval Framework for Skills

Inspired by anthropics/skills 4-mode eval system (create → eval → improve → benchmark).

### 10.1 Eval Structure per Skill

```yaml
# evals/test-prompts.yaml
test_cases:
  - id: "tc-001"
    description: "Simple password validation feature"
    input:
      issue_description: "Add password validation: 8-64 chars, at least one number"
      acceptance_criteria:
        - "Password must be 8-64 characters"
        - "Password must contain at least one number"
    expected:
      verdict: "PASS"
      test_count_min: 4
      coverage_min: 80

  - id: "tc-002"
    description: "Complex multi-service feature with missing AC"
    input:
      issue_description: "Implement payment retry logic"
      acceptance_criteria:
        - "Should retry failed payments"
    expected:
      ambiguity_flags: ["'Should retry' — how many times?", "No timeout specified"]
      verdict: "FAIL"
      reason_contains: "ambiguous"
```

### 10.2 Eval Execution

```
symphony skill eval <skill-name>
    │
    ├── Load test cases from evals/test-prompts.yaml
    ├── For each test case:
    │   ├── Spawn executor subagent with skill active
    │   ├── Spawn grader subagent to evaluate output against assertions
    │   └── Record: pass/fail, execution time, token usage
    ├── Aggregate results
    └── Report: pass rate, avg tokens, avg time, failing cases
```

## 11. Phased Delivery

### Phase 1 (P1): Core QA Ecosystem — Quick Win

**Goal:** All components needed for demoable QA verification loop.

| Component | Deliverables |
|-----------|-------------|
| **Plugin** | symphony-qa-core v1.0 |
| **Skills** | parsing-requirements, test-driven-development (extend existing), analyzing-coverage, validating-acceptance-criteria, classifying-test-failures, generating-qa-report |
| **Hooks** | load-qa-context, inject-tdd-rules, load-acceptance-criteria, block-commit-if-tests-fail, typecheck-on-edit, generate-qa-summary, update-workpad |
| **MCPs** | coverage-service (auto-detect backend), tracker-bridge (Linear + JIRA) |
| **Rules** | qa-standards.md, tdd-rules.md |
| **Evals** | Test cases for each P1 skill |

**Not in P1:** Test generation skills, security plugin, knowledge base MCP, test-infrastructure MCP, self-healing, smart regression, risk scoring.

### Phase 2 (P2): Generation & Platform Expansion

| Component | Deliverables |
|-----------|-------------|
| **Plugins** | symphony-qa-web v1.0, symphony-qa-mobile v1.0, symphony-qa-security v1.0 |
| **Skills** | generating-playwright-tests, generating-api-tests, generating-perf-tests, generating-mobile-tests, generating-test-data |
| **Hooks** | security-scan-pre-commit, lint-on-edit, lint-before-commit, coverage-delta-check |
| **MCPs** | sast-scanner, knowledge-base (initial), test-infrastructure (Selenium Grid, device farm) |
| **Rules** | security-standards.md, platform/ rules |

### Phase 3 (P3): Advanced & Self-Improving

| Component | Deliverables |
|-----------|-------------|
| **Plugin** | symphony-qa-advanced v1.0 |
| **Skills** | scoring-risk, reviewing-code-quality, selecting-regressions, healing-broken-tests, analyzing-defects |
| **MCPs** | knowledge-base (full: RAG + history) |
| **Hooks** | All strict-profile hooks, custom team hooks |

## 12. Mapping to Existing Specs

### 12.1 Skill Name Mapping (SKILL.md → Python class)

The SKILL.md directory names use gerund convention (Anthropic/Superpowers standard). The QA agent spec and orchestrator spec use agent-noun naming suitable for Python classes. This table maps between them:

| SKILL.md Name | Python Class Name (qa-agent) | Spec Reference |
|---|---|---|
| `parsing-requirements` | `RequirementParser` | QA Agent §5.1 requirement-parser |
| `test-driven-development` | `TddEnforcer` | Orchestrator §4.3, QA Ecosystem §4.5.2 |
| `analyzing-coverage` | `CoverageAnalyzer` | QA Agent §5.1 coverage-analyzer |
| `validating-acceptance-criteria` | `AcceptanceValidator` | QA Agent §5.1 acceptance-validator |
| `classifying-test-failures` | `FailureClassifier` | QA Agent §5.1 failure-classifier |
| `generating-qa-report` | `QaReporter` | QA Agent §5.1 qa-reporter |

### 12.2 Orchestrator Spec Cross-References

| Orchestrator Section | This Spec Coverage |
|---------------------|-------------------|
| §4 Agent Role System | §7.2 Plugins define agent.md files; §8 Rules provide agent guidelines |
| §5 Multi-Phase Orchestration | §9 Integration flows show skill/hook/MCP usage per phase |
| §6.2 Prompt Assembly | §4.3 L1→L2→L3 skill loading aligns with context engineering principles |
| §7 Quality Gate Engine | §4.5.6 generating-qa-report produces gate input; §5 hooks enforce at tool boundaries |
| §8 Tracker Adapter | §6.2.3 tracker-bridge MCP wraps TrackerAdapter |
| §17 Delivery Phases | §11 aligned: P1 = core eval, P2 = generation + platforms, P3 = advanced |
| §26 AI Governance | §7.5 Plugin versioning + governance approval workflow |
| §27 Maturity Model | §5.3 Hook profiles map to maturity levels |

### 12.3 QA Agent Spec Cross-References

| QA Agent Section | This Spec Coverage |
|-----------------|-------------------|
| §3.1 Pre-coding | §4.5.1 parsing-requirements, §4.5.2 test-driven-development (test case generation phase) |
| §3.2 During-coding | §4.5.2 test-driven-development (enforcement phase), §5 PostToolUse hooks |
| §3.3 Post-coding | §4.5.3–4.5.6 Post-coding skills, §5 Stop hooks |
| §4 Evaluation Dimensions | §4.5.3–4.5.5 One skill per dimension + failure classifier |
| §5.1 Skill Categories | §4.5–4.7 Full skill catalog with standard structure |
| §5.2 Skill Standard Structure | §4.1–4.2 Enhanced with evals/, aligned with anthropics/skills format |
| §6 Knowledge Base | §6.3.2 knowledge-base MCP, skill-level knowledge/ dirs |
| §10 M1–M8 Mapping | §4.5–4.7 Each M mapped to specific skills |

### 12.4 Removed Components (Audit Trail)

The following components from the v1 spec were removed or reclassified during the design audit:

| Component | Disposition | Reason |
|-----------|-----------|--------|
| `test-runner` skill | **Removed** | Running `npm test`/`pytest` is a shell command, not QA expertise. Agent runs tests directly. `classifying-test-failures` handles the interesting part. |
| `test-case-matrix` skill | **Merged** into `test-driven-development` | Inseparable step in TDD workflow. Never used independently. |
| `test-skeleton-gen` skill | **Merged** into `test-driven-development` | Same — TDD Red phase, not a standalone skill. |
| `coverage-guard` skill | **Reclassified** as hook `coverage-delta-check` | Deterministic command (run coverage, compare). No LLM judgment needed. |
| `lint-on-edit` skill | **Reclassified** as hook only | Running a linter is a shell command, not QA expertise. |
| `typecheck-on-edit` skill | **Reclassified** as hook only | Running `tsc --noEmit` is a shell command. |
| `security-scan-incremental` skill | **Reclassified** as hook `security-scan-pre-commit` | Pattern matching for secrets/injection is deterministic. |
| `risk-scorer` skill | **Deferred** from P1 to P3 (`scoring-risk`) | Needs historical defect data from Knowledge Base MCP (P2). No consumer in P1. |
| `test-infrastructure` MCP | **Deferred** from P1 to P2 | P1 agents run tests via shell. MCP needed for Selenium Grid/device farms (P2). |

## 13. Open Design Decisions

1. **Hook execution model** — Should hooks run in-process (Python subprocess) or as external processes? In-process is faster but shares the agent's resource limits. External is more isolated but adds IPC overhead.

2. **Skill versioning granularity** — Should individual skills have independent versions, or does the plugin version cover all contained skills? Independent versions enable finer updates but complicate dependency management.

3. **MCP transport** — stdio (local process) vs HTTP (remote service) for each MCP. P1 uses stdio for simplicity. P3 may need HTTP for shared infrastructure (e.g., one SAST scanner instance serving multiple agents).

4. **Hook debounce strategy** — For PostToolUse hooks like `coverage-delta-check`, how long should the debounce window be? Too short = excessive runs; too long = delayed feedback.

5. **Cross-model skill compatibility** — Skills are currently model-agnostic (plain SKILL.md). Should skills have model-specific variants (e.g., a GPT-optimized prompt vs Claude-optimized prompt) for the cross-model evaluation strategy?

6. **Knowledge Base vector DB selection** — ChromaDB (lightweight, P2 suitable) vs Milvus/Pinecone (production-grade, P3). Decision needed before P2 implementation.

7. **Plugin marketplace** — Should Symphony have an internal plugin marketplace for teams to share custom plugins? Or is central CoE distribution sufficient?
