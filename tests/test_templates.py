import json
import zipfile

import pytest

from caelus_terminal.templates import TemplateValidationError, export_template, import_template


def test_exports_and_imports_allowlisted_portable_agent_template(tmp_path):
    source = tmp_path / "source"
    (source / "skills").mkdir(parents=True)
    (source / "agent.json").write_text(
        json.dumps(
            {
                "name": "Research assistant",
                "description": "A reusable research workflow",
                "instructions": "Cite sources and keep findings concise.",
                "toolsets": ["web", "file"],
            }
        )
    )
    (source / "skills" / "research.md").write_text("# Research\nUse primary sources.\n")
    archive = tmp_path / "research.caelus-template"

    manifest = export_template(source, archive)

    assert archive.is_file()
    assert manifest["format"] == "caelus-agent-template"
    assert [entry["path"] for entry in manifest["files"]] == [
        "agent.json",
        "skills/research.md",
    ]
    with zipfile.ZipFile(archive) as package:
        assert sorted(package.namelist()) == ["agent.json", "manifest.json", "skills/research.md"]

    destination = tmp_path / "imported"
    imported = import_template(archive, destination)

    assert imported == manifest
    assert (destination / "agent.json").read_text() == (source / "agent.json").read_text()
    assert (destination / "skills" / "research.md").read_text() == "# Research\nUse primary sources.\n"


def test_export_rejects_private_state_and_credential_like_content(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "agent.json").write_text(
        json.dumps({"name": "Safe", "description": "Safe", "instructions": "Safe"})
    )
    (source / ".env").write_text("API_KEY=not-safe-to-export\n")

    with pytest.raises(TemplateValidationError, match="unsupported or unsafe path"):
        export_template(source, tmp_path / "template.caelus-template")

    (source / ".env").unlink()
    (source / "skills").mkdir()
    (source / "skills" / "unsafe.md").write_text("token: definitely-not-portable\n")
    with pytest.raises(TemplateValidationError, match="credential-like"):
        export_template(source, tmp_path / "template.caelus-template")


def test_import_rejects_traversal_and_checksum_tampering(tmp_path):
    traversal = tmp_path / "traversal.caelus-template"
    manifest = {
        "format": "caelus-agent-template",
        "version": 1,
        "files": [{"path": "agent.json", "sha256": "0" * 64}],
    }
    with zipfile.ZipFile(traversal, "w") as package:
        package.writestr("manifest.json", json.dumps(manifest))
        package.writestr("../agent.json", "{}")
    with pytest.raises(TemplateValidationError, match="Unsafe archive path"):
        import_template(traversal, tmp_path / "imported")

    source = tmp_path / "source"
    source.mkdir()
    (source / "agent.json").write_text(
        json.dumps({"name": "Safe", "description": "Safe", "instructions": "Safe"})
    )
    valid = tmp_path / "valid.caelus-template"
    export_template(source, valid)
    tampered = tmp_path / "tampered.caelus-template"
    with zipfile.ZipFile(valid) as original, zipfile.ZipFile(tampered, "w") as altered:
        for info in original.infolist():
            altered.writestr(info.filename, "{}" if info.filename == "agent.json" else original.read(info.filename))
    with pytest.raises(TemplateValidationError, match="Checksum mismatch"):
        import_template(tampered, tmp_path / "tampered-import")


def test_import_rejects_malformed_manifest_without_writing_destination(tmp_path):
    archive = tmp_path / "malformed.caelus-template"
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("manifest.json", "[]")
    destination = tmp_path / "destination"

    with pytest.raises(TemplateValidationError, match="manifest.json must be an object"):
        import_template(archive, destination)

    assert not destination.exists()
