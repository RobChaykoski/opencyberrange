# Roles and admin

## Purpose

Control who can do what. The platform combines role-based access control with
policy attributes (tenant, ownership, course scope, consent, sensitivity) and
keeps an auditable record of administrative actions.

## Code map

| Concern | Location |
|---|---|
| Permission catalogue | `platform/backend/app/security/permissions.py` |
| Dependencies | `platform/backend/app/security/dependencies.py` |
| RBAC service | `platform/backend/app/services/rbac.py` |
| Authorization service | `platform/backend/app/services/authorization.py` |
| Access matrix | `platform/backend/app/services/access_matrix.py` |
| Security admin router | `platform/backend/app/routers/security_admin.py` |
| Admin users | `platform/backend/app/routers/admin.py` |
| Audit and impersonation | `platform/backend/app/routers/audit.py`, `services/audit.py` |
| Route audit | `platform/backend/app/security/route_audit.py` |

## Roles

The seeded roles include `student`, `instructor`, `admin`, `institution_admin`,
`auditor`, `privacy_officer`, `mentor`, `teaching_assistant`, and
`service_account`. The exact permission grants are in the RBAC matrix, not in
this page. Always read the matrix or the permission catalogue before adding a
route.

Tenant scopes:

| Scope | Meaning |
|---|---|
| global | platform admin only |
| institution | confined to `institution_id` |
| shared | explicit share or employer view |
| explicit | service identity with explicit grants |

## API surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/admin/users` | user list; supports pagination and search |
| POST | `/api/admin/users/create` | create an account |
| POST | `/api/admin/users/approve` | approve pending accounts |
| PUT/DELETE | `/api/admin/users/{id}` | update or delete |
| POST | `/api/admin/users/{id}/reset-password` | reset without revealing the password |
| POST | `/api/admin/users/{id}/force-logout` | revoke sessions |
| POST | `/api/admin/users/{id}/mfa/reset` | reset MFA |
| GET | `/api/admin/security/rbac/matrix` | role/permission matrix |
| GET | `/api/admin/security/rbac/permissions` | permission catalogue |
| PUT | `/api/admin/security/rbac/roles/{role}/permissions` | change grants |
| POST | `/api/admin/security/rbac/users/{id}/roles` | assign a role |
| GET/POST | `/api/admin/security/break-glass` | time-boxed elevated access |
| GET | `/api/admin/security/events` | security event query |
| POST | `/api/admin/impersonate/launch` | audited impersonation |

## Behaviour that matters

- **Server-side authority.** Role and permission come from the database, never
  from a client header or a JWT claim alone.
- **Tenant from the session.** The session's institution is the boundary. A
  platform admin is the only cross-tenant role, and private data still requires
  break-glass.
- **Break-glass is time-boxed and reviewed.** It does not silently widen a role.
- **Impersonation is explicit and audited.** Exit restores the original session.
- **Route audit.** `OCR_AUTHZ_STRICT=1` fails startup if a protected route is
  missing an auth or permission dependency.
- **Least privilege.** Deny by default; grant the narrow permission, not the
  broad role.

## Persistent state

| Store | Data |
|---|---|
| `users` | role, `is_admin`, institution, active/approved/locked |
| RBAC tables | role definitions and permission grants |
| `security_events` | RBAC changes, admin actions, break-glass, impersonation |
| `activity_events` | administrative activity history |
| Settings change sets | ticket/reason encrypted; secret values redacted |

## Fixtures and tests

- First admin: setup wizard.
- Demo instructor and students: `seed_demo_class.py`.
- Institution admin tests create their own rows.
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_authorization_matrix.py tests/test_access_matrix.py \
  tests/test_authorization_service.py tests/test_admin_users.py \
  tests/test_institution_admin.py tests/test_tenant_rls.py \
  tests/test_route_authorization.py -q
```

## Extension checklist

- Add a permission to the catalogue before using it.
- Add the dependency to the route; never check the role inline.
- Add a tenant-scope test.
- Add a security event for a privileged action.
- Update the RBAC matrix with `python scripts/generate-rbac-matrix.py`.
- Add the route to the access-matrix test.

## Related

- [RBAC/PBAC](../../../../docs/RBAC-PBAC.md)
- [Authorization service](../../../../docs/AUTHORIZATION-SERVICE.md)
- [Security events](../../../../docs/SECURITY-EVENTS.md)
- [Tenant isolation status](../../../../docs/TENANT-ISOLATION-STATUS.md)
