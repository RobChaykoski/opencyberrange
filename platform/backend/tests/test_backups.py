"""Backup identity selection tests."""

from app.services import backups


def test_backup_url_prefers_dedicated_role(monkeypatch):
    monkeypatch.setattr(backups.settings, "BACKUP_DATABASE_URL", "postgresql://ocr_backup:pw@db/labdb")
    monkeypatch.setattr(backups.settings, "MIGRATOR_DATABASE_URL", "postgresql://ocr_migrator:pw@db/labdb")
    monkeypatch.setattr(backups.settings, "DATABASE_URL", "postgresql://ocr_runtime:pw@db/labdb")
    assert backups._backup_database_url().startswith("postgresql://ocr_backup:")


def test_backup_url_falls_back_to_migrator(monkeypatch):
    monkeypatch.setattr(backups.settings, "BACKUP_DATABASE_URL", "")
    monkeypatch.setattr(backups.settings, "MIGRATOR_DATABASE_URL", "postgresql://ocr_migrator:pw@db/labdb")
    monkeypatch.setattr(backups.settings, "DATABASE_URL", "postgresql://ocr_runtime:pw@db/labdb")
    assert backups._backup_database_url().startswith("postgresql://ocr_migrator:")


def test_backup_url_falls_back_to_runtime_for_single_role_dev(monkeypatch):
    monkeypatch.setattr(backups.settings, "BACKUP_DATABASE_URL", "")
    monkeypatch.setattr(backups.settings, "MIGRATOR_DATABASE_URL", "")
    monkeypatch.setattr(backups.settings, "DATABASE_URL", "postgresql://labuser:pw@db/labdb")
    assert backups._backup_database_url() == "postgresql://labuser:pw@db/labdb"


def test_strip_pg17_transaction_timeout_from_dump(tmp_path):
    path = tmp_path / "dump.sql"
    path.write_bytes(
        b"-- header\n"
        b"SET transaction_timeout = 0;\n"
        b"SET statement_timeout = 0;\n"
    )

    assert backups.strip_unsupported_dump_settings(str(path)) is True

    data = path.read_bytes()
    assert b"transaction_timeout" not in data
    assert b"SET statement_timeout = 0;" in data
    assert backups.strip_unsupported_dump_settings(str(path)) is False
