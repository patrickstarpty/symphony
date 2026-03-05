"""Dynamic workflow file watcher.

Watches the WORKFLOW.md file for changes and re-parses it.
On successful parse, updates the orchestrator's prompt template and config.
On error, keeps the last-known-good configuration.

Uses ``watchdog`` for cross-platform file system events.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Callable

from symphony.config import Config, ConfigError, build_config
from symphony.log import get_logger
from symphony.workflow import Workflow, WorkflowError, load_workflow

log = get_logger(__name__)


class WorkflowWatcher:
    """Watches a workflow file and reloads on change.

    Uses watchdog for file system events, with a debounce to
    avoid reloading multiple times on rapid saves.

    Usage::

        watcher = WorkflowWatcher(workflow_path, on_reload=callback)
        await watcher.start()
        # ... later ...
        await watcher.stop()
    """

    def __init__(
        self,
        workflow_path: Path,
        on_reload: Callable[[Workflow, Config], Any] | None = None,
        debounce_seconds: float = 1.0,
    ) -> None:
        self._path = workflow_path.resolve()
        self._on_reload = on_reload
        self._debounce = debounce_seconds
        self._observer: Any = None
        self._last_workflow: Workflow | None = None
        self._last_config: Config | None = None
        self._reload_count = 0
        self._error_count = 0
        self._last_error: str = ""
        self._debounce_task: asyncio.Task | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    @property
    def reload_count(self) -> int:
        """Number of successful reloads."""
        return self._reload_count

    @property
    def error_count(self) -> int:
        """Number of failed reload attempts."""
        return self._error_count

    @property
    def last_error(self) -> str:
        """Last reload error message, or empty string."""
        return self._last_error

    async def start(self) -> None:
        """Start watching the workflow file."""
        from watchdog.events import FileModifiedEvent, FileSystemEventHandler
        from watchdog.observers import Observer

        self._loop = asyncio.get_running_loop()
        watch_dir = str(self._path.parent)
        filename = self._path.name

        class _Handler(FileSystemEventHandler):
            def __init__(inner_self) -> None:
                super().__init__()
                inner_self.watcher = self

            def on_modified(inner_self, event: FileModifiedEvent) -> None:
                if event.is_directory:
                    return
                if Path(event.src_path).name == filename:
                    # Schedule reload in the asyncio event loop
                    if self._loop and self._loop.is_running():
                        self._loop.call_soon_threadsafe(self._schedule_reload)

        self._observer = Observer()
        self._observer.schedule(_Handler(), watch_dir, recursive=False)
        self._observer.daemon = True
        self._observer.start()

        log.info(
            "watcher_started",
            workflow=str(self._path),
            debounce=self._debounce,
        )

    def _schedule_reload(self) -> None:
        """Schedule a debounced reload (called from watchdog thread via call_soon_threadsafe)."""
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()
        self._debounce_task = asyncio.create_task(self._debounced_reload())

    async def _debounced_reload(self) -> None:
        """Wait for the debounce period, then reload."""
        await asyncio.sleep(self._debounce)
        await self._reload()

    async def _reload(self) -> None:
        """Attempt to reload the workflow file.

        On success:
        - Update last-known-good workflow and config
        - Call the on_reload callback
        - Log success

        On error:
        - Keep last-known-good config
        - Log error
        """
        log.info("watcher_reloading", workflow=str(self._path))

        try:
            workflow = load_workflow(self._path)
            config = build_config(workflow.config, workflow.path)
        except (WorkflowError, ConfigError) as exc:
            self._error_count += 1
            self._last_error = str(exc)
            log.error(
                "watcher_reload_failed",
                error=str(exc),
                keeping="last-known-good",
                error_count=self._error_count,
            )
            return

        self._last_workflow = workflow
        self._last_config = config
        self._reload_count += 1
        self._last_error = ""

        log.info(
            "watcher_reloaded",
            name=workflow.name,
            reload_count=self._reload_count,
        )

        if self._on_reload:
            try:
                result = self._on_reload(workflow, config)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:
                log.error("watcher_callback_error", error=str(exc))

    async def stop(self) -> None:
        """Stop watching the workflow file."""
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

        log.info("watcher_stopped")

    def status(self) -> dict[str, Any]:
        """Return watcher status for API responses."""
        return {
            "watching": str(self._path),
            "reload_count": self._reload_count,
            "error_count": self._error_count,
            "last_error": self._last_error,
        }
