"""Per-session flag generation and grader fallback."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from app.models import Lab, LabSession
from app.routers.curriculum import _expected_flag_hash
from app.routers.labs import (
    _flag_render_plan,
    _session_flag_env,
    _session_flag_value,
)
from app.services.docker_manager import DockerManager

STATIC_FLAG = "OCR{static_flag}"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def test_session_flag_env_rotates_matching_dict_environment():
    compose = """
services:
  target:
    environment:
      FLAG: "OCR{static_flag}"
  helper:
    environment:
      LAB_FLAG: "OCR{static_flag}"
      OTHER: "keep"
"""
    env, session_flag = _session_flag_env(compose, _hash(STATIC_FLAG))
    assert session_flag is not None
    assert session_flag.startswith("OCR{static_flag_")
    assert session_flag.endswith("}")
    assert session_flag != STATIC_FLAG
    assert env["target"]["FLAG"] == session_flag
    assert env["helper"]["LAB_FLAG"] == session_flag
    assert "OTHER" not in env["helper"]


def test_session_flag_env_rotates_matching_list_environment():
    compose = """
services:
  target:
    environment:
      - "FLAG=OCR{static_flag}"
      - "OTHER=keep"
"""
    env, session_flag = _session_flag_env(compose, _hash(STATIC_FLAG))
    assert session_flag is not None
    assert env == {"target": {"FLAG": session_flag}}


def test_session_flag_env_leaves_non_matching_flag_alone():
    compose = """
services:
  target:
    environment:
      FLAG: "OCR{other_flag}"
"""
    env, session_flag = _session_flag_env(compose, _hash(STATIC_FLAG))
    assert env == {}
    assert session_flag is None


def test_session_flag_env_without_shared_hash_is_noop():
    env, session_flag = _session_flag_env(
        "services:\n  target:\n    environment:\n      FLAG: OCR{static_flag}\n",
        None,
    )
    assert env == {}
    assert session_flag is None


def test_flag_render_plan_reads_the_lab_contract():
    plan = _flag_render_plan("linux-1-1-ssh-service-detection")
    assert plan is not None
    assert plan["path"] == "/root/flag.txt"
    assert plan["service"] == "target"
    assert plan["command"] == [
        "python3",
        "-u",
        "/opt/ssh-server/ssh_server.py",
    ]


def test_flag_render_override_writes_then_execs_the_original_command():
    session_flag = _session_flag_value(STATIC_FLAG)
    override = DockerManager._flag_render_override(
        {
            "service": "target",
            "path": "/root/flag.txt",
            "command": ["python3", "-u", "/opt/server.py"],
            "owner": "",
            "flag": session_flag,
        }
    )
    assert override["entrypoint"] == ["/bin/sh", "-c"]
    script = override["command"][0]
    assert "/root/flag.txt" in script
    assert "mkdir -p /root" in script
    assert "exec python3 -u /opt/server.py" in script
    assert override["environment"]["LAB_FLAG"] == session_flag


@pytest.mark.db
def test_newest_session_hash_wins_even_when_it_is_null(db_session, test_user):
    now = datetime.now(timezone.utc)
    lab = Lab(
        name="Session Flag Test",
        slug="session-flag-test",
        description="test",
        difficulty="beginner",
        category="web",
        compose_file="services: {}\n",
        is_active=True,
    )
    db_session.add(lab)
    db_session.commit()
    db_session.refresh(lab)

    older = LabSession(
        user_id=test_user.id,
        lab_id=lab.id,
        status="stopped",
        started_at=now - timedelta(hours=2),
        expires_at=now + timedelta(hours=1),
        seeded_flag_hash="a" * 64,
    )
    newer = LabSession(
        user_id=test_user.id,
        lab_id=lab.id,
        status="stopped",
        started_at=now - timedelta(hours=1),
        expires_at=now + timedelta(hours=1),
        seeded_flag_hash=None,
    )
    db_session.add_all([older, newer])
    db_session.commit()

    try:
        assert _expected_flag_hash(db_session, test_user.id, lab.id, "shared") == "shared"

        newer.seeded_flag_hash = "b" * 64
        db_session.commit()
        assert _expected_flag_hash(db_session, test_user.id, lab.id, "shared") == "b" * 64
    finally:
        db_session.query(LabSession).filter(LabSession.lab_id == lab.id).delete()
        db_session.query(Lab).filter(Lab.id == lab.id).delete()
        db_session.commit()
