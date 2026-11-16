"""Permission catalog and role grants.

This is the PBAC seam for the platform. Existing routers keep their current
role dependencies; new privacy-sensitive surfaces call :func:`authorize` with a
permission and, where relevant, a resource owner or course scope. The catalog
is intentionally small and atomic so it can grow into the full multi-tenant
matrix without changing call sites.
"""

from __future__ import annotations

from dataclasses import dataclass, field


READ_ONLY_PERMISSIONS = frozenset(
    {
        "audit.view",
        "consent.view",
        "privacy.audit.view",
        "reports.view",
        "class.analytics.view",
        "student.progress.view",
        "competency.view",
        "achievement.view",
    }
)

SELF_PERMISSIONS = frozenset(
    {
        "profile.view.self",
        "profile.edit.self",
        "profile.delete.self",
        "dna.view.self",
        "dna.export.self",
        "dna.delete.self",
        "gps.view.self",
        "gps.generate",
        "gps.disable",
        "portfolio.view.self",
        "portfolio.export.self",
        "portfolio.share",
        "coach.use",
        "consent.manage.self",
        "consent.view.self",
        "export.request.self",
        "deletion.request.self",
        "transcript.view.self",
    }
)

SHARED_PERMISSIONS = frozenset(
    {
        "portfolio.view.shared",
        "certificate.view.shared",
        "shared_profile.view",
    }
)

# Staff permissions whose policy requires an owned course/cohort scope.
SCOPED_PERMISSIONS = frozenset(
    {
        "student.progress.view",
        "class.analytics.view",
        "competency.view",
        "achievement.view",
        "assignment.grade",
        "feedback.create",
        "reports.view",
        "reports.export",
    }
)

SENSITIVE_PRIVATE_PERMISSIONS = frozenset(
    {
        "coach.transcript.view",
        "dna.view.private",
        "gps.view.private",
        "privacy.consent.read",
    }
)

PERMISSION_CATALOG: dict[str, str] = {
    # Identity
    "profile.view.self": "View own profile",
    "profile.edit.self": "Edit own profile",
    "profile.delete.self": "Request deletion of own account",
    "user.manage": "Manage platform users",
    "role.assign": "Assign roles and scopes",
    # Learning
    "lab.view": "View exercises",
    "lab.start": "Start an exercise",
    "lab.submit": "Submit exercise work",
    "workbook.view": "View workbook content",
    "transcript.view.self": "View own transcript",
    "course.view": "View courses",
    "course.create": "Create courses",
    "course.edit": "Edit courses",
    "course.archive": "Archive courses",
    "assignment.manage": "Manage assignments",
    "assignment.grade": "Grade assignments",
    "feedback.create": "Create learner feedback",
    "student.progress.view": "View assigned learners' progress",
    "class.analytics.view": "View class analytics",
    # Cyber DNA / GPS
    "dna.view.self": "View own Cyber DNA",
    "dna.export.self": "Export own Cyber DNA",
    "dna.delete.self": "Revoke own Cyber DNA processing",
    "dna.view.student": "View an assigned learner's competencies",
    "dna.view.private": "View private DNA notes",
    "dna.admin": "Administer DNA configuration",
    "gps.view.self": "View own Cyber GPS",
    "gps.generate": "Generate own Cyber GPS view",
    "gps.disable": "Disable own Cyber GPS",
    "gps.view.student": "View an assigned learner's GPS direction",
    "gps.view.private": "View private GPS notes",
    "gps.admin": "Administer GPS configuration",
    "competency.view": "View competencies for assigned learners",
    "achievement.view": "View achievements for assigned learners",
    # Portfolio / sharing
    "portfolio.view.self": "View own portfolio",
    "portfolio.export.self": "Export own portfolio",
    "portfolio.share": "Create or revoke own share links",
    "portfolio.view.shared": "View a portfolio shared by a learner",
    "portfolio.admin": "Administer portfolio templates",
    "certificate.view.shared": "Verify a shared certificate",
    "shared_profile.view": "View a explicitly shared profile",
    # AI
    "coach.use": "Use the AI coach",
    "coach.transcript.view": "View AI conversations",
    "coach.admin": "Administer AI coach settings",
    "coach.moderate": "Moderate AI coach content",
    # Privacy / reporting
    "consent.manage.self": "Manage own consent",
    "consent.view.self": "View own consent state",
    "export.request.self": "Request an export of own data",
    "consent.view": "View aggregate consent status",
    "consent.manage": "Manage another learner's consent",
    "privacy.audit.view": "View privacy and revocation audit records",
    "privacy.revocation.execute": "Execute purge and verification jobs",
    "deletion.request.self": "Request own deletion",
    "deletion.approve": "Approve a deletion request",
    "audit.view": "View audit logs",
    "reports.view": "View reports",
    "reports.export": "Export reports",
    "analytics.view": "View analytics",
    # Administration
    "institution.manage": "Manage institutions and programs",
    "faculty.manage": "Manage faculty assignments",
    "student.enrollment.manage": "Manage learner enrolment",
    "program.reporting.view": "View program-level reports",
    "platform.admin": "Platform administration",
    "readonly": "Read-only access",
}

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "student": frozenset(
        {
            "profile.view.self",
            "profile.edit.self",
            "profile.delete.self",
            "lab.view",
            "lab.start",
            "lab.submit",
            "workbook.view",
            "transcript.view.self",
            "dna.view.self",
            "dna.export.self",
            "dna.delete.self",
            "gps.view.self",
            "gps.generate",
            "gps.disable",
            "portfolio.view.self",
            "portfolio.export.self",
            "portfolio.share",
            "coach.use",
            "consent.manage.self",
            "consent.view.self",
            "export.request.self",
            "deletion.request.self",
        }
    ),
    "instructor": frozenset(
        {
            "profile.view.self",
            "profile.edit.self",
            "lab.view",
            "lab.start",
            "lab.submit",
            "workbook.view",
            "course.view",
            "course.create",
            "course.edit",
            "course.archive",
            "assignment.manage",
            "assignment.grade",
            "feedback.create",
            "student.progress.view",
            "class.analytics.view",
            "competency.view",
            "achievement.view",
            "reports.view",
            "reports.export",
            "consent.view",
        }
    ),
    "teaching_assistant": frozenset(
        {
            "profile.view.self",
            "lab.view",
            "student.progress.view",
            "assignment.grade",
            "feedback.create",
            "competency.view",
        }
    ),
    "mentor": frozenset(
        {
            "profile.view.self",
            "student.progress.view",
            "competency.view",
            "achievement.view",
        }
    ),
    "institution_admin": frozenset(
        {
            "profile.view.self",
            "institution.manage",
            "faculty.manage",
            "student.enrollment.manage",
            "program.reporting.view",
            "class.analytics.view",
            "reports.view",
            "reports.export",
            "analytics.view",
            "consent.view",
            "audit.view",
        }
    ),
    "privacy_officer": frozenset(
        {
            "profile.view.self",
            "consent.view",
            "consent.manage",
            "privacy.audit.view",
            "privacy.revocation.execute",
            "deletion.approve",
            "audit.view",
            "reports.view",
            "readonly",
        }
    ),
    "auditor": frozenset(
        {
            "profile.view.self",
            "consent.view",
            "privacy.audit.view",
            "audit.view",
            "reports.view",
            "readonly",
        }
    ),
    "employer": frozenset(
        {
            "portfolio.view.shared",
            "certificate.view.shared",
            "shared_profile.view",
        }
    ),
    "recruiter": frozenset(
        {
            "portfolio.view.shared",
            "certificate.view.shared",
            "shared_profile.view",
        }
    ),
    "admin": frozenset(
        set(PERMISSION_CATALOG)
        - SENSITIVE_PRIVATE_PERMISSIONS
    ),
}

SEEDED_ROLES = tuple(ROLE_PERMISSIONS)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    permission: str
    reason: str
    role: str
    scope: dict = field(default_factory=dict)


def permissions_for_role(role: str) -> frozenset[str]:
    return ROLE_PERMISSIONS.get((role or "student").strip().lower(), frozenset())
