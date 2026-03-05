"""Tests for watcher.py — dynamic workflow file watcher."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from symphony.watcher import WorkflowWatcher


@pytest.fixture
def workflow_file(tmp_path: Path) -> Path:
    """Create a minimal workflow file for testing."""
    wf = tmp_path / "WORKFLOW.md"
    wf.write_text(
        """\
---
name: test
tracker:
  kind: file
  file: issues.json
---

# System Prompt

You are a helpful assistant.
""",
        encoding="utf-8",
    )
    return wf


class TestWorkflowWatcher:
    def test_initial_state(self, workflow_file: Path):
        watcher = WorkflowWatcher(workflow_file)
        assert watcher.reload_count == 0
        assert watcher.error_count == 0
        assert watcher.last_error == ""

    def test_status(self, workflow_file: Path):
        watcher = WorkflowWatcher(workflow_file)
        s = watcher.status()
        assert "watching" in s
        assert s["reload_count"] == 0
        assert s["error_count"] == 0
        assert s["last_error"] == ""

    @pytest.mark.asyncio
    async def test_start_stop(self, workflow_file: Path):
        watcher = WorkflowWatcher(workflow_file)
        await watcher.start()
        assert watcher._observer is not None
        await watcher.stop()
        assert watcher._observer is None

    @pytest.mark.asyncio
    async def test_reload_on_valid_change(self, workflow_file: Path):
        """Test that modifying the workflow triggers reload."""
        callback = MagicMock()
        watcher = WorkflowWatcher(
            workflow_file,
            on_reload=callback,
            debounce_seconds=0.1,
        )

        await watcher.start()
        try:
            # Trigger reload directly (avoids waiting for FS events)
            await watcher._reload()
            assert watcher.reload_count == 1
            assert watcher.error_count == 0
            assert callback.called
        finally:
            await watcher.stop()

    @pytest.mark.asyncio
    async def test_reload_keeps_good_on_error(self, workflow_file: Path):
        """Test that a bad config keeps the last-known-good."""
        callback = MagicMock()
        watcher = WorkflowWatcher(
            workflow_file,
            on_reload=callback,
            debounce_seconds=0.1,
        )

        await watcher.start()
        try:
            # First valid reload
            await watcher._reload()
            assert watcher.reload_count == 1

            # Now break the file
            workflow_file.write_text("---\n\n---\n\nbad content without valid yaml config", encoding="utf-8")

            # This reload should fail gracefully
            await watcher._reload()
            assert watcher.reload_count == 1  # still 1
            assert watcher.error_count == 1
            assert watcher.last_error != ""
        finally:
            await watcher.stop()

    @pytest.mark.asyncio
    async def test_debounce(self, workflow_file: Path):
        """Test that rapid changes are debounced."""
        watcher = WorkflowWatcher(workflow_file, debounce_seconds=0.2)
        await watcher.start()

        try:
            # Schedule multiple reloads in rapid succession
            watcher._schedule_reload()
            watcher._schedule_reload()
            watcher._schedule_reload()

            # Wait for debounce to complete
            await asyncio.sleep(0.4)
            # Should have only reloaded once due to debounce
            assert watcher.reload_count == 1
        finally:
            await watcher.stop()

    @pytest.mark.asyncio
    async def test_callback_error_handled(self, workflow_file: Path):
        """Test that callback errors don't crash the watcher."""

        def bad_callback(workflow, config):
            raise ValueError("callback broke")

        watcher = WorkflowWatcher(
            workflow_file,
            on_reload=bad_callback,
            debounce_seconds=0.1,
        )

        await watcher.start()
        try:
            # Should not raise, just log the error
            await watcher._reload()
            assert watcher.reload_count == 1  # reload itself succeeded
        finally:
            await watcher.stop()
