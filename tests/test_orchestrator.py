"""Tests for orchestrator.py — dispatch, concurrency, reconciliation, retry."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from symphony.agent_runner import AgentResult
from symphony.config import Config, TrackerConfig
from symphony.models import Issue, IssueState, OrchestratorState, RetryEntry
from symphony.orchestrator import Orchestrator


def _make_issue(
    id: str = "42",
    identifier: str = "#42",
    title: str = "Fix bug",
    state: IssueState = IssueState.TODO,
    blocked_by: list[str] | None = None,
) -> Issue:
    return Issue(
        id=id,
        identifier=identifier,
        title=title,
        description="description",
        state=state,
        blocked_by=blocked_by or [],
    )


def _make_config(
    max_concurrent: int = 10,
    max_concurrent_by_state: dict | None = None,
    max_retries: int = 5,
    poll_seconds: int = 1,
    stall_timeout: int = 300,
) -> Config:
    return Config(
        name="test",
        workflow_path=Path("/tmp/WORKFLOW.md"),
        tracker=TrackerConfig(kind="github", repo="o/r", token_env="GITHUB_TOKEN"),
        max_concurrent_agents=max_concurrent,
        max_concurrent_agents_by_state=max_concurrent_by_state or {},
        max_retries=max_retries,
        poll_seconds=poll_seconds,
        stall_timeout_seconds=stall_timeout,
    )


@pytest.fixture
def mock_tracker():
    tracker = AsyncMock()
    tracker.fetch_issues = AsyncMock(return_value=[])
    tracker.get_issue = AsyncMock(return_value=None)
    tracker.transition_issue = AsyncMock(return_value=True)
    tracker.close = AsyncMock()
    return tracker


@pytest.fixture
def mock_runner():
    with patch("symphony.orchestrator.create_runner") as mock:
        runner = AsyncMock()
        runner.run = AsyncMock(
            return_value=AgentResult(success=True, session_id="test-session")
        )
        mock.return_value = runner
        yield runner


class TestDispatchEligible:
    @pytest.mark.asyncio
    async def test_dispatch_new_issue(self, mock_tracker, mock_runner):
        config = _make_config()
        orch = Orchestrator(config, mock_tracker, "prompt template")
        issue = _make_issue()
        result = await orch._maybe_dispatch(issue)
        assert result is True
        assert issue.id in orch.state.running

    @pytest.mark.asyncio
    async def test_skip_known_issue(self, mock_tracker, mock_runner):
        config = _make_config()
        orch = Orchestrator(config, mock_tracker, "prompt")
        issue = _make_issue()
        orch._state.completed.add(issue.id)
        result = await orch._maybe_dispatch(issue)
        assert result is False

    @pytest.mark.asyncio
    async def test_skip_terminal_state(self, mock_tracker, mock_runner):
        config = _make_config()
        orch = Orchestrator(config, mock_tracker, "prompt")
        issue = _make_issue(state=IssueState.DONE)
        result = await orch._maybe_dispatch(issue)
        assert result is False


class TestConcurrencyLimit:
    @pytest.mark.asyncio
    async def test_global_limit(self, mock_tracker, mock_runner):
        config = _make_config(max_concurrent=2)
        orch = Orchestrator(config, mock_tracker, "prompt")

        # Make the runner block so sessions stay in "running"
        hold = asyncio.Event()

        async def _slow_run(**kwargs):
            await hold.wait()
            return AgentResult(success=True, session_id="test-session")

        mock_runner.run = AsyncMock(side_effect=_slow_run)

        # Fill up with running entries
        for i in range(2):
            issue = _make_issue(id=str(i), identifier=f"#{i}")
            await orch._maybe_dispatch(issue)
        # Let the event loop schedule the tasks
        await asyncio.sleep(0)

        # This one should be skipped — at global limit
        extra = _make_issue(id="extra", identifier="#extra")
        result = await orch._maybe_dispatch(extra)
        assert result is False

        # Release the held tasks
        hold.set()
        await asyncio.sleep(0.05)

    @pytest.mark.asyncio
    async def test_per_state_limit(self, mock_tracker, mock_runner):
        config = _make_config(max_concurrent_by_state={"todo": 1})
        orch = Orchestrator(config, mock_tracker, "prompt")

        # Make the runner block so sessions stay in "running"
        hold = asyncio.Event()

        async def _slow_run(**kwargs):
            await hold.wait()
            return AgentResult(success=True, session_id="test-session")

        mock_runner.run = AsyncMock(side_effect=_slow_run)

        issue1 = _make_issue(id="1", identifier="#1", state=IssueState.TODO)
        await orch._maybe_dispatch(issue1)
        await asyncio.sleep(0)

        issue2 = _make_issue(id="2", identifier="#2", state=IssueState.TODO)
        result = await orch._maybe_dispatch(issue2)
        assert result is False

        # Release the held tasks
        hold.set()
        await asyncio.sleep(0.05)


class TestRetryScheduling:
    def test_backoff_delay(self):
        assert RetryEntry.backoff_delay(1) == 10.0
        assert RetryEntry.backoff_delay(2) == 20.0
        assert RetryEntry.backoff_delay(3) == 40.0
        assert RetryEntry.backoff_delay(4) == 80.0
        # Verify cap
        assert RetryEntry.backoff_delay(10) == 300.0  # capped at 5 min

    def test_retry_entry_create(self):
        issue = _make_issue()
        entry = RetryEntry.create(issue, attempt=2, error="timeout")
        assert entry.attempt == 2
        assert entry.last_error == "timeout"
        assert entry.next_retry_at > time.time()

    @pytest.mark.asyncio
    async def test_retry_dispatch(self, mock_tracker, mock_runner):
        config = _make_config(max_retries=3)
        orch = Orchestrator(config, mock_tracker, "prompt")
        issue = _make_issue()

        # Manually schedule a retry that's ready
        entry = RetryEntry(
            issue=issue,
            attempt=2,
            next_retry_at=time.time() - 1,  # in the past = ready
            last_error="previous error",
        )
        orch._state.retry_queue[issue.id] = entry

        # Mock tracker to return the issue
        mock_tracker.get_issue.return_value = issue

        await orch._process_retries()

        # Should have been dispatched (moved to running)
        assert issue.id not in orch._state.retry_queue
        assert issue.id in orch._state.running


class TestBlockedIssues:
    @pytest.mark.asyncio
    async def test_skip_blocked(self, mock_tracker, mock_runner):
        config = _make_config()
        orch = Orchestrator(config, mock_tracker, "prompt")
        issue = _make_issue(blocked_by=["99"])
        result = await orch._maybe_dispatch(issue)
        assert result is False

    @pytest.mark.asyncio
    async def test_dispatch_unblocked(self, mock_tracker, mock_runner):
        config = _make_config()
        orch = Orchestrator(config, mock_tracker, "prompt")
        issue = _make_issue(blocked_by=["99"])
        orch._state.completed.add("99")  # blocker is done
        result = await orch._maybe_dispatch(issue)
        assert result is True
