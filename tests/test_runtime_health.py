import json
from unittest.mock import patch

from caelus_terminal.runtime import api_is_healthy, bootstrap_runtime


class _Response:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps({"status": "ok", "platform": "hermes-agent"}).encode()


def test_health_check_uses_loopback_api_server_without_sending_credentials(tmp_path):
    runtime_home = tmp_path / "caelus" / "runtime"
    bootstrap_runtime(runtime_home, port=8765, token_factory=lambda: "test-key")

    with patch("caelus_terminal.runtime.urlopen", return_value=_Response()) as urlopen:
        assert api_is_healthy(runtime_home) is True

    request = urlopen.call_args.args[0]
    assert request.full_url == "http://127.0.0.1:8765/health"
    assert request.get_header("Authorization") is None
