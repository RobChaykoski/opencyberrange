"""File-backed consent suppression ledger.

A PostgreSQL restore can resurrect ranked, cached, or derived rows that a
learner already revoked. The database is not a trustworthy place to remember a
deletion that happened after the backup was taken, so the durable proof lives
in an append-only JSONL ledger on the persistent workbook volume.

Entries contain a keyed subject hash and a consent type, never a user id,
username, email, or deleted payload. A later ``cancelled`` entry for the same
subject and consent type wins, which lets a failed transaction or an explicit
re-grant undo the suppression without deleting the history.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_LEDGER_PATH = "/workbook/consent-suppression.jsonl"


def _ledger_path(path: str | os.PathLike | None = None) -> Path:
    return Path(
        path
        or os.environ.get("CONSENT_SUPPRESSION_PATH")
        or DEFAULT_LEDGER_PATH
    )


def _ledger_key(key: str | bytes | None = None) -> bytes:
    value = (
        key
        or os.environ.get("CONSENT_SUPPRESSION_KEY")
        or os.environ.get("JWT_SECRET")
    )
    if isinstance(value, bytes):
        return value
    if not value:
        # Tests and isolated tools may run without the platform secret. A fixed
        # fallback keeps hashes stable there; deployments always have JWT_SECRET.
        value = "opencyberrange-consent-suppression"
    return value.encode("utf-8")


def subject_hash(user_id: int, key: str | bytes | None = None) -> str:
    normalized = str(int(user_id)).encode("utf-8")
    return hmac.new(_ledger_key(key), normalized, hashlib.sha256).hexdigest()


def append_suppression(
    user_id: int,
    consent_type: str,
    consent_version: int,
    *,
    status: str = "committed",
    reason: str = "consent_revoked",
    path: str | os.PathLike | None = None,
    key: str | bytes | None = None,
) -> str:
    """Append a suppression entry and return the ledger path.

    The entry is fsynced before the caller commits the state transition. If the
    write fails, the caller must abort the revocation: deleting derived data
    without a suppression proof would let a restore bring it back.
    """
    if status not in {"committed", "cancelled"}:
        raise ValueError("status must be committed or cancelled")
    ledger = _ledger_path(path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "subject_hash": subject_hash(user_id, key),
        "consent_type": consent_type,
        "consent_version": int(consent_version),
        "status": status,
        "reason": reason,
    }
    line = (json.dumps(entry, separators=(",", ":")) + "\n").encode("utf-8")
    fd = os.open(ledger, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    try:
        os.write(fd, line)
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        os.chmod(ledger, 0o600)
    except OSError:
        pass
    return str(ledger)


def load_suppressions(
    path: str | os.PathLike | None = None,
) -> dict[tuple[str, str], dict]:
    """Return the latest ledger entry per (subject hash, consent type)."""
    ledger = _ledger_path(path)
    if not ledger.exists():
        return {}
    state: dict[tuple[str, str], dict] = {}
    with ledger.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Ignoring malformed consent suppression line")
                continue
            subject = entry.get("subject_hash")
            consent_type = entry.get("consent_type")
            if not subject or not consent_type:
                continue
            state[(subject, consent_type)] = entry
    return state


def is_suppressed(
    user_id: int,
    consent_type: str,
    *,
    path: str | os.PathLike | None = None,
    key: str | bytes | None = None,
) -> bool:
    entry = load_suppressions(path).get((subject_hash(user_id, key), consent_type))
    return bool(entry and (entry.get("status") or "committed") == "committed")


def suppression_version(
    user_id: int,
    consent_type: str,
    *,
    path: str | os.PathLike | None = None,
    key: str | bytes | None = None,
) -> int | None:
    entry = load_suppressions(path).get((subject_hash(user_id, key), consent_type))
    if not entry or (entry.get("status") or "committed") != "committed":
        return None
    try:
        return int(entry.get("consent_version") or 0)
    except (TypeError, ValueError):
        return None


def active_suppressions(
    path: str | os.PathLike | None = None,
) -> list[dict]:
    """Return committed entries only, newest first."""
    rows = [
        entry
        for entry in load_suppressions(path).values()
        if (entry.get("status") or "committed") == "committed"
    ]
    rows.sort(key=lambda entry: entry.get("ts") or "", reverse=True)
    return rows
