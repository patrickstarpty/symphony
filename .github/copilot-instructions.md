# Symphony — Copilot Instructions

Symphony polls Linear for issues, creates isolated per-issue workspaces, launches GitHub Copilot CLI through a local bridge, and manages the full agent lifecycle. Reference implementation is in `elixir/`. All paths below are relative to `elixir/` unless noted.

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

`Orchestrator` (GenServer) polls Linear → dispatches `AgentRunner` per issue → `AgentRunner` launches the internal Copilot CLI app-server bridge (JSONL over stdio) → legacy dynamic-tool / bridge MCP wiring serves `linear_graphql` back to the agent.

| Component | Role |
|---|---|
| `Orchestrator` | Polling loop, dispatch, retry, reconciliation, cleanup |
| `AgentRunner` | One Copilot session per issue; turn lifecycle |
| `App-server bridge` | Internal JSONL bridge layer for GitHub Copilot CLI |
| `Dynamic tool adapter` | Legacy Linear tool compatibility surface |
| `Config` / `Workflow` / `WorkflowStore` | Runtime config from `WORKFLOW.md` front matter |
| `Linear.Client` / `Linear.Adapter` | Linear API |
| `Tracker` | Issue tracker abstraction (Linear or in-memory) |
| `Workspace` / `PathSafety` | Per-issue directories; workspace root confinement |
| `SSH` | Remote Copilot workers over SSH |
| `StatusDashboard` | Terminal UI |
| `HttpServer` + `SymphonyElixirWeb.*` | Optional Phoenix LiveView dashboard + JSON API |
| `LogFile` / `PromptBuilder` | Per-issue logs; Liquid prompt rendering |

Optional web layer (Phoenix + Bandit + LiveView) is enabled only when `--port` is passed or `server.port` is configured.

## Conventions

**`@spec` required on all `def` in `lib/`.** `defp` and `@impl` are exempt. Enforced by `mix specs.check`.

**Config via `SymphonyElixir.Config` only.** Never read env vars ad-hoc; all config flows from `WORKFLOW.md` front matter through `Config`.

**Workspace safety.** Never set GitHub Copilot CLI `cwd` inside the source repo. All paths validated through `PathSafety` to stay under workspace root.

**Orchestrator semantics.** State is concurrency-sensitive. Preserve backoff, retry, reconciliation, and cleanup logic — do not simplify away state transitions.

**Logging** (`docs/logging.md`). Issue-related logs require `issue_id` + `issue_identifier`. Copilot session logs require `session_id`. Use `key=value` inline pairs; use deterministic wording for lifecycle events.

**Issue execution flow.** Use one persistent `## Copilot Workpad` comment per issue as the source of truth, while reusing legacy `## Codex Workpad` comments when continuing older work. Do not track progress in the issue body or post separate completion comments. For `Todo`, move the issue to `In Progress` before active work, then create/update the workpad. Reproduce the problem before coding, and mirror any issue-authored `Validation`, `Test Plan`, or `Testing` sections into the workpad as mandatory checks.

**Linear operations.** For issue state, comments, and attachments during orchestrated runs, use Linear MCP or Symphony’s injected `linear_graphql` tool. Prefer exact `stateId` lookups over hardcoded state names, and prefer the GitHub PR attachment flow over generic URL links when attaching a PR to a Linear issue.

**Review gate.** Before moving to `Human Review`, sweep top-level PR comments, inline review comments, and review summaries. Every actionable comment must be addressed or explicitly pushed back, and the PR must carry the `symphony` label.

**Coverage.** Threshold is 100%. Hard-to-test modules (runtime I/O, HTTP, Phoenix) are allowlisted in `mix.exs`. Do not add to the ignore list without justification.

**Spec alignment.** Implementation must not conflict with `../SPEC.md`. Update `SPEC.md` in the same PR when behavior changes meaningfully.

**PR body** must follow `../.github/pull_request_template.md` exactly. Validate: `mix pr_body.check --file <path>`.

**Docs updates.** Config/behavior changes require same-PR updates to `../README.md`, `README.md`, and `WORKFLOW.md` as appropriate.

## Issue State → Agent Action

| Linear state | Action |
|---|---|
| `Backlog` | Do not modify. Wait for human to move to `Todo`. |
| `Todo` | Move to `In Progress` → create/find `## Copilot Workpad` comment (or reuse legacy `## Codex Workpad`) → execute. |
| `In Progress` | Continue from existing workpad comment. |
| `Human Review` | Do not code. Poll for review updates. |
| `Rework` | Full reset: close PR, delete workpad, fresh branch from `origin/main`, restart. |
| `Merging` | Open and follow `.github/skills/finishing-a-development-branch/SKILL.md` until PR is merged, then move to `Done`. |
| `Done` / `Closed` / `Cancelled` / `Duplicate` | Terminal — stop and clean up workspace. |

Before moving to `Human Review`, all of the following must be true: workpad checklist complete, acceptance criteria met, tests green, PR feedback sweep done, PR checks passing, `symphony` label on PR.
