# Authorization Service

OpenCyberRange has one server-side decision point for new and high-risk
surfaces: `app.services.authorization.AuthorizationService`. A route no longer
compares role strings to decide whether a record may leave the API.

The service joins four inputs:

```
RBAC (server-loaded role)
  + tenant boundary (resource.tenantId == actor.tenantId)
  + consent (learner decision)
  + break-glass (time-bound exception)
= allow or deny
```

Every denial on a high-sensitivity permission and every break-glass use is
written to the append-only security event store.

## Roles are never trusted from the client

`get_current_user()` decodes the JWT only to find the account subject. It then
loads the `User` row and uses `User.role` and `User.institution_id` from the
database. A role claim in a token, request body, query parameter, or
`X-Debug-Role` header has no effect. Impersonation tokens are server-issued and
remain read-only through the existing middleware.

## RBAC tables

`permissions.yaml` is the reviewed baseline. It is authoritative for the
permission catalog, sensitivity, scope, read-only status, break-glass
eligibility, and default role grants.

At startup (`rbac.seed`) the catalog is copied into:

| Table | Purpose |
|---|---|
| `rbac_roles` | Role key, label, description, rank |
| `rbac_permissions` | Permission key, description, category, sensitivity |
| `rbac_role_permissions` | Explicit role grants |
| `rbac_user_roles` | Extra, optionally expiring role assignments |

Seeding is idempotent. An administrator's reviewed changes survive a reboot:
only newly introduced permissions receive their default grants on a later boot.
`User.role` remains the primary role; extra roles are additive and expire.

### Least privilege

- `admin` is the platform administrator and is the only cross-tenant role.
- `institution_admin` is **not** a system administrator. Its course and record
  access is confined to its own `institution_id`.
- `privacy_officer` manages consent, revocation, privacy audit, and deletion
  approval; it does not automatically receive private data.
- `auditor` is read-only.
- Private permissions (`dna.view.private`, `gps.view.private`,
  `coach.transcript.view`) are granted to **no role**, including `admin`.
  They require the owner, an explicit share, or a break-glass grant.
- Faculty receive `competency.view` and `achievement.view`, never
  `career_affinity.view.self`, `recommendation.view.self`, or private DNA.
- `service_account` exists with no default grants. A service identity must be
  given explicit roles; shared administrator keys are not supported.

### Catalog review

```bash
cd platform/backend
python -m app.scripts.review_permissions --check
```

The check fails when private data becomes role-grantable, faculty accumulate
private learner signals, high-sensitivity permissions lack review metadata, or
a break-glass permission is not actually sensitive.

## Tenant boundary

`User.institution_id` is the tenant key. It is server-loaded and never taken
from a token. The Authorization Service denies a non-system role when the
resource owner's institution differs from the actor's. Course scope derives the
tenant from the course instructor. `tenant_isolation_enabled` defaults to true.

This is a record-level boundary for services that call the Authorization
Service. Full PostgreSQL RLS on every legacy table is not enabled yet because
those tables do not all carry `institution_id`; the security event store is the
first table with forced RLS. See `docs/PIA-TRA-FINDINGS.md` for the remaining
migration work.

## Consent

Consent is evaluated **before** break-glass. A learner who revokes `cyber_dna`,
`cyber_gps`, `ai_coach`, or `portfolio` blocks derived-data access even for a
platform administrator. Emergency access cannot override a consent decision.

Mapping is deliberately narrow:

| Permission prefix | Consent |
|---|---|
| `dna.*`, `career_affinity.*`, `recommendation.*`, `competency.*` | `cyber_dna` |
| `gps.*` | `cyber_gps` |
| `coach.*` | `ai_coach` |
| `portfolio.*` | `portfolio` |

## Owner and share checks

- Self-scoped permissions require `resource_user_id == actor.id`.
- Shared permissions require `shared=True` from a verified live share token, not
  a bare query parameter.
- `authorization.require_owner()` raises **404** for a foreign record so a
  guessed identifier cannot reveal whether the record exists.
- Course-scoped staff permissions require an owned course in the actor's tenant.
- Instructor learner-enumeration is limited to learners already enrolled in one
  of that instructor's courses.

See `tests/test_horizontal_privilege.py` for owner/non-owner regression tests.

## Break-glass access

Break-glass is an emergency exception, not a role.

- **Eligible permissions:** `dna.view.private`, `gps.view.private`,
  `coach.transcript.view`, `export.restricted`, and `audit.view`.
- **Off by default:** `break_glass_enabled=false`.
- **MFA required by default** on the requester and target.
- **Reason** of at least 10 characters and optional incident reference.
- **Maximum lifetime** from `break_glass_max_minutes` (default 60).
- **Second-operator approval** when `break_glass_require_approval=true`.
- **No extension.** Create and review a new grant.
- **Automatic scope:** a grant can be limited to one learner or one course.
- **Use is a `critical` event** with the reference and reason.
- **Post-use review:** `review_status` and a required note close the loop.
- **No consent override:** a revoked learner consent still blocks access.

The Authorization Service checks break-glass only after normal policy denies.
A grant never changes the user's role and never appears as a permission grant.

## Route audit

`app.security.route_audit.audit_routes()` walks the compiled FastAPI routes,
including lazy included routers. It reports protected prefixes
(`/api/admin`, `/api/consent/admin`, `/api/instructor`, `/api/reports`,
`/api/audit`, `/api/profile`, `/api/dna`, `/api/cyber-dna`, `/api/identity`,
`/api/lti`, `/api/setup`, `/api/security`, and sensitive auth routes) that have
no recognized auth or permission dependency.

Startup logs a warning by default. Set `authorization_strict_startup=true` or
`OCR_AUTHZ_STRICT=1` for enterprise deployments that must refuse to start with a
missing dependency. `tests/test_route_authorization.py` asserts the current
route table has zero gaps.

## Migrating a route

Old routes can keep their existing dependencies. A new or high-risk route
should use:

```python
from app.security.dependencies import require_permission

@router.get("/records/{user_id}")
def read_record(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    _decision: PolicyDecision = Depends(require_permission("student.progress.view")),
):
    authorization.require_owner(db, current_user, user_id, resource="record")
    ...
```

`require_permission` automatically passes `user_id`, `student_id`, and
`course_id` path parameters into the decision, so a route cannot drop the
resource scope while keeping the permission check.

## Administrator API

See `docs/SECURITY-EVENTS.md` for the full route list. The same API exposes the
role catalog, user effective permissions, decision explanation, and
break-glass workflow.

## Tests

- `tests/test_authorization_service.py`: catalog review, seed idempotence,
  admin-edit preservation, extra-role expiry, tenant isolation, consent over
  break-glass, MFA/approval/expiry, owner and tenant helpers.
- `tests/test_security_policy.py`: existing self, shared, scoped, auditor, and
  private-data rules.
- `tests/test_route_authorization.py`: every protected route has a dependency.
- `tests/test_horizontal_privilege.py`: owner/non-owner and faculty overreach.
