# Caelus Terminal

A macOS-first terminal chat UI powered by the Hermes Agent runtime.

## Release status

Caelus Terminal is a macOS-first terminal UI and local launcher powered by the separately installed Hermes Agent runtime. Its installer and runtime use a dedicated `~/.caelus/runtime` by default; they do not silently reuse an operator's active `~/.hermes` profile.

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

The installer creates `~/.caelus/venv`, installs the `caelus` command in `~/.local/bin`, initializes only `~/.caelus/runtime`, and installs Hermes if it is missing. It does not copy another user’s memory, sessions, secrets, or workflows. Provider setup remains an explicit, separate step:

```bash
HERMES_HOME="$HOME/.caelus/runtime" hermes setup
caelus runtime start
```

For automated or isolated installation tests, `CAELUS_HOME`, `CAELUS_BIN_DIR`, `PYTHON`, and `CAELUS_SKIP_SETUP=1` are supported. `CAELUS_SKIP_SETUP` does not configure a model provider.

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

## Safe agent templates

Caelus templates are portable behavior bundles, **not profile exports**. They may contain only a validated `agent.json` with generic name, description, instructions, and optional toolsets, plus UTF-8 Markdown files below `skills/`. The exporter rejects everything else — including `.env`, credentials, sessions, memory, logs, contacts, browser data, symlinks, and unsupported machine-specific files — and scans allowed text for credential-like content.

Each `.caelus-template` archive has a versioned manifest and SHA-256 checksum for every allowed file. Imports validate the archive before writing it, reject traversal paths/symlinks/checksum mismatches, and will not overwrite an existing destination.

```bash
# The source must contain agent.json and may contain skills/*.md.
caelus template export --source ./generic-research-agent --output ./research.caelus-template
caelus template import --input ./research.caelus-template --destination ./my-research-agent
```

A template recipient must configure their own Hermes provider credentials, runtime, memory, and integrations.

## Local access gate

Caelus can require a hidden password prompt before every normal command. Configure it locally — the password is never accepted as a command-line argument or saved in plaintext:

```bash
caelus gate set
caelus gate status
```

The gate stores only a salted password verifier in `~/.caelus/access-gate.json` with private filesystem permissions. Each command invocation allows **three attempts**; after three failures, that invocation exits without running the requested Caelus command. Changing an existing gate requires the current password first.

This is a **local deterrent, not real invite-only authentication**. Anyone who can modify the installed source/package, replace the gate file, or access the same macOS account can bypass it. A genuinely invite-only product requires server-side authentication and per-user accounts; Caelus does not claim otherwise.

## Packaging and release verification

Caelus Terminal is MIT-licensed; see [LICENSE](LICENSE). [NOTICE](NOTICE) identifies Hermes Agent as the separately installed MIT-licensed runtime dependency and preserves its attribution.

Before distributing a checkout or the wheel, run the release gate:

```bash
PYTHON="$PWD/.venv/bin/python" bash scripts/release-check.sh
```

It runs the full test suite, builds `dist/caelus_terminal-*.whl`, verifies the wheel includes the required Caelus modules and legal notices, installs that wheel into a fresh virtual environment, and executes the macOS installer under isolated temporary home/bin/runtime paths.

GitHub Actions runs the same release check on pull requests and updates to `main`, then retains the verified wheel as a workflow artifact. See [CHANGELOG.md](CHANGELOG.md) for versioned release notes.

## Privacy and attribution

- No personal Caelus memory, credentials, sessions, or workflows are included.
- Runtime testing uses an isolated `HERMES_HOME`, never the active `~/.hermes` directory.
- Caelus Terminal is powered by Hermes Agent; runtime attribution and licensing are in [NOTICE](NOTICE).
