"""Abstract tracker client protocol.

Any tracker adapter must implement these three operations:
1. ``fetch_issues()`` — list eligible issues
2. ``get_issue(issue_id)`` — get a single issue by ID
3. ``transition_issue(issue_id, to_state)`` — move issue to a new state
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from symphony.models import Issue, IssueState


class TrackerClient(ABC):
    """Abstract base for issue tracker adapters."""

    @abstractmethod
    async def fetch_issues(self) -> list[Issue]:
        """Return all issues eligible for agent work.

        Typically filters by state (e.g. "Todo") and other criteria
        defined in the workflow configuration.
        """
        ...

    @abstractmethod
    async def get_issue(self, issue_id: str) -> Issue | None:
        """Fetch a single issue by its tracker ID.

        Returns None if the issue doesn't exist.
        """
        ...

    @abstractmethod
    async def transition_issue(self, issue_id: str, to_state: IssueState) -> bool:
        """Attempt to transition an issue to a new state.

        Returns True if the transition succeeded, False otherwise.
        Some trackers may not support programmatic transitions.
        """
        ...

    async def close(self) -> None:
        """Clean up any resources (HTTP clients, etc.)."""
