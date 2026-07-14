from unittest.mock import patch

from caelus_terminal.cli import main


def test_runtime_init_cli_creates_only_the_requested_isolated_home(tmp_path, capsys):
    runtime_home = tmp_path / "isolated" / "runtime"

    result = main(["runtime", "init", "--runtime-home", str(runtime_home), "--runtime-port", "8765"])

    output = capsys.readouterr().out
    assert result == 0
    assert (runtime_home / ".env").exists()
    assert "HERMES_HOME=" + str(runtime_home) in output
    assert "http://127.0.0.1:8765/v1" in output
    assert not (tmp_path / ".hermes").exists()


def test_console_invocation_dispatches_runtime_init_from_sys_argv(tmp_path, monkeypatch):
    runtime_home = tmp_path / "isolated" / "runtime"
    monkeypatch.setattr(
        "sys.argv",
        ["caelus", "runtime", "init", "--runtime-home", str(runtime_home)],
    )

    assert main() == 0
    assert (runtime_home / ".env").exists()


def test_runtime_start_cli_starts_only_the_requested_runtime(tmp_path, capsys):
    runtime_home = tmp_path / "caelus" / "runtime"

    with patch("caelus_terminal.cli.start_runtime", return_value=1234) as start:
        result = main(["runtime", "start", "--runtime-home", str(runtime_home)])

    assert result == 0
    assert start.call_args.args == (runtime_home,)
    assert "Started isolated Caelus runtime (PID 1234)." in capsys.readouterr().out


def test_runtime_status_cli_reports_process_and_api_health(tmp_path, capsys):
    runtime_home = tmp_path / "caelus" / "runtime"

    with patch("caelus_terminal.cli.runtime_is_running", return_value=True), patch(
        "caelus_terminal.cli.api_is_healthy", return_value=True
    ):
        result = main(["runtime", "status", "--runtime-home", str(runtime_home)])

    output = capsys.readouterr().out
    assert result == 0
    assert "process: running" in output
    assert "api: healthy" in output


def test_runtime_stop_cli_stops_only_the_requested_runtime(tmp_path, capsys):
    runtime_home = tmp_path / "caelus" / "runtime"

    with patch("caelus_terminal.cli.stop_runtime", return_value=True) as stop:
        result = main(["runtime", "stop", "--runtime-home", str(runtime_home)])

    assert result == 0
    assert stop.call_args.args == (runtime_home,)
    assert "Stopped isolated Caelus runtime." in capsys.readouterr().out
