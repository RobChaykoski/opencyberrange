"""Database snapshot collection and retention.

Snapshots written by the admin UI and the scheduled collector share one
directory. In production that directory is a named volume, so recreating the
backend container no longer deletes every snapshot.
"""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

from app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_BACKUP_DIR = "/app/backups"
DEFAULT_RETENTION_DAYS = 30
DEFAULT_INTERVAL_HOURS = 24


def backup_directory() -> str:
    return os.environ.get("OCR_BACKUP_DIR", DEFAULT_BACKUP_DIR)


def retention_days() -> int:
    try:
        return max(0, int(os.environ.get(
            "OCR_BACKUP_RETENTION_DAYS", DEFAULT_RETENTION_DAYS
        )))
    except (TypeError, ValueError):
        return DEFAULT_RETENTION_DAYS


def collection_interval_hours() -> float:
    try:
        return float(os.environ.get(
            "OCR_BACKUP_INTERVAL_HOURS", DEFAULT_INTERVAL_HOURS
        ))
    except (TypeError, ValueError):
        return DEFAULT_INTERVAL_HOURS


def backup_files() -> list[dict]:
    """Return .sql snapshots, newest first, matching the admin API shape."""
    directory = backup_directory()
    if not os.path.isdir(directory):
        return []
    files = []
    for name in sorted(os.listdir(directory), reverse=True):
        if not name.endswith(".sql"):
            continue
        path = os.path.join(directory, name)
        files.append({
            "filename": name,
            "size_bytes": os.path.getsize(path),
            "created": datetime.fromtimestamp(
                os.path.getmtime(path), tz=timezone.utc
            ).isoformat(),
            "mtime": os.path.getmtime(path),
        })
    return files


def latest_backup_time() -> Optional[datetime]:
    files = backup_files()
    if not files:
        return None
    latest = max(item["mtime"] for item in files)
    return datetime.fromtimestamp(latest, tz=timezone.utc)


def should_collect_backup(now: Optional[datetime] = None) -> bool:
    interval = collection_interval_hours()
    if interval <= 0:
        return False
    now = now or datetime.now(timezone.utc)
    latest = latest_backup_time()
    if latest is None:
        return True
    return now - latest >= timedelta(hours=interval)


def prune_old_backups(now: Optional[datetime] = None) -> list[str]:
    """Delete snapshots (and their ledgers) past the retention window."""
    days = retention_days()
    if days <= 0:
        return []
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    directory = backup_directory()
    removed = []
    for name in os.listdir(directory):
        if not (name.startswith("ocr_backup_") or name.startswith("ocr_erasure_ledger_")):
            continue
        path = os.path.join(directory, name)
        try:
            modified = datetime.fromtimestamp(
                os.path.getmtime(path), tz=timezone.utc
            )
            if modified < cutoff:
                os.remove(path)
                removed.append(name)
        except OSError as exc:
            logger.warning("Could not prune backup %s: %s", name, exc)
    return removed


def _backup_database_url() -> str:
    """Return a dump identity that can read every tenant row.

    The runtime role is subject to forced RLS, so ``pg_dump`` fails on tables
    such as ``accommodation_events``. Prefer an explicit backup role, then the
    schema owner, and only fall back to the runtime URL for single-role
    development installations.
    """
    return (
        (settings.BACKUP_DATABASE_URL or "").strip()
        or (settings.MIGRATOR_DATABASE_URL or "").strip()
        or settings.DATABASE_URL
    )


# The PostgreSQL 17 pg_dump client emits this setting even when it dumps a
# PostgreSQL 15 server. PG15 rejects the parameter, so a restore with
# ON_ERROR_STOP aborts on the first few lines. Strip it while the dump is
# written; the supported server line is PostgreSQL 15.
_PG17_ONLY_DUMP_SETTINGS = (b"SET transaction_timeout = 0;",)


def strip_unsupported_dump_settings(path: str) -> bool:
    """Remove PG17-only SET lines from a plain SQL dump.

    Returns ``True`` when the file changed. The replacement is atomic and keeps
    the dump at mode 600, so a failed rewrite cannot leave a partial backup.
    """
    directory = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(
        prefix=".ocr-backup-", suffix=".tmp", dir=directory
    )
    changed = False
    try:
        with open(path, "rb") as src, os.fdopen(fd, "wb") as dst:
            for line in src:
                if line.strip() in _PG17_ONLY_DUMP_SETTINGS:
                    changed = True
                    continue
                dst.write(line)
        if changed:
            os.chmod(tmp_path, 0o600)
            os.replace(tmp_path, path)
        else:
            os.unlink(tmp_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    return changed


def create_database_backup(timestamp: Optional[str] = None) -> dict:
    """Run pg_dump into the shared snapshot directory.

    Snapshots are plaintext SQL on the ``backups_data`` volume. They contain
    password hashes, sessions, and PII. The volume must live on encrypted host
    storage, and the directory is forced to mode 700 with files at mode 600.
    See docs/BACKUP-SECURITY.md for the threat model and the offsite GPG path.

    Raises RuntimeError with the pg_dump stderr on failure so callers can put a
    useful message in front of an administrator.
    """
    db_url = _backup_database_url()
    parsed = urlparse(db_url)
    directory = backup_directory()
    os.makedirs(directory, exist_ok=True)
    try:
        os.chmod(directory, 0o700)
    except OSError:
        pass

    stamp = timestamp or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(directory, f"ocr_backup_{stamp}.sql")

    env = os.environ.copy()
    env["PGPASSWORD"] = parsed.password or ""

    try:
        result = subprocess.run(
            [
                "pg_dump",
                "-h", parsed.hostname or "db",
                "-p", str(parsed.port or 5432),
                "-U", parsed.username or "labuser",
                "-d", parsed.path.lstrip("/") or "labdb",
                "-f", backup_file,
                "--no-owner",
                "--no-acl",
                "--clean",
                "--if-exists",
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Backup timed out") from exc

    if result.returncode != 0:
        try:
            os.remove(backup_file)
        except OSError:
            pass
        raise RuntimeError(result.stderr or "pg_dump failed")

    strip_unsupported_dump_settings(backup_file)
    try:
        os.chmod(backup_file, 0o600)
    except OSError:
        pass

    ledger_source = os.environ.get(
        "ERASURE_LEDGER_PATH", "/workbook/erasure-ledger.jsonl"
    )
    ledger_file = None
    if os.path.exists(ledger_source):
        ledger_file = os.path.join(
            directory, f"ocr_erasure_ledger_{stamp}.jsonl"
        )
        shutil.copy2(ledger_source, ledger_file)
        try:
            os.chmod(ledger_file, 0o600)
        except OSError:
            pass

    size = os.path.getsize(backup_file)
    removed = prune_old_backups()
    if removed:
        logger.info("Pruned %d expired backup file(s)", len(removed))

    return {
        "file": backup_file,
        "filename": os.path.basename(backup_file),
        "size_bytes": size,
        "ledger_file": ledger_file,
        "timestamp": stamp,
    }
