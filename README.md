# ♫ Symphony

**Autonomous coding agents, orchestrated.**

Symphony is a daemon that picks up issues from your tracker, spins up isolated workspaces, and lets AI agents fix them — while you watch everything happen in a real-time dashboard.

<p align="center">
  <code>http://localhost:3000</code> — Dashboard auto-starts with the daemon
</p>

---

## ✨ What You Get

| | |
|---|---|
| **🖥 Live Dashboard** | Real-time web UI showing running agents, token usage, retry queue, and session history |
| **🔄 Continuous Loop** | Polls your issue tracker, dispatches agents, retries on failure — fully autonomous |
| **🔒 Isolated Workspaces** | Each issue gets its own copy of your project — originals are never touched |
| **📊 Token Tracking** | Per-session and aggregate metrics: prompt/completion tokens, runtime, costs |
| **🔥 Hot-Reload** | Edit `WORKFLOW.md` and config updates instantly — no restart needed |
| **📋 Result Reports** | Git diffs + agent summaries saved for every resolved issue |

---

## Quick Start

```bash
# 1. Install
uv sync

# 2. Set your API key
echo "DEEPSEEK_API_KEY=sk-your-key-here" > .env

# 3. Launch Symphony
uv run python -m symphony ./WORKFLOW.md
```

Then open **http://localhost:3000** to see the dashboard.

Symphony picks up the 2 demo issues from `issues.json`, copies `demo/project/` into isolated workspaces, and runs an AI agent on each. The demo project is a calculator with a bug (division by zero) and a missing feature (power function).

---

## Dashboard

The dashboard launches automatically at **http://localhost:3000** when Symphony starts. No build step needed — it works out of the box.

### What You See

- **Overview** — running / completed / failed / retrying counts, total tokens consumed, uptime
- **Running Sessions** — active agents with duration, turns taken, and stall detection
- **Retry Queue** — failed issues with attempt count, countdown timer, and last error
- **Recent Sessions** — completed sessions with status badge, duration, token usage, error details
- **Configuration** — current model, concurrency limits, poll interval, tracker type

### Customizing the Dashboard

```bash
# Default: port 3000
uv run python -m symphony ./WORKFLOW.md

# Custom port
uv run python -m symphony ./WORKFLOW.md --port 8080

# Run without dashboard (headless mode)
uv run python -m symphony ./WORKFLOW.md --no-dashboard
```

### Building the React SPA (optional)

The built-in dashboard works immediately. If you want the full React experience:

```bash
cd dashboard && npm install && npm run build
```

Symphony auto-detects `dashboard/dist/` and serves the React SPA instead.

### REST API

The dashboard is backed by a JSON API you can use for custom integrations:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/state` | GET | Full orchestrator state + metrics — the main endpoint |
| `/api/v1/sessions` | GET | Running + recently completed sessions |
| `/api/v1/sessions/{id}` | GET | Single session detail |
| `/api/v1/health` | GET | Health check: uptime, session count |
| `/api/v1/refresh` | POST | Force an immediate tracker re-poll |
| `/api/v1/watcher` | GET | Workflow file watcher status |

---

## Configuration

Symphony reads configuration from the YAML front matter of your `WORKFLOW.md` file:

```yaml
---
name: my-project
tracker:
  kind: file
  repo: ./issues.json
source_dir: /path/to/your/project
agent_model: deepseek/deepseek-chat
max_concurrent_agents: 5
poll_seconds: 30
---
You are an expert developer. Fix this issue:

**{{ issue.identifier }}: {{ issue.title }}**

{{ issue.description }}
```

### Config Reference

| Option | Default | Description |
|--------|---------|-------------|
| `tracker.kind` | `github` | `file` (local JSON) or `github` (GitHub Issues) |
| `tracker.repo` | — | Path to JSON file, or `owner/repo` for GitHub |
| `source_dir` | — | Your project directory to copy into each workspace |
| `agent_model` | `gpt-4o` | Any LiteLLM-supported model (e.g. `deepseek/deepseek-chat`) |
| `max_concurrent_agents` | 10 | Max parallel agent sessions |
| `max_turns` | 20 | Max agent iterations per issue |
| `poll_seconds` | 30 | How often to poll the tracker |
| `max_retries` | 5 | Max retry attempts per issue |

### Environment Variables (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPSEEK_API_KEY` | For DeepSeek models | API key via LiteLLM |
| `OPENAI_API_KEY` | For OpenAI models | API key via LiteLLM |
| `GITHUB_TOKEN` | For `tracker.kind: github` | GitHub personal access token |

### Tracker Modes

| Mode | Config | Best For |
|------|--------|----------|
| **File** | `kind: file`, `repo: ./issues.json` | Local dev, demos, testing — no API key needed |
| **GitHub** | `kind: github`, `repo: owner/repo` | Production use with GitHub Issues |

---

## Using Your Own Project

**1.** Create a `WORKFLOW.md`:

```yaml
---
name: my-project
tracker:
  kind: file
  repo: ./my-issues.json
source_dir: /path/to/your/project
agent_model: deepseek/deepseek-chat
---
You are an expert developer. Fix this issue:

**{{ issue.identifier }}: {{ issue.title }}**

{{ issue.description }}
```

**2.** Create `my-issues.json`:

```json
[
  {
    "id": "1",
    "identifier": "#1",
    "title": "Fix the login bug",
    "description": "Users get a 500 error when logging in with email containing a + character.",
    "state": "todo"
  }
]
```

**3.** Launch: `uv run python -m symphony ./WORKFLOW.md`

**4.** Open **http://localhost:3000** and watch the agent work.

---

## Hot-Reload

Symphony watches `WORKFLOW.md` for changes in real-time:

- **Save the file** → config and prompt update instantly, no restart
- **Invalid change?** → last-known-good config is kept, error logged
- **Rapid saves?** → debounced (1-second window), only one reload triggered

Disable with `--no-watch` if not needed.

---

## Agent Capabilities

The AI agent has real tools for reading and writing code:

| Tool | What it does |
|------|-------------|
| **FileReadTool** | Read any file in the workspace |
| **FileWriterTool** | Create or modify files |
| **DirectoryReadTool** | List directory contents to explore the project |

Agents run in isolated copies of your project. Your original source is never modified.

---

## Results

After each issue is processed:

1. **Dashboard** updates in real-time with session status, duration, and token usage
2. **Result files** saved to `.symphony-workspaces/_results/<issue>.md` — includes agent summary, git diff, and original issue
3. **Modified workspace** at `.symphony-workspaces/<issue>/` — the actual changed files

---

## CLI Reference

```bash
uv run python -m symphony ./WORKFLOW.md [OPTIONS]
```

| Flag | Default | Description |
|------|---------|-------------|
| `--port` | `3000` | Dashboard server port |
| `--no-dashboard` | — | Headless mode, no web server |
| `--no-watch` | — | Disable `WORKFLOW.md` hot-reload |
| `--log-level` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `--json-logs` | — | Structured JSON log output |

---

## Project Structure

```
symphony/
├── src/symphony/          # Core source code
│   ├── orchestrator.py    # Poll-dispatch-reconcile loop
│   ├── server.py          # FastAPI dashboard server + REST API
│   ├── metrics.py         # Token accounting + session metrics
│   ├── watcher.py         # Workflow hot-reload via watchdog
│   ├── agent_runner.py    # CrewAI agent with file tools
│   ├── workspace.py       # Workspace creation + source copying
│   ├── tracker/           # Issue tracker adapters (file, GitHub)
│   ├── config.py          # Typed configuration layer
│   ├── workflow.py        # WORKFLOW.md parser
│   ├── prompt.py          # Liquid template renderer
│   ├── log.py             # Structured logging with contextvars
│   └── cli.py             # CLI entry point
├── dashboard/             # React dashboard SPA (Vite + Tailwind)
│   ├── src/               # React components + hooks
│   └── dist/              # Built output (gitignored)
├── demo/                  # Demo project for testing
├── tests/                 # 95 tests
└── WORKFLOW.md            # Root workflow config
```
