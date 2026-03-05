"""File-based tracker adapter for local development and testing.

Reads issues from a JSON or YAML file. Useful for:
- Local development without needing a GitHub token
- Testing the orchestrator without external dependencies
- Demos and CI

Example issues file (JSON)::

    [
      {
        "id": "1",
        "identifier": "#1",
        "title": "Add user authentication",
        "description": "Implement JWT-based auth for the API.",
        "state": "todo",
        "labels": ["feature"],
        "priority": 1
      }
    ]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from symphony.config import TrackerConfig
from symphony.log import get_logger
from symphony.models import Issue, IssueState
from symphony.tracker.base import TrackerClient

log = get_logger(__name__)


def _parse_state(raw: str) -> IssueState:
    """Parse a state string into IssueState, with flexible matching."""
    mapping = {
        "backlog": IssueState.BACKLOG,
        "todo": IssueState.TODO,
        "to_do": IssueState.TODO,
        "to-do": IssueState.TODO,
        "in_progress": IssueState.IN_PROGRESS,
        "in-progress": IssueState.IN_PROGRESS,
        "in_review": IssueState.IN_REVIEW,
        "in-review": IssueState.IN_REVIEW,
        "done": IssueState.DONE,
        "canceled": IssueState.CANCELED,
        "cancelled": IssueState.CANCELED,
    }
    normalised = raw.strip().lower()
    if normalised in mapping:
        return mapping[normalised]
    # Try direct enum value
    try:
        return IssueState(normalised)
    except ValueError:
        log.warning("unknown_issue_state", raw=raw, defaulting_to="backlog")
        return IssueState.BACKLOG


def _parse_issue(data: dict[str, Any]) -> Issue:
    """Parse a single issue dict into an Issue model."""
    return Issue(
        id=str(data["id"]),
        identifier=str(data.get("identifier", f"#{data['id']}")),
        title=str(data.get("title", "")),
        description=str(data.get("description", "")),
        state=_parse_state(str(data.get("state", "todo"))),
        labels=list(data.get("labels", [])),
        priority=int(data.get("priority", 0)),
        blocked_by=list(data.get("blocked_by", [])),
        url=str(data.get("url", "")),
        raw=data,
    )


def _load_file(path: Path) -> list[dict[str, Any]]:
    """Load issues from a JSON or YAML file."""
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in (".json",):
        data = json.loads(text)
    elif suffix in (".yaml", ".yml"):
        data = yaml.safe_load(text)
    else:
        # Try JSON first, then YAML
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = yaml.safe_load(text)

    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "issues" in data:
        return data["issues"]
    raise ValueError(f"Expected a JSON array or object with 'issues' key, got {type(data).__name__}")


class FileTracker(TrackerClient):
    """File-based tracker that reads issues from a local JSON/YAML file.

    The file is re-read on every ``fetch_issues()`` call, so you can
    edit it while Symphony is running to simulate issue state changes.
    """

    def __init__(self, tracker_config: TrackerConfig) -> None:
        self._config = tracker_config
        # 'repo' field is repurposed as the path to the issues file
        file_path = tracker_config.repo or tracker_config.extra.get("file", "")
        if not file_path:
            raise ValueError(
                "File tracker requires 'tracker.repo' or 'tracker.file' pointing "
                "to a JSON/YAML issues file"
            )
        self._path = Path(file_path).expanduser().resolve()
        if not self._path.is_file():
            raise FileNotFoundError(f"Issues file not found: {self._path}")

        log.info("file_tracker_init", path=str(self._path))

    async def fetch_issues(self) -> list[Issue]:
        """Read all active issues from the file."""
        try:
            raw_issues = _load_file(self._path)
        except Exception as exc:
            log.error("file_tracker_load_error", path=str(self._path), error=str(exc))
            return []

        all_issues = [_parse_issue(item) for item in raw_issues]

        # Only return issues in active states (like a real tracker query would)
        active = [i for i in all_issues if i.state.is_active]
        log.info(
            "file_issues_fetched",
            total=len(all_issues),
            active=len(active),
            path=str(self._path),
        )
        return active

    async def get_issue(self, issue_id: str) -> Issue | None:
        """Look up a single issue by ID from the file."""
        try:
            raw_issues = _load_file(self._path)
        except Exception:
            return None

        for item in raw_issues:
            if str(item.get("id")) == issue_id:
                return _parse_issue(item)
        return None

    async def transition_issue(self, issue_id: str, to_state: IssueState) -> bool:
        """Update an issue's state in the file.

        Reads the file, modifies the matching issue, and writes it back.
        """
        try:
            raw_issues = _load_file(self._path)
        except Exception as exc:
            log.error("file_tracker_transition_error", error=str(exc))
            return False

        for item in raw_issues:
            if str(item.get("id")) == issue_id:
                item["state"] = to_state.value
                log.info(
                    "file_issue_transitioned",
                    issue_id=issue_id,
                    to_state=to_state.value,
                )
                # Write back
                suffix = self._path.suffix.lower()
                if suffix in (".yaml", ".yml"):
                    self._path.write_text(
                        yaml.dump(raw_issues, default_flow_style=False),
                        encoding="utf-8",
                    )
                else:
                    self._path.write_text(
                        json.dumps(raw_issues, indent=2) + "\n",
                        encoding="utf-8",
                    )
                return True

        log.warning("file_issue_not_found", issue_id=issue_id)
        return False

    async def close(self) -> None:
        """No-op for file tracker."""
