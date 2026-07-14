from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Callable


_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class TrajectoryError(RuntimeError):
    """Raised when the optional local Cua Driver integration cannot complete."""


def recording_path(recordings_dir: Path, name: str) -> Path:
    if not isinstance(name, str) or not _NAME.fullmatch(name):
        raise TrajectoryError("Recorded Replay name must use lowercase letters, numbers, and hyphens")
    return Path(recordings_dir) / name


class TrajectoryDriver:
    """Small, explicit adapter for Cua Driver's local trajectory recorder."""

    def __init__(self, command_runner: Callable = subprocess.run) -> None:
        self._command_runner = command_runner

    def _call(self, tool: str, arguments: dict) -> dict:
        if shutil.which("cua-driver") is None:
            raise TrajectoryError("Cua Driver is required for recorded Replay workflows. Install cua-driver first.")
        command = ["cua-driver", "call", tool, json.dumps(arguments, separators=(",", ":"))]
        result = self._command_runner(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            message = (result.stderr or result.stdout or "unknown Cua Driver error").strip()
            raise TrajectoryError(f"Cua Driver {tool} failed: {message}")
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise TrajectoryError(f"Cua Driver {tool} returned invalid JSON") from exc
        if not isinstance(response, dict):
            raise TrajectoryError(f"Cua Driver {tool} returned an invalid response")
        return response

    def start(self, output_dir: Path) -> Path:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._call("start_recording", {"output_dir": str(output_dir), "record_video": False})
        return output_dir

    def stop(self) -> dict:
        return self._call("stop_recording", {})

    def replay(self, output_dir: Path) -> dict:
        output_dir = Path(output_dir).resolve()
        if not output_dir.is_dir():
            raise TrajectoryError(f"Recorded Replay not found: {output_dir}")
        return self._call(
            "replay_trajectory",
            {"dir": str(output_dir), "stop_on_error": True, "delay_ms": 500},
        )
