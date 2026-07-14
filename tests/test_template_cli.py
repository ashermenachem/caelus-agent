import json

from caelus_terminal.cli import main


def test_template_export_and_import_commands_round_trip(tmp_path, capsys):
    source = tmp_path / "source"
    source.mkdir()
    (source / "agent.json").write_text(
        json.dumps(
            {
                "name": "Research assistant",
                "description": "Reusable research workflow",
                "instructions": "Cite primary sources.",
            }
        )
    )
    archive = tmp_path / "research.caelus-template"
    destination = tmp_path / "imported"

    assert main(["template", "export", "--source", str(source), "--output", str(archive)]) == 0
    assert archive.is_file()
    assert "Exported safe Caelus agent template" in capsys.readouterr().out

    assert main(["template", "import", "--input", str(archive), "--destination", str(destination)]) == 0
    assert (destination / "agent.json").is_file()
    assert "Imported safe Caelus agent template" in capsys.readouterr().out
