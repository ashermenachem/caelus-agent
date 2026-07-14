from unittest.mock import Mock, patch

from caelus_terminal.runtime import bootstrap_runtime, start_runtime, stop_runtime


def test_start_runtime_spawns_gateway_with_isolated_environment_and_records_pid(tmp_path):
    runtime_home = tmp_path / "caelus" / "runtime"
    bootstrap_runtime(runtime_home, token_factory=lambda: "test-key")
    process = Mock(pid=4321)

    with patch("caelus_terminal.runtime.subprocess.Popen", return_value=process) as popen:
        assert start_runtime(runtime_home, hermes_executable="/usr/local/bin/hermes") == 4321

    command = popen.call_args.args[0]
    assert command == ["/usr/local/bin/hermes", "gateway", "run", "--force"]
    assert popen.call_args.kwargs["env"]["HERMES_HOME"] == str(runtime_home)
    assert (runtime_home / "caelus-api.pid").read_text() == "4321\n"
    assert (runtime_home / "logs" / "api-server.log").exists()


def test_start_runtime_replaces_a_stale_pid_file(tmp_path):
    runtime_home = tmp_path / "caelus" / "runtime"
    bootstrap_runtime(runtime_home, token_factory=lambda: "test-key")
    (runtime_home / "caelus-api.pid").write_text("9999\n")
    process = Mock(pid=4321)

    with patch("caelus_terminal.runtime.os.kill", side_effect=ProcessLookupError), patch(
        "caelus_terminal.runtime.subprocess.Popen", return_value=process
    ):
        assert start_runtime(runtime_home, hermes_executable="/usr/local/bin/hermes") == 4321

    assert (runtime_home / "caelus-api.pid").read_text() == "4321\n"


def test_stop_runtime_terminates_recorded_process_and_removes_pid_file(tmp_path):
    runtime_home = tmp_path / "caelus" / "runtime"
    bootstrap_runtime(runtime_home, token_factory=lambda: "test-key")
    (runtime_home / "caelus-api.pid").write_text("4321\n")

    with patch("caelus_terminal.runtime.os.kill") as kill:
        assert stop_runtime(runtime_home) is True

    assert kill.call_args.args[0] == 4321
    assert not (runtime_home / "caelus-api.pid").exists()
