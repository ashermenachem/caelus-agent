from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import zipfile


FORMAT = "caelus-agent-template"
VERSION = 1
MANIFEST_NAME = "manifest.json"
MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_BYTES = 5_000_000
_SECRET_PATTERN = re.compile(
    r"(?i)\b(?:api[_-]?key|token|secret|password|authorization)\b\s*[:=]\s*\S+|\bsk-[A-Za-z0-9_-]{12,}\b"
)


class TemplateValidationError(ValueError):
    """Raised when a template contains non-portable or unsafe content."""


def _allowed_path(path: str) -> bool:
    pure = PurePosixPath(path)
    return path == "agent.json" or (
        len(pure.parts) >= 2
        and pure.parts[0] == "skills"
        and pure.suffix == ".md"
        and all(part not in {"", ".", ".."} and not part.startswith(".") for part in pure.parts)
    )


def _validated_text(path: str, content: bytes) -> None:
    if len(content) > MAX_FILE_BYTES:
        raise TemplateValidationError(f"Template file exceeds {MAX_FILE_BYTES} bytes: {path}")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TemplateValidationError(f"Template files must be UTF-8 text: {path}") from exc
    if _SECRET_PATTERN.search(text):
        raise TemplateValidationError(f"Template contains credential-like content: {path}")
    if path == "agent.json":
        try:
            agent = json.loads(text)
        except json.JSONDecodeError as exc:
            raise TemplateValidationError("agent.json must contain valid JSON") from exc
        if not isinstance(agent, dict) or not agent:
            raise TemplateValidationError("agent.json must be a non-empty object")
        allowed_keys = {"name", "description", "instructions", "toolsets"}
        if set(agent) - allowed_keys:
            raise TemplateValidationError("agent.json contains unsupported fields")
        if any(not isinstance(agent.get(key), str) for key in {"name", "description", "instructions"}):
            raise TemplateValidationError("agent.json requires string name, description, and instructions")
        if "toolsets" in agent and (
            not isinstance(agent["toolsets"], list)
            or any(not isinstance(toolset, str) for toolset in agent["toolsets"])
        ):
            raise TemplateValidationError("agent.json toolsets must be a list of strings")


def _manifest(files: dict[str, bytes]) -> dict:
    return {
        "format": FORMAT,
        "version": VERSION,
        "files": [
            {"path": path, "sha256": hashlib.sha256(files[path]).hexdigest()}
            for path in sorted(files)
        ],
    }


def export_template(source: Path, archive: Path) -> dict:
    """Export only generic agent metadata and Markdown skills into a verified archive."""
    source = Path(source)
    archive = Path(archive)
    if not source.is_dir():
        raise TemplateValidationError("Template source must be a directory")
    files: dict[str, bytes] = {}
    for item in sorted(source.rglob("*")):
        if item.is_dir():
            continue
        relative = item.relative_to(source).as_posix()
        if item.is_symlink() or not item.is_file() or not _allowed_path(relative):
            raise TemplateValidationError(f"Template contains unsupported or unsafe path: {relative}")
        content = item.read_bytes()
        _validated_text(relative, content)
        files[relative] = content
    if "agent.json" not in files:
        raise TemplateValidationError("Template must include agent.json")
    if sum(map(len, files.values())) > MAX_TOTAL_BYTES:
        raise TemplateValidationError(f"Template exceeds {MAX_TOTAL_BYTES} bytes")

    manifest = _manifest(files)
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=archive.parent, suffix=".tmp", delete=False) as temp:
        temporary_archive = Path(temp.name)
    try:
        with zipfile.ZipFile(temporary_archive, "w", compression=zipfile.ZIP_DEFLATED) as package:
            package.writestr(MANIFEST_NAME, json.dumps(manifest, sort_keys=True, separators=(",", ":")))
            for path in sorted(files):
                package.writestr(path, files[path])
        temporary_archive.replace(archive)
    finally:
        temporary_archive.unlink(missing_ok=True)
    return manifest


def _safe_archive_path(info: zipfile.ZipInfo) -> str:
    path = info.filename
    pure = PurePosixPath(path)
    if (
        "\\" in path
        or pure.is_absolute()
        or not path
        or any(part in {"", ".", ".."} for part in pure.parts)
        or (info.external_attr >> 16) & 0o170000 == 0o120000
    ):
        raise TemplateValidationError(f"Unsafe archive path: {path}")
    return path


def _read_validated_archive(archive: Path) -> tuple[dict, dict[str, bytes]]:
    try:
        with zipfile.ZipFile(archive) as package:
            infos = package.infolist()
            names = [_safe_archive_path(info) for info in infos]
            if len(names) != len(set(names)) or MANIFEST_NAME not in names:
                raise TemplateValidationError("Archive must contain one manifest.json")
            if sum(info.file_size for info in infos) > MAX_TOTAL_BYTES + 100_000:
                raise TemplateValidationError("Archive is too large")
            raw_manifest = package.read(MANIFEST_NAME)
            try:
                manifest = json.loads(raw_manifest)
            except json.JSONDecodeError as exc:
                raise TemplateValidationError("manifest.json must contain valid JSON") from exc
            if not isinstance(manifest, dict):
                raise TemplateValidationError("manifest.json must be an object")
            if manifest.get("format") != FORMAT or manifest.get("version") != VERSION:
                raise TemplateValidationError("Unsupported Caelus template format")
            entries = manifest.get("files")
            if not isinstance(entries, list) or not entries:
                raise TemplateValidationError("Manifest must list template files")
            declared = {entry.get("path"): entry.get("sha256") for entry in entries if isinstance(entry, dict)}
            if len(declared) != len(entries) or "agent.json" not in declared:
                raise TemplateValidationError("Manifest file entries are invalid")
            if set(names) != {MANIFEST_NAME, *declared}:
                raise TemplateValidationError("Archive contents do not match manifest")
            files: dict[str, bytes] = {}
            for path, digest in declared.items():
                if not isinstance(path, str) or not isinstance(digest, str) or not _allowed_path(path):
                    raise TemplateValidationError("Manifest contains a disallowed template path")
                info = package.getinfo(path)
                if info.file_size > MAX_FILE_BYTES:
                    raise TemplateValidationError(f"Template file exceeds {MAX_FILE_BYTES} bytes: {path}")
                content = package.read(path)
                if hashlib.sha256(content).hexdigest() != digest:
                    raise TemplateValidationError(f"Checksum mismatch for {path}")
                _validated_text(path, content)
                files[path] = content
            return manifest, files
    except zipfile.BadZipFile as exc:
        raise TemplateValidationError("Template archive is not a valid ZIP file") from exc


def import_template(archive: Path, destination: Path) -> dict:
    """Validate then atomically import a portable template into a new directory."""
    archive = Path(archive)
    destination = Path(destination)
    if destination.exists():
        raise TemplateValidationError("Template destination must not already exist")
    manifest, files = _read_validated_archive(archive)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".caelus-template-") as staging:
        staged_destination = Path(staging) / "template"
        staged_destination.mkdir()
        for path, content in files.items():
            target = staged_destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        shutil.move(str(staged_destination), str(destination))
    return manifest
