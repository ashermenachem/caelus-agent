#!/usr/bin/env bash
# Installs Caelus Terminal without modifying an existing Hermes profile.
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Caelus Terminal v0.1 supports macOS only." >&2
  exit 1
fi

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CAELUS_HOME="${CAELUS_HOME:-$HOME/.caelus}"
VENV="$CAELUS_HOME/venv"
BIN_DIR="$HOME/.local/bin"

command -v python3 >/dev/null || { echo "Python 3 is required." >&2; exit 1; }
mkdir -p "$CAELUS_HOME" "$BIN_DIR"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip >/dev/null
"$VENV/bin/python" -m pip install "$SOURCE_DIR" >/dev/null
ln -sfn "$VENV/bin/caelus" "$BIN_DIR/caelus"

echo "Caelus Terminal installed: $BIN_DIR/caelus"
if ! command -v hermes >/dev/null 2>&1; then
  echo "Installing the open-source agent runtime…"
  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v hermes >/dev/null 2>&1; then
  echo "The runtime install completed but 'hermes' is not on PATH yet. Reopen Terminal, then run: hermes setup" >&2
  exit 1
fi

if [[ "${CAELUS_SKIP_SETUP:-0}" == "1" ]]; then
  echo "Skipping native setup (CAELUS_SKIP_SETUP=1)."
  exit 0
fi

echo "Starting native agent setup…"
hermes setup

echo "Setup complete. Start Caelus Terminal with: caelus --help"
