#!/usr/bin/env bash
# Removes Caelus Terminal's own local workspace and launcher only.
set -euo pipefail

CAELUS_HOME="${CAELUS_HOME:-$HOME/.caelus}"
BIN_DIR="${CAELUS_BIN_DIR:-$HOME/.local/bin}"
LAUNCHER="$BIN_DIR/caelus"
TARGET="$CAELUS_HOME/venv/bin/caelus"
PID_FILE="$CAELUS_HOME/runtime/caelus-api.pid"

if [[ -f "$PID_FILE" ]]; then
  PID="$(tr -d '[:space:]' < "$PID_FILE")"
  if [[ "$PID" =~ ^[0-9]+$ ]] && kill -0 "$PID" 2>/dev/null; then
    kill "$PID" 2>/dev/null || true
  fi
fi

if [[ -L "$LAUNCHER" && "$(readlink "$LAUNCHER")" == "$TARGET" ]]; then
  rm -f "$LAUNCHER"
fi

rm -rf "$CAELUS_HOME"
echo "Caelus Terminal has been removed from this Mac."
