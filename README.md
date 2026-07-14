# Caelus Terminal

A macOS-first terminal chat UI powered by the Hermes Agent runtime.

## Current prototype

The first build is isolated from the active Hermes installation. It renders the matrix-style terminal dashboard and includes a small client for Hermes's documented local API server.

```bash
cd /Users/ashermenachem/Developer/caelus-terminal
./.venv/bin/python -m caelus_terminal --demo
```

Expand collapsed tool activity:

```bash
./.venv/bin/python -m caelus_terminal --demo --expanded-tools
```

## macOS installer

From a checked-out Caelus Terminal release:

```bash
bash scripts/install-macos.sh
```

The installer creates `~/.caelus/venv`, installs the `caelus` command in `~/.local/bin`, installs Hermes automatically if it is missing, and launches native `hermes setup`. It does not copy another user’s memory, sessions, secrets, or workflows.

## Runtime connection

Caelus connects only to the explicitly supplied local Hermes API endpoint and key. It does not silently read the operator's active `~/.hermes` profile. Start an interactive terminal chat with:

```bash
./.venv/bin/python -m caelus_terminal \
  --endpoint http://127.0.0.1:8642/v1 \
  --api-key YOUR_LOCAL_KEY \
  --agent nova \
  --interactive
```

At connection time, Caelus reads Hermes's documented capabilities, skills, and enabled toolsets and renders them in the terminal dashboard. A toolset whose name starts with `mcp-` is displayed as an observable MCP integration; Hermes currently exposes no separate API endpoint for MCP server configuration/status.

For a one-shot request instead:

```bash
./.venv/bin/python -m caelus_terminal \
  --endpoint http://127.0.0.1:8642/v1 \
  --api-key YOUR_LOCAL_KEY \
  --agent nova \
  --chat "Hello"
```

Interactive mode creates a persisted Hermes session, streams structured tool activity and final responses through the dashboard, and sends `POST /v1/runs/{run_id}/stop` when you press `Ctrl-C` during an active run. Resume a persisted session (including its transcript) with `--session-id`:

```bash
./.venv/bin/python -m caelus_terminal \
  --endpoint http://127.0.0.1:8642/v1 \
  --api-key YOUR_LOCAL_KEY \
  --session-id SESSION_ID \
  --interactive
```

Within interactive mode, `/help` shows Caelus controls and `/quit` exits. Caelus does not rename or impersonate Hermes commands.

## Privacy and attribution

- No personal Caelus memory, credentials, sessions, or workflows are included.
- Runtime testing uses an isolated `HERMES_HOME`, never the active `~/.hermes` directory.
- Caelus Terminal is powered by Hermes Agent; full licensing notices will be included before distribution.
