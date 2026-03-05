"""FastAPI HTTP server for the Symphony dashboard.

Provides REST API endpoints:
- ``GET  /api/v1/state``      — Full orchestrator state + metrics
- ``GET  /api/v1/sessions``   — Running + recent sessions with metrics
- ``GET  /api/v1/sessions/{id}`` — Single session detail
- ``POST /api/v1/refresh``    — Force re-poll tracker + reload workflow
- ``GET  /api/v1/health``     — Health check

Also serves the React dashboard SPA from ``/`` when built.

Spec Section 13 — Observability.
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from symphony.log import get_logger

if TYPE_CHECKING:
    from symphony.metrics import MetricsCollector
    from symphony.orchestrator import Orchestrator

log = get_logger(__name__)


def create_app(
    orchestrator: "Orchestrator",
    metrics: "MetricsCollector",
    *,
    dashboard_dir: Path | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        orchestrator: The running Orchestrator instance.
        metrics: The MetricsCollector instance.
        dashboard_dir: Optional path to the built React dashboard directory.

    Returns:
        Configured FastAPI app.
    """
    app = FastAPI(
        title="Symphony Dashboard API",
        description="REST API for monitoring the Symphony coding-agent orchestrator",
        version="0.1.0",
    )

    # CORS — allow the React dev server (Vite default port 5173)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store references for endpoint handlers
    app.state.orchestrator = orchestrator
    app.state.metrics = metrics
    app.state.started_at = time.time()

    # ── API Routes ─────────────────────────────────────────────────────

    @app.get("/api/v1/health")
    async def health() -> dict[str, Any]:
        """Health check endpoint."""
        orch = app.state.orchestrator
        return {
            "status": "ok",
            "uptime_seconds": round(time.time() - app.state.started_at, 1),
            "orchestrator_running": orch._running,
            "running_sessions": orch.state.running_count,
        }

    @app.get("/api/v1/state")
    async def get_state() -> dict[str, Any]:
        """Full orchestrator state + metrics snapshot.

        This is the main endpoint the dashboard polls.
        """
        orch: Orchestrator = app.state.orchestrator
        met: MetricsCollector = app.state.metrics
        state = orch.state

        return {
            "config": {
                "name": orch._config.name,
                "poll_seconds": orch._config.poll_seconds,
                "max_concurrent_agents": orch._config.max_concurrent_agents,
                "max_turns": orch._config.max_turns,
                "max_retries": orch._config.max_retries,
                "agent_model": orch._config.agent_model,
                "tracker_kind": orch._config.tracker.kind,
            },
            "running": [
                _serialise_running(entry)
                for entry in state.running.values()
            ],
            "retry_queue": [
                _serialise_retry(entry)
                for entry in state.retry_queue.values()
            ],
            "completed_count": len(state.completed),
            "failed_count": len(state.failed),
            "completed_ids": sorted(state.completed),
            "failed_ids": sorted(state.failed),
            "metrics": met.snapshot(),
        }

    @app.get("/api/v1/sessions")
    async def get_sessions() -> dict[str, Any]:
        """Running and recent sessions with metrics."""
        met: MetricsCollector = app.state.metrics
        return met.snapshot()

    @app.get("/api/v1/sessions/{session_id}")
    async def get_session(session_id: str) -> dict[str, Any]:
        """Get detail for a specific session."""
        met: MetricsCollector = app.state.metrics
        session = met.get_session(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return session.to_dict()

    @app.post("/api/v1/refresh")
    async def refresh() -> dict[str, str]:
        """Force a re-poll of the tracker.

        Also triggers workflow file re-read if the watcher is active.
        """
        orch: Orchestrator = app.state.orchestrator
        log.info("api_refresh_triggered")
        # Schedule a tick in the orchestrator
        asyncio.create_task(orch._tick())
        return {"status": "refresh_scheduled"}

    # ── Dashboard SPA serving ──────────────────────────────────────────

    # Try to find the built dashboard
    if dashboard_dir is None:
        # Look in common locations relative to the package
        candidates = [
            Path(__file__).parent.parent.parent / "dashboard" / "dist",
            Path(__file__).parent / "dashboard",
        ]
        for candidate in candidates:
            if candidate.is_dir() and (candidate / "index.html").is_file():
                dashboard_dir = candidate
                break

    if dashboard_dir and dashboard_dir.is_dir():
        # Serve static assets
        assets_dir = dashboard_dir / "assets"
        if assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/")
        async def dashboard_index() -> FileResponse:
            return FileResponse(str(dashboard_dir / "index.html"))

        # Catch-all for SPA client-side routing
        @app.get("/{full_path:path}", response_model=None)
        async def dashboard_spa(full_path: str) -> FileResponse | JSONResponse:
            # Don't catch API routes
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not found")
            file = dashboard_dir / full_path  # type: ignore[operator]
            if file.is_file():
                return FileResponse(str(file))
            return FileResponse(str(dashboard_dir / "index.html"))

        log.info("dashboard_serving", directory=str(dashboard_dir))
    else:
        # No built dashboard — serve a minimal status page
        @app.get("/")
        async def dashboard_placeholder() -> HTMLResponse:
            return HTMLResponse(_PLACEHOLDER_HTML)

    return app


def _serialise_running(entry: Any) -> dict[str, Any]:
    """Serialise a RunningEntry to a dict."""
    now = time.time()
    return {
        "issue_id": entry.issue.id,
        "issue_identifier": entry.issue.identifier,
        "issue_title": entry.issue.title,
        "issue_state": entry.issue.state.value,
        "workspace_path": entry.workspace_path,
        "session_id": entry.session_id,
        "started_at": entry.started_at,
        "last_event_at": entry.last_event_at,
        "duration_seconds": round(now - entry.started_at, 1),
        "stall_seconds": round(now - entry.last_event_at, 1),
        "turns": entry.turns,
    }


def _serialise_retry(entry: Any) -> dict[str, Any]:
    """Serialise a RetryEntry to a dict."""
    now = time.time()
    return {
        "issue_id": entry.issue.id,
        "issue_identifier": entry.issue.identifier,
        "issue_title": entry.issue.title,
        "attempt": entry.attempt,
        "next_retry_at": entry.next_retry_at,
        "retry_in_seconds": round(max(0, entry.next_retry_at - now), 1),
        "last_error": entry.last_error,
    }


async def start_server(
    app: FastAPI,
    host: str = "0.0.0.0",
    port: int = 3000,
) -> None:
    """Start the uvicorn server as an asyncio task.

    This runs inside the existing event loop alongside the orchestrator.
    """
    import uvicorn

    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(config)
    log.info("dashboard_server_starting", host=host, port=port, url=f"http://localhost:{port}")
    await server.serve()


_PLACEHOLDER_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Symphony Dashboard</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f172a; color: #e2e8f0;
    display: flex; flex-direction: column; align-items: center;
    padding: 2rem; min-height: 100vh;
  }
  h1 { font-size: 1.8rem; margin-bottom: 0.5rem; color: #38bdf8; }
  .subtitle { color: #94a3b8; margin-bottom: 2rem; }
  .card {
    background: #1e293b; border-radius: 12px; padding: 1.5rem;
    width: 100%; max-width: 800px; margin-bottom: 1rem;
    border: 1px solid #334155;
  }
  .card h2 { font-size: 1rem; color: #94a3b8; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.05em; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
  .stat { text-align: center; }
  .stat .value { font-size: 2rem; font-weight: 700; color: #38bdf8; }
  .stat .label { font-size: 0.85rem; color: #94a3b8; }
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; padding: 0.5rem; color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; border-bottom: 1px solid #334155; }
  td { padding: 0.5rem; border-bottom: 1px solid #1e293b; font-size: 0.9rem; }
  .badge {
    display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
    font-size: 0.75rem; font-weight: 600;
  }
  .badge-running { background: #1d4ed8; color: #bfdbfe; }
  .badge-success { background: #15803d; color: #bbf7d0; }
  .badge-failed { background: #b91c1c; color: #fecaca; }
  .badge-retry { background: #a16207; color: #fef3c7; }
  .empty { color: #64748b; font-style: italic; padding: 1rem; text-align: center; }
  #error { color: #f87171; display: none; margin-bottom: 1rem; }
  .refresh-btn {
    background: #1e293b; border: 1px solid #475569; color: #e2e8f0;
    padding: 0.5rem 1rem; border-radius: 8px; cursor: pointer;
    font-size: 0.85rem; margin-bottom: 1.5rem;
  }
  .refresh-btn:hover { background: #334155; }
</style>
</head>
<body>
<h1>&#9835; Symphony</h1>
<p class="subtitle">Coding Agent Orchestrator</p>
<button class="refresh-btn" onclick="fetchState()">&#8634; Refresh</button>
<div id="error"></div>

<div class="card">
  <h2>Overview</h2>
  <div class="grid">
    <div class="stat"><div class="value" id="s-running">-</div><div class="label">Running</div></div>
    <div class="stat"><div class="value" id="s-completed">-</div><div class="label">Completed</div></div>
    <div class="stat"><div class="value" id="s-failed">-</div><div class="label">Failed</div></div>
    <div class="stat"><div class="value" id="s-retrying">-</div><div class="label">Retrying</div></div>
    <div class="stat"><div class="value" id="s-tokens">-</div><div class="label">Tokens</div></div>
    <div class="stat"><div class="value" id="s-uptime">-</div><div class="label">Uptime</div></div>
  </div>
</div>

<div class="card">
  <h2>Running Sessions</h2>
  <div id="running-table"><p class="empty">No active sessions</p></div>
</div>

<div class="card">
  <h2>Retry Queue</h2>
  <div id="retry-table"><p class="empty">No retries queued</p></div>
</div>

<div class="card">
  <h2>Recent Sessions</h2>
  <div id="recent-table"><p class="empty">No completed sessions yet</p></div>
</div>

<script>
const API = '/api/v1';
function fmt(s) { return s < 60 ? s + 's' : Math.floor(s/60) + 'm ' + Math.round(s%60) + 's'; }
function fmtK(n) { return n > 9999 ? (n/1000).toFixed(1) + 'k' : n.toString(); }

async function fetchState() {
  try {
    const r = await fetch(API + '/state');
    if (!r.ok) throw new Error(r.statusText);
    const d = await r.json();
    document.getElementById('error').style.display = 'none';
    render(d);
  } catch (e) {
    const el = document.getElementById('error');
    el.textContent = 'Failed to fetch state: ' + e.message;
    el.style.display = 'block';
  }
}

function render(d) {
  const m = d.metrics?.aggregate || {};
  document.getElementById('s-running').textContent = d.running?.length || 0;
  document.getElementById('s-completed').textContent = d.completed_count || 0;
  document.getElementById('s-failed').textContent = d.failed_count || 0;
  document.getElementById('s-retrying').textContent = d.retry_queue?.length || 0;
  document.getElementById('s-tokens').textContent = fmtK(m.total_tokens || 0);
  document.getElementById('s-uptime').textContent = fmt(d.metrics?.uptime_seconds || 0);

  // Running table
  const running = d.running || [];
  if (running.length === 0) {
    document.getElementById('running-table').innerHTML = '<p class="empty">No active sessions</p>';
  } else {
    let h = '<table><tr><th>Issue</th><th>Session</th><th>Duration</th><th>Turns</th><th>Status</th></tr>';
    for (const s of running) {
      h += '<tr><td>' + s.issue_identifier + ' ' + s.issue_title + '</td>';
      h += '<td>' + s.session_id + '</td>';
      h += '<td>' + fmt(s.duration_seconds) + '</td>';
      h += '<td>' + s.turns + '</td>';
      h += '<td><span class="badge badge-running">running</span></td></tr>';
    }
    h += '</table>';
    document.getElementById('running-table').innerHTML = h;
  }

  // Retry table
  const retries = d.retry_queue || [];
  if (retries.length === 0) {
    document.getElementById('retry-table').innerHTML = '<p class="empty">No retries queued</p>';
  } else {
    let h = '<table><tr><th>Issue</th><th>Attempt</th><th>Retry In</th><th>Last Error</th></tr>';
    for (const r of retries) {
      h += '<tr><td>' + r.issue_identifier + ' ' + r.issue_title + '</td>';
      h += '<td>#' + r.attempt + '</td>';
      h += '<td>' + fmt(r.retry_in_seconds) + '</td>';
      h += '<td>' + (r.last_error || '').substring(0, 80) + '</td></tr>';
    }
    h += '</table>';
    document.getElementById('retry-table').innerHTML = h;
  }

  // Recent sessions
  const recent = d.metrics?.recent_sessions || [];
  if (recent.length === 0) {
    document.getElementById('recent-table').innerHTML = '<p class="empty">No completed sessions yet</p>';
  } else {
    let h = '<table><tr><th>Issue</th><th>Status</th><th>Duration</th><th>Tokens</th><th>Turns</th></tr>';
    for (const s of recent) {
      const badge = s.status === 'success' ? 'badge-success' : 'badge-failed';
      h += '<tr><td>' + s.issue_identifier + ' ' + s.issue_title + '</td>';
      h += '<td><span class="badge ' + badge + '">' + s.status + '</span></td>';
      h += '<td>' + fmt(s.duration_seconds) + '</td>';
      h += '<td>' + fmtK(s.total_tokens) + '</td>';
      h += '<td>' + s.turns + '</td></tr>';
    }
    h += '</table>';
    document.getElementById('recent-table').innerHTML = h;
  }
}

fetchState();
setInterval(fetchState, 3000);
</script>
</body>
</html>
"""
