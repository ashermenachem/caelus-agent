from __future__ import annotations

import os
from pathlib import Path


def build_runtime_env(caelus_test_home: Path) -> dict[str, str]:
    """Return an isolated runtime environment without changing the active Hermes home."""
    env = os.environ.copy()
    env["HERMES_HOME"] = str(caelus_test_home / "runtime")
    return env
