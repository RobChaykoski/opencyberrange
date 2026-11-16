"""RLS is enforced for a non-superuser runtime role."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app import database
from app.auth import get_password_hash
from app.models import LabCompletion, User
from app.services import tenant_rls

PASSWORD = "Rls#Pass123"  # Test-only credential; security-delta: allow
pytestmark = pytest.mark.db


def _user(db, institution="tenant-a"):
    suffix = uuid.uuid4().hex[:8]
    user = User(
        username=f"rls_{suffix}",
        email=f"rls_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
        institution_id=institution,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_runtime_role_is_subject_to_tenant_rls(db_session, test_lab):
    tenant_rls.apply(database.engine)
    learner_a = _user(db_session, "tenant-a")
    learner_b = _user(db_session, "tenant-b")
    db_session.add_all(
        [
            LabCompletion(user_id=learner_a.id, lab_id=test_lab.id),
            LabCompletion(user_id=learner_b.id, lab_id=test_lab.id),
        ]
    )
    db_session.commit()

    role = f"ocr_probe_{uuid.uuid4().hex[:8]}"
    db_session.execute(text(f'DROP ROLE IF EXISTS "{role}"'))
    db_session.execute(text(f'CREATE ROLE "{role}" NOLOGIN NOBYPASSRLS'))
    db_session.execute(text(f'GRANT USAGE ON SCHEMA public TO "{role}"'))
    db_session.execute(text(f'GRANT SELECT, INSERT ON lab_completions TO "{role}"'))
    db_session.commit()

    try:
        db_session.execute(text(f'SET ROLE "{role}"'))
        db_session.execute(
            text(
                "SELECT set_config('ocr.institution_id', 'tenant-a', true), "
                "set_config('ocr.system_admin', 'false', true)"
            )
        )

        visible = db_session.execute(
            text("SELECT institution_id, count(*) FROM lab_completions GROUP BY 1")
        ).fetchall()
        assert visible == [("tenant-a", 1)]

        with pytest.raises(DBAPIError):
            db_session.execute(
                text(
                    "INSERT INTO lab_completions "
                    "(user_id, lab_id, institution_id) "
                    "VALUES (:user_id, :lab_id, 'tenant-b')"
                ),
                {"user_id": learner_a.id, "lab_id": test_lab.id},
            )
        db_session.rollback()

        db_session.execute(text("RESET ROLE"))
        db_session.execute(
            text(
                "SELECT set_config('ocr.institution_id', 'tenant-b', true), "
                "set_config('ocr.system_admin', 'false', true)"
            )
        )
        db_session.execute(text(f'SET ROLE "{role}"'))
        visible_b = db_session.execute(
            text("SELECT institution_id, count(*) FROM lab_completions GROUP BY 1")
        ).fetchall()
        assert visible_b == [("tenant-b", 1)]
        db_session.execute(text("RESET ROLE"))
    finally:
        db_session.rollback()
        db_session.execute(text(f'DROP OWNED BY "{role}"'))
        db_session.execute(text(f'DROP ROLE IF EXISTS "{role}"'))
        db_session.query(LabCompletion).filter(
            LabCompletion.user_id.in_([learner_a.id, learner_b.id])
        ).delete(synchronize_session=False)
        db_session.query(User).filter(
            User.id.in_([learner_a.id, learner_b.id])
        ).delete(synchronize_session=False)
        db_session.commit()


def test_bootstrap_sql_defines_separate_roles():
    """The bootstrap contract: runtime cannot bypass RLS; migrator can."""
    from pathlib import Path

    sql = (
        Path(__file__).resolve().parents[3] / "db" / "bootstrap-db-roles.sql"
    ).read_text(encoding="utf-8")
    assert "ocr_runtime" in sql
    assert "NOBYPASSRLS" in sql
    assert "BYPASSRLS" in sql
    assert "ALTER DEFAULT PRIVILEGES FOR ROLE ocr_migrator" in sql
