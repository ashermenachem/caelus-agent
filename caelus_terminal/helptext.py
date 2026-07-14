from __future__ import annotations


def runtime_help() -> str:
    """Describe Caelus Agent controls without pretending to replace Hermes."""
    return "\n".join(
        [
            "Caelus Agent controls:",
            "  /help          show this help",
            "  /quit, /exit   end this Caelus chat",
            "",
            "Caelus uses the Hermes Agent runtime for the agent loop, tools, skills,",
            "memory, integrations, and provider setup. Runtime slash-command support",
            "will be added only where the connected Hermes API exposes it.",
        ]
    )
