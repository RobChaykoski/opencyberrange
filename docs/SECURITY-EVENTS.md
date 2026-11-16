# Security event store

The security event store is the platform's queryable evidence trail for
security, audit, and privacy actions. It is append-only at the database layer,
not only by application convention.

## Event families

| Category | What it answers | Examples |
|---|---|---|
| `security` | Who tried to authenticate, escalate, or reach a denied action? | `auth.login_failed`, `auth.mfa_failed`, `authz.denied`, `http.denied`, `break_glass.used` |
| `audit` | Who changed a role, setting, record, or configuration? | `admin.action`, `rbac.permissions_changed`, `export.allowed`, `security.events_read` |
| `privacy` | Who accessed, exported, revoked, or erased personal data? | `consent.revoked`, `consent.granted`, `portfolio.share_used`, `privacy.exported` |

Severity is `info`, `notice`, `warning`, or `critical`. Outcome is `success`,
`failure`, `denied`, or `error`.

## Sensitive-action coverage

Coverage uses two layers:

1. **Explicit events** at high-value call sites: sign-in success and failure,
   MFA failure, password change, registration, consent grant/revoke, export
   allow/deny, RBAC changes, break-glass request/approval/use/revoke, portfolio
   share creation/use/revocation, and every `log_admin_action` call.
2. **HTTP fallback** for sensitive paths that do not have a richer explicit
   event. It skips `/api/health`, `/api/version`, `/api/auth/me`, and
   non-sensitive reads. Explicit call sites set a request marker so the fallback
   does not duplicate them.

Turning on `security_event_http_logging` is the default. A high-volume
deployment with an external pipeline can turn it off without losing explicit
events.

## Append-only row-level security

The table is `security_events`. PostgreSQL RLS is enabled and forced:

- `INSERT` is allowed.
- `SELECT` is limited to the actor's `institution_id`, platform-wide rows with
  a null institution, or all rows when the `ocr.system_admin` GUC is true.
- `UPDATE` and `DELETE` have `USING (false)` policies, so they affect zero rows
  even for the table owner.
- `UPDATE`/`DELETE` are also revoked from `PUBLIC`.

The application installs the policies at startup with
`security_events.ensure_rls()` and the Alembic revision installs them for an
existing database.

**Runtime role requirement:** the application must connect as a non-superuser
role. PostgreSQL superusers bypass RLS. Startup logs a warning when the runtime
role is a superuser. Tests prove the deny behaviour by switching to a
non-superuser probe role.

## Retention and legal hold

The application role cannot delete events. Retention is an operator action:

1. Export the window to the institution's immutable archive.
2. Delete only through an elevated maintenance role under the institution's
   retention schedule.
3. Record the disposition in the security event store before the archives are
   closed.

The recommended default is 365 days (`security_event_retention_days`). Legal
hold overrides the default. See `docs/RETENTION-POLICIES.md`.

## Alerts

The scheduler runs a five-minute security-operations pass:

1. Expire stale break-glass grants (`break_glass.expired`).
2. Scan the rolling alert window.
3. Write deduplicated `security.alert` events.

Alert rules:

| Rule | Default | Severity |
|---|---|---|
| Any `break_glass.used` | always | critical |
| Repeated `auth.login_failed`, `auth.mfa_failed`, `authz.denied`, `http.denied`, `service_identity.auth_failed` | 5 in 15 minutes per actor/IP | warning |
| Repeated `export.denied` | 5 in 15 minutes per actor/IP | critical |

Settings: `security_alert_enabled`, `security_alert_window_minutes`, and
`security_alert_threshold`. Alerts appear in the admin **Security** center and
can be routed to the institution's SIEM from the event store.

## Administrator console

The admin **Security** tab shows:

- event summary cards and a filterable event table;
- break-glass request, approval, revocation, and post-use review;
- service-identity creation and revocation (the token is shown once); and
- the RBAC role catalog and permission counts.

## Administrator API

All routes require `security.events.view` except role editing, which requires
`rbac.manage`.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/admin/security/events` | Filter by category, type, severity, outcome, actor, institution, time, or text |
| `GET` | `/api/admin/security/events/summary` | Counts by category, severity, outcome, and top event types |
| `GET` | `/api/admin/security/events/{id}` | One event |
| `GET` | `/api/admin/security/rbac/roles` | Role catalog with effective grants |
| `GET` | `/api/admin/security/rbac/permissions` | Reviewed permission catalog |
| `PUT` | `/api/admin/security/rbac/roles/{role}/permissions` | Replace one role's grants |
| `GET` | `/api/admin/security/rbac/users/{id}` | Effective roles and permissions |
| `POST` | `/api/admin/security/rbac/users/{id}/roles` | Grant an expiring extra role |
| `DELETE` | `/api/admin/security/rbac/users/{id}/roles/{role}` | Revoke an extra role |
| `POST` | `/api/admin/security/rbac/check` | Explain one decision |
| `GET/POST` | `/api/admin/security/break-glass` | List or request emergency access |
| `POST` | `/api/admin/security/break-glass/{id}/approve` | Second-operator approval |
| `POST` | `/api/admin/security/break-glass/{id}/revoke` | Revoke a grant |
| `POST` | `/api/admin/security/break-glass/{id}/review` | Close the post-use review |
| `GET/POST` | `/api/admin/security/service-identities` | List or create scoped non-human credentials |
| `DELETE` | `/api/admin/security/service-identities/{id}` | Revoke a service credential |

Reading the store is itself an audit event (`security.events_read`).

## Settings

| Setting | Default | Purpose |
|---|---|---|
| `security_event_store_enabled` | `true` | Master switch for new writes |
| `security_event_http_logging` | `true` | HTTP fallback coverage |
| `security_event_retention_days` | `365` | Recommended retention |
| `security_alert_enabled` | `true` | Run the threshold alert scan |
| `security_alert_window_minutes` | `15` | Alert rolling window |
| `security_alert_threshold` | `5` | Events per actor/IP before an alert |
| `authorization_strict_startup` | `false` | Refuse startup when a protected route lacks auth |

## Tests

`tests/test_security_events.py` covers redaction, actor/category capture,
admin queries, non-admin denial, admin-action mirroring, tenant-scoped SELECT,
and zero-row UPDATE/DELETE under forced RLS.
