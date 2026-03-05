"""Tests for config.py — typed configuration layer."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from symphony.config import ConfigError, build_config, _resolve_env_vars


class TestEnvVarResolution:
    def test_dollar_var(self, monkeypatch):
        monkeypatch.setenv("MY_TOKEN", "secret123")
        assert _resolve_env_vars("token=$MY_TOKEN") == "token=secret123"

    def test_braced_var(self, monkeypatch):
        monkeypatch.setenv("MY_TOKEN", "secret123")
        assert _resolve_env_vars("token=${MY_TOKEN}") == "token=secret123"

    def test_unset_var_raises(self):
        # Make sure the var doesn't exist
        os.environ.pop("NONEXISTENT_VAR_XYZ", None)
        with pytest.raises(ConfigError, match="NONEXISTENT_VAR_XYZ"):
            _resolve_env_vars("$NONEXISTENT_VAR_XYZ")

    def test_no_vars_passthrough(self):
        assert _resolve_env_vars("plain string") == "plain string"


class TestBuildConfig:
    def test_minimal_github_config(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        raw = {
            "name": "test",
            "tracker": {"kind": "github", "repo": "owner/repo"},
        }
        config = build_config(raw, Path("/tmp/WORKFLOW.md"))
        assert config.name == "test"
        assert config.tracker.kind == "github"
        assert config.tracker.repo == "owner/repo"
        assert config.max_concurrent_agents == 10  # default

    def test_github_missing_repo_raises(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        raw = {
            "name": "test",
            "tracker": {"kind": "github"},
        }
        with pytest.raises(ConfigError, match="tracker.repo"):
            build_config(raw, Path("/tmp/WORKFLOW.md"))

    def test_defaults(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        raw = {
            "name": "defaults",
            "tracker": {"kind": "github", "repo": "o/r"},
        }
        config = build_config(raw, Path("/tmp/WORKFLOW.md"))
        assert config.poll_seconds == 30
        assert config.max_turns == 20
        assert config.turn_timeout_seconds == 3600
        assert config.stall_timeout_seconds == 300
        assert config.max_retries == 5
        assert config.agent_kind == "crewai"

    def test_overrides(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        raw = {
            "name": "custom",
            "tracker": {"kind": "github", "repo": "o/r"},
            "poll_seconds": 60,
            "max_concurrent_agents": 3,
            "max_turns": 5,
            "agent_model": "claude-3-opus",
        }
        config = build_config(raw, Path("/tmp/WORKFLOW.md"))
        assert config.poll_seconds == 60
        assert config.max_concurrent_agents == 3
        assert config.max_turns == 5
        assert config.agent_model == "claude-3-opus"

    def test_env_var_in_config(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        monkeypatch.setenv("MY_REPO", "myorg/myrepo")
        raw = {
            "name": "env-test",
            "tracker": {"kind": "github", "repo": "$MY_REPO"},
        }
        config = build_config(raw, Path("/tmp/WORKFLOW.md"))
        assert config.tracker.repo == "myorg/myrepo"

    def test_invalid_tracker_type(self, monkeypatch):
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
        raw = {
            "name": "bad",
            "tracker": "not-a-dict",
        }
        with pytest.raises(ConfigError, match="'tracker' must be a mapping"):
            build_config(raw, Path("/tmp/WORKFLOW.md"))
