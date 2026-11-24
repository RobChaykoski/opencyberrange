"""Deterministic capstone planning."""

from __future__ import annotations

import uuid

import pytest

from app.auth import get_password_hash
from app.models import CapstonePlan, User
from app.services import capstone_builder

PASSWORD = "Capstone#Pass123"  # Test-only credential; security-delta: allow


def _soc_waivers() -> list[str]:
    return [
        "SIEM-001",
        "SIEM-002",
        "SIEM-004",
        "SIEM-005",
        "SOC-002",
        "TH-001",
        "TH-007",
        "WIN-005",
        "WIN-017",
        "WIN-018",
        "NET-014",
        "NET-015",
        "NET-016",
        "NET-022",
        "NET-034",
    ]


def test_profiles_include_the_soc_analyst():
    rows = capstone_builder.profiles()
    profile = next(row for row in rows if row["id"] == "soc-analyst")
    assert profile["critical_competency_count"] >= 20
    assert profile["tracks"]
    assert profile["capstone"]["title"]


def test_plan_selects_labs_and_reports_a_gate():
    plan = capstone_builder.build_plan(
        {"profile_id": "soc-analyst", "duration_hours": 40, "max_labs": 8}
    )
    assert plan["profile"]["id"] == "soc-analyst"
    assert plan["labs"]
    assert plan["objectives"]
    assert plan["deliverables"]
    assert plan["evidence_map"]
    validation = plan["validation"]
    assert validation["assessment_weights_total"] == 1.0
    assert validation["weights_pass"] is True
    assert validation["coverage_percent"] < 90
    assert validation["publishable"] is False
    assert validation["gaps"]
    assert plan["notes"]


def test_a_waived_plan_can_pass_the_gate():
    plan = capstone_builder.build_plan(
        {
            "profile_id": "soc-analyst",
            "duration_hours": 12,
            "max_labs": 12,
            "waived_competencies": _soc_waivers(),
            "waiver_reason": "The remaining competencies are scheduled for the next curriculum wave.",
            "assume_entry_level": True,
        }
    )
    validation = plan["validation"]
    assert validation["coverage_percent"] == 100.0
    assert validation["coverage_pass"] is True
    assert validation["workload_pass"] is True
    assert validation["waiver_valid"] is True
    assert validation["prerequisite_assumed"]
    assert validation["publishable"] is True


def test_waivers_without_a_reason_do_not_pass():
    plan = capstone_builder.build_plan(
        {
            "profile_id": "soc-analyst",
            "duration_hours": 12,
            "max_labs": 12,
            "waived_competencies": _soc_waivers(),
        }
    )
    assert plan["validation"]["waiver_valid"] is False
    assert plan["validation"]["publishable"] is False


def test_unknown_profile_is_rejected():
    with pytest.raises(capstone_builder.CapstoneError) as error:
        capstone_builder.build_plan({"profile_id": "not-a-profile"})
    assert error.value.code == "capstone_profile_unknown"


def _user(db, role: str) -> User:
    suffix = uuid.uuid4().hex[:10]
    user = User(
        username=f"capstone_{role}_{suffix}",
        email=f"capstone_{role}_{suffix}@example.org",
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        is_approved=True,
        is_admin=role == "admin",
        role=role,
        institution_id="default",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _headers(client, user: User) -> dict:
    response = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": PASSWORD},
    )
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.mark.db
def test_planner_requires_an_instructor(client, db_session):
    student = _user(db_session, "student")
    try:
        response = client.post(
            "/api/capstones/plan",
            json={"profile_id": "soc-analyst"},
            headers=_headers(client, student),
        )
        assert response.status_code == 403
        assert response.headers["X-Error-Code"] == "capstone_forbidden"
    finally:
        db_session.delete(student)
        db_session.commit()


@pytest.mark.db
def test_instructor_can_generate_a_plan(client, db_session):
    instructor = _user(db_session, "instructor")
    try:
        headers = _headers(client, instructor)
        profiles = client.get("/api/capstones/profiles", headers=headers)
        assert profiles.status_code == 200
        assert any(row["id"] == "soc-analyst" for row in profiles.json()["profiles"])

        plan = client.post(
            "/api/capstones/plan",
            json={"profile_id": "soc-analyst", "duration_hours": 40, "max_labs": 8},
            headers=headers,
        )
        assert plan.status_code == 200, plan.text
        body = plan.json()
        assert body["labs"]
        assert body["validation"]["assessment_weights_total"] == 1.0
        assert "publishable" in body["validation"]

        unknown = client.post(
            "/api/capstones/plan",
            json={"profile_id": "not-a-profile"},
            headers=headers,
        )
        assert unknown.status_code == 404
        assert unknown.headers["X-Error-Code"] == "capstone_profile_unknown"
    finally:
        db_session.delete(instructor)
        db_session.commit()


def _waived_payload(**overrides) -> dict:
    payload = {
        "profile_id": "soc-analyst",
        "duration_hours": 12,
        "max_labs": 12,
        "waived_competencies": _soc_waivers(),
        "waiver_reason": "The remaining competencies are scheduled for the next curriculum wave.",
        "assume_entry_level": True,
    }
    payload.update(overrides)
    return payload


def _cleanup(db, users: list[User]) -> None:
    ids = [user.id for user in users]
    db.query(CapstonePlan).filter(CapstonePlan.owner_id.in_(ids)).delete(
        synchronize_session=False
    )
    for user in users:
        db.delete(user)
    db.commit()


@pytest.mark.db
def test_save_list_get_and_approve_a_plan(client, db_session):
    instructor = _user(db_session, "instructor")
    try:
        headers = _headers(client, instructor)
        saved = client.post(
            "/api/capstones/plans",
            json=_waived_payload(title="Blue Team capstone"),
            headers=headers,
        )
        assert saved.status_code == 201, saved.text
        body = saved.json()
        assert body["status"] == "draft"
        assert body["version"] == 1
        assert body["validation"]["publishable"] is True
        plan_id = body["id"]

        listed = client.get("/api/capstones/plans", headers=headers)
        assert listed.status_code == 200
        assert [row["id"] for row in listed.json()["plans"]] == [plan_id]

        fetched = client.get(
            f"/api/capstones/plans/{plan_id}", headers=headers
        )
        assert fetched.status_code == 200
        assert fetched.json()["title"] == "Blue Team capstone"

        approved = client.post(
            f"/api/capstones/plans/{plan_id}/approve", headers=headers
        )
        assert approved.status_code == 200, approved.text
        assert approved.json()["status"] == "approved"
        assert approved.json()["approved_at"]
    finally:
        _cleanup(db_session, [instructor])


@pytest.mark.db
def test_unpublishable_plan_cannot_be_approved(client, db_session):
    instructor = _user(db_session, "instructor")
    try:
        headers = _headers(client, instructor)
        saved = client.post(
            "/api/capstones/plans",
            json={"profile_id": "soc-analyst", "duration_hours": 40, "max_labs": 8},
            headers=headers,
        )
        assert saved.status_code == 201, saved.text
        plan_id = saved.json()["id"]
        approved = client.post(
            f"/api/capstones/plans/{plan_id}/approve", headers=headers
        )
        assert approved.status_code == 409
        assert approved.headers["X-Error-Code"] == "capstone_not_publishable"
    finally:
        _cleanup(db_session, [instructor])


@pytest.mark.db
def test_update_resets_approval_and_increments_version(client, db_session):
    instructor = _user(db_session, "instructor")
    try:
        headers = _headers(client, instructor)
        saved = client.post(
            "/api/capstones/plans", json=_waived_payload(), headers=headers
        ).json()
        plan_id = saved["id"]
        client.post(f"/api/capstones/plans/{plan_id}/approve", headers=headers)

        updated = client.put(
            f"/api/capstones/plans/{plan_id}",
            json=_waived_payload(title="Revised capstone", duration_hours=12),
            headers=headers,
        )
        assert updated.status_code == 200, updated.text
        body = updated.json()
        assert body["version"] == 2
        assert body["status"] == "draft"
        assert body["approved_at"] is None
        assert body["title"] == "Revised capstone"

        archived = client.post(
            f"/api/capstones/plans/{plan_id}/archive", headers=headers
        )
        assert archived.status_code == 200
        assert archived.json()["status"] == "archived"
        edit_archived = client.put(
            f"/api/capstones/plans/{plan_id}",
            json=_waived_payload(),
            headers=headers,
        )
        assert edit_archived.status_code == 409
        assert edit_archived.headers["X-Error-Code"] == "capstone_status_invalid"
    finally:
        _cleanup(db_session, [instructor])


@pytest.mark.db
def test_another_instructor_cannot_read_the_plan(client, db_session):
    owner = _user(db_session, "instructor")
    other = _user(db_session, "instructor")
    try:
        owner_headers = _headers(client, owner)
        saved = client.post(
            "/api/capstones/plans", json=_waived_payload(), headers=owner_headers
        ).json()
        response = client.get(
            f"/api/capstones/plans/{saved['id']}",
            headers=_headers(client, other),
        )
        assert response.status_code == 404
        assert response.headers["X-Error-Code"] == "capstone_not_found"
    finally:
        _cleanup(db_session, [owner, other])
