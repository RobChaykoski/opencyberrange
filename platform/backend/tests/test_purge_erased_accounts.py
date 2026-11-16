"""Verify restore-time erasure purge against a populated test database.

A database dump can predate a deletion. The live erasure ledger is the source
of truth; this test restores the account row and proves the purge script removes
it again while leaving unrelated accounts alone.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

from app.auth import get_password_hash
from app.models import User
from app.services.erasure import erase_user

pytestmark = pytest.mark.db

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / "scripts" / "purge_erased_accounts.py"


def _user(db, prefix):
    suffix = uuid.uuid4().hex[:8]
    row = User(
        username=f"{prefix}_{suffix}",
        email=f"{prefix}_{suffix}@example.org",
        hashed_password=get_password_hash("Purge#Pass123"),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _run_script(db_url, ledger, key, *args):
    env = os.environ.copy()
    env.update(
        {
            "DATABASE_URL": db_url,
            "ERASURE_LEDGER_PATH": str(ledger),
            "ERASURE_LEDGER_KEY": key,
            "PYTHONPATH": str(REPO / "platform" / "backend"),
        }
    )
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--ledger", str(ledger), "--ledger-key", key, *args],
        cwd=REPO / "platform" / "backend",
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_restored_account_is_purged_and_unrelated_account_survives(
    db_session, monkeypatch, tmp_path
):
    db_url = os.environ["DATABASE_URL"]
    ledger = tmp_path / "erasure-ledger.jsonl"
    key = "test-erasure-ledger-key-32-characters"
    monkeypatch.setenv("ERASURE_LEDGER_PATH", str(ledger))
    monkeypatch.setenv("ERASURE_LEDGER_KEY", key)

    deleted = _user(db_session, "purge_deleted")
    survivor = _user(db_session, "purge_survivor")
    username = deleted.username
    email = deleted.email

    erase_user(db_session, deleted, actor="self", external_cleanup=False)
    assert db_session.query(User).filter(User.id == deleted.id).first() is None

    # Simulate restoring a pre-deletion dump: the same identity returns with a
    # new row id. The ledger must still recognise and purge it.
    restored = User(
        username=username,
        email=email,
        hashed_password=get_password_hash("Purge#Pass123"),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add(restored)
    db_session.commit()
    db_session.refresh(restored)

    dry = _run_script(db_url, ledger, key, "--dry-run")
    assert dry.returncode == 0, dry.stderr
    assert username in dry.stdout
    assert db_session.query(User).filter(User.username == username).first() is not None

    real = _run_script(db_url, ledger, key)
    assert real.returncode == 0, real.stderr
    assert username in real.stdout
    db_session.expire_all()
    assert db_session.query(User).filter(User.username == username).first() is None
    assert db_session.query(User).filter(User.id == survivor.id).first() is not None
