# Troubleshooting & Gotchas

Common pitfalls when working with the Symphony ↔ Copilot CLI bridge.

---

## 1. Silent Message Drops — Missing `"jsonrpc": "2.0"`

**Symptom:** The bridge process starts (gets a PID) but produces zero output.
`await_response` always times out with `:response_timeout`. No error, no
exit, no stderr — just silence.

**Cause:** The bridge validates every incoming line at the top of
`handleSymphonyLine` (bin/copilot_cli_app_server, line 90):

```javascript
if (!message || message.jsonrpc !== '2.0' || typeof message.method !== 'string') {
  return;   // silently dropped
}
```

If `"jsonrpc"` is missing or not exactly `"2.0"`, the message is discarded
without any error response. This is per the JSON-RPC 2.0 spec — but the
failure mode is completely silent.

**Fix:** `send_message/2` in `app_server.ex` injects the field automatically:

```elixir
defp send_message(port, message) do
  line = Jason.encode!(Map.put_new(message, "jsonrpc", "2.0")) <> "\n"
  Port.command(port, line)
end
```

**Prevention:** Never hand-build JSON-RPC payloads without `"jsonrpc": "2.0"`.
If adding a new message type, use `send_message/2` which guarantees it.

---

## 2. Relative Command Path Resolution

**Symptom:** `No such file or directory` in logs when the bridge command
starts with `./` or `../` (e.g., `./bin/copilot_cli_app_server`).

**Cause:** Erlang's `Port.open` `cd:` option sets the working directory to
the *issue workspace* (e.g., `~/code/symphony-workspaces/PTY-7/`), not the
repository root. A relative path like `./bin/copilot_cli_app_server` is
resolved against the workspace, where the file doesn't exist.

**Fix:** `resolve_local_command/2` expands `./` and `../` prefixed commands
against the directory containing `WORKFLOW.md` (the repo/elixir root):

```elixir
Path.expand(executable, Path.dirname(Path.expand(Workflow.workflow_file_path())))
```

**Prevention:** When writing `copilot_cli.command` in WORKFLOW.md, remember
that `.` means "relative to WORKFLOW.md", not "relative to the issue
workspace".

---

## 3. Login Shell Mangles PATH — `bash -lc` vs `bash -c`

**Symptom:** Bridge can't find `node` or `copilot` even though they're in
PATH when tested interactively.

**Cause:** Using `bash -lc` (login shell) re-sources `.bash_profile` /
`.zprofile` which can reset or reorder PATH, hiding binaries that were
available in the parent Erlang VM's environment.

**Fix:** Use `bash -c` (non-login) to inherit the VM's PATH as-is.

**Prevention:** Never use `-l` flag in `Port.open` args unless you
specifically need login shell initialization.

---

## 4. Read Timeout Too Aggressive

**Symptom:** `:response_timeout` on `thread/start` despite the bridge being
healthy. Works on retry or with faster networks.

**Cause:** The `initialize` → Copilot ACP handshake takes ~2s, and
`thread/start` (which maps to `session/new` on the ACP side) takes ~6s.
A `read_timeout_ms` under 10s will hit spurious timeouts.

**Measured latencies** (typical, may vary):

| Message        | ACP Mapping      | Latency   |
|----------------|------------------|-----------|
| `initialize`   | ACP `initialize` | ~1.9s     |
| `thread/start` | `session/new`    | ~5.7s     |
| `turn/start`   | `session/prompt` | ~10s+     |

**Fix:** Default `read_timeout_ms` is set to `15_000` (15s). Don't lower it
below 10s for production use. `turn_timeout_ms` should remain much higher
(minutes) since turns involve actual AI work.

---

## 5. Bridge Stdin Closes → Immediate Shutdown

**Symptom:** Bridge process exits immediately (exit code 0 or 1) right
after spawn.

**Cause:** The bridge registers `process.stdin.on('end', shutdown)`. If the
pipe from Erlang's Port closes (e.g., port is GC'd, process crashes, or
there's a pipe setup race), the bridge shuts down instantly.

**Diagnosis:** Check whether the Erlang process holding the Port is still
alive. Verify with:

```elixir
Port.info(port)  # returns nil if port is dead
```

---

## 6. Copilot ACP Hangs During Initialization

**Symptom:** Bridge starts, receives the `initialize` message, spawns
`copilot --acp`, but never responds. No timeout, no error — just hangs.

**Cause:** The bridge's `ensureCopilotInitialized()` awaits
`requestCopilot('initialize', ...)` with no timeout. If Copilot ACP
itself hangs (auth issues, rate limits, network problems), the bridge
blocks indefinitely.

**Diagnosis:**

```bash
# Test Copilot ACP directly:
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":1,"clientCapabilities":{},"clientInfo":{"name":"test","version":"0.1.0"}}}' \
  | copilot --acp --allow-all 2>/dev/null | head -1
```

If this hangs, the issue is Copilot auth/backend — not the bridge.

**Prevention:** Ensure `copilot login` has been run and the token is valid.
Check `copilot --version` works without hanging.

---

## 7. Stale Compiled Code After Source Edits

**Symptom:** Logs still show old behavior (wrong labels, old paths) even
after editing `.ex` source files.

**Cause:** The BEAM VM runs compiled `.beam` bytecode. Editing source files
doesn't take effect until recompilation.

**Fix:**

```bash
cd elixir && mix compile   # recompile changed modules
# or, for a full server restart:
make -C elixir server
```

**Prevention:** Always recompile after editing Elixir source. If running
`iex -S mix`, use `recompile()` in the shell.

---

## 8. Port Line Buffer Overflow

**Symptom:** Messages from the bridge appear truncated or never arrive.
Possible `:malformed` parse errors in logs.

**Cause:** `Port.open` uses `line: @port_line_bytes` (10 MB). If a single
JSON line from the bridge exceeds this, Erlang splits it across multiple
`{:eol, ...}` / `{:noeol, ...}` messages. The current parser expects
complete lines.

**Prevention:** This is unlikely in normal operation but could happen with
extremely large agent responses. If you see `:noeol` tuples in port
messages, the line buffer is too small.

---

## Quick Diagnostic Checklist

When agents fail with no obvious error:

1. **Check logs** — `elixir/log/symphony.log*`
2. **Verify bridge path** — does the resolved command path exist?
   ```elixir
   File.exists?(resolved_path)  # must be true
   ```
3. **Verify Copilot CLI** — can it respond at all?
   ```bash
   copilot --version
   echo '...' | copilot --acp --allow-all 2>/dev/null | head -1
   ```
4. **Check JSON-RPC compliance** — every message to the bridge must have
   `"jsonrpc": "2.0"` and a string `"method"` field
5. **Check timeouts** — `read_timeout_ms` ≥ 15000 for production
6. **Recompile** — `mix compile` after any source change
