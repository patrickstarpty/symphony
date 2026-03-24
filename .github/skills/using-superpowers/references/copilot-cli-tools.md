# GitHub Copilot CLI Tool Mapping

Skills use Claude Code tool names. When you encounter these in a skill, use the closest GitHub Copilot CLI equivalent:

| Skill references | GitHub Copilot CLI equivalent |
|-----------------|-------------------------------|
| `Task` tool (dispatch subagent) | `task` agent |
| Multiple `Task` calls (parallel) | Parallel `task` calls or `multi_tool_use.parallel` when safe |
| Task returns result | `read_agent` |
| Task completes automatically | Background agents complete on their own; read them only when needed |
| `TodoWrite` (task tracking) | Session SQL `todos` tracking or the current execution plan |
| `Skill` tool (invoke a skill) | Repo-local `.github/skills/` and Copilot skill invocation by name |
| `Read`, `Write`, `Edit` (files) | `view` + `apply_patch` |
| `Bash` (run commands) | `bash` |

## Notes

- Prefer repo-local skills checked into `.github/skills/`.
- Prefer Copilot's native sub-agents over ad-hoc shell orchestration when a skill calls for delegation.
- Use `report_intent` and parallel tool calls to preserve the same high-signal workflow the original skills expect.
