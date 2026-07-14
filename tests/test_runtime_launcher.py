from pathlib import Path

from caelus_terminal.runtime import bootstrap_runtime, runtime_launch_command


def test_runtime_launch_command_runs_gateway_only_with_the_isolated_home(tmp_path):
    runtime_home = tmp_path / "caelus" / "runtime"
    bootstrap_runtime(runtime_home, token_factory=lambda: "test-key")

    command, env = runtime_launch_command(runtime_home, hermes_executable="/usr/local/bin/hermes")

    assert command == ["/usr/local/bin/hermes", "gateway", "run", "--force"]
    assert env["HERMES_HOME"] == str(runtime_home)
    assert env["HOME"] != str(runtime_home)
    assert "API_SERVER_KEY" not in env
    assert Path(env["HERMES_HOME"]) != Path.home() / ".hermes"
