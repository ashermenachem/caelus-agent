from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "install-macos.sh"


def test_macos_installer_bootstraps_only_an_isolated_caelus_runtime():
    script = SCRIPT.read_text()

    assert '"$BIN_DIR/caelus" runtime init' in script
    assert 'HERMES_HOME=\\"$CAELUS_HOME/runtime\\" hermes setup' in script
    assert "hermes setup\n" not in script.replace(
        'HERMES_HOME="$CAELUS_HOME/runtime" hermes setup\n', ""
    )
