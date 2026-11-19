"""Privacy-office and auditor governance dashboards.

Both dashboards are aggregate views built from evidence tables. They never
expose learner-level rows, and every view is recorded as a security event.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.consent.models import ConsentState, ConsentSuppression
from app.database import get_db
from app.models import (
    Course,
    CourseEnrollment,
    CourseStaff,
    DataIntegrityLedger,
    DataIntegrityReview,
    LabCompletion,
    OpenBadgeCredential,
    ReadinessStudentNote,
    ReportExport,
    RetentionRun,
    ReviewRequest,
    SecurityEvent,
    User,
)
from app.services import security_events
from app.services.audit import AuditActions, log_admin_action
from app.services.export_labels import export_labels

router = APIRouter()

PRIVACY_ROLES = {"privacy_officer", "institution_admin", "admin"}
AUDIT_ROLES = {"auditor", "institution_admin", "admin"}
DEFAULT_SUPPRESSION = 5


def _require_role(user: User, roles: set[str], label: str) -> None:
    if (user.role or "").strip().lower() not in roles:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail=f"{label} access required")


def _count(db: Session, model, *filters) -> int:
    query = db.query(func.count(model.id))
    if filters:
        query = query.filter(*filters)
    return int(query.scalar() or 0)


def _event_counts(db: Session, days: int = 30) -> dict[str, int]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(SecurityEvent.event_type, func.count(SecurityEvent.id))
        .filter(SecurityEvent.occurred_at >= cutoff)
        .group_by(SecurityEvent.event_type)
        .all()
    )
    return {event_type: int(count) for event_type, count in rows}


def _suppression(db: Session) -> int:
    from app.services import settings_service

    raw = settings_service.get_setting_fresh(
        db, "analytics_min_cohort_size", str(DEFAULT_SUPPRESSION)
    )
    try:
        return max(0, min(int(raw), 1000))
    except (TypeError, ValueError):
        return DEFAULT_SUPPRESSION


def _audit_view(
    db: Session,
    request: Request,
    user: User,
    dashboard: str,
    detail: dict,
) -> None:
    log_admin_action(
        action=AuditActions.GOVERNANCE_VIEWED,
        admin_user_id=user.id,
        admin_username=user.username,
        target_type="governance_dashboard",
        target_id=0,
        target_identifier=dashboard,
        details=detail,
        ip_address=request.client.host if request.client else None,
    )
    security_events.record(
        "governance.viewed",
        actor=user,
        target_type="governance_dashboard",
        target_label=dashboard,
        action=AuditActions.GOVERNANCE_VIEWED,
        path=str(request.url.path),
        ip_address=request.client.host if request.client else None,
        detail=detail,
    )


@router.get("/privacy/dashboard")
def privacy_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggregate privacy evidence for the privacy office."""
    _require_role(current_user, PRIVACY_ROLES, "Privacy office")
    now = datetime.now(timezone.utc)
    threshold = _suppression(db)
    consent_rows = (
        db.query(ConsentState.consent_type, ConsentState.granted, func.count(ConsentState.id))
        .group_by(ConsentState.consent_type, ConsentState.granted)
        .all()
    )
    consent = {}
    for consent_type, granted, count in consent_rows:
        entry = consent.setdefault(consent_type, {"granted": 0, "declined": 0})
        entry["granted" if granted else "declined"] += int(count)
    event_counts = _event_counts(db)
    labels = export_labels() or {}
    latest_retention = (
        db.query(RetentionRun)
        .order_by(RetentionRun.created_at.desc())
        .first()
    )
    payload = {
        "generated_at": now.isoformat(),
        "scope": "institution",
        "suppression_threshold": threshold,
        "learners": _count(db, User, User.role == "student"),
        "minors": _count(db, User, User.role == "student", User.is_minor.is_(True)),
        "courses": _count(db, Course),
        "enrollments": _count(db, CourseEnrollment),
        "consent": consent,
        "erasure_suppressions": _count(db, ConsentSuppression),
        "retention_runs": _count(db, RetentionRun),
        "latest_retention_run": (
            {
                "action": latest_retention.action,
                "created_at": latest_retention.created_at.isoformat()
                if latest_retention.created_at
                else None,
            }
            if latest_retention
            else None
        ),
        "report_exports": _count(db, ReportExport),
        "expired_reports": _count(
            db, ReportExport, ReportExport.expires_at.isnot(None), ReportExport.expires_at < now
        ),
        "report_access": {
            "viewed": event_counts.get("report.viewed", 0),
            "exported": event_counts.get("report.exported", 0),
            "denied": event_counts.get("report.access_denied", 0),
            "library_views": event_counts.get("report.library_viewed", 0),
        },
        "privacy_events": _count(db, SecurityEvent, SecurityEvent.category == "privacy"),
        "data_inventory": {
            "lab_completions": _count(db, LabCompletion),
            "support_records": _count(db, ReadinessStudentNote),
            "report_exports": _count(db, ReportExport),
            "consent_records": _count(db, ConsentState),
            "course_staff": _count(db, CourseStaff),
        },
        "data_labels": {
            "classification": labels.get("classification"),
            "classification_key": labels.get("classification_key"),
            "framework_refs": labels.get("framework_refs") or [],
            "organisation": labels.get("organisation"),
        },
    }
    _audit_view(
        db,
        request,
        current_user,
        "privacy",
        {"learners": payload["learners"], "reports": payload["report_exports"]},
    )
    return payload


@router.get("/audit/dashboard")
def audit_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggregate audit evidence for an auditor."""
    _require_role(current_user, AUDIT_ROLES, "Auditor")
    now = datetime.now(timezone.utc)
    event_counts = _event_counts(db)
    payload = {
        "generated_at": now.isoformat(),
        "scope": "institution",
        "suppression_threshold": _suppression(db),
        "report_exports": _count(db, ReportExport),
        "expired_reports": _count(
            db, ReportExport, ReportExport.expires_at.isnot(None), ReportExport.expires_at < now
        ),
        "report_access": {
            "viewed": event_counts.get("report.viewed", 0),
            "exported": event_counts.get("report.exported", 0),
            "denied": event_counts.get("report.access_denied", 0),
            "library_views": event_counts.get("report.library_viewed", 0),
        },
        "course_staff_events": (
            event_counts.get("course.staff_assigned", 0)
            + event_counts.get("course.staff_removed", 0)
        ),
        "security_events": _count(db, SecurityEvent),
        "integrity_entries": _count(db, DataIntegrityLedger),
        "integrity_unattributed": _count(
            db, DataIntegrityLedger, DataIntegrityLedger.actor_type == "unattributed"
        ),
        "integrity_reviews": _count(db, DataIntegrityReview),
        "retention_runs": _count(db, RetentionRun),
        "erasure_suppressions": _count(db, ConsentSuppression),
        "certificates": _count(db, OpenBadgeCredential),
        "review_requests": _count(db, ReviewRequest),
        "governance_views": event_counts.get("governance.viewed", 0),
    }
    _audit_view(
        db,
        request,
        current_user,
        "audit",
        {
            "report_exports": payload["report_exports"],
            "security_events": payload["security_events"],
        },
    )
    return payload
