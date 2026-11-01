"""GDPR erasure regression tests.

These cover the rules that matter beyond "the user row is gone":
- an instructor who owns courses cannot be deleted;
- the last usable administrator cannot be deleted;
- deleting a student does not touch another student's achievements or
  competition entry, and leaves the competition itself intact;
- self-service deletion clears personal data, WebSocket tickets, activity
  identifiers and invite addresses;
- the data export includes the account record but no secrets.
"""

from datetime import datetime, timedelta, timezone
import uuid

import pytest
from sqlalchemy import text

from app.auth import get_password_hash
from app.models import (
    Achievement,
    ActivityEvent,
    Competition,
    CompetitionLab,
    CompetitionParticipant,
    Course,
    CourseEnrollment,
    FlagAttempt,
    InviteCode,
    LabCompletion,
    User,
)
from app.services.erasure import ErasureBlocked, erase_user


def _user(db, *, role="student", password_hash, suffix):
    user = User(
        username=f"erase_{suffix}",
        email=f"erase_{suffix}@example.edu",
        hashed_password=get_password_hash(password_hash),
        is_active=True,
        is_approved=True,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _course(db, instructor, suffix):
    now = datetime.now(timezone.utc)
    course = Course(
        name=f"Erasure Test {suffix}",
        code=f"ER{suffix[:8]}",
        semester="Test",
        invite_code=f"INV{suffix[:10]}",
        instructor_id=instructor.id,
        start_date=now,
        end_date=now + timedelta(days=7),
        is_active=True,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def _login(client, user, password):
    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_erasure_preserves_other_students_achievements_and_competition(
    client, db_session, test_lab, test_password
):
    suffix = uuid.uuid4().hex[:10]
    instructor = _user(db_session, role="instructor", password_hash=test_password, suffix=f"i{suffix}")
    alice = _user(db_session, password_hash=test_password, suffix=f"a{suffix}")
    bob = _user(db_session, password_hash=test_password, suffix=f"b{suffix}")
    course = _course(db_session, instructor, suffix)
    now = datetime.now(timezone.utc)
    alice_id, alice_username = alice.id, alice.username
    bob_id, bob_username = bob.id, bob.username
    instructor_id = instructor.id

    competition = Competition(
        name=f"Erasure Cup {suffix}",
        start_at=now - timedelta(hours=1),
        end_at=now + timedelta(hours=1),
        created_by=instructor.id,
        is_active=True,
    )
    db_session.add(competition)
    db_session.commit()
    db_session.refresh(competition)

    db_session.add_all([
        CompetitionLab(competition_id=competition.id, lab_id=test_lab.id, sort_order=0),
        CompetitionParticipant(competition_id=competition.id, user_id=alice_id, source="opt_in"),
        CompetitionParticipant(competition_id=competition.id, user_id=bob_id, source="opt_in"),
        Achievement(
            user_id=alice_id,
            course_id=course.id,
            lab_id=test_lab.id,
            achievement_type="first_blood",
        ),
        Achievement(
            user_id=bob_id,
            course_id=course.id,
            lab_id=test_lab.id,
            achievement_type="clean_sweep",
        ),
        LabCompletion(
            user_id=alice_id,
            lab_id=test_lab.id,
            completed_at=now,
            flag_submitted="alice-flag",
            attempts=1,
        ),
        LabCompletion(
            user_id=bob_id,
            lab_id=test_lab.id,
            completed_at=now + timedelta(minutes=1),
            flag_submitted="bob-flag",
            attempts=1,
        ),
    ])
    db_session.commit()

    result = erase_user(db_session, alice, external_cleanup=False, write_ledger=False)
    assert "users" in result.deleted

    db_session.expire_all()
    assert db_session.query(User).filter(User.id == alice_id).first() is None
    assert db_session.query(Achievement).filter(Achievement.user_id == alice_id).count() == 0
    assert db_session.query(CompetitionParticipant).filter(
        CompetitionParticipant.user_id == alice_id
    ).count() == 0

    # Bob and the event itself are untouched.
    assert db_session.query(Achievement).filter(Achievement.user_id == bob_id).count() == 1
    assert db_session.query(CompetitionParticipant).filter(
        CompetitionParticipant.user_id == bob_id
    ).count() == 1
    assert db_session.query(Competition).filter(Competition.id == competition.id).first() is not None
    assert db_session.query(Course).filter(Course.id == course.id).first() is not None
    assert db_session.query(LabCompletion).filter(LabCompletion.user_id == bob_id).count() == 1

    headers = _login(client, bob, test_password)
    wall = client.get("/api/dashboard/celebrations", headers=headers)
    assert wall.status_code == 200, wall.text
    wall_names = {row["username"] for row in wall.json()["recent"]}
    assert bob_username in wall_names
    assert alice_username not in wall_names

    detail = client.get(f"/api/competitions/{competition.id}", headers=headers)
    assert detail.status_code == 200, detail.text
    entry_names = {row["username"] for row in detail.json()["leaderboard"]["entries"]}
    assert bob_username in entry_names
    assert alice_username not in entry_names

    # Cleanup the rows this test created. Bob is still a real row.
    db_session.query(LabCompletion).filter(LabCompletion.lab_id == test_lab.id).delete()
    db_session.query(Achievement).filter(Achievement.course_id == course.id).delete()
    db_session.query(CompetitionParticipant).filter(
        CompetitionParticipant.competition_id == competition.id
    ).delete()
    db_session.query(Competition).filter(Competition.id == competition.id).delete()
    db_session.query(CourseEnrollment).filter(CourseEnrollment.course_id == course.id).delete()
    db_session.query(Course).filter(Course.id == course.id).delete()
    db_session.query(User).filter(User.id.in_([bob_id, instructor_id])).delete()
    db_session.commit()


def test_instructor_with_course_is_blocked(db_session, test_password):
    suffix = uuid.uuid4().hex[:10]
    instructor = _user(db_session, role="instructor", password_hash=test_password, suffix=f"i{suffix}")
    student = _user(db_session, password_hash=test_password, suffix=f"s{suffix}")
    course = _course(db_session, instructor, suffix)
    db_session.add_all([
        CourseEnrollment(course_id=course.id, user_id=student.id),
        Achievement(
            user_id=student.id,
            course_id=course.id,
            achievement_type="first_blood",
        ),
    ])
    db_session.commit()

    with pytest.raises(ErasureBlocked) as exc:
        erase_user(db_session, instructor, external_cleanup=False, write_ledger=False)
    assert exc.value.code == "owned_courses"
    assert exc.value.details["courses"][0]["code"] == course.code

    db_session.expire_all()
    assert db_session.query(User).filter(User.id == instructor.id).first() is not None
    assert db_session.query(Course).filter(Course.id == course.id).first() is not None
    assert db_session.query(CourseEnrollment).filter(
        CourseEnrollment.user_id == student.id
    ).count() == 1
    assert db_session.query(Achievement).filter(Achievement.user_id == student.id).count() == 1

    db_session.query(Achievement).filter(Achievement.course_id == course.id).delete()
    db_session.query(CourseEnrollment).filter(CourseEnrollment.course_id == course.id).delete()
    db_session.query(Course).filter(Course.id == course.id).delete()
    db_session.query(User).filter(User.id.in_([student.id, instructor.id])).delete()
    db_session.commit()


def test_last_admin_is_blocked(db_session, test_password):
    suffix = uuid.uuid4().hex[:10]
    admin = _user(db_session, role="admin", password_hash=test_password, suffix=f"adm{suffix}")

    other_admins = db_session.query(User).filter(
        User.role == "admin", User.id != admin.id
    ).all()
    previous = [(u.id, u.is_active, u.is_locked) for u in other_admins]
    for other in other_admins:
        other.is_active = False
        other.is_locked = True
    db_session.commit()

    try:
        with pytest.raises(ErasureBlocked) as exc:
            erase_user(db_session, admin, external_cleanup=False, write_ledger=False)
        assert exc.value.code == "last_admin"
        assert db_session.query(User).filter(User.id == admin.id).first() is not None
    finally:
        for user_id, is_active, is_locked in previous:
            other = db_session.query(User).filter(User.id == user_id).first()
            if other:
                other.is_active = is_active
                other.is_locked = is_locked
        db_session.query(User).filter(User.id == admin.id).delete()
        db_session.commit()


def test_self_service_erasure_clears_pii_and_export_hides_secrets(
    client, db_session, test_password, monkeypatch
):
    # Do not let the endpoint touch Docker or WireGuard in a unit test.
    monkeypatch.setattr(
        "app.services.erasure._external_cleanup",
        lambda *args, **kwargs: {"labs_destroyed": [], "lab_errors": [], "wireguard": []},
    )
    monkeypatch.setattr(
        "app.services.erasure.append_erasure",
        lambda *args, **kwargs: "/tmp/test-erasure-ledger.jsonl",
    )

    suffix = uuid.uuid4().hex[:10]
    student = _user(db_session, password_hash=test_password, suffix=suffix)
    creator = _user(db_session, role="instructor", password_hash=test_password, suffix=f"c{suffix}")
    student_id = student.id
    student_username = student.username
    student_email = student.email
    creator_id = creator.id

    db_session.execute(
        text(
            "CREATE TABLE IF NOT EXISTS ws_tickets ("
            "ticket varchar(64) PRIMARY KEY, user_id integer NOT NULL, "
            "expires_at timestamp NOT NULL)"
        )
    )
    db_session.execute(
        text(
            "INSERT INTO ws_tickets (ticket, user_id, expires_at) "
            "VALUES (:ticket, :user_id, :expires_at)"
        ),
        {"ticket": f"ticket-{suffix}", "user_id": student_id, "expires_at": datetime.now(timezone.utc)},
    )
    invite = InviteCode(
        code=f"INVITE{suffix}",
        email=student_email,
        created_by=creator_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
    )
    event = ActivityEvent(
        event_type="USER_REGISTERED",
        actor_id=student_id,
        target_type="user",
        target_id=student_id,
        target_label=student_username,
        detail='{"email": "%s"}' % student_email,
        ip_address="203.0.113.5",
    )
    db_session.add_all([invite, event])
    db_session.commit()

    headers = _login(client, student, test_password)

    export = client.get("/api/auth/export", headers=headers)
    assert export.status_code == 200, export.text
    payload = export.json()
    assert payload["account"]["username"] == student_username
    serialized = str(payload)
    assert "hashed_password" not in serialized
    assert "totp_secret" not in serialized
    assert "mfa_recovery_codes" not in serialized

    wrong_confirm = client.post(
        "/api/auth/delete-account",
        headers=headers,
        json={"password": test_password, "confirm": "delete"},
    )
    assert wrong_confirm.status_code == 400

    wrong_password = client.post(
        "/api/auth/delete-account",
        headers=headers,
        json={"password": "not-the-password", "confirm": "DELETE"},
    )
    assert wrong_password.status_code == 401

    deleted = client.post(
        "/api/auth/delete-account",
        headers=headers,
        json={"password": test_password, "confirm": "DELETE"},
    )
    assert deleted.status_code == 200, deleted.text

    db_session.expire_all()
    assert db_session.query(User).filter(User.id == student_id).first() is None
    assert db_session.execute(
        text("SELECT count(*) FROM ws_tickets WHERE user_id = :uid"),
        {"uid": student_id},
    ).scalar() == 0

    invite_row = db_session.query(InviteCode).filter(InviteCode.code == invite.code).first()
    assert invite_row is not None
    assert invite_row.email is None

    event_row = db_session.query(ActivityEvent).filter(ActivityEvent.id == event.id).first()
    assert event_row is not None
    assert event_row.actor_id is None
    assert event_row.target_id is None
    assert event_row.target_label is None
    assert event_row.ip_address is None

    assert client.get("/api/auth/export", headers=headers).status_code == 401

    db_session.query(InviteCode).filter(InviteCode.code == invite.code).delete()
    db_session.query(ActivityEvent).filter(ActivityEvent.id == event.id).delete()
    db_session.query(User).filter(User.id == creator_id).delete()
    db_session.commit()


def test_erasure_ledger_round_trip(tmp_path):
    from app.services.erasure_ledger import (
        append_erasure,
        identifier_hashes,
        is_erased,
        load_erased_hashes,
    )

    path = tmp_path / "erasure-ledger.jsonl"
    key = b"test-ledger-key"

    append_erasure("Alice", "Alice@Example.edu", actor="self", path=path, key=key)

    assert is_erased("alice", "ALICE@example.EDU", path=path, key=key)
    assert not is_erased("bob", "bob@example.edu", path=path, key=key)
    assert len(load_erased_hashes(path)) == 2
    assert identifier_hashes("alice", "ALICE@example.EDU", key) & load_erased_hashes(path)

    # A different key must not match: the ledger is a keyed suppression list,
    # not a portable rainbow table.
    assert not is_erased("alice", "alice@example.edu", path=path, key=b"other-key")

    # A cancelled entry after a committed one means the database delete failed;
    # the account is still live and must not be purged on a restore.
    append_erasure("Alice", "Alice@Example.edu", actor="self", status="cancelled", path=path, key=key)
    assert not is_erased("alice", "alice@example.edu", path=path, key=key)
