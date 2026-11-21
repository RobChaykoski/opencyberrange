"""Uploaded SQL dumps are validated before psql executes them."""

from __future__ import annotations

import types

import pytest
from fastapi import HTTPException

from app.routers import admin as admin_router
from app.services.backup_sql import (
    UnsafeBackupError,
    validate_sql_dump,
    validate_sql_text,
)

SAFE_DUMP = """--
-- PostgreSQL database dump
--
SET statement_timeout = 0;
SELECT pg_catalog.set_config('search_path', '', false);
DROP TABLE IF EXISTS public.users;
CREATE TABLE public.users (id integer, name text);
COPY public.users (id, name) FROM stdin;
1\tALTER SYSTEM
2\tGRANT ALL
\\.
DROP EXTENSION IF EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
CREATE FUNCTION public.touch() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RETURN NEW; END; $$;
"""


def test_safe_pg_dump_is_accepted():
    validate_sql_text(SAFE_DUMP)


def test_pg_dump_restrict_marker_is_accepted():
    validate_sql_text("\\restrict abc123\n\\unrestrict abc123\n")


@pytest.mark.parametrize(
    "sql",
    [
        "\\! id\n",
        "\\copy users from program 'id'\n",
        "COPY users FROM PROGRAM 'id';\n",
        "COPY users FROM '/etc/passwd';\n",
        "COPY users TO '/tmp/leak';\n",
        "SELECT pg_read_file('/etc/passwd');\n",
        "SELECT lo_import('/etc/passwd');\n",
        "ALTER SYSTEM SET work_mem = '1GB';\n",
        "CREATE ROLE attacker SUPERUSER;\n",
        "GRANT ALL ON users TO attacker;\n",
        "DROP DATABASE postgres;\n",
        "SET ROLE ocr_runtime;\n",
        "CREATE EXTENSION plpython3u;\n",
        "DO $$ BEGIN PERFORM 1; END $$;\n",
    ],
)
def test_unsafe_statements_are_rejected(sql):
    with pytest.raises(UnsafeBackupError):
        validate_sql_text(sql)


def test_unterminated_copy_block_is_rejected():
    with pytest.raises(UnsafeBackupError):
        validate_sql_text("COPY users FROM stdin;\n1\tlearner\n")


def test_nul_byte_is_rejected():
    with pytest.raises(UnsafeBackupError):
        validate_sql_text("SELECT 1;\x00")


def test_restore_uses_migrator_role_and_psqlrc_guard(tmp_path, monkeypatch):
    dump = tmp_path / "safe.sql"
    dump.write_text(SAFE_DUMP, encoding="utf-8")

    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["env"] = kwargs.get("env")
        return types.SimpleNamespace(returncode=0, stderr="", stdout="")

    monkeypatch.setattr(admin_router.settings, "MIGRATOR_DATABASE_URL", "postgresql://ocr_migrator:pw@db:5432/labdb")
    monkeypatch.setattr(admin_router.settings, "DATABASE_URL", "postgresql://ocr_runtime:pw@db:5432/labdb")
    monkeypatch.setattr(admin_router, "create_database_backup", lambda: {"filename": "safety.sql"})
    monkeypatch.setattr(admin_router, "log_admin_action", lambda **kwargs: None)
    monkeypatch.setattr("subprocess.run", fake_run)

    admin = types.SimpleNamespace(id=1, username="admin")
    request = types.SimpleNamespace(client=types.SimpleNamespace(host="127.0.0.1"))
    result = admin_router._restore_database_from_path(
        str(dump), "safe.sql", admin, request
    )

    assert result["message"] == "Database restored from safe.sql"
    args = captured["args"]
    assert "-X" in args
    assert "--no-psqlrc" in args
    assert "ocr_migrator" in args
    assert "ocr_runtime" not in args
    assert captured["env"]["PGPASSWORD"] == "pw"


def test_restore_rejects_unsafe_dump_before_snapshot(tmp_path, monkeypatch):
    dump = tmp_path / "unsafe.sql"
    dump.write_text("ALTER SYSTEM SET work_mem = '1GB';\n", encoding="utf-8")

    snapshot_calls = []
    monkeypatch.setattr(
        admin_router,
        "create_database_backup",
        lambda: snapshot_calls.append(True),
    )

    admin = types.SimpleNamespace(id=1, username="admin")
    request = types.SimpleNamespace(client=types.SimpleNamespace(host="127.0.0.1"))

    with pytest.raises(HTTPException) as exc:
        admin_router._restore_database_from_path(
            str(dump), "unsafe.sql", admin, request
        )

    assert exc.value.status_code == 400
    assert snapshot_calls == []


def test_validate_sql_dump_reads_a_file(tmp_path):
    dump = tmp_path / "safe.sql"
    dump.write_text(SAFE_DUMP, encoding="utf-8")
    validate_sql_dump(dump)
