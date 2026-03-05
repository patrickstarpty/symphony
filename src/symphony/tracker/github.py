"""GitHub Issues tracker adapter.

Maps GitHub Issues to the normalised Issue model.
Uses labels to represent workflow states since GitHub Issues
don't have native state columns like Linear.

Label mapping (configurable):
- ``symphony:todo`` → IssueState.TODO
- ``symphony:in-progress`` → IssueState.IN_PROGRESS
- ``symphony:in-review`` → IssueState.IN_REVIEW
- ``symphony:done`` → IssueState.DONE (also: closed issues)
- ``symphony:canceled`` → IssueState.CANCELED (also: closed + not-planned)
"""

from __future__ import annotations

import httpx

from symphony.config import TrackerConfig
from symphony.log import get_logger
from symphony.models import Issue, IssueState
from symphony.tracker.base import TrackerClient

log = get_logger(__name__)

# Default mapping from GitHub labels to normalised states
DEFAULT_LABEL_STATE_MAP: dict[str, IssueState] = {
    "symphony:todo": IssueState.TODO,
    "symphony:in-progress": IssueState.IN_PROGRESS,
    "symphony:in-review": IssueState.IN_REVIEW,
    "symphony:done": IssueState.DONE,
    "symphony:canceled": IssueState.CANCELED,
}

# Reverse mapping for transitions
DEFAULT_STATE_LABEL_MAP: dict[IssueState, str] = {
    v: k for k, v in DEFAULT_LABEL_STATE_MAP.items()
}


def _parse_issue(data: dict, label_state_map: dict[str, IssueState]) -> Issue:
    """Convert a GitHub API issue response to a normalised Issue."""
    labels = [lbl["name"] if isinstance(lbl, dict) else lbl for lbl in data.get("labels", [])]

    # Determine state from labels (first matching label wins)
    state = IssueState.BACKLOG  # default for open issues with no symphony label
    for label in labels:
        if label in label_state_map:
            state = label_state_map[label]
            break

    # Handle closed issues
    if data.get("state") == "closed":
        reason = data.get("state_reason", "completed")
        if state not in (IssueState.DONE, IssueState.CANCELED):
            state = IssueState.CANCELED if reason == "not_planned" else IssueState.DONE

    # Extract blocked_by from issue body (convention: "blocked by #123")
    blocked_by: list[str] = []
    body = data.get("body") or ""

    # Priority from labels (convention: priority:1 through priority:4)
    priority = 0
    for label in labels:
        if label.startswith("priority:"):
            try:
                priority = int(label.split(":")[1])
            except (ValueError, IndexError):
                pass

    return Issue(
        id=str(data["number"]),
        identifier=f"#{data['number']}",
        title=data.get("title", ""),
        description=body,
        state=state,
        labels=labels,
        priority=priority,
        blocked_by=blocked_by,
        url=data.get("html_url", ""),
        raw=data,
    )


class GitHubTracker(TrackerClient):
    """GitHub Issues tracker adapter."""

    def __init__(self, tracker_config: TrackerConfig) -> None:
        self._config = tracker_config
        self._repo = tracker_config.repo  # "owner/repo"
        base_url = tracker_config.api_url or "https://api.github.com"
        self._base_url = base_url.rstrip("/")

        # Label-to-state mapping (can be overridden via config)
        self._label_state_map = dict(DEFAULT_LABEL_STATE_MAP)
        custom_map = tracker_config.extra.get("label_state_map", {})
        for label, state_str in custom_map.items():
            try:
                self._label_state_map[label] = IssueState(state_str)
            except ValueError:
                log.warning("unknown_state_in_label_map", label=label, state=state_str)

        self._state_label_map = {v: k for k, v in self._label_state_map.items()}

        # Build HTTP client
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        try:
            headers["Authorization"] = f"Bearer {tracker_config.token}"
        except Exception:
            log.warning("github_token_not_available", hint="Set $GITHUB_TOKEN")

        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=30.0,
        )

        log.info("github_tracker_init", repo=self._repo)

    async def fetch_issues(self) -> list[Issue]:
        """Fetch open issues with a ``symphony:todo`` label (default) or custom query."""
        # Fetch issues that are open and have any symphony label
        query_label = self._config.extra.get("fetch_label", "symphony:todo")
        params: dict[str, str | int] = {
            "state": "open",
            "labels": query_label,
            "per_page": 100,
            "sort": "created",
            "direction": "asc",
        }

        url = f"/repos/{self._repo}/issues"
        log.debug("github_fetch_issues", url=url, params=params)

        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        # Filter out pull requests (GitHub API returns PRs mixed with issues)
        issues_data = [item for item in data if "pull_request" not in item]

        issues = [_parse_issue(item, self._label_state_map) for item in issues_data]
        log.info("github_issues_fetched", count=len(issues))
        return issues

    async def get_issue(self, issue_id: str) -> Issue | None:
        """Fetch a single issue by number."""
        url = f"/repos/{self._repo}/issues/{issue_id}"
        resp = await self._client.get(url)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return _parse_issue(resp.json(), self._label_state_map)

    async def transition_issue(self, issue_id: str, to_state: IssueState) -> bool:
        """Transition an issue by changing its labels.

        Removes any existing symphony state labels and adds the target one.
        For terminal states (DONE, CANCELED), also closes the issue.
        """
        target_label = self._state_label_map.get(to_state)
        if not target_label:
            log.warning("no_label_for_state", state=to_state, issue_id=issue_id)
            return False

        # Get current labels
        issue = await self.get_issue(issue_id)
        if issue is None:
            return False

        # Remove existing symphony state labels, add new one
        current_labels = [
            lbl for lbl in issue.labels if lbl not in self._label_state_map
        ]
        current_labels.append(target_label)

        url = f"/repos/{self._repo}/issues/{issue_id}"
        payload: dict[str, object] = {"labels": current_labels}

        # Close issue for terminal states
        if to_state.is_terminal:
            payload["state"] = "closed"
            if to_state == IssueState.CANCELED:
                payload["state_reason"] = "not_planned"
            else:
                payload["state_reason"] = "completed"

        resp = await self._client.patch(url, json=payload)
        if resp.status_code >= 400:
            log.error(
                "github_transition_failed",
                issue_id=issue_id,
                status=resp.status_code,
                body=resp.text,
            )
            return False

        log.info("github_issue_transitioned", issue_id=issue_id, to_state=to_state.value)
        return True

    async def close(self) -> None:
        await self._client.aclose()
