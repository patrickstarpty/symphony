"""Token accounting and session metrics.

Tracks per-session and aggregate metrics:
- Token usage (prompt + completion)
- Runtime duration
- Success/failure counts
- Rate limit events

Spec Section 13 — Observability.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from symphony.log import get_logger

log = get_logger(__name__)


@dataclass
class SessionMetrics:
    """Metrics for a single agent session."""

    session_id: str
    issue_id: str
    issue_identifier: str = ""
    issue_title: str = ""
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None

    # Token usage
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    # Execution
    turns: int = 0
    success: bool | None = None  # None = still running
    error: str = ""

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds (so far if still running)."""
        end = self.finished_at or time.time()
        return end - self.started_at

    @property
    def status(self) -> str:
        if self.success is None:
            return "running"
        return "success" if self.success else "failed"

    def finish(self, success: bool, error: str = "") -> None:
        """Mark the session as finished."""
        self.finished_at = time.time()
        self.success = success
        self.error = error

    def record_tokens(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> None:
        """Add token usage from an LLM call."""
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens = self.prompt_tokens + self.completion_tokens

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a dict for API responses."""
        return {
            "session_id": self.session_id,
            "issue_id": self.issue_id,
            "issue_identifier": self.issue_identifier,
            "issue_title": self.issue_title,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": round(self.duration_seconds, 1),
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "turns": self.turns,
            "status": self.status,
            "error": self.error,
        }


@dataclass
class AggregateMetrics:
    """Aggregate metrics across all sessions."""

    total_sessions: int = 0
    successful_sessions: int = 0
    failed_sessions: int = 0
    running_sessions: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_runtime_seconds: float = 0.0
    rate_limit_events: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a dict for API responses."""
        return {
            "total_sessions": self.total_sessions,
            "successful_sessions": self.successful_sessions,
            "failed_sessions": self.failed_sessions,
            "running_sessions": self.running_sessions,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "total_runtime_seconds": round(self.total_runtime_seconds, 1),
            "rate_limit_events": self.rate_limit_events,
        }


class MetricsCollector:
    """Central metrics collector for all agent sessions.

    Thread-safe: all mutations happen in the asyncio event loop.
    The dashboard server reads via ``snapshot()`` which returns a copy.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionMetrics] = {}  # session_id -> metrics
        self._aggregate = AggregateMetrics()
        self._started_at = time.time()

    @property
    def uptime_seconds(self) -> float:
        """How long the orchestrator has been running."""
        return time.time() - self._started_at

    def start_session(
        self,
        session_id: str,
        issue_id: str,
        issue_identifier: str = "",
        issue_title: str = "",
    ) -> SessionMetrics:
        """Register a new agent session."""
        session = SessionMetrics(
            session_id=session_id,
            issue_id=issue_id,
            issue_identifier=issue_identifier,
            issue_title=issue_title,
        )
        self._sessions[session_id] = session
        self._aggregate.total_sessions += 1
        self._aggregate.running_sessions += 1

        log.debug(
            "metrics_session_started",
            session_id=session_id,
            issue_id=issue_id,
        )
        return session

    def finish_session(
        self,
        session_id: str,
        success: bool,
        error: str = "",
        turns: int = 0,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> SessionMetrics | None:
        """Mark a session as finished and update aggregates."""
        session = self._sessions.get(session_id)
        if session is None:
            log.warning("metrics_unknown_session", session_id=session_id)
            return None

        session.finish(success=success, error=error)
        session.turns = turns
        session.record_tokens(prompt_tokens, completion_tokens)

        # Update aggregates
        self._aggregate.running_sessions = max(0, self._aggregate.running_sessions - 1)
        if success:
            self._aggregate.successful_sessions += 1
        else:
            self._aggregate.failed_sessions += 1

        self._aggregate.total_prompt_tokens += prompt_tokens
        self._aggregate.total_completion_tokens += completion_tokens
        self._aggregate.total_tokens += prompt_tokens + completion_tokens
        self._aggregate.total_runtime_seconds += session.duration_seconds

        log.debug(
            "metrics_session_finished",
            session_id=session_id,
            success=success,
            duration=round(session.duration_seconds, 1),
            tokens=session.total_tokens,
        )
        return session

    def record_rate_limit(self) -> None:
        """Record a rate limit event."""
        self._aggregate.rate_limit_events += 1
        log.warning("metrics_rate_limit")

    def snapshot(self) -> dict[str, Any]:
        """Return a complete snapshot of all metrics for API responses.

        Returns a dict suitable for JSON serialisation.
        """
        running = [
            s.to_dict() for s in self._sessions.values() if s.success is None
        ]
        recent = sorted(
            (s for s in self._sessions.values() if s.success is not None),
            key=lambda s: s.finished_at or 0,
            reverse=True,
        )[:50]  # Last 50 completed sessions

        return {
            "uptime_seconds": round(self.uptime_seconds, 1),
            "aggregate": self._aggregate.to_dict(),
            "running_sessions": running,
            "recent_sessions": [s.to_dict() for s in recent],
        }

    def get_session(self, session_id: str) -> SessionMetrics | None:
        """Look up a specific session."""
        return self._sessions.get(session_id)
