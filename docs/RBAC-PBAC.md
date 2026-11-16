# RBAC + policy-based authorization

OpenCyberRange keeps role checks for existing routes and adds a policy seam for
new privacy-sensitive surfaces. A role answers "what kind of work may this user
do?"; a policy answers "may this user do it to this record?".

## Implemented

`app/security/` provides:

- `permissions.py` — atomic permission catalog, role grants, self/shared/scoped
  permission sets, read-only auditor set, and sensitive-private set.
- `policy.py` — deny-by-default `authorize()` / `require_allowed()` with
  resource-owner, course-scope, and explicit-share checks.
- `dependencies.py` — `require_permission("...")` for FastAPI routes.

Roles seeded today (existing `User.role` values keep working):

| Role | Core grants |
|---|---|
| `student` | self profile, labs, own DNA/GPS/portfolio, own consent, export/deletion requests |
| `instructor` | course-scoped progress, class analytics, competency/achievement views, reports |
| `teaching_assistant` | assigned-course progress, grading, feedback |
| `mentor` | assigned-learner progress and competencies |
| `institution_admin` | institution, faculty, enrolment, program reporting |
| `privacy_officer` | consent management, revocation execution, privacy audit, deletion approval |
| `auditor` | read-only audit, consent status, reports |
| `employer` / `recruiter` | only explicitly shared portfolio/certificate/profile |
| `admin` | platform operations; **not** private AI/DNA/GPS data by default |

Policy rules:

1. Unknown permission or role → deny.
2. Self-scoped permission must target the caller.
3. Shared permission requires `shared=True` from a verified live share, never a
   query parameter alone.
4. Staff-scoped permission requires an owned course; missing or foreign course
   → deny.
5. Auditor may only use read permissions.
6. Sensitive private data requires the owner or an explicit share; no role
   receives it by default, including `admin`.

The consent admin endpoints already use the policy dependency:
`privacy.audit.view` for revocation lists/metrics and
`privacy.revocation.execute` for running purges or the suppression sweep.

## Deliberately deferred

The full multi-tenant academic hierarchy (Institution, Program, ProgramCourse,
CourseModule, Cohort, scoped `UserRole`, break-glass access, employer share
tokens) is specified but not migrated yet. The policy call sites are designed
so those additions change `authorize()` inputs, not route code:

- `resource_user_id` becomes the learner profile owner.
- `course_id` becomes the course/cohort scope from `UserRole`.
- `shared=True` becomes a verified `PortfolioShare` token.
- Institution scoping is checked in the same function before the role grant.

Until then, existing routers keep `get_current_admin_user`,
`get_current_instructor_user`, and `get_current_active_user`. New privacy
surfaces must use `require_permission()`.

## Tests

`tests/test_security_policy.py` verifies catalog consistency, self isolation,
course ownership, read-only auditor, shared-access requirements, privacy-officer
execution, and admin denial for private transcripts. The consent tests verify
the route-level 403s and the auditor/privacy-officer split.
