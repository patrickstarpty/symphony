"""Tests for workflow.py — WORKFLOW.md loader."""

from __future__ import annotations

import pytest
from pathlib import Path

from symphony.workflow import WorkflowError, load_workflow


@pytest.fixture
def tmp_workflow(tmp_path: Path):
    """Helper to create a temporary workflow file."""

    def _create(content: str) -> Path:
        p = tmp_path / "WORKFLOW.md"
        p.write_text(content, encoding="utf-8")
        return p

    return _create


class TestLoadWorkflow:
    def test_valid_workflow(self, tmp_workflow):
        path = tmp_workflow(
            "---\nname: test-flow\ntracker:\n  kind: github\n  repo: o/r\n---\nHello {{ issue.title }}\n"
        )
        wf = load_workflow(path)
        assert wf.name == "test-flow"
        assert wf.prompt_template == "Hello {{ issue.title }}"
        assert wf.tracker["kind"] == "github"
        assert wf.tracker["repo"] == "o/r"

    def test_missing_file(self, tmp_path):
        with pytest.raises(WorkflowError, match="not found"):
            load_workflow(tmp_path / "nonexistent.md")

    def test_bad_yaml(self, tmp_workflow):
        path = tmp_workflow("---\n: invalid: yaml: [}\n---\nbody\n")
        with pytest.raises(WorkflowError, match="Invalid YAML"):
            load_workflow(path)

    def test_non_map_front_matter(self, tmp_workflow):
        path = tmp_workflow("---\n- a list\n- not a map\n---\nbody\n")
        with pytest.raises(WorkflowError, match="must be a YAML mapping"):
            load_workflow(path)

    def test_missing_name(self, tmp_workflow):
        path = tmp_workflow("---\ntracker:\n  kind: github\n---\nbody\n")
        with pytest.raises(WorkflowError, match="'name' field"):
            load_workflow(path)

    def test_no_front_matter_fences(self, tmp_workflow):
        path = tmp_workflow("just a plain file\nno front matter\n")
        with pytest.raises(WorkflowError, match="front matter"):
            load_workflow(path)

    def test_config_properties(self, tmp_workflow):
        path = tmp_workflow(
            "---\nname: x\npoll_seconds: 60\nmax_concurrent_agents: 3\nmax_turns: 10\n---\nprompt\n"
        )
        wf = load_workflow(path)
        assert wf.poll_seconds == 60
        assert wf.max_concurrent_agents == 3
        assert wf.max_turns == 10
        # Defaults
        assert wf.turn_timeout_seconds == 3600
        assert wf.stall_timeout_seconds == 300
        assert wf.max_retries == 5
