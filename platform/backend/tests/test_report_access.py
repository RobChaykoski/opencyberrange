"""Report access policy and small-cell suppression tests."""

from types import SimpleNamespace

from app.services import report_access


def _user(role: str, institution_id: str = "inst-a", user_id: int = 1):
    return SimpleNamespace(
        id=user_id,
        role=role,
        institution_id=institution_id,
        username=f"{role}_{user_id}",
    )


def _course(instructor_id: int = 1, institution_id: str = "inst-a"):
    return SimpleNamespace(
        id=10,
        code="CYB101",
        institution_id=institution_id,
        instructor_id=instructor_id,
    )


def test_aggregate_reports_exclude_individual_roles():
    assert report_access.role_can_view("course-health", "privacy_officer")
    assert report_access.role_can_view("course-health", "auditor")
    assert report_access.role_can_view("course-health", "teaching_assistant")
    assert not report_access.role_can_view("course-health", "student")


def test_individual_reports_are_narrower():
    assert report_access.role_can_view("coaching-queue", "mentor")
    assert report_access.role_can_view("coaching-queue", "teaching_assistant")
    assert not report_access.role_can_view("coaching-queue", "privacy_officer")
    assert not report_access.role_can_view("coaching-queue", "auditor")
    assert report_access.role_can_view("student-record-pack", "instructor")
    assert not report_access.role_can_view("student-record-pack", "mentor")


def test_course_scope_for_institution_roles():
    course = _course()
    assert report_access.can_view(course, _user("admin"), "course-health")
    assert report_access.can_view(
        course, _user("auditor", "inst-a"), "course-health"
    )
    assert not report_access.can_view(
        course, _user("auditor", "inst-b"), "course-health"
    )
    assert report_access.can_view(
        course, _user("instructor", "inst-a", 1), "course-health"
    )
    assert not report_access.can_view(
        course, _user("instructor", "inst-a", 2), "course-health"
    )


def test_small_cells_are_blanked():
    rows = [
        {
            "sample_size": 3,
            "completion_rate": 66.7,
            "median_time_minutes": 40,
            "flags": ["low_sample"],
        },
        {
            "sample_size": 8,
            "completion_rate": 75.0,
            "median_time_minutes": 50,
            "flags": [],
        },
    ]
    result = report_access.suppress_small_cells(rows, minimum=5)
    assert result[0]["suppressed"] is True
    assert result[0]["completion_rate"] is None
    assert result[0]["median_time_minutes"] is None
    assert result[0]["flags"] == ["low_sample"]
    assert result[1]["suppressed"] is False
    assert result[1]["completion_rate"] == 75.0


def test_policy_labels_include_purpose_owner_and_retention():
    policy = report_access.policy_for("course-health")
    lines = report_access.csv_label_lines(policy)
    assert any(line.startswith("Report purpose:") for line in lines)
    assert any(line.startswith("Data owner:") for line in lines)
    assert any(line.startswith("Retention:") for line in lines)
    headers = report_access.export_headers(policy)
    assert headers["X-Report-Purpose"] == policy.purpose
    assert headers["X-Report-Retention-Days"] == str(policy.retention_days)
