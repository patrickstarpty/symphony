"""Agent runner — launches coding agents for issues.

Supports two modes:
1. **CrewAI** (default) — runs agent in-process using CrewAI framework
2. **Subprocess** (future) — launches external agent via JSON-RPC over stdio

The runner interface is designed so either mode can be used.

The CrewAI runner equips agents with real tools (file read/write, directory
listing, shell commands) so they can actually interact with the workspace
codebase, not just produce text.
"""

from __future__ import annotations

import asyncio
import subprocess
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from symphony.config import Config
from symphony.log import get_logger
from symphony.models import Issue

log = get_logger(__name__)


@dataclass
class AgentResult:
    """Result from an agent session."""

    success: bool
    session_id: str
    turns_used: int = 0
    error: str = ""
    output: str = ""
    diff: str = ""  # Git diff of changes made by the agent


class AgentRunner(ABC):
    """Abstract interface for running coding agents."""

    @abstractmethod
    async def run(
        self,
        issue: Issue,
        prompt: str,
        workspace: Path,
        session_id: str,
        on_turn: Any | None = None,
    ) -> AgentResult:
        """Run an agent session for an issue.

        Args:
            issue: The issue to work on.
            prompt: The rendered prompt for the agent.
            workspace: Path to the isolated workspace.
            session_id: Unique session ID for tracking.
            on_turn: Optional callback called after each agent turn.

        Returns:
            AgentResult with success/failure and metadata.
        """
        ...


def _capture_diff(workspace: Path) -> str:
    """Capture a git diff of changes in the workspace.

    If the workspace is a git repo, returns the diff of uncommitted changes.
    Falls back to listing modified files if git is not available.
    """
    try:
        # Check if workspace is a git repo
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return ""

        status = result.stdout.strip()
        if not status:
            return "(no changes detected)"

        # Stage all changes to include new files in diff
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(workspace),
            capture_output=True,
            timeout=30,
        )

        # Get the diff
        diff_result = subprocess.run(
            ["git", "diff", "--cached", "--stat"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Also get the full diff (truncated)
        full_diff = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Unstage (leave workspace in original state)
        subprocess.run(
            ["git", "reset", "HEAD"],
            cwd=str(workspace),
            capture_output=True,
            timeout=30,
        )

        summary = diff_result.stdout.strip()
        detail = full_diff.stdout.strip()
        # Truncate very large diffs
        if len(detail) > 10_000:
            detail = detail[:10_000] + "\n... (truncated)"

        return f"{summary}\n\n{detail}" if detail else summary

    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def _build_crewai_tools(workspace: Path) -> list[Any]:
    """Build CrewAI tools scoped to the workspace directory.

    Provides the agent with:
    - FileReadTool: read any file in the workspace
    - FileWriterTool: create/overwrite files in the workspace
    - DirectoryReadTool: list directory contents
    """
    try:
        from crewai_tools import DirectoryReadTool, FileReadTool, FileWriterTool
    except ImportError:
        log.warning("crewai_tools_not_installed", hint="uv add crewai-tools")
        return []

    ws = str(workspace)
    return [
        FileReadTool(directory=ws),
        FileWriterTool(directory=ws),
        DirectoryReadTool(directory=ws),
    ]


class CrewAIRunner(AgentRunner):
    """Run agents using CrewAI framework (in-process).

    This replaces the subprocess/JSON-RPC protocol with direct
    CrewAI API calls. The agent is equipped with file and directory
    tools scoped to the workspace, so it can actually read, write,
    and explore the codebase.
    """

    def __init__(self, config: Config) -> None:
        self._model = config.agent_model
        self._max_turns = config.max_turns

    async def run(
        self,
        issue: Issue,
        prompt: str,
        workspace: Path,
        session_id: str,
        on_turn: Any | None = None,
    ) -> AgentResult:
        """Run a CrewAI agent session."""
        log.info(
            "crewai_session_start",
            session_id=session_id,
            issue_id=issue.id,
            workspace=str(workspace),
        )

        try:
            # Import CrewAI here to avoid import errors when not installed
            from crewai import Agent, Crew, Task
        except ImportError:
            log.error("crewai_not_installed", hint="uv add crewai")
            return AgentResult(
                success=False,
                session_id=session_id,
                error="CrewAI is not installed. Run: uv add crewai",
            )

        try:
            # Build workspace-scoped tools
            tools = _build_crewai_tools(workspace)
            tool_names = [type(t).__name__ for t in tools]
            log.info("agent_tools_loaded", tools=tool_names, workspace=str(workspace))

            agent = Agent(
                role="Software Engineer",
                goal=f"Resolve issue {issue.identifier}: {issue.title}",
                backstory=(
                    "You are an expert software engineer. You have tools to "
                    "read files, write files, and list directories. Use them "
                    "to explore the codebase, understand the code, and make "
                    "the necessary changes to resolve the issue.\n\n"
                    f"Your workspace is at: {workspace}\n"
                    "Always start by listing the directory to understand the "
                    "project structure, then read relevant files before making "
                    "changes."
                ),
                tools=tools,
                verbose=True,
                llm=self._model,
                max_iter=self._max_turns,
            )

            task = Task(
                description=prompt,
                expected_output=(
                    "A summary of all changes made, including:\n"
                    "1. Which files were modified/created\n"
                    "2. What changes were made and why\n"
                    "3. How the changes resolve the issue"
                ),
                agent=agent,
            )

            crew = Crew(
                agents=[agent],
                tasks=[task],
                verbose=True,
            )

            # Run in a thread to avoid blocking the event loop
            result = await asyncio.to_thread(crew.kickoff)

            output = str(result) if result else ""

            # Capture diff of changes
            diff = _capture_diff(workspace)

            log.info(
                "crewai_session_complete",
                session_id=session_id,
                issue_id=issue.id,
                output_length=len(output),
                has_diff=bool(diff),
            )

            return AgentResult(
                success=True,
                session_id=session_id,
                turns_used=1,
                output=output,
                diff=diff,
            )

        except Exception as exc:
            error_msg = str(exc)
            # Detect missing API key errors
            if "API_KEY" in error_msg or "api_key" in error_msg or "AuthenticationError" in error_msg:
                log.error(
                    "agent_api_key_missing",
                    session_id=session_id,
                    issue_id=issue.id,
                    error=error_msg,
                    hint="Set OPENAI_API_KEY (or the appropriate key for your model) in your environment",
                )
            else:
                log.error(
                    "crewai_session_error",
                    session_id=session_id,
                    issue_id=issue.id,
                    error=error_msg,
                )
            return AgentResult(
                success=False,
                session_id=session_id,
                error=error_msg,
            )


class SubprocessRunner(AgentRunner):
    """Run agents as external subprocesses (future Codex support).

    Communicates via JSON-RPC over stdio. This is a placeholder
    implementation — the full JSON-RPC protocol will be added when
    Codex app-server support is needed.
    """

    def __init__(self, config: Config) -> None:
        self._config = config

    async def run(
        self,
        issue: Issue,
        prompt: str,
        workspace: Path,
        session_id: str,
        on_turn: Any | None = None,
    ) -> AgentResult:
        """Run an agent as a subprocess."""
        log.warning(
            "subprocess_runner_not_implemented",
            hint="Use agent_kind: crewai instead",
        )
        return AgentResult(
            success=False,
            session_id=session_id,
            error="Subprocess runner not yet implemented",
        )


def create_runner(config: Config) -> AgentRunner:
    """Factory function to create the appropriate agent runner."""
    if config.agent_kind == "subprocess":
        return SubprocessRunner(config)
    return CrewAIRunner(config)


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())[:8]
