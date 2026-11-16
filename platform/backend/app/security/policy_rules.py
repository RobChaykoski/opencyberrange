"""Reviewed PBAC policy dimensions shown in the access matrix.

These strings are documentation for operators. Enforcement lives in the
Authorization Service, tenant helpers, and the routers; the matrix generator
and the Security Center both read this list so the explanation cannot drift
from the catalog review.
"""

from __future__ import annotations

POLICY_RULES: tuple[dict[str, str], ...] = (
    {
        "id": "default_deny",
        "label": "Default deny",
        "rule": "An unknown permission, unknown role, or missing dependency is denied.",
        "enforced_by": "app.services.authorization.AuthorizationService",
    },
    {
        "id": "server_authority",
        "label": "Server-resolved roles",
        "rule": "Roles come from the RBAC tables, never from a JWT claim or request body.",
        "enforced_by": "app.services.rbac.effective_roles",
    },
    {
        "id": "tenant_boundary",
        "label": "Tenant boundary",
        "rule": "Every role is confined to its reviewed tenant scope; only admin is cross-tenant.",
        "enforced_by": "app.security.tenant + PostgreSQL RLS",
    },
    {
        "id": "self_scope",
        "label": "Self scope",
        "rule": "A self-scoped permission is allowed only when the target is the caller.",
        "enforced_by": "authorize(resource_user_id=...)",
    },
    {
        "id": "shared_scope",
        "label": "Explicit share",
        "rule": "A shared permission requires shared=True from a verified, live share token.",
        "enforced_by": "portfolio/certificate share verification",
    },
    {
        "id": "course_scope",
        "label": "Course scope",
        "rule": "A course-scoped permission requires an owned or assigned course in the actor's tenant.",
        "enforced_by": "authorize(course_id=...)",
    },
    {
        "id": "private_data",
        "label": "Private derived data",
        "rule": "Private DNA, GPS, transcript, and AI data require owner, share, or break-glass; never a role grant.",
        "enforced_by": "SENSITIVE_PRIVATE_PERMISSIONS",
    },
    {
        "id": "consent_gate",
        "label": "Consent gate",
        "rule": "Revoked learner consent blocks derived-data processing, including break-glass access.",
        "enforced_by": "consent middleware + AuthorizationService",
    },
    {
        "id": "auditor_readonly",
        "label": "Auditor read-only",
        "rule": "The auditor role may use read-only permissions only.",
        "enforced_by": "READ_ONLY_PERMISSIONS",
    },
    {
        "id": "break_glass",
        "label": "Break-glass controls",
        "rule": "Emergency access is time-bound, MFA-gated, reasoned, optionally approved, reviewed, and never changes the role.",
        "enforced_by": "app.services.authorization + break-glass service",
    },
    {
        "id": "export_ceiling",
        "label": "Export ceiling",
        "rule": "Export requires export.data plus the rank permission and the actor's institution role/region ceiling; Restricted is blocked by default.",
        "enforced_by": "export authorization + data labels",
    },
    {
        "id": "service_identity",
        "label": "Service identity",
        "rule": "A non-human identity has no password login and only its explicit, expiring scopes.",
        "enforced_by": "app.services.service_identities",
    },
)
