"""Role-aware report access, labels, and small-cell suppression.

This is the single policy layer for course reports. Route code asks this module
whether a user may view or export a report; it does not compare role strings in
several places.

Classification is intentionally institution-defined. The export label uses the
configured data-label taxonomy and may carry framework references (for example a
U of T level, ISO/IEC 27001, NIST, GDPR, HIPAA, or PCI DSS mapping) supplied by
the institution.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

from fastapi import HTTPException, Request

from app.models import Course, CourseStaff, User
from app.services import security_events
from app.services.audit import AuditActions, log_admin_action


@dataclass(frozen=True)
class ReportPolicy:
    report_id: str
    title: str
    purpose: str
    owner: str
    retention_days: int
    audience: str  # aggregate | individual
    roles: frozenset[str]
    aggregate: bool = True


AGGREGATE_ROLES = frozenset(
    {
        "instructor",
        "teaching_assistant",
        "institution_admin",
        "admin",
        "auditor",
        "privacy_officer",
    }
)
INDIVIDUAL_ROLES = frozenset(
    {"instructor", "mentor", "teaching_assistant", "admin"}
)
# A gradebook is an academic record, not a coaching view. Mentors and auditors
# do not need learner-level scores, so they stay out of this set.
GRADEBOOK_ROLES = frozenset({"instructor", "teaching_assistant", "admin"})

REPORT_POLICIES: dict[str, ReportPolicy] = {
    "course-health": ReportPolicy(
        report_id="course-health",
        title="Course health brief",
        purpose="Decide what the teaching team should address next.",
        owner="Course instructor",
        retention_days=365,
        audience="aggregate",
        roles=AGGREGATE_ROLES,
    ),
    "exercise-diagnostics": ReportPolicy(
        report_id="exercise-diagnostics",
        title="Exercise diagnostics",
        purpose="Diagnose an underperforming exercise or cohort baseline.",
        owner="Course instructor",
        retention_days=365,
        audience="aggregate",
        roles=AGGREGATE_ROLES,
    ),
    "lab-friction": ReportPolicy(
        report_id="lab-friction",
        title="Lab friction report",
        purpose="Find the exercises where learners start but do not finish, or guess repeatedly.",
        owner="Course instructor or curriculum lead",
        retention_days=365,
        audience="aggregate",
        roles=AGGREGATE_ROLES,
    ),
    "lms-gradebook": ReportPolicy(
        report_id="lms-gradebook",
        title="LMS gradebook export",
        purpose="Import course scores into Canvas, Brightspace, Moodle, or a generic gradebook.",
        owner="Course instructor",
        retention_days=365,
        audience="individual",
        roles=GRADEBOOK_ROLES,
        aggregate=False,
    ),
    "coaching-queue": ReportPolicy(
        report_id="coaching-queue",
        title="Coaching queue",
        purpose="Choose the next support action for an assigned learner.",
        owner="Course instructor or mentor lead",
        retention_days=180,
        audience="individual",
        roles=INDIVIDUAL_ROLES,
        aggregate=False,
    ),
    "student-record-pack": ReportPolicy(
        report_id="student-record-pack",
        title="Full student record pack",
        purpose="Support a meeting, file, appeal, or individual record request.",
        owner="Course instructor",
        retention_days=180,
        audience="individual",
        roles=frozenset({"instructor", "admin"}),
        aggregate=False,
    ),
}

REPORT_LIBRARY = tuple(REPORT_POLICIES)

_EVENT_TYPES = {
    AuditActions.REPORT_VIEWED: "report.viewed",
    AuditActions.REPORT_EXPORTED: "report.exported",
    AuditActions.REPORT_ACCESS_DENIED: "report.access_denied",
    AuditActions.REPORT_LIBRARY_VIEWED: "report.library_viewed",
}


def policy_for(report_id: str) -> ReportPolicy:
    policy = REPORT_POLICIES.get(report_id)
    if policy is None:
        raise HTTPException(status_code=404, detail="Unknown report type")
    return policy


def role_can_view(report_id: str, role: str) -> bool:
    return str(role or "").strip().lower() in policy_for(report_id).roles


def course_scope_allowed(db, course: Course, user: User) -> bool:
    """Return whether the user's course scope permits report access."""
    role = (getattr(user, "role", "") or "").strip().lower()
    if role == "admin":
        return True
    if role in {"institution_admin", "privacy_officer", "auditor"}:
        return (
            course.institution_id is not None
            and course.institution_id == getattr(user, "institution_id", None)
        )
    if role in {"instructor", "mentor", "teaching_assistant"}:
        if course.instructor_id == user.id:
            return True
        if db is None:
            return False
        staff_roles = {
            row.staff_role
            for row in db.query(CourseStaff)
            .filter(
                CourseStaff.course_id == course.id,
                CourseStaff.user_id == user.id,
            )
            .all()
        }
        if role == "instructor":
            return "co_instructor" in staff_roles
        return role in staff_roles
    return False


def can_view(db, course: Course, user: User, report_id: str) -> bool:
    return role_can_view(report_id, getattr(user, "role", "")) and course_scope_allowed(
        db, course, user
    )


def _details(policy: ReportPolicy, **extra) -> dict:
    details = {
        "report": policy.report_id,
        "purpose": policy.purpose,
        "owner": policy.owner,
        "retention_days": policy.retention_days,
        "audience": policy.audience,
    }
    details.update({key: value for key, value in extra.items() if value is not None})
    return details


def audit_access(
    db,
    request: Request,
    user: User,
    course: Course,
    policy: ReportPolicy,
    action: str,
    *,
    reason: Optional[str] = None,
    **extra,
) -> None:
    log_admin_action(
        action=action,
        admin_user_id=user.id,
        admin_username=user.username,
        target_type="course_report",
        target_id=course.id,
        target_identifier=course.code,
        details=_details(policy, reason=reason, **extra),
        ip_address=request.client.host if request.client else None,
    )
    security_events.record(
        _EVENT_TYPES.get(action, "report.viewed"),
        actor=user,
        target_type="course_report",
        target_id=course.id,
        target_label=course.code,
        action=action,
        path=str(request.url.path),
        ip_address=request.client.host if request.client else None,
        detail=_details(policy, reason=reason, **extra),
    )


def audit_library(
    db,
    request: Request,
    user: User,
    course: Course,
    report_ids: Iterable[str],
) -> None:
    log_admin_action(
        action=AuditActions.REPORT_LIBRARY_VIEWED,
        admin_user_id=user.id,
        admin_username=user.username,
        target_type="course_report",
        target_id=course.id,
        target_identifier=course.code,
        details={"reports": list(report_ids)},
        ip_address=request.client.host if request.client else None,
    )
    security_events.record(
        "report.library_viewed",
        actor=user,
        target_type="course_report",
        target_id=course.id,
        target_label=course.code,
        action=AuditActions.REPORT_LIBRARY_VIEWED,
        path=str(request.url.path),
        ip_address=request.client.host if request.client else None,
        detail={"reports": list(report_ids)},
    )


def require_report_access(
    db,
    request: Request,
    user: User,
    course: Course,
    report_id: str,
    *,
    export: bool = False,
) -> ReportPolicy:
    policy = policy_for(report_id)
    if not can_view(db, course, user, report_id):
        audit_access(
            db,
            request,
            user,
            course,
            policy,
            AuditActions.REPORT_ACCESS_DENIED,
            export=export,
        )
        raise HTTPException(
            status_code=403,
            detail="Your role is not permitted to view this report for this course.",
        )
    return policy


def export_headers(policy: ReportPolicy) -> dict[str, str]:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=policy.retention_days)
    return {
        "X-Report-Purpose": policy.purpose,
        "X-Report-Owner": policy.owner,
        "X-Report-Audience": policy.audience,
        "X-Report-Retention-Days": str(policy.retention_days),
        "X-Report-Expires-At": expires.isoformat(),
    }


def expiration(policy: ReportPolicy) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=policy.retention_days)


def csv_label_lines(policy: ReportPolicy) -> list[str]:
    return [
        f"Report purpose: {policy.purpose}",
        f"Data owner: {policy.owner}",
        f"Audience: {policy.audience}",
        f"Retention: {policy.retention_days} days",
    ]


def suppress_small_cells(
    rows: Iterable[dict],
    minimum: int,
    *,
    sample_key: str = "sample_size",
    metric_keys: tuple[str, ...] = (
        "started_learners",
        "completed_learners",
        "completion_rate",
        "started_completion_rate",
        "abandonment_rate",
        "median_time_minutes",
        "median_attempts",
        "hint_pressure_rate",
        "first_attempt_rate",
        "baseline_completions",
        "baseline_median_time_minutes",
        "baseline_mean_time_minutes",
        "baseline_median_hints",
        "baseline_mean_hints",
        "baseline_hint_free_rate",
    ),
) -> list[dict]:
    """Blank aggregate metrics for cells below the institution threshold."""
    result = []
    for row in rows:
        item = dict(row)
        sample = item.get(sample_key)
        try:
            sample_value = int(sample)
        except (TypeError, ValueError):
            sample_value = None
        if minimum > 0 and sample_value is not None and 0 < sample_value < minimum:
            item["suppressed"] = True
            item["suppression_reason"] = (
                f"Small cell: {sample_value} of {minimum} minimum learners."
            )
            for key in metric_keys:
                if key in item:
                    item[key] = None
        else:
            item.setdefault("suppressed", False)
        result.append(item)
    return result
