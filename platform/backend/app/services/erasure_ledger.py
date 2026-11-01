"""Persistent erasure suppression ledger.

A deleted account must not come back when an operator restores an older
database dump or merges a pre-deletion ``users-export.json``. The database row
is gone, so the only durable proof is a small append-only ledger outside the
database.

The ledger stores keyed hashes, not usernames or email addresses. It lives on
the persistent ``/workbook`` volume by default, which survives container
rebuilds and is not overwritten by a PostgreSQL restore. Backups copy it as a
disaster-recovery artefact, but restore procedures use the live ledger.

Set ``ERASURE_LEDGER_PATH`` to move it and ``ERASURE_LEDGER_KEY`` to use a
dedicated key. When no explicit key is set, the platform JWT secret is used.
Changing the key invalidates existing entries, so treat it as long-lived.
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

DEFAULT_LEDGER_PATH = "/workbook/erasure-ledger.jsonl"


def _ledger_path(path: str | os.PathLike | None = None) -> Path:
    return Path(path or os.environ.get("ERASURE_LEDGER_PATH") or DEFAULT_LEDGER_PATH)


def _ledger_key(key: str | bytes | None = None) -> bytes:
    value = key or os.environ.get("ERASURE_LEDGER_KEY") or os.environ.get("JWT_SECRET")
    if isinstance(value, bytes):
        return value
    if not value:
        # Tests and isolated tools may run without the platform secret. A fixed
        # fallback keeps hashes stable in that environment but is not suitable
        # for a real deployment, where JWT_SECRET is always set.
        value = "opencyberrange-erasure-ledger"
    return value.encode("utf-8")


def identifier_hash(value: str | None, key: str | bytes | None = None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower().encode("utf-8")
    return hmac.new(_ledger_key(key), normalized, hashlib.sha256).hexdigest()


def identifier_hashes(
    username: str | None,
    email: str | None,
    key: str | bytes | None = None,
) -> set[str]:
    return {
        digest
        for digest in (identifier_hash(username, key), identifier_hash(email, key))
        if digest
    }


def append_erasure(
    username: str | None,
    email: str | None,
    *,
    actor: str = "self",
    status: str = "committed",
    path: str | os.PathLike | None = None,
    key: str | bytes | None = None,
) -> str | None:
    """Append a suppression entry and return the ledger path.

    Uses O_APPEND so concurrent workers cannot interleave a line. The entry is
    fsynced before the account row is removed; if this fails, deletion should
    stop rather than create a state a restore can undo.

    ``status`` is ``committed`` or ``cancelled``. A cancelled entry negates an
    earlier committed entry with the same hashes, so a database failure after
    the ledger write cannot suppress a live account on a future restore.
    """
    hashes = identifier_hashes(username, email, key)
    if not hashes:
        return None

    ledger = _ledger_path(path)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "status": status,
        "username_hash": identifier_hash(username, key),
        "email_hash": identifier_hash(email, key),
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


def load_erased_hashes(
    path: str | os.PathLike | None = None,
) -> set[str]:
    """Return every username/email hash recorded in the ledger."""
    ledger = _ledger_path(path)
    if not ledger.exists():
        return set()
    # Later entries win: a cancelled entry after a committed one removes the
    # suppression for that identifier.
    state: dict[str, str] = {}
    with ledger.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Ignoring malformed erasure ledger line")
                continue
            status = entry.get("status") or "committed"
            for field in ("username_hash", "email_hash"):
                value = entry.get(field)
                if value:
                    state[value] = status
    return {value for value, status in state.items() if status == "committed"}


def is_erased(
    username: str | None,
    email: str | None,
    *,
    path: str | os.PathLike | None = None,
    key: str | bytes | None = None,
) -> bool:
    return bool(identifier_hashes(username, email, key) & load_erased_hashes(path))
