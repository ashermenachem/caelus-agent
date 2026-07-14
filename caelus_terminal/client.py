from __future__ import annotations

import json
from urllib.request import Request, urlopen


class HermesClient:
    """Small adapter for Hermes's documented local OpenAI-compatible API server."""

    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def chat(self, message: str, *, conversation: str) -> str:
        payload = {
            "model": "hermes-agent",
            "input": message,
            "conversation": conversation,
        }
        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urlopen(request, timeout=120) as response:  # nosec B310: user supplies local endpoint
            body = json.loads(response.read())
        return body["choices"][0]["message"]["content"]
