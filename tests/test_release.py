from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_release_metadata_and_notices_disclose_hermes_runtime():
    pyproject = (ROOT / "pyproject.toml").read_text()
    license_text = (ROOT / "LICENSE").read_text()
    notice = (ROOT / "NOTICE").read_text()

    assert 'readme = "README.md"' in pyproject
    assert 'license = {text = "MIT"}' in pyproject
    assert "MIT License" in license_text
    assert "Caelus Terminal" in notice
    assert "Hermes Agent" in notice
    assert "Nous Research" in notice


def test_macos_installer_honors_isolated_home_and_bin_directory():
    script = (ROOT / "scripts" / "install-macos.sh").read_text()

    assert 'BIN_DIR="${CAELUS_BIN_DIR:-$HOME/.local/bin}"' in script
    assert '"$BIN_DIR/caelus" runtime init --runtime-home "$CAELUS_HOME/runtime"' in script
    assert 'PYTHON="${PYTHON:-python3}"' in script


def test_release_check_builds_wheel_and_smoke_tests_isolated_install():
    script = (ROOT / "scripts" / "release-check.sh").read_text()

    assert "pip wheel --no-deps --no-build-isolation" in script
    assert "pytest tests -q" in script
    assert "CAELUS_SKIP_SETUP=1" in script
