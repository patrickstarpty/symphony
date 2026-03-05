# Demo: Calculator API

A minimal Python project for demonstrating Symphony's autonomous agent workflow.

Symphony will pick up issues from `issues.json`, create isolated workspaces with a copy of this project, and run an AI agent to resolve each issue.

## Structure

```
demo/
├── project/           # The target project (copied into each workspace)
│   ├── calculator.py  # Main module (intentionally has bugs/missing features)
│   └── test_calc.py   # Tests
├── issues.json        # Issues for the agent to work on
└── WORKFLOW.md        # Workflow definition
```

## Usage

```bash
cd demo
uv run python -m symphony ./WORKFLOW.md
```

After running, check `.symphony-workspaces/_results/` for agent output and diffs.
