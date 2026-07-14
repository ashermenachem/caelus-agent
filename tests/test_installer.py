from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "install-macos.sh"


def test_macos_installer_bootstraps_only_an_isolated_caelus_runtime():
    script = SCRIPT.read_text()

    assert '"$BIN_DIR/caelus" runtime init' in script
    assert 'HERMES_HOME=\\"$CAELUS_HOME/runtime\\" hermes setup' in script
    assert "hermes setup\n" not in script.replace(
        'HERMES_HOME="$CAELUS_HOME/runtime" hermes setup\n', ""
    )


def test_macos_installer_can_bootstrap_a_versioned_release_when_piped_from_the_web():
    script = SCRIPT.read_text()

    assert 'CAELUS_VERSION="${CAELUS_VERSION:-v0.1.2}"' in script
    assert "archive/refs/tags/$CAELUS_VERSION.tar.gz" in script
    assert "tar -xz" in script
    assert "CAELUS_SOURCE_DIR" in script
    assert '${BASH_SOURCE[0]:-$0}' in script
    assert 'Downloading Caelus Terminal ${CAELUS_VERSION}' in script
    assert "cleanup()" in script
    assert "  return 0" in script
