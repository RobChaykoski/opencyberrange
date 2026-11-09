"""DB-backed coverage for the instructor dashboard learning metrics."""
import uuid
from datetime import datetime, timedelta, timezone

from app.auth import get_password_hash
from app.models import FlagAttempt, Lab, LabCompletion, LabSession, User
from app.routers.dashboard import _instructor_learning_metrics

NOW = datetime.now(timezone.utc)


def _student(db, suffix):
    user = User(
        username=f"metric_student_{suffix}",
        email=f"metric_student_{suffix}@university.edu",
        hashed_password=get_password_hash("Correct#Horse7Battery"),
        is_active=True,
        is_admin=False,
        role="student",
        is_approved=True,
    )
    db.add(user)
    db.flush()
    return user


def _lab(db, suffix, index):
    lab = Lab(
        name=f"Metric Lab {index} {suffix}",
        slug=f"metric-lab-{index}-{suffix}",
        description="Learning metrics test lab",
        compose_file="services: {}\n",
        is_active=True,
        visibility="public",
        duration_minutes=30,
        difficulty="beginner",
    )
    db.add(lab)
    db.flush()
    return lab


def test_instructor_learning_metrics_summarize_the_cohort(db_session):
    suffix = uuid.uuid4().hex[:8]
    students = [_student(db_session, f"{suffix}{i}") for i in range(3)]
    labs = [_lab(db_session, suffix, 1), _lab(db_session, suffix, 2)]

    for student in students:
        db_session.add(LabSession(
            user_id=student.id,
            lab_id=labs[0].id,
            status="stopped",
            started_at=NOW - timedelta(days=2),
            expires_at=NOW + timedelta(hours=1),
            stopped_at=NOW - timedelta(days=1),
        ))
    db_session.add_all([
        LabCompletion(
            user_id=students[0].id,
            lab_id=labs[0].id,
            completed_at=NOW - timedelta(days=1),
            flag_submitted="OCR{metrics}",
            attempts=1,
            hints_used=0,
            time_spent_minutes=20,
        ),
        LabCompletion(
            user_id=students[1].id,
            lab_id=labs[1].id,
            completed_at=NOW - timedelta(days=1),
            flag_submitted="OCR{metrics}",
            attempts=3,
            hints_used=2,
            time_spent_minutes=40,
        ),
    ])
    for _ in range(6):
        db_session.add(FlagAttempt(
            user_id=students[2].id,
            lab_id=labs[0].id,
            flag_submitted="OCR{wrong}",
            is_correct=False,
            attempted_at=NOW - timedelta(hours=2),
        ))
    db_session.flush()

    metrics = _instructor_learning_metrics(
        db_session,
        NOW,
        admin_ids=set(),
        student_ids={student.id for student in students},
    )

    assert metrics["students_active"] == 3
    assert metrics["labs_completed"] == 2
    assert metrics["average_score"] == 85.0
    # Student 2 used 2 hints and 3 attempts; student 3 never completed.
    assert metrics["struggling_students"] == 2
    assert metrics["metrics_window_days"] == 7


def test_instructor_learning_metrics_empty_scope_is_zero(db_session):
    metrics = _instructor_learning_metrics(
        db_session, NOW, admin_ids=set(), student_ids=set(),
    )
    assert metrics == {
        "students_active": 0,
        "labs_completed": 0,
        "average_score": None,
        "struggling_students": 0,
        "metrics_window_days": 7,
    }
