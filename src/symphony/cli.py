"""CLI entry point for Symphony.

Usage::

    python -m symphony ./WORKFLOW.md
    symphony ./WORKFLOW.md --port 3000
    symphony ./WORKFLOW.md --log-level debug --json-logs
"""

from __future__ import annotations

import argparse
import asyncio
import signal
import sys
from pathlib import Path

from symphony.config import ConfigError, build_config
from symphony.log import get_logger, setup_logging
from symphony.metrics import MetricsCollector
from symphony.orchestrator import Orchestrator
from symphony.tracker.file import FileTracker
from symphony.tracker.github import GitHubTracker
from symphony.workflow import Workflow, WorkflowError, load_workflow


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="symphony",
        description="Symphony — autonomous coding-agent orchestrator",
    )
    parser.add_argument(
        "workflow",
        type=str,
        help="Path to the WORKFLOW.md file",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port for the dashboard web server (default: 3000 if enabled)",
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        default=False,
        help="Disable the dashboard web server",
    )
    parser.add_argument(
        "--no-watch",
        action="store_true",
        default=False,
        help="Disable workflow file watching (no hot-reload)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "debug", "info", "warning", "error"],
        help="Log level (default: INFO)",
    )
    parser.add_argument(
        "--json-logs",
        action="store_true",
        default=False,
        help="Output logs as JSON lines",
    )
    return parser


def _create_tracker(config):
    """Create the appropriate tracker client based on config."""
    kind = config.tracker.kind
    if kind == "github":
        return GitHubTracker(config.tracker)
    elif kind == "file":
        return FileTracker(config.tracker)
    else:
        raise ConfigError(f"Unknown tracker kind: {kind}. Supported: github, file")


async def _run(args: argparse.Namespace) -> int:
    """Main async entry point."""
    log = get_logger("symphony.cli")

    # Load workflow
    try:
        workflow = load_workflow(args.workflow)
    except WorkflowError as exc:
        log.error("workflow_error", error=str(exc))
        return 1

    # Build config
    try:
        config = build_config(
            workflow.config,
            workflow.path,
        )
        if args.port:
            config = build_config(
                {**workflow.config, "port": args.port},
                workflow.path,
            )
    except ConfigError as exc:
        log.error("config_error", error=str(exc))
        return 1

    # Create tracker
    try:
        tracker = _create_tracker(config)
    except (ConfigError, Exception) as exc:
        log.error("tracker_error", error=str(exc))
        return 1

    # Create metrics collector
    metrics = MetricsCollector()

    # Create orchestrator
    orchestrator = Orchestrator(
        config=config,
        tracker=tracker,
        prompt_template=workflow.prompt_template,
        metrics=metrics,
    )

    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()

    def _signal_handler(sig: signal.Signals) -> None:
        log.info("signal_received", signal=sig.name)
        asyncio.create_task(orchestrator.shutdown())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler, sig)

    # ── Start workflow file watcher ──────────────────────────────
    watcher = None
    if not args.no_watch:
        from symphony.watcher import WorkflowWatcher

        def _on_workflow_reload(new_workflow: Workflow, new_config) -> None:
            orchestrator.update_prompt_template(new_workflow.prompt_template)
            log.info(
                "workflow_hot_reloaded",
                name=new_workflow.name,
            )

        watcher = WorkflowWatcher(
            workflow_path=workflow.path,
            on_reload=_on_workflow_reload,
        )
        await watcher.start()

    # ── Start dashboard server ───────────────────────────────────
    server_task = None
    if not args.no_dashboard:
        port = args.port or config.port or 3000
        try:
            from symphony.server import create_app, start_server
            app = create_app(orchestrator, metrics)

            # Add watcher status to state endpoint
            if watcher:
                @app.get("/api/v1/watcher")
                async def watcher_status():
                    return watcher.status()

            server_task = asyncio.create_task(
                start_server(app, port=port),
                name="dashboard-server",
            )
        except ImportError as exc:
            log.warning(
                "dashboard_disabled",
                error=str(exc),
                hint="Install with: uv add fastapi 'uvicorn[standard]'",
            )

    # Start the orchestrator
    log.info(
        "symphony_starting",
        workflow=str(workflow.path),
        name=workflow.name,
        tracker=config.tracker.kind,
        repo=config.tracker.repo,
        dashboard="enabled" if server_task else "disabled",
        watcher="enabled" if watcher else "disabled",
    )

    try:
        await orchestrator.start()
    finally:
        # Clean up watcher
        if watcher:
            await watcher.stop()
        # Cancel server
        if server_task and not server_task.done():
            server_task.cancel()
            try:
                await server_task
            except asyncio.CancelledError:
                pass

    return 0


def _load_dotenv() -> None:
    """Load .env file if present (searches cwd and parents)."""
    from pathlib import Path
    env_file = Path.cwd() / ".env"
    if not env_file.is_file():
        return
    import os
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:  # don't override existing vars
                os.environ[key] = value


def main() -> None:
    """CLI entry point."""
    _load_dotenv()

    parser = _build_parser()
    args = parser.parse_args()

    # Set up logging before anything else
    setup_logging(level=args.log_level, json_output=args.json_logs)

    try:
        exit_code = asyncio.run(_run(args))
    except KeyboardInterrupt:
        exit_code = 130

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
