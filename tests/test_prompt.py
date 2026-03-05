"""Tests for prompt.py — Liquid template rendering."""

from __future__ import annotations

import pytest

from symphony.models import Issue, IssueState
from symphony.prompt import PromptError, render_prompt


def _make_issue(**kwargs) -> Issue:
    defaults = {
        "id": "42",
        "identifier": "#42",
        "title": "Fix login bug",
        "description": "The login page crashes on submit",
        "state": IssueState.TODO,
        "labels": ["bug", "priority:1"],
        "priority": 1,
        "url": "https://github.com/org/repo/issues/42",
    }
    defaults.update(kwargs)
    return Issue(**defaults)


class TestRenderPrompt:
    def test_basic_render(self):
        template = "Fix {{ issue.identifier }}: {{ issue.title }}"
        result = render_prompt(template, _make_issue())
        assert result == "Fix #42: Fix login bug"

    def test_render_with_attempt(self):
        template = "Attempt {{ attempt }} for {{ issue.identifier }}"
        result = render_prompt(template, _make_issue(), attempt=3)
        assert result == "Attempt 3 for #42"

    def test_render_with_description(self):
        template = "{{ issue.description }}"
        result = render_prompt(template, _make_issue())
        assert result == "The login page crashes on submit"

    def test_render_with_extra_vars(self):
        template = "Model: {{ model_name }}"
        result = render_prompt(
            template, _make_issue(), extra_vars={"model_name": "gpt-4o"}
        )
        assert result == "Model: gpt-4o"

    def test_render_conditional(self):
        template = "{% if attempt > 1 %}RETRY{% endif %}"
        result1 = render_prompt(template, _make_issue(), attempt=1)
        result2 = render_prompt(template, _make_issue(), attempt=2)
        assert result1.strip() == ""
        assert result2.strip() == "RETRY"

    def test_empty_template(self):
        result = render_prompt("", _make_issue())
        assert result == ""
