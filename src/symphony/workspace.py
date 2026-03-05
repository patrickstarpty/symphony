"""Workspace manager — create and manage isolated workspaces for agents.

Each issue gets its own workspace directory. The manager handles:
- Creating workspace directories with sanitised names
- Copying a source project or cloning a git repo into the workspace
- Initialising git in each workspace (for diff tracking)
- Running lifecycle hooks (setup, pre-run, post-run, teardown)
- Path containment checks (no symlink escapes)

Spec Sections 9.1-9.5.
"""

from __future__ import annotations

import asyncio
import re
import shutil
from pathlib import Path
from typing import Any

from symphony.config import Config
from symphony.log import get_logger
from symphony.models import Issue

log = get_logger(__name__)

# Allowed chars for workspace directory names
_SANITIZE_RE = re.compile(r"[^a-zA-Z0-9_\-.]")
_MULTI_DASH_RE = re.compile(r"-{2,}")

# Hook timeout (seconds)
DEFAULT_HOOK_TIMEOUT = 120

# Directories/files to skip when copying source
_COPY_IGNORE = shutil.ignore_patterns(
    ".git", ".venv", "venv", "__pycache__", "*.pyc",
    "node_modules", ".symphony-workspaces", ".env",
)


class WorkspaceError(Exception):
    """Raised on workspace operation failure."""


def sanitize_key(issue: Issue) -> str:
    """Create a filesystem-safe workspace key from an issue.

    Combines the identifier (with special chars removed) and a slug of the title.
    Example: ``42-fix-login-bug``
    """
    # Start with issue number/identifier, stripped of non-alnum
    ident = _SANITIZE_RE.sub("-", issue.identifier.lstrip("#"))

    # Add a title slug (first ~40 chars)
    title_slug = _SANITIZE_RE.sub("-", issue.title.lower()[:40]).strip("-")
    title_slug = _MULTI_DASH_RE.sub("-", title_slug)

    key = f"{ident}-{title_slug}" if title_slug else ident
    return key.strip("-")[:80]  # Cap total length


def _check_path_containment(workspace: Path, base: Path) -> None:
    """Verify the workspace path doesn't escape the base directory.

    Resolves symlinks and checks containment.

    Raises:
        WorkspaceError: If the resolved path escapes the base.
    """
    resolved = workspace.resolve()
    resolved_base = base.resolve()
    if not str(resolved).startswith(str(resolved_base)):
        raise WorkspaceError(
            f"Workspace path escapes base directory: {resolved} not under {resolved_base}"
        )


class WorkspaceManager:
    """Manages isolated workspaces for agent sessions."""

    def __init__(self, config: Config) -> None:
        self._base = config.workspace_base
        self._repo_url = config.repo_url
        self._source_dir = config.source_dir
        self._hook_timeout = DEFAULT_HOOK_TIMEOUT

    async def create_or_reuse(self, issue: Issue) -> Path:
        """Create a workspace directory for an issue, or reuse an existing one.

        Args:
            issue: The issue to create a workspace for.

        Returns:
            Path to the workspace directory.
        """
        key = sanitize_key(issue)
        workspace = self._base / key

        _check_path_containment(workspace, self._base)

        if workspace.exists():
            log.info("workspace_reused", path=str(workspace), issue_id=issue.id)
            return workspace

        workspace.mkdir(parents=True, exist_ok=True)

        # Copy source project if configured (highest priority)
        if self._source_dir:
            await self._copy_source(workspace)
        # Otherwise clone repo if configured
        elif self._repo_url:
            await self._clone_repo(workspace)

        # Initialise git so we can track changes via diff
        await self._init_git(workspace)

        log.info("workspace_created", path=str(workspace), issue_id=issue.id)
        return workspace

    async def _copy_source(self, workspace: Path) -> None:
        """Copy the source project directory into the workspace."""
        source = Path(self._source_dir).resolve()
        if not source.is_dir():
            log.error("source_dir_not_found", source_dir=str(source))
            return

        log.info("copying_source_project", source=str(source), dest=str(workspace))

        # Copy contents of source into workspace (not as a subdirectory)
        def _do_copy() -> None:
            for item in source.iterdir():
                dest = workspace / item.name
                if dest.exists():
                    continue
                if item.is_dir():
                    # Skip ignored directories
                    if item.name in {".git", ".venv", "venv", "__pycache__",
                                     "node_modules", ".symphony-workspaces"}:
                        continue
                    shutil.copytree(item, dest, ignore=_COPY_IGNORE)
                else:
                    if item.name == ".env":
                        continue
                    shutil.copy2(item, dest)

        await asyncio.to_thread(_do_copy)

        log.info("source_copied", file_count=len(list(workspace.iterdir())))

    async def _init_git(self, workspace: Path) -> None:
        """Initialise a git repo in the workspace and commit the initial state.

        This allows us to generate a diff of agent changes afterwards.
        """
        git_dir = workspace / ".git"
        if git_dir.exists():
            return  # Already a git repo

        try:
            # git init
            process = await asyncio.create_subprocess_exec(
                "git", "init",
                cwd=str(workspace),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(process.communicate(), timeout=30)

            # git add -A
            process = await asyncio.create_subprocess_exec(
                "git", "add", "-A",
                cwd=str(workspace),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(process.communicate(), timeout=30)

            # git commit (initial snapshot)
            process = await asyncio.create_subprocess_exec(
                "git", "commit", "-m", "Initial workspace snapshot",
                "--allow-empty",
                cwd=str(workspace),
                env={
                    **dict(__import__("os").environ),
                    "GIT_AUTHOR_NAME": "Symphony",
                    "GIT_AUTHOR_EMAIL": "symphony@local",
                    "GIT_COMMITTER_NAME": "Symphony",
                    "GIT_COMMITTER_EMAIL": "symphony@local",
                },
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(process.communicate(), timeout=30)

            log.debug("workspace_git_init", path=str(workspace))

        except (FileNotFoundError, asyncio.TimeoutError) as exc:
            log.warning("git_init_failed", error=str(exc), hint="git not available")

    async def _clone_repo(self, workspace: Path) -> None:
        """Clone the configured git repo into the workspace."""
        try:
            process = await asyncio.create_subprocess_exec(
                "git", "clone", "--depth", "1", self._repo_url, str(workspace / "repo"),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=300
            )
            if process.returncode != 0:
                log.error(
                    "git_clone_failed",
                    returncode=process.returncode,
                    stderr=stderr.decode(),
                )
        except asyncio.TimeoutError:
            log.error("git_clone_timeout", repo=self._repo_url)
        except FileNotFoundError:
            log.warning("git_not_found", hint="git is not installed")

    async def run_hook(
        self,
        hook_name: str,
        workspace: Path,
        env: dict[str, str] | None = None,
        fatal: bool = False,
    ) -> bool:
        """Run a lifecycle hook script if it exists.

        Hooks are shell scripts at ``<workspace>/.symphony/hooks/<hook_name>``.

        Args:
            hook_name: Name of the hook (setup, pre-run, post-run, teardown).
            workspace: The workspace directory.
            env: Extra environment variables for the hook.
            fatal: If True, raise on hook failure; otherwise log and continue.

        Returns:
            True if hook succeeded or didn't exist; False on failure (non-fatal).
        """
        hook_path = workspace / ".symphony" / "hooks" / hook_name
        if not hook_path.is_file():
            return True

        _check_path_containment(hook_path, workspace)

        hook_env = dict(env or {})
        hook_env["SYMPHONY_WORKSPACE"] = str(workspace)
        hook_env["SYMPHONY_HOOK"] = hook_name

        log.info("hook_start", hook=hook_name, workspace=str(workspace))

        try:
            process = await asyncio.create_subprocess_exec(
                str(hook_path),
                cwd=str(workspace),
                env={**dict(__import__("os").environ), **hook_env},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self._hook_timeout
            )

            # Truncate hook output for safety (spec Section 15)
            stdout_str = stdout.decode(errors="replace")[:10_000]
            stderr_str = stderr.decode(errors="replace")[:10_000]

            if process.returncode != 0:
                msg = f"Hook '{hook_name}' failed with code {process.returncode}"
                log.error(
                    "hook_failed",
                    hook=hook_name,
                    returncode=process.returncode,
                    stderr=stderr_str,
                )
                if fatal:
                    raise WorkspaceError(msg)
                return False

            log.info("hook_completed", hook=hook_name, stdout_len=len(stdout_str))
            return True

        except asyncio.TimeoutError:
            msg = f"Hook '{hook_name}' timed out after {self._hook_timeout}s"
            log.error("hook_timeout", hook=hook_name, timeout=self._hook_timeout)
            if fatal:
                raise WorkspaceError(msg)
            return False
        except FileNotFoundError:
            log.warning("hook_not_executable", hook=hook_name, path=str(hook_path))
            return True

    async def cleanup(self, workspace: Path) -> None:
        """Remove a workspace directory and all its contents."""
        if workspace.exists():
            _check_path_containment(workspace, self._base)
            shutil.rmtree(workspace, ignore_errors=True)
            log.info("workspace_cleaned", path=str(workspace))

    def list_workspaces(self) -> list[Path]:
        """List all existing workspace directories."""
        if not self._base.exists():
            return []
        return sorted(p for p in self._base.iterdir() if p.is_dir())
