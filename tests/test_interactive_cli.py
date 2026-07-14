from unittest.mock import patch

from caelus_terminal.cli import main
from caelus_terminal.client import RuntimeDetails


def test_interactive_mode_discovers_runtime_then_sends_messages_until_user_quits(capsys):
    with patch("caelus_terminal.cli.HermesClient") as client_class, patch(
        "builtins.input", side_effect=["Hello", "/quit"]
    ):
        client_class.return_value.discover.return_value = RuntimeDetails(
            model_name="gpt-test",
            skills=["research"],
            mcp_servers=["mcp-github"],
            tools=["web_search"],
        )
        client_class.return_value.chat.return_value = "Connected reply"
        exit_code = main(
            [
                "--endpoint", "http://127.0.0.1:8642/v1", "--api-key", "test-key", "--interactive"
            ]
        )

    output = capsys.readouterr().out
    assert exit_code == 0
    assert client_class.return_value.discover.call_count == 1
    assert client_class.return_value.chat.call_count == 1
    assert "model: gpt-test" in output
    assert "SKILLS: research" in output
    assert "MCP SERVERS: mcp-github" in output
    assert "Connected reply" in output
