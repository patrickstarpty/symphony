"""Typed configuration layer with environment variable resolution.

Handles:
- Default values for all config keys
- ``$VAR`` / ``${VAR}`` resolution in string values
- ``~`` expansion in paths
- Validation of required fields
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from symphony.log import get_logger

log = get_logger(__name__)

# Match $VAR or ${VAR}
_ENV_VAR_RE = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


class ConfigError(Exception):
    """Raised on configuration validation failure."""


def _resolve_env_vars(value: str) -> str:
    """Replace ``$VAR`` and ``${VAR}`` references with environment values."""

    def _replace(m: re.Match) -> str:
        var_name = m.group(1) or m.group(2)
        env_val = os.environ.get(var_name)
        if env_val is None:
            raise ConfigError(f"Environment variable not set: ${var_name}")
        return env_val

    return _ENV_VAR_RE.sub(_replace, value)


def _resolve_value(value: Any) -> Any:
    """Recursively resolve env vars and paths in config values."""
    if isinstance(value, str):
        resolved = _resolve_env_vars(value)
        # Expand ~ in path-like strings
        if resolved.startswith("~"):
            resolved = str(Path(resolved).expanduser())
        return resolved
    if isinstance(value, dict):
        return {k: _resolve_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_value(item) for item in value]
    return value


@dataclass(frozen=True)
class TrackerConfig:
    """Tracker-specific configuration."""

    kind: str  # "github", "file", "linear", etc.
    repo: str = ""  # For GitHub: "owner/repo"
    query: str = ""  # Filter query (e.g. label filter)
    token_env: str = "GITHUB_TOKEN"  # Env var name holding the API token
    api_url: str = ""  # Base API URL (for GitHub Enterprise, etc.)
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def token(self) -> str:
        val = os.environ.get(self.token_env, "")
        if not val:
            raise ConfigError(
                f"Tracker token environment variable not set: ${self.token_env}"
            )
        return val


@dataclass(frozen=True)
class Config:
    """Fully resolved Symphony configuration."""

    # Workflow
    name: str
    workflow_path: Path

    # Tracker
    tracker: TrackerConfig

    # Orchestrator
    poll_seconds: int = 30
    max_concurrent_agents: int = 10
    max_concurrent_agents_by_state: dict[str, int] = field(default_factory=dict)
    max_turns: int = 20
    turn_timeout_seconds: int = 3600
    stall_timeout_seconds: int = 300
    max_retries: int = 5

    # Workspace
    workspace_base: Path = field(default_factory=lambda: Path.cwd() / ".symphony-workspaces")
    repo_url: str = ""  # Git repo to clone for each workspace
    source_dir: str = ""  # Local directory to copy into each workspace

    # Agent
    agent_kind: str = "crewai"  # "crewai" or "subprocess"
    agent_model: str = "gpt-4o"  # LLM model for the agent

    # Server (Phase 2)
    port: int | None = None


def build_config(raw: dict[str, Any], workflow_path: Path) -> Config:
    """Build a validated Config from raw YAML config dict.

    Args:
        raw: The config dict (workflow front matter).
        workflow_path: Resolved path to the workflow file.

    Returns:
        Validated ``Config`` object.

    Raises:
        ConfigError: On validation failure.
    """
    # Resolve env vars in all values
    resolved = _resolve_value(raw)

    # Build tracker config
    tracker_raw = resolved.get("tracker", {})
    if not isinstance(tracker_raw, dict):
        raise ConfigError("'tracker' must be a mapping")

    kind = tracker_raw.get("kind", "github")
    known_tracker_keys = {"kind", "repo", "query", "token_env", "api_url"}
    extra = {k: v for k, v in tracker_raw.items() if k not in known_tracker_keys}

    tracker = TrackerConfig(
        kind=kind,
        repo=tracker_raw.get("repo", ""),
        query=tracker_raw.get("query", ""),
        token_env=tracker_raw.get("token_env", "GITHUB_TOKEN"),
        api_url=tracker_raw.get("api_url", ""),
        extra=extra,
    )

    # Validate tracker
    if tracker.kind == "github" and not tracker.repo:
        raise ConfigError("GitHub tracker requires 'tracker.repo' (e.g. 'owner/repo')")

    # Build workspace base path
    ws_base_str = resolved.get("workspace_base", "")
    if ws_base_str:
        workspace_base = Path(ws_base_str)
    else:
        workspace_base = Path.cwd() / ".symphony-workspaces"

    # Resolve source_dir relative to the workflow file
    source_dir_str = resolved.get("source_dir", "")
    if source_dir_str:
        source_path = Path(source_dir_str)
        if not source_path.is_absolute():
            source_path = (workflow_path.parent / source_path).resolve()
        source_dir_str = str(source_path)

    # Resolve tracker.repo relative to workflow for file-based tracker
    tracker_repo = tracker.repo
    if tracker.kind == "file" and tracker_repo:
        repo_path = Path(tracker_repo)
        if not repo_path.is_absolute():
            repo_path = (workflow_path.parent / repo_path).resolve()
            tracker = TrackerConfig(
                kind=tracker.kind,
                repo=str(repo_path),
                query=tracker.query,
                token_env=tracker.token_env,
                api_url=tracker.api_url,
                extra=tracker.extra,
            )

    config = Config(
        name=resolved.get("name", "symphony"),
        workflow_path=workflow_path,
        tracker=tracker,
        poll_seconds=int(resolved.get("poll_seconds", 30)),
        max_concurrent_agents=int(resolved.get("max_concurrent_agents", 10)),
        max_concurrent_agents_by_state=dict(
            resolved.get("max_concurrent_agents_by_state", {})
        ),
        max_turns=int(resolved.get("max_turns", 20)),
        turn_timeout_seconds=int(resolved.get("turn_timeout_seconds", 3600)),
        stall_timeout_seconds=int(resolved.get("stall_timeout_seconds", 300)),
        max_retries=int(resolved.get("max_retries", 5)),
        workspace_base=workspace_base,
        repo_url=resolved.get("repo_url", ""),
        source_dir=source_dir_str,
        agent_kind=resolved.get("agent_kind", "crewai"),
        agent_model=resolved.get("agent_model", "gpt-4o"),
        port=resolved.get("port"),
    )

    log.info(
        "config_built",
        name=config.name,
        tracker_kind=config.tracker.kind,
        max_concurrent=config.max_concurrent_agents,
    )

    return config
