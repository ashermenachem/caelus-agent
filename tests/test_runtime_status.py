from unittest.mock import patch

from caelus_terminal.runtime import bootstrap_runtime, runtime_is_running


def test_runtime_status_uses_only_the_isolated_runtime_pid_file(tmp_path):
    runtime_home = tmp_path / "caelus" / "runtime"
    bootstrap_runtime(runtime_home, token_factory=lambda: "test-key")
    (runtime_home / "caelus-api.pid").write_text("4321\n")

    with patch("caelus_terminal.runtime.os.kill") as kill:
        assert runtime_is_running(runtime_home) is True

    assert kill.call_args.args == (4321, 0)


def test_runtime_status_treats_a_dead_pid_as_not_running(tmp_path):
    runtime_home = tmp_path / "caelus" / "runtime"
    bootstrap_runtime(runtime_home, token_factory=lambda: "test-key")
    (runtime_home / "caelus-api.pid").write_text("4321\n")

    with patch("caelus_terminal.runtime.os.kill", side_effect=ProcessLookupError):
        assert runtime_is_running(runtime_home) is False
