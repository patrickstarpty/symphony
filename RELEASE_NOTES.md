# Release Notes

---

## v0.2.0 — Phase 2: Dashboard + Observability

**Released:** 2026-03-06

### Highlights

Symphony now includes a built-in web dashboard and REST API for real-time monitoring. The `WORKFLOW.md` file is watched for changes and hot-reloaded without restarting the daemon. All agent sessions are tracked with token usage, runtime, and success/failure metrics.

### New Features

#### Web Dashboard & REST API
- **FastAPI HTTP server** starts automatically on `http://localhost:3000` alongside the orchestrator
- **Built-in HTML dashboard** — dark-themed, polls every 3 seconds, zero build step required
- **React SPA dashboard** (optional) — Vite 5 + React 18 + TypeScript + Tailwind CSS 3
- **6 REST endpoints:**
  - `GET /api/v1/health` — uptime, running session count
  - `GET /api/v1/state` — full orchestrator state + metrics (main polling endpoint)
  - `GET /api/v1/sessions` — running + recent sessions
  - `GET /api/v1/sessions/{id}` — single session detail
  - `POST /api/v1/refresh` — force re-poll the tracker
  - `GET /api/v1/watcher` — workflow file watcher status
- CORS enabled for dev convenience

#### Workflow Hot-Reload
- **watchdog-based file watcher** monitors `WORKFLOW.md` for changes
- Debounced reload (1-second window) — rapid saves trigger only one reload
- **Last-known-good fallback** — invalid config changes are rejected, previous config preserved
- Async callback bridges watchdog's thread into the asyncio event loop

#### Token Accounting & Metrics
- **Per-session metrics:** prompt tokens, completion tokens, duration, turns, success/failure
- **Aggregate metrics:** total sessions, tokens, runtime, rate limit events
- Metrics snapshot API for the dashboard
- Keeps last 50 completed sessions in memory

#### Structured Logging Improvements
- `bind_context()` / `clear_context()` — per-task log context using `structlog.contextvars`
- Every log line within an agent session automatically includes `issue_id` and `session_id`
- Quieted noisy libraries: watchdog, uvicorn, fastapi

#### New CLI Flags
- `--port <N>` — dashboard server port (default: 3000)
- `--no-dashboard` — disable the web server entirely
- `--no-watch` — disable workflow file watching

### New Files

| File | Lines | Purpose |
|------|------:|---------|
| `src/symphony/server.py` | 413 | FastAPI server + REST API + inline HTML dashboard |
| `src/symphony/watcher.py` | 180 | Workflow hot-reload with watchdog |
| `src/symphony/metrics.py` | 230 | Token accounting + session metrics |
| `dashboard/` (14 files) | 596 | React SPA (App, components, hooks, types, config) |

### Modified Files

| File | Change |
|------|--------|
| `src/symphony/orchestrator.py` | Metrics integration in dispatch/completion, `update_prompt_template()` |
| `src/symphony/cli.py` | Full rewrite — server, watcher, metrics wiring, new flags |
| `src/symphony/log.py` | `bind_context()`, `clear_context()`, quiet libraries |
| `pyproject.toml` | Removed optional-dependencies (server deps are now core) |
| `.gitignore` | Added `dashboard/node_modules/`, `dashboard/dist/` |

### New Dependencies

- `fastapi` 0.135.1
- `uvicorn[standard]` (already present, now core)
- `watchdog` 6.0.0

### Tests

- **39 new tests** (18 metrics, 14 server, 7 watcher)
- Fixed pre-existing concurrency limit test race condition (mock runner completing too fast)
- **95 tests total, all passing**

### Dashboard Components

| Component | Description |
|-----------|-------------|
| `OverviewStats` | Running / completed / failed / retrying counts, total tokens, uptime |
| `RunningTable` | Active agent sessions with duration, turns, stall detection |
| `RetryQueue` | Issues queued for retry with attempt count and countdown |
| `RecentSessions` | Completed sessions with status, duration, token usage |
| `ConfigCard` | Current orchestrator configuration display |
| `StatusBadge` | Color-coded status badges (running/success/failed/retry) |
| `usePolling` | React hook for interval-based API polling |

---

## v0.1.0 — Phase 1: MVP — "The Loop Works"

**Released:** 2026-03-04

### Highlights

First working version of Symphony. A CLI daemon that continuously polls an issue tracker, creates isolated workspaces, and dispatches AI coding agents to resolve issues automatically. Includes a demo project with a buggy calculator to test the full pipeline.

### Features

#### Core Orchestrator
- **Poll-dispatch-reconcile loop** — continuously polls the tracker and dispatches agents
- **Concurrency control** — global limit (`max_concurrent_agents`) and per-state limits
- **Retry with exponential backoff** — configurable max retries, 10s → 20s → 40s → ... up to 5min cap
- **Stall detection** — kills agents with no activity beyond the timeout
- **Reconciliation** — cancels agents if issues move to terminal states
- **Graceful shutdown** — SIGINT/SIGTERM drains running sessions before exit

#### Issue Trackers
- **GitHub Issues adapter** — polls via REST API, normalizes to internal Issue model
- **File-based adapter** — reads issues from a local JSON file (no API key needed)
- **Pluggable tracker interface** — `TrackerClient` protocol for adding new adapters

#### Workspace Management
- **Isolated workspaces** — each issue gets its own directory under `.symphony-workspaces/`
- **Source directory copying** — copies your project into each workspace (excludes `.git`, `node_modules`, `.env`, etc.)
- **Git initialization** — each workspace is a git repo for diff capture
- **Path containment** — agents cannot escape their workspace directory
- **Lifecycle hooks** — setup, pre-run, post-run, cleanup (with timeouts)

#### AI Agent Runner
- **CrewAI integration** — agents run in-process with LiteLLM for model routing
- **File tools** — `FileReadTool`, `FileWriterTool`, `DirectoryReadTool`
- **Turn limit** — configurable max iterations per session
- **Result reports** — saved to `.symphony-workspaces/_results/` with agent output + git diff

#### Configuration
- **WORKFLOW.md** — YAML front matter for config + Liquid template for prompts
- **Environment variable resolution** — `$VAR` and `${VAR}` in config values
- **Typed config layer** — validated dataclasses with sensible defaults
- **Model routing** — any model supported by LiteLLM (`deepseek/deepseek-chat`, `gpt-4o`, etc.)

#### Demo Project
- Sample calculator project with 2 bugs (division by zero, missing power function)
- Pre-configured `WORKFLOW.md` and `issues.json` for immediate testing
- 30-second quickstart: `uv sync && uv run python -m symphony ./WORKFLOW.md`

### Files

| File | Lines | Purpose |
|------|------:|---------|
| `src/symphony/orchestrator.py` | 559 | Core poll-dispatch-reconcile loop |
| `src/symphony/agent_runner.py` | 331 | CrewAI agent with file tools |
| `src/symphony/workspace.py` | 306 | Workspace creation, copying, hooks |
| `src/symphony/cli.py` | 105 | CLI entry point with signal handling |
| `src/symphony/config.py` | 208 | Typed configuration layer |
| `src/symphony/tracker/github.py` | 205 | GitHub Issues adapter |
| `src/symphony/tracker/file.py` | 195 | File-based issue tracker |
| `src/symphony/workflow.py` | 143 | WORKFLOW.md parser |
| `src/symphony/models.py` | 127 | Domain models (Issue, State, etc.) |
| `src/symphony/log.py` | 64 | Structured logging setup |
| `src/symphony/prompt.py` | 76 | Liquid template renderer |
| `src/symphony/tracker/base.py` | 46 | TrackerClient protocol |
| **Total** | **2,368** | |

### Dependencies

- `crewai` 1.10.1 + `crewai-tools`
- `litellm` (model routing)
- `httpx` (async HTTP)
- `pyyaml` (YAML parsing)
- `python-liquid` (template rendering)
- `structlog` (structured logging)
- `uvicorn` (ASGI server, used in Phase 2)

### Tests

- **56 tests, all passing**
- Coverage: workflow loading, config validation, orchestrator dispatch/concurrency/retry, prompt rendering, workspace management, tracker normalization
