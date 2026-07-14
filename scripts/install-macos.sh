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
"$VENV/bin/python" -m pip install --force-reinstall --no-deps "$SOURCE_DIR" >/dev/null
ln -sfn "$VENV/bin/caelus" "$BIN_DIR/caelus"

# This creates only a dedicated HERMES_HOME and a loopback API key. It never
# clones ~/.hermes or starts provider authentication in the user's main profile.
"$BIN_DIR/caelus" runtime init

echo "Caelus Terminal installed: $BIN_DIR/caelus"
if ! command -v hermes >/dev/null 2>&1; then
  echo "Installing the open-source agent runtime…"
  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
  export PATH="$HOME/.local/bin:$PATH"
fi

if ! command -v hermes >/dev/null 2>&1; then
  echo "The runtime install completed but 'hermes' is not on PATH yet. Reopen Terminal, then configure Caelus with the command below." >&2
  exit 1
fi

if [[ "${CAELUS_SKIP_SETUP:-0}" == "1" ]]; then
  echo "Skipping isolated provider setup (CAELUS_SKIP_SETUP=1)."
  exit 0
fi

echo "Caelus has its own empty runtime. Configure a provider there; this does not reuse ~/.hermes:"
echo "  HERMES_HOME=\"$CAELUS_HOME/runtime\" hermes setup"
echo "Then start the local API: caelus runtime start"
