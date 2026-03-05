"""Tests for server.py — FastAPI HTTP server."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from symphony.metrics import MetricsCollector
from symphony.server import create_app


def _make_orchestrator_mock() -> MagicMock:
    """Create a mock Orchestrator with the attributes the server reads."""
    orch = MagicMock()
    orch._running = True

    # Config
    orch._config.name = "test-project"
    orch._config.poll_seconds = 30
    orch._config.max_concurrent_agents = 5
    orch._config.max_turns = 20
    orch._config.max_retries = 3
    orch._config.agent_model = "deepseek/deepseek-chat"
    orch._config.tracker.kind = "file"

    # State
    state = MagicMock()
    state.running = {}
    state.retry_queue = {}
    state.completed = set()
    state.failed = set()
    state.running_count = 0
    orch.state = state

    return orch


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the server."""
    orch = _make_orchestrator_mock()
    metrics = MetricsCollector()
    app = create_app(orch, metrics)
    return TestClient(app)


@pytest.fixture
def client_with_sessions() -> TestClient:
    """Create a test client with some sessions registered."""
    orch = _make_orchestrator_mock()
    metrics = MetricsCollector()
    metrics.start_session("s1", "i1", issue_identifier="#1", issue_title="Bug fix")
    metrics.start_session("s2", "i2", issue_identifier="#2", issue_title="Feature")
    metrics.finish_session("s1", success=True, turns=3, prompt_tokens=100, completion_tokens=50)
    app = create_app(orch, metrics)
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_ok(self, client: TestClient):
        r = client.get("/api/v1/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "uptime_seconds" in data
        assert data["orchestrator_running"] is True

    def test_health_has_session_count(self, client: TestClient):
        r = client.get("/api/v1/health")
        data = r.json()
        assert "running_sessions" in data


class TestStateEndpoint:
    def test_state_returns_config(self, client: TestClient):
        r = client.get("/api/v1/state")
        assert r.status_code == 200
        data = r.json()
        assert data["config"]["name"] == "test-project"
        assert data["config"]["agent_model"] == "deepseek/deepseek-chat"
        assert data["config"]["tracker_kind"] == "file"

    def test_state_returns_running(self, client: TestClient):
        r = client.get("/api/v1/state")
        data = r.json()
        assert "running" in data
        assert isinstance(data["running"], list)

    def test_state_returns_retry_queue(self, client: TestClient):
        r = client.get("/api/v1/state")
        data = r.json()
        assert "retry_queue" in data
        assert isinstance(data["retry_queue"], list)

    def test_state_returns_metrics(self, client: TestClient):
        r = client.get("/api/v1/state")
        data = r.json()
        assert "metrics" in data
        assert "aggregate" in data["metrics"]
        assert "uptime_seconds" in data["metrics"]

    def test_state_returns_counts(self, client: TestClient):
        r = client.get("/api/v1/state")
        data = r.json()
        assert data["completed_count"] == 0
        assert data["failed_count"] == 0

    def test_state_with_sessions(self, client_with_sessions: TestClient):
        r = client_with_sessions.get("/api/v1/state")
        data = r.json()
        metrics = data["metrics"]
        assert metrics["aggregate"]["total_sessions"] == 2
        assert metrics["aggregate"]["successful_sessions"] == 1
        assert metrics["aggregate"]["running_sessions"] == 1


class TestSessionsEndpoint:
    def test_sessions_empty(self, client: TestClient):
        r = client.get("/api/v1/sessions")
        assert r.status_code == 200
        data = r.json()
        assert data["running_sessions"] == []
        assert data["recent_sessions"] == []

    def test_sessions_with_data(self, client_with_sessions: TestClient):
        r = client_with_sessions.get("/api/v1/sessions")
        data = r.json()
        assert len(data["running_sessions"]) == 1
        assert len(data["recent_sessions"]) == 1
        assert data["recent_sessions"][0]["session_id"] == "s1"
        assert data["running_sessions"][0]["session_id"] == "s2"


class TestSessionDetailEndpoint:
    def test_session_found(self, client_with_sessions: TestClient):
        r = client_with_sessions.get("/api/v1/sessions/s1")
        assert r.status_code == 200
        data = r.json()
        assert data["session_id"] == "s1"
        assert data["status"] == "success"

    def test_session_not_found(self, client: TestClient):
        r = client.get("/api/v1/sessions/nonexistent")
        assert r.status_code == 404


class TestRefreshEndpoint:
    def test_refresh_returns_status(self, client: TestClient):
        # Patch asyncio.create_task to avoid coroutine error with mock
        with patch("symphony.server.asyncio.create_task"):
            r = client.post("/api/v1/refresh")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "refresh_scheduled"


class TestDashboardServing:
    def test_placeholder_html_served(self, client: TestClient):
        r = client.get("/")
        assert r.status_code == 200
        assert "Symphony" in r.text
