---
name: fix-issue
tracker:
  kind: file
  repo: ./issues.json
source_dir: ./demo/project
poll_seconds: 30
max_concurrent_agents: 5
max_turns: 20
turn_timeout_seconds: 3600
stall_timeout_seconds: 300
max_retries: 3
agent_kind: crewai
agent_model: deepseek/deepseek-chat
---
You are an expert software engineer. You have been assigned to work on the following issue:

**{{ issue.identifier }}: {{ issue.title }}**

{{ issue.description }}

{% if attempt > 1 %}
NOTE: This is attempt {{ attempt }}. Previous attempts failed. Try a different approach.
{% endif %}

## Instructions

1. Read and understand the issue description carefully.
2. Explore the codebase in your workspace to understand the relevant code.
3. Implement the fix or feature described in the issue.
4. Write or update tests to cover your changes.
5. Ensure all existing tests still pass.

## Guidelines

- Make minimal, focused changes.
- Follow existing code style and conventions.
- Add comments where the intent isn't obvious.
- If you're unsure about something, make a reasonable choice and document it.
