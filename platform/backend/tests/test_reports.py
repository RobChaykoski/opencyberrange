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
    Lab,
    LabCompletion,
    LabSession,
    PlatformSetting,
    ReportExport,
    User,
)

pytestmark = pytest.mark.db

TEST_PASSWORD = "Correct#Horse7Battery"


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

    diagnostics = client.get(
        f"/api/courses/{course_id}/reports/exercise-diagnostics.csv",
        params={"reason": "content review"},
        headers=instructor,
    )
    assert diagnostics.status_code == 200, diagnostics.text
    assert diagnostics.content.startswith(b"\xef\xbb\xbf")
    lines = diagnostics.content.decode("utf-8-sig").splitlines()
    assert lines[0].startswith("report_id,")
    assert lines[1].startswith(diagnostics.headers["x-report-id"])

    queue = client.get(
        f"/api/courses/{course_id}/reports/coaching-queue.csv",
        params={"reason": "outreach planning"},
        headers=instructor,
    )
    assert queue.status_code == 200, queue.text
    queue_lines = queue.content.decode("utf-8-sig").splitlines()
    assert queue_lines[0].startswith("report_id,")
    assert "learner" in queue_lines[0]

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
    rows = list(csv.DictReader(io.StringIO(diagnostics.content.decode("utf-8-sig"))))
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
        csv.DictReader(io.StringIO(queue.content.decode("utf-8-sig")))
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


def test_schema_initialization_is_idempotent(db_schema):
    from app.main import _initialize_schema

    _initialize_schema()
    _initialize_schema()
