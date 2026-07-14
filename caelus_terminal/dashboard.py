from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DashboardState:
    agent_name: str = "Default"
    model_name: str = "not configured"
    context_percent: int = 0
    runtime_seconds: int = 0
    skills: list[str] = field(default_factory=list)
    mcp_servers: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    tool_activity: list[str] = field(default_factory=list)


def _format_runtime(seconds: int) -> str:
    minutes, remaining_seconds = divmod(max(0, seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02}:{minutes:02}:{remaining_seconds:02}"
    return f"{minutes:02}:{remaining_seconds:02}"


def _display(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def render_dashboard(
    state: DashboardState, *, width: int = 100, show_tool_activity: bool = False
) -> str:
    width = max(width, 60)
    border = "─" * (width - 2)
    title = f" CAELUS // ACTIVE AGENT: {state.agent_name.upper()} "
    title_line = "┌" + title.center(width - 2, "─") + "┐"
    capability_lines = [
        f"SKILLS: {_display(state.skills)}",
        f"MCP SERVERS: {_display(state.mcp_servers)}",
        f"TOOLS: {_display(state.tools)}",
    ]
    lines = [title_line, "├" + border + "┤"]
    lines.extend(f"│ {line:<{width - 4}} │" for line in capability_lines)
    lines.extend(["├" + border + "┤", f"│ {'Chat session ready.':<{width - 4}} │"])

    activity_count = len(state.tool_activity)
    if activity_count:
        marker = "▾" if show_tool_activity else "▸"
        lines.append(f"│ {f'{marker} {activity_count} tool actions':<{width - 4}} │")
        if show_tool_activity:
            lines.extend(
                f"│ {f'  [tool] {activity}':<{width - 4}} │"
                for activity in state.tool_activity
            )

    lines.extend(
        [
            "├" + border + "┤",
            f"│ {'> type a message...':<{width - 4}} │",
            f"│ {f'model: {state.model_name} | context: {state.context_percent}% | runtime: {_format_runtime(state.runtime_seconds)}':<{width - 4}} │",
            "└" + border + "┘",
        ]
    )
    return "\n".join(lines)
