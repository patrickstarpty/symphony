"""Tests for metrics.py — token accounting and session metrics."""

from __future__ import annotations

import time

import pytest

from symphony.metrics import AggregateMetrics, MetricsCollector, SessionMetrics


class TestSessionMetrics:
    def test_initial_state(self):
        s = SessionMetrics(session_id="s1", issue_id="i1")
        assert s.status == "running"
        assert s.success is None
        assert s.total_tokens == 0
        assert s.duration_seconds >= 0

    def test_finish_success(self):
        s = SessionMetrics(session_id="s1", issue_id="i1")
        s.finish(success=True)
        assert s.status == "success"
        assert s.success is True
        assert s.finished_at is not None

    def test_finish_failure(self):
        s = SessionMetrics(session_id="s1", issue_id="i1")
        s.finish(success=False, error="timeout")
        assert s.status == "failed"
        assert s.success is False
        assert s.error == "timeout"

    def test_record_tokens(self):
        s = SessionMetrics(session_id="s1", issue_id="i1")
        s.record_tokens(prompt_tokens=100, completion_tokens=50)
        assert s.prompt_tokens == 100
        assert s.completion_tokens == 50
        assert s.total_tokens == 150

    def test_record_tokens_accumulates(self):
        s = SessionMetrics(session_id="s1", issue_id="i1")
        s.record_tokens(prompt_tokens=100, completion_tokens=50)
        s.record_tokens(prompt_tokens=200, completion_tokens=100)
        assert s.prompt_tokens == 300
        assert s.completion_tokens == 150
        assert s.total_tokens == 450

    def test_duration_while_running(self):
        s = SessionMetrics(session_id="s1", issue_id="i1", started_at=time.time() - 10)
        dur = s.duration_seconds
        assert dur >= 9.9  # allow small float variance

    def test_duration_when_finished(self):
        now = time.time()
        s = SessionMetrics(session_id="s1", issue_id="i1", started_at=now - 5)
        s.finished_at = now
        assert abs(s.duration_seconds - 5.0) < 0.1

    def test_to_dict(self):
        s = SessionMetrics(
            session_id="s1",
            issue_id="i1",
            issue_identifier="#42",
            issue_title="Fix bug",
        )
        s.record_tokens(prompt_tokens=500, completion_tokens=200)
        s.turns = 3
        d = s.to_dict()
        assert d["session_id"] == "s1"
        assert d["issue_id"] == "i1"
        assert d["issue_identifier"] == "#42"
        assert d["issue_title"] == "Fix bug"
        assert d["prompt_tokens"] == 500
        assert d["completion_tokens"] == 200
        assert d["total_tokens"] == 700
        assert d["turns"] == 3
        assert d["status"] == "running"


class TestAggregateMetrics:
    def test_initial_values(self):
        a = AggregateMetrics()
        assert a.total_sessions == 0
        assert a.total_tokens == 0

    def test_to_dict(self):
        a = AggregateMetrics(total_sessions=5, total_tokens=1000)
        d = a.to_dict()
        assert d["total_sessions"] == 5
        assert d["total_tokens"] == 1000


class TestMetricsCollector:
    def test_start_session(self):
        mc = MetricsCollector()
        s = mc.start_session("s1", "i1", issue_identifier="#1", issue_title="Bug")
        assert s.session_id == "s1"
        assert s.issue_id == "i1"
        assert mc._aggregate.total_sessions == 1
        assert mc._aggregate.running_sessions == 1

    def test_finish_session_success(self):
        mc = MetricsCollector()
        mc.start_session("s1", "i1")
        mc.finish_session("s1", success=True, turns=5, prompt_tokens=100, completion_tokens=50)
        assert mc._aggregate.running_sessions == 0
        assert mc._aggregate.successful_sessions == 1
        assert mc._aggregate.total_tokens == 150

    def test_finish_session_failure(self):
        mc = MetricsCollector()
        mc.start_session("s1", "i1")
        mc.finish_session("s1", success=False, error="crash")
        assert mc._aggregate.running_sessions == 0
        assert mc._aggregate.failed_sessions == 1

    def test_finish_unknown_session(self):
        mc = MetricsCollector()
        result = mc.finish_session("nonexistent", success=True)
        assert result is None

    def test_record_rate_limit(self):
        mc = MetricsCollector()
        mc.record_rate_limit()
        mc.record_rate_limit()
        assert mc._aggregate.rate_limit_events == 2

    def test_snapshot(self):
        mc = MetricsCollector()
        mc.start_session("s1", "i1", issue_identifier="#1")
        mc.start_session("s2", "i2", issue_identifier="#2")
        mc.finish_session("s1", success=True, turns=3, prompt_tokens=100, completion_tokens=50)

        snap = mc.snapshot()
        assert snap["uptime_seconds"] >= 0
        assert snap["aggregate"]["total_sessions"] == 2
        assert snap["aggregate"]["successful_sessions"] == 1
        assert snap["aggregate"]["running_sessions"] == 1
        assert len(snap["running_sessions"]) == 1
        assert snap["running_sessions"][0]["session_id"] == "s2"
        assert len(snap["recent_sessions"]) == 1
        assert snap["recent_sessions"][0]["session_id"] == "s1"

    def test_get_session(self):
        mc = MetricsCollector()
        mc.start_session("s1", "i1")
        assert mc.get_session("s1") is not None
        assert mc.get_session("unknown") is None

    def test_multiple_sessions_aggregate(self):
        mc = MetricsCollector()
        mc.start_session("s1", "i1")
        mc.start_session("s2", "i2")
        mc.start_session("s3", "i3")
        mc.finish_session("s1", success=True, prompt_tokens=100, completion_tokens=50)
        mc.finish_session("s2", success=False, error="err", prompt_tokens=200, completion_tokens=100)

        assert mc._aggregate.total_sessions == 3
        assert mc._aggregate.running_sessions == 1
        assert mc._aggregate.successful_sessions == 1
        assert mc._aggregate.failed_sessions == 1
        assert mc._aggregate.total_prompt_tokens == 300
        assert mc._aggregate.total_completion_tokens == 150
        assert mc._aggregate.total_tokens == 450
