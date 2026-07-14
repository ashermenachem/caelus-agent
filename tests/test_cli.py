from caelus_terminal.cli import main


def test_demo_command_prints_matrix_terminal_dashboard(capsys):
    exit_code = main(["--demo", "--expanded-tools"])

    output = capsys.readouterr().out

    assert exit_code == 0
    assert "CAELUS // ACTIVE AGENT: NOVA" in output
    assert "[tool] Reading runtime capabilities" in output
