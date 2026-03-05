"""Tests for workspace.py — workspace manager."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from symphony.models import Issue, IssueState
from symphony.workspace import WorkspaceError, WorkspaceManager, sanitize_key, _check_path_containment


def _make_issue(
    id: str = "42",
    identifier: str = "#42",
    title: str = "Fix login bug",
    state: IssueState = IssueState.TODO,
) -> Issue:
    return Issue(
        id=id,
        identifier=identifier,
        title=title,
        description="",
        state=state,
    )


class TestSanitizeKey:
    def test_basic(self):
        issue = _make_issue(identifier="#42", title="Fix login bug")
        key = sanitize_key(issue)
        assert key == "42-fix-login-bug"

    def test_special_chars(self):
        issue = _make_issue(identifier="#42", title="Fix: some/weird (chars)!")
        key = sanitize_key(issue)
        assert "/" not in key
        assert ":" not in key
        assert "(" not in key

    def test_long_title_truncated(self):
        issue = _make_issue(identifier="#1", title="A" * 200)
        key = sanitize_key(issue)
        assert len(key) <= 80

    def test_empty_title(self):
        issue = _make_issue(identifier="#99", title="")
        key = sanitize_key(issue)
        assert key == "99"


class TestPathContainment:
    def test_valid_path(self, tmp_path):
        workspace = tmp_path / "workspaces" / "test"
        base = tmp_path / "workspaces"
        base.mkdir()
        workspace.mkdir()
        # Should not raise
        _check_path_containment(workspace, base)

    def test_escape_raises(self, tmp_path):
        workspace = tmp_path / "workspaces" / ".." / "escape"
        base = tmp_path / "workspaces"
        base.mkdir()
        with pytest.raises(WorkspaceError, match="escapes base"):
            _check_path_containment(workspace, base)


class TestWorkspaceManager:
    @pytest.fixture
    def config(self, tmp_path):
        """Create a mock Config with tmp_path as workspace_base."""
        cfg = MagicMock()
        cfg.workspace_base = tmp_path / "workspaces"
        cfg.repo_url = ""
        cfg.source_dir = ""
        return cfg

    @pytest.fixture
    def manager(self, config):
        return WorkspaceManager(config)

    @pytest.mark.asyncio
    async def test_create_workspace(self, manager, config):
        issue = _make_issue()
        path = await manager.create_or_reuse(issue)
        assert path.exists()
        assert path.is_dir()
        assert str(path).startswith(str(config.workspace_base))

    @pytest.mark.asyncio
    async def test_reuse_workspace(self, manager):
        issue = _make_issue()
        path1 = await manager.create_or_reuse(issue)
        path2 = await manager.create_or_reuse(issue)
        assert path1 == path2

    @pytest.mark.asyncio
    async def test_cleanup(self, manager):
        issue = _make_issue()
        path = await manager.create_or_reuse(issue)
        assert path.exists()
        await manager.cleanup(path)
        assert not path.exists()

    @pytest.mark.asyncio
    async def test_hook_not_found_returns_true(self, manager):
        issue = _make_issue()
        path = await manager.create_or_reuse(issue)
        result = await manager.run_hook("nonexistent", path)
        assert result is True


class TestSourceDirCopy:
    """Test that source_dir contents are copied into the workspace."""

    @pytest.fixture
    def source_project(self, tmp_path):
        """Create a small source project directory."""
        src = tmp_path / "my_project"
        src.mkdir()
        (src / "main.py").write_text("print('hello')\n")
        (src / "lib").mkdir()
        (src / "lib" / "utils.py").write_text("def helper(): pass\n")
        # Should be skipped
        (src / "__pycache__").mkdir()
        (src / "__pycache__" / "main.cpython-311.pyc").write_text("bytecode")
        (src / ".env").write_text("SECRET=123")
        return src

    @pytest.fixture
    def config_with_source(self, tmp_path, source_project):
        cfg = MagicMock()
        cfg.workspace_base = tmp_path / "workspaces"
        cfg.repo_url = ""
        cfg.source_dir = str(source_project)
        return cfg

    @pytest.mark.asyncio
    async def test_copies_source_files(self, config_with_source):
        manager = WorkspaceManager(config_with_source)
        issue = _make_issue()
        path = await manager.create_or_reuse(issue)
        assert (path / "main.py").is_file()
        assert (path / "main.py").read_text() == "print('hello')\n"
        assert (path / "lib" / "utils.py").is_file()

    @pytest.mark.asyncio
    async def test_skips_ignored_dirs(self, config_with_source):
        manager = WorkspaceManager(config_with_source)
        issue = _make_issue()
        path = await manager.create_or_reuse(issue)
        assert not (path / "__pycache__").exists()

    @pytest.mark.asyncio
    async def test_skips_env_file(self, config_with_source):
        manager = WorkspaceManager(config_with_source)
        issue = _make_issue()
        path = await manager.create_or_reuse(issue)
        assert not (path / ".env").exists()

    @pytest.mark.asyncio
    async def test_initialises_git(self, config_with_source):
        manager = WorkspaceManager(config_with_source)
        issue = _make_issue()
        path = await manager.create_or_reuse(issue)
        assert (path / ".git").is_dir()
