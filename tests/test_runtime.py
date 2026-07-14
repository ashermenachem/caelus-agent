from pathlib import Path

from caelus_terminal.runtime import build_runtime_env


def test_runtime_adapter_uses_a_separate_caelus_test_home(tmp_path):
    env = build_runtime_env(tmp_path)

    assert env["HERMES_HOME"] == str(tmp_path / "runtime")
    assert Path(env["HERMES_HOME"]).name == "runtime"
    assert ".hermes" not in env["HERMES_HOME"]
