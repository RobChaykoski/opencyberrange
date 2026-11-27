"""Instructor report library and tamper-evident manifest tests."""
import csv
import io
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from app.auth import get_password_hash
from app.models import (
    Course,
    CourseEnrollment,
    CourseLabAssignment,
    CourseStaff,
    FlagAttempt,
    Lab,
    LabCompletion,
    LabSession,
    PlatformSetting,
    ReportExport,
    User,
)

pytestmark = pytest.mark.db

TEST_PASSWORD = "Correct#Horse7Battery"


def _csv_text(content: bytes) -> str:
    """Drop the visible export-label comments before parsing the table."""
    text = content.decode("utf-8-sig")
    return "\n".join(
        line for line in text.splitlines() if not line.startswith("#")
    )


def _csv_rows(content: bytes) -> list[dict]:
    return list(csv.DictReader(io.StringIO(_csv_text(content))))


def _login(client, user):
    resp = client.post(
        "/api/auth/login",
        data={"username": user.username, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture()
def report_data(db_session):
    suffix = uuid.uuid4().hex[:8]
    now = datetime.now(timezone.utc)

    instructor = User(
        username=f"report_instructor_{suffix}",
        email=f"report_instructor_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="instructor",
    )
    outsider = User(
        username=f"report_outsider_{suffix}",
        email=f"report_outsider_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="instructor",
    )
    student_one = User(
        username=f"report_student_one_{suffix}",
        email=f"report_student_one_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    student_two = User(
        username=f"report_student_two_{suffix}",
        email=f"report_student_two_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    student_three = User(
        username=f"report_student_three_{suffix}",
        email=f"report_student_three_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="student",
    )
    db_session.add_all([instructor, outsider, student_one, student_two, student_three])
    db_session.flush()

    cohort_setting = db_session.query(PlatformSetting).filter(
        PlatformSetting.key == "analytics_min_cohort_size"
    ).first()
    if cohort_setting is None:
        db_session.add(PlatformSetting(
            key="analytics_min_cohort_size",
            value="1",
            category="security",
            description="Test threshold",
            is_secret=False,
        ))
    else:
        cohort_setting.value = "1"

    labs = []
    for index in range(2):
        lab = Lab(
            name=f"Report Lab {index + 1} {suffix}",
            slug=f"report-lab-{index + 1}-{suffix}",
            description="Report test lab",
            compose_file="services: {}\n",
            is_active=True,
            visibility="public",
            duration_minutes=60,
            difficulty="medium",
        )
        db_session.add(lab)
        labs.append(lab)
    db_session.flush()

    course = Course(
        name=f"Report Course {suffix}",
        code=f"RP{suffix[:5].upper()}",
        semester="Fall",
        invite_code=f"RP-{suffix}",
        instructor_id=instructor.id,
        start_date=now - timedelta(days=20),
        end_date=now + timedelta(days=20),
        is_active=True,
    )
    db_session.add(course)
    db_session.flush()

    db_session.add_all([
        CourseEnrollment(
            course_id=course.id,
            user_id=student_one.id,
            enrolled_at=now - timedelta(days=10),
        ),
        CourseEnrollment(
            course_id=course.id,
            user_id=student_two.id,
            enrolled_at=now - timedelta(days=10),
        ),
        CourseEnrollment(
            course_id=course.id,
            user_id=student_three.id,
            enrolled_at=now - timedelta(days=10),
        ),
    ])
    for order, lab in enumerate(labs):
        db_session.add(CourseLabAssignment(
            course_id=course.id, lab_id=lab.id, sort_order=order,
        ))
    db_session.add(LabSession(
        user_id=student_one.id,
        lab_id=labs[0].id,
        status="stopped",
        started_at=now - timedelta(days=5),
        expires_at=now + timedelta(hours=1),
        stopped_at=now - timedelta(days=5) + timedelta(hours=1),
    ))
    db_session.add(LabCompletion(
        user_id=student_one.id,
        lab_id=labs[0].id,
        flag_submitted="OCR{report}",
        completed_at=now - timedelta(days=3),
        attempts=3,
        hints_used=2,
        time_spent_minutes=120,
    ))
    db_session.add_all([
        LabCompletion(
            user_id=student_two.id,
            lab_id=labs[0].id,
            flag_submitted="OCR{report}",
            completed_at=now - timedelta(days=3),
            attempts=2,
            hints_used=2,
            time_spent_minutes=100,
        ),
        LabCompletion(
            user_id=student_three.id,
            lab_id=labs[0].id,
            flag_submitted="OCR{report}",
            completed_at=now - timedelta(days=2),
            attempts=1,
            hints_used=0,
            time_spent_minutes=30,
        ),
        LabCompletion(
            user_id=student_one.id,
            lab_id=labs[1].id,
            flag_submitted="OCR{report}",
            completed_at=now - timedelta(days=3),
            attempts=3,
            hints_used=3,
            time_spent_minutes=110,
        ),
        LabCompletion(
            user_id=student_two.id,
            lab_id=labs[1].id,
            flag_submitted="OCR{report}",
            completed_at=now - timedelta(days=3),
            attempts=2,
            hints_used=2,
            time_spent_minutes=90,
        ),
        LabCompletion(
            user_id=student_three.id,
            lab_id=labs[1].id,
            flag_submitted="OCR{report}",
            completed_at=now - timedelta(days=2),
            attempts=1,
            hints_used=0,
            time_spent_minutes=20,
        ),
    ])
    db_session.add_all([
        FlagAttempt(
            user_id=student_one.id,
            lab_id=labs[0].id,
            flag_submitted="OCR{wrong}",
            is_correct=False,
            attempted_at=now - timedelta(days=4),
        ),
        FlagAttempt(
            user_id=student_one.id,
            lab_id=labs[0].id,
            flag_submitted="OCR{still_wrong}",
            is_correct=False,
            attempted_at=now - timedelta(days=4),
        ),
        FlagAttempt(
            user_id=student_one.id,
            lab_id=labs[0].id,
            flag_submitted="HINT_REQUEST_1",
            is_correct=False,
            attempted_at=now - timedelta(days=4),
        ),
        FlagAttempt(
            user_id=student_two.id,
            lab_id=labs[1].id,
            flag_submitted="OCR{nope}",
            is_correct=False,
            attempted_at=now - timedelta(days=4),
        ),
    ])
    db_session.commit()

    yield {
        "course": course,
        "instructor": instructor,
        "outsider": outsider,
        "student_one": student_one,
        "student_two": student_two,
        "student_three": student_three,
        "labs": labs,
    }

    lab_ids = [lab.id for lab in labs]
    db_session.query(ReportExport).filter(
        ReportExport.course_id == course.id
    ).delete(synchronize_session=False)
    db_session.query(LabCompletion).filter(
        LabCompletion.lab_id.in_(lab_ids)
    ).delete(synchronize_session=False)
    db_session.query(LabSession).filter(
        LabSession.lab_id.in_(lab_ids)
    ).delete(synchronize_session=False)
    db_session.query(FlagAttempt).filter(
        FlagAttempt.lab_id.in_(lab_ids)
    ).delete(synchronize_session=False)
    db_session.query(CourseLabAssignment).filter(
        CourseLabAssignment.course_id == course.id
    ).delete(synchronize_session=False)
    db_session.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course.id
    ).delete(synchronize_session=False)
    db_session.query(Course).filter(Course.id == course.id).delete()
    db_session.query(Lab).filter(Lab.id.in_(lab_ids)).delete(synchronize_session=False)
    for user in (instructor, outsider, student_one, student_two, student_three):
        db_session.query(User).filter(User.id == user.id).delete()
    db_session.commit()


def test_report_catalog_requires_course_instructor(client, report_data):
    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id

    resp = client.get(f"/api/courses/{course_id}/reports", headers=instructor)
    assert resp.status_code == 200, resp.text
    catalog = resp.json()["reports"]
    ids = {report["id"] for report in catalog}
    assert {"course-health", "exercise-diagnostics", "coaching-queue"} <= ids
    for report in catalog:
        assert report["formats"]
        for item in report["formats"]:
            assert item["path"].startswith("/courses/")

    outsider = _login(client, report_data["outsider"])
    assert client.get(
        f"/api/courses/{course_id}/reports", headers=outsider
    ).status_code == 403

    student = _login(client, report_data["student_one"])
    assert client.get(
        f"/api/courses/{course_id}/reports", headers=student
    ).status_code == 403


def test_course_staff_assignment_expands_report_scope(client, report_data, db_session):
    instructor = _login(client, report_data["instructor"])
    course = report_data["course"]
    suffix = uuid.uuid4().hex[:8]
    mentor = User(
        username=f"report_mentor_{suffix}",
        email=f"report_mentor_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="mentor",
        institution_id=course.institution_id,
    )
    assistant = User(
        username=f"report_ta_{suffix}",
        email=f"report_ta_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="teaching_assistant",
        institution_id=course.institution_id,
    )
    db_session.add_all([mentor, assistant])
    db_session.commit()
    db_session.refresh(mentor)
    db_session.refresh(assistant)
    try:
        mentor_staff = client.post(
            f"/api/courses/{course.id}/staff",
            headers=instructor,
            json={"user_id": mentor.id, "staff_role": "mentor"},
        )
        assert mentor_staff.status_code == 200, mentor_staff.text
        assistant_staff = client.post(
            f"/api/courses/{course.id}/staff",
            headers=instructor,
            json={"user_id": assistant.id, "staff_role": "teaching_assistant"},
        )
        assert assistant_staff.status_code == 200, assistant_staff.text

        mentor_headers = _login(client, mentor)
        mentor_catalog = client.get(
            f"/api/courses/{course.id}/reports", headers=mentor_headers
        )
        assert mentor_catalog.status_code == 200, mentor_catalog.text
        mentor_ids = {row["id"] for row in mentor_catalog.json()["reports"]}
        assert "coaching-queue" in mentor_ids
        assert "course-health" not in mentor_ids

        mentor_health = client.get(
            f"/api/courses/{course.id}/reports/course-health.pdf",
            params={"reason": "mentor should not see aggregate health"},
            headers=mentor_headers,
        )
        assert mentor_health.status_code == 403

        assistant_headers = _login(client, assistant)
        assistant_catalog = client.get(
            f"/api/courses/{course.id}/reports", headers=assistant_headers
        )
        assert assistant_catalog.status_code == 200, assistant_catalog.text
        assistant_ids = {row["id"] for row in assistant_catalog.json()["reports"]}
        assert {"course-health", "exercise-diagnostics", "coaching-queue"} <= assistant_ids
    finally:
        for member in (mentor, assistant):
            db_session.query(CourseStaff).filter(
                CourseStaff.user_id == member.id
            ).delete()
        for member in (mentor, assistant):
            db_session.delete(member)
        db_session.commit()


def test_course_staff_assignment_is_removed(client, report_data, db_session):
    instructor = _login(client, report_data["instructor"])
    course = report_data["course"]
    suffix = uuid.uuid4().hex[:8]
    mentor = User(
        username=f"report_remove_mentor_{suffix}",
        email=f"report_remove_mentor_{suffix}@university.edu",
        hashed_password=get_password_hash(TEST_PASSWORD),
        is_active=True,
        is_approved=True,
        role="mentor",
        institution_id=course.institution_id,
    )
    db_session.add(mentor)
    db_session.commit()
    db_session.refresh(mentor)
    try:
        created = client.post(
            f"/api/courses/{course.id}/staff",
            headers=instructor,
            json={"user_id": mentor.id, "staff_role": "mentor"},
        )
        assert created.status_code == 200, created.text
        staff_id = created.json()["id"]
        removed = client.delete(
            f"/api/courses/{course.id}/staff/{staff_id}", headers=instructor
        )
        assert removed.status_code == 200, removed.text
        remaining = client.get(
            f"/api/courses/{course.id}/staff", headers=instructor
        )
        assert all(row["id"] != staff_id for row in remaining.json()["staff"])
    finally:
        db_session.query(CourseStaff).filter(
            CourseStaff.user_id == mentor.id
        ).delete()
        db_session.delete(mentor)
        db_session.commit()


def test_report_catalog_enforces_role_policy(client, report_data, db_session):
    course = report_data["course"]
    suffix = uuid.uuid4().hex[:8]
    created = []

    def make_user(role):
        user = User(
            username=f"report_{role}_{suffix}",
            email=f"report_{role}_{suffix}@university.edu",
            hashed_password=get_password_hash(TEST_PASSWORD),
            is_active=True,
            is_approved=True,
            role=role,
            institution_id=course.institution_id,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        created.append(user)
        return _login(client, user)

    try:
        privacy = make_user("privacy_officer")
        auditor = make_user("auditor")
        mentor = make_user("mentor")

        for headers in (privacy, auditor):
            resp = client.get(
                f"/api/courses/{course.id}/reports", headers=headers
            )
            assert resp.status_code == 200, resp.text
            ids = {report["id"] for report in resp.json()["reports"]}
            assert {"course-health", "exercise-diagnostics", "lab-friction"} <= ids
            assert "coaching-queue" not in ids
            assert "student-record-pack" not in ids
            assert "lms-gradebook" not in ids

        health = client.get(
            f"/api/courses/{course.id}/reports/course-health.pdf",
            params={"reason": "privacy and audit review"},
            headers=privacy,
        )
        assert health.status_code == 200, health.text
        assert health.headers["x-report-purpose"]
        assert health.headers["x-report-owner"]
        assert health.headers["x-report-retention-days"] == "365"

        denied = client.get(
            f"/api/courses/{course.id}/reports/coaching-queue.csv",
            params={"reason": "should not be permitted"},
            headers=privacy,
        )
        assert denied.status_code == 403

        mentor_catalog = client.get(
            f"/api/courses/{course.id}/reports", headers=mentor
        )
        assert mentor_catalog.status_code == 403
    finally:
        for user in created:
            db_session.delete(user)
        db_session.commit()


def test_instructor_can_generate_and_download_reports(client, report_data, db_session):
    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id

    health = client.get(
        f"/api/courses/{course_id}/reports/course-health.pdf",
        params={"reason": "weekly teaching review"},
        headers=instructor,
    )
    assert health.status_code == 200, health.text
    assert health.headers["content-type"] == "application/pdf"
    assert health.content.startswith(b"%PDF")
    report_id = health.headers["x-report-id"]
    digest = health.headers["x-report-sha256"]
    assert health.headers["cache-control"] == "no-store"
    assert report_id in health.headers["x-report-filename"]
    assert len(digest) == 64

    manifest = db_session.query(ReportExport).filter(
        ReportExport.report_id == report_id
    ).first()
    assert manifest is not None
    assert manifest.course_id == course_id
    assert manifest.report_type == "course-health"
    assert manifest.format == "pdf"
    assert manifest.sha256 == digest
    assert manifest.signature
    assert manifest.expires_at is not None
    assert health.headers["x-report-purpose"]
    assert health.headers["x-report-retention-days"] == "365"

    diagnostics = client.get(
        f"/api/courses/{course_id}/reports/exercise-diagnostics.csv",
        params={"reason": "content review"},
        headers=instructor,
    )
    assert diagnostics.status_code == 200, diagnostics.text
    assert diagnostics.content.startswith(b"\xef\xbb\xbf")
    lines = diagnostics.content.decode("utf-8-sig").splitlines()
    assert lines[0].startswith("# Data classification:")
    assert any(line.startswith("# Report purpose:") for line in lines)
    assert any(line.startswith("# Data owner:") for line in lines)
    assert any(line.startswith("# Retention:") for line in lines)
    header_index = next(index for index, line in enumerate(lines) if line.startswith("report_id,"))
    assert lines[header_index + 1].startswith(diagnostics.headers["x-report-id"])

    queue = client.get(
        f"/api/courses/{course_id}/reports/coaching-queue.csv",
        params={"reason": "outreach planning"},
        headers=instructor,
    )
    assert queue.status_code == 200, queue.text
    queue_lines = queue.content.decode("utf-8-sig").splitlines()
    queue_header = next(line for line in queue_lines if line.startswith("report_id,"))
    assert "learner" in queue_header

    queue_pdf = client.get(
        f"/api/courses/{course_id}/reports/coaching-queue.pdf",
        params={"reason": "outreach planning"},
        headers=instructor,
    )
    assert queue_pdf.status_code == 200, queue_pdf.text
    assert queue_pdf.content.startswith(b"%PDF")


def test_exercise_baselines_and_fast_hint_free_coaching_signal(client, report_data):
    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id

    diagnostics = client.get(
        f"/api/courses/{course_id}/reports/exercise-diagnostics.csv",
        params={"reason": "baseline review"},
        headers=instructor,
    )
    assert diagnostics.status_code == 200, diagnostics.text
    rows = _csv_rows(diagnostics.content)
    baseline_fields = {
        "baseline_completions",
        "baseline_median_time_minutes",
        "baseline_mean_time_minutes",
        "baseline_median_hints",
        "baseline_mean_hints",
        "baseline_hint_free_rate",
    }
    assert baseline_fields <= set(rows[0])
    lab_one = next(
        row for row in rows if row["exercise"] == report_data["labs"][0].name
    )
    assert lab_one["baseline_completions"] == "3"
    assert lab_one["baseline_median_time_minutes"] == "100.0"
    assert lab_one["baseline_mean_time_minutes"] == "83.3"
    assert lab_one["baseline_median_hints"] == "2.0"
    assert lab_one["baseline_mean_hints"] == "1.33"

    queue = client.get(
        f"/api/courses/{course_id}/reports/coaching-queue.csv",
        params={"reason": "engagement check"},
        headers=instructor,
    )
    assert queue.status_code == 200, queue.text
    queue_rows = list(
        _csv_rows(queue.content)
    )
    fast = next(
        row
        for row in queue_rows
        if row["learner"] == report_data["student_three"].username
    )
    assert fast["signal"] == "Unusually fast, hint-free completion"
    assert "half the cohort" in fast["evidence"]
    assert "not a disciplinary finding" in fast["suggested_action"]
    assert fast["fast_hint_free_completions"] == "2"


def test_student_record_pack_is_manifested_too(client, report_data, db_session):
    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id

    resp = client.get(
        f"/api/courses/{course_id}/report",
        params={"reason": "appeal evidence"},
        headers=instructor,
    )
    assert resp.status_code == 200, resp.text
    assert resp.content.startswith(b"%PDF")
    report_id = resp.headers["x-report-id"]
    manifest = db_session.query(ReportExport).filter(
        ReportExport.report_id == report_id
    ).first()
    assert manifest is not None
    assert manifest.report_type == "student-record-pack"


def test_verification_accepts_only_unmodified_platform_files(
    client, report_data, db_session
):
    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id
    resp = client.get(
        f"/api/courses/{course_id}/reports/course-health.pdf",
        params={"reason": "verification test"},
        headers=instructor,
    )
    report_id = resp.headers["x-report-id"]

    verified = client.post(
        "/api/reports/verify",
        data={"report_id": report_id},
        files={"file": ("report.pdf", resp.content, "application/pdf")},
    )
    assert verified.status_code == 200, verified.text
    assert verified.json()["valid"] is True
    assert verified.json()["report_id"] == report_id
    assert verified.json()["course_code"] == report_data["course"].code
    assert verified.json()["generated_by_role"] == "instructor"
    assert "generated_by" not in verified.json()

    modified = client.post(
        "/api/reports/verify",
        data={"report_id": report_id},
        files={"file": ("report.pdf", resp.content + b"tampered", "application/pdf")},
    )
    assert modified.status_code == 200
    assert modified.json() == {"valid": False, "reason": "checksum_mismatch"}

    missing = client.post(
        "/api/reports/verify",
        data={"report_id": str(uuid.uuid4())},
        files={"file": ("report.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert missing.status_code == 200
    assert missing.json() == {"valid": False, "reason": "not_found"}

    row = db_session.query(ReportExport).filter(
        ReportExport.report_id == report_id
    ).first()
    row.signature = "0" * 64
    db_session.commit()

    rejected = client.post(
        "/api/reports/verify",
        data={"report_id": report_id},
        files={"file": ("report.pdf", resp.content, "application/pdf")},
    )
    assert rejected.status_code == 200
    assert rejected.json() == {
        "valid": False,
        "reason": "manifest_signature_invalid",
    }


def test_students_cannot_generate_reports(client, report_data):
    student = _login(client, report_data["student_one"])
    course_id = report_data["course"].id

    for path in (
        f"/api/courses/{course_id}/reports/course-health.pdf",
        f"/api/courses/{course_id}/reports/exercise-diagnostics.csv",
        f"/api/courses/{course_id}/reports/coaching-queue.csv",
        f"/api/courses/{course_id}/report",
    ):
        resp = client.get(
            path,
            params={"reason": "unauthorized attempt"},
            headers=student,
        )
        assert resp.status_code == 403, (path, resp.text)


def test_non_owner_instructor_cannot_generate_reports(client, report_data):
    outsider = _login(client, report_data["outsider"])
    course_id = report_data["course"].id

    resp = client.get(
        f"/api/courses/{course_id}/reports/course-health.pdf",
        params={"reason": "unauthorized attempt"},
        headers=outsider,
    )
    assert resp.status_code == 403


def test_report_generation_requires_a_reason(client, report_data):
    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id

    resp = client.get(
        f"/api/courses/{course_id}/reports/course-health.pdf",
        params={"reason": "no"},
        headers=instructor,
    )
    assert resp.status_code == 422


def test_under_18_learner_is_excluded_from_reports(client, report_data, db_session):
    minor = report_data["student_three"]
    minor.is_minor = True
    db_session.commit()

    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id

    queue = client.get(
        f"/api/courses/{course_id}/reports/coaching-queue.csv",
        params={"reason": "privacy check"},
        headers=instructor,
    )
    assert queue.status_code == 200, queue.text
    assert minor.username not in queue.content.decode("utf-8-sig")

    individual = client.get(
        f"/api/courses/{course_id}/report/{minor.id}",
        params={"reason": "privacy check"},
        headers=instructor,
    )
    assert individual.status_code == 403


def test_lab_friction_report_counts_wrong_flags_and_hints(
    client, report_data, db_session
):
    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id

    resp = client.get(
        f"/api/courses/{course_id}/reports/lab-friction.csv",
        params={"reason": "pick the next lab to fix"},
        headers=instructor,
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers["x-report-retention-days"] == "365"
    assert "lab-friction" in resp.headers["x-report-filename"]
    rows = _csv_rows(resp.content)
    assert len(rows) == 2
    lab_one = next(
        row for row in rows if row["lab"] == report_data["labs"][0].name
    )
    assert lab_one["starts"] == "3"
    assert lab_one["completed_learners"] == "3"
    assert lab_one["completion_rate"] == "100.0"
    assert lab_one["failed_attempts"] == "2"
    assert lab_one["hint_uses"] == "1"
    assert lab_one["failed_per_completion"] == "0.67"
    assert lab_one["hints_per_completion"] == "0.33"
    assert lab_one["median_minutes"] == "100.0"
    assert lab_one["median_attempts"] == "2.0"
    assert "Slow for its estimate" in lab_one["friction_flags"]

    manifest = db_session.query(ReportExport).filter(
        ReportExport.report_id == resp.headers["x-report-id"]
    ).first()
    assert manifest is not None
    assert manifest.report_type == "lab-friction"


def test_lms_gradebook_adapters_and_access(client, report_data, db_session):
    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id
    lab_names = [lab.name for lab in report_data["labs"]]

    generic = client.get(
        f"/api/courses/{course_id}/reports/lms-gradebook.csv",
        params={"reason": "gradebook sync", "adapter": "generic"},
        headers=instructor,
    )
    assert generic.status_code == 200, generic.text
    assert generic.headers["x-gradebook-adapter"] == "generic"
    assert generic.content.startswith(b"\xef\xbb\xbfreport_id,")
    generic_rows = _csv_rows(generic.content)
    assert len(generic_rows) == 3
    first = generic_rows[0]
    assert set(lab_names) <= set(first)
    assert int(first["max_score"]) > 0
    assert sum(int(first[name]) for name in lab_names) == int(first["total_score"])
    assert float(first["percentage"]) >= 0

    canvas = client.get(
        f"/api/courses/{course_id}/reports/lms-gradebook.csv",
        params={"reason": "gradebook sync", "adapter": "canvas"},
        headers=instructor,
    )
    assert canvas.status_code == 200, canvas.text
    assert canvas.headers["x-gradebook-adapter"] == "canvas"
    canvas_rows = _csv_rows(canvas.content)
    assert canvas_rows[0]["Student"].strip() == "Points Possible"
    assert len(canvas_rows) == 4
    assert {"ID", "SIS User ID", "SIS Login ID", "Section", "Total"} <= set(
        canvas_rows[0]
    )

    brightspace = client.get(
        f"/api/courses/{course_id}/reports/lms-gradebook.csv",
        params={"reason": "gradebook sync", "adapter": "brightspace"},
        headers=instructor,
    )
    assert brightspace.status_code == 200, brightspace.text
    brightspace_rows = _csv_rows(brightspace.content)
    assert len(brightspace_rows) == 3
    assert "OrgDefinedId" in brightspace_rows[0]
    assert brightspace_rows[0]["End-of-Line Indicator"] == "#"

    moodle = client.get(
        f"/api/courses/{course_id}/reports/lms-gradebook.csv",
        params={"reason": "gradebook sync", "adapter": "moodle"},
        headers=instructor,
    )
    assert moodle.status_code == 200, moodle.text
    moodle_rows = _csv_rows(moodle.content)
    assert len(moodle_rows) == 3
    assert {"username", "email", "firstname", "lastname", "idnumber"} <= set(
        moodle_rows[0]
    )

    unknown = client.get(
        f"/api/courses/{course_id}/reports/lms-gradebook.csv",
        params={"reason": "gradebook sync", "adapter": "blackboard"},
        headers=instructor,
    )
    assert unknown.status_code == 400

    outsider = _login(client, report_data["outsider"])
    assert client.get(
        f"/api/courses/{course_id}/reports/lms-gradebook.csv",
        params={"reason": "unauthorized attempt"},
        headers=outsider,
    ).status_code == 403
    student = _login(client, report_data["student_one"])
    assert client.get(
        f"/api/courses/{course_id}/reports/lms-gradebook.csv",
        params={"reason": "unauthorized attempt"},
        headers=student,
    ).status_code == 403


def test_gradebook_excludes_under_18_learners(client, report_data, db_session):
    minor = report_data["student_three"]
    minor.is_minor = True
    db_session.commit()

    instructor = _login(client, report_data["instructor"])
    course_id = report_data["course"].id
    resp = client.get(
        f"/api/courses/{course_id}/reports/lms-gradebook.csv",
        params={"reason": "privacy check"},
        headers=instructor,
    )
    assert resp.status_code == 200, resp.text
    rows = _csv_rows(resp.content)
    assert len(rows) == 2
    assert minor.username not in resp.content.decode("utf-8-sig")


def test_schema_initialization_is_idempotent(db_schema):
    from app.main import _initialize_schema

    _initialize_schema()
    _initialize_schema()
