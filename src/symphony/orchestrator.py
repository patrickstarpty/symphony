"""Orchestrator — the core poll-dispatch-reconcile loop.

This is the heart of Symphony. It:
1. Polls the tracker for eligible issues on a timer
2. Dispatches agent sessions for new issues (respecting concurrency limits)
3. Reconciles running sessions against tracker state
4. Manages retry queue with exponential backoff
5. Handles stall detection and turn timeouts

Spec Sections 7.1-7.4, 8.1-8.6.

The orchestrator is the single authority for state mutation.
All state changes happen in the main asyncio event loop (single-threaded),
so no locks are needed.
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import Any

from symphony.agent_runner import AgentResult, AgentRunner, create_runner, generate_session_id
from symphony.config import Config
from symphony.log import bind_context, clear_context, get_logger
from symphony.metrics import MetricsCollector
from symphony.models import (
    Issue,
    IssueState,
    OrchestratorState,
    RetryEntry,
    RunningEntry,
)
from symphony.prompt import render_prompt
from symphony.tracker.base import TrackerClient
from symphony.workspace import WorkspaceManager

log = get_logger(__name__)


class Orchestrator:
    """The main orchestration loop.

    Lifecycle::

        orchestrator = Orchestrator(config, tracker, workflow_template)
        await orchestrator.start()
        # ... runs until shutdown is requested ...
        await orchestrator.shutdown()
    """

    def __init__(
        self,
        config: Config,
        tracker: TrackerClient,
        prompt_template: str,
        metrics: MetricsCollector | None = None,
    ) -> None:
        self._config = config
        self._tracker = tracker
        self._prompt_template = prompt_template
        self._state = OrchestratorState()
        self._workspace_mgr = WorkspaceManager(config)
        self._runner: AgentRunner = create_runner(config)
        self._running = False
        self._tasks: dict[str, asyncio.Task] = {}  # issue_id -> agent task
        self._shutdown_event = asyncio.Event()
        self._metrics = metrics or MetricsCollector()

    @property
    def state(self) -> OrchestratorState:
        """Read-only access to orchestrator state (for dashboard API)."""
        return self._state

    @property
    def metrics(self) -> MetricsCollector:
        """Read-only access to metrics collector (for dashboard API)."""
        return self._metrics

    def update_prompt_template(self, template: str) -> None:
        """Update the prompt template (used by watcher on hot-reload)."""
        self._prompt_template = template
        log.info("prompt_template_updated")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the poll-dispatch-reconcile loop."""
        self._running = True
        log.info(
            "orchestrator_started",
            poll_seconds=self._config.poll_seconds,
            max_concurrent=self._config.max_concurrent_agents,
        )

        try:
            while self._running:
                await self._tick()
                # Wait for poll interval or shutdown signal
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=self._config.poll_seconds,
                    )
                    # If we get here, shutdown was requested
                    break
                except asyncio.TimeoutError:
                    # Normal: poll interval elapsed
                    pass
        except asyncio.CancelledError:
            log.info("orchestrator_cancelled")
        finally:
            await self._drain()

    async def shutdown(self) -> None:
        """Signal the orchestrator to shut down gracefully."""
        log.info("orchestrator_shutdown_requested")
        self._running = False
        self._shutdown_event.set()

    # ------------------------------------------------------------------
    # Poll tick
    # ------------------------------------------------------------------

    async def _tick(self) -> None:
        """Execute one poll-dispatch-reconcile cycle."""
        log.debug(
            "tick_start",
            running=self._state.running_count,
            retry_queue=len(self._state.retry_queue),
        )

        # 1. Reconcile — check running sessions against tracker state
        await self._reconcile()

        # 2. Process retry queue — re-dispatch eligible retries
        await self._process_retries()

        # 3. Fetch issues from tracker
        try:
            issues = await self._tracker.fetch_issues()
        except Exception as exc:
            log.error("tracker_fetch_error", error=str(exc))
            return

        # 4. Dispatch eligible issues
        for issue in issues:
            if not self._running:
                break
            await self._maybe_dispatch(issue)

        log.debug(
            "tick_complete",
            running=self._state.running_count,
            retry_queue=len(self._state.retry_queue),
        )

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    async def _maybe_dispatch(self, issue: Issue, attempt: int = 1) -> bool:
        """Decide whether to dispatch an agent for this issue.

        Checks:
        - Is the issue already being handled?
        - Is the issue in an active state?
        - Are we at global concurrency limit?
        - Are we at per-state concurrency limit?
        - Are there blocking issues?

        Returns True if dispatched, False if skipped.
        """
        if self._state.is_known(issue.id):
            return False

        if not issue.state.is_active:
            return False

        # Global concurrency check
        if self._state.running_count >= self._config.max_concurrent_agents:
            log.debug("dispatch_skipped_global_limit", issue_id=issue.id)
            return False

        # Per-state concurrency check
        state_limits = self._config.max_concurrent_agents_by_state
        state_key = issue.state.value
        if state_key in state_limits:
            current = self._state.running_count_by_state(issue.state)
            if current >= state_limits[state_key]:
                log.debug(
                    "dispatch_skipped_state_limit",
                    issue_id=issue.id,
                    state=state_key,
                    current=current,
                    limit=state_limits[state_key],
                )
                return False

        # Blocker check
        if issue.blocked_by:
            for blocker_id in issue.blocked_by:
                if blocker_id not in self._state.completed:
                    log.debug(
                        "dispatch_skipped_blocked",
                        issue_id=issue.id,
                        blocked_by=blocker_id,
                    )
                    return False

        # Dispatch!
        await self._dispatch(issue, attempt)
        return True

    async def _dispatch(self, issue: Issue, attempt: int = 1) -> None:
        """Create a workspace and launch an agent session."""
        session_id = generate_session_id()

        log.info(
            "dispatching_agent",
            issue_id=issue.id,
            identifier=issue.identifier,
            title=issue.title,
            attempt=attempt,
            session_id=session_id,
        )

        try:
            # Create workspace
            workspace = await self._workspace_mgr.create_or_reuse(issue)

            # Run setup hook
            await self._workspace_mgr.run_hook("setup", workspace, fatal=False)

            # Render prompt
            prompt = render_prompt(
                self._prompt_template,
                issue=issue,
                attempt=attempt,
            )

            # Record running entry
            entry = RunningEntry(
                issue=issue,
                workspace_path=str(workspace),
                session_id=session_id,
            )
            self._state.running[issue.id] = entry

            # Register session in metrics
            self._metrics.start_session(
                session_id=session_id,
                issue_id=issue.id,
                issue_identifier=issue.identifier,
                issue_title=issue.title,
            )

            # Launch agent as a background task
            task = asyncio.create_task(
                self._run_agent_session(issue, prompt, workspace, session_id, attempt),
                name=f"agent-{issue.id}-{session_id}",
            )
            self._tasks[issue.id] = task

        except Exception as exc:
            log.error(
                "dispatch_error",
                issue_id=issue.id,
                error=str(exc),
            )
            # Schedule retry
            self._schedule_retry(issue, attempt, str(exc))

    async def _run_agent_session(
        self,
        issue: Issue,
        prompt: str,
        workspace: Path,
        session_id: str,
        attempt: int,
    ) -> None:
        """Run an agent session and handle the result."""
        # Bind log context for all log lines in this task
        bind_context(issue_id=issue.id, session_id=session_id)

        try:
            # Run pre-run hook
            await self._workspace_mgr.run_hook("pre-run", workspace, fatal=False)

            # Run agent with timeout
            result = await asyncio.wait_for(
                self._runner.run(
                    issue=issue,
                    prompt=prompt,
                    workspace=workspace,
                    session_id=session_id,
                ),
                timeout=self._config.turn_timeout_seconds,
            )

            # Run post-run hook
            await self._workspace_mgr.run_hook("post-run", workspace, fatal=False)

            # Finish metrics for this session
            self._metrics.finish_session(
                session_id=session_id,
                success=result.success,
                error=result.error,
                turns=result.turns_used,
            )

            # Handle result
            await self._handle_agent_result(issue, result, attempt)

        except asyncio.TimeoutError:
            log.error(
                "agent_session_timeout",
                issue_id=issue.id,
                session_id=session_id,
                timeout=self._config.turn_timeout_seconds,
            )
            self._metrics.finish_session(
                session_id=session_id, success=False,
                error=f"Timed out after {self._config.turn_timeout_seconds}s",
            )
            await self._handle_agent_failure(
                issue, attempt, f"Agent timed out after {self._config.turn_timeout_seconds}s"
            )
        except asyncio.CancelledError:
            log.info("agent_session_cancelled", issue_id=issue.id, session_id=session_id)
            self._metrics.finish_session(
                session_id=session_id, success=False, error="Cancelled",
            )
        except Exception as exc:
            log.error(
                "agent_session_error",
                issue_id=issue.id,
                session_id=session_id,
                error=str(exc),
            )
            self._metrics.finish_session(
                session_id=session_id, success=False, error=str(exc),
            )
            await self._handle_agent_failure(issue, attempt, str(exc))
        finally:
            # Clean up running state and log context
            self._state.running.pop(issue.id, None)
            self._tasks.pop(issue.id, None)
            clear_context()

    async def _handle_agent_result(
        self, issue: Issue, result: AgentResult, attempt: int
    ) -> None:
        """Handle a completed agent session."""
        if result.success:
            log.info(
                "agent_session_success",
                issue_id=issue.id,
                session_id=result.session_id,
                turns_used=result.turns_used,
            )

            # ── Display results ──────────────────────────────────
            self._print_result(issue, result)

            self._state.completed.add(issue.id)
            # Transition issue to done
            try:
                await self._tracker.transition_issue(issue.id, IssueState.DONE)
            except Exception as exc:
                log.error(
                    "transition_error",
                    issue_id=issue.id,
                    error=str(exc),
                )
        else:
            await self._handle_agent_failure(issue, attempt, result.error)

    def _print_result(self, issue: Issue, result: AgentResult) -> None:
        """Print a human-readable summary of an agent session result."""
        separator = "=" * 72
        log.info(separator)
        log.info(
            "result_summary",
            issue=f"{issue.identifier} {issue.title}",
            status="SUCCESS" if result.success else "FAILED",
            session_id=result.session_id,
        )

        if result.output:
            log.info("agent_output", output=result.output[:2000])

        if result.diff:
            log.info("agent_diff", diff=result.diff[:3000])
        else:
            log.info("agent_no_changes", note="No file changes detected")

        # Also save full result to a file for later review
        self._save_result(issue, result)

        log.info(separator)

    def _save_result(self, issue: Issue, result: AgentResult) -> None:
        """Save full agent result to a file in the workspace base dir."""
        results_dir = self._config.workspace_base / "_results"
        results_dir.mkdir(parents=True, exist_ok=True)

        from symphony.workspace import sanitize_key
        filename = f"{sanitize_key(issue)}.md"
        result_file = results_dir / filename

        content = f"""# Agent Result: {issue.identifier} — {issue.title}

## Status: {"SUCCESS" if result.success else "FAILED"}

**Session:** {result.session_id}
**Turns:** {result.turns_used}

## Agent Output

{result.output}

## Changes (Diff)

```diff
{result.diff or "(no changes)"}
```

## Original Issue

{issue.description}
"""
        try:
            result_file.write_text(content, encoding="utf-8")
            log.info("result_saved", path=str(result_file))
        except OSError as exc:
            log.warning("result_save_failed", error=str(exc))

    async def _handle_agent_failure(
        self, issue: Issue, attempt: int, error: str
    ) -> None:
        """Handle a failed agent session — retry or mark as failed."""
        if attempt < self._config.max_retries:
            self._schedule_retry(issue, attempt, error)
        else:
            log.error(
                "agent_exhausted_retries",
                issue_id=issue.id,
                attempts=attempt,
                last_error=error,
            )
            self._state.failed.add(issue.id)

    # ------------------------------------------------------------------
    # Retry queue
    # ------------------------------------------------------------------

    def _schedule_retry(self, issue: Issue, attempt: int, error: str) -> None:
        """Add an issue to the retry queue with exponential backoff."""
        next_attempt = attempt + 1
        entry = RetryEntry.create(issue, next_attempt, error)

        log.info(
            "retry_scheduled",
            issue_id=issue.id,
            attempt=next_attempt,
            delay=RetryEntry.backoff_delay(next_attempt),
            next_retry_at=entry.next_retry_at,
        )

        self._state.retry_queue[issue.id] = entry

    async def _process_retries(self) -> None:
        """Check retry queue and re-dispatch eligible entries."""
        now = time.time()
        ready = [
            entry
            for entry in self._state.retry_queue.values()
            if entry.next_retry_at <= now
        ]

        for entry in ready:
            # Remove from retry queue before dispatching
            del self._state.retry_queue[entry.issue.id]

            # Re-fetch issue state from tracker
            try:
                current = await self._tracker.get_issue(entry.issue.id)
            except Exception as exc:
                log.error(
                    "retry_fetch_error",
                    issue_id=entry.issue.id,
                    error=str(exc),
                )
                # Put back in retry queue
                self._state.retry_queue[entry.issue.id] = entry
                continue

            if current is None or current.state.is_terminal:
                log.info(
                    "retry_skipped_terminal",
                    issue_id=entry.issue.id,
                    state=current.state.value if current else "not_found",
                )
                continue

            # Dispatch with incremented attempt
            await self._dispatch(current, entry.attempt)

    # ------------------------------------------------------------------
    # Reconciliation
    # ------------------------------------------------------------------

    async def _reconcile(self) -> None:
        """Reconcile running sessions against current tracker state.

        Checks:
        - Stall detection (no events for stall_timeout)
        - Issue state changed to terminal (someone closed the issue)
        """
        now = time.time()
        to_cancel: list[str] = []

        for issue_id, entry in list(self._state.running.items()):
            # Stall detection
            stall_elapsed = now - entry.last_event_at
            if stall_elapsed > self._config.stall_timeout_seconds:
                log.warning(
                    "stall_detected",
                    issue_id=issue_id,
                    stall_seconds=stall_elapsed,
                )
                to_cancel.append(issue_id)
                continue

            # Check if issue state changed
            try:
                current = await self._tracker.get_issue(issue_id)
            except Exception as exc:
                log.warning(
                    "reconcile_fetch_error",
                    issue_id=issue_id,
                    error=str(exc),
                )
                continue

            if current is None:
                log.warning("reconcile_issue_gone", issue_id=issue_id)
                to_cancel.append(issue_id)
                continue

            if current.state.is_terminal:
                log.info(
                    "reconcile_issue_terminal",
                    issue_id=issue_id,
                    state=current.state.value,
                )
                to_cancel.append(issue_id)
                self._state.completed.add(issue_id)

        # Cancel stale sessions
        for issue_id in to_cancel:
            await self._cancel_session(issue_id)

    async def _cancel_session(self, issue_id: str) -> None:
        """Cancel a running agent session."""
        task = self._tasks.get(issue_id)
        if task and not task.done():
            task.cancel()
            log.info("session_cancelled", issue_id=issue_id)

        self._state.running.pop(issue_id, None)
        self._tasks.pop(issue_id, None)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    async def _drain(self) -> None:
        """Drain all running sessions on shutdown."""
        log.info("draining_sessions", count=len(self._tasks))

        # Cancel all running agent tasks
        for issue_id, task in list(self._tasks.items()):
            if not task.done():
                task.cancel()

        # Wait for all tasks to finish
        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)

        self._tasks.clear()
        self._state.running.clear()

        # Close tracker client
        await self._tracker.close()

        log.info("orchestrator_stopped")
