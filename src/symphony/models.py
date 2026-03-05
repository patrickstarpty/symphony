"""Domain models for the Symphony orchestrator.

Covers: Issue, RetryEntry, RunningEntry, OrchestratorState.
Based on SPEC.md Section 4.1.1 normalised Issue model.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Issue model (normalised from any tracker)
# ---------------------------------------------------------------------------

class IssueState(str, Enum):
    """Normalised issue states across trackers."""

    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELED = "canceled"

    @property
    def is_terminal(self) -> bool:
        return self in (IssueState.DONE, IssueState.CANCELED)

    @property
    def is_active(self) -> bool:
        """States where an agent should be running."""
        return self in (IssueState.TODO, IssueState.IN_PROGRESS)


@dataclass(frozen=True)
class Issue:
    """Normalised issue from any tracker (spec Section 4.1.1)."""

    id: str  # Tracker-specific unique ID
    identifier: str  # Human-readable identifier (e.g. "ORG-123", "#42")
    title: str
    description: str
    state: IssueState
    labels: list[str] = field(default_factory=list)
    priority: int = 0  # 0 = no priority, 1 = urgent, 4 = low
    blocked_by: list[str] = field(default_factory=list)  # IDs of blocking issues
    url: str = ""
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


# ---------------------------------------------------------------------------
# Orchestrator state entries
# ---------------------------------------------------------------------------

@dataclass
class RetryEntry:
    """An issue awaiting retry (spec Section 8.5)."""

    issue: Issue
    attempt: int  # Current attempt number (1-based)
    next_retry_at: float  # Unix timestamp
    last_error: str = ""

    @staticmethod
    def backoff_delay(attempt: int, base: float = 10.0, cap: float = 300.0) -> float:
        """Compute exponential backoff: base * 2^(attempt-1), capped."""
        return min(base * (2 ** (attempt - 1)), cap)

    @classmethod
    def create(cls, issue: Issue, attempt: int, error: str = "") -> RetryEntry:
        delay = cls.backoff_delay(attempt)
        return cls(
            issue=issue,
            attempt=attempt,
            next_retry_at=time.time() + delay,
            last_error=error,
        )


@dataclass
class RunningEntry:
    """A currently running agent session (spec Section 7.3)."""

    issue: Issue
    workspace_path: str
    started_at: float = field(default_factory=time.time)
    last_event_at: float = field(default_factory=time.time)
    turns: int = 0
    session_id: str = ""

    def touch(self) -> None:
        """Record that activity occurred."""
        self.last_event_at = time.time()

    def increment_turn(self) -> None:
        self.turns += 1
        self.touch()


@dataclass
class OrchestratorState:
    """In-memory state of the orchestrator (spec Section 7.2)."""

    running: dict[str, RunningEntry] = field(default_factory=dict)  # keyed by issue.id
    retry_queue: dict[str, RetryEntry] = field(default_factory=dict)  # keyed by issue.id
    completed: set[str] = field(default_factory=set)  # issue IDs we've finished
    failed: set[str] = field(default_factory=set)  # issue IDs that exhausted retries

    @property
    def running_count(self) -> int:
        return len(self.running)

    def running_count_by_state(self, state: IssueState) -> int:
        return sum(1 for e in self.running.values() if e.issue.state == state)

    def is_known(self, issue_id: str) -> bool:
        """Check if an issue is already tracked (running, retrying, completed, or failed)."""
        return (
            issue_id in self.running
            or issue_id in self.retry_queue
            or issue_id in self.completed
            or issue_id in self.failed
        )
