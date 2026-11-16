# RBAC + policy-based authorization

OpenCyberRange keeps role checks for existing routes and routes every new or
high-risk surface through one Authorization Service. A role answers "what kind
of work may this user do?"; the service answers "may this user do it to this
record, in this tenant, with this learner's consent?".

## Implemented

`app/security/` and `app/services/authorization.py` provide:

- `permissions.yaml` — authoritative permission catalog with description,
  category, sensitivity, scope, read-only status, break-glass eligibility, and
  default role grants.
- `permissions.py` — typed accessors and startup validation for that catalog.
- `models/security.py` + `services/rbac.py` — persisted roles, permissions,
  role grants, and expiring extra user roles.
- `services/authorization.py` — deny-by-default evaluation of RBAC, tenant,
  owner/share scope, consent, and break-glass.
- `policy.py` / `dependencies.py` — the historical `authorize()` /
  `require_permission()` FastAPI seam, now backed by the service.
- `route_audit.py` — startup audit that reports protected routes without an
  auth/permission dependency. Enterprise deployments can make it fail closed.

See `docs/AUTHORIZATION-SERVICE.md` for the full contract and
`docs/SECURITY-EVENTS.md` for the evidence trail.

Roles seeded today:

| Role | Core grants | Tenant scope |
|---|---|---|
| `student` | self profile, labs, own DNA/GPS/portfolio, own consent, export/deletion requests | institution |
| `instructor` | course-scoped progress, class analytics, competency/achievement views, reports | institution |
| `teaching_assistant` | assigned-course progress, grading, feedback | institution |
| `mentor` | assigned-learner progress and competencies | institution |
| `institution_admin` | institution, faculty, enrolment, program reporting; confined to its `institution_id` | institution |
| `privacy_officer` | consent management, revocation execution, privacy audit, deletion approval | institution |
| `auditor` | read-only audit, consent status, security events, reports | institution |
| `employer` / `recruiter` | only explicitly shared portfolio/certificate/profile | shared |
| `admin` | platform operations and the only cross-tenant role; **not** private AI/DNA/GPS data by default | global |
| `service_account` | no default grants; explicit extra roles only | explicit |

The reviewable **RBAC and PBAC matrix** is generated from this catalog in
[`RBAC-PBAC-MATRIX.md`](RBAC-PBAC-MATRIX.md). The Security Center renders the
same matrix from the live RBAC tables under **Security center → Access matrix**,
so administrator edits are visible without regenerating the document. Run
`python scripts/generate-rbac-matrix.py --check` in review; CI fails when the
catalog and the document drift.

Policy rules:

1. Unknown permission or role → deny.
2. Roles are loaded from the database, never from a JWT claim or request field.
3. Private permission → owner, explicit share, or break-glass grant; never a
   role grant.
4. Self-scoped permission must target the caller.
5. Shared permission requires `shared=True` from a verified live share.
6. Staff-scoped permission requires an owned course in the actor's tenant.
7. Auditor may only use read permissions.
8. Non-system roles are confined to their `institution_id`.
9. A revoked learner consent blocks derived-data access, including break-glass.
10. Break-glass is time-bound, reasoned, MFA-gated, optionally second-approved,
    and never changes the role.

## Consent is a separate layer

Authorization answers "may this user do this to this record?". Consent answers
"may this learner's derived data be processed at all?". The service evaluates
consent before break-glass. Do not fold the two together. A learner who grants
Cyber DNA consent still cannot read another learner's DNA, and an instructor
with course scope still cannot read a learner's private AI transcript.

Field-level output follows the same rule: career affinity is never included in
a response when Cyber GPS/DNA consent is missing, and portfolio fields are
omitted when portfolio sharing is revoked. The field must not leave the API and
then be hidden by the client.

## Deliberately deferred

The full multi-tenant academic hierarchy (Institution, Program, ProgramCourse,
CourseModule, Cohort) is not migrated yet. The Authorization Service is
designed so those additions change inputs, not route code:

- `resource_user_id` is already the learner profile owner.
- `course_id` is already the teaching scope.
- `shared=True` must come from a verified share token.
- `institution_id` is already checked for learner records and courses; legacy
  tables still need the column and a migration to the service.

Until a legacy router is migrated, it keeps
`get_current_admin_user`, `get_current_instructor_user`, or
`get_current_active_user`. New privacy surfaces must use `require_permission()`.

## Tests

`tests/test_security_policy.py` verifies catalog consistency, self isolation,
course ownership, read-only auditor, shared-access requirements,
privacy-officer execution, and admin denial for private transcripts.
`tests/test_authorization_service.py` verifies RBAC-table seeding, tenant
boundaries, consent-over-break-glass, MFA/approval, and owner helpers.
`tests/test_route_authorization.py` verifies every protected route declares a
dependency.
