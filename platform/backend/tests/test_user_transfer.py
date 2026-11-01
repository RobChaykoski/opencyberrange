"""Portable user export/import tests.

The transfer utility lives outside the backend package so it can be copied into
an older installation. These tests exercise it against the same ephemeral
database as the rest of the suite.
"""
import importlib.util
import json
import os
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.auth import get_password_hash, verify_password
from app.models import User

pytestmark = pytest.mark.db

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "user_transfer.py"
_spec = importlib.util.spec_from_file_location("user_transfer", SCRIPT)
user_transfer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(user_transfer)


def test_export_contains_portable_fields_without_mfa(tmp_path, db_session, test_user):
    output = tmp_path / "users.json"
    user_transfer.export_users(SimpleNamespace(
        database_url=os.environ["DATABASE_URL"],
        output=str(output),
        include_avatars=False,
    ))

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["format"] == user_transfer.FORMAT
    exported = next(u for u in payload["users"] if u["username"] == test_user.username)
    assert exported["email"] == test_user.email
    assert exported["password_hash"].startswith("$2")
    assert "totp_secret" not in exported
    assert "mfa_recovery_codes" not in exported
    assert "vpn_registered" not in exported


def test_import_creates_user_with_working_password(tmp_path, db_session, test_user):
    suffix = uuid.uuid4().hex[:10]
    username = f"pytest_import_{suffix}"
    email = f"{username}@university.edu"
    password = "Imported#Pass9"
    export = {
        "format": user_transfer.FORMAT,
        "version": 1,
        "users": [{
            "username": username,
            "email": email,
            "password_hash": get_password_hash(password),
            "first_name": "Imported",
            "last_name": "Student",
            "role": "student",
            "is_admin": False,
            "is_active": True,
            "is_approved": True,
        }],
    }
    path = tmp_path / "users.json"
    path.write_text(json.dumps(export), encoding="utf-8")

    user_transfer.import_users(SimpleNamespace(
        input=str(path),
        database_url=os.environ["DATABASE_URL"],
        update=False,
        dry_run=False,
    ))

    created = db_session.query(User).filter(User.username == username).one()
    assert created.email == email
    assert created.first_name == "Imported"
    assert verify_password(password, created.hashed_password)

    db_session.query(User).filter(User.id == created.id).delete()
    db_session.commit()


def test_import_dry_run_does_not_write(tmp_path, db_session):
    suffix = uuid.uuid4().hex[:10]
    username = f"pytest_dry_{suffix}"
    export = {
        "format": user_transfer.FORMAT,
        "version": 1,
        "users": [{
            "username": username,
            "email": f"{username}@university.edu",
            "password_hash": get_password_hash("DryRun#Pass9"),
            "role": "student",
            "is_approved": True,
        }],
    }
    path = tmp_path / "users.json"
    path.write_text(json.dumps(export), encoding="utf-8")

    user_transfer.import_users(SimpleNamespace(
        input=str(path),
        database_url=os.environ["DATABASE_URL"],
        update=False,
        dry_run=True,
    ))

    assert db_session.query(User).filter(User.username == username).first() is None


def test_import_update_refreshes_existing_profile(tmp_path, db_session, test_user):
    export = {
        "format": user_transfer.FORMAT,
        "version": 1,
        "users": [{
            "username": test_user.username,
            "email": test_user.email,
            "password_hash": test_user.hashed_password,
            "first_name": "Updated",
            "last_name": "Name",
            "role": "student",
            "is_admin": False,
            "is_active": True,
            "is_approved": True,
        }],
    }
    path = tmp_path / "users.json"
    path.write_text(json.dumps(export), encoding="utf-8")

    user_transfer.import_users(SimpleNamespace(
        input=str(path),
        database_url=os.environ["DATABASE_URL"],
        update=True,
        dry_run=False,
    ))

    db_session.expire_all()
    updated = db_session.query(User).filter(User.id == test_user.id).one()
    assert updated.first_name == "Updated"
    assert updated.last_name == "Name"
