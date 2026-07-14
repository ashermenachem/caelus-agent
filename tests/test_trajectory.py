import json
from unittest.mock import patch

import pytest

from caelus_terminal.cli import main
from caelus_terminal.trajectory import TrajectoryDriver


def test_trajectory_driver_starts_recording_in_a_private_replay_directory(tmp_path):
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        return type("Result", (), {"returncode": 0, "stdout": '{"enabled": true}', "stderr": ""})()

    driver = TrajectoryDriver(command_runner=run)
    output_dir = driver.start(tmp_path / "recording")

    assert output_dir == tmp_path / "recording"
    assert commands == [
        [
            "cua-driver",
            "call",
            "start_recording",
            json.dumps({"output_dir": str(output_dir), "record_video": False}, separators=(",", ":")),
        ]
    ]


def test_trajectory_driver_replays_a_recorded_workflow_and_stops_on_error(tmp_path):
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        return type("Result", (), {"returncode": 0, "stdout": '{"replayed": 2}', "stderr": ""})()

    output_dir = tmp_path / "recording"
    output_dir.mkdir()
    result = TrajectoryDriver(command_runner=run).replay(output_dir)

    assert result == {"replayed": 2}
    assert commands[0][2] == "replay_trajectory"
    assert json.loads(commands[0][3]) == {
        "dir": str(tmp_path / "recording"),
        "stop_on_error": True,
        "delay_ms": 500,
    }


def test_replay_record_commands_delegate_to_cua_driver_and_preserve_the_recording_path(tmp_path, capsys):
    recordings = tmp_path / "recordings"

    class FakeDriver:
        def start(self, output_dir):
            output_dir.mkdir(parents=True)
            return output_dir

        def stop(self):
            return {"enabled": False}

        def replay(self, output_dir):
            assert output_dir == recordings / "daily-assignments"
            return {"replayed": 2}

    with patch("caelus_terminal.cli.TrajectoryDriver", return_value=FakeDriver()):
        assert main(["replay", "record", "start", "daily-assignments", "--recordings-dir", str(recordings)]) == 0
        assert main(["replay", "record", "stop", "daily-assignments", "--recordings-dir", str(recordings)]) == 0
        assert main(["replay", "record", "play", "daily-assignments", "--recordings-dir", str(recordings)]) == 0

    output = capsys.readouterr().out
    assert "Recording started: daily-assignments" in output
    assert "Recording stopped: daily-assignments" in output


def test_replay_record_reports_a_local_driver_error_without_a_traceback(tmp_path, capsys):
    recordings = tmp_path / "recordings"

    class BrokenDriver:
        def start(self, output_dir):
            from caelus_terminal.trajectory import TrajectoryError

            raise TrajectoryError("Cua Driver unavailable")

    with patch("caelus_terminal.cli.TrajectoryDriver", return_value=BrokenDriver()):
        with pytest.raises(SystemExit) as error:
            main(["replay", "record", "start", "daily-assignments", "--recordings-dir", str(recordings)])

    assert error.value.code == 2
    assert "Cua Driver unavailable" in capsys.readouterr().err
