"""Tests for tracker/github.py — GitHub Issues adapter and base protocol."""

from __future__ import annotations

import pytest

from symphony.models import IssueState
from symphony.tracker.github import _parse_issue, DEFAULT_LABEL_STATE_MAP


def _gh_issue(
    number: int = 42,
    title: str = "Fix bug",
    state: str = "open",
    labels: list[str] | None = None,
    body: str = "",
    state_reason: str | None = None,
) -> dict:
    """Create a mock GitHub API issue response."""
    lbl_objects = [{"name": lbl} for lbl in (labels or [])]
    issue = {
        "number": number,
        "title": title,
        "state": state,
        "labels": lbl_objects,
        "body": body,
        "html_url": f"https://github.com/org/repo/issues/{number}",
    }
    if state_reason:
        issue["state_reason"] = state_reason
    return issue


class TestParseIssue:
    def test_open_with_todo_label(self):
        data = _gh_issue(labels=["symphony:todo"])
        issue = _parse_issue(data, DEFAULT_LABEL_STATE_MAP)
        assert issue.id == "42"
        assert issue.identifier == "#42"
        assert issue.state == IssueState.TODO

    def test_open_no_symphony_label(self):
        data = _gh_issue(labels=["bug"])
        issue = _parse_issue(data, DEFAULT_LABEL_STATE_MAP)
        assert issue.state == IssueState.BACKLOG

    def test_closed_completed(self):
        data = _gh_issue(state="closed", state_reason="completed")
        issue = _parse_issue(data, DEFAULT_LABEL_STATE_MAP)
        assert issue.state == IssueState.DONE

    def test_closed_not_planned(self):
        data = _gh_issue(state="closed", state_reason="not_planned")
        issue = _parse_issue(data, DEFAULT_LABEL_STATE_MAP)
        assert issue.state == IssueState.CANCELED

    def test_in_progress_label(self):
        data = _gh_issue(labels=["symphony:in-progress"])
        issue = _parse_issue(data, DEFAULT_LABEL_STATE_MAP)
        assert issue.state == IssueState.IN_PROGRESS

    def test_priority_from_label(self):
        data = _gh_issue(labels=["symphony:todo", "priority:1"])
        issue = _parse_issue(data, DEFAULT_LABEL_STATE_MAP)
        assert issue.priority == 1

    def test_labels_preserved(self):
        data = _gh_issue(labels=["symphony:todo", "bug", "frontend"])
        issue = _parse_issue(data, DEFAULT_LABEL_STATE_MAP)
        assert "bug" in issue.labels
        assert "frontend" in issue.labels
        assert "symphony:todo" in issue.labels

    def test_body_as_description(self):
        data = _gh_issue(body="Detailed description here")
        issue = _parse_issue(data, DEFAULT_LABEL_STATE_MAP)
        assert issue.description == "Detailed description here"

    def test_url_preserved(self):
        data = _gh_issue(number=99)
        issue = _parse_issue(data, DEFAULT_LABEL_STATE_MAP)
        assert issue.url == "https://github.com/org/repo/issues/99"
