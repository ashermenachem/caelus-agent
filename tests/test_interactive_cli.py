from unittest.mock import patch

from caelus_terminal.cli import main


def test_interactive_mode_sends_messages_until_user_quits(capsys):
    with patch("caelus_terminal.cli.HermesClient") as client_class, patch(
        "builtins.input", side_effect=["Hello", "/quit"]
    ):
        client_class.return_value.chat.return_value = "Connected reply"
        exit_code = main(
            [
                "--endpoint", "http://127.0.0.1:8642/v1", "--api-key", "test-key", "--interactive"
            ]
        )

    assert exit_code == 0
    assert client_class.return_value.chat.call_count == 1
    assert "Connected reply" in capsys.readouterr().out
