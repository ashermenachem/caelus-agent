from caelus_terminal.dashboard import DashboardState, render_dashboard


def test_dashboard_renders_agent_capabilities_and_runtime_status():
    state = DashboardState(
        agent_name="Nova",
        model_name="gpt-test",
        context_percent=42,
        runtime_seconds=125,
        skills=["Research", "Files"],
        mcp_servers=["GitHub"],
        tools=["Web", "Terminal"],
    )

    output = render_dashboard(state, width=100)

    assert "CAELUS // ACTIVE AGENT: NOVA" in output
    assert "SKILLS: Research, Files" in output
    assert "MCP SERVERS: GitHub" in output
    assert "TOOLS: Web, Terminal" in output
    assert "model: gpt-test" in output
    assert "context: 42%" in output
    assert "runtime: 02:05" in output


def test_dashboard_collapses_tool_activity_until_expanded():
    state = DashboardState(tool_activity=["Reading docs", "Running tests"])

    collapsed = render_dashboard(state, width=100)
    expanded = render_dashboard(state, width=100, show_tool_activity=True)

    assert "▸ 2 tool actions" in collapsed
    assert "Reading docs" not in collapsed
    assert "▾ 2 tool actions" in expanded
    assert "[tool] Reading docs" in expanded
    assert "[tool] Running tests" in expanded
