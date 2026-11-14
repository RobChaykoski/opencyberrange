"""
Activity event logging service for dashboard feeds and analytics.
"""

import json
import logging
from sqlalchemy.orm import Session
from app.models import ActivityEvent

logger = logging.getLogger(__name__)


class EventTypes:
    LAB_STARTED = "lab_started"
    LAB_STOPPED = "lab_stopped"
    LAB_PAUSED = "lab_paused"
    LAB_RESUMED = "lab_resumed"
    LAB_COMPLETED = "lab_completed"
    FLAG_CORRECT = "flag_correct"
    FLAG_INCORRECT = "flag_incorrect"
    HINT_USED = "hint_used"
    USER_REGISTERED = "user_registered"
    USER_APPROVED = "user_approved"
    SESSION_EXPIRED = "session_expired"
    VPN_DOWNLOADED = "vpn_downloaded"
    COURSE_ENROLLED = "course_enrolled"
    ACHIEVEMENT_AWARDED = "achievement_awarded"
    IMPERSONATION_START = "impersonation_start"
    IMPERSONATION_END = "impersonation_end"
    ACTIVITY_LOG_CLEARED = "activity_log_cleared"
    WORKBOOK_OPENED = "workbook_opened"
    SSO_LOGIN_SUCCESS = "sso_login_success"
    SSO_USER_PROVISIONED = "sso_user_provisioned"
    SSO_ACCOUNT_LINKED = "sso_account_linked"
    ACCOMMODATION_CHANGED = "accommodation_changed"
    MINOR_CONSENT_RECORDED = "minor_consent_recorded"
    RETENTION_POLICY_SET = "retention_policy_set"
    RETENTION_PREVIEW = "retention_preview"
    RETENTION_COMPLETED = "retention_completed"
    REVIEW_REQUESTED = "review_requested"
    REVIEW_DECIDED = "review_decided"
    AUDIT_REPORT_VIEWED = "audit_report_viewed"
    COHORT_CREATED = "cohort_created"
    OPEN_BADGE_ISSUED = "open_badge_issued"
    OPEN_BADGE_REVOKED = "open_badge_revoked"
    OPEN_BADGE_SETTINGS_CHANGED = "open_badge_settings_changed"
    OPEN_BADGE_KEY_ROTATED = "open_badge_key_rotated"
    OPEN_BADGE_CONSENT_CHANGED = "open_badge_consent_changed"


# Human-readable labels for the feed
EVENT_LABELS = {
    EventTypes.LAB_STARTED: "Started Lab",
    EventTypes.LAB_STOPPED: "Stopped Lab",
    EventTypes.LAB_PAUSED: "Paused Lab Clock",
    EventTypes.LAB_RESUMED: "Resumed Lab Clock",
    EventTypes.LAB_COMPLETED: "Completed Lab",
    EventTypes.FLAG_CORRECT: "Solved",
    EventTypes.FLAG_INCORRECT: "Wrong Flag",
    EventTypes.HINT_USED: "Used Hint",
    EventTypes.USER_REGISTERED: "Registered",
    EventTypes.USER_APPROVED: "Approved",
    EventTypes.SESSION_EXPIRED: "Session Expired",
    EventTypes.VPN_DOWNLOADED: "Downloaded VPN",
    EventTypes.COURSE_ENROLLED: "Enrolled in Course",
    EventTypes.ACHIEVEMENT_AWARDED: "Achievement Earned",
    EventTypes.IMPERSONATION_START: "Started Impersonation",
    EventTypes.IMPERSONATION_END: "Ended Impersonation",
    EventTypes.ACTIVITY_LOG_CLEARED: "Activity Log Cleared",
    EventTypes.WORKBOOK_OPENED: "Opened Workbook",
    EventTypes.SSO_LOGIN_SUCCESS: "Signed in with SSO",
    EventTypes.SSO_USER_PROVISIONED: "SSO Account Provisioned",
    EventTypes.SSO_ACCOUNT_LINKED: "SSO Account Linked",
    EventTypes.ACCOMMODATION_CHANGED: "Accommodation Changed",
    EventTypes.MINOR_CONSENT_RECORDED: "Minor Consent Recorded",
    EventTypes.RETENTION_POLICY_SET: "Retention Policy Set",
    EventTypes.RETENTION_PREVIEW: "Retention Preview Run",
    EventTypes.RETENTION_COMPLETED: "Retention Run Completed",
    EventTypes.REVIEW_REQUESTED: "Human Review Requested",
    EventTypes.REVIEW_DECIDED: "Human Review Decided",
    EventTypes.AUDIT_REPORT_VIEWED: "Audit History Viewed",
    EventTypes.COHORT_CREATED: "Course Cohort Created",
    EventTypes.OPEN_BADGE_ISSUED: "Open Badge Issued",
    EventTypes.OPEN_BADGE_REVOKED: "Open Badge Revoked",
    EventTypes.OPEN_BADGE_SETTINGS_CHANGED: "Open Badge Settings Changed",
    EventTypes.OPEN_BADGE_KEY_ROTATED: "Open Badge Key Rotated",
    EventTypes.OPEN_BADGE_CONSENT_CHANGED: "Open Badge Name Sharing Changed",
}


def log_activity(
    db: Session,
    event_type: str,
    actor_id: int = None,
    target_type: str = None,
    target_id: int = None,
    target_label: str = None,
    detail: dict = None,
    ip_address: str = None,
    commit: bool = True,
):
    """Log an activity event to the database."""
    try:
        event = ActivityEvent(
            event_type=event_type,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            target_label=target_label,
            detail=json.dumps(detail) if detail else None,
            ip_address=ip_address,
        )
        db.add(event)
        if commit:
            db.commit()
    except Exception as e:
        logger.warning(f"Failed to log activity event {event_type}: {e}")
        if commit:
            try:
                db.rollback()
            except Exception:
                pass



