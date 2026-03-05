"""WORKFLOW.md loader and parser.

A workflow file has two parts:
1. YAML front matter between ``---`` fences (configuration)
2. The rest is a Liquid-template prompt body

Example::

    ---
    name: fix-issue
    tracker:
      kind: github
      repo: owner/repo
    ---
    You are a coding agent. Fix issue {{ issue.identifier }}: {{ issue.title }}
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from symphony.log import get_logger

log = get_logger(__name__)

# Regex to split front matter from body.
# Matches: optional leading whitespace, ``---\n``, content, ``---\n``, rest
_FRONT_MATTER_RE = re.compile(
    r"\A\s*---[ \t]*\r?\n(.*?)^---[ \t]*\r?\n(.*)\Z",
    re.MULTILINE | re.DOTALL,
)


class WorkflowError(Exception):
    """Raised when a workflow file cannot be loaded or parsed."""


@dataclass(frozen=True)
class Workflow:
    """Parsed workflow definition."""

    path: Path
    name: str
    config: dict[str, Any]  # raw YAML front matter
    prompt_template: str  # Liquid template body
    # Convenience access to common config keys with defaults
    tracker: dict[str, Any] = field(default_factory=dict)

    @property
    def poll_seconds(self) -> int:
        return int(self.config.get("poll_seconds", 30))

    @property
    def max_concurrent_agents(self) -> int:
        return int(self.config.get("max_concurrent_agents", 10))

    @property
    def max_concurrent_agents_by_state(self) -> dict[str, int]:
        return dict(self.config.get("max_concurrent_agents_by_state", {}))

    @property
    def max_turns(self) -> int:
        return int(self.config.get("max_turns", 20))

    @property
    def turn_timeout_seconds(self) -> int:
        return int(self.config.get("turn_timeout_seconds", 3600))

    @property
    def stall_timeout_seconds(self) -> int:
        return int(self.config.get("stall_timeout_seconds", 300))

    @property
    def max_retries(self) -> int:
        return int(self.config.get("max_retries", 5))


def load_workflow(path: str | Path) -> Workflow:
    """Load and parse a workflow file.

    Args:
        path: Path to the WORKFLOW.md file.

    Returns:
        Parsed ``Workflow`` object.

    Raises:
        WorkflowError: If the file doesn't exist, has invalid YAML, or
            is missing required fields.
    """
    path = Path(path).resolve()

    if not path.is_file():
        raise WorkflowError(f"Workflow file not found: {path}")

    text = path.read_text(encoding="utf-8")

    match = _FRONT_MATTER_RE.match(text)
    if not match:
        raise WorkflowError(
            f"Workflow file must start with YAML front matter between --- fences: {path}"
        )

    front_matter_str = match.group(1)
    prompt_template = match.group(2).strip()

    # Parse YAML
    try:
        config = yaml.safe_load(front_matter_str)
    except yaml.YAMLError as exc:
        raise WorkflowError(f"Invalid YAML in front matter: {exc}") from exc

    if not isinstance(config, dict):
        raise WorkflowError(
            f"Front matter must be a YAML mapping, got {type(config).__name__}: {path}"
        )

    # Extract required fields
    name = config.get("name")
    if not name:
        raise WorkflowError(f"Workflow must have a 'name' field in front matter: {path}")

    # Extract tracker config
    tracker = config.get("tracker", {})
    if not isinstance(tracker, dict):
        raise WorkflowError(
            f"'tracker' must be a mapping, got {type(tracker).__name__}: {path}"
        )

    log.info("workflow_loaded", path=str(path), name=name)

    return Workflow(
        path=path,
        name=str(name),
        config=config,
        prompt_template=prompt_template,
        tracker=tracker,
    )
