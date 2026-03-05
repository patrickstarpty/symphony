# Symphony Implementation Plan

## Project Overview

**Symphony** is a long-running automation service (CLI daemon) that continuously reads work from an issue tracker, creates an isolated workspace for each issue, and runs a coding agent session for that issue inside the workspace. It was created by OpenAI and published as a language-agnostic specification ([SPEC.md](https://github.com/openai/symphony/blob/main/SPEC.md), 75KB, 2110 lines, 18 sections).

The reference implementation is written in **Elixir/OTP with Phoenix LiveView**. This plan covers a **Python + React** re-implementation.

---

## What Symphony Is (and Is Not)

| Is | Is Not |
|---|---|
| A CLI daemon / background service | A web application |
| A scheduler and runner for coding agents | An AI agent itself |
| A tracker reader (polls issues) | A tracker writer (agents write back via tools) |
| An orchestrator with in-memory state | A database-backed job queue |
| Optionally has a web dashboard for monitoring | Required to have any UI |

### How Symphony Controls Agents

Symphony launches an external coding agent as a **child subprocess** and communicates via **JSON-RPC over stdio**. It does NOT contain an AI agent — it's the scheduler that decides **when** and **where** to run agents. The `WORKFLOW.md` prompt decides **what** the agent does.

Control mechanisms:
- **Concurrency limit** — max 10 simultaneous agents (configurable)
- **Per-state concurrency** — e.g., max 3 agents on "Todo" issues
- **Turn timeout** — kill agent if a single turn > 1 hour
- **Stall detection** — kill agent if no events for 5 minutes
- **Max turns** — stop after 20 turns per worker session
- **Reconciliation** — every poll tick, check if issue states changed; kill agent if issue is now terminal
- **Retry with exponential backoff** — 10s, 20s, 40s... up to 5min cap

---

## Key Architecture Decisions

### 1. No Linear / LINEAR_API_KEY Required

The spec's architecture explicitly supports pluggable tracker adapters:
- **Layer 5 "Integration Layer"** is labeled `(Linear adapter)` — a pluggable slot
- The core orchestrator only consumes a **normalized Issue model** (Section 4.1.1)
- The `linear_graphql` tool extension is explicitly **optional**

**Decision:** Use **GitHub Issues** as the default tracker (free, REST API, no API key purchase needed). Architect the tracker interface for easy addition of Linear, Jira, or file-based adapters later.

### 2. Agent Framework: CrewAI (Recommended) over MetaGPT

| Factor | CrewAI | MetaGPT |
|---|---|---|
| **Symphony fit** | Natural — issues map to tasks with custom agents | Awkward — multi-role SOP is overkill for issue work |
| **Production readiness** | v1.10.1, 141 releases, very active | v0.8.1, slower cadence |
| **Python version** | 3.10-3.13 | 3.9-3.11 only |
| **Runtime cost** | Lower — define exactly the agents you need | Higher — multi-role pipeline uses more tokens |
| **Dev effort** | ~21 days | ~24 days |

CrewAI's `Flow` = Symphony orchestrator. `Crew` = Symphony worker. `Task` = issue work.

Using CrewAI eliminates the entire subprocess/JSON-RPC/stdio protocol layer (spec Section 10), replacing ~500 lines of protocol code with ~50 lines of Crew definition. However, the `agent_runner.py` interface will be designed so Codex subprocess support can be added later.

### 3. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Runtime** | Python 3.12+ | asyncio for concurrent agent management |
| **Async** | `asyncio` | Natural fit for poll loop + subprocess; single event loop = single-authority state |
| **HTTP** | FastAPI + uvicorn | Fast, async-native, auto-generated OpenAPI docs |
| **YAML** | PyYAML | WORKFLOW.md front matter |
| **Templates** | python-liquid | Liquid-compatible, strict mode support |
| **File watcher** | watchdog | Cross-platform file system events |
| **HTTP client** | httpx | Async HTTP for tracker API calls |
| **Logging** | structlog | Structured JSON logging with context binding |
| **Agent (primary)** | CrewAI | In-process, simpler, no subprocess protocol |
| **Agent (optional)** | Subprocess + JSON-RPC | Codex app-server compatible (future) |
| **Frontend** | React 18 + TypeScript | Dashboard SPA |
| **Build** | Vite | Fast frontend build |
| **Styling** | Tailwind CSS | Utility-first, fast to build |
| **Testing** | pytest + pytest-asyncio | Async test support |

---

## AI-Assisted Development Cost

### With GitHub Copilot + Claude Opus 4.6

| Factor | Estimate |
|---|---|
| Developer time | ~27 working days (5-6 weeks) |
| Copilot subscription | $19-39/mo |
| Claude Opus 4.6 API cost | ~$300-500 over project |
| **Total AI tooling cost** | **~$340-540** |

### With GitHub Copilot + GPT-5.3 Codex

| Factor | Estimate |
|---|---|
| Developer time | ~27 working days (similar) |
| Copilot subscription | $19-39/mo |
| GPT-5.3 Codex API cost | ~$200-400 over project |
| **Total AI tooling cost** | **~$240-440** |

Both models are capable. Claude Opus 4.6 may have a slight edge on the orchestrator's complex reconciliation logic; GPT-5.3 Codex may be faster for straightforward CRUD/API code.

### Runtime Cost (per month, ~50 issues/day with CrewAI)

| Model | Monthly Cost |
|---|---|
| Claude Opus 4.6 | ~$600-1,200/mo |
| GPT-5.3 Codex | ~$400-800/mo |

---

## Spec Component Breakdown

The spec defines 8 main components across 18 sections:

| # | Component | Spec Sections | Complexity |
|---|---|---|---|
| 1 | Workflow Loader | 5.1, 5.2 | Low |
| 2 | Config Layer | 5.3, 6.1-6.4 | Medium |
| 3 | Issue Tracker Client | 11.1-11.5 | Medium |
| 4 | Orchestrator | 7.1-7.4, 8.1-8.6 | **High** |
| 5 | Workspace Manager | 9.1-9.5 | Medium |
| 6 | Agent Runner | 10.1-10.7 | **High** (subprocess) / Medium (CrewAI) |
| 7 | Prompt Construction | 12.1-12.4 | Low |
| 8 | Observability | 13.1-13.7 | Medium |

Supporting concerns: Failure Model (14), Security (15), Reference Algorithms (16), Test Matrix (17), Checklist (18).

---

## Phased Implementation Plan

### Phase 1: MVP — "The Loop Works" (~10 days)

**Goal:** CLI daemon that polls GitHub Issues, dispatches coding agents in isolated workspaces, handles retries, logs to stdout.

**Demo:** `python -m symphony ./WORKFLOW.md` picks up issues, launches agents, logs progress.

#### Project Structure

```
symphony/
├── pyproject.toml
├── README.md
├── WORKFLOW.md                  # Example workflow file
├── src/
│   └── symphony/
│       ├── __init__.py
│       ├── __main__.py          # CLI entry point
│       ├── cli.py               # argparse: positional workflow path, --port
│       ├── config.py            # Typed config layer
│       ├── workflow.py          # WORKFLOW.md loader + parser
│       ├── models.py            # Issue, RetryEntry, RunningEntry, OrchestratorState
│       ├── orchestrator.py      # Poll loop, dispatch, reconciliation, retry
│       ├── tracker/
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract TrackerClient protocol
│       │   └── github.py        # GitHub Issues adapter
│       ├── workspace.py         # Workspace manager + hooks
│       ├── agent_runner.py      # Agent launcher (CrewAI or subprocess)
│       ├── prompt.py            # Liquid template rendering
│       └── log.py               # Structured logging setup
├── tests/
│   ├── test_workflow.py
│   ├── test_config.py
│   ├── test_orchestrator.py
│   ├── test_workspace.py
│   ├── test_tracker.py
│   └── test_prompt.py
└── dashboard/                   # (Phase 2)
```

#### MVP Tasks

| # | Task | Days | Details |
|---|---|:---:|---|
| 1 | Project scaffolding + dependencies | 0.5 | pyproject.toml, package structure, dev tooling |
| 2 | `workflow.py` — WORKFLOW.md loader | 0.5 | YAML front matter + prompt body split, error classes |
| 3 | `config.py` — Typed config layer | 1 | Defaults, `$VAR` resolution, `~` expansion, validation |
| 4 | `models.py` — Domain model | 0.5 | Issue, RetryEntry, RunningEntry, OrchestratorState dataclasses |
| 5 | `tracker/github.py` — GitHub Issues adapter | 1.5 | 3 required operations, normalize to Issue model |
| 6 | `workspace.py` — Workspace manager | 1.5 | Create/reuse, sanitize key, path containment, 4 hooks with timeout |
| 7 | `prompt.py` — Prompt renderer | 0.5 | python-liquid strict mode, issue + attempt variables |
| 8 | `agent_runner.py` — Agent launcher | 1.5 | CrewAI in-process or Codex subprocess with JSON-RPC |
| 9 | `orchestrator.py` — Core loop | 3.5 | Poll tick, dispatch, reconciliation, retry/backoff, concurrency |
| 10 | `cli.py` — CLI entry point | 0.5 | Workflow path arg, signal handling, startup/shutdown |
| | **Phase 1 Total** | **10** | |

#### MVP Test Coverage (~15 tests)

- Workflow loader: valid file, missing file, bad YAML, non-map front matter
- Config: defaults, `$VAR` resolution, validation failures
- Workspace: create, reuse, sanitize key, path containment, hooks
- Orchestrator: dispatch eligible, skip claimed, concurrency limit, retry scheduling
- Prompt: render with issue+attempt, fail on unknown variable

---

### Phase 2: Dashboard + Observability (~6 days)

**Goal:** REST API + React dashboard for monitoring. Dynamic WORKFLOW.md reload.

**Demo:** Open `http://localhost:3000`, see running sessions updating in real-time.

#### Tasks

| # | Task | Days | Details |
|---|---|:---:|---|
| 1 | `server.py` — FastAPI HTTP server | 1 | `/api/v1/state`, `/api/v1/{id}`, `/api/v1/refresh`, error envelopes |
| 2 | `watcher.py` — Dynamic reload | 1 | watchdog file monitor, re-parse + re-validate, keep last-known-good on error |
| 3 | `metrics.py` — Token accounting | 1 | Per-session + aggregate tokens, runtime seconds, rate limits |
| 4 | React dashboard | 2 | Running table, retry queue, token totals, health indicators |
| 5 | Structured logging improvements | 1 | issue_id/identifier/session_id context, JSON + console formatters |
| | **Phase 2 Total** | **6** | |

#### Dashboard Structure

```
dashboard/
├── package.json
├── vite.config.ts
├── index.html
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── api.ts              # fetch /api/v1/state
│   ├── components/
│   │   ├── RunningTable.tsx  # Active sessions table
│   │   ├── RetryQueue.tsx    # Retry queue table
│   │   ├── TokenTotals.tsx   # Aggregate counters
│   │   ├── RateLimits.tsx    # Rate limit display
│   │   └── StatusBadge.tsx   # Health indicator
│   └── hooks/
│       └── usePolling.ts     # Poll /api/v1/state every 3s
```

---

### Phase 3: Production Hardening (~6 days)

**Goal:** Full spec conformance per Section 18.1. Comprehensive tests. Security invariants.

#### Tasks

| # | Task | Days | Details |
|---|---|:---:|---|
| 1 | Full reconciliation | 1 | Stall detection, tracker state refresh, terminal/non-active handling |
| 2 | Blocker rule + per-state concurrency | 0.5 | Todo blockers check, `max_concurrent_agents_by_state` |
| 3 | Full hook lifecycle | 0.5 | All 4 hooks with correct fatal/non-fatal semantics |
| 4 | Security invariants | 0.5 | Path containment, sanitization, secret masking, hook output truncation |
| 5 | Comprehensive test suite (45+ tests) | 3 | Cover all Section 17 categories |
| 6 | Graceful shutdown | 0.5 | SIGINT/SIGTERM → drain → cleanup → exit |
| | **Phase 3 Total** | **6** | |

#### Test Matrix (from Spec Section 17)

| Category | Tests |
|---|---|
| 17.1 Workflow/Config Parsing | 8 tests |
| 17.2 Workspace Manager + Safety | 12 tests |
| 17.3 Issue Tracker Client | 9 tests |
| 17.4 Orchestrator Dispatch/Reconciliation/Retry | 14 tests |
| 17.5 Agent App-Server Client | 10 tests |
| 17.6 Observability | 4 tests |
| 17.7 CLI Lifecycle | 5 tests |
| **Total** | **62 tests** |

---

### Phase 4: Extensions + Multi-Tracker (~5 days)

**Goal:** Pluggable tracker adapters, persistent state, Docker support, enhanced dashboard.

#### Tasks

| # | Task | Days | Details |
|---|---|:---:|---|
| 1 | Pluggable tracker system | 1.5 | Linear GraphQL adapter, file-based adapter, Jira adapter |
| 2 | `linear_graphql` tool extension | 1 | Optional client-side tool for Codex/CrewAI sessions |
| 3 | Enhanced dashboard | 1 | Issue detail page, events timeline, log viewer, dark mode |
| 4 | Operational improvements | 1.5 | SQLite retry persistence, Docker support, health endpoint |
| | **Phase 4 Total** | **5** | |

---

## Timeline Summary

```
Week 1-2:  Phase 1 — MVP (CLI daemon, core loop, agent runner)
           ════════════════════════════════ [DEMO]

Week 3:    Phase 2 — Dashboard + API + dynamic reload
           ═══════════════════ [MONITORING]

Week 4:    Phase 3 — Production hardening + full tests
           ═══════════════════ [SPEC CONFORMANCE]

Week 5:    Phase 4 — Extensions + multi-tracker
           ═══════════════════ [PRODUCTION READY]
```

| Phase | Days | Cumulative | What Works |
|---|:---:|:---:|---|
| **MVP** | 10 | 10 | CLI daemon polls tracker, dispatches agents, retries, logs to stdout |
| **Dashboard** | 6 | 16 | Web UI shows running sessions, retry queue, token usage. Config hot-reload. |
| **Hardening** | 6 | 22 | Full spec conformance. 62 tests. Security invariants. |
| **Extensions** | 5 | 27 | Multiple trackers, persistent state, Docker, enhanced dashboard. |

---

## What is Linear? (Context)

Linear is a **modern, developer-centric project management and issue tracking tool** (founded 2019). It's known for its speed, keyboard-first UX, and opinionated workflows. Think of it as a modern alternative to Jira.

- **GraphQL API** — what Symphony uses to poll issues and read state
- **States:** Backlog → Todo → In Progress → In Review → Done → Canceled
- **Pricing:** Free (250 issues) → $8/user/mo → $14/user/mo → Enterprise

**Competitors:** Jira, GitHub Issues, GitLab Issues, Shortcut, Plane.so, Asana, ClickUp, Notion, Azure DevOps

**For this project:** We replace Linear with **GitHub Issues** (free, no API key purchase needed).

---

## Tracker Adapter Options

| Tracker | Effort | Pros | Cons |
|---|---|---|---|
| **GitHub Issues** (default) | Included in MVP | Free, REST API, no extra key needed | No native "In Progress" (use labels) |
| **File-based (JSON/YAML)** | +0.5 day | Zero dependencies, great for dev/testing | Manual, no web UI |
| **Linear** | +1.5 days | What the spec was designed for | Requires paid plan + LINEAR_API_KEY |
| **Jira** | +2-3 days | Enterprise standard | Complex API, heavy field mapping |
| **Plane.so** | +1.5 days | Open-source Linear alternative | Less mature API |
| **Notion** | +2-3 days | Nice UI | Complex field mapping |

---

## Risk Factors

1. **Agent Runner Protocol** — The JSON-RPC-over-stdio protocol with Codex app-server is the least-documented part. CrewAI avoids this entirely but limits compatibility with the original Codex ecosystem.
2. **Concurrency correctness** — The orchestrator must be single-authority for state mutation. With `asyncio` this is natural (single-threaded event loop), but careless task spawning could introduce races.
3. **Tracker normalization** — The alternative tracker (GitHub Issues) must produce normalized Issue objects with all required fields (including `blocked_by`, `labels`, `priority`).
4. **CrewAI stability** — CrewAI is actively developed (141 releases). API changes between versions may require adjustments.

---

## Success Criteria

- [ ] **Phase 1:** `python -m symphony ./WORKFLOW.md` picks up a GitHub issue, launches agent, logs completion
- [ ] **Phase 2:** `http://localhost:3000` shows live dashboard; editing WORKFLOW.md changes behavior without restart
- [ ] **Phase 3:** `pytest tests/ -v` → 62 tests pass; all Section 18.1 checklist items verified
- [ ] **Phase 4:** Switch `tracker.kind: file` → issues load from local JSON; Docker container runs successfully
