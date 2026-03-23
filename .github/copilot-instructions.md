# Symphony — Copilot Instructions

Symphony polls Linear for issues, creates isolated per-issue workspaces, launches Codex in app-server mode, and manages the full agent lifecycle. Reference implementation is in `elixir/`. All paths below are relative to `elixir/` unless noted.

## Commands

```bash
mise install                  # install Elixir 1.19.x / OTP 28
mise exec -- mix setup        # install deps
mise exec -- mix build        # compile escript → bin/symphony
make all                      # full gate: fmt-check + lint + coverage + dialyzer
mix test                      # full test suite
mix test path/to/test.exs     # single file
mix test path/to/test.exs:42  # single test
mix specs.check               # verify @spec on all public defs
mix dialyzer --format short
make e2e                      # live end-to-end (requires LINEAR_API_KEY)
```

`mix lint` = `mix specs.check` + `mix credo --strict`. Run `make all` before handing off.

## Architecture

`Orchestrator` (GenServer) polls Linear → dispatches `AgentRunner` per issue → `AgentRunner` launches `Codex.AppServer` (JSONL over stdio) → `Codex.DynamicTool` serves a `linear_graphql` HTTP tool back to the agent.

| Module | Role |
|---|---|
| `Orchestrator` | Polling loop, dispatch, retry, reconciliation, cleanup |
| `AgentRunner` | One Codex session per issue; turn lifecycle |
| `Codex.AppServer` | Codex app-server protocol |
| `Codex.DynamicTool` | Serves `linear_graphql` tool to agents |
| `Config` / `Workflow` / `WorkflowStore` | Runtime config from `WORKFLOW.md` front matter |
| `Linear.Client` / `Linear.Adapter` | Linear API |
| `Tracker` | Issue tracker abstraction (Linear or in-memory) |
| `Workspace` / `PathSafety` | Per-issue directories; workspace root confinement |
| `SSH` | Remote Codex workers over SSH |
| `StatusDashboard` | Terminal UI |
| `HttpServer` + `SymphonyElixirWeb.*` | Optional Phoenix LiveView dashboard + JSON API |
| `LogFile` / `PromptBuilder` | Per-issue logs; Liquid prompt rendering |

Optional web layer (Phoenix + Bandit + LiveView) is enabled only when `--port` is passed or `server.port` is configured.

## Conventions

**`@spec` required on all `def` in `lib/`.** `defp` and `@impl` are exempt. Enforced by `mix specs.check`.

**Config via `SymphonyElixir.Config` only.** Never read env vars ad-hoc; all config flows from `WORKFLOW.md` front matter through `Config`.

**Workspace safety.** Never set Codex `cwd` inside the source repo. All paths validated through `PathSafety` to stay under workspace root.

**Orchestrator semantics.** State is concurrency-sensitive. Preserve backoff, retry, reconciliation, and cleanup logic — do not simplify away state transitions.

**Logging** (`docs/logging.md`). Issue-related logs require `issue_id` + `issue_identifier`. Codex session logs require `session_id`. Use `key=value` inline pairs; use deterministic wording for lifecycle events.

**Coverage.** Threshold is 100%. Hard-to-test modules (runtime I/O, HTTP, Phoenix) are allowlisted in `mix.exs`. Do not add to the ignore list without justification.

**Spec alignment.** Implementation must not conflict with `../SPEC.md`. Update `SPEC.md` in the same PR when behavior changes meaningfully.

**PR body** must follow `../.github/pull_request_template.md` exactly. Validate: `mix pr_body.check --file <path>`.

**Docs updates.** Config/behavior changes require same-PR updates to `../README.md`, `README.md`, and `WORKFLOW.md` as appropriate.

## Skill & Agent Routing

Skills live in `.github/skills/<name>/SKILL.md`. Agents live in `.github/agents/<name>.md`. Route to them based on the current task:

| When | Use |
|---|---|
| Starting any session | `.github/skills/using-superpowers/SKILL.md` |
| Multi-step task, before touching code | `.github/skills/writing-plans/SKILL.md` |
| Executing a written plan | `.github/skills/executing-plans/SKILL.md` |
| Implementing any feature or bugfix | `.github/skills/test-driven-development/SKILL.md` |
| 2+ independent tasks with no shared state | `.github/skills/dispatching-parallel-agents/SKILL.md` |
| Independent tasks within the current session | `.github/skills/subagent-driven-development/SKILL.md` |
| Bug, test failure, or unexpected behavior | `.github/skills/systematic-debugging/SKILL.md` |
| About to claim work is complete | `.github/skills/verification-before-completion/SKILL.md` |
| Implementation done, ready to integrate | `.github/skills/finishing-a-development-branch/SKILL.md` |
| Requesting a code review | `.github/skills/requesting-code-review/SKILL.md` |
| Receiving code review feedback | `.github/skills/receiving-code-review/SKILL.md` |
| A major step is complete and needs validation | `code-reviewer` agent (`.github/agents/code-reviewer.md`) |
| Starting feature work needing workspace isolation | `.github/skills/using-git-worktrees/SKILL.md` |

## Issue State → Agent Action

| Linear state | Action |
|---|---|
| `Backlog` | Do not modify. Wait for human to move to `Todo`. |
| `Todo` | Move to `In Progress` → create/find `## Codex Workpad` comment → execute. |
| `In Progress` | Continue from existing workpad comment. |
| `Human Review` | Do not code. Poll for review updates. |
| `Rework` | Full reset: close PR, delete workpad, fresh branch from `origin/main`, restart. |
| `Merging` | Open and follow `.github/skills/finishing-a-development-branch/SKILL.md` until PR is merged, then move to `Done`. |
| `Done` / `Closed` / `Cancelled` / `Duplicate` | Terminal — stop and clean up workspace. |

Before moving to `Human Review`, all of the following must be true: workpad checklist complete, acceptance criteria met, tests green, PR feedback sweep done, PR checks passing, `symphony` label on PR.
