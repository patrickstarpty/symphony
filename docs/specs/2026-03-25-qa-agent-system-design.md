# QA Agent System — Design Spec

**Date:** 2026-03-25
**Author:** Patrick (QA CoE)
**Status:** Approved (design)

---

## 1. Problem Statement

The company is undergoing AI Native SDLC transformation. AI Governance has selected Copilot CLI as the autonomous coding agent operating within a harness. Currently there is no standardized QA process for AI-generated code. Business teams have varying automation maturity. QA CoE needs to:

1. Ensure AI-generated code meets quality standards
2. Provide QA capabilities as a platform for business teams
3. Establish QA as a first-class role in the agent orchestration architecture

## 2. Architecture: Hybrid (Embedded Agent + Service)

Two layers with clear separation of concerns.

### 2.1 QA Agent (Decision Layer)

Embedded within the orchestrator (Symphony Python). Responsibilities:

- Understand issue context and Coding Agent intent
- Decide what types of testing are needed
- Call QA Service APIs for execution
- Aggregate results, make pass/fail verdict
- Controlled by harness policy (WORKFLOW.md)

### 2.2 QA Service (Execution Layer)

Independently deployed FastAPI service. Responsibilities:

- Execute test generation, running, and reporting
- Manage Skill Hub and Knowledge Base
- Expose framework-agnostic REST API
- Controlled by QA CoE

### 2.3 API Surface

```
QA Service (FastAPI)
  POST /evaluate     — Full evaluation: dispatch skills, collect 3-dimension results, return report
  POST /generate     — Generate test scripts for target platform
  POST /execute      — Run test suite, return results
  GET  /report       — Query historical evaluation reports
```

### 2.4 Framework-Agnostic Design

QA Service does not know or care what orchestrator calls it. QA Agent is a thin adapter per orchestrator:

| Orchestrator | QA Agent Implementation |
|-------------|------------------------|
| Symphony Python | Built-in Evaluator module |
| Claude Code | Claude Code skill calling QA Service API |
| CI/CD Pipeline | Direct API call from pipeline step |
| Manual | CLI tool or web UI |

## 3. QA Agent Intervention Points

### 3.1 Pre-coding (Left-shift)

- Analyze requirements, generate test skeleton (M1 TDD)
- Detect requirement ambiguity (M2)
- Negotiate acceptance criteria with Coding Agent

### 3.2 During coding (Companion)

- Monitor TDD rhythm (Red → Green → Refactor)
- Incremental check: new code must have test coverage
- Static analysis (lint, type check, security scan)

### 3.3 Post-coding (Evaluation)

- Generate missing tests (M3)
- Run full test suite + regression tests (M6)
- Verify functional completeness against requirements
- Score on three dimensions, generate report
- Verdict: pass → Human Review / fail → Rework with reason

## 4. Evaluation Dimensions

| Dimension | What it measures | Failure condition |
|-----------|-----------------|-------------------|
| **Pass Rate** | All tests passing (including regression). Sub-capability: distinguish real bug vs flaky vs env issue. P1 flaky detection: retry failed tests up to 2 times; P3: historical pass rate analysis via defect-analyzer | Any real test failure |
| **Coverage** | Code coverage + requirement coverage | Below threshold (P1 default: 80% line coverage; P3: dynamic per M4 risk model) |
| **Acceptance** | Implementation satisfies acceptance criteria from issue | Any AC not met |

Verdict logic:

```
Pass Rate < 100% (excluding flaky/env) → FAIL + failure analysis
Coverage < threshold                    → FAIL + missing scenario suggestions
Acceptance not satisfied                → FAIL + unmet AC list
All pass                                → PASS → transition to Human Review
```

## 5. Skill Hub

### 5.1 Skill Categories

```
skill-hub/
├─ analysis/
│   ├─ requirement-parser/        — M2: Requirement parsing + ambiguity detection
│   ├─ change-impact/             — M6: Change impact analysis
│   └─ risk-scorer/               — M4: Risk scoring
│
├─ generation/                    — Per-platform, not unified
│   ├─ playwright-gen/            — M3: Web test script generation
│   ├─ appium-gen/                — M3: Mobile test script generation (iOS/Android)
│   ├─ api-test-gen/              — M3: API test generation
│   ├─ k6-gen/                    — M3: Performance test generation
│   ├─ test-case-matrix/          — M2: Requirement → test case matrix
│   ├─ test-data-gen/             — M7: Synthetic test data generation
│   └─ cobol-boundary-test/       — AS400/COBOL integration boundary test generation (P3)
│
├─ execution/
│   ├─ test-runner/               — Unified test execution dispatch
│   ├─ regression-selector/       — M6: Smart regression selection
│   └─ self-healer/               — M5: Failure classification + auto-repair
│
└─ evaluation/
    ├─ coverage-analyzer/         — Coverage analysis against thresholds
    ├─ acceptance-validator/       — AC verification against requirements
    ├─ qa-reporter/               — Aggregate results into structured QA report
    ├─ failure-classifier/        — Distinguish real bug vs flaky vs env issue
    └─ defect-analyzer/           — M8: Defect root cause analysis
```

### 5.2 Skill Standard Structure

```
<skill-name>/
├─ skill.yaml          — Metadata: name, version, input/output schema, dependencies
├─ prompt.md           — LLM prompt template
├─ knowledge/          — Skill-specific knowledge files
├─ templates/          — Code templates / scaffolding
└─ tests/              — Skill's own tests
```

## 6. Knowledge Base

```
knowledge-base/
├─ standards/          — CoE coding standards, naming conventions, POM structure
├─ patterns/           — Automation patterns per platform (Page Object, Screenplay...)
├─ domain/             — Insurance domain knowledge
│   ├─ new-policy/     — 投保流程 (policy application workflow)
│   ├─ underwriting/   — 核保流程 (underwriting rules and workflow)
│   └─ claims/         — 理赔流程 (claims processing workflow)
└─ history/            — Historical defect patterns, common team mistakes (M8 input)
```

Indexed via RAG (vector embeddings). Test generation references existing code patterns and team standards to ensure style consistency.

## 7. Copilot CLI Integration

### 7.1 Phase 1 (P1) / Phase 2 (P2): Same-session dual role

QA evaluation defined as a mandatory phase in WORKFLOW.md prompt template. Copilot CLI codes first, then evaluates its own work within the same session.

**Why self-evaluation is acceptable for P1:** Pass Rate and Coverage are objective, deterministic checks — test pass/fail and coverage percentages are facts regardless of who runs them. Acceptance validation is the most vulnerable to self-evaluation bias, but P1 treats it as a structured AC checklist comparison rather than subjective judgment.

**P1 execution flow:**

```
Copilot CLI session (same session, dual role):
  1. Read issue from Linear (requirements + AC)
  2. Code implementation (turns 1-N)
  3. Enter QA Evaluation Phase:
     a. Shell out: run project test command (e.g. `make test`)
     b. Shell out: run coverage tool (e.g. `make coverage`)
     c. Parse test results → Pass Rate dimension
     d. Parse coverage output → Coverage dimension (threshold: 80% default)
     e. Compare AC checklist against code changes → Acceptance dimension
     f. Write structured QA Report to issue workpad (via Linear GraphQL tool)
     g. Verdict: PASS → transition to Human Review
                 FAIL → transition to Rework with failure reason
```

```yaml
# WORKFLOW.md excerpt
---
agent:
  qa_evaluation: true
  qa_gate_policy: strict    # strict = must pass | advisory = informational
---

# Prompt template includes QA Evaluation Phase:
# - Run tests, check coverage, verify AC
# - Generate QA Report in workpad
# - Verdict determines issue state transition
```

### 7.2 P3: Independent Agent Session

Orchestrator spawns a separate Copilot CLI session for QA evaluation. Independent context eliminates self-evaluation bias.

```
Session A (Coding Agent): writes code → completes
    ↓
Orchestrator: creates new workspace snapshot
    ↓
Session B (QA Agent): evaluates Session A output with fresh context
```

## 8. Phased Delivery

### Phase 1: Quick Win

**Goal:** Demoable PR evaluation loop.

**Deliverables:**
- QA Evaluator embedded in WORKFLOW.md (same-session dual role)
- 5 core skills: test-runner, coverage-analyzer, acceptance-validator, qa-reporter, failure-classifier
- Structured QA Report in issue workpad
- Auto state transition: pass → Human Review, fail → Rework

**Not in scope:** Test generation, self-healing, smart regression, independent QA Service deployment.

**Demo scenario:**
1. Create Linear issue (e.g. "Add password validation to login form")
2. Orchestrator picks up issue → Copilot CLI codes
3. Coding complete → QA Evaluation Phase triggers
4. Tests run, coverage checked, AC verified
5. QA Report appears in workpad
6. Issue auto-transitions based on verdict

### Phase 2: Test Generation

**Goal:** Business teams can generate multi-platform test scripts.

**Deliverables:**
- Per-platform generation skills: playwright-gen, appium-gen, api-test-gen, k6-gen
- Knowledge Base with CoE standards + insurance domain knowledge
- QA Service begins independent deployment (FastAPI)
- test-case-matrix skill (requirement → structured test cases)
- test-data-gen skill with insurance domain awareness

### Phase 3: Full Platform

**Goal:** Complete QA-as-a-Platform.

**Deliverables:**
- Independent QA Agent Session (separate Copilot CLI)
- Self-healing automation (M5)
- Smart regression selection (M6)
- Defect root cause analysis (M8)
- Risk-based prioritization (M4)
- CI/CD integration (Jenkins / GitHub Actions / GitLab CI)
- Quality metrics dashboard
- Full Knowledge Base with historical defect patterns

## 9. Tech Stack

| Component | Technology |
|-----------|-----------|
| Orchestrator | Symphony (Python rewrite) |
| Coding Agent | Copilot CLI (via app-server JSONL bridge) |
| QA Service | FastAPI (Python) |
| Knowledge Base | RAG with vector embeddings |
| Test Platforms | Playwright, Appium, XCTest, UIAutomator2, K6, Locust, JMeter |
| Issue Tracker | Linear (swappable via adapter, future: JIRA) |
| CI/CD | Jenkins / GitHub Actions / GitLab CI |

## 10. M1-M8 Mapping

| Measure | Phase | Implementation |
|---------|-------|---------------|
| M1 TDD-driven SDLC | P2 | tdd-skeleton-gen skill: test skeleton generation from requirements |
| M2 Requirement → test case | P2 | requirement-parser + test-case-matrix skills |
| M3 Code gen with skills | P2 | Per-platform generation skills + Knowledge Base |
| M4 Risk-based prioritization | P3 | risk-scorer skill + dynamic coverage thresholds |
| M5 Self-healing automation | P3 | self-healer skill + auto-fix loop |
| M6 Regression intelligence | P3 | change-impact + regression-selector skills |
| M7 Simulation test data | P2 | test-data-gen skill with domain knowledge |
| M8 Defect root cause | P3 | defect-analyzer skill + history knowledge base |

## 11. Organizational Model

| Role | Responsibility |
|------|---------------|
| **QA CoE** | Maintains QA Service, Skill Hub, Knowledge Base. Defines quality standards and evaluation criteria. |
| **AI Governance** | Defines Copilot CLI policies, harness standards. QA CoE provides Evaluator component for their harness. |
| **Business Teams** | Consume QA capabilities via orchestrator integration or direct API calls. Contribute domain knowledge. |

## 12. Security & Compliance

- **QA Service API auth:** Service-to-service JWT tokens. Orchestrator and CI/CD pipelines authenticate via signed tokens issued by internal identity provider.
- **RBAC:** `/evaluate` and `/execute` require `qa:write` role. `/report` requires `qa:read`. Skill Hub management requires `qa:admin`.
- **Test data handling:** Insurance data (PII, health, financial) must never appear in test scripts or reports. test-data-gen skill generates synthetic data with realistic distribution but no real customer data. Data masking compliant with PDPA/GDPR.
- **Workspace isolation:** QA Agent operates within the same workspace sandbox as Coding Agent (PathSafety enforcement from Symphony).

## 13. Failure Modes & Recovery

| Failure | Impact | Recovery |
|---------|--------|----------|
| QA Service unavailable | Cannot evaluate | `strict` policy: block merge, retry with backoff. `advisory` policy: skip evaluation, flag in workpad |
| Individual skill failure | Partial report | Report available dimensions, mark failed dimension as "inconclusive", do not auto-PASS |
| Copilot CLI timeout mid-evaluation | Incomplete QA phase | Orchestrator retries with exponential backoff (inherits Symphony retry logic) |
| Flaky test false positive | Incorrect FAIL verdict | Retry failed tests up to 2 times before reporting as failure |
| Coverage tool unavailable | Cannot measure coverage | Mark Coverage dimension as "inconclusive", evaluate on remaining dimensions |

## 14. Observability

- **Structured logging:** All QA Agent actions logged with `issue_id`, `session_id`, `skill_name`, `dimension`, `verdict`
- **Metrics:** Evaluation duration, skill execution time, pass/fail/inconclusive rates, coverage trends
- **Tracing:** Distributed trace across Orchestrator → QA Agent → QA Service → Skill execution
- **Dashboard:** P1: logs only. P3: Quality metrics dashboard with historical trends

## 15. Team Onboarding Profiles

| Profile | `qa_gate_policy` | Description |
|---------|------------------|-------------|
| **Strict** | `strict` | Must pass all 3 dimensions. For mature teams and critical systems (core, underwriting) |
| **Advisory** | `advisory` | QA report generated but does not block merge. For teams ramping up automation |
| **Custom** | per-dimension config | e.g. Pass Rate = strict, Coverage = advisory. For teams in transition |

Policy configured per project in WORKFLOW.md. CoE sets defaults, business teams can request adjustments with CoE approval.

## 16. Open Design Decisions

1. **QA Agent model selection** — Same Copilot CLI, or could a different model (e.g. Claude) serve as QA evaluator for cross-model objectivity?
2. **Knowledge Base storage** — Dedicated vector DB (Milvus/Pinecone) or lightweight solution (ChromaDB/FAISS) for P1?
3. **AS400/COBOL test strategy** — What can AI realistically do here? Integration boundary testing vs green-screen automation?
4. **Skill versioning** — How to manage skill versions across teams with different maturity?
5. **Metrics baseline** — What are current pass rate / coverage / defect escape rate numbers to measure improvement against?
