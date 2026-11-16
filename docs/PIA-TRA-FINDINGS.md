# PIA / TRA findings and status

This is the engineering evidence register for the privacy impact assessment
(PIA) and threat/risk assessment (TRA) findings. It distinguishes product
controls from deployment obligations. A **Completed** item has code, tests, and
documentation in this repository. **Partial** means the core control exists but
a named migration or operational step remains. **Planned** means no enforceable
control is present yet.

Last reviewed: 2026-11-16.

## PIA findings

| Finding | Status | Evidence | Remaining work |
|---|---|---|---|
| Consent Management | **Completed** | `app/consent/` registry, state, grant/revoke service, central middleware, learner UI, grant/revoke security events | Institutional consent text is a deployment choice |
| Consent Audit Log | **Completed** | `consent_events`, `consent_audits`, suppression ledger, verification jobs, `/api/consent/admin/*`, `tests/test_consent_revocation.py` | Legal hold duration is institutional |
| Data Classification | **Completed** | `docs/DATA-CLASSIFICATION.md`, `docs/DATA-LABELS.md`, custom levels, path classification, admin policy endpoint, export middleware | Institution must map its own scheme |
| Retention Policies | **Partial** | `docs/RETENTION-POLICIES.md`, backup retention setting, consent suppression, event retention setting | Automated purge jobs for every legacy table are not complete; several schedules are operator-run |
| Export Auditing | **Completed** | `X-Data-*` headers, `export_metadata`, `export.allowed` / `export.denied` security events, `ReportExport` manifest, `tests/test_data_label_policy.py` | External SIEM export is deployment-specific |
| RBAC | **Completed** | `permissions.yaml`, RBAC tables, Authorization Service, tenant/owner/consent checks, admin RBAC API, `tests/test_authorization_service.py` | Institution-specific role names can be added through extra roles |

## TRA findings

| Finding | Status | Evidence | Remaining work |
|---|---|---|---|
| RBAC | **Completed** | See PIA RBAC row; deny-by-default, auditor read-only, private data never role-granted | Periodic access review is institutional |
| MFA | **Completed** | TOTP enrolment, recovery codes, login enforcement, break-glass MFA requirement, `tests/test_auth_security.py` | Institution must enforce enrolment policy |
| Audit Logging | **Completed** | Append-only `security_events` with forced PostgreSQL RLS, admin-action mirror, sign-in/consent/export/RBAC events, admin query API | Retention archive is operator-run |
| Institution Boundaries | **Partial** | `User.institution_id`, tenant-aware Authorization Service, cross-tenant denial tests, tenant-scoped RLS on security events | Legacy tables lack `institution_id` and are not all migrated to the service; full table-wide RLS is deferred |
| Container Hardening | **Completed** | Docker isolation, default-deny lab egress, read-only/limited runtime settings, integrity checks; see `docs/HARDENING-2026-11.md` | Host kernel hardening is deployment-specific |
| WireGuard Lifecycle Controls | **Completed** | Peer register/resync/remove audit actions, encrypted keys, firewall ensure, stale-peer cleanup; see `docs/DEPLOYMENT-RUNBOOK.md` | Key rotation cadence is institutional |

## Additional threat-model controls

| Threat | Control | Status | Evidence |
|---|---|---|---|
| Horizontal privilege escalation (student reads another student) | Owner check after RBAC; 404 on foreign record; owner/non-owner tests | **Completed** for profile, portfolio, report snapshot, Cyber DNA snapshot, session, consent, and transcript surfaces | `authorization.require_owner`, `tests/test_horizontal_privilege.py` |
| Vertical privilege escalation (student obtains faculty permissions) | Server-loaded roles, no client role claims, route audit, permission catalog review | **Completed** | `get_current_user`, `route_audit.py`, `review_permissions.py`, `test_jwt_role_tampering_cannot_promote_a_student` |
| Institution administrator abuse | `institution_admin` is not system `admin`; tenant check; scoped course access | **Partial** | Authorization Service; legacy admin routes still use platform-admin checks and tenant migration is incomplete |
| Permission drift | Authoritative `permissions.yaml`, sensitivity metadata, release check, startup validation | **Completed** | `app/security/permissions.yaml`, `python -m app.scripts.review_permissions --check` |
| Portfolio sharing abuse | 30-day default, hashed token, revocation, single-use/max uses, consent gate, audit events | **Completed** | `app/services/portfolio_shares.py`, `tests/test_portfolio_shares.py` |
| Cyber DNA overexposure | Separate `competency.view`, `career_affinity.view.self`, `recommendation.view.self`; faculty do not receive private signals | **Completed** | Permission catalog, Cyber DNA dependencies, privacy tests |
| Broken authorization middleware | Startup route audit; optional strict fail-fast | **Completed** | `authorization_strict_startup`, `tests/test_route_authorization.py` |
| Consent bypass | Consent evaluated in the Authorization Service before break-glass | **Completed** | `test_revoked_dna_consent_blocks_even_a_break_glass_attempt` |
| Confused deputy / service-account abuse | `service_account` role with no default grants; explicit extra roles | **Partial** | Role exists; scoped service API keys and rotation workflow are not yet implemented |
| Audit log tampering | Forced RLS, no UPDATE/DELETE policies, no delete API, non-superuser runtime role requirement | **Completed** | `test_rls_denies_update_delete_and_scopes_tenants`, `docs/SECURITY-EVENTS.md` |
| Break-glass abuse | Reason, MFA, optional second approval, max lifetime, scope limit, critical use event, post-use review | **Completed** | `app/services/authorization.py`, `tests/test_authorization_service.py`, `docs/AUTHORIZATION-SERVICE.md` |
| Row-level security | Forced RLS on the security event store; tenant GUCs; append-only | **Partial** | Complete on `security_events`; table-wide rollout depends on adding `institution_id` to legacy tenant-owned tables |
| Tenant middleware | Server-loaded tenant context, RLS GUC binding, request cleanup | **Completed** | `app/security/tenant.py`, `get_current_user`, `database.py` session hooks |
| Permission review automation | `review_permissions --check` and startup catalog validation | **Completed** | `app/scripts/review_permissions.py`, `validate_catalog()` |

## Deployment obligations

The product cannot complete these for an institution:

1. Approve the PIA and the institution-specific retention schedule.
2. Run the database as a non-superuser role so PostgreSQL RLS is effective.
3. Decide whether break-glass requires second-operator approval, and review
   every use within the institution's incident process.
4. Map the institution's own data-label scheme and region rules.
5. Archive security events to an immutable external store if the institution's
   retention period exceeds the database window.
6. Complete a third-party penetration test and a signed VPAT where required.

## Verification commands

```bash
cd platform/backend
python -m app.scripts.review_permissions --check
python -m pytest tests/test_authorization_service.py \
  tests/test_security_events.py tests/test_horizontal_privilege.py \
  tests/test_portfolio_shares.py tests/test_route_authorization.py -q
```

A full backend run with `TEST_DATABASE_URL` pointed at a scratch PostgreSQL
database covers the migration and integration paths.
