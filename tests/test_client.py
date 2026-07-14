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


def test_client_posts_chat_request_with_named_conversation():
    client = HermesClient("http://127.0.0.1:8642/v1", "test-key")

    with patch("caelus_terminal.client.urlopen", return_value=_Response({"choices": [{"message": {"content": "Hi"}}]})) as request:
        assert client.chat("Hello", conversation="nova") == "Hi"

    sent = request.call_args.args[0]
    assert sent.full_url == "http://127.0.0.1:8642/v1/chat/completions"
    assert json.loads(sent.data) == {"model": "hermes-agent", "input": "Hello", "conversation": "nova"}
    assert sent.get_header("Authorization") == "Bearer test-key"
