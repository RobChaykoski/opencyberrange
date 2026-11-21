"""Validate a SQL dump before ``psql`` is allowed to execute it.

Database backups are administrator uploads, but an upload is still
untrusted input. The restore path runs ``psql`` with a schema-owner role, so a
crafted dump must not be able to escape the database, read server files, spawn
programs, change roles, or install an untrusted language.

This is defence in depth, not the only guard. The restore also runs as
``ocr_migrator`` (never the runtime or a superuser), with ``psql -X`` and
``--single-transaction``.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

MAX_SQL_BYTES = 512 * 1024 * 1024

# Meta-commands that a legitimate pg_dump may emit. Everything else is
# rejected: \copy, \i, \o, \connect, \!, \lo_import, and friends can touch the
# host or another database.
_ALLOWED_PSQL_META = {r"\.", r"\restrict", r"\unrestrict"}

_DANGEROUS_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("COPY FROM PROGRAM", re.compile(r"\bCOPY\b[\s\S]*?\bFROM\s+PROGRAM\b", re.I)),
    ("COPY TO PROGRAM", re.compile(r"\bCOPY\b[\s\S]*?\bTO\s+PROGRAM\b", re.I)),
    (
        "COPY from a server file",
        re.compile(r"\bCOPY\b[\s\S]*?\bFROM\s+['\"]?(?:/|[A-Za-z]:[\\/])", re.I),
    ),
    (
        "COPY to a server file",
        re.compile(r"\bCOPY\b[\s\S]*?\bTO\s+['\"]?(?:/|[A-Za-z]:[\\/])", re.I),
    ),
    ("pg_read_file", re.compile(r"\bpg_read_(?:binary_)?file\s*\(", re.I)),
    ("pg_write_file", re.compile(r"\bpg_write_file\s*\(", re.I)),
    ("pg_ls_dir", re.compile(r"\bpg_ls_dir\s*\(", re.I)),
    ("pg_stat_file", re.compile(r"\bpg_stat_file\s*\(", re.I)),
    ("lo_import", re.compile(r"\blo_import\s*\(", re.I)),
    ("lo_export", re.compile(r"\blo_export\s*\(", re.I)),
    ("ALTER SYSTEM", re.compile(r"\bALTER\s+SYSTEM\b", re.I)),
    (
        "role change",
        re.compile(r"\b(?:CREATE|ALTER|DROP)\s+(?:ROLE|USER)\b", re.I),
    ),
    ("privilege change", re.compile(r"\b(?:GRANT|REVOKE)\b", re.I)),
    (
        "database create/drop",
        re.compile(r"\b(?:CREATE|DROP)\s+DATABASE\b", re.I),
    ),
    (
        "role switch",
        re.compile(r"\b(?:SET|RESET)\s+(?:ROLE|SESSION\s+AUTHORIZATION)\b", re.I),
    ),
    (
        "untrusted procedural language",
        re.compile(
            r"\bLANGUAGE\s+(?:plpythonu|plpython3u|plperlu|plsh|plr|plv8|pljava|pllua)\b",
            re.I,
        ),
    ),
    (
        "C or internal language",
        re.compile(r"\bLANGUAGE\s+(?:c|internal)\b", re.I),
    ),
    ("DO block", re.compile(r"^\s*DO\s+(?:\$|\b)", re.I | re.M)),
]

_EXTENSION_RE = re.compile(
    r"\b(?:CREATE|ALTER|DROP)\s+EXTENSION\s+"
    r"(?:IF\s+(?:NOT\s+)?EXISTS\s+)?"
    r"([A-Za-z_][A-Za-z0-9_]*)",
    re.I,
)
_ALLOWED_EXTENSIONS = {"pgcrypto"}
_COPY_FROM_STDIN_RE = re.compile(
    r"^\s*COPY\b.*\bFROM\s+stdin\s*;\s*$", re.I
)


class UnsafeBackupError(ValueError):
    """The dump contains SQL that is not allowed in a restore."""


def _strip_block_comments(text: str) -> str:
    """Replace /* ... */ with whitespace, preserving line numbers."""
    out: list[str] = []
    index = 0
    in_block = False
    while index < len(text):
        if not in_block and text.startswith("/*", index):
            in_block = True
            out.append("  ")
            index += 2
        elif in_block and text.startswith("*/", index):
            in_block = False
            out.append("  ")
            index += 2
        elif in_block:
            out.append("\n" if text[index] == "\n" else " ")
            index += 1
        else:
            out.append(text[index])
            index += 1
    return "".join(out)


def validate_sql_text(text: str) -> None:
    """Raise :class:`UnsafeBackupError` if the SQL text is not restore-safe."""
    if "\x00" in text:
        raise UnsafeBackupError("NUL byte in SQL dump")

    text = _strip_block_comments(text)
    in_copy_data = False

    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()

        if in_copy_data:
            if stripped == r"\.":
                in_copy_data = False
            continue

        # pg_dump writes full-line comments. Keep inline text so a dangerous
        # statement cannot hide after a comment-looking string.
        if not stripped or stripped.startswith("--"):
            continue

        if stripped.startswith("\\"):
            meta_name = stripped.split(None, 1)[0]
            if meta_name not in _ALLOWED_PSQL_META:
                raise UnsafeBackupError(
                    f"line {number}: psql meta-command is not allowed"
                )
            continue

        if _COPY_FROM_STDIN_RE.match(line):
            in_copy_data = True
            continue

        for label, pattern in _DANGEROUS_PATTERNS:
            if pattern.search(line):
                raise UnsafeBackupError(f"line {number}: {label} is not allowed")

        for match in _EXTENSION_RE.finditer(line):
            if match.group(1).lower() not in _ALLOWED_EXTENSIONS:
                raise UnsafeBackupError(
                    f"line {number}: extension {match.group(1)} is not allowed"
                )

    if in_copy_data:
        raise UnsafeBackupError("COPY data block is not terminated")


def validate_sql_dump(path: str | os.PathLike[str]) -> None:
    """Read and validate a dump file before a restore."""
    file_path = Path(path)
    try:
        size = file_path.stat().st_size
    except OSError as exc:
        raise UnsafeBackupError("backup file is not readable") from exc
    if size > MAX_SQL_BYTES:
        raise UnsafeBackupError("backup file is too large to restore")
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise UnsafeBackupError("backup file is not readable") from exc
    validate_sql_text(text)
