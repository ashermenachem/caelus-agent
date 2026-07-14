from unittest.mock import patch

from caelus_terminal.cli import main


def test_connected_chat_sends_message_to_runtime_client(capsys):
    with patch("caelus_terminal.cli.HermesClient") as client_class:
        client_class.return_value.chat.return_value = "Connected reply"
        exit_code = main(
            [
                "--endpoint",
                "http://127.0.0.1:8642/v1",
                "--api-key",
                "test-key",
                "--agent",
                "nova",
                "--chat",
                "Hello",
            ]
        )

    assert exit_code == 0
    assert client_class.return_value.chat.call_args.kwargs["conversation"] == "nova"
    assert "Connected reply" in capsys.readouterr().out
