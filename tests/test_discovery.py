import json
from unittest.mock import patch

from caelus_terminal.client import HermesClient


class _Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


def test_client_discovers_model_skills_and_enabled_tools_from_runtime():
    client = HermesClient("http://127.0.0.1:8642/v1", "test-key")
    replies = [
        _Response({"model": "openai-codex/gpt-test"}),
        _Response({"data": [{"name": "maps"}, {"name": "research"}]}),
        _Response(
            {
                "data": [
                    {
                        "name": "web",
                        "enabled": True,
                        "tools": ["web_search", "web_extract"],
                    },
                    {"name": "browser", "enabled": False, "tools": ["browser_navigate"]},
                    {
                        "name": "mcp-github",
                        "enabled": True,
                        "tools": ["github_list_repos"],
                    },
                ]
            }
        ),
    ]

    with patch("caelus_terminal.client.urlopen", side_effect=replies) as urlopen:
        discovered = client.discover()

    assert discovered.model_name == "openai-codex/gpt-test"
    assert discovered.skills == ["maps", "research"]
    assert discovered.tools == ["web_search", "web_extract", "github_list_repos"]
    assert discovered.mcp_servers == ["mcp-github"]
    assert [call.args[0].full_url for call in urlopen.call_args_list] == [
        "http://127.0.0.1:8642/v1/capabilities",
        "http://127.0.0.1:8642/v1/skills",
        "http://127.0.0.1:8642/v1/toolsets",
    ]


def test_client_sends_bearer_auth_when_discovering_runtime():
    client = HermesClient("http://127.0.0.1:8642/v1", "test-key")

    with patch(
        "caelus_terminal.client.urlopen",
        return_value=_Response({"model": "gpt-test"}),
    ) as urlopen:
        client.discover()

    assert urlopen.call_args.args[0].get_header("Authorization") == "Bearer test-key"
