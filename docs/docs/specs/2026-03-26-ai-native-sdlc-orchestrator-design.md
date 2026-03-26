# AI Native SDLC Orchestrator — Design Spec

**Date:** 2026-03-26
**Author:** Patrick (QA CoE)
**Status:** Active
**Sub-specs:** [QA Agent System](2026-03-25-qa-agent-system-design.md)

---

## 1. Problem Statement

The company is transitioning to AI Native SDLC development. AI Governance has selected Copilot CLI as the autonomous coding agent. Currently:

1. No standardized orchestration — teams run Copilot CLI ad-hoc with varying maturity
2. No multi-agent coordination — coding, testing, and review happen in silos
3. No quality gates enforced at orchestration level — quality is an afterthought
4. No unified skill ecosystem — teams build one-off prompts instead of reusable skills
5. No observability — no visibility into agent efficiency, cost, or quality metrics

This spec defines **Symphony** — a Python-based SDLC orchestrator that receives work from issue trackers, routes it to specialized agent roles, enforces quality gates, and drives issues through the full development lifecycle.

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Symphony Orchestrator                     │
│                                                                  │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────────────┐   │
│  │  Tracker    │  │  Agent Role  │  │  Quality Gate Engine  │   │
│  │  Adapter    │  │  Router      │  │                       │   │
│  │ (JIRA/     │  │              │  │  Configurable per-    │   │
│  │  Linear)   │  │  issue →     │  │  state gates with     │   │
│  └─────┬──────┘  │  agent.md    │  │  strict/advisory      │   │
│        │         └──────┬───────┘  └───────────┬───────────┘   │
│        │                │                      │                │
│  ┌─────▼────────────────▼──────────────────────▼───────────┐   │
│  │                   Coordination Layer                     │   │
│  │  Polling │ Dispatch │ Concurrency │ Retry │ Reconcile   │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │                    Execution Layer                       │   │
│  │                                                          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │   │
│  │  │Developer│ │QA Eval  │ │Code Rev │ │DevOps   │ ...  │   │
│  │  │Agent    │ │Agent    │ │Agent    │ │Agent    │      │   │
│  │  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘      │   │
│  │       │           │           │           │             │   │
│  │       └───────────┴───────────┴───────────┘             │   │
│  │                       │                                  │   │
│  │              Copilot CLI (JSONL bridge)                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐   │
│  │                  Shared Infrastructure                    │   │
│  │  Skill Hub │ Knowledge Base │ Event Bus │ Observability  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.1 Seven Layers

| Layer | Responsibility | Inherited from Elixir | New |
|-------|---------------|----------------------|-----|
| **Policy** | WORKFLOW.md: config + prompt templates | Yes | agent.md role definitions |
| **Configuration** | Typed getters, env resolution, hot-reload | Yes | Quality gate config |
| **Integration** | Tracker adapter (Linear/JIRA), normalized issue model | Yes | JIRA adapter |
| **Coordination** | Polling, dispatch, concurrency, retry, reconciliation | Yes | Multi-phase orchestration |
| **Execution** | Workspace isolation, agent runner, Copilot CLI bridge | Yes | Agent Role Router, multi-agent per issue |
| **Quality** | Quality gate enforcement | — | New layer |
| **Observability** | Logging, metrics, tracing, dashboard | Partial | Full metrics + cost tracking |

## 3. Core Domain Model

### 3.1 Issue (Normalized from Tracker)

```python
class Issue:
    id: str                    # Tracker-internal stable ID
    identifier: str            # Human-readable key (e.g. PROJ-123)
    title: str
    description: str
    state: str                 # Current tracker state
    priority: str              # critical | high | medium | low (normalized from tracker)
    labels: list[str]
    issue_type: str | None         # epic | story | task | bug | incident (normalized)
    acceptance_criteria: list[str]   # Extracted from description
    blocked_by: list[str]            # Dependency blocking
    branch_name: str | None
    url: str
    created_at: datetime
    updated_at: datetime
```

### 3.2 Agent Role

```python
class AgentRole:
    name: str                          # e.g. "developer", "qa-evaluator"
    agent_md_path: str                 # Path to agent.md definition
    trigger_states: list[str]          # Issue states that activate this role
    trigger_labels: list[str]          # Label-based routing (e.g. needs-analysis)
    trigger_events: list[str]          # Event-based routing (e.g. pr.created, pr.merged)
    trigger_internal: bool             # True if triggered by orchestrator only (not tracker)
    available_skills: list[str]        # Skills this role can use
    evaluation_dimensions: list[str]   # How this role's work is judged
    handoff_state: str                 # Issue state after successful completion
    fail_state: str                    # Issue state on failure
    model: str                         # Copilot CLI model (e.g. gpt-5.3-codex)
```

### 3.3 Orchestration Phase

```python
class Phase:
    """Internal phase within an issue's lifecycle, managed by orchestrator."""
    role: str               # Agent role name
    gate: str | None        # Quality gate to pass before advancing
    next_phase: str | None  # Next phase on success
    fail_phase: str | None  # Phase on failure (e.g. back to developer)
```

### 3.4 Pipeline Definition

```python
class Pipeline:
    """Ordered sequence of phases for an issue lifecycle."""
    phases: list[Phase]
    # Example: developer → qa_evaluation → human_review → merge
```

### 3.5 Workpad

The **workpad** is a pinned tracker comment on the issue, used as the agent's running log and source of truth. It is the same concept as the Elixir implementation's `## Copilot Workpad` comment. Symphony creates one workpad per issue at the start of the first phase and updates it in place throughout the lifecycle. Agents write progress, decisions, QA reports, and sprint contract summaries to the workpad. Humans read the workpad to understand what the agent has done and why.

```
TrackerAdapter.update_workpad(issue_id, content)
  → updates the pinned "## Copilot Workpad" comment body in JIRA/Linear
```

## 4. Agent Role System

### 4.1 Role Definitions (`agents/` directory)

```
.github/agents/
├─ requirements-analyst.md
├─ developer.md
├─ qa-evaluator.md
├─ code-reviewer.md
├─ devops.md
└─ documentation.md
```

### 4.2 agent.md Standard Structure

```markdown
# [Role Name]

## Identity
Who this agent is and what it optimizes for.
One paragraph. Defines perspective and priorities.

## Trigger Conditions
- **States:** [Todo, In Progress, ...]
- **Labels:** [needs-analysis, ...]  (optional)
- **Events:** [pr_created, tests_failed, ...]  (optional)

## Available Skills
- skill-hub/generation/playwright-gen
- skill-hub/evaluation/test-runner
- ...

## Evaluation Criteria
| Dimension | Threshold | Policy |
|-----------|-----------|--------|
| Pass Rate | 100% | strict |
| Coverage  | 80%  | strict |

## Input Contract
What this role expects to find when it starts:
- Issue description with acceptance criteria
- Workspace with repo cloned
- Previous phase artifacts (e.g. structured requirements from analyst)

## Output Contract
What this role must produce before handing off:
- Updated workpad with checklist
- All tests passing
- QA Report (for QA role)
- PR created (for developer role)

## Handoff Protocol
- **On success:** Transition to [state] / advance to next phase
- **On failure:** Transition to [state] with failure reason in workpad

## Guardrails
- Must NOT modify issue body
- Must NOT skip quality gate
- Must NOT push to main directly
```

### 4.3 Role Catalog

#### Requirements Analyst

| Aspect | Detail |
|--------|--------|
| **Model** | Claude Sonnet 4.6 (overridable in WORKFLOW.md) |
| **Trigger** | Issue state = Todo, label = `needs-analysis` |
| **Skills** | requirement-parser, test-case-matrix |
| **Output** | Structured AC in workpad, ambiguity flags as comments, traceability links |
| **Handoff** | Remove `needs-analysis` label, issue stays in Todo for Developer pickup |
| **Guardrail** | Does not write code. Only analyzes and structures. |

#### Developer

| Aspect | Detail |
|--------|--------|
| **Model** | GPT-5.3-Codex (overridable in WORKFLOW.md) |
| **Trigger** | Issue state = Todo (no `needs-analysis` label) or In Progress |
| **Skills** | commit, push, pull, test-driven-development, systematic-debugging |
| **Output** | Implementation code, tests, PR, updated workpad |
| **Handoff** | Advance to QA Evaluation phase (internal) |
| **Guardrail** | Must follow TDD. Must not merge own PR. |

#### QA Evaluator

| Aspect | Detail |
|--------|--------|
| **Model** | Gemini 3 Pro (overridable in WORKFLOW.md; intentionally cross-model from Developer) |
| **Trigger** | Internal phase only — triggered by orchestrator after Developer phase completes (`trigger: { internal: true }`). Never triggered directly by tracker state. |
| **Skills** | test-runner, coverage-analyzer, acceptance-validator, qa-reporter, failure-classifier |
| **Output** | QA Report in workpad, verdict (PASS/FAIL) |
| **Handoff** | PASS → Human Review. FAIL → Rework (back to Developer). |
| **Guardrail** | Does not write implementation code. Evaluates only. Must be calibrated skeptical, not lenient. |
| **Sub-spec** | [QA Agent System Design](2026-03-25-qa-agent-system-design.md) |

#### Code Reviewer

| Aspect | Detail |
|--------|--------|
| **Model** | Claude Sonnet 4.6 (overridable in WORKFLOW.md; intentionally cross-model from Developer) |
| **Trigger** | Issue state = Human Review (runs alongside human reviewer) |
| **Skills** | requesting-code-review, verification-before-completion |
| **Output** | Review comments on PR, categorized by severity (Critical/High/Medium/Suggestion) |
| **Handoff** | Critical issues → Rework. Otherwise → human decides. |
| **Guardrail** | Does not modify code. Reviews only. |

#### DevOps Agent

| Aspect | Detail |
|--------|--------|
| **Model** | Claude Sonnet 4.6 (overridable in WORKFLOW.md) |
| **Trigger** | Issue state = Merging |
| **Skills** | finishing-a-development-branch, CI/CD integration skills |
| **Output** | Merged PR, deployment confirmation |
| **Handoff** | Successful deploy → Done. Failed → back to Human Review with error details. |
| **Guardrail** | Must not force-push. Must not skip CI. |

#### Documentation Agent

| Aspect | Detail |
|--------|--------|
| **Model** | Claude Sonnet 4.6 (overridable in WORKFLOW.md) |
| **Trigger** | Post-merge event, or label = `needs-docs` |
| **Skills** | Documentation generation, changelog update |
| **Output** | Updated API docs, changelog entries, architecture diagram updates |
| **Handoff** | PR with doc changes → Human Review |
| **Guardrail** | Does not modify application code. Docs only. |

#### Architecture / Design Agent

| Aspect | Detail |
|--------|--------|
| **Model** | Claude Sonnet 4.6 (overridable in WORKFLOW.md) |
| **Trigger** | Issue has label `needs-design`, or issue has label `epic` or `major-feature` (note: these are labels, not JIRA issue types) |
| **Skills** | adr-writer, system-design-reviewer, api-contract-generator, change-impact |
| **Output** | Architecture Decision Record (ADR), system design document, API contracts, dependency map |
| **Handoff** | Remove `needs-design` label, attach design doc link to issue, issue stays in Todo for Developer pickup |
| **Guardrail** | Does not write implementation code. Design artifacts only. Must flag unresolvable constraints as human decisions. |

#### Security Agent

| Aspect | Detail |
|--------|--------|
| **Model** | Claude Sonnet 4.6 (overridable in WORKFLOW.md) |
| **Trigger** | PR created event (automatic), or label `needs-security-review` |
| **Skills** | sast-runner, dependency-scanner, owasp-checker, compliance-validator, secret-detector |
| **Output** | Security report with findings categorized: Critical / High / Medium / Info |
| **Handoff** | Critical findings → `state:Rework`. High findings → add `security-high` label for human triage. Medium/Info → annotate PR comments only. No findings → pass. |
| **Guardrail** | Does not fix code. Reports only. Must not suppress or downgrade findings without human approval. |

#### Release Manager Agent

| Aspect | Detail |
|--------|--------|
| **Model** | Claude Sonnet 4.6 (overridable in WORKFLOW.md) |
| **Trigger** | PR merged event (post-DevOps handoff), or issue state = Done |
| **Skills** | changelog-generator, version-bumper, release-notes-writer, deployment-tracker |
| **Output** | Changelog entry, version tag, release notes PR, deployment record in tracker |
| **Handoff** | Release notes PR → Human Review. Version tag created after human approves. |
| **Guardrail** | Does not merge to main. Must not bump major version without explicit human approval. Semantic versioning enforced. |

#### Incident Response Agent

| Aspect | Detail |
|--------|--------|
| **Model** | GPT-5.3-Codex for hotfix code; Claude Sonnet 4.6 for root-cause analysis |
| **Trigger** | Issue has label `incident` (P0/P1 severity) |
| **Skills** | log-analyzer, root-cause-analysis, systematic-debugging, hotfix-developer |
| **Output** | Root cause analysis report, hotfix PR with tests, incident timeline in workpad |
| **Handoff** | Hotfix PR → Human Review (emergency fast-track: skip QA gate, go directly to human). |
| **Guardrail** | Hotfix must include at least one regression test. Must not bypass security scan (runs in parallel to minimize delay). Must not push to main without human approval. |

> **Cross-model objectivity principle:** Developer uses GPT-5.3-Codex; QA Evaluator uses Gemini 3 Pro; Code Reviewer uses Claude Sonnet 4.6. Using different models for generation and evaluation reduces the risk of blind spots inherited from a single model's training. All models are accessed through Copilot CLI's model-selection capability.

## 5. Multi-Phase Orchestration

### 5.1 Pipeline Configuration

Defined in WORKFLOW.md front matter. Each repository has its own WORKFLOW.md that defines the pipeline, quality gates, and prompt templates for that project. Symphony reads this file at startup and on hot-reload. WORKFLOW.md contains two concerns: (1) orchestration config (pipeline phases, gates, subagent limits) as YAML front matter, and (2) prompt templates as Liquid/Jinja body. The agent.md files (Section 4) define role identity; WORKFLOW.md defines how roles are sequenced and configured per project.

```yaml
# on_success / on_failure values:
#   phase:<role>          — advance to an internal phase (same tracker state)
#   state:<tracker-state> — transition the tracker issue state (Symphony-initiated)
#   label:<label-name>    — add a label to the issue (signal without state change)
#   null                  — no automatic action; wait for human or retry

pipeline:
  phases:
    - role: requirements-analyst
      trigger: { labels: [needs-analysis] }
      gate: null
      on_success: phase:developer
      on_failure: null  # flags issue, waits for human

    - role: developer
      trigger: { states: [Todo, In Progress, Rework] }
      gate: null
      on_success: phase:qa-evaluator
      on_failure: null  # stays in progress, retries

    - role: qa-evaluator
      trigger: { internal: true }  # triggered by orchestrator, not tracker state
      gate: qa_gate
      on_success: state:Human Review
      on_failure: state:Rework

    - role: code-reviewer
      trigger: { states: [Human Review] }
      gate: null
      on_success: label:ready-to-merge  # signals no critical findings; human still approves Merging
      on_failure: state:Rework

    # NOTE: Human Review → Merging is ALWAYS human-initiated.
    # Symphony adds the ready-to-merge label on code-reviewer success, but never
    # transitions to Merging itself. The human approves in the tracker, which
    # triggers the devops phase via webhook (issue.state_changed → Merging).

    - role: devops
      trigger: { states: [Merging] }
      gate: ci_gate
      on_success: state:Done
      on_failure: state:Human Review
```

### 5.2 Phase Execution Flow

```
Orchestrator picks up issue
  │
  ▼
Route to current phase's agent role
  │
  ▼
Start Copilot CLI session with:
  - agent.md (role identity + guardrails)
  - WORKFLOW.md prompt template (issue context)
  - Available skills injected into context
  │
  ▼
Agent executes (turns 1..N)
  │
  ▼
Agent completes → Orchestrator checks quality gate (if defined)
  │
  ├─ Gate PASS → advance to next phase (on_success)
  ├─ Gate FAIL → route to failure phase (on_failure)
  └─ No gate   → advance to next phase
  │
  ▼
Next phase starts (new agent role, new Copilot CLI session)
```

### 5.3 Internal Phase vs Tracker State

| Tracker State | Internal Phases | Agent Role(s) |
|---------------|----------------|---------------|
| **Todo** | requirements-analysis (optional), dev-ready | Requirements Analyst, Developer |
| **In Progress** | development, qa-evaluation | Developer, QA Evaluator |
| **Human Review** | code-review, human-approval | Code Reviewer + Human |
| **Rework** | rework-development | Developer |
| **Merging** | merge-and-deploy | DevOps |
| **Done** | — | — |

Tracker state transitions happen at phase boundaries:
- `Todo → In Progress`: When Developer phase starts
- `In Progress → Human Review`: When QA gate passes
- `Human Review → Rework`: When reviewer requests changes
- `Human Review → Merging`: When human approves
- `Merging → Done`: When merge and deploy complete

Internal phases within a tracker state are invisible to the tracker — orchestrator manages them.

## 6. Agent Role Router

### 6.1 Routing Logic

There are two dispatch surfaces: **issue-based routing** (for state/label/internal-phase triggers) and **event-based routing** (for agents triggered by PR/CI/deploy events). They run independently.

```python
# ── Issue-based routing (runs each polling cycle) ──────────────────────────
def route_issue(issue: Issue, pipeline: Pipeline) -> AgentRole | None:
    """Determine which agent role should handle this issue."""

    # 1. Check internal phase first (orchestrator-managed, highest priority)
    #    Internal phases represent in-progress orchestration that must not
    #    be overridden by state/label triggers.
    current_phase = get_current_internal_phase(issue.id)
    if current_phase and current_phase.trigger.get("internal"):
        return load_role(current_phase.role)

    # 2. Check label-triggered roles (e.g. needs-analysis, needs-design, incident)
    for phase in pipeline.phases:
        if phase.trigger.get("labels"):
            if any(l in issue.labels for l in phase.trigger["labels"]):
                return load_role(phase.role)

    # 3. Check state-triggered roles
    for phase in pipeline.phases:
        if issue.state in phase.trigger.get("states", []):
            return load_role(phase.role)

    return None  # No matching role — skip this issue


# ── Event-based routing (runs on each webhook event) ──────────────────────
def route_event(event: TrackerEvent, pipeline: Pipeline) -> list[AgentRole]:
    """Dispatch agents triggered by tracker/CI events (parallel, non-blocking)."""
    roles = []
    for phase in pipeline.phases:
        if event.type in phase.trigger.get("events", []):
            roles.append(load_role(phase.role))
    return roles  # Multiple roles may respond to the same event (e.g. pr.created)


# ── Event types that trigger event-based dispatch ─────────────────────────
# pr.created    → Security Agent (SAST scan)
# pr.merged     → Release Manager Agent, Documentation Agent
# ci.completed  → informs DevOps phase (surfaced as artifact, not separate dispatch)
```

**Key distinction:** Issue-based routes produce one agent per issue at a time. Event-based routes are fire-and-forget: the event spawns the agent asynchronously, with results posted back to the issue as tracker comments or PR annotations. Event-triggered agents do not block or advance the main pipeline phase.

### 6.2 Prompt Assembly

When a role is selected, the orchestrator assembles the agent prompt:

```
[1] System: agent.md content (role identity, guardrails)
[2] System: Available skills metadata (L1 descriptors only — names + one-line descriptions)
[3] User: WORKFLOW.md prompt template rendered with issue context
[4] User: Previous phase artifacts (workpad content, QA report, etc.)
[5] User: Phase initialization instructions (see Section 9.3)
```

**Context engineering principles:**

- **Resident identity** — `agent.md` is always in context; defines who the agent is and what it optimizes for.
- **Just-in-time skills** — Only L1 descriptors loaded upfront. Full skill content (L2/L3) fetched on demand when the agent invokes the skill. Never dump the entire skill library into context.
- **Right altitude** — System prompts must be specific enough to guide behavior, but not so brittle they encode hardcoded logic. The test: can you explain the agent's role in one sentence? If the prompt requires paragraph-level conditionals, it's too low-altitude.
- **Minimal viable tool sets** — Each role receives only the tools relevant to its function. Ambiguous overlapping tools are a failure mode; agents cannot reliably choose between tools that have unclear boundaries.
- **Progress file over memory** — Phase state is in `.symphony/progress.json` (machine-readable) and `.symphony/notes.md` (agent-written notes). Never rely on the context window to hold progress across sessions.

This follows the context engineering principle: resident identity (agent.md) + on-demand skills (L1→L2→L3) + runtime context (issue + artifacts) + persistent progress (progress.json + notes.md).

## 7. Quality Gate Engine

### 7.1 Gate Configuration

```yaml
# WORKFLOW.md
quality_gates:
  qa_gate:
    dimensions:
      pass_rate: { threshold: 100, policy: strict }
      coverage: { threshold: 80, policy: strict }
      acceptance: { threshold: 100, policy: strict }
    on_fail: rework
    on_inconclusive: strict  # strict = treat as fail, advisory = treat as pass

  ci_gate:
    checks:
      - "CI pipeline passes"
      - "No merge conflicts"
      - "PR has required approvals"
    on_fail: human-review
```

### 7.2 Gate Evaluation

```python
def evaluate_gate(gate_config: dict, phase_artifacts: dict) -> GateResult:
    """Evaluate a quality gate against phase output."""
    if gate_config.get("dimensions"):
        # QA-style dimensional evaluation
        results = []
        for dim, config in gate_config["dimensions"].items():
            result = evaluate_dimension(dim, config, phase_artifacts)
            results.append(result)
        return compute_gate_verdict(results, gate_config)

    if gate_config.get("checks"):
        # Checklist-style evaluation
        for check in gate_config["checks"]:
            if not verify_check(check, phase_artifacts):
                return GateResult(passed=False, reason=f"Failed: {check}")
        return GateResult(passed=True)
```

### 7.3 Team Onboarding Profiles

| Profile | Gates | Description |
|---------|-------|-------------|
| **Strict** | All gates strict | Mature teams, critical systems (core, underwriting) |
| **Advisory** | QA gate strict, others advisory | Most teams |
| **Custom** | Per-gate config (e.g. QA = strict, CI = advisory) | Teams in transition or ramping up |

Configured per project in WORKFLOW.md. CoE sets defaults, business teams can request adjustments with CoE approval. Profile names align with QA sub-spec (Strict/Advisory/Custom) so the same project-level profile governs both orchestrator gates and QA evaluation policy.

## 8. Tracker Adapter

### 8.1 Adapter Interface

```python
class TrackerAdapter(Protocol):
    async def fetch_candidates(self, active_states: list[str]) -> list[Issue]: ...
    async def fetch_issue(self, issue_id: str) -> Issue: ...
    async def update_state(self, issue_id: str, state: str) -> None: ...
    async def add_comment(self, issue_id: str, body: str) -> None: ...
    async def update_workpad(self, issue_id: str, content: str) -> None: ...
    async def fetch_issue_states(self, issue_ids: list[str]) -> dict[str, str]: ...
```

### 8.2 Implementations

| Adapter | Status | Notes |
|---------|--------|-------|
| **Linear** | Port from Elixir | GraphQL API, already proven |
| **JIRA** | New | REST API, required for company adoption |
| **Memory** | Port from Elixir | In-memory mock for testing |

### 8.3 JIRA-Specific Considerations

- JIRA workflow states are customizable per project — adapter must map custom states to canonical states (Todo, In Progress, etc.)
- JIRA has subtasks — orchestrator can use subtasks for internal phases
- JIRA has custom fields — acceptance criteria may be in custom field, not description
- Authentication: OAuth 2.0 or API token, managed via `$JIRA_API_TOKEN` env var

### 8.4 JIRA State Mapping (Hybrid Model)

Company-level defaults are maintained by Platform Engineering and ship with Symphony. Each project can override any mapping in its WORKFLOW.md.

```yaml
# WORKFLOW.md — per-project overrides (optional)
jira_state_mapping:
  # Company defaults are loaded first; entries here override them per state name
  "Awaiting Sign-off": Human Review
  "Ready to Deploy": Merging
```

```yaml
# Company-level defaults (Symphony built-in, managed by Platform Engineering)
jira_state_defaults:
  "To Do": Todo
  "Open": Todo
  "In Progress": In Progress
  "In Development": In Progress
  "In Review": Human Review
  "Ready for QA": Human Review
  "QA": Human Review
  "Resolved": Done
  "Done": Done
  "Closed": Done
  "Won't Do": Cancelled
```

Unmapped states are logged as a warning and treated as `null` (issue skipped). Platform Engineering reviews unmapped state warnings during onboarding to converge on complete mappings.

### 8.5 Webhook Integration

Symphony supports real-time event delivery via webhooks in addition to polling. Webhooks are the primary trigger mechanism; polling is the reliability fallback.

```
JIRA/Linear Webhook → Symphony HTTP endpoint → Event Queue → Orchestrator
                          (/api/v1/webhooks)
```

```yaml
# Supported webhook events
webhook_events:
  - issue.created          # New issue → evaluate if Symphony should pick up
  - issue.state_changed    # State transition → trigger matching phase
  - issue.label_added      # Label added → may trigger role (needs-design, incident, etc.)
  - issue.comment_added    # Human comment → parse for @symphony commands
  - issue.dependency_resolved  # Blocked-by issue reaches Done → unblock dependents
  - pr.created             # → trigger Security Agent (parallel to Code Reviewer)
  - pr.merged              # → trigger Release Manager + Documentation agents
  - ci.completed           # CI pass/fail → inform DevOps phase
```

Webhook endpoint authenticates via HMAC signature verification. Failed delivery is retried by the tracker. Symphony deduplicates events via event ID to prevent double-processing.

### 8.6 Bidirectional State Machine

Symphony transitions tracker states on behalf of agents. Guard conditions prevent invalid transitions.

```
Allowed transitions (Symphony-initiated):
  ┌──────────┬───────────────┬──────────────────────────────────────────────┐
  │ From     │ To            │ Guard Condition                              │
  ├──────────┼───────────────┼──────────────────────────────────────────────┤
  │ Todo     │ In Progress   │ Symphony starts Developer phase              │
  │ In Prog. │ Human Review  │ QA gate PASS                                 │
  │ In Prog. │ Rework        │ Internal failure (agent error or gate FAIL)  │
  │ Human R. │ Rework        │ Critical code review finding                 │
  │ Human R. │ Merging       │ Human approval (not Symphony-initiated)      │
  │ Merging  │ Done          │ DevOps phase completes, deploy confirmed      │
  │ Merging  │ Human Review  │ CI gate FAIL                                 │
  │ Rework   │ In Progress   │ Symphony restarts Developer phase after reset│
  │ Any      │ Blocked       │ Dependency issue not yet Done                │
  │ Blocked  │ In Progress   │ All blocking issues reached Done (unblocked) │
  └──────────┴───────────────┴──────────────────────────────────────────────┘

Forbidden (Symphony cannot initiate):
  - Any state → Done (except via DevOps phase)
  - Any state → Merging (human approves at Human Review)
  - Rework → Human Review directly (must go through Rework → In Progress → QA gate pass first)
```

Human actors can transition to any state at any time. Symphony detects unexpected state changes on the next turn boundary and adjusts accordingly (see Section 23).

### 8.7 Issue Dependency Handling

```
blocked_by: [PROJ-100, PROJ-101]  ← from JIRA/Linear issue links
```

Symphony maintains a dependency graph per polling cycle:

1. When an issue has unresolved `blocked_by` links, it is skipped during candidate selection.
2. When a blocking issue reaches Done/Merged, Symphony emits `issue.dependency_resolved` internally.
3. The blocked issue is re-evaluated on the next poll cycle; if no remaining blockers, it is picked up normally.
4. Dependency cycles (PROJ-A blocks PROJ-B blocks PROJ-A) are detected and flagged as `dependency-cycle` label on both issues; humans must resolve.

## 9. Workspace & Execution

### 9.1 Per-Issue Workspace (Inherited from Elixir)

```
~/code/symphony-workspaces/
├─ PROJ-123_add-password-validation/
│   ├─ .git/
│   ├─ .symphony/
│   │   ├─ phase.json          — Current internal phase state
│   │   ├─ progress.json       — Feature checklist (JSON; agents update passes: true/false only)
│   │   ├─ notes.md            — Agent-written session notes (persistent memory)
│   │   ├─ init.sh             — Workspace setup script (start dev server, run smoke test)
│   │   ├─ artifacts/          — Phase output artifacts (QA report, sprint contracts, etc.)
│   │   └─ history.jsonl       — Phase transition log
│   └─ <project files>
├─ PROJ-124_fix-login-bug/
└─ ...
```

**Multi-repo issues:** When an issue spans multiple microservice repos, one workspace per repo is created under a shared parent directory. Each workspace has its own `.symphony/` directory. The issue is the parent; sub-workspaces are named `PROJ-123_<repo-name>/`.

```
~/code/symphony-workspaces/
├─ PROJ-123/
│   ├─ api-service/            — One workspace per repo
│   │   ├─ .git/
│   │   └─ .symphony/
│   ├─ web-frontend/
│   │   ├─ .git/
│   │   └─ .symphony/
│   └─ .symphony/              — Parent-level coordination state
│       └─ phase.json          — Which sub-workspace is active
└─ ...
```

### 9.2 Phase State Persistence

```json
// .symphony/phase.json
{
  "current_phase": "qa-evaluation",
  "previous_phases": [
    {"role": "developer", "status": "completed", "completed_at": "2026-03-26T10:00:00Z"}
  ],
  "artifacts": {
    "developer": {"pr_url": "https://github.com/...", "branch": "feat/PROJ-123"},
    "qa-evaluator": null
  }
}
```

### 9.3 Agent Runner (Per Phase)

Every agent session begins with a **Phase Initialization Protocol** to orient the agent before any work begins:

```
Phase Initialization Protocol (first turns of every session):
  1. Get bearings  — run `pwd`, confirm workspace, confirm git branch
  2. Read progress — load .symphony/progress.json, .symphony/notes.md
  3. Read git log  — last 10 commits for context
  4. Run init.sh   — start dev server and run smoke test
  5. Assess state  — identify first failing feature in progress.json
  6. Begin work    — work on ONE feature at a time until all pass
```

```python
async def run_phase(issue: Issue, phase: Phase, workspace: str):
    """Execute a single phase for an issue."""
    # 1. Load agent role definition
    role = load_agent_md(phase.role)

    # 2. Assemble prompt (includes phase initialization instructions)
    prompt = assemble_prompt(role, issue, workspace)

    # 3. Start Copilot CLI session
    session = await start_copilot_session(
        workspace=workspace,
        prompt=prompt,
        skills=role.available_skills,
        model=role.model,
    )

    # 4. Turn loop (with context reset support)
    for turn in range(max_turns):
        result = await session.run_turn()
        if result.completed:
            break
        if result.context_near_limit:
            # Context reset: summarize state → handoff artifact → new session
            handoff = await create_handoff_artifact(session, workspace)
            session = await reset_session(role, issue, workspace, handoff)

    # 5. Collect artifacts
    artifacts = collect_phase_artifacts(workspace, phase.role)

    # 6. Evaluate quality gate (if defined)
    if phase.gate:
        gate_result = evaluate_gate(phase.gate, artifacts)
        if not gate_result.passed:
            return PhaseResult(status="failed", reason=gate_result.reason)

    # 7. Persist phase state
    update_phase_state(workspace, phase.role, "completed", artifacts)

    return PhaseResult(status="completed", artifacts=artifacts)
```

## 10. Subagent Strategy

### 10.1 When to Use Subagents

| Trigger | Example | Strategy |
|---------|---------|----------|
| **Multi-file changes** | Issue touches 5+ files across modules | Developer spawns parallel subagents per module |
| **Multi-platform testing** | Need web + mobile + API tests | QA Evaluator spawns subagent per platform |
| **Deep investigation** | Debugging a complex failure | Debugging subagent explores while main agent continues |
| **Independent subtasks** | Issue has 3 independent ACs | Parallel subagent per AC |

### 10.2 Coordination Protocol

- **Delegation:** Parent agent sends task description + scope constraints + expected output format
- **Isolation:** Each subagent gets its own git worktree (prevents conflicts)
- **Communication:** Subagents return summary only (not full context) to parent
- **Timeout:** Subagent has time budget; returns partial results on timeout
- **Validation:** Parent cross-validates subagent results before integrating (prevent hallucination amplification)

### 10.3 Configuration

```yaml
# WORKFLOW.md
subagent:
  max_concurrent: 4
  timeout_ms: 600000        # 10 minutes per subagent
  isolation: worktree       # worktree | directory | none
  result_format: summary    # summary | full
```

## 11. Skill Hub

Shared across all agent roles. Organized by domain, consumed by roles via `available_skills` in agent.md.

```
skill-hub/
├─ analysis/
│   ├─ requirement-parser/
│   ├─ change-impact/
│   └─ risk-scorer/
│
├─ generation/
│   ├─ playwright-gen/
│   ├─ appium-gen/
│   ├─ api-test-gen/
│   ├─ k6-gen/
│   ├─ test-case-matrix/
│   ├─ test-data-gen/
│   └─ cobol-boundary-test/
│
├─ execution/
│   ├─ test-runner/
│   ├─ regression-selector/
│   └─ self-healer/
│
├─ evaluation/
│   ├─ coverage-analyzer/
│   ├─ acceptance-validator/
│   ├─ qa-reporter/
│   ├─ failure-classifier/
│   └─ defect-analyzer/
│
├─ development/
│   ├─ commit/
│   ├─ push/
│   ├─ pull/
│   ├─ test-driven-development/
│   ├─ systematic-debugging/
│   └─ finishing-a-development-branch/
│
├─ review/
│   ├─ code-quality-review/
│   ├─ security-scan/
│   └─ architecture-compliance/
│
└─ devops/
    ├─ ci-pipeline/
    ├─ deployment/
    └─ environment-health-check/
```

Skill standard structure as defined in QA Agent sub-spec (skill.yaml + prompt.md + knowledge/ + templates/ + tests/).

## 12. Knowledge Base

```
knowledge-base/
├─ standards/
│   ├─ coding-standards/     — Language-specific coding conventions
│   ├─ testing-standards/    — POM structure, naming, coverage targets
│   ├─ api-standards/        — REST/GraphQL conventions, versioning
│   └─ security-standards/   — OWASP, authentication patterns
│
├─ patterns/
│   ├─ automation/           — Page Object, Screenplay, etc.
│   ├─ architecture/         — Microservices, event-driven, etc.
│   └─ ci-cd/               — Pipeline patterns, deployment strategies
│
├─ domain/
│   ├─ new-policy/           — 投保流程 (policy application workflow)
│   ├─ underwriting/         — 核保流程 (underwriting rules)
│   ├─ claims/               — 理赔流程 (claims processing)
│   └─ core-system/          — AS400/COBOL integration boundaries
│
└─ history/
    ├─ defect-patterns/      — Historical defect clusters
    └─ team-gotchas/         — Common mistakes per team/domain
```

Indexed via RAG (vector embeddings). All agent roles can query the knowledge base for domain context and team conventions.

## 13. Event Bus

### 13.1 Event Types

| Event | Producer | Consumers |
|-------|----------|-----------|
| `issue.state_changed` | Tracker Adapter | Orchestrator, Observability |
| `phase.started` | Orchestrator | Observability, Event Log |
| `phase.completed` | Orchestrator | Next Phase Trigger, Observability |
| `phase.failed` | Orchestrator | Retry Logic, Alerting |
| `gate.evaluated` | Quality Gate Engine | Observability, Reporting |
| `pr.created` | Developer Agent | Code Reviewer trigger |
| `pr.merged` | DevOps Agent | Documentation trigger |
| `tests.completed` | QA Agent | Observability, Reporting |
| `subagent.spawned` | Any Agent | Observability |
| `subagent.completed` | Subagent | Parent Agent |

### 13.2 Implementation

P2: In-process event emitter (Python asyncio). P3: External message broker (Redis Pub/Sub or similar) for distributed deployment.

## 14. Observability

### 14.1 Structured Logging

All log entries include:
- `issue_id`, `issue_identifier`
- `phase`, `role`
- `session_id` (Copilot CLI thread-turn)
- `event_type`

### 14.2 Metrics

| Category | Metrics |
|----------|---------|
| **Throughput** | Issues completed/day, phases completed/day, average cycle time per phase |
| **Quality** | QA gate pass rate, code review rejection rate, defect escape rate |
| **Cost** | Tokens per issue, tokens per phase, tokens per role, cost per issue |
| **Efficiency** | Agent turns per phase, retry rate, subagent utilization |
| **Team** | Per-team issue velocity, per-team quality gate pass rate |

### 14.3 Cost Budget Model

Per-team monthly token budgets, allocated by Platform Engineering. Tracked in real time; alerts sent at 80% utilization; hard stops at 100%.

```yaml
# WORKFLOW.md (team section, configured by Platform Engineering)
cost_budget:
  team: payments-api
  monthly_token_limit: 10_000_000
  alert_threshold: 0.80        # Alert at 80% usage
  hard_stop: true              # Hard stop at 100% (no new sessions)
  carry_over: false            # Unused budget does not roll over
```

Budget tracking is aggregated per-team across all issues and repos managed by Symphony. Platform Engineering manages budgets centrally; teams request adjustments via standard change request.

### 14.4 Dashboard

- P1: Terminal UI (port from Elixir StatusDashboard) + structured JSON logs
- P2: Web dashboard (FastAPI + simple frontend) with real-time phase tracking
- P3: Full metrics platform with historical trends, cost attribution, team comparisons

## 15. Security & Compliance

- **Workspace isolation:** Each issue runs in sandboxed directory. PathSafety prevents escape.
- **Agent sandboxing:** Copilot CLI runs with `workspace-write` sandbox policy.
- **Tracker authentication:** API keys via environment variables (`$LINEAR_API_KEY`, `$JIRA_API_TOKEN`). Never in WORKFLOW.md.
- **Skill Hub access:** RBAC — CoE manages skills (`qa:admin`), teams consume (`qa:read`).
- **PII protection:** Knowledge base domain content must not contain real customer data. Test data generation uses synthetic data only.
- **Audit trail:** All phase transitions, gate evaluations, and state changes logged immutably.
- **Human gates:** Merging requires human approval. No agent can merge to main autonomously.
- **AS400 / COBOL access:** Agents may interact with AS400 via approved tooling only. All AS400 tool calls are logged. Direct database access to core system tables is prohibited; agents must go through approved API layers.
- **Network requirements:** Symphony and Copilot CLI require full internet access. Air-gapped or restricted-network environments are not supported in P1. Teams in restricted zones must arrange for an approved proxy or defer to a future release.

## 16. Failure Modes & Recovery

| Failure | Impact | Detection | Recovery |
|---------|--------|-----------|----------|
| **Copilot CLI timeout** | Phase incomplete, issue stuck | Turn counter exceeds `max_turns` or session exceeds timeout | Retry with exponential backoff (max 3). On exhaust: park issue, notify human via tracker comment |
| **Copilot CLI crash** | Session lost mid-phase | Process exit code != 0 | Restart from last checkpoint (workspace + phase.json). If workspace corrupted: re-clone, restart phase |
| **Tracker API unavailable** | Cannot poll or update issues | HTTP 5xx or connection timeout on adapter calls | Retry with backoff. After 5 failures: pause polling, emit `tracker.unavailable` alert, resume on recovery |
| **Quality gate false negative** | Good work rejected, rework loop | Rework count exceeds threshold (e.g. 3 cycles for same issue) | Escalate to human: add `needs-human-review` label, pause orchestration for that issue |
| **Quality gate false positive** | Bad work passes | Post-merge defect detected (human report or CI failure) | Log for gate calibration. Knowledge base records pattern for future detection |
| **Agent produces harmful code** | Security/compliance risk | CI security scan catches it, or code reviewer flags | Phase fails at CI gate. Code reviewer role runs before merge as safety net. Human gate at merge is mandatory |
| **Subagent divergence** | Conflicting changes from parallel subagents | Merge conflict in worktree integration | Parent agent retries sequentially. If unresolvable: escalate to human |
| **Workspace disk full** | Cannot clone or write | OS-level error during git operations | Alert, pause issue. Admin cleans stale workspaces. Configurable workspace TTL for auto-cleanup |
| **Infinite rework loop** | Issue bounces developer ↔ QA indefinitely | Loop counter in phase.json | After N cycles (configurable, default 3): park issue with `stuck` label, notify human |
| **Rate limit (Copilot CLI)** | Cannot start new sessions | HTTP 429 from Copilot API | Orchestrator-level rate limiter with token bucket. Queue excess work, process in order |

### 16.1 Graceful Degradation

When the orchestrator itself encounters errors:

1. **Individual issue failure** — does not affect other issues. Failed issue is parked with full error context in `.symphony/history.jsonl`.
2. **Systemic failure** (tracker down, Copilot API down) — orchestrator enters "paused" mode. Existing in-progress sessions continue. No new sessions started. Resumes automatically when health checks pass.
3. **Orchestrator restart** — recovers state from `.symphony/phase.json` per workspace. Incomplete phases are re-evaluated (check if agent already completed work, avoid duplicate execution).

### 16.2 Subagent Lifecycle

Subagent cleanup protocol:
- On **success**: worktree merged into parent branch, worktree deleted
- On **failure**: worktree preserved for debugging (configurable TTL, default 24h), then auto-deleted
- On **timeout**: partial results returned to parent, worktree preserved
- **Orphan detection**: Orchestrator periodically scans for worktrees without active parent sessions, cleans up after TTL

## 17. Phased Delivery

### Phase 1: Core Orchestrator + QA Quick Win

**Goal:** Symphony Python running with Developer + QA Evaluator roles.

**Pilot:** QA CoE internal tooling — dogfood Symphony on the CoE team's own work before rolling out to other teams. This validates the orchestrator, surfaces integration issues, and produces reference configurations for other teams.

**Deliverables:**
- Python orchestrator core: polling, dispatch, workspace, agent runner
- Linear adapter (port from Elixir)
- WORKFLOW.md parser + Liquid template rendering
- Developer role (agent.md) — Copilot CLI writes code
- QA Evaluator role (agent.md) — same-session prompt injection, not separate agent dispatch (from QA sub-spec P1; upgrades to independent session in P3)
- 5 QA evaluation skills (test-runner, coverage-analyzer, acceptance-validator, qa-reporter, failure-classifier)
- QA quality gate (pass rate + coverage + acceptance)
- Sprint Contract Protocol between Developer and QA Evaluator (see Section 22)
- Phase Initialization Protocol + `.symphony/progress.json` + `.symphony/notes.md`
- Terminal UI dashboard
- Memory adapter (testing)
- CoE pilot playbook + rollback runbook

### Phase 2: Multi-Role + Test Generation

**Goal:** Full role catalog, multi-phase orchestration, test generation skills.

**Deliverables:**
- Requirements Analyst role + requirement-parser skill
- Code Reviewer role
- Multi-phase pipeline execution (developer → qa → review)
- Internal phase state management (.symphony/phase.json)
- JIRA adapter (basic: fetch issues, update state, add comments)
- Per-platform test generation skills (playwright-gen, appium-gen, api-test-gen, k6-gen)
- Knowledge Base (RAG) with CoE standards + insurance domain
- QA Service independent deployment (FastAPI)
- Event bus (in-process)
- Web dashboard (basic)

### Phase 3: Full Platform

**Goal:** Production-grade SDLC orchestrator.

**Deliverables:**
- DevOps role + CI/CD integration skills
- Documentation role
- Independent QA Agent Session (separate Copilot CLI)
- Subagent orchestration (worktree isolation, parallel execution)
- Self-healing automation (M5)
- Smart regression selection (M6)
- Defect root cause analysis (M8)
- Risk-based prioritization (M4)
- Full metrics platform with cost attribution
- Event bus (external broker)
- Team onboarding profiles (Strict/Advisory/Custom)
- Skill versioning and governance

## 18. M1-M8 QA Mapping (Cross-reference)

| Measure | Phase | Owner |
|---------|-------|-------|
| M1 TDD-driven SDLC | P2 | Developer role (TDD skill) + QA gate |
| M2 Requirement → test case | P2 | Requirements Analyst role |
| M3 Code gen with skills | P2 | QA Evaluator role (test gen skills) |
| M4 Risk-based prioritization | P3 | Quality Gate Engine |
| M5 Self-healing automation | P3 | QA Evaluator role (self-healer skill) |
| M6 Regression intelligence | P3 | QA Evaluator role (regression-selector skill) |
| M7 Simulation test data | P2 | QA Evaluator role (test-data-gen skill) |
| M8 Defect root cause | P3 | QA Evaluator role (defect-analyzer skill) |

## 19. Organizational Model

| Role | Responsibility |
|------|---------------|
| **QA CoE** | Maintains QA skills, QA Service, Knowledge Base testing standards. Designs QA Evaluator role. Advises on quality gates. |
| **AI Governance** | Defines Copilot CLI policies, approves agent roles, manages WORKFLOW.md standards, controls cost budgets. |
| **Platform Engineering** | Operates Symphony orchestrator, maintains tracker adapters, manages infrastructure. |
| **Business Teams** | Configure WORKFLOW.md per project, contribute domain knowledge, consume agent capabilities. |

## 20. Resolved Design Decisions

All design decisions from the original draft have been resolved:

| # | Decision | Resolution |
|---|---|---|
| 1 | **JIRA workflow mapping** | Hybrid: company-wide defaults ship with Symphony; teams override per-state in WORKFLOW.md. See Section 8.4. |
| 2 | **Multi-repo orchestration** | One Symphony instance; one workspace per repo; multi-repo issues use a shared parent directory with sub-workspaces. See Section 9.1. |
| 3 | **Cost budget model** | Per-team monthly token budget; Platform Engineering allocates; 80% alert + 100% hard stop. See Section 14.3. |
| 4 | **Agent model diversity** | All roles use Copilot CLI; different models per role by default (GPT-5.3-Codex for Developer, Gemini for QA, Sonnet for others); overridable in WORKFLOW.md. See Section 4.3. |
| 5 | **AS400 integration depth** | Full integration via approved tooling; direct database access prohibited; all AS400 calls logged. See Section 15. |
| 6 | **Human override protocol** | Tracker state change = hard kill; `@symphony` comment commands = soft guidance (pause/redirect/stop). See Section 22. |
| 7 | **Offline/air-gapped** | Not supported in P1; Symphony requires full internet access. See Section 15. |
| 8 | **Progressive rollout** | QA CoE dogfoods first; then other teams with CoE as reference implementation. See Section 17. |

## 21. Context Management Strategy

Long-horizon agent sessions require active context management. Symphony enforces three complementary strategies:

### 21.1 Structured Progress File (JSON)

Each workspace maintains `.symphony/progress.json` — a JSON feature checklist initialized by the first agent session and updated incrementally. Agents may only change `passes` fields; they must not delete or rewrite features.

```json
{
  "issue": "PROJ-123",
  "features": [
    {
      "id": "f1",
      "description": "User can submit payment form with valid card details",
      "steps": ["Navigate to checkout", "Fill card form", "Submit", "Verify confirmation page"],
      "passes": true,
      "completed_at": "2026-03-26T10:00:00Z"
    },
    {
      "id": "f2",
      "description": "Payment fails gracefully with invalid card",
      "steps": ["Submit form with invalid card", "Verify error message shown"],
      "passes": false,
      "completed_at": null
    }
  ]
}
```

**Why JSON over Markdown:** Agents are more likely to append to or overwrite markdown files inappropriately. JSON schema makes accidental corruption detectable and reversible.

### 21.2 Context Resets for Long Phases

When a session nears context limit, Symphony performs a context reset instead of relying solely on compaction:

1. **Create handoff artifact:** Agent writes `.symphony/handoff-<timestamp>.md` with: current feature, what's done, what's next, key decisions made, gotchas discovered.
2. **Reset session:** Start a new Copilot CLI session with the phase initialization prompt + handoff artifact.
3. **Continue from checkpoint:** New session reads `progress.json`, `notes.md`, and handoff artifact to resume without re-doing completed work.

Context resets provide a clean slate (addressing "context anxiety" in some models) at the cost of handoff overhead. Compaction is still used within a session for routine growth; resets are the fallback when compaction is insufficient.

### 21.3 Structured Notes (Agent-Written Memory)

Agents maintain `.symphony/notes.md` for persistent memory across sessions. This file is agent-written and human-readable. Format is free-form but structured by convention:

```markdown
## Architecture Decisions
- Used Repository pattern for DB layer (not ORM) to match team standard

## Gotchas
- Payment API returns 200 with error in body on invalid card (not 4xx)

## Next Steps
- [ ] Handle 3DS redirect flow (AC #4)
- [ ] Write integration test for decline scenario
```

Notes persist across context resets and survive orchestrator restarts. They are included in the context reset handoff artifact.

## 22. Sprint Contract Protocol

Inspired by the generator-evaluator architecture in Anthropic's harness research: before the Developer writes code for a feature chunk, Developer and QA Evaluator negotiate a **Sprint Contract** that defines what "done" looks like.

### 22.1 Contract Structure

```json
{
  "sprint": 1,
  "feature_ids": ["f1", "f2"],
  "acceptance_criteria": [
    "Payment form submits successfully with valid Visa/Mastercard/Amex",
    "Invalid card number shows 'Invalid card number' error inline",
    "Submit button disabled while processing"
  ],
  "test_criteria": [
    {
      "id": "tc1",
      "description": "Submit form with valid card → confirmation page shown",
      "verification": "Playwright: navigate to /checkout, fill form, submit, assert URL = /confirmation"
    },
    {
      "id": "tc2",
      "description": "Submit form with 4242 4242 4242 4241 → error inline",
      "verification": "Playwright: fill form with invalid card, assert error element visible"
    }
  ],
  "out_of_scope": ["Saved payment methods", "PayPal integration"],
  "agreed_by": { "developer": true, "qa-evaluator": true },
  "created_at": "2026-03-26T09:00:00Z"
}
```

### 22.2 Contract Negotiation Flow

```
Developer proposes contract (feature chunk + test criteria)
    │
    ▼
QA Evaluator reviews → approves or requests changes
    │
    ├─ Changes requested → Developer revises → QA re-reviews
    └─ Approved → written to .symphony/artifacts/sprint-contract-N.json
    │
    ▼
Developer implements against contract
    │
    ▼
QA Evaluator evaluates against contract (not against own interpretation)
    │
    ├─ PASS → mark features in progress.json, advance to next sprint
    └─ FAIL → detailed feedback to Developer (specific failing criteria)
```

### 22.3 Why Sprint Contracts Matter

- **Prevents scope creep:** Out-of-scope is explicit.
- **Prevents premature completion:** Agent cannot declare victory without verifiable test criteria.
- **Reduces QA subjectivity:** Evaluator grades against agreed criteria, not its own judgment.
- **Enables context resets:** Contract artifact survives reset; new session picks up exactly where it left off.

**P1 implementation note:** In P1, Developer and QA Evaluator share a single Copilot CLI session (QA is prompt-injected, not a separate process). The sprint contract is generated by the Developer role, written to `.symphony/artifacts/sprint-contract-N.json`, and then the session is handed to the QA Evaluator prompt context which reads and evaluates against it. This simulates the two-agent negotiation within one session. In P3, when QA becomes an independent session, the contract file becomes the actual inter-agent communication channel with no changes to the schema.

Sprint contracts are generated and agreed in the same Copilot CLI session using agent-to-agent prompting. The QA Evaluator is prompted to be skeptical during contract review — to push back on vague criteria and demand measurability before agreeing.

## 23. Human Override Protocol

Humans can intervene in any active agent session at two levels:

### 23.1 Hard Kill (Tracker State Change)

Changing the issue's tracker state is the definitive stop signal. Symphony polls for state changes on every turn boundary. If the state no longer matches the expected state for the active phase, the session is terminated immediately and the workspace is preserved.

| Transition | Effect |
|---|---|
| Any state → `Rework` | Current session killed. Fresh branch from `origin/main`. Workpad preserved with failure reason. |
| Any state → `Done`/`Closed`/`Cancelled` | Session killed. Workspace cleaned up after TTL. |
| `In Progress` → `Human Review` (manual) | Session killed. Human takes over review. |

### 23.2 Soft Guidance (Comment Commands)

Post a comment on the issue with one of the following commands. Symphony reads new comments at each turn boundary.

| Command | Effect |
|---|---|
| `@symphony pause` | Suspend after current turn. Workspace preserved. Resume when human removes pause. |
| `@symphony stop` | Gracefully end current phase. Save progress. Do not advance to next phase. |
| `@symphony redirect: <instruction>` | Inject instruction into next agent turn as a priority override. |
| `@symphony skip: <feature_id>` | Mark a feature as out-of-scope for this issue (updates progress.json). |
| `@symphony context: <note>` | Inject a note into `.symphony/notes.md` for the agent to read. |

Commands are case-insensitive and can appear anywhere in the comment. Multiple commands in one comment are processed in order.

### 23.3 Audit

All override events (state changes + comment commands) are logged in `.symphony/history.jsonl` with the issuer's identity and timestamp.

## 24. End-to-End SDLC Lifecycle

This section provides the complete picture of how work flows through Symphony from idea to production. Every agent role in Section 4.3 has a defined entry and exit point in this lifecycle.

### 24.1 Complete Flow Diagram

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  IDEA / REQUEST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          │
          ▼ Issue created in JIRA/Linear (by human PM / BA / engineer)
  ┌───────────────┐
  │  Backlog      │ ← needs-design label?
  └───────┬───────┘       │
          │               ▼
          │     ┌─────────────────────────┐
          │     │  Architecture / Design  │ → ADR, system design doc
          │     │  Agent                  │   API contracts
          │     └────────────┬────────────┘
          │                  │ Remove needs-design
          ▼                  ▼
  ┌───────────────┐
  │     Todo      │ ← needs-analysis label?
  └───────┬───────┘       │
          │               ▼
          │     ┌──────────────────────────┐
          │     │  Requirements Analyst    │ → Structured AC, test matrix,
          │     │  Agent                   │   ambiguity flags
          │     └────────────┬─────────────┘
          │                  │ Remove needs-analysis
          ▼                  ▼
          │ [Developer Agent picks up]
  ┌───────────────┐
  │  In Progress  │◄──────────────────────────────────────────────────┐
  └───────┬───────┘                                                    │
          │                                                            │
          │  Developer Agent (GPT-5.3-Codex)                          │
          │  ├─ Phase Init (get bearings, smoke test, progress.json)   │
          │  ├─ Sprint Contract negotiation with QA Evaluator          │
          │  ├─ TDD: test first, then implement, feature by feature    │
          │  ├─ Spawns subagents: parallel modules / debugging         │
          │  └─ Creates PR, updates workpad                            │
          │                  │                                         │
          │                  ▼ (internal phase)                        │
          │     ┌──────────────────────────┐                          │
          │     │  QA Evaluator            │ (Gemini 3 Pro)           │
          │     │  Agent                   │                          │
          │     │  ├─ Evaluates sprint     │                          │
          │     │  │  contracts (iterative │                          │
          │     │  │  GAN-style loops)     │                          │
          │     │  ├─ 3 dimensions:        │                          │
          │     │  │  pass rate / coverage │                          │
          │     │  │  / acceptance         │                          │
          │     │  └─ Verdict: PASS/FAIL   │                          │
          │     └────────┬─────────────────┘                          │
          │           FAIL│   PASS                                     │
          │              │    │                                        │
          │      state:Rework  └──── state:Human Review                │
          │         (fresh branch                                      │
          │          from main) ──────────────────────────────────────┘
          │
          ▼
  ┌───────────────┐
  │ Human Review  │
  └───────┬───────┘
          │  (parallel, async)
          ├──── Code Reviewer Agent (Claude Sonnet 4.6) → PR review comments
          ├──── Security Agent (Claude Sonnet 4.6) → SAST, deps, OWASP
          └──── Human reviewer ← makes final approval decision
                    │
             Critical finding?
             ├─ YES → state:Rework
             └─ NO (human approves) → state:Merging
                    │
                    ▼
  ┌───────────────┐
  │    Merging    │
  └───────┬───────┘
          │  DevOps Agent (Claude Sonnet 4.6)
          │  ├─ Merge PR to main
          │  ├─ Trigger / monitor CI/CD pipeline
          │  └─ Confirm deployment
          │
          ├─ CI FAIL → state:Human Review (with error context)
          └─ Deploy OK → state:Done
                    │
                    ▼
  ┌───────────────┐
  │     Done      │ (async, post-merge)
  └───────┬───────┘
          ├──── Release Manager Agent → changelog, version tag, release notes
          └──── Documentation Agent  → API docs, architecture diagram updates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PRODUCTION INCIDENT PATH (parallel track, pre-empts queue)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Label: incident (P0/P1)
          │
          ▼
  Incident Response Agent
  ├─ Log analysis + root cause (Claude Sonnet 4.6)
  ├─ Hotfix implementation (GPT-5.3-Codex)
  └─ Incident report in workpad
          │
          ▼ Emergency fast-track
  Human Review → Merging → Done + post-mortem
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 24.2 Agent Responsibility Matrix

| Tracker State | Active Agents | Human Role |
|---|---|---|
| Backlog | Architecture Agent (if `needs-design`) | Creates issues, sets labels |
| Todo | Requirements Analyst (if `needs-analysis`) | Reviews AC, approves issue |
| In Progress | Developer + QA Evaluator (sequential internal) | Available for override only |
| Human Review | Code Reviewer + Security Agent (parallel, async) | Final approval/rejection |
| Rework | Developer + QA Evaluator (full reset) | Reviews rework scope if needed |
| Merging | DevOps Agent | Notified of deploy status |
| Done | Release Manager + Documentation (async) | Approves release notes |
| Incident | Incident Response Agent (pre-empts queue) | Reviews hotfix, approves merge |

### 24.3 SDLC Time Budget (Reference)

Rough estimates for planning — actual times depend on issue complexity and model speed.

| Phase | Typical Duration | Max (configurable) |
|---|---|---|
| Requirements Analysis | 5–15 min | 30 min |
| Architecture / Design | 20–60 min | 2 hr |
| Development | 30 min – 4 hr | 8 hr |
| QA Evaluation | 15–45 min | 2 hr |
| Code Review (automated) | 5–15 min | 30 min |
| Security Scan | 5–20 min | 1 hr |
| DevOps / Deploy | 10–30 min | 1 hr |
| Release Notes | 5–10 min | 30 min |

## 25. Concurrency & Capacity Model

### 25.1 Queue Architecture

Symphony maintains a priority queue of eligible issues per team. Issues are evaluated each polling cycle and dispatched according to available capacity.

```
Priority Levels (highest → lowest):
  P0: incident        — pre-empts any running non-incident session
  P1: critical        — fills next available slot immediately
  P2: high            — normal queue priority
  P3: medium          — normal queue priority
  P4: low             — fills slots only when P0–P3 backlog is empty
```

```yaml
# WORKFLOW.md
concurrency:
  max_concurrent_global: 20        # Symphony-wide limit (governed by Copilot API rate limits)
  max_per_team: 3                  # No team monopolizes the orchestrator
  max_per_issue: 4                 # Max subagents per issue (parent + 3 subagents)
  priority_preemption: true        # P0/P1 can preempt running P3/P4 sessions
  preempt_at_turn_boundary: true   # Never interrupt mid-turn; wait for clean boundary
  issue_timeout_hr: 8              # Park issue if phase exceeds this; notify human
```

### 25.2 Concurrency Safety

- **Each issue has exactly one active agent session at a time.** Subagents are children of that session, not independent sessions.
- **Two-phase locking:** Orchestrator acquires a lock on each issue before dispatching. Prevents duplicate dispatch during parallel polling cycles. P1: in-process lock (single Python process, threading.Lock). P3: distributed lock (Redis or similar) for multi-instance deployment.
- **Idempotent dispatch:** If Symphony restarts mid-dispatch, it checks `.symphony/phase.json` to determine if a session is already in progress before starting a new one.

### 25.3 Resource Signals

Symphony dynamically adjusts concurrency based on:
- Copilot API error rate (429 responses → back off)
- Tracker API latency (slow tracker → reduce polling frequency)
- Team budget utilization (>90% monthly budget → pause non-critical issues)
- Workspace disk usage (>80% → block new workspace creation, alert admin)

## 26. AI Governance Integration

### 26.1 Governance Role in Symphony

AI Governance does not operate Symphony day-to-day. Their role is:
1. **Policy setting** — Define acceptable use, approved models, quality gate minimums
2. **Approval** — Sign off on new agent.md definitions before activation
3. **Oversight** — Receive regular reports on agent behavior, quality, and cost
4. **Intervention** — Can pause Symphony globally or per-team

### 26.2 Agent Approval Workflow

New or modified `agent.md` files require AI Governance review before activation in any production team:

```
1. Engineer or CoE submits agent.md PR to .github/agents/
2. PR includes:
   - Role definition
   - Trigger conditions
   - Guardrails
   - Quality gate configuration
   - Risk assessment (what can this agent break?)
3. AI Governance reviewer approves/rejects via PR review
4. On approval: agent.md is tagged with approval metadata:

   # Approved: 2026-03-26
   # Approved-by: AI Governance (governance@company.com)
   # Risk-level: medium
   # Review-due: 2026-09-26  ← semi-annual re-review

5. Symphony validates approval metadata at startup;
   agents without valid approval are disabled with a warning.
```

### 26.3 Governance Reporting

Weekly automated report delivered to AI Governance:

```markdown
## Symphony Weekly Report — Week of 2026-03-24

### Throughput
- Issues completed: 47 (↑12% vs last week)
- Avg cycle time: 4.2 hr (↓8%)
- Phases completed: 183

### Quality
- QA gate pass rate: 89% (target: 85%) ✓
- Code review rejection rate: 12%
- Defect escape rate: 0.8% (↑ alert: was 0.2% last week)

### Cost
- Total tokens used: 8.4M (budget: 10M) — 84% utilized
- Cost per issue (avg): $4.20
- Top 3 teams by cost: payments-api ($890), web-checkout ($720), core-api ($650)

### Security
- Security findings: 3 Critical (all blocked PR), 12 High (human review), 28 Medium
- Critical finding types: SQL injection (2), hardcoded secret (1)

### Model Usage
- GPT-5.3-Codex: 42% of tokens (Developer role)
- Gemini 3 Pro: 28% of tokens (QA Evaluator)
- Claude Sonnet 4.6: 30% of tokens (all other roles)

### Human Override Events
- @symphony stop: 3 (reasons logged in audit trail)
- State override (human): 7
- Agent pre-emptions (P0/P1): 2

### Governance Actions Required
- [ALERT] Defect escape rate spike on payments-api — review recommended
- [RENEWAL] security-agent.md approval expires 2026-04-01 — re-review needed
```

### 26.4 Compliance Audit Trail (Insurance Regulatory)

For insurance industry compliance (internal audit, regulatory review):

| Requirement | Symphony Implementation |
|---|---|
| **Who did what** | All state transitions logged with actor (agent role + session ID, or human username) |
| **When** | ISO 8601 timestamps on all log entries |
| **What changed** | Before/after state for every tracker transition; PR diff links |
| **Why** | Gate evaluation results, workpad notes, sprint contracts preserved as artifacts |
| **Immutability** | `.symphony/history.jsonl` is append-only; stored in compliance-grade object storage |
| **Retention** | 90 days hot (searchable), 2 years cold archive (regulatory minimum) |
| **Access control** | Audit logs readable by compliance team (`audit:read` role); not modifiable by anyone |

### 26.5 Model Governance

AI Governance maintains an approved model list. Symphony only allows models on this list:

```yaml
# Symphony global config (managed by AI Governance)
approved_models:
  - claude-sonnet-4.6
  - gpt-5.3-codex
  - gemini-3-pro
  # Unapproved: claude-opus-4.6 (cost), gpt-5.4 (not yet evaluated)
```

Using an unapproved model in WORKFLOW.md causes Symphony to reject the config and log a compliance violation.

## 27. Incremental Adoption Maturity Model

Teams do not need to adopt Symphony all at once. This maturity model defines a progressive path from zero to full AI-native SDLC.

### 27.1 Maturity Levels

```
Level 0 — Ad-hoc
  Engineers use Copilot CLI manually, no orchestration.
  Quality: depends on individual discipline.
  Symphony role: none.

Level 1 — Developer Automation
  Symphony handles Developer role only.
  Engineers review and QA manually.
  Value: consistent code style, TDD enforced, faster implementation.
  Config: developer.md only in WORKFLOW.md.

Level 2 — Dev + QA
  Symphony adds QA Evaluator phase after Developer.
  Manual human review and merge.
  Value: automated quality gate, reduced manual testing burden.
  Config: developer.md + qa-evaluator.md.

Level 3 — Full Inner Loop
  Symphony runs: Analyst → Developer → QA → Code Reviewer.
  DevOps and Release still manual.
  Value: full automated SDLC from Todo to Human Review.
  Config: 4 roles active.

Level 4 — End-to-End
  All roles active: full pipeline from Backlog to Done.
  Human gates only at: architecture decisions, merge approval, incident hotfix.
  Value: Symphony manages entire development lifecycle.
  Config: all agent.md files active.

Level 5 — AI-Native (Future)
  Symphony uses retrospective data to improve its own skills and quality gates.
  Agent performance tracked over time; underperforming agents flagged for skill update.
  Skill versions managed via Skill Hub governance.
  Value: self-improving SDLC orchestration.
  Config: requires full observability pipeline + CoE skill governance process.
```

### 27.2 Adoption Timeline (Reference)

| Level | Typical Onboarding Time | Prerequisites |
|---|---|---|
| 0 → 1 | 1 sprint | WORKFLOW.md configured, workspace dir set up |
| 1 → 2 | 1–2 sprints | QA skills deployed, quality gate thresholds agreed |
| 2 → 3 | 2–3 sprints | Code reviewer + analyst agent.md approved by AI Governance |
| 3 → 4 | 1–2 sprints | CI/CD integration, DevOps agent.md approved |
| 4 → 5 | Ongoing | Full observability, CoE skill governance active |

### 27.3 Onboarding Checklist

For each team onboarding to Symphony:

- [ ] WORKFLOW.md created with pipeline configuration
- [ ] Target maturity level agreed with AI Governance
- [ ] Agent.md files submitted for Governance approval
- [ ] Quality gate thresholds agreed (profile selection: Strict/Advisory/Custom available from P3; P1/P2 teams use Advisory defaults)
- [ ] Team budget allocated by Platform Engineering
- [ ] JIRA/Linear webhook configured
- [ ] Workspace storage provisioned
- [ ] Pilot issues selected (non-critical, well-defined AC)
- [ ] Rollback plan documented (what to do if Symphony produces bad code)
- [ ] Team briefing: what Symphony does, what humans must still do, how to override

## 28. WORKFLOW.md Template System

WORKFLOW.md is the single configuration file per project. It has two layers: YAML front matter (orchestration config) and a Liquid/Jinja body (prompt templates).

### 28.1 Complete Front Matter Schema

```yaml
---
# ── Orchestrator Identity ──────────────────────────────────────────────
project:
  name: "Payments API"
  team: "payments-api"
  repo: "github.com/company/payments-api"
  tracker: linear           # linear | jira
  tracker_project: "PAY"    # JIRA project key or Linear team identifier

# ── Pipeline Definition ───────────────────────────────────────────────
pipeline:
  phases:
    - role: developer
      trigger: { states: [Todo, In Progress, Rework] }
      gate: null
      on_success: phase:qa-evaluator
      on_failure: null
    - role: qa-evaluator
      trigger: { internal: true }
      gate: qa_gate
      on_success: state:Human Review
      on_failure: state:Rework
    # ... additional phases

    # Event-triggered phases (fire-and-forget, do not block main pipeline):
    - role: security
      trigger: { events: [pr.created], labels: [needs-security-review] }
      on_success: label:security-passed
      on_failure: state:Rework

    - role: release-manager
      trigger: { events: [pr.merged] }
      on_success: null

    - role: documentation
      trigger: { events: [pr.merged], labels: [needs-docs] }
      on_success: null

# ── Quality Gates ──────────────────────────────────────────────────────
quality_gates:
  qa_gate:
    profile: Advisory         # Strict | Advisory | Custom
    dimensions:
      pass_rate:  { threshold: 100, policy: strict }
      coverage:   { threshold: 80,  policy: strict }
      acceptance: { threshold: 100, policy: strict }   # Advisory profile: QA gate is strict
    on_fail: rework
    on_inconclusive: advisory

# ── Model Overrides ────────────────────────────────────────────────────
models:
  developer:    gpt-5.3-codex          # override per-role (must be on approved list)
  qa-evaluator: gemini-3-pro

# ── JIRA State Mapping (optional overrides) ───────────────────────────
jira_state_mapping:
  "Awaiting Sign-off": Human Review
  "Ready to Deploy": Merging

# ── JIRA Field Overrides ─────────────────────────────────────────────
jira_fields:
  ac_field: "customfield_10020"  # Custom field for acceptance criteria (default: description)

# ── Concurrency & Budget ──────────────────────────────────────────────
concurrency:
  max_per_team: 3
  priority_preemption: true
  issue_timeout_hr: 8

cost_budget:
  team: payments-api
  monthly_token_limit: 5_000_000
  alert_threshold: 0.80
  hard_stop: true

# ── Subagent Config ───────────────────────────────────────────────────
subagent:
  max_concurrent: 3
  timeout_ms: 600000
  isolation: worktree

# ── Workspace ─────────────────────────────────────────────────────────
workspace:
  root: ~/code/symphony-workspaces
  ttl_days: 7               # Auto-cleanup after issue reaches Done
  stale_session_ttl_hr: 24  # Clean up subagent worktrees after this duration
---
```

### 28.2 Prompt Template Body

The Markdown body below the front matter contains Liquid/Jinja templates rendered when Symphony assembles agent prompts.

```liquid
## Developer Prompt

You are working on {{ issue.identifier }}: {{ issue.title }}

**Acceptance Criteria:**
{% for ac in issue.acceptance_criteria %}
- {{ ac }}
{% endfor %}

**Branch:** {{ issue.branch_name | default: "to be created" }}
**PR:** {{ artifacts.developer.pr_url | default: "not yet created" }}

{% if previous_phases contains "qa-evaluator" %}
**Previous QA Feedback:**
{{ artifacts.qa_evaluator.report_summary }}
{% endif %}

**Working Directory:** {{ workspace.path }}

Start with the Phase Initialization Protocol, then implement one feature at a time.
```

### 28.3 Template Variable Reference

| Variable | Type | Description |
|---|---|---|
| `issue.identifier` | string | e.g. `PAY-123` |
| `issue.title` | string | Issue title |
| `issue.description` | string | Full issue body |
| `issue.acceptance_criteria` | list | Extracted AC items |
| `issue.labels` | list | Current labels |
| `issue.priority` | string | critical/high/medium/low |
| `issue.url` | string | Link to tracker issue |
| `artifacts.<role>.*` | object | Phase artifacts from previous roles |
| `workspace.path` | string | Absolute workspace directory |
| `workspace.repo` | string | Repo URL |
| `phase.current` | string | Current phase name |
| `phase.turn` | int | Current turn number |
| `phase.context_usage_pct` | float | Context window usage 0.0–1.0 |
