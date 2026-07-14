from caelus_terminal.helptext import runtime_help


def test_runtime_help_exposes_caelus_controls_and_retains_runtime_attribution():
    output = runtime_help()

    assert "/help" in output
    assert "/quit" in output
    assert "Caelus uses the Hermes Agent runtime" in output
    assert "caelus setup" not in output
