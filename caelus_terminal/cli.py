from __future__ import annotations

import argparse

from .client import HermesClient
from .dashboard import DashboardState, render_dashboard
from .helptext import runtime_help


def demo_state() -> DashboardState:
    return DashboardState(
        agent_name="Nova",
        model_name="runtime not connected",
        context_percent=0,
        runtime_seconds=0,
        skills=["Research", "Files", "Memory"],
        mcp_servers=["none configured"],
        tools=["Web", "Terminal", "Browser"],
        tool_activity=["Reading runtime capabilities", "Waiting for an agent connection"],
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Caelus Terminal")
    parser.add_argument("--demo", action="store_true", help="render the local UI demo")
    parser.add_argument(
        "--expanded-tools", action="store_true", help="show collapsed tool activity"
    )
    parser.add_argument("--endpoint", help="local Hermes API endpoint ending in /v1")
    parser.add_argument("--api-key", help="local Hermes API server key")
    parser.add_argument("--agent", default="default", help="Caelus agent conversation name")
    parser.add_argument("--chat", help="send one message through the configured runtime")
    parser.add_argument("--interactive", action="store_true", help="start an interactive terminal chat")
    args = parser.parse_args(argv)

    if args.demo:
        print(render_dashboard(demo_state(), show_tool_activity=args.expanded_tools))
        return 0

    if args.interactive:
        if not args.endpoint or not args.api_key:
            parser.error("--interactive requires --endpoint and --api-key")
        client = HermesClient(args.endpoint, args.api_key)
        runtime = client.discover()
        state = DashboardState(
            agent_name=args.agent,
            model_name=runtime.model_name,
            skills=runtime.skills,
            mcp_servers=runtime.mcp_servers,
            tools=runtime.tools,
        )
        print(render_dashboard(state))
        print("Type /quit to end the Caelus chat session.")
        while True:
            message = input("\n> ").strip()
            if message in {"/quit", "/exit"}:
                return 0
            if message == "/help":
                print("\n" + runtime_help())
                continue
            if not message:
                continue
            state.transcript.append(("You", message))
            reply = client.chat(message, conversation=args.agent)
            state.transcript.append((args.agent, reply))
            print("\n" + render_dashboard(state))

    if args.chat:
        if not args.endpoint or not args.api_key:
            parser.error("--chat requires --endpoint and --api-key")
        reply = HermesClient(args.endpoint, args.api_key).chat(
            args.chat, conversation=args.agent
        )
        print(f"{args.agent}: {reply}")
        return 0

    parser.print_help()
    return 0
