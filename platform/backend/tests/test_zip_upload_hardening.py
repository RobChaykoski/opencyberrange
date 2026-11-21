"""ZIP upload limits: traversal, links, encryption, bombs, and metadata size."""

from __future__ import annotations

import io
import stat
import zipfile

import pytest
import yaml

from app.services import lab_upload


def _lab_yaml() -> str:
    return yaml.safe_dump(
        {
            "title": "Demo Lab",
            "category": "network",
            "difficulty": "beginner",
            "estimated_time": 30,
            "prerequisites": [],
            "learning_outcomes": ["Identify the target"],
            "mapped_skills": ["network_systems"],
            "assessment_criteria": ["Submit the flag"],
            "flag": "OCR{demo}",
        },
        sort_keys=False,
    )


def _base_entries() -> dict[str, str]:
    return {
        "lab.yaml": _lab_yaml(),
        "docker-compose.yml": (
            "services:\n"
            "  target:\n"
            "    build: .\n"
            "    labels:\n"
            "      ip_offset: \"10\"\n"
        ),
        "containers/target/Dockerfile": "FROM alpine:3.20\n",
    }


def _zip(entries: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def _target(tmp_path) -> str:
    return str(tmp_path / "labs" / "Track" / "demo-1-1-test")


def _prepare(tmp_path, monkeypatch):
    labs = tmp_path / "labs"
    labs.mkdir()
    monkeypatch.setattr(lab_upload, "LABS_ROOT", str(labs))
    return labs


def test_valid_zip_is_extracted(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    result = lab_upload.validate_and_extract_lab_zip(
        _zip(_base_entries()), _target(tmp_path)
    )
    assert result["file_count"] == 3
    assert (tmp_path / "labs" / "Track" / "demo-1-1-test" / "lab.yaml").is_file()


def test_entry_metadata_rejects_symlink():
    info = zipfile.ZipInfo("link")
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with pytest.raises(lab_upload.ZipValidationError, match="Symbolic links"):
        lab_upload._validate_zip_entry(info)


def test_entry_metadata_rejects_encryption():
    info = zipfile.ZipInfo("secret")
    info.flag_bits = 0x1
    with pytest.raises(lab_upload.ZipValidationError, match="Encrypted"):
        lab_upload._validate_zip_entry(info)


@pytest.mark.parametrize(
    "name",
    ["..\\evil", "/etc/passwd", "C:/Windows/win.ini", "../escape"],
)
def test_entry_metadata_rejects_unsafe_paths(name):
    with pytest.raises(lab_upload.ZipValidationError):
        lab_upload._validate_zip_entry(zipfile.ZipInfo(name))


def test_entry_count_limit(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    monkeypatch.setattr(lab_upload, "MAX_ZIP_ENTRIES", 3)
    entries = _base_entries()
    entries["extra.txt"] = "one too many"
    with pytest.raises(lab_upload.ZipValidationError, match="too many entries"):
        lab_upload.validate_and_extract_lab_zip(_zip(entries), _target(tmp_path))


def test_per_entry_size_limit(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    monkeypatch.setattr(lab_upload, "MAX_ENTRY_UNCOMPRESSED_SIZE", 10)
    with pytest.raises(lab_upload.ZipValidationError, match="too large"):
        lab_upload.validate_and_extract_lab_zip(
            _zip(_base_entries()), _target(tmp_path)
        )


def test_compression_ratio_limit(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    monkeypatch.setattr(lab_upload, "MAX_COMPRESSION_RATIO", 2)
    entries = _base_entries()
    entries["bomb.txt"] = "A" * (1024 * 1024)
    with pytest.raises(lab_upload.ZipValidationError, match="compression ratio"):
        lab_upload.validate_and_extract_lab_zip(_zip(entries), _target(tmp_path))


def test_duplicate_path_is_rejected(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in _base_entries().items():
            archive.writestr(name, data)
        archive.writestr("lab.yaml", _lab_yaml())
    with pytest.raises(lab_upload.ZipValidationError, match="Duplicate path"):
        lab_upload.validate_and_extract_lab_zip(
            buffer.getvalue(), _target(tmp_path)
        )


def test_metadata_file_size_limit(tmp_path, monkeypatch):
    _prepare(tmp_path, monkeypatch)
    monkeypatch.setattr(lab_upload, "MAX_METADATA_FILE_SIZE", 10)
    with pytest.raises(lab_upload.ZipValidationError, match="too large"):
        lab_upload.validate_and_extract_lab_zip(
            _zip(_base_entries()), _target(tmp_path)
        )
