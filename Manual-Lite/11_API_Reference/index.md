# API reference

This page is generated from the running FastAPI OpenAPI schema. It is the
complete route reference for the platform API. Use the interactive
OpenAPI page only when an administrator has enabled API documentation.

!!! note "Generated page"
    Run `python scripts/generate-api-manual.py` after changing a router or
    schema. The CI check regenerates this page and fails on drift.

## Base URL and versioning

The API is served under `/api` on the same origin as the web interface.
The current platform version is available at `GET /api/version`. The
health probe is `GET /health` and does not require authentication.

## Authentication

1. `POST /api/auth/login` with form fields `username` and `password`.
2. Store the returned access token and refresh token in the client.
3. Send `Authorization: Bearer <access_token>` on protected requests.
4. Rotate the access token with `POST /api/auth/refresh` before it expires.
5. Re-authenticate for sensitive actions with `POST /api/auth/reauth`.

An expired or revoked token returns `401`. A valid token without the
required permission returns `403`. Never place a token in a URL, a log,
a screenshot, or a report.

## Request conventions

- Send JSON with `Content-Type: application/json` unless the endpoint
  documents a form, multipart, or plain-text body.
- Use `Idempotency-Key` only where the endpoint documents it; do not
  assume every write is idempotent.
- Paginated endpoints use `page` and `per_page` when documented. Respect
  the server cap; do not request an unbounded page.
- Tenant and object scope are enforced on the server. A client-supplied
  `institution_id`, role, or owner field is not trusted.

## Response conventions

- Success responses use the documented schema and a `2xx` status.
- Validation failures use `422` with a structured `detail` list.
- Authorization failures use `401` (not signed in) or `403` (not allowed).
- Missing objects use `404`; conflict and state errors use `409`.
- Rate limits use `429`; retry after the documented window.
- Unexpected failures use `500` and must not include a stack trace or secret.

A typical error body is:

```json
{"detail": "Not enough permissions"}
```

A validation error body is:

```json
{"detail": [{"loc": ["body", "field"], "msg": "field required", "type": "missing"}]}
```

## Rate limits and sensitive actions

Authentication, registration, password reset, flag submission, exports,
and administrative changes have stricter limits than ordinary reads.
The exact limit is enforced per route and may use a shared counter across
workers. A `429` means the request was refused, not that the credential
was wrong.

Sensitive actions may also require re-authentication, a written reason,
or an approval. The response can include `X-Reauth-Required`; the SPA
opens the re-authentication dialog instead of silently retrying.

## Permissions and data scope

Authorization is deny-by-default. A route may require a role permission,
an object ownership check, a tenant match, a course enrollment, or an
explicit share. The permission catalogue and matrix are documented in
[RBAC and PBAC](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/RBAC-PBAC.md) and the admin **Security** tab.

Data labels and export rules are documented in
[Data labels](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/DATA-LABELS.md). Private DNA, GPS, and AI data are
owner-only unless an explicit share or break-glass grant exists.

## OpenAPI and interactive docs

- `GET /openapi.json` returns the schema used to build this page.
- `GET /docs` and `GET /redoc` are disabled by default.
- An administrator can enable them with the `enable_api_docs` setting or
  the `ENABLE_API_DOCS=true` environment override for emergency debugging.
- The API schema and this manual are informational; they do not grant
  access to a route.

## Security schemes

- **OAuth2PasswordBearer**: oauth2

## Endpoint index

| Method | Path | Summary | Authentication |
|---|---|---|---|
| `GET` | `/` | Root | Public |
| `GET` | `/api/about` | Get About | OAuth2PasswordBearer |
| `GET` | `/api/about/licences/{name}` | Get Licence | OAuth2PasswordBearer |
| `GET` | `/api/about/sbom/{name}` | Get Sbom | OAuth2PasswordBearer |
| `GET` | `/api/accommodations/me` | Get My Accommodation | OAuth2PasswordBearer |
| `GET` | `/api/admin/activity` | Get Activity Log | OAuth2PasswordBearer |
| `POST` | `/api/admin/activity/clear` | Clear Activity Log | OAuth2PasswordBearer |
| `GET` | `/api/admin/activity/export` | Export Activity Log | OAuth2PasswordBearer |
| `GET` | `/api/admin/audit/impersonations` | Admin Impersonation Sessions | OAuth2PasswordBearer |
| `GET` | `/api/admin/audit/users/by-username/{username}/history` | Admin User History By Username | OAuth2PasswordBearer |
| `GET` | `/api/admin/audit/users/{user_id}/history` | Admin User History | OAuth2PasswordBearer |
| `GET` | `/api/admin/badges` | List Badges | OAuth2PasswordBearer |
| `POST` | `/api/admin/badges/rotate-key` | Rotate Badge Key | OAuth2PasswordBearer |
| `GET` | `/api/admin/badges/settings` | Badge Settings | OAuth2PasswordBearer |
| `PUT` | `/api/admin/badges/settings` | Update Badge Settings | OAuth2PasswordBearer |
| `POST` | `/api/admin/badges/{badge_id}/revoke` | Revoke Badge | OAuth2PasswordBearer |
| `GET` | `/api/admin/competency-coverage` | Competency Coverage | OAuth2PasswordBearer |
| `POST` | `/api/admin/containers/cleanup-orphaned` | Cleanup Orphaned Containers | OAuth2PasswordBearer |
| `GET` | `/api/admin/courses/{course_id}/retention` | Get Retention Policy | OAuth2PasswordBearer |
| `PUT` | `/api/admin/courses/{course_id}/retention` | Set Retention Policy | OAuth2PasswordBearer |
| `POST` | `/api/admin/courses/{course_id}/retention/complete` | Complete Retention | OAuth2PasswordBearer |
| `POST` | `/api/admin/courses/{course_id}/retention/preview` | Preview Retention | OAuth2PasswordBearer |
| `GET` | `/api/admin/courses/{course_id}/retention/runs` | List Retention Runs | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/curriculum/levels/{level_id}` | Delete Level | OAuth2PasswordBearer |
| `PUT` | `/api/admin/curriculum/levels/{level_id}` | Update Level | OAuth2PasswordBearer |
| `GET` | `/api/admin/curriculum/tracks` | List Tracks | OAuth2PasswordBearer |
| `POST` | `/api/admin/curriculum/tracks` | Create Track | OAuth2PasswordBearer |
| `PUT` | `/api/admin/curriculum/tracks/reorder` | Reorder Tracks | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/curriculum/tracks/{track_id}` | Delete Track | OAuth2PasswordBearer |
| `PUT` | `/api/admin/curriculum/tracks/{track_id}` | Update Track | OAuth2PasswordBearer |
| `POST` | `/api/admin/curriculum/tracks/{track_id}/levels` | Create Level | OAuth2PasswordBearer |
| `PUT` | `/api/admin/curriculum/tracks/{track_id}/levels/reorder` | Reorder Levels | OAuth2PasswordBearer |
| `GET` | `/api/admin/data-labels/policy` | Get Data Label Policy | OAuth2PasswordBearer |
| `GET` | `/api/admin/docker/disk-usage` | Get Docker Disk Usage | OAuth2PasswordBearer |
| `POST` | `/api/admin/docker/prune-build-cache` | Prune Build Cache | OAuth2PasswordBearer |
| `POST` | `/api/admin/docker/prune-images` | Prune All Images | OAuth2PasswordBearer |
| `POST` | `/api/admin/exercise-test` | Run Exercise Test | OAuth2PasswordBearer |
| `GET` | `/api/admin/exercise-test/active` | Get Active Test Run | OAuth2PasswordBearer |
| `POST` | `/api/admin/exercise-test/cancel` | Cancel Exercise Test | OAuth2PasswordBearer |
| `GET` | `/api/admin/exercise-test/events/{run_id}` | Get Test Events | OAuth2PasswordBearer |
| `GET` | `/api/admin/exercise-test/labs` | List Testable Labs | OAuth2PasswordBearer |
| `POST` | `/api/admin/exercise-test/report` | Generate Exercise Test Report | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/exercise-test/results` | Clear All Exercise Test Results | OAuth2PasswordBearer |
| `GET` | `/api/admin/exercise-test/results` | Get Exercise Test Results | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/exercise-test/results/{lab_slug}` | Delete Exercise Test Result | OAuth2PasswordBearer |
| `POST` | `/api/admin/impersonate/disconnect` | Disconnect Impersonation | OAuth2PasswordBearer |
| `POST` | `/api/admin/impersonate/launch` | Impersonate Launch Lab | OAuth2PasswordBearer |
| `GET` | `/api/admin/impersonate/status` | Impersonation Status | OAuth2PasswordBearer |
| `POST` | `/api/admin/impersonate/{session_id}` | Impersonate Session | OAuth2PasswordBearer |
| `GET` | `/api/admin/labs` | List Labs | OAuth2PasswordBearer |
| `POST` | `/api/admin/labs` | Create Lab | OAuth2PasswordBearer |
| `POST` | `/api/admin/labs/bulk-toggle` | Bulk Toggle Labs | OAuth2PasswordBearer |
| `POST` | `/api/admin/labs/discover` | Discover Labs | OAuth2PasswordBearer |
| `POST` | `/api/admin/labs/import` | Import Exercise | OAuth2PasswordBearer |
| `PUT` | `/api/admin/labs/{lab_id}` | Update Lab | OAuth2PasswordBearer |
| `POST` | `/api/admin/labs/{lab_id}/approve` | Approve Lab | OAuth2PasswordBearer |
| `PUT` | `/api/admin/labs/{lab_id}/compose` | Update Lab Compose | OAuth2PasswordBearer |
| `GET` | `/api/admin/labs/{lab_id}/details` | Get Lab Details Admin | OAuth2PasswordBearer |
| `GET` | `/api/admin/labs/{lab_id}/export` | Export Exercise | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/labs/{lab_id}/images` | Delete Lab Images | OAuth2PasswordBearer |
| `GET` | `/api/admin/labs/{lab_id}/images` | Get Lab Images | OAuth2PasswordBearer |
| `POST` | `/api/admin/labs/{lab_id}/reject` | Reject Lab | OAuth2PasswordBearer |
| `POST` | `/api/admin/labs/{lab_id}/toggle` | Toggle Lab | OAuth2PasswordBearer |
| `GET` | `/api/admin/question-banks` | List certification question banks | OAuth2PasswordBearer |
| `POST` | `/api/admin/question-banks/validate` | Validate the question banks | OAuth2PasswordBearer |
| `GET` | `/api/admin/question-banks/{pathway_id}` | Read one certification question bank | OAuth2PasswordBearer |
| `GET` | `/api/admin/rangebox-capacity` | Get Rangebox Capacity | OAuth2PasswordBearer |
| `POST` | `/api/admin/rangebox-capacity/test` | Run Rangebox Capacity Test | OAuth2PasswordBearer |
| `GET` | `/api/admin/retention/due` | List Retention Due | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/access-rules` | List sign-in and registration allow/deny rules | OAuth2PasswordBearer |
| `POST` | `/api/admin/security/access-rules` | Add a sign-in or registration allow/deny rule | OAuth2PasswordBearer |
| `POST` | `/api/admin/security/access-rules/test` | Explain how the current rules evaluate one request | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/security/access-rules/{rule_id}` | Remove a sign-in or registration allow/deny rule | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/break-glass` | Break-glass grants and review state | OAuth2PasswordBearer |
| `POST` | `/api/admin/security/break-glass` | Request time-bound emergency access | OAuth2PasswordBearer |
| `POST` | `/api/admin/security/break-glass/{grant_id}/approve` | Approve a pending grant | OAuth2PasswordBearer |
| `POST` | `/api/admin/security/break-glass/{grant_id}/review` | Close the post-use review | OAuth2PasswordBearer |
| `POST` | `/api/admin/security/break-glass/{grant_id}/revoke` | Revoke a grant | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/events` | Query security, audit, and privacy events | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/events/summary` | Security event counts and top event types | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/events/{event_id}` | One security event | OAuth2PasswordBearer |
| `POST` | `/api/admin/security/rbac/check` | Explain one authorization decision | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/rbac/matrix` | Role and policy access matrix | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/rbac/permissions` | Reviewed permission catalog | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/rbac/roles` | Roles, grants, and effective permission counts | OAuth2PasswordBearer |
| `PUT` | `/api/admin/security/rbac/roles/{role_key}/permissions` | Replace one role's permission grants | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/rbac/users/{user_id}` | Effective roles and permissions | OAuth2PasswordBearer |
| `POST` | `/api/admin/security/rbac/users/{user_id}/roles` | Grant an expiring extra role | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/security/rbac/users/{user_id}/roles/{role_key}` | Revoke an extra role | OAuth2PasswordBearer |
| `GET` | `/api/admin/security/service-identities` | List non-human service credentials | OAuth2PasswordBearer |
| `POST` | `/api/admin/security/service-identities` | Create a scoped service credential | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/security/service-identities/{credential_id}` | Revoke a service credential | OAuth2PasswordBearer |
| `GET` | `/api/admin/sessions/active` | List Active Sessions | OAuth2PasswordBearer |
| `GET` | `/api/admin/sessions/health` | Get Sessions Health | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/sessions/history` | Clear Session History | OAuth2PasswordBearer |
| `GET` | `/api/admin/sessions/history` | Session History | OAuth2PasswordBearer |
| `POST` | `/api/admin/sessions/terminate-all` | Terminate All Sessions | OAuth2PasswordBearer |
| `POST` | `/api/admin/sessions/terminate/{session_id}` | Terminate Session | OAuth2PasswordBearer |
| `GET` | `/api/admin/sessions/{session_id}/logs` | Get Session Logs | OAuth2PasswordBearer |
| `POST` | `/api/admin/sessions/{session_id}/reset-stale` | Reset Stale Session | OAuth2PasswordBearer |
| `POST` | `/api/admin/sessions/{session_id}/resync-vpn` | Resync Session Vpn | OAuth2PasswordBearer |
| `GET` | `/api/admin/stats` | Get Stats | OAuth2PasswordBearer |
| `POST` | `/api/admin/stress-test` | Start Stress Test | OAuth2PasswordBearer |
| `GET` | `/api/admin/stress-test/active` | Get Active Stress Test | OAuth2PasswordBearer |
| `POST` | `/api/admin/stress-test/cancel` | Cancel Stress Test | OAuth2PasswordBearer |
| `POST` | `/api/admin/stress-test/cleanup` | Stress Test Cleanup | OAuth2PasswordBearer |
| `GET` | `/api/admin/stress-test/events/{run_id}` | Get Stress Test Events | OAuth2PasswordBearer |
| `GET` | `/api/admin/stress-test/last-result` | Get Last Stress Result | OAuth2PasswordBearer |
| `POST` | `/api/admin/stress-test/report` | Generate Stress Report Pdf | OAuth2PasswordBearer |
| `GET` | `/api/admin/system/activity-calendar` | Activity Calendar | OAuth2PasswordBearer |
| `POST` | `/api/admin/system/backup` | Create Backup | OAuth2PasswordBearer |
| `GET` | `/api/admin/system/backups` | List Backups | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/system/backups/{filename}` | Delete Backup | OAuth2PasswordBearer |
| `GET` | `/api/admin/system/backups/{filename}` | Download Backup | OAuth2PasswordBearer |
| `GET` | `/api/admin/system/data-integrity` | Get Data Integrity Status | OAuth2PasswordBearer |
| `POST` | `/api/admin/system/data-integrity/review` | Review Data Integrity Write | OAuth2PasswordBearer |
| `GET` | `/api/admin/system/metrics` | Get System Metrics | OAuth2PasswordBearer |
| `POST` | `/api/admin/system/metrics/sample` | Sample System Metrics | OAuth2PasswordBearer |
| `GET` | `/api/admin/system/release` | Compare this installation with the latest GitHub release | OAuth2PasswordBearer |
| `POST` | `/api/admin/system/restore` | Restore Backup | OAuth2PasswordBearer |
| `POST` | `/api/admin/system/restore/upload` | Restore Uploaded Backup | OAuth2PasswordBearer |
| `GET` | `/api/admin/system/software-integrity` | Verify deployed lab content against the release manifest | OAuth2PasswordBearer |
| `GET` | `/api/admin/system/status` | System Status | OAuth2PasswordBearer |
| `GET` | `/api/admin/users` | List Users | OAuth2PasswordBearer |
| `POST` | `/api/admin/users/approve` | Approve User | OAuth2PasswordBearer |
| `POST` | `/api/admin/users/create` | Create User | OAuth2PasswordBearer |
| `GET` | `/api/admin/users/export` | Export Users | OAuth2PasswordBearer |
| `POST` | `/api/admin/users/import` | Import Users | OAuth2PasswordBearer |
| `GET` | `/api/admin/users/locked` | List Locked Users | OAuth2PasswordBearer |
| `GET` | `/api/admin/users/pending` | List Pending Users | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/users/{user_id}` | Delete User | OAuth2PasswordBearer |
| `GET` | `/api/admin/users/{user_id}` | Get User | OAuth2PasswordBearer |
| `PUT` | `/api/admin/users/{user_id}` | Update User | OAuth2PasswordBearer |
| `GET` | `/api/admin/users/{user_id}/details` | Get User Details | OAuth2PasswordBearer |
| `POST` | `/api/admin/users/{user_id}/force-logout` | Force Logout User | OAuth2PasswordBearer |
| `POST` | `/api/admin/users/{user_id}/labs/{lab_id}/reset` | Reset User Lab | OAuth2PasswordBearer |
| `POST` | `/api/admin/users/{user_id}/mfa/reset` | Reset another account's MFA | OAuth2PasswordBearer |
| `POST` | `/api/admin/users/{user_id}/reset-password` | Reset Password | OAuth2PasswordBearer |
| `POST` | `/api/admin/users/{user_id}/unlock` | Unlock User | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/vpn/peer-by-key/{public_key}` | Remove Vpn Peer By Key | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/vpn/peer/{user_id}` | Remove Vpn Peer | OAuth2PasswordBearer |
| `GET` | `/api/admin/vpn/peers` | List Vpn Peers | OAuth2PasswordBearer |
| `POST` | `/api/admin/vpn/peers/{user_id}/repair` | Repair Vpn Peer | OAuth2PasswordBearer |
| `POST` | `/api/admin/vpn/reconcile-peers` | Reconcile Vpn Peers | OAuth2PasswordBearer |
| `POST` | `/api/admin/vpn/register/{user_id}` | Register Vpn Peer | OAuth2PasswordBearer |
| `GET` | `/api/admin/vpn/status` | Vpn Sync Status | OAuth2PasswordBearer |
| `POST` | `/api/admin/vpn/sync` | Sync Vpn Peers | OAuth2PasswordBearer |
| `POST` | `/api/admin/workbook/build` | Trigger Build | OAuth2PasswordBearer |
| `POST` | `/api/admin/workbook/build-all-course-wikis` | Build All Course Wikis | OAuth2PasswordBearer |
| `DELETE` | `/api/admin/workbook/chapter/{chapter_dir}` | Delete Chapter | OAuth2PasswordBearer |
| `GET` | `/api/admin/workbook/chapters` | List Chapters | OAuth2PasswordBearer |
| `POST` | `/api/admin/workbook/upload` | Upload Chapter | OAuth2PasswordBearer |
| `GET` | `/api/analytics/courses/{course_id}/competency` | Course Competency | OAuth2PasswordBearer |
| `GET` | `/api/analytics/courses/{course_id}/exercises` | Course Exercises | OAuth2PasswordBearer |
| `POST` | `/api/analytics/courses/{course_id}/labs/{lab_id}/reviews` | Add Lab Health Review | OAuth2PasswordBearer |
| `GET` | `/api/analytics/courses/{course_id}/overview` | Course Overview | OAuth2PasswordBearer |
| `GET` | `/api/analytics/courses/{course_id}/pulse-comments` | Course Pulse Comments | OAuth2PasswordBearer |
| `GET` | `/api/analytics/courses/{course_id}/readiness` | Course Readiness | OAuth2PasswordBearer |
| `GET` | `/api/analytics/courses/{course_id}/readiness/calibration` | Readiness Calibration | OAuth2PasswordBearer |
| `GET` | `/api/analytics/courses/{course_id}/students/{user_id}/capabilities` | Student Capabilities | OAuth2PasswordBearer |
| `POST` | `/api/analytics/courses/{course_id}/students/{user_id}/notes` | Add Readiness Note | OAuth2PasswordBearer |
| `POST` | `/api/analytics/events/workbook-open` | Workbook Opened | OAuth2PasswordBearer |
| `GET` | `/api/analytics/metrics` | Metric Dictionary | OAuth2PasswordBearer |
| `GET` | `/api/analytics/pulse/{lab_id}` | Get Pulse | OAuth2PasswordBearer |
| `POST` | `/api/analytics/pulse/{lab_id}` | Submit Pulse | OAuth2PasswordBearer |
| `GET` | `/api/analytics/reaction/{lab_id}` | Get Exercise Reaction | OAuth2PasswordBearer |
| `POST` | `/api/analytics/reaction/{lab_id}` | Set Exercise Reaction | OAuth2PasswordBearer |
| `GET` | `/api/analytics/reports/activity` | Reports Activity | OAuth2PasswordBearer |
| `GET` | `/api/analytics/reports/curriculum-demand` | Curriculum Demand | OAuth2PasswordBearer |
| `POST` | `/api/analytics/reports/export-audit` | Audit Report Export | OAuth2PasswordBearer |
| `GET` | `/api/analytics/reports/export.pdf` | Reports Export Pdf | OAuth2PasswordBearer |
| `GET` | `/api/analytics/reports/overview` | Reports Overview | OAuth2PasswordBearer |
| `GET` | `/api/analytics/student/me` | Student Analytics | OAuth2PasswordBearer |
| `GET` | `/api/analytics/surveys` | List Surveys | OAuth2PasswordBearer |
| `POST` | `/api/analytics/surveys` | Create Survey | OAuth2PasswordBearer |
| `GET` | `/api/analytics/surveys/available` | Available Surveys | OAuth2PasswordBearer |
| `DELETE` | `/api/analytics/surveys/{survey_id}` | Delete Survey | OAuth2PasswordBearer |
| `GET` | `/api/analytics/surveys/{survey_id}/responses` | Survey Responses | OAuth2PasswordBearer |
| `POST` | `/api/analytics/surveys/{survey_id}/responses` | Submit Survey Response | OAuth2PasswordBearer |
| `POST` | `/api/auth/change-password` | Change Password | OAuth2PasswordBearer |
| `POST` | `/api/auth/delete-account` | Delete My Account | OAuth2PasswordBearer |
| `POST` | `/api/auth/delete-request` | Request Account Deletion | OAuth2PasswordBearer |
| `GET` | `/api/auth/export` | Export User Data | OAuth2PasswordBearer |
| `GET` | `/api/auth/export-status` | Export Status | OAuth2PasswordBearer |
| `POST` | `/api/auth/forgot-password` | Forgot Password | Public |
| `POST` | `/api/auth/forgot-username` | Forgot Username | Public |
| `POST` | `/api/auth/impersonate` | Start Impersonation | OAuth2PasswordBearer |
| `POST` | `/api/auth/impersonate/exit` | Exit Impersonation | OAuth2PasswordBearer |
| `POST` | `/api/auth/login` | Login | Public |
| `POST` | `/api/auth/logout` | Logout | OAuth2PasswordBearer |
| `GET` | `/api/auth/me` | Get Current User Info | OAuth2PasswordBearer |
| `GET` | `/api/auth/me/impersonation` | Get Impersonation Status | OAuth2PasswordBearer |
| `POST` | `/api/auth/mfa/disable` | Disable Mfa | OAuth2PasswordBearer |
| `POST` | `/api/auth/mfa/enroll` | Enroll Mfa | OAuth2PasswordBearer |
| `POST` | `/api/auth/mfa/recovery-codes` | Generate Recovery Codes | OAuth2PasswordBearer |
| `POST` | `/api/auth/mfa/recovery-codes/verify` | Verify Recovery Code | OAuth2PasswordBearer |
| `POST` | `/api/auth/mfa/verify` | Verify Mfa | OAuth2PasswordBearer |
| `POST` | `/api/auth/reauth` | Reauthenticate | OAuth2PasswordBearer |
| `POST` | `/api/auth/refresh` | Refresh Access Token | Public |
| `POST` | `/api/auth/register` | Register | Public |
| `POST` | `/api/auth/reset-password` | Reset Password | Public |
| `GET` | `/api/auth/sessions` | List Sessions | OAuth2PasswordBearer |
| `POST` | `/api/auth/sessions/revoke-all` | Revoke All Sessions | OAuth2PasswordBearer |
| `DELETE` | `/api/auth/sessions/{session_id}` | Revoke One Session | OAuth2PasswordBearer |
| `GET` | `/api/auth/settings` | Get User Settings | OAuth2PasswordBearer |
| `PUT` | `/api/auth/settings` | Update User Settings | OAuth2PasswordBearer |
| `POST` | `/api/auth/sso/exchange` | Exchange Ticket | Public |
| `POST` | `/api/auth/sso/ldap/{provider_id}/login` | Ldap Login | Public |
| `GET` | `/api/auth/sso/oidc/{provider_id}/callback` | Oidc Callback | Public |
| `GET` | `/api/auth/sso/oidc/{provider_id}/login` | Oidc Login | Public |
| `GET` | `/api/auth/sso/providers` | List Sso Providers | Public |
| `POST` | `/api/auth/sso/saml/{provider_id}/acs` | Saml Acs | Public |
| `GET` | `/api/auth/sso/saml/{provider_id}/login` | Saml Login | Public |
| `GET` | `/api/auth/survey-consent` | Get Survey Consent | OAuth2PasswordBearer |
| `POST` | `/api/auth/survey-consent` | Update Survey Consent | OAuth2PasswordBearer |
| `GET` | `/api/auth/wiki-access` | Check Wiki Access | OAuth2PasswordBearer |
| `GET` | `/api/auth/wiki-admin-access` | Check Wiki Admin Access | OAuth2PasswordBearer |
| `DELETE` | `/api/auth/wiki-cookie` | Clear Wiki Cookie | Public |
| `POST` | `/api/auth/wiki-cookie` | Issue Wiki Cookie | OAuth2PasswordBearer |
| `GET` | `/api/auth/wiki-released` | Wiki Released Chapters | Public |
| `GET` | `/api/badges/achievements/{certificate_id}` | Achievement Definition | Public |
| `GET` | `/api/badges/achievements/{certificate_id}/image` | Achievement Image | Public |
| `GET` | `/api/badges/credentials/{jti}` | Hosted Credential | Public |
| `GET` | `/api/badges/credentials/{jti}/jwt` | Hosted Credential Jwt | Public |
| `GET` | `/api/badges/credentials/{jti}/status` | Credential Status | Public |
| `POST` | `/api/badges/events/issue` | Issue Event Badge | OAuth2PasswordBearer |
| `POST` | `/api/badges/issue` | Issue Badge | OAuth2PasswordBearer |
| `GET` | `/api/badges/issuer` | Issuer Profile | Public |
| `GET` | `/api/badges/issuer/jwks` | Issuer Jwks | Public |
| `GET` | `/api/badges/mine` | My Badges | OAuth2PasswordBearer |
| `POST` | `/api/badges/{badge_id}/consent` | Badge Consent | OAuth2PasswordBearer |
| `GET` | `/api/competencies/{competency_id}/evidence` | Competency Evidence | OAuth2PasswordBearer |
| `GET` | `/api/competitions` | List Competitions | OAuth2PasswordBearer |
| `POST` | `/api/competitions` | Create Competition | OAuth2PasswordBearer |
| `GET` | `/api/competitions/public/{competition_id}` | Public Competition | Public |
| `DELETE` | `/api/competitions/{competition_id}` | Delete Competition | OAuth2PasswordBearer |
| `GET` | `/api/competitions/{competition_id}` | Get Competition | OAuth2PasswordBearer |
| `PATCH` | `/api/competitions/{competition_id}` | Update Competition | OAuth2PasswordBearer |
| `POST` | `/api/competitions/{competition_id}/archive` | Archive Competition | OAuth2PasswordBearer |
| `GET` | `/api/competitions/{competition_id}/certificate/{award}` | Get Event Certificate | OAuth2PasswordBearer |
| `GET` | `/api/competitions/{competition_id}/certificates` | List Event Certificates | OAuth2PasswordBearer |
| `GET` | `/api/competitions/{competition_id}/discovery` | Get Event Discovery | OAuth2PasswordBearer |
| `GET` | `/api/competitions/{competition_id}/discovery/overview` | Get Event Discovery Overview | OAuth2PasswordBearer |
| `POST` | `/api/competitions/{competition_id}/join` | Join Competition | OAuth2PasswordBearer |
| `POST` | `/api/competitions/{competition_id}/leave` | Leave Competition | OAuth2PasswordBearer |
| `POST` | `/api/competitions/{competition_id}/unarchive` | Unarchive Competition | OAuth2PasswordBearer |
| `GET` | `/api/config/public` | Public Config | Public |
| `GET` | `/api/consent/` | Learner consent and revocation status | OAuth2PasswordBearer |
| `POST` | `/api/consent/admin/enforce-suppressions` | Apply the suppression ledger | OAuth2PasswordBearer |
| `GET` | `/api/consent/admin/metrics` | Revocation verification metrics | OAuth2PasswordBearer |
| `GET` | `/api/consent/admin/revocations` | All revocation workflows | OAuth2PasswordBearer |
| `POST` | `/api/consent/admin/run-jobs` | Run due purge and verification jobs | OAuth2PasswordBearer |
| `GET` | `/api/consent/revocations` | The learner's own revocation history | OAuth2PasswordBearer |
| `GET` | `/api/consent/types` | Available consent types | OAuth2PasswordBearer |
| `POST` | `/api/consent/{consent_type}/grant` | Grant Consent | OAuth2PasswordBearer |
| `POST` | `/api/consent/{consent_type}/revoke` | Revoke Consent | OAuth2PasswordBearer |
| `GET` | `/api/courses/` | List Courses | OAuth2PasswordBearer |
| `POST` | `/api/courses/` | Create Course | OAuth2PasswordBearer |
| `POST` | `/api/courses/join` | Join Course | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}` | Delete Course | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}` | Get Course | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}` | Update Course | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/achievements` | List Achievements | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/archive` | Archive Course | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/assignments` | List Assignments | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/assignments` | Create Assignment | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}/assignments/reorder` | Reorder Assignments | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}/assignments/{assignment_id}` | Delete Assignment | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}/assignments/{assignment_id}` | Update Assignment | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/assignments/{assignment_id}/labs` | Add Labs To Assignment | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}/assignments/{assignment_id}/labs/{lab_id}` | Remove Lab From Assignment | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/assignments/{assignment_id}/report` | Assignment Class Report | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/assignments/{assignment_id}/report/{user_id}` | Assignment Student Report | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}/cohort-settings` | Update Cohort Settings | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/cohorts` | Create Cohort | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/cohorts/sync-default` | Sync Default Cohort Members | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}/cohorts/{cohort_id}` | Delete Cohort | OAuth2PasswordBearer |
| `PATCH` | `/api/courses/{course_id}/cohorts/{cohort_id}` | Update Cohort | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}/cohorts/{cohort_id}/members` | Set Cohort Members | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/enroll-bulk` | Enroll Students Bulk | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}/enroll/{user_id}` | Remove Student | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/exercise-sets` | Create Set | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}/exercise-sets/{set_id}` | Delete Set | OAuth2PasswordBearer |
| `PATCH` | `/api/courses/{course_id}/exercise-sets/{set_id}` | Update Set | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}/exercise-sets/{set_id}/items` | Set Items | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/feedback` | Submit Course Feedback | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/feedback/me` | My Course Feedback | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/feedback/summary` | Course Feedback Summary | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/labs` | Assign Labs | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/labs/bulk-remove` | Remove several exercises from a course | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}/labs/reorder` | Reorder Labs | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}/labs/{lab_id}` | Remove Lab | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}/labs/{lab_id}` | Update Course Lab | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/labs/{lab_id}/reset/{user_id}` | Reset Student Lab | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/planning` | Get Planning | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/planning/coverage` | Get Coverage | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/regenerate-invite` | Regenerate Invite | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/report` | Class Report | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/report/{user_id}` | Student Report | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/reports` | List Reports | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/reports/coaching-queue.csv` | Coaching Queue Csv | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/reports/coaching-queue.pdf` | Coaching Queue Pdf | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/reports/course-health.pdf` | Course Health Report | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/reports/exercise-diagnostics.csv` | Exercise Diagnostics Csv | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/reports/exercise-diagnostics.pdf` | Exercise Diagnostics Report | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/requirements` | Create Requirement | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}/requirements/{requirement_id}` | Delete Requirement | OAuth2PasswordBearer |
| `PATCH` | `/api/courses/{course_id}/requirements/{requirement_id}` | Update Requirement | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/reviews` | List Course Reviews | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/scoreboard` | Get Scoreboard | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/staff` | List Course Staff | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/staff` | Add Course Staff | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/staff/candidates` | List Course Staff Candidates | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}/staff/{staff_id}` | Remove Course Staff | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/students` | List Students | OAuth2PasswordBearer |
| `DELETE` | `/api/courses/{course_id}/students/{student_id}/accommodation` | Clear Student Accommodation | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/students/{student_id}/accommodation` | Get Student Accommodation | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}/students/{student_id}/accommodation` | Set Student Accommodation | OAuth2PasswordBearer |
| `PUT` | `/api/courses/{course_id}/students/{user_id}/consent` | Record Minor Consent | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/students/{user_id}/history` | Course Student History | OAuth2PasswordBearer |
| `GET` | `/api/courses/{course_id}/students/{user_id}/labs/{lab_id}/attempts` | Get Student Lab Attempts | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/toggle-active` | Toggle Course Active | OAuth2PasswordBearer |
| `POST` | `/api/courses/{course_id}/unarchive` | Unarchive Course | OAuth2PasswordBearer |
| `GET` | `/api/dashboard/celebrations` | Celebration Wall | OAuth2PasswordBearer |
| `POST` | `/api/dashboard/celebrations/{achievement_id}/celebrate` | Toggle Celebration | OAuth2PasswordBearer |
| `GET` | `/api/dashboard/instructor/feed` | Instructor Feed | OAuth2PasswordBearer |
| `GET` | `/api/dashboard/instructor/filter-options` | Instructor Filter Options | OAuth2PasswordBearer |
| `GET` | `/api/dashboard/instructor/ics-coverage` | Ics Attack Coverage | OAuth2PasswordBearer |
| `GET` | `/api/dashboard/instructor/learning` | Instructor Learning | OAuth2PasswordBearer |
| `GET` | `/api/dashboard/instructor/pulse` | Instructor Pulse | OAuth2PasswordBearer |
| `GET` | `/api/dashboard/instructor/report` | Instructor Report | OAuth2PasswordBearer |
| `GET` | `/api/dashboard/instructor/stats` | Instructor Stats | OAuth2PasswordBearer |
| `GET` | `/api/dashboard/student` | Student Dashboard | OAuth2PasswordBearer |
| `GET` | `/api/dna/v3/affinity` | Cyber DNA career affinity | OAuth2PasswordBearer |
| `GET` | `/api/dna/v3/behavior` | Cyber DNA behavior profile | OAuth2PasswordBearer |
| `GET` | `/api/dna/v3/competencies` | Cyber DNA competency scores | OAuth2PasswordBearer |
| `GET` | `/api/dna/v3/dna` | Cyber DNA learner payload | OAuth2PasswordBearer |
| `GET` | `/api/dna/v3/evidence` | Cyber DNA evidence ledger | OAuth2PasswordBearer |
| `GET` | `/api/dna/v3/interest` | Cyber DNA interest vector | OAuth2PasswordBearer |
| `GET` | `/api/dna/v3/snapshots` | List Cyber DNA snapshots | OAuth2PasswordBearer |
| `POST` | `/api/dna/v3/snapshots` | Record a Cyber DNA snapshot | OAuth2PasswordBearer |
| `GET` | `/api/dna/v3/snapshots/{snapshot_id}` | Cyber DNA snapshot | OAuth2PasswordBearer |
| `GET` | `/api/evidence` | List Evidence | OAuth2PasswordBearer |
| `POST` | `/api/evidence` | Create Evidence | OAuth2PasswordBearer |
| `GET` | `/api/evidence/analytics` | Evidence Analytics Overview | OAuth2PasswordBearer |
| `GET` | `/api/evidence/queue` | Review Queue | OAuth2PasswordBearer |
| `GET` | `/api/evidence/rubrics` | List Evidence Rubrics | OAuth2PasswordBearer |
| `GET` | `/api/evidence/{evidence_id}` | Get Evidence | OAuth2PasswordBearer |
| `POST` | `/api/evidence/{evidence_id}/review` | Review Evidence | OAuth2PasswordBearer |
| `GET` | `/api/exercises/labs/{lab_id}` | Get Lab Details | OAuth2PasswordBearer |
| `GET` | `/api/exercises/labs/{lab_id}/hint` | Get Hint | OAuth2PasswordBearer |
| `POST` | `/api/exercises/labs/{lab_id}/submit-flag` | Submit Flag | OAuth2PasswordBearer |
| `GET` | `/api/exercises/labs/{lab_slug}/quiz` | Get Exercise Quiz | OAuth2PasswordBearer |
| `GET` | `/api/exercises/labs/{lab_slug}/quiz/attempts` | List Exercise Quiz Attempts | OAuth2PasswordBearer |
| `POST` | `/api/exercises/labs/{lab_slug}/quiz/attempts` | Start Exercise Quiz | OAuth2PasswordBearer |
| `POST` | `/api/exercises/labs/{lab_slug}/quiz/attempts/{attempt_id}/submit` | Submit Exercise Quiz | OAuth2PasswordBearer |
| `POST` | `/api/exercises/labs/{lab_slug}/quiz/feedback` | Submit Exercise Quiz Feedback | OAuth2PasswordBearer |
| `GET` | `/api/exercises/progress` | Get Progress | OAuth2PasswordBearer |
| `GET` | `/api/exercises/tracks` | List Tracks | OAuth2PasswordBearer |
| `GET` | `/api/exercises/tracks/{track_slug}` | Get Track | OAuth2PasswordBearer |
| `GET` | `/api/exercises/tracks/{track_slug}/levels/{level_id}/certificate` | Get a printable level-completion certificate | OAuth2PasswordBearer |
| `GET` | `/api/exercises/tracks/{track_slug}/levels/{level_id}/certificate.pdf` | Download the certificate as a PDF | OAuth2PasswordBearer |
| `GET` | `/api/exercises/tracks/{track_slug}/levels/{level_id}/quiz` | Get Level Quiz | OAuth2PasswordBearer |
| `GET` | `/api/exercises/tracks/{track_slug}/levels/{level_id}/quiz/attempts` | List Quiz Attempts | OAuth2PasswordBearer |
| `POST` | `/api/exercises/tracks/{track_slug}/levels/{level_id}/quiz/submit` | Submit Level Quiz | OAuth2PasswordBearer |
| `GET` | `/api/exercises/verify/certificate/{certificate_id}` | Verify Certificate | Public |
| `GET` | `/api/exercises/workbooks` | List Workbooks | OAuth2PasswordBearer |
| `GET` | `/api/governance/audit/dashboard` | Audit Dashboard | OAuth2PasswordBearer |
| `GET` | `/api/governance/privacy/dashboard` | Privacy Dashboard | OAuth2PasswordBearer |
| `GET` | `/api/identity/providers` | List Identity Providers | OAuth2PasswordBearer |
| `POST` | `/api/identity/providers` | Create Identity Provider | OAuth2PasswordBearer |
| `GET` | `/api/identity/providers/export` | Export Identity Providers | OAuth2PasswordBearer |
| `POST` | `/api/identity/providers/import` | Import Identity Providers | OAuth2PasswordBearer |
| `DELETE` | `/api/identity/providers/{provider_id}` | Delete Identity Provider | OAuth2PasswordBearer |
| `PATCH` | `/api/identity/providers/{provider_id}` | Update Identity Provider | OAuth2PasswordBearer |
| `POST` | `/api/identity/providers/{provider_id}/default` | Make Default Identity Provider | OAuth2PasswordBearer |
| `POST` | `/api/identity/providers/{provider_id}/test` | Test Identity Provider | OAuth2PasswordBearer |
| `GET` | `/api/instructor/courses` | List My Courses | OAuth2PasswordBearer |
| `GET` | `/api/instructor/courses/{course_id}` | Get My Course | OAuth2PasswordBearer |
| `GET` | `/api/instructor/courses/{course_id}/enrollable-users` | List Enrollable Users | OAuth2PasswordBearer |
| `POST` | `/api/instructor/exercise-test` | Run Exercise Test | OAuth2PasswordBearer |
| `GET` | `/api/instructor/exercise-test/active` | Get Active Test Run | OAuth2PasswordBearer |
| `POST` | `/api/instructor/exercise-test/cancel` | Cancel Exercise Test | OAuth2PasswordBearer |
| `GET` | `/api/instructor/exercise-test/events/{run_id}` | Get Test Events | OAuth2PasswordBearer |
| `GET` | `/api/instructor/exercise-test/labs` | List Testable Labs | OAuth2PasswordBearer |
| `POST` | `/api/instructor/exercise-test/report` | Generate Exercise Test Report | OAuth2PasswordBearer |
| `DELETE` | `/api/instructor/exercise-test/results` | Clear All Exercise Test Results | OAuth2PasswordBearer |
| `GET` | `/api/instructor/exercise-test/results` | Get Exercise Test Results | OAuth2PasswordBearer |
| `DELETE` | `/api/instructor/exercise-test/results/{lab_slug}` | Delete Exercise Test Result | OAuth2PasswordBearer |
| `GET` | `/api/instructor/labs` | List Available Labs | OAuth2PasswordBearer |
| `GET` | `/api/instructor/labs/assignments` | Lab Course Assignments | OAuth2PasswordBearer |
| `POST` | `/api/instructor/labs/upload` | Upload Lab Zip | OAuth2PasswordBearer |
| `DELETE` | `/api/instructor/labs/{lab_id}` | Delete Own Lab | OAuth2PasswordBearer |
| `PUT` | `/api/instructor/labs/{lab_id}` | Update Own Lab | OAuth2PasswordBearer |
| `GET` | `/api/instructor/labs/{lab_id}/export` | Export Own Lab | OAuth2PasswordBearer |
| `GET` | `/api/instructor/labs/{lab_id}/flag` | Reveal Lab Flag | OAuth2PasswordBearer |
| `PUT` | `/api/instructor/labs/{lab_id}/visibility` | Update Lab Visibility | OAuth2PasswordBearer |
| `GET` | `/api/instructor/overview` | Instructor Overview | OAuth2PasswordBearer |
| `GET` | `/api/instructor/stats` | Instructor Stats | OAuth2PasswordBearer |
| `GET` | `/api/instructor/tracks-and-levels` | List Tracks And Levels | OAuth2PasswordBearer |
| `GET` | `/api/labs/` | Get Labs | OAuth2PasswordBearer |
| `GET` | `/api/labs/active` | Get Active Lab | OAuth2PasswordBearer |
| `POST` | `/api/labs/extend` | Extend Lab Session | OAuth2PasswordBearer |
| `POST` | `/api/labs/pause` | Pause Lab Session | OAuth2PasswordBearer |
| `GET` | `/api/labs/prebuild-status` | Prebuild Status | OAuth2PasswordBearer |
| `POST` | `/api/labs/resume` | Resume Lab Session | OAuth2PasswordBearer |
| `GET` | `/api/labs/spawn-status/{session_id}` | Get Spawn Status | OAuth2PasswordBearer |
| `POST` | `/api/labs/spawn/{lab_slug}` | Spawn Lab | OAuth2PasswordBearer |
| `POST` | `/api/labs/stop` | Stop Lab | OAuth2PasswordBearer |
| `GET` | `/api/labs/vpn-config` | Get Vpn Config | OAuth2PasswordBearer |
| `GET` | `/api/labs/vpn-config/qr` | Get Vpn Config Qr | OAuth2PasswordBearer |
| `GET` | `/api/labs/vpn-status` | Get Vpn Status | OAuth2PasswordBearer |
| `GET` | `/api/lti/admin/links` | List Links | OAuth2PasswordBearer |
| `POST` | `/api/lti/admin/links/{link_id}/lineitem` | Create Link Lineitem | OAuth2PasswordBearer |
| `GET` | `/api/lti/admin/links/{link_id}/results` | Get Link Results | OAuth2PasswordBearer |
| `GET` | `/api/lti/admin/links/{link_id}/roster` | Get Link Roster | OAuth2PasswordBearer |
| `GET` | `/api/lti/admin/links/{link_id}/roster/saved` | Get Saved Roster | OAuth2PasswordBearer |
| `POST` | `/api/lti/admin/links/{link_id}/score` | Post Link Score | OAuth2PasswordBearer |
| `GET` | `/api/lti/admin/links/{link_id}/scores` | List Link Scores | OAuth2PasswordBearer |
| `POST` | `/api/lti/admin/links/{link_id}/sync-roster` | Sync Link Roster | OAuth2PasswordBearer |
| `GET` | `/api/lti/admin/platforms` | List Platforms | OAuth2PasswordBearer |
| `POST` | `/api/lti/admin/platforms` | Create Platform | OAuth2PasswordBearer |
| `DELETE` | `/api/lti/admin/platforms/{platform_id}` | Delete Platform | OAuth2PasswordBearer |
| `PATCH` | `/api/lti/admin/platforms/{platform_id}` | Update Platform | OAuth2PasswordBearer |
| `POST` | `/api/lti/admin/platforms/{platform_id}/test` | Test Platform | OAuth2PasswordBearer |
| `GET` | `/api/lti/deep-link/{session_token}` | Deep Link Info | OAuth2PasswordBearer |
| `POST` | `/api/lti/deep-link/{session_token}/response` | Deep Link Response | OAuth2PasswordBearer |
| `GET` | `/api/lti/jwks` | Tool Jwks | Public |
| `POST` | `/api/lti/launch` | Lti Launch | Public |
| `GET` | `/api/lti/login` | Lti Login | Public |
| `POST` | `/api/lti/login` | Lti Login | Public |
| `GET` | `/api/modules/` | Get Modules Status | OAuth2PasswordBearer |
| `GET` | `/api/nice/components` | Nice Components | OAuth2PasswordBearer |
| `GET` | `/api/nice/coverage` | Nice Coverage | OAuth2PasswordBearer |
| `POST` | `/api/nice/labs/seed` | Seed Nice Lab Mappings | OAuth2PasswordBearer |
| `GET` | `/api/nice/labs/{lab_id}` | Get Lab Nice Mappings | OAuth2PasswordBearer |
| `PUT` | `/api/nice/labs/{lab_id}` | Set Lab Nice Mappings | OAuth2PasswordBearer |
| `POST` | `/api/nice/labs/{lab_id}/review` | Review Lab Nice Mappings | OAuth2PasswordBearer |
| `POST` | `/api/nice/refresh` | Refresh Nice Framework | OAuth2PasswordBearer |
| `GET` | `/api/nice/status` | Nice Status | OAuth2PasswordBearer |
| `GET` | `/api/profile/career-assessment` | Short career-direction questions | OAuth2PasswordBearer |
| `POST` | `/api/profile/career-assessment` | Score a short career-direction check | OAuth2PasswordBearer |
| `GET` | `/api/profile/career-dossier` | Career-profile dossier (JSON) | OAuth2PasswordBearer |
| `GET` | `/api/profile/career-dossier.html` | Career-profile dossier (HTML) | OAuth2PasswordBearer |
| `GET` | `/api/profile/career-dossier.md` | Career-profile dossier (Markdown) | OAuth2PasswordBearer |
| `GET` | `/api/profile/competencies` | Learner competency assessment profile | OAuth2PasswordBearer |
| `POST` | `/api/profile/gps` | Optional cybersecurity GPS direction finder | OAuth2PasswordBearer |
| `GET` | `/api/profile/portfolio` | Professional portfolio (JSON) | OAuth2PasswordBearer |
| `GET` | `/api/profile/portfolio.html` | Professional portfolio (printable HTML) | OAuth2PasswordBearer |
| `GET` | `/api/profile/portfolio.md` | Professional portfolio (Markdown) | OAuth2PasswordBearer |
| `GET` | `/api/profile/role-readiness` | Role readiness answer | OAuth2PasswordBearer |
| `GET` | `/api/profile/roles` | Career pathway catalogue | OAuth2PasswordBearer |
| `GET` | `/api/profile/shares` | List portfolio share links | OAuth2PasswordBearer |
| `POST` | `/api/profile/shares` | Create a portfolio share link | OAuth2PasswordBearer |
| `DELETE` | `/api/profile/shares/{share_id}` | Revoke a portfolio share link | OAuth2PasswordBearer |
| `GET` | `/api/profile/skill-dna` | Learner Skill DNA character sheet | OAuth2PasswordBearer |
| `GET` | `/api/profile/snapshots` | Stored report snapshots | OAuth2PasswordBearer |
| `GET` | `/api/profile/snapshots/{snapshot_id}` | Stored report snapshot | OAuth2PasswordBearer |
| `GET` | `/api/profile/snapshots/{snapshot_id}/html` | Stored report (HTML) | OAuth2PasswordBearer |
| `GET` | `/api/profile/snapshots/{snapshot_id}/markdown` | Stored report (Markdown) | OAuth2PasswordBearer |
| `GET` | `/api/profile/summary` | Profile snapshot with certificates and completions | OAuth2PasswordBearer |
| `PUT` | `/api/profile/title` | Equip an unlocked achievement title | OAuth2PasswordBearer |
| `GET` | `/api/profile/transcript.pdf` | Download a printable completion transcript | OAuth2PasswordBearer |
| `GET` | `/api/public/community-events` | Community Events | Public |
| `GET` | `/api/public/portfolio/{token}` | Read a shared portfolio | OAuth2PasswordBearer |
| `GET` | `/api/public/qr/{source}` | Qr Landing | Public |
| `GET` | `/api/rangebox/capacity` | Rangebox Capacity | OAuth2PasswordBearer |
| `DELETE` | `/api/rangebox/standalone/destroy` | Standalone Rangebox Destroy | OAuth2PasswordBearer |
| `POST` | `/api/rangebox/standalone/launch` | Standalone Rangebox Launch | OAuth2PasswordBearer |
| `GET` | `/api/rangebox/standalone/status` | Standalone Rangebox Status | OAuth2PasswordBearer |
| `GET` | `/api/rangebox/transport` | Rangebox Transport | OAuth2PasswordBearer |
| `POST` | `/api/rangebox/ws-ticket` | Get Ws Ticket | OAuth2PasswordBearer |
| `GET` | `/api/rangebox/{session_id}/lab` | Rangebox Lab | OAuth2PasswordBearer |
| `GET` | `/api/rangebox/{session_id}/status` | Rangebox Status | OAuth2PasswordBearer |
| `POST` | `/api/reports/verify` | Verify Report File | Public |
| `POST` | `/api/reviews` | Request Review | OAuth2PasswordBearer |
| `GET` | `/api/reviews/mine` | List My Reviews | OAuth2PasswordBearer |
| `PUT` | `/api/reviews/{review_id}/decision` | Decide Review | OAuth2PasswordBearer |
| `GET` | `/api/settings/` | Get All Settings | OAuth2PasswordBearer |
| `PUT` | `/api/settings/` | Update Settings | OAuth2PasswordBearer |
| `GET` | `/api/settings/achievement-catalogue` | Grouped achievement catalogue for the studio | OAuth2PasswordBearer |
| `GET` | `/api/settings/change-requests` | List Change Requests | OAuth2PasswordBearer |
| `POST` | `/api/settings/change-requests/{change_id}/revert` | Revert Change Request | OAuth2PasswordBearer |
| `GET` | `/api/settings/custom-achievements` | List custom achievements | OAuth2PasswordBearer |
| `POST` | `/api/settings/custom-achievements` | Create a custom achievement | OAuth2PasswordBearer |
| `DELETE` | `/api/settings/custom-achievements/{achievement_id}` | Delete a custom achievement | OAuth2PasswordBearer |
| `PUT` | `/api/settings/custom-achievements/{achievement_id}` | Update a custom achievement | OAuth2PasswordBearer |
| `POST` | `/api/settings/mail/test` | Send Mail Test | OAuth2PasswordBearer |
| `POST` | `/api/settings/production/cutover` | Production Cutover | OAuth2PasswordBearer |
| `GET` | `/api/settings/production/preview` | Production Preview | OAuth2PasswordBearer |
| `GET` | `/api/settings/{category}` | Get Settings By Category | OAuth2PasswordBearer |
| `POST` | `/api/setup/complete` | Complete Setup | Public |
| `GET` | `/api/setup/config` | Public Config | Public |
| `GET` | `/api/setup/status` | Setup Status | Public |
| `GET` | `/api/usage/admin` | Admin Usage | OAuth2PasswordBearer |
| `GET` | `/api/usage/admin.csv` | Admin Usage Csv | OAuth2PasswordBearer |
| `GET` | `/api/usage/admin/qr` | Admin Qr Png | OAuth2PasswordBearer |
| `GET` | `/api/usage/public` | Public Usage | Public |
| `GET` | `/api/usage/public.csv` | Public Usage Csv | Public |
| `GET` | `/api/version` | Api Version | Public |
| `GET` | `/api/workbook-answers` | List My Answers | OAuth2PasswordBearer |
| `GET` | `/api/workbook-answers/options` | Answer Options | OAuth2PasswordBearer |
| `GET` | `/api/workbook-answers/{lab_slug}` | Get My Answer | OAuth2PasswordBearer |
| `PUT` | `/api/workbook-answers/{lab_slug}` | Save My Answer | OAuth2PasswordBearer |
| `GET` | `/health` | Health | Public |

## Endpoint details

## About

### `GET /api/about`

**Get About**

Return the release inventory with live build and runtime values.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/about/licences/{name}`

**Get Licence**

Serve a project or third-party licence document.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `name` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/about/sbom/{name}`

**Get Sbom**

Serve a generated CycloneDX SBOM as a download.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `name` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Accommodations

### `GET /api/accommodations/me`

**Get My Accommodation**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/courses/{course_id}/students/{student_id}/accommodation`

**Clear Student Accommodation**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `student_id` | path | integer | yes |  |
| `reason` | query | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/students/{student_id}/accommodation`

**Get Student Accommodation**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `student_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/courses/{course_id}/students/{student_id}/accommodation`

**Set Student Accommodation**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `student_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `AccommodationUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `time_multiplier` | number | yes |  |
| `due_date_extension_days` | integer | yes |  |
| `notes` | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Admin

### `GET /api/admin/activity`

**Get Activity Log**

Get paginated activity log with optional event type and date range filters.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `page` | query | integer | no |  |
| `per_page` | query | integer | no |  |
| `event_type` | query | string or null | no |  |
| `start_date` | query | string or null | no |  |
| `end_date` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/activity/clear`

**Clear Activity Log**

Delete activity events, either all of them or those older than N days.  The action is written to the structured audit log and a new ``activity_log_cleared`` event is inserted so the activity feed shows that the log was cleared rather than looking silently truncated.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ActivityClearRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `confirm` | string | yes |  |
| `all` | boolean | no |  |
| `older_than_days` | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/activity/export`

**Export Activity Log**

Download the filtered activity log as JSON or CSV.  This is the archive path: export before clearing so the record survives outside the platform. The export itself is audited.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `format` | query | string | no |  |
| `event_type` | query | string or null | no |  |
| `start_date` | query | string or null | no |  |
| `end_date` | query | string or null | no |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/competency-coverage`

**Competency Coverage**

Read-only Release 6 coverage for the contract review queue.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/containers/cleanup-orphaned`

**Cleanup Orphaned Containers**

Clean up orphaned lab containers that aren't associated with active sessions

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/courses/{course_id}/retention`

**Get Retention Policy**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/admin/courses/{course_id}/retention`

**Set Retention Policy**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `RetentionPolicyRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `retention_until` | string or null | no |  |
| `note` | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/courses/{course_id}/retention/complete`

**Complete Retention**

Record the operator's completed purge after the documented runbook step.  The platform deliberately does not auto-delete learner records. The operator takes a backup, runs the documented purge, then records the reference here.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `RetentionCompleteRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `note` | string | no |  |
| `reference` | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/courses/{course_id}/retention/preview`

**Preview Retention**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/courses/{course_id}/retention/runs`

**List Retention Runs**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/data-labels/policy`

**Get Data Label Policy**

Return the effective label scheme, RBAC map, and export ceilings.  Use ``role`` and ``path`` to preview a decision before enabling enforcement. Invalid custom JSON is returned as a warning; the built-in scheme stays active until the setting is corrected.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `role` | query | string or null | no |  |
| `path` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/docker/disk-usage`

**Get Docker Disk Usage**

Return Docker disk usage broken down by images, containers, build cache, and volumes.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/docker/prune-build-cache`

**Prune Build Cache**

Remove Docker build cache to free disk space.  Future image builds will take longer as layers must be rebuilt from scratch.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/docker/prune-images`

**Prune All Images**

Remove all unused Docker images not referenced by running containers.  Exercises will rebuild their images on the next student launch.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/impersonate/disconnect`

**Disconnect Impersonation**

Disconnect admin's RangeBox from any impersonated student lab network.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/impersonate/launch`

**Impersonate Launch Lab**

Launch a lab AS a specific student, even if they aren't logged in. Creates a session under the student's user_id with their subnet, marks it as admin-initiated, and bridges the admin's RangeBox.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ImpersonateLaunchRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `user_id` | integer | yes |  |
| `lab_slug` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/impersonate/status`

**Impersonation Status**

Check if admin is currently impersonating a student session.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/impersonate/{session_id}`

**Impersonate Session**

Bridge the admin's standalone RangeBox to a student's lab network. Auto-disconnects from any previous impersonation.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/labs`

**List Labs**

List all labs with track and level information

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/labs`

**Create Lab**

Create a new lab from the web UI.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `LabCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `slug` | string | yes |  |
| `description` | string or null | no |  |
| `scenario` | string or null | no |  |
| `difficulty` | string | no |  |
| `category` | string | no |  |
| `duration_minutes` | integer | no |  |
| `level_id` | integer or null | no |  |
| `compose_file` | string | no |  |
| `objectives` | string or null | no |  |
| `prerequisites` | string or null | no |  |
| `mapped_skills` | string or null | no |  |
| `assessment_criteria` | string or null | no |  |
| `mitre_attack` | string or null | no |  |
| `hints` | string or null | no |  |
| `tools` | string or null | no |  |
| `hostnames` | string or null | no |  |
| `flag` | string or null | no |  |
| `visibility` | string or null | no |  |
| `lab_yaml` | string or null | no |  |
| `nice` | object or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/labs/bulk-toggle`

**Bulk Toggle Labs**

Enable or disable multiple labs at once

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `BulkToggleRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `lab_ids` | array[integer] | no |  |
| `is_active` | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/labs/discover`

**Discover Labs**

Scan the /labs directory for lab.yaml files and sync to database.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/labs/import`

**Import Exercise**

Import an exercise ZIP as a draft under a selected track and level.  If ``flag`` is blank, a new flag is generated and returned once in the response. The imported exercise is never published automatically.

**Authentication:** OAuth2PasswordBearer

**Request body** (`multipart/form-data`)

**Schema:** `Body_import_exercise_api_admin_labs_import_post`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | string | yes |  |
| `track` | string | yes |  |
| `level_id` | integer | yes |  |
| `name` | string or null | no |  |
| `flag` | string or null | no |  |
| `reuse_flag` | boolean | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/admin/labs/{lab_id}`

**Update Lab**

Update lab settings

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `app__schemas__lab__UpdateLabRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `description` | string or null | no |  |
| `difficulty` | string or null | no |  |
| `category` | string or null | no |  |
| `duration_minutes` | integer or null | no |  |
| `is_active` | boolean or null | no |  |
| `is_course_exclusive` | boolean or null | no |  |
| `is_course_available` | boolean or null | no |  |
| `visibility` | string or null | no |  |
| `level_id` | integer or null | no |  |
| `prerequisites` | string or null | no |  |
| `mapped_skills` | string or null | no |  |
| `assessment_criteria` | string or null | no |  |
| `mitre_attack` | string or null | no |  |
| `nice` | object or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/labs/{lab_id}/approve`

**Approve Lab**

Approve a lab: change visibility from 'pending_public' to 'public'.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/admin/labs/{lab_id}/compose`

**Update Lab Compose**

Update a lab's docker-compose file content.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `ComposeUpdateRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `compose_file` | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/labs/{lab_id}/details`

**Get Lab Details Admin**

Return full lab details including compose file and flag status.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/labs/{lab_id}/export`

**Export Exercise**

Download an exercise as a reusable authoring ZIP.  The flag is replaced with a placeholder unless ``include_flag=true`` is explicitly requested for a trusted backup.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |
| `include_flag` | query | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/admin/labs/{lab_id}/images`

**Delete Lab Images**

Delete cached Docker images for a specific exercise.  The exercise will rebuild its images on the next student launch.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/labs/{lab_id}/images`

**Get Lab Images**

List cached Docker images for a specific exercise.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/labs/{lab_id}/reject`

**Reject Lab**

Reject a lab: change visibility from 'pending_public' back to 'course'.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/labs/{lab_id}/toggle`

**Toggle Lab**

Enable or disable a lab

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/rangebox-capacity`

**Get Rangebox Capacity**

Return the RangeBox capacity policy and the last capacity test.  The live cap is ``rangebox_capacity_percent`` of the host's computed maximum. ``MAX_CONCURRENT_RANGEBOXES`` in the environment still pins an exact cap and takes precedence over the percentage.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/rangebox-capacity/test`

**Run Rangebox Capacity Test**

Run a Level 4 RangeBox ceiling test.  The test spawns the host's computed maximum by default so the result can be recorded as the measured ceiling and the live cap is recalculated from it. An administrator can pass a smaller ``users`` value for a quicker check, but that run is not used to lower the production ceiling.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** object or null

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/retention/due`

**List Retention Due**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/sessions/active`

**List Active Sessions**

List active lab sessions.  Without ``page``/``per_page`` this keeps the original array response; supplying either returns a page envelope with totals.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `page` | query | integer or null | no |  |
| `per_page` | query | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/sessions/health`

**Get Sessions Health**

Get live container health for all active sessions. Returns detailed container status, resource usage, health status, VPN connectivity, stale detection, and container IPs.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/admin/sessions/history`

**Clear Session History**

Clear session history (non-running sessions only) - rate limited to 5 per minute

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `status_filter` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/sessions/history`

**Session History**

Get paginated session history with optional date range filters.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `page` | query | integer | no |  |
| `per_page` | query | integer | no |  |
| `start_date` | query | string or null | no |  |
| `end_date` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/sessions/terminate-all`

**Terminate All Sessions**

Emergency: terminate all running sessions - rate limited to 2 per minute

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/sessions/terminate/{session_id}`

**Terminate Session**

Terminate a specific lab session.  Sync on purpose: destroy_lab_environment performs blocking Docker calls. FastAPI runs sync endpoints in the threadpool, so one teardown cannot freeze the event loop and the health probe.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/sessions/{session_id}/logs`

**Get Session Logs**

Get container logs for a lab session.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | integer | yes |  |
| `tail` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/sessions/{session_id}/reset-stale`

**Reset Stale Session**

Reset a stale session (DB says running but containers are gone).

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/sessions/{session_id}/resync-vpn`

**Resync Session Vpn**

Re-sync VPN peer for a session's user.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/stats`

**Get Stats**

Get platform or institution statistics.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/stress-test`

**Start Stress Test**

Launch a stress test in the background.  Body:     level: 1\|2\|3\|4     users: int (default 45)     concurrent_spawns: int (default 5, level 3/4 only)     lab_slug: str\|null

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `StressTestRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `level` | integer | no |  |
| `users` | integer | no |  |
| `concurrent_spawns` | integer | no |  |
| `lab_slug` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/stress-test/active`

**Get Active Stress Test**

Return the currently active stress test (if any).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/stress-test/cancel`

**Cancel Stress Test**

Cancel a running stress test.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `StressCancelRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `run_id` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/stress-test/cleanup`

**Stress Test Cleanup**

Clean up stress test users and data from the database.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/stress-test/events/{run_id}`

**Get Stress Test Events**

Return events for a stress test run starting after index `after`.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `run_id` | path | string | yes |  |
| `after` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/stress-test/last-result`

**Get Last Stress Result**

Return the most recent completed/cancelled stress test results.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/stress-test/report`

**Generate Stress Report Pdf**

Generate a PDF report from stress test results.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Request body** (`application/json`)

**Schema:** object

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/system/activity-calendar`

**Activity Calendar**

Return daily event data for the backup heatmap (last 12 months).  Each day includes change/backup counts and the latest timestamp for each, so the frontend can detect same-day backup-then-change ordering.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/system/backup`

**Create Backup**

Create a database backup (pg_dump).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/system/backups`

**List Backups**

List available database backups.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/admin/system/backups/{filename}`

**Delete Backup**

Delete a specific backup file.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `filename` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/system/backups/{filename}`

**Download Backup**

Download a specific backup file.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `filename` | path | string | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/system/data-integrity`

**Get Data Integrity Status**

Live, read-only summary of the append-only integrity ledger.  Full chain verification, data-quality checks, and signed checksum manifests run from the host schedule so they do not compete with request traffic.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/system/data-integrity/review`

**Review Data Integrity Write**

Record an administrator review of an unattributed ledger write.  The ledger itself is append-only. This endpoint only adds a signed-in reviewer's decision and reason; it never edits or removes evidence.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `IntegrityReviewRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `table` | string | yes |  |
| `operation` | string | yes |  |
| `decision` | `expected` | `investigated` | `escalated` | yes |  |
| `note` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/system/metrics`

**Get System Metrics**

Sampled host/platform metrics for the admin System graphs.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `hours` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/system/metrics/sample`

**Sample System Metrics**

Take a metrics sample now (the scheduler also samples every minute).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/system/release`

**Compare this installation with the latest GitHub release**

Return the installed version, latest GitHub release, and upgrade path.  The result is cached for 15 minutes. A GitHub outage returns the last good result as stale, or ``unknown`` on a first check; the admin page keeps working either way. This endpoint never deploys or changes anything.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `force` | query | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/system/restore`

**Restore Backup**

Restore the database from a snapshot already on this install.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `RestoreRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `filename` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/system/restore/upload`

**Restore Uploaded Backup**

Accept a plain SQL snapshot from another installation.  The file is saved into the normal snapshot directory. With ``restore_now`` it is applied immediately in one transaction; otherwise it is left in the list so an administrator can restore it later. A full restore replaces every account, so the caller should warn before using this across versions.

**Authentication:** OAuth2PasswordBearer

**Request body** (`multipart/form-data`)

**Schema:** `Body_restore_uploaded_backup_api_admin_system_restore_upload_post`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | string | yes |  |
| `restore_now` | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/system/software-integrity`

**Verify deployed lab content against the release manifest**

Recompute the lab content hashes and compare them with the release manifest.  The manifest is generated from supply-chain.lock.json at build time. This is the runtime half of the supply-chain check: it proves the mounted lab tree still matches the reviewed release and reports the running image digest and build revision for the audit trail.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/system/status`

**System Status**

Minimal, plain-language status for non-technical admins. Every item is derived from THIS install (the database, the entitlement, this instance's own disk) rather than the whole Docker daemon or hardcoded assumptions, so it never reports on content that is not loaded and does not drift between OCR-Lite and OCR-Enterprise. The deep firewall/network/security diagnostics live in the Advanced section, not here.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/users`

**List Users**

List users without side effects.  A platform admin sees every institution; an institution admin sees only its own tenant. Without ``page``/``per_page`` this keeps the original array response; supplying either returns a page envelope with totals.  VPN state is refreshed by the dedicated ``/vpn/sync`` endpoint and the scheduler, not by this GET: a read must not call Peer Manager or write to the database.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `page` | query | integer or null | no |  |
| `per_page` | query | integer or null | no |  |

**Responses**

- `200`: Successful Response — array[`UserAdminResponse`] or `UserPage`
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/users/approve`

**Approve User**

Approve or reject a user

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | query | integer | yes |  |
| `approved` | query | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/users/create`

**Create User**

Create a new user - rate limited to 5 per minute

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `CreateUserRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `username` | string | yes |  |
| `email` | string | yes |  |
| `student_id` | string or null | no |  |
| `first_name` | string or null | no |  |
| `last_name` | string or null | no |  |
| `password` | string | yes |  |
| `is_approved` | boolean | no |  |
| `is_admin` | boolean | no |  |
| `role` | string or null | no |  |
| `institution_id` | string or null | no |  |
| `age_band` | `under_13` | `13_15` | `16_17` | `18_plus` or null | no |  |
| `parental_consent_reference` | string or null | no |  |

**Responses**

- `200`: Successful Response — `UserAdminResponse`
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/users/export`

**Export Users**

Download every account as a portable JSON file.  Password hashes are included so migrated users keep their existing passwords. MFA, trusted devices, VPN peers, sessions, and learning progress are intentionally excluded. Treat the download as sensitive.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `include_avatars` | query | boolean | no |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/users/import`

**Import Users**

Import accounts from a portable export.  ``dry_run`` validates the file and reports what would happen without writing. ``update`` replaces matching usernames instead of skipping them.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** object

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/users/locked`

**List Locked Users**

List locked accounts in the actor's institution.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response — array[`UserAdminResponse`]

### `GET /api/admin/users/pending`

**List Pending Users**

List users awaiting approval in the actor's institution.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response — array[`UserAdminResponse`]

### `DELETE /api/admin/users/{user_id}`

**Delete User**

Erase an account and its personal data.  Refuses when the account owns courses (transfer them first) or is the last usable administrator. The audit record keeps the admin identity, action and timestamp but not the erased person's identifier.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/users/{user_id}`

**Get User**

Get a specific user in the actor's institution.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response — `UserAdminResponse`
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/admin/users/{user_id}`

**Update User**

Update user details

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `UpdateUserRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `username` | string or null | no |  |
| `email` | string or null | no |  |
| `password` | string or null | no |  |
| `first_name` | string or null | no |  |
| `last_name` | string or null | no |  |
| `organization` | string or null | no |  |
| `institution_id` | string or null | no |  |
| `is_active` | boolean or null | no |  |
| `is_approved` | boolean or null | no |  |
| `is_admin` | boolean or null | no |  |
| `role` | string or null | no |  |
| `must_change_password` | boolean or null | no |  |
| `age_band` | `under_13` | `13_15` | `16_17` | `18_plus` or null | no |  |
| `parental_consent_reference` | string or null | no |  |

**Responses**

- `200`: Successful Response — `UserAdminResponse`
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/users/{user_id}/details`

**Get User Details**

Get detailed user information with completions and statistics

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response — `UserDetailResponse`
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/users/{user_id}/force-logout`

**Force Logout User**

Revoke all active JWT tokens for a user, forcing them to re-authenticate.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/users/{user_id}/labs/{lab_id}/reset`

**Reset User Lab**

Reset a lab for a user, allowing them to replay it

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/users/{user_id}/mfa/reset`

**Reset another account's MFA**

Reset MFA after a fresh password + MFA reauthentication.  The operator must prove possession of their own credentials, the reason is recorded, and the target's sessions and refresh families are revoked. This is the supported recovery path for a lost authenticator; there is no unauthenticated reset endpoint.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `MfaResetRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | string | yes |  |
| `admin_password` | string | yes |  |
| `totp_code` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/users/{user_id}/reset-password`

**Reset Password**

Reset another user's password after re-authenticating the admin.  This is deliberately separate from the general profile update. The action re-checks the admin password, revokes every target session, forces a password change, and writes a PASSWORD_RESET audit record.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `ResetPasswordRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `new_password` | string | yes |  |
| `admin_password` | string | yes |  |
| `must_change_password` | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/users/{user_id}/unlock`

**Unlock User**

Unlock a locked user account

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/admin/vpn/peer-by-key/{public_key}`

**Remove Vpn Peer By Key**

Remove a VPN peer from Peer Manager by public key (for unknown peers)

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `public_key` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/admin/vpn/peer/{user_id}`

**Remove Vpn Peer**

Remove a user's VPN peer from Peer Manager

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/vpn/peers`

**List Vpn Peers**

List all VPN peers from Peer Manager - returns empty list if API unavailable.  Each peer is annotated with a `health` field:   - 'ok': peer is registered correctly   - 'no_allowed_ips': peer exists but allowed_ips is empty/(none) — WG drops all its traffic   - 'duplicate_for_ip': another peer (not this one) holds the IP the DB expects for its user   - 'orphan_no_db': peer is registered on WG but has no matching DB row

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `page` | query | integer or null | no |  |
| `per_page` | query | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/vpn/peers/{user_id}/repair`

**Repair Vpn Peer**

Re-assert WireGuard registration for a user from DB truth.  Removes any peer on the WG server whose public key matches the DB row OR whose allowed_ips matches the DB client_ip (catches stale duplicates), then re-adds the DB peer with the correct allowed_ips. Use this when a user can handshake but their traffic is dropped (allowed_ips=(none)) or when a stale duplicate has stolen their IP slot.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/vpn/reconcile-peers`

**Reconcile Vpn Peers**

Prune dead and duplicate WireGuard peers from wg0.  Historical allocator churn (re-downloads that minted a new key, formula changes, deleted users) can leave orphan peers on wg0 that no live config owns, and stale-IP peers squatting on an address now assigned to someone else. Both break connectivity for the rightful owner (allowed_ips is exclusive per peer). This reconciles wg0 against wireguard_configs: it removes orphans and repairs IP mismatches.  Defaults to a DRY RUN (reports what it would change, touches nothing). Pass ?apply=true to actually prune and repair. `missing` (DB configs with no live peer) is reported for visibility; use the per-user resync to re-add those.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `apply` | query | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/vpn/register/{user_id}`

**Register Vpn Peer**

Manually register a user's VPN peer with Peer Manager

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/vpn/status`

**Vpn Sync Status**

Get VPN sync status - compare DB to Peer Manager.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `page` | query | integer or null | no |  |
| `per_page` | query | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/vpn/sync`

**Sync Vpn Peers**

Sync all user VPN configs to Peer Manager

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

## Analytics

### `GET /api/analytics/courses/{course_id}/competency`

**Course Competency**

Cohort competency radar with median, IQR, target, and drill-down.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/courses/{course_id}/exercises`

**Course Exercises**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/analytics/courses/{course_id}/labs/{lab_id}/reviews`

**Add Lab Health Review**

Record a lab-health review and its outcome.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `lab_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `ReadinessLabReviewRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | `healthy` | `warning` | `degraded` | `no_data` | yes |  |
| `finding` | string or null | no |  |
| `action` | string or null | no |  |
| `outcome` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/courses/{course_id}/overview`

**Course Overview**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/courses/{course_id}/pulse-comments`

**Course Pulse Comments**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/courses/{course_id}/readiness`

**Course Readiness**

Pilot instructor support queue and lab health for one course.  The response is descriptive and provisional. It does not rank learners publicly, predict grades, or make an automated decision.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/courses/{course_id}/readiness/calibration`

**Readiness Calibration**

Aggregate the pilot's bands, flags, actions, outcomes, and lab reviews.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/courses/{course_id}/students/{user_id}/capabilities`

**Student Capabilities**

Capability detail for one enrolled learner in the actor's course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/analytics/courses/{course_id}/students/{user_id}/notes`

**Add Readiness Note**

Record context, a support action, a flag state, or a case update.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `user_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `ReadinessNoteRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `kind` | `context` | `flag_state` | `action` | `case` | `calibration` | yes |  |
| `key` | string | yes |  |
| `state` | `dismissed` | `snoozed` | `acknowledged` | `open` | `closed` | `confirmed` | `partly_confirmed` | `not_confirmed` | `insufficient_context` or null | no |  |
| `note` | string or null | no |  |
| `outcome` | string or null | no |  |
| `start_at` | string or null | no |  |
| `end_at` | string or null | no |  |
| `follow_up_at` | string or null | no |  |
| `owner_id` | integer or null | no |  |
| `priority` | `low` | `normal` | `high` or null | no |  |
| `band` | `critical_intervention` | `high_risk` | `elevated` | `monitor` | `healthy` or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/analytics/events/workbook-open`

**Workbook Opened**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `WorkbookOpenRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string or null | no |  |
| `url` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/metrics`

**Metric Dictionary**

One definition set shared by the UI, exports, and documentation.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/analytics/pulse/{lab_id}`

**Get Pulse**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/analytics/pulse/{lab_id}`

**Submit Pulse**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `PulseSurveyRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `difficulty` | integer | yes |  |
| `learning` | integer | yes |  |
| `unclear` | string or null | no |  |
| `topic_interest` | string or null | no |  |
| `course_id` | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/reaction/{lab_id}`

**Get Exercise Reaction**

Return the signed-in learner's own reaction to an exercise.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/analytics/reaction/{lab_id}`

**Set Exercise Reaction**

Create, change, or clear a learner's reaction to an exercise.  One reaction is kept per learner and exercise. Passing ``null`` clears it. Reports only aggregate likes and dislikes; they never show who reacted.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `ExerciseReactionRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `reaction` | string or null | no |  |
| `course_id` | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/reports/activity`

**Reports Activity**

Period-scoped aggregate activity across the visible courses.  This is separate from the all-time catalog snapshot. It answers "what happened in this window?" and never names or ranks a learner. Small cohorts are suppressed using the same minimum as the course analytics.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `start` | query | string or null | no |  |
| `end` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/reports/curriculum-demand`

**Curriculum Demand**

Aggregate telemetry turned into where-to-build-next prompts.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/analytics/reports/export-audit`

**Audit Report Export**

Record why a report was exported.  The CSV is assembled in the browser from data the instructor can already see, so this endpoint exists to keep the compliance trail complete. The PDF path records the same fields directly in ``reports_export_pdf``.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ReportExportAuditRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `format` | string | yes |  |
| `reason` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/reports/export.pdf`

**Reports Export Pdf**

Download the cross-course report as a PDF.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `range_label` | query | string or null | no |  |
| `start` | query | string or null | no |  |
| `end` | query | string or null | no |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/reports/overview`

**Reports Overview**

Cross-course reporting landing data for instructors and admins.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/analytics/student/me`

**Student Analytics**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/analytics/surveys`

**List Surveys**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/analytics/surveys`

**Create Survey**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `SurveyCreateInput`

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | yes |  |
| `description` | string or null | no |  |
| `questions` | array[`SurveyQuestionInput`] | yes |  |
| `course_ids` | array[integer] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/surveys/available`

**Available Surveys**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/analytics/surveys/{survey_id}`

**Delete Survey**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `survey_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/analytics/surveys/{survey_id}/responses`

**Survey Responses**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `survey_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/analytics/surveys/{survey_id}/responses`

**Submit Survey Response**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `survey_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `SurveyResponseInput`

| Field | Type | Required | Description |
|---|---|---|---|
| `answers` | object | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Audit

### `GET /api/admin/audit/impersonations`

**Admin Impersonation Sessions**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `live_only` | query | boolean | no |  |
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/audit/users/by-username/{username}/history`

**Admin User History By Username**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `username` | path | string | yes |  |
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/audit/users/{user_id}/history`

**Admin User History**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/students/{user_id}/history`

**Course Student History**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `user_id` | path | integer | yes |  |
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Authentication

### `POST /api/auth/change-password`

**Change Password**

Change user password - rate limited to 5 per minute

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ChangePasswordRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `current_password` | string | yes |  |
| `new_password` | string | yes |  |
| `confirm_password` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/delete-account`

**Delete My Account**

Permanently erase the signed-in account and its personal data.  Requires the current password, a live TOTP code (or an unused recovery code) when MFA is enabled, and the literal confirmation ``DELETE``.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `DeleteAccountRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `password` | string | yes |  |
| `code` | string or null | no |  |
| `confirm` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/delete-request`

**Request Account Deletion**

Retired no-op endpoint.  It previously claimed to record a request while only writing a log line. Self-service deletion is now immediate and authenticated; keep this route so older clients get a clear instruction instead of a silent no-op.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `410`: Successful Response

### `GET /api/auth/export`

**Export User Data**

Return the account holder's personal data in a portable JSON document.  Secrets are deliberately excluded (password hash, TOTP secret, recovery codes, trusted-device tokens and the WireGuard private key). Everything else the platform holds about the account is included so this can serve as the response to a subject-access request.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/auth/export-status`

**Export Status**

Return when the account last downloaded a copy of its data.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/auth/forgot-password`

**Forgot Password**

Send a one-time reset link to an eligible local account.  The response never reveals whether the address exists. Accounts created only through SSO, inactive accounts, and unapproved accounts receive no message because they cannot use the local password form.

**Authentication:** Public

**Request body** (`application/json`)

**Schema:** `PasswordResetRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/forgot-username`

**Forgot Username**

Email the username to the address already on the account.  The response is always the same, whether or not the address is registered, so this endpoint cannot be used to enumerate accounts. Mail is sent to the address supplied only after it matches an account; no other address is ever used.

**Authentication:** Public

**Request body** (`application/json`)

**Schema:** `UsernameReminderRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/impersonate`

**Start Impersonation**

Start an impersonation session.  Modes:   1. target_user_id set          → impersonate a specific user (admin only)   2. target_role + course_id set  → synthetic student in a course (admin or instructor-of-course)   3. target_role only             → generic role view (admin only)

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ImpersonateRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `target_user_id` | integer or null | no |  |
| `target_role` | string or null | no |  |
| `course_id` | integer or null | no |  |

**Responses**

- `200`: Successful Response — `ImpersonateResponse`
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/impersonate/exit`

**Exit Impersonation**

Exit impersonation and return a fresh token for the original user.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/auth/login`

**Login**

Login endpoint - rate limited to 10 attempts per minute

**Authentication:** Public

**Request body** (`application/x-www-form-urlencoded`)

**Schema:** `Body_login_api_auth_login_post`

| Field | Type | Required | Description |
|---|---|---|---|
| `totp_code` | string or null | no |  |
| `grant_type` | string or null | no |  |
| `username` | string | yes |  |
| `password` | string | yes |  |
| `scope` | string | no |  |
| `client_id` | string or null | no |  |
| `client_secret` | string or null | no |  |

**Responses**

- `200`: Successful Response — `Token`
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/logout`

**Logout**

Revoke the presented token so it stops working on every worker.  Revocation is DB-backed (revoked_tokens table), so a logged-out token is dead platform-wide, not just on the worker that handled this request.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/auth/me`

**Get Current User Info**

Get current user information - syncs VPN registration status with Peer Manager. When impersonating, returns the effective (impersonated) identity with metadata.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/auth/me/impersonation`

**Get Impersonation Status**

Return impersonation metadata for the current session.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/auth/mfa/disable`

**Disable Mfa**

Turn MFA off. Requires the account password AND a current TOTP code, so a hijacked session alone cannot strip the second factor.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `MfaDisableRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `password` | string | yes |  |
| `code` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/mfa/enroll`

**Enroll Mfa**

Start TOTP enrollment: generate a secret and return the otpauth URI.  The secret is stored Fernet-encrypted; mfa_enabled stays False until the user proves possession via /mfa/verify. Re-calling before verification rotates the pending secret.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/auth/mfa/recovery-codes`

**Generate Recovery Codes**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/auth/mfa/recovery-codes/verify`

**Verify Recovery Code**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `RecoveryCodeVerifyRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `code` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/mfa/verify`

**Verify Mfa**

Confirm TOTP enrollment with a code from the authenticator app.  First valid code flips mfa_enabled on; later calls just report state.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `MfaCodeRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `code` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/reauth`

**Reauthenticate**

Open the short reauthentication window for sensitive operations.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ReauthRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `password` | string | yes |  |
| `totp_code` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/refresh`

**Refresh Access Token**

Rotate a refresh token and issue a new access/refresh pair.  A rotated token is single-use. Replaying it revokes the whole rotation family and the bound session, then returns 401.

**Authentication:** Public

**Request body** (`application/json`)

**Schema:** `RefreshRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `refresh_token` | string | yes |  |

**Responses**

- `200`: Successful Response — `Token`
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/register`

**Register**

Register a new user.  Per-IP limits are strict normally (5/minute; 30/hour; 100/day) and relax to a burst allowance (20/minute; 120/hour; 400/day) from ``EVENT_BURST_BUFFER_MINUTES`` before a competition starts until the same margin after it ends. The invite-code and approval gates remain the controls that decide *who* may register.

**Authentication:** Public

**Request body** (`application/json`)

**Schema:** `RegisterRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `username` | string | yes |  |
| `email` | string | yes |  |
| `student_id` | string or null | no |  |
| `first_name` | string or null | no |  |
| `last_name` | string or null | no |  |
| `organization` | string or null | no |  |
| `password` | string | yes |  |
| `invite_code` | string or null | no |  |
| `competition_id` | integer or null | no |  |
| `send_registration_email` | boolean | no |  |
| `is_minor` | boolean | no |  |
| `age_band` | `under_13` | `13_15` | `16_17` | `18_plus` or null | no |  |
| `privacy_acknowledged` | boolean | no |  |
| `source` | string or null | no |  |
| `campaign` | string or null | no |  |

**Responses**

- `200`: Successful Response — `UserResponse`
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/reset-password`

**Reset Password**

Consume a reset link and set the new password.  The link is bound to the current password hash, so a successful reset (or any other password change) invalidates it immediately. Every existing session is revoked after the reset.

**Authentication:** Public

**Request body** (`application/json`)

**Schema:** `PasswordResetConfirm`

| Field | Type | Required | Description |
|---|---|---|---|
| `token` | string | yes |  |
| `new_password` | string | yes |  |
| `confirm_password` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/auth/sessions`

**List Sessions**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/auth/sessions/revoke-all`

**Revoke All Sessions**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/auth/sessions/{session_id}`

**Revoke One Session**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/auth/settings`

**Get User Settings**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `PUT /api/auth/settings`

**Update User Settings**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `UserSettingsUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `first_name` | string or null | no |  |
| `last_name` | string or null | no |  |
| `organization` | string or null | no |  |
| `avatar_data` | string or null | no |  |
| `avatar_border_style` | `none` | `solid` | `dashed` | `double` | `glow` | `gradient` or null | no |  |
| `avatar_border_color` | string or null | no |  |
| `timezone` | string or null | no |  |
| `show_on_scoreboard` | boolean or null | no |  |
| `scoreboard_name_mode` | `real_name` | `username` | `anonymous` or null | no |  |
| `login_notifications` | boolean or null | no |  |
| `email_notifications` | boolean or null | no |  |
| `notification_prefs` | object or null | no |  |
| `show_hidden_achievements` | boolean or null | no |  |
| `certificates_public` | boolean or null | no |  |
| `is_minor` | boolean or null | no |  |
| `privacy_acknowledged` | boolean or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/auth/survey-consent`

**Get Survey Consent**

Return the account's survey opt-in state and the current statement.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/auth/survey-consent`

**Update Survey Consent**

Record an explicit survey opt-in or withdrawal.  Opting in requires the caller to have reviewed the current statement. Every change is appended to ``survey_consent_events`` with the statement version so the consent decision remains auditable after the user row changes.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `SurveyConsentUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `opt_in` | boolean | yes |  |
| `policy_version` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/auth/wiki-access`

**Check Wiki Access**

Validate wiki access for a specific path.  Nginx sends the original URI via X-Original-URI header.  Course-specific chapters (``/wiki/course/<slug>/...``, or any path that resolves to a lab with visibility='course') require the user to be enrolled in, or to be instructing, a course that assigns that lab.  Any other wiki path is open to every authenticated user.  Returns 200 if allowed, raises 403 if denied.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/auth/wiki-admin-access`

**Check Wiki Admin Access**

Validate admin-only wiki access.  Used by nginx auth_request for /wiki-admin/ paths. Returns 200 if the user is an admin, raises 403 otherwise.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/auth/wiki-cookie`

**Clear Wiki Cookie**

Remove the HttpOnly wiki cookie on logout or account deletion.

**Authentication:** Public

**Responses**

- `204`: Successful Response

### `POST /api/auth/wiki-cookie`

**Issue Wiki Cookie**

Copy the caller's JWT into an HttpOnly wiki cookie.  The browser keeps the SPA token in localStorage. This endpoint gives the wiki origin a cookie it can use for nginx auth_request without exposing a script-readable token to the framed page. The cookie is scoped by WIKI_COOKIE_DOMAIN so a sibling wiki hostname receives it; leave that unset for a same-origin wiki.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `204`: Successful Response

### `GET /api/auth/wiki-released`

**Wiki Released Chapters**

Chapter directories of a course wiki this user may open right now.  Feeds the workbook's own navigation so a learner is not shown links that the release gate will refuse. Purely cosmetic: /wiki-access is still the enforcement point, and hiding a link protects nothing on its own.  Returns every chapter when the caller is staff or the course has no schedule, which matches the gate's permissive default.  Authenticates from the ``wiki_auth`` cookie as well as a bearer header. The caller is a script running inside a workbook page, which carries the wiki cookie and no Authorization header; nginx only rewrites that cookie into a bearer for its internal auth_request locations, not for /api. Taking the header alone made this 401 for every learner, and since the script fails open the navigation then listed every chapter as though nothing was gated.

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `slug` | query | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Competencies

### `GET /api/competencies/{competency_id}/evidence`

**Competency Evidence**

Evidence linked to one competency, scoped to the caller.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competency_id` | path | string | yes |  |
| `learner_id` | query | integer or null | no |  |
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Competitions

### `GET /api/competitions`

**List Competitions**

List competitions. Inactive events are hidden from students.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/competitions`

**Create Competition**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `CompetitionCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `description` | string or null | no |  |
| `logo_data` | string or null | no |  |
| `start_at` | string | yes |  |
| `end_at` | string | yes |  |
| `lab_ids` | array[integer] | yes |  |
| `sponsors` | array[`CompetitionSponsorInput`] | no |  |
| `experience_key` | string or null | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/competitions/public/{competition_id}`

**Public Competition**

Minimal public event information for a competition sign-up link.

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/competitions/{competition_id}`

**Delete Competition**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/competitions/{competition_id}`

**Get Competition**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PATCH /api/competitions/{competition_id}`

**Update Competition**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CompetitionUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `description` | string or null | no |  |
| `logo_data` | string or null | no |  |
| `start_at` | string or null | no |  |
| `end_at` | string or null | no |  |
| `lab_ids` | array[integer] or null | no |  |
| `sponsors` | array[`CompetitionSponsorInput`] or null | no |  |
| `is_active` | boolean or null | no |  |
| `experience_key` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/competitions/{competition_id}/archive`

**Archive Competition**

Archive an event: keep every result, hide it from the default list.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/competitions/{competition_id}/certificate/{award}`

**Get Event Certificate**

Return one event certificate as JSON or a downloadable PDF.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |
| `award` | path | string | yes |  |
| `format` | query | `json` | `pdf` | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/competitions/{competition_id}/certificates`

**List Event Certificates**

List the participation, placement, and trophy certificates a learner earned.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/competitions/{competition_id}/discovery`

**Get Event Discovery**

Return the Cyber Discovery layer for an event, if the event has one.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/competitions/{competition_id}/discovery/overview`

**Get Event Discovery Overview**

Aggregate event participation for the organiser, with suppression.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/competitions/{competition_id}/join`

**Join Competition**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/competitions/{competition_id}/leave`

**Leave Competition**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/competitions/{competition_id}/unarchive`

**Unarchive Competition**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competition_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Consent

### `GET /api/consent/`

**Learner consent and revocation status**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/consent/admin/enforce-suppressions`

**Apply the suppression ledger**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/consent/admin/metrics`

**Revocation verification metrics**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/consent/admin/revocations`

**All revocation workflows**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `status` | query | string or null | no |  |
| `consent_type` | query | string or null | no |  |
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/consent/admin/run-jobs`

**Run due purge and verification jobs**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `RunJobsRequest` or null

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/consent/revocations`

**The learner's own revocation history**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/consent/types`

**Available consent types**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/consent/{consent_type}/grant`

**Grant Consent**

Re-enable a feature. Previously deleted data stays deleted.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `consent_type` | path | string | yes |  |

**Request body** (`application/json`)

**Schema:** `ConsentGrantRequest` or null

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/consent/{consent_type}/revoke`

**Revoke Consent**

Immediately block a feature and queue destructive cleanup.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `consent_type` | path | string | yes |  |

**Request body** (`application/json`)

**Schema:** `ConsentRevokeRequest` or null

**Responses**

- `202`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Course planning

### `PUT /api/courses/{course_id}/cohort-settings`

**Update Cohort Settings**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CohortSettingsUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `strict` | boolean | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/cohorts`

**Create Cohort**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CohortCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `description` | string or null | no |  |
| `is_default` | boolean | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/cohorts/sync-default`

**Sync Default Cohort Members**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/courses/{course_id}/cohorts/{cohort_id}`

**Delete Cohort**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `cohort_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PATCH /api/courses/{course_id}/cohorts/{cohort_id}`

**Update Cohort**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `cohort_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CohortUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `description` | string or null | no |  |
| `is_default` | boolean or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/courses/{course_id}/cohorts/{cohort_id}/members`

**Set Cohort Members**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `cohort_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `MembersRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `user_ids` | array[integer] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/exercise-sets`

**Create Set**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `SetCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `description` | string or null | no |  |
| `sort_order` | integer | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/courses/{course_id}/exercise-sets/{set_id}`

**Delete Set**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `set_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PATCH /api/courses/{course_id}/exercise-sets/{set_id}`

**Update Set**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `set_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `SetUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `description` | string or null | no |  |
| `sort_order` | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/courses/{course_id}/exercise-sets/{set_id}/items`

**Set Items**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `set_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `SetItemsRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `items` | array[`SetItem`] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/planning`

**Get Planning**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/planning/coverage`

**Get Coverage**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/requirements`

**Create Requirement**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `RequirementCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `cohort_id` | integer | yes |  |
| `set_id` | integer | yes |  |
| `rule_type` | string | no |  |
| `threshold` | integer or null | no |  |
| `due_at` | string or null | no |  |
| `note` | string or null | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/courses/{course_id}/requirements/{requirement_id}`

**Delete Requirement**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `requirement_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PATCH /api/courses/{course_id}/requirements/{requirement_id}`

**Update Requirement**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `requirement_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `RequirementUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `cohort_id` | integer or null | no |  |
| `set_id` | integer or null | no |  |
| `rule_type` | string or null | no |  |
| `threshold` | integer or null | no |  |
| `due_at` | string or null | no |  |
| `note` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Courses

### `GET /api/courses/`

**List Courses**

List courses. Admins see all; instructors see own courses; students see enrolled only.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/courses/`

**Create Course**

Create a new course. Admin only.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `CourseCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `code` | string | yes |  |
| `semester` | string | yes |  |
| `description` | string or null | no |  |
| `start_date` | string | yes |  |
| `end_date` | string | yes |  |
| `instructor_id` | integer or null | no |  |
| `wiki_theme_color` | string or null | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/join`

**Join Course**

Join a course via invite code.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `CourseJoinRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `invite_code` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/courses/{course_id}`

**Delete Course**

Delete a course. Must be the instructor.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}`

**Get Course**

Get course detail with assigned labs.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/courses/{course_id}`

**Update Course**

Update a course. Must be the instructor.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CourseUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `code` | string or null | no |  |
| `semester` | string or null | no |  |
| `description` | string or null | no |  |
| `start_date` | string or null | no |  |
| `end_date` | string or null | no |  |
| `is_active` | boolean or null | no |  |
| `is_archived` | boolean or null | no |  |
| `instructor_id` | integer or null | no |  |
| `wiki_theme_color` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/achievements`

**List Achievements**

List all achievements in a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/archive`

**Archive Course**

Archive a course. Sets is_archived=True and is_active=False.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/assignments`

**List Assignments**

List assignments for a course with labs and completion stats.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/assignments`

**Create Assignment**

Create a new assignment within a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `AssignmentCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `description` | string or null | no |  |
| `due_date` | string or null | no |  |
| `start_date` | string or null | no |  |
| `locked` | boolean or null | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/courses/{course_id}/assignments/reorder`

**Reorder Assignments**

Reorder assignments in a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `AssignmentReorderRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `assignment_order` | array[object] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/courses/{course_id}/assignments/{assignment_id}`

**Delete Assignment**

Delete an assignment (labs remain assigned to the course).

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `assignment_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/courses/{course_id}/assignments/{assignment_id}`

**Update Assignment**

Update an assignment's name, description, or due date.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `assignment_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `AssignmentUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `description` | string or null | no |  |
| `due_date` | string or null | no |  |
| `start_date` | string or null | no |  |
| `locked` | boolean or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/assignments/{assignment_id}/labs`

**Add Labs To Assignment**

Add labs to an assignment. Auto-assigns labs to the course if needed.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `assignment_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `AssignmentLabsRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `lab_ids` | array[integer] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/courses/{course_id}/assignments/{assignment_id}/labs/{lab_id}`

**Remove Lab From Assignment**

Remove a lab from an assignment (lab stays assigned to the course).

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `assignment_id` | path | integer | yes |  |
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/assignments/{assignment_id}/report`

**Assignment Class Report**

Generate PDF class report scoped to a specific assignment.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `assignment_id` | path | integer | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/assignments/{assignment_id}/report/{user_id}`

**Assignment Student Report**

Generate PDF student report scoped to a specific assignment.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `assignment_id` | path | integer | yes |  |
| `user_id` | path | integer | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/enroll-bulk`

**Enroll Students Bulk**

Admin bulk-enrolls multiple students in a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `BulkEnrollRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `user_ids` | array[integer] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/courses/{course_id}/enroll/{user_id}`

**Remove Student**

Remove a student from a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/feedback`

**Submit Course Feedback**

Submit a student course check-in or an instructor coaching note.  Students update their own single check-in. Instructors address one enrolled student per note and may update it. Student rows keep the author internally for duplicate prevention but are aggregated anonymously for instructors.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CourseFeedbackRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `clarity` | integer or null | no |  |
| `challenge` | integer or null | no |  |
| `engagement` | integer or null | no |  |
| `confidence` | integer or null | no |  |
| `comment` | string or null | no |  |
| `subject_user_id` | integer or null | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/feedback/me`

**My Course Feedback**

Return the current user's own check-in and coaching notes.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/feedback/summary`

**Course Feedback Summary**

Return the private two-way feedback analysis for a course.  Existing exercise pulse surveys and reactions are included immediately, so the dashboard is useful before anyone submits a new course check-in.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/labs`

**Assign Labs**

Assign labs to a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CourseLabAssignRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `lab_ids` | array[integer] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/labs/bulk-remove`

**Remove several exercises from a course**

Remove multiple exercises from a course in one request.  Used by the instructor panel's multi-select action. Labs that are not assigned to the course are ignored so a stale selection cannot fail the whole batch.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CourseLabBulkRemoveRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `lab_ids` | array[integer] | yes |  |

**Responses**

- `200`: Number of assignments removed
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/courses/{course_id}/labs/reorder`

**Reorder Labs**

Reorder labs in a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CourseLabReorderRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `lab_order` | array[object] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/courses/{course_id}/labs/{lab_id}`

**Remove Lab**

Remove a lab from a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/courses/{course_id}/labs/{lab_id}`

**Update Course Lab**

Update a course lab assignment (e.g. display_name). Instructor only.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `lab_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CourseLabUpdateRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `display_name` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/labs/{lab_id}/reset/{user_id}`

**Reset Student Lab**

Reset a student's lab completion within this course (admin only).

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `lab_id` | path | integer | yes |  |
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/regenerate-invite`

**Regenerate Invite**

Regenerate the invite code for a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/report`

**Class Report**

Generate PDF report for entire class.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/report/{user_id}`

**Student Report**

Generate PDF report for a single student.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `user_id` | path | integer | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/scoreboard`

**Get Scoreboard**

Get course scoreboard. Must be enrolled or instructor.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/staff`

**List Course Staff**

List mentors, teaching assistants, and co-instructors for a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/staff`

**Add Course Staff**

Assign a mentor, teaching assistant, or co-instructor to a course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CourseStaffCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `user_id` | integer | yes |  |
| `staff_role` | `co_instructor` | `mentor` | `teaching_assistant` | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/staff/candidates`

**List Course Staff Candidates**

List users who can be assigned to the course.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/courses/{course_id}/staff/{staff_id}`

**Remove Course Staff**

Remove a course staff assignment.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `staff_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/students`

**List Students**

List enrolled students.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/courses/{course_id}/students/{user_id}/consent`

**Record Minor Consent**

Record the institution's parental/guardian consent reference for a minor.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `user_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `MinorConsentRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `reference` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/students/{user_id}/labs/{lab_id}/attempts`

**Get Student Lab Attempts**

Every flag attempt one student made on one exercise, oldest first.  The scoreboard shows an attempt count. A count cannot answer the questions that actually come up: was the first try right, how far apart were the tries, and what did they type. Auditing a suspicious-looking solve without that meant reading the database by hand.  Restricted to the course's instructor and to admins. A student cannot read another student's attempts, and cannot read their own here either: the submitted strings for an exercise they may not have finished are in this payload, so enrolment is not enough.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `user_id` | path | integer | yes |  |
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/toggle-active`

**Toggle Course Active**

Toggle course active/inactive status.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/courses/{course_id}/unarchive`

**Unarchive Course**

Unarchive a course. Sets is_archived=False but keeps is_active=False.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Curriculum Admin

### `DELETE /api/admin/curriculum/levels/{level_id}`

**Delete Level**

Delete a level. Fails if labs are assigned to it.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `level_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/admin/curriculum/levels/{level_id}`

**Update Level**

Update a level.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `level_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `LevelUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `description` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/curriculum/tracks`

**List Tracks**

List all tracks with level and lab counts.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/curriculum/tracks`

**Create Track**

Create a new track.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `TrackCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `slug` | string | yes |  |
| `description` | string or null | no |  |
| `icon` | string or null | no |  |
| `color` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/admin/curriculum/tracks/reorder`

**Reorder Tracks**

Update track sort order from an ordered list of IDs.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ReorderRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `ordered_ids` | array[integer] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/admin/curriculum/tracks/{track_id}`

**Delete Track**

Hard-delete a track, its levels, and unassign any labs.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/admin/curriculum/tracks/{track_id}`

**Update Track**

Update a track.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `TrackUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `description` | string or null | no |  |
| `icon` | string or null | no |  |
| `color` | string or null | no |  |
| `is_active` | boolean or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/curriculum/tracks/{track_id}/levels`

**Create Level**

Create a new level within a track.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `LevelCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `description` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/admin/curriculum/tracks/{track_id}/levels/reorder`

**Reorder Levels**

Update level sort order and level numbers from an ordered list of IDs.  A direct renumber collides with the unique (track_id, level_number) index when two levels swap positions, so park the whole track on unique negative numbers first and only then assign the final sequence. Levels omitted from the payload keep their relative order after the listed ones.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `ReorderRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `ordered_ids` | array[integer] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Cyber DNA

### `GET /api/dna/v3/affinity`

**Cyber DNA career affinity**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `pathway_id` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dna/v3/behavior`

**Cyber DNA behavior profile**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/dna/v3/competencies`

**Cyber DNA competency scores**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/dna/v3/dna`

**Cyber DNA learner payload**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/dna/v3/evidence`

**Cyber DNA evidence ledger**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `competency_id` | query | string or null | no |  |
| `domain` | query | string or null | no |  |
| `limit` | query | integer | no |  |
| `offset` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dna/v3/interest`

**Cyber DNA interest vector**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/dna/v3/snapshots`

**List Cyber DNA snapshots**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `kind` | query | string or null | no |  |
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/dna/v3/snapshots`

**Record a Cyber DNA snapshot**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `kind` | query | string | yes |  |
| `pathway_id` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dna/v3/snapshots/{snapshot_id}`

**Cyber DNA snapshot**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `snapshot_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Dashboard

### `GET /api/dashboard/celebrations`

**Celebration Wall**

A cross-course wall of achievement wins, visible to every signed-in user.  Only active users who have not opted out of scoreboards are counted in the public stats, feed, and leaderboard. Admin accounts are left off the public wall because they are the diagnostic actors in the instructor views. The current user's own awards are still returned in ``me`` so someone in privacy mode can see their personal corner.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `limit` | query | integer | no | Recent wins to return |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/dashboard/celebrations/{achievement_id}/celebrate`

**Toggle Celebration**

Toggle one anonymous celebration on a public achievement.  The celebration is voluntary and anonymous: the wall returns only the count. The actor is stored so one person can celebrate a win once, but the actor's identity is never exposed. This endpoint does not touch analytics, progress, grading, or course-health data.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `achievement_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dashboard/instructor/feed`

**Instructor Feed**

Paginated activity event feed for the instructor dashboard.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `limit` | query | integer | no |  |
| `offset` | query | integer | no |  |
| `start` | query | string or null | no | ISO 8601 start datetime |
| `end` | query | string or null | no | ISO 8601 end datetime |
| `course_id` | query | integer or null | no | Filter to a specific course |
| `user_id` | query | integer or null | no | Filter to a specific user |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dashboard/instructor/filter-options`

**Instructor Filter Options**

Return courses and students available to the current user for filtering.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | query | integer or null | no | Get students for a specific course |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dashboard/instructor/ics-coverage`

**Ics Attack Coverage**

ICS ATT&CK coverage matrix per track, computed from lab ics_techniques tags.  For each track: labs tagged vs total, techniques covered vs taxonomy total, a per-tactic heatmap (covered/total + lab count), the covered techniques with the labs that teach them, the gaps (taxonomy techniques no lab covers), and the untagged labs. Drives the instructor coverage view.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track` | query | string or null | no | Track slug to scope to; default all tracks with tags |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dashboard/instructor/learning`

**Instructor Learning**

Range-scoped learning metrics for the selected period and scope.  The response states its own window and the number of students in scope so the UI never presents a count without a denominator.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `start` | query | string or null | no | ISO 8601 start datetime |
| `end` | query | string or null | no | ISO 8601 end datetime |
| `course_id` | query | integer or null | no | Filter to a specific course |
| `user_id` | query | integer or null | no | Filter to a specific user |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dashboard/instructor/pulse`

**Instructor Pulse**

Hourly or daily data points for The Pulse chart.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `start` | query | string or null | no | ISO 8601 start datetime |
| `end` | query | string or null | no | ISO 8601 end datetime |
| `course_id` | query | integer or null | no | Filter to a specific course |
| `user_id` | query | integer or null | no | Filter to a specific user |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dashboard/instructor/report`

**Instructor Report**

Download a report of the currently filtered dashboard view.  Includes: student details (or per-student summary), an activity graphic, and the filtered activity log.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `format` | query | string | no | Report format: 'pdf' or 'csv' |
| `start` | query | string or null | no |  |
| `end` | query | string or null | no |  |
| `course_id` | query | integer or null | no |  |
| `user_id` | query | integer or null | no |  |
| `range_label` | query | string or null | no | Human label for window e.g. 'Last 7 days' |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dashboard/instructor/stats`

**Instructor Stats**

Rich stat card data for the instructor Ops Center.  Admins see platform-wide stats.  Instructors see only students enrolled in courses they own.  *tz_offset* (minutes) adjusts "today" to the client's local midnight.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `tz_offset` | query | integer | no | Client UTC offset in minutes (e.g. -300 for CDT) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/dashboard/student`

**Student Dashboard**

Student dashboard: next objective, progress, VPN, rank.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

## Evidence

### `GET /api/evidence`

**List Evidence**

List evidence visible to the caller.  Learners see their own records. Reviewers see learners in courses they own or staff. Tenant-wide roles see their institution, and a platform administrator sees the system.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `learner_id` | query | integer or null | no |  |
| `status` | query | string or null | no |  |
| `source_type` | query | string or null | no |  |
| `competency_id` | query | string or null | no |  |
| `limit` | query | integer | no |  |
| `offset` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/evidence`

**Create Evidence**

Record evidence from a reviewed rubric and competency contract.  Replaying the same learner, source, rubric, competencies, and artifact hash returns the existing record instead of creating a duplicate.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `EvidenceCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `learner_id` | integer | yes |  |
| `source_type` | string | yes |  |
| `source_id` | string | yes |  |
| `competencies` | array[`CompetencyLinkIn`] | yes |  |
| `rubric_id` | string | yes |  |
| `rubric_version` | string | yes |  |
| `confidence` | string | no |  |
| `confidence_reason` | string or null | no |  |
| `collected_at` | string or null | no |  |
| `provenance` | string | no |  |
| `provenance_version` | string or null | no |  |
| `visibility` | string | no |  |
| `formula_version` | string | no |  |
| `artifact` | `ArtifactIn` or null | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/evidence/analytics`

**Evidence Analytics Overview**

Aggregate evidence operations for the caller's scope.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/evidence/queue`

**Review Queue**

Evidence awaiting a first review or more evidence.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/evidence/rubrics`

**List Evidence Rubrics**

Return the versioned rubric registry used by the review form.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/evidence/{evidence_id}`

**Get Evidence**

Read one record with its competencies, reviews, and artifact hash.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `evidence_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/evidence/{evidence_id}/review`

**Review Evidence**

Score, accept, reject, or request more evidence.  The decision is appended; the record's content is never edited.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `evidence_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `EvidenceReviewIn`

| Field | Type | Required | Description |
|---|---|---|---|
| `decision` | string | yes |  |
| `criterion_scores` | map[string, integer] | no |  |
| `notes` | string or null | no |  |
| `next_step` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Exercise Quizzes

### `GET /api/exercises/labs/{lab_slug}/quiz`

**Get Exercise Quiz**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/exercises/labs/{lab_slug}/quiz/attempts`

**List Exercise Quiz Attempts**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/exercises/labs/{lab_slug}/quiz/attempts`

**Start Exercise Quiz**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/exercises/labs/{lab_slug}/quiz/attempts/{attempt_id}/submit`

**Submit Exercise Quiz**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |
| `attempt_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `ExerciseQuizSubmitRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `answers` | object | no |  |
| `feedback` | `ExerciseQuizFeedbackInput` or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/exercises/labs/{lab_slug}/quiz/feedback`

**Submit Exercise Quiz Feedback**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |

**Request body** (`application/json`)

**Schema:** `ExerciseQuizFeedbackInput`

| Field | Type | Required | Description |
|---|---|---|---|
| `satisfaction` | integer or null | no |  |
| `relevance` | integer or null | no |  |
| `usefulness` | integer or null | no |  |
| `ease_of_use` | integer or null | no |  |
| `comment` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Exercise Tester

### `POST /api/admin/exercise-test`

**Run Exercise Test**

Run automated exercise tester on one or more labs.  Body:     lab_slugs: list of lab slugs, or ["all"]     user_id:   optional user ID to test as (default 249)     timeout:   optional per-lab timeout in seconds (default 300)  Returns: text/event-stream with JSON events.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** object

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/exercise-test/active`

**Get Active Test Run**

Return the currently active test run (if any). Reads file-based state so it works regardless of which worker handled the original POST.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/exercise-test/cancel`

**Cancel Exercise Test**

Cancel a running exercise test by run_id. Sets a file flag the running task polls, so cancellation works even when this request is handled by a different worker than the one executing the run.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** object

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/exercise-test/events/{run_id}`

**Get Test Events**

Return events for a run starting after index `after` (for polling). Reads file-based state so any worker can serve the poll.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `run_id` | path | string | yes |  |
| `after` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/exercise-test/labs`

**List Testable Labs**

Return list of all labs for the tester dropdown (includes inactive).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/exercise-test/report`

**Generate Exercise Test Report**

Generate a PDF report from exercise test results.  Body: {labName, category, date, status, duration, sections: [...]} Returns: PDF file download.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Request body** (`application/json`)

**Schema:** object

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/admin/exercise-test/results`

**Clear All Exercise Test Results**

Delete all saved test results.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/exercise-test/results`

**Get Exercise Test Results**

Return all saved exercise test results (latest per lab).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/admin/exercise-test/results/{lab_slug}`

**Delete Exercise Test Result**

Delete a single saved test result.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Exercise Tester (Instructor)

### `POST /api/instructor/exercise-test`

**Run Exercise Test**

Run automated exercise tester on one or more labs.  Body:     lab_slugs: list of lab slugs, or ["all"]     user_id:   optional user ID to test as (default 249)     timeout:   optional per-lab timeout in seconds (default 300)  Returns: text/event-stream with JSON events.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** object

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/exercise-test/active`

**Get Active Test Run**

Return the currently active test run (if any). Reads file-based state so it works regardless of which worker handled the original POST.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/instructor/exercise-test/cancel`

**Cancel Exercise Test**

Cancel a running exercise test by run_id. Sets a file flag the running task polls, so cancellation works even when this request is handled by a different worker than the one executing the run.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** object

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/exercise-test/events/{run_id}`

**Get Test Events**

Return events for a run starting after index `after` (for polling). Reads file-based state so any worker can serve the poll.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `run_id` | path | string | yes |  |
| `after` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/exercise-test/labs`

**List Testable Labs**

Return list of all labs for the tester dropdown (includes inactive).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/instructor/exercise-test/report`

**Generate Exercise Test Report**

Generate a PDF report from exercise test results.  Body: {labName, category, date, status, duration, sections: [...]} Returns: PDF file download.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Request body** (`application/json`)

**Schema:** object

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/instructor/exercise-test/results`

**Clear All Exercise Test Results**

Delete all saved test results.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/instructor/exercise-test/results`

**Get Exercise Test Results**

Return all saved exercise test results (latest per lab).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/instructor/exercise-test/results/{lab_slug}`

**Delete Exercise Test Result**

Delete a single saved test result.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Exercises

### `GET /api/exercises/labs/{lab_id}`

**Get Lab Details**

Get detailed lab info for active lab view

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |
| `course_id` | query | integer | no |  |
| `launch` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/exercises/labs/{lab_id}/hint`

**Get Hint**

Get next hint for a lab (with time-based unlocking support)

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/exercises/labs/{lab_id}/submit-flag`

**Submit Flag**

Submit flag for validation. Pass course_id to allow resubmission for course credit.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |
| `course_id` | query | integer or null | no |  |

**Request body** (`application/json`)

**Schema:** `FlagSubmitRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `flag` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/exercises/progress`

**Get Progress**

Get user's overall progress across all tracks

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/exercises/tracks`

**List Tracks**

Get all tracks with user progress

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/exercises/tracks/{track_slug}`

**Get Track**

Get track details with levels and labs

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_slug` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/exercises/tracks/{track_slug}/levels/{level_id}/certificate`

**Get a printable level-completion certificate**

Return the data needed to render a printable certificate.  A certificate is only issued when every lab the student can see in the level has been completed. The certificate ID is deterministic for a (user, track, level) triple so the same certificate can be reissued without changing its identifier.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_slug` | path | string | yes |  |
| `level_id` | path | integer | yes |  |
| `include_achievements` | query | boolean | no | Include achievements earned in courses that contain this level's labs |

**Responses**

- `200`: Certificate metadata for a completed level
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/exercises/tracks/{track_slug}/levels/{level_id}/certificate.pdf`

**Download the certificate as a PDF**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_slug` | path | string | yes |  |
| `level_id` | path | integer | yes |  |
| `include_achievements` | query | boolean | no |  |
| `design` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/exercises/verify/certificate/{certificate_id}`

**Verify Certificate**

Public verification endpoint for a certificate ID.  Certificates are derived from completion records, so this resolves the deterministic ID back to the matching user/level and re-checks that the level is still complete. Only public certificate fields are returned; no username, email, or account details are exposed.

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `certificate_id` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/exercises/workbooks`

**List Workbooks**

Workbook landing data: every shipped track that has a workbook, with the URL of its workbook root. Derived from lab.workbook fields, so it reflects exactly what this install ships (edition-correct with no extra config).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

## General

### `GET /`

**Root**

**Authentication:** Public

**Responses**

- `200`: Successful Response

### `GET /api/version`

**Api Version**

Public build identity for the web interface and support reports.  Kept independent of the database so the frontend can show the running version even when the health probe is degraded.

**Authentication:** Public

**Responses**

- `200`: Successful Response

### `GET /health`

**Health**

Health probe with a real database check.  Sync def on purpose: FastAPI runs it in the threadpool, so the blocking SELECT never stalls the event loop. Returns 200/healthy when the DB answers, 503/degraded when it does not, so load balancers and container healthchecks see actual readiness instead of a static string.

**Authentication:** Public

**Responses**

- `200`: Successful Response

## Governance

### `GET /api/governance/audit/dashboard`

**Audit Dashboard**

Aggregate audit evidence for an auditor.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/governance/privacy/dashboard`

**Privacy Dashboard**

Aggregate privacy evidence for the privacy office.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

## Human review

### `GET /api/courses/{course_id}/reviews`

**List Course Reviews**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `status` | query | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/reviews`

**Request Review**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ReviewRequestCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `lab_id` | integer | yes |  |
| `course_id` | integer or null | no |  |
| `source` | string | no |  |
| `reason` | string | yes |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/reviews/mine`

**List My Reviews**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `PUT /api/reviews/{review_id}/decision`

**Decide Review**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `review_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `ReviewDecision`

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | string | yes |  |
| `note` | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Identity Providers

### `GET /api/identity/providers`

**List Identity Providers**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/identity/providers`

**Create Identity Provider**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `IdentityProviderCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `kind` | string | yes |  |
| `enabled` | boolean | no |  |
| `is_default` | boolean | no |  |
| `config` | object | no |  |
| `secrets` | object or null | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/identity/providers/export`

**Export Identity Providers**

Export portable provider settings. Secret values are never included.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/identity/providers/import`

**Import Identity Providers**

Validate or import an exported provider bundle.  The default is a dry run. Secret values may be supplied on import; they are encrypted at rest and never echoed back. A provider whose required secrets are absent is imported disabled rather than enabled in a broken state.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `IdentityProviderImport`

| Field | Type | Required | Description |
|---|---|---|---|
| `providers` | array[`IdentityProviderImportItem`] | yes |  |
| `dry_run` | boolean | no |  |
| `update_existing` | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/identity/providers/{provider_id}`

**Delete Identity Provider**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `provider_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PATCH /api/identity/providers/{provider_id}`

**Update Identity Provider**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `provider_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `IdentityProviderUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `enabled` | boolean or null | no |  |
| `is_default` | boolean or null | no |  |
| `config` | object or null | no |  |
| `secrets` | object or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/identity/providers/{provider_id}/default`

**Make Default Identity Provider**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `provider_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/identity/providers/{provider_id}/test`

**Test Identity Provider**

Validate provider settings and reachability for its adapter.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `provider_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Instructor

### `GET /api/instructor/courses`

**List My Courses**

List courses owned by the current instructor (admins see all).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/instructor/courses/{course_id}`

**Get My Course**

Get detail for a single course (must own it, or be admin).

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/courses/{course_id}/enrollable-users`

**List Enrollable Users**

List students not yet enrolled in this course (for enrollment dropdown). Only course owner or admin can call this.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/labs`

**List Available Labs**

List labs available for course assignment.  Returns public and course-visible labs, plus any labs created by this instructor. Admins see all labs. When ``start`` or ``end`` is supplied, each lab also carries activity counts for the instructor's visible students in that window.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `start` | query | string or null | no | ISO 8601 start datetime for activity |
| `end` | query | string or null | no | ISO 8601 end datetime for activity |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/labs/assignments`

**Lab Course Assignments**

Return a mapping of lab_id -> list of courses it's assigned to, scoped to the current instructor's courses (admins see all).

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/instructor/labs/upload`

**Upload Lab Zip**

Upload a ZIP file containing a lab exercise and register it.

**Authentication:** OAuth2PasswordBearer

**Request body** (`multipart/form-data`)

**Schema:** `Body_upload_lab_zip_api_instructor_labs_upload_post`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | string | yes |  |
| `track` | string | yes |  |
| `level_id` | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/instructor/labs/{lab_id}`

**Delete Own Lab**

Delete an exercise (DB record + files on disk). Instructors can only delete their own.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/instructor/labs/{lab_id}`

**Update Own Lab**

Update metadata on an exercise. Instructors can only edit their own.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `app__routers__instructor__UpdateLabRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `description` | string or null | no |  |
| `scenario` | string or null | no |  |
| `difficulty` | string or null | no |  |
| `category` | string or null | no |  |
| `duration_minutes` | integer or null | no |  |
| `objectives` | string or null | no |  |
| `hints` | string or null | no |  |
| `flag` | string or null | no |  |
| `level_id` | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/labs/{lab_id}/export`

**Export Own Lab**

Download a reusable exercise ZIP with the flag replaced by a placeholder.  Export is read-only and available to instructors for any catalog exercise they can already see. The original flag is never included on this path.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/labs/{lab_id}/flag`

**Reveal Lab Flag**

Reveal a lab's answer flag to the instructor who teaches it.  The database only ever stores the SHA256 (labs.flag_hash), so the plaintext has to come from the lab.yaml on disk. That is also why this endpoint reports drift instead of guessing: if the file no longer hashes to the column, the flag on disk is NOT what grading accepts, and showing it without saying so would send an instructor to argue a student's correct submission was wrong.  Admins see any lab. An instructor sees a lab only when it is assigned to a course they own, which keeps one instructor account from being an answer key for all 455 labs.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/instructor/labs/{lab_id}/visibility`

**Update Lab Visibility**

Change exercise visibility. Instructors: draft/course/pending_public only.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `VisibilityUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `visibility` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/overview`

**Instructor Overview**

Aggregate cross-course cards and a trend series for the instructor view.  Definitions: assigned pairs = course lab assignments × enrolled learners; completion = completed learner–exercise pairs / assigned pairs. Slices with fewer than five learners have their rate suppressed. No learner is named.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `days` | query | integer | no |  |
| `course_id` | query | integer or null | no |  |
| `student_id` | query | integer or null | no |  |
| `start` | query | string or null | no |  |
| `end` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/instructor/stats`

**Instructor Stats**

Dashboard stats for the current instructor.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/instructor/tracks-and-levels`

**List Tracks And Levels**

Flat list of all tracks and their levels for the lab re-categorize picker.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

## LTI 1.3

### `GET /api/lti/admin/links`

**List Links**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `platform_id` | query | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/lti/admin/links/{link_id}/lineitem`

**Create Link Lineitem**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `link_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `LtiLineItemRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `label` | string | yes |  |
| `max_score` | number | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/lti/admin/links/{link_id}/results`

**Get Link Results**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `link_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/lti/admin/links/{link_id}/roster`

**Get Link Roster**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `link_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/lti/admin/links/{link_id}/roster/saved`

**Get Saved Roster**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `link_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/lti/admin/links/{link_id}/score`

**Post Link Score**

Post a reviewed score to the LMS and record the attempt.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `link_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `LtiScoreRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `user_id` | integer | yes |  |
| `score` | number | yes |  |
| `max_score` | number | yes |  |
| `reason` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/lti/admin/links/{link_id}/scores`

**List Link Scores**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `link_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/lti/admin/links/{link_id}/sync-roster`

**Sync Link Roster**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `link_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/lti/admin/platforms`

**List Platforms**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/lti/admin/platforms`

**Create Platform**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `LtiPlatformCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `issuer` | string | yes |  |
| `client_id` | string | yes |  |
| `deployment_id` | string | yes |  |
| `auth_login_url` | string | yes |  |
| `token_url` | string | yes |  |
| `jwks_url` | string | yes |  |
| `private_key` | string or null | no |  |
| `enabled` | boolean | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/lti/admin/platforms/{platform_id}`

**Delete Platform**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `platform_id` | path | integer | yes |  |

**Responses**

- `204`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PATCH /api/lti/admin/platforms/{platform_id}`

**Update Platform**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `platform_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `LtiPlatformUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `issuer` | string or null | no |  |
| `client_id` | string or null | no |  |
| `deployment_id` | string or null | no |  |
| `auth_login_url` | string or null | no |  |
| `token_url` | string or null | no |  |
| `jwks_url` | string or null | no |  |
| `private_key` | string or null | no |  |
| `enabled` | boolean or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/lti/admin/platforms/{platform_id}/test`

**Test Platform**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `platform_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/lti/deep-link/{session_token}`

**Deep Link Info**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_token` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/lti/deep-link/{session_token}/response`

**Deep Link Response**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_token` | path | string | yes |  |

**Request body** (`application/json`)

**Schema:** `LtiDeepLinkResponseRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `lab_slugs` | array[string] | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/lti/jwks`

**Tool Jwks**

Public tool keyset used by an LMS to verify our signed messages.

**Authentication:** Public

**Responses**

- `200`: Successful Response

### `POST /api/lti/launch`

**Lti Launch**

Validate the LMS launch and hand off to the normal SPA exchange.

**Authentication:** Public

**Request body** (`application/x-www-form-urlencoded`)

**Schema:** `Body_lti_launch_api_lti_launch_post`

| Field | Type | Required | Description |
|---|---|---|---|
| `id_token` | string | no |  |
| `state` | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/lti/login`

**Lti Login**

OIDC third-party initiated login from the LMS (GET or form POST).

**Authentication:** Public

**Responses**

- `200`: Successful Response

### `POST /api/lti/login`

**Lti Login**

OIDC third-party initiated login from the LMS (GET or form POST).

**Authentication:** Public

**Responses**

- `200`: Successful Response

## Labs

### `GET /api/labs/`

**Get Labs**

Get available labs for the current user.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/labs/active`

**Get Active Lab**

Get the user's active lab session

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/labs/extend`

**Extend Lab Session**

Extend the user's active lab session by 1 hour

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/labs/pause`

**Pause Lab Session**

Pause the learner's clock; the session stays running and is not reaped.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `PauseRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/labs/prebuild-status`

**Prebuild Status**

Background lab-prebuild progress for the 'still preparing' banner.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/labs/resume`

**Resume Lab Session**

Resume a paused session and credit the paused time to its expiry.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/labs/spawn-status/{session_id}`

**Get Spawn Status**

Poll the spawn progress of a lab session.  The status field moves starting -> running on success or starting -> error on failure. Status lives on the lab_sessions row, so the answer is correct no matter which worker ran the background bring-up.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/labs/spawn/{lab_slug}`

**Spawn Lab**

Spawn a lab environment for the user

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |
| `launch` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/labs/stop`

**Stop Lab**

Stop the user's active lab session

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/labs/vpn-config`

**Get Vpn Config**

Get or generate WireGuard VPN configuration - routes the student's lab /24

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response — string

### `GET /api/labs/vpn-config/qr`

**Get Vpn Config Qr**

Return the user's WireGuard config as a QR code image.  WireGuard mobile apps can import a tunnel by scanning the full config. The image contains the user's private key, so it is generated on demand and marked no-store. The web UI reveals it only after an explicit click.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/labs/vpn-status`

**Get Vpn Status**

Get VPN registration status for current user - checks Peer Manager directly

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

## Modules

### `GET /api/modules/`

**Get Modules Status**

Return enabled/disabled status of the optional modules this build ships.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

## NICE Framework

### `GET /api/nice/components`

**Nice Components**

Search NICE components for the authoring dropdown.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `component_type` | query | `work_role` | `task` | `knowledge` | `skill` | no |  |
| `q` | query | string | no |  |
| `work_role` | query | string or null | no |  |
| `limit` | query | integer | no |  |
| `offset` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/nice/coverage`

**Nice Coverage**

Return lab mapping coverage and the provisional review queue.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/nice/labs/seed`

**Seed Nice Lab Mappings**

Fill labs that have no NICE mapping from the provisional seed file.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/nice/labs/{lab_id}`

**Get Lab Nice Mappings**

Return the selected NICE components for one lab.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/nice/labs/{lab_id}`

**Set Lab Nice Mappings**

Replace the NICE components selected for one lab.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `NiceSelection`

| Field | Type | Required | Description |
|---|---|---|---|
| `work_role` | array[string] | no |  |
| `task` | array[string] | no |  |
| `knowledge` | array[string] | no |  |
| `skill` | array[string] | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/nice/labs/{lab_id}/review`

**Review Lab Nice Mappings**

Mark an existing provisional mapping as reviewed without editing it.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/nice/refresh`

**Refresh Nice Framework**

Refresh NICE components from NIST or the bundled snapshot.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `NiceRefreshRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `source` | `official` | `snapshot` | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/nice/status`

**Nice Status**

Return the installed NICE Framework version and component counts.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

## Open Badges

### `GET /api/admin/badges`

**List Badges**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/badges/rotate-key`

**Rotate Badge Key**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/badges/settings`

**Badge Settings**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `PUT /api/admin/badges/settings`

**Update Badge Settings**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `BadgeSettingsUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `issuer_name` | string | yes |  |
| `issuer_url` | string | no |  |
| `confirm_change` | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/badges/{badge_id}/revoke`

**Revoke Badge**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `badge_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `RevokeRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/badges/achievements/{certificate_id}`

**Achievement Definition**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `certificate_id` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/badges/achievements/{certificate_id}/image`

**Achievement Image**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `certificate_id` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/badges/credentials/{jti}`

**Hosted Credential**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `jti` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/badges/credentials/{jti}/jwt`

**Hosted Credential Jwt**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `jti` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/badges/credentials/{jti}/status`

**Credential Status**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `jti` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/badges/events/issue`

**Issue Event Badge**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `EventIssueRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `competition_id` | integer | yes |  |
| `award` | string | yes |  |
| `include_name` | boolean | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/badges/issue`

**Issue Badge**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `IssueRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `track_slug` | string | yes |  |
| `level_id` | integer | yes |  |
| `include_name` | boolean | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/badges/issuer`

**Issuer Profile**

**Authentication:** Public

**Responses**

- `200`: Successful Response

### `GET /api/badges/issuer/jwks`

**Issuer Jwks**

**Authentication:** Public

**Responses**

- `200`: Successful Response

### `GET /api/badges/mine`

**My Badges**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/badges/{badge_id}/consent`

**Badge Consent**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `badge_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `ConsentRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `include_name` | boolean | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Portfolio shares

### `GET /api/profile/shares`

**List portfolio share links**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/profile/shares`

**Create a portfolio share link**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ShareCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `label` | string or null | no |  |
| `audience` | string or null | no |  |
| `days` | integer or null | no |  |
| `single_use` | boolean | no |  |
| `max_uses` | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/profile/shares/{share_id}`

**Revoke a portfolio share link**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `share_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/public/portfolio/{token}`

**Read a shared portfolio**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `token` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Profile

### `GET /api/profile/career-assessment`

**Short career-direction questions**

Return eight reflection questions. No answers are stored.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/profile/career-assessment`

**Score a short career-direction check**

Score optional answers for this response only.  The result is a reflection aid, not a personality test or a career decision. Nothing is persisted, logged, or shared with the cohort.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `CareerAssessmentRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `answers` | map[string, integer] | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/profile/career-dossier`

**Career-profile dossier (JSON)**

Return the learner's career-discovery dossier as JSON.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/profile/career-dossier.html`

**Career-profile dossier (HTML)**

View or print the learner's career-discovery dossier as HTML.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/profile/career-dossier.md`

**Career-profile dossier (Markdown)**

Download the learner's career-discovery dossier as Markdown.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/profile/competencies`

**Learner competency assessment profile**

Return the learner's taxonomy evidence and assessment scores.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/profile/gps`

**Optional cybersecurity GPS direction finder**

Answer 'where could I go?' from evidence, growth, and optional answers.  Answers are accepted in the request body for this response only. They are not persisted, logged, or shared with the cohort.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `GpsRequest` or null

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/profile/portfolio`

**Professional portfolio (JSON)**

Return the learner's professional portfolio as JSON.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/profile/portfolio.html`

**Professional portfolio (printable HTML)**

View or print the learner's professional portfolio as HTML.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/profile/portfolio.md`

**Professional portfolio (Markdown)**

Download the learner's professional portfolio as Markdown.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/profile/role-readiness`

**Role readiness answer**

Answer 'what do I need for this role?' from the learner's evidence.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `role` | query | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/profile/roles`

**Career pathway catalogue**

Return the pathway catalogue used by the role readiness selector.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/profile/skill-dna`

**Learner Skill DNA character sheet**

Return the learner's six traits, class, affinities, and titles.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/profile/snapshots`

**Stored report snapshots**

List the learner's stored reports, newest first.  A stored report is immutable: re-downloading it returns the payload and factor weights captured when it was generated.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `kind` | query | string or null | no |  |
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/profile/snapshots/{snapshot_id}`

**Stored report snapshot**

Return a stored report payload and the weights used to build it.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `snapshot_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/profile/snapshots/{snapshot_id}/html`

**Stored report (HTML)**

Re-render a stored report as printable HTML without recomputing it.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `snapshot_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/profile/snapshots/{snapshot_id}/markdown`

**Stored report (Markdown)**

Re-render a stored report as Markdown without recomputing it.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `snapshot_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/profile/summary`

**Profile snapshot with certificates and completions**

Return everything the profile page renders in one round trip.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `PUT /api/profile/title`

**Equip an unlocked achievement title**

Equip an unlocked title, or clear it to return to the class title.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `TitleUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/profile/transcript.pdf`

**Download a printable completion transcript**

Render the profile summary as a PDF transcript.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

## Public config

### `GET /api/config/public`

**Public Config**

Return runtime values needed by the SPA before authentication.

**Authentication:** Public

**Responses**

- `200`: Successful Response

### `GET /api/public/community-events`

**Community Events**

Return the public SWOCTS Hub calendar, cached by the backend.

**Authentication:** Public

**Responses**

- `200`: Successful Response

## Public usage

### `GET /api/public/qr/{source}`

**Qr Landing**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `source` | path | string | yes |  |
| `campaign` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Question Banks

### `GET /api/admin/question-banks`

**List certification question banks**

Return bank summaries and validation counts. Admin only.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/question-banks/validate`

**Validate the question banks**

Run the static reliability checks and return every issue.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/question-banks/{pathway_id}`

**Read one certification question bank**

Return the full bank, including answers, explanations, and references.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `pathway_id` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Quizzes

### `GET /api/exercises/tracks/{track_slug}/levels/{level_id}/quiz`

**Get Level Quiz**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_slug` | path | string | yes |  |
| `level_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/exercises/tracks/{track_slug}/levels/{level_id}/quiz/attempts`

**List Quiz Attempts**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_slug` | path | string | yes |  |
| `level_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/exercises/tracks/{track_slug}/levels/{level_id}/quiz/submit`

**Submit Level Quiz**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `track_slug` | path | string | yes |  |
| `level_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** object

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## RangeBox

### `GET /api/rangebox/capacity`

**Rangebox Capacity**

Return current and maximum RangeBox capacity.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/rangebox/standalone/destroy`

**Standalone Rangebox Destroy**

Stop and remove the standalone RangeBox.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/rangebox/standalone/launch`

**Standalone Rangebox Launch**

Launch a standalone RangeBox (not tied to any lab session).

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `image` | query | string | no | Image shorthand: 'kali', 'ubuntu', or 'remnux' |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/rangebox/standalone/status`

**Standalone Rangebox Status**

Get standalone RangeBox container status.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/rangebox/transport`

**Rangebox Transport**

Report which browser-desktop client the running RangeBox expects.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | query | integer or null | no |  |
| `standalone` | query | boolean | no |  |
| `admin_target_user_id` | query | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/rangebox/ws-ticket`

**Get Ws Ticket**

Exchange a JWT for a short-lived, single-use WebSocket ticket. The ticket replaces the JWT in WebSocket URLs to prevent token leakage.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/rangebox/{session_id}/lab`

**Rangebox Lab**

Return the lab name, target IPs, and flag state for this RangeBox.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/rangebox/{session_id}/status`

**Rangebox Status**

Get RangeBox container status for an active lab session.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `session_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Reports

### `GET /api/courses/{course_id}/reports`

**List Reports**

Return the report library for a course the caller can manage.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/reports/coaching-queue.csv`

**Coaching Queue Csv**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/reports/coaching-queue.pdf`

**Coaching Queue Pdf**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/reports/course-health.pdf`

**Course Health Report**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/reports/exercise-diagnostics.csv`

**Exercise Diagnostics Csv**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/courses/{course_id}/reports/exercise-diagnostics.pdf`

**Exercise Diagnostics Report**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `course_id` | path | integer | yes |  |
| `reason` | query | string | yes | Why this export is needed (recorded in the audit log) |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/reports/verify`

**Verify Report File**

Verify that a report file matches the platform manifest.  This endpoint is intentionally public but requires both the unguessable report id and the file. It does not return learner data beyond the report metadata.

**Authentication:** Public

**Request body** (`multipart/form-data`)

**Schema:** `Body_verify_report_file_api_reports_verify_post`

| Field | Type | Required | Description |
|---|---|---|---|
| `report_id` | string | yes |  |
| `file` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Security administration

### `GET /api/admin/security/access-rules`

**List sign-in and registration allow/deny rules**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `scope` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/security/access-rules`

**Add a sign-in or registration allow/deny rule**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `AccessRuleCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `scope` | string | yes |  |
| `kind` | string | yes |  |
| `value` | string | yes |  |
| `action` | string | yes |  |
| `note` | string or null | no |  |
| `expires_at` | string or null | no |  |

**Responses**

- `201`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/security/access-rules/test`

**Explain how the current rules evaluate one request**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `AccessRuleTest`

| Field | Type | Required | Description |
|---|---|---|---|
| `scope` | string | yes |  |
| `ip_address` | string or null | no |  |
| `email` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/admin/security/access-rules/{rule_id}`

**Remove a sign-in or registration allow/deny rule**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `rule_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/security/break-glass`

**Break-glass grants and review state**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `status` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/security/break-glass`

**Request time-bound emergency access**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `BreakGlassRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `permission` | string | yes |  |
| `reason` | string | yes |  |
| `minutes` | integer | no |  |
| `reference` | string or null | no |  |
| `user_id` | integer or null | no |  |
| `course_id` | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/security/break-glass/{grant_id}/approve`

**Approve a pending grant**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `grant_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/security/break-glass/{grant_id}/review`

**Close the post-use review**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `grant_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `BreakGlassReview`

| Field | Type | Required | Description |
|---|---|---|---|
| `note` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/security/break-glass/{grant_id}/revoke`

**Revoke a grant**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `grant_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `BreakGlassRevoke` or null

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/security/events`

**Query security, audit, and privacy events**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `category` | query | string or null | no |  |
| `event_type` | query | string or null | no |  |
| `severity` | query | string or null | no |  |
| `outcome` | query | string or null | no |  |
| `actor_id` | query | integer or null | no |  |
| `institution_id` | query | string or null | no |  |
| `search` | query | string or null | no |  |
| `since` | query | string or null | no |  |
| `until` | query | string or null | no |  |
| `limit` | query | integer | no |  |
| `offset` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/security/events/summary`

**Security event counts and top event types**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `days` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/security/events/{event_id}`

**One security event**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `event_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/security/rbac/check`

**Explain one authorization decision**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `AuthorizationCheck`

| Field | Type | Required | Description |
|---|---|---|---|
| `user_id` | integer | yes |  |
| `permission` | string | yes |  |
| `resource_user_id` | integer or null | no |  |
| `course_id` | integer or null | no |  |
| `shared` | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/security/rbac/matrix`

**Role and policy access matrix**

Return the effective role grants and the PBAC attributes together.  This is a read-only review surface: it never returns learner data, secrets, or request-scoped decisions. Role grants come from the RBAC tables so an administrator's reviewed edits are what the matrix shows.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/security/rbac/permissions`

**Reviewed permission catalog**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/admin/security/rbac/roles`

**Roles, grants, and effective permission counts**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `PUT /api/admin/security/rbac/roles/{role_key}/permissions`

**Replace one role's permission grants**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `role_key` | path | string | yes |  |

**Request body** (`application/json`)

**Schema:** `RolePermissionsUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `permissions` | array[string] | no |  |
| `reason` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/security/rbac/users/{user_id}`

**Effective roles and permissions**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/admin/security/rbac/users/{user_id}/roles`

**Grant an expiring extra role**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `UserRoleGrant`

| Field | Type | Required | Description |
|---|---|---|---|
| `role_key` | string | yes |  |
| `reason` | string or null | no |  |
| `expires_at` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/admin/security/rbac/users/{user_id}/roles/{role_key}`

**Revoke an extra role**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `user_id` | path | integer | yes |  |
| `role_key` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/security/service-identities`

**List non-human service credentials**

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/security/service-identities`

**Create a scoped service credential**

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ServiceIdentityCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `scopes` | array[string] | no |  |
| `days` | integer | no |  |
| `institution_id` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/admin/security/service-identities/{credential_id}`

**Revoke a service credential**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `credential_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Settings

### `GET /api/settings/`

**Get All Settings**

Return all platform settings grouped by category. Secret values are masked.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `PUT /api/settings/`

**Update Settings**

Bulk update platform settings.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `SettingsBulkUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `settings` | object | yes |  |
| `ticket_number` | string or null | no |  |
| `reason` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/settings/achievement-catalogue`

**Grouped achievement catalogue for the studio**

Return every achievement in one grouped, filterable payload.  Built-in achievements are code paths and are read-only. Custom achievements can be edited in the same view. Points are derived from tier and difficulty so a harder badge is worth more.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Built-in and custom achievements with group, tier, difficulty, and points

### `GET /api/settings/change-requests`

**List Change Requests**

Recent settings change sets with encrypted ticket/reason fields.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `limit` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/settings/change-requests/{change_id}/revert`

**Revert Change Request**

Apply the inverse of an applied change set after checking for drift.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `change_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `SettingsChangeRevert`

| Field | Type | Required | Description |
|---|---|---|---|
| `reason` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/settings/custom-achievements`

**List custom achievements**

Return every admin-defined achievement, including inactive ones.  Built-in achievements (first blood, no hints, and so on) are code paths and are not listed here. ``trigger`` is one of the keys in ``CUSTOM_ACHIEVEMENT_TRIGGERS``; ``threshold`` is the count required for the count-based triggers and is ignored by ``course_completed``.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Admin-defined achievement definitions

### `POST /api/settings/custom-achievements`

**Create a custom achievement**

Create an achievement that is awarded automatically on flag submission.  The award is evaluated for every course the student is enrolled in, after the built-in achievement checks. Existing completions are not re-scored retroactively; the definition applies from the next correct flag onward.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `CustomAchievementCreate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes |  |
| `description` | string or null | no |  |
| `icon` | string | no |  |
| `trigger` | string | no |  |
| `threshold` | integer | no |  |
| `group_key` | string | no |  |
| `tier` | string | no |  |
| `difficulty` | string | no |  |
| `is_active` | boolean | no |  |

**Responses**

- `201`: The newly created achievement definition
- `422`: Validation Error — `HTTPValidationError`

### `DELETE /api/settings/custom-achievements/{achievement_id}`

**Delete a custom achievement**

Delete a custom achievement definition.  Awards that students already earned are kept; their label falls back to the stored achievement type once the definition is gone.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `achievement_id` | path | integer | yes |  |

**Responses**

- `200`: Deletion confirmation
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/settings/custom-achievements/{achievement_id}`

**Update a custom achievement**

Update a custom achievement. Omitted fields are left unchanged.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `achievement_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `CustomAchievementUpdate`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string or null | no |  |
| `description` | string or null | no |  |
| `icon` | string or null | no |  |
| `trigger` | string or null | no |  |
| `threshold` | integer or null | no |  |
| `group_key` | string or null | no |  |
| `tier` | string or null | no |  |
| `difficulty` | string or null | no |  |
| `is_active` | boolean or null | no |  |

**Responses**

- `200`: The updated achievement definition
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/settings/mail/test`

**Send Mail Test**

Send a test message using the saved SMTP settings.  The recipient defaults to the signed-in administrator. A failed relay is a bad gateway, and an unconfigured relay is a client error, so the operator can tell the difference without reading container logs.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `MailTestRequest` or null

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/settings/production/cutover`

**Production Cutover**

Complete the one-way production transition.  Requires a ticket, the current password, the exact confirmation phrase, and both acknowledgements. The action is irreversible from the application and is recorded with an evidence hash.

**Authentication:** OAuth2PasswordBearer

**Request body** (`application/json`)

**Schema:** `ProductionCutoverRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `ticket_number` | string | yes |  |
| `password` | string | yes |  |
| `confirmation` | string | yes |  |
| `acknowledge_data_loss` | boolean | yes |  |
| `acknowledge_one_way` | boolean | yes |  |
| `reason` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/settings/production/preview`

**Production Preview**

Preview the one-way cutover and the sample data that would be removed.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/settings/{category}`

**Get Settings By Category**

Return settings for a specific category.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `category` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Setup

### `POST /api/setup/complete`

**Complete Setup**

First-run setup. Creates admin user and seeds default settings. No auth required — guarded by 'no users exist' check.  Uses a PostgreSQL advisory lock to prevent race conditions where two concurrent requests could both pass the "no users exist" check and create duplicate admin accounts.

**Authentication:** Public

**Request body** (`application/json`)

**Schema:** `SetupRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `admin_username` | string | yes |  |
| `admin_email` | string | yes |  |
| `admin_password` | string | yes |  |
| `first_name` | string or null | no |  |
| `last_name` | string or null | no |  |
| `organization` | string or null | no |  |
| `require_approval` | boolean or null | no |  |
| `setup_token` | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/setup/config`

**Public Config**

Return non-sensitive platform config for the frontend. No auth required — only exposes display-safe values.

**Authentication:** Public

**Responses**

- `200`: Successful Response

### `GET /api/setup/status`

**Setup Status**

Check if first-run setup has been completed. No auth required.

**Authentication:** Public

**Responses**

- `200`: Successful Response

## Single Sign-On

### `POST /api/auth/sso/exchange`

**Exchange Ticket**

Exchange the one-time callback ticket for the platform JWT.  The ticket is single-use, short-lived, and only issued after a completed authentication flow, so it stays exchangeable when the SSO switch is off. Turning SSO off must stop new provider logins, not strand a ticket that was already issued. LTI launches also use this exchange, and they must not depend on the institution SSO setting.

**Authentication:** Public

**Request body** (`application/json`)

**Schema:** `SsoExchangeRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `ticket` | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `POST /api/auth/sso/ldap/{provider_id}/login`

**Ldap Login**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `provider_id` | path | integer | yes |  |

**Request body** (`application/json`)

**Schema:** `LdapLoginRequest`

| Field | Type | Required | Description |
|---|---|---|---|
| `username` | string | yes |  |
| `password` | string | yes |  |
| `return_to` | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/auth/sso/oidc/{provider_id}/callback`

**Oidc Callback**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `provider_id` | path | integer | yes |  |
| `code` | query | string or null | no |  |
| `state` | query | string or null | no |  |
| `error` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/auth/sso/oidc/{provider_id}/login`

**Oidc Login**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `provider_id` | path | integer | yes |  |
| `return_to` | query | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/auth/sso/providers`

**List Sso Providers**

List enabled providers for the login screen.  The global switch is evaluated here as well as in every flow endpoint, so turning SSO off removes the institution sign-in panel immediately rather than only rejecting the click that follows.

**Authentication:** Public

**Responses**

- `200`: Successful Response

### `POST /api/auth/sso/saml/{provider_id}/acs`

**Saml Acs**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `provider_id` | path | integer | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/auth/sso/saml/{provider_id}/login`

**Saml Login**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `provider_id` | path | integer | yes |  |
| `return_to` | query | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Usage

### `GET /api/usage/admin`

**Admin Usage**

Exact usage detail for administrators.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `days` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/usage/admin.csv`

**Admin Usage Csv**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `days` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/usage/admin/qr`

**Admin Qr Png**

Return a printable QR code for a tracked registration link.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `source` | query | string | yes |  |
| `campaign` | query | string or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/usage/public`

**Public Usage**

Aggregate usage for the shareable tracker page.

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `days` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/usage/public.csv`

**Public Usage Csv**

**Authentication:** Public

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `days` | query | integer | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Workbook

### `POST /api/admin/workbook/build`

**Trigger Build**

Trigger a manual mkdocs build of the track wikis.  Returns the structured per-track result (success may be partial). In a bake-in deployment the wiki source is not mounted in the backend container, so builds run host-side via scripts/deploy-wiki.sh; this endpoint then reports success=false with an explanatory output rather than erroring.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/workbook/build-all-course-wikis`

**Build All Course Wikis**

Build wikis for all courses that have a wiki_slug and assigned labs.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `DELETE /api/admin/workbook/chapter/{chapter_dir}`

**Delete Chapter**

Delete a workbook chapter directory and rebuild the wiki.

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `chapter_dir` | path | string | yes |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/admin/workbook/chapters`

**List Chapters**

List all workbook chapters and their files.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `POST /api/admin/workbook/upload`

**Upload Chapter**

Upload a ZIP of markdown files for a workbook chapter.  - **file**: ZIP archive containing .md files - **chapter_dir**: Target directory name (e.g. CH_COURSE01_Weekly_Challenges) - **section_name**: Top-level nav section name (default: Course Weekly Challenges) - **auto_build**: Automatically rebuild the wiki after upload (default: true)

**Authentication:** OAuth2PasswordBearer

**Request body** (`multipart/form-data`)

**Schema:** `Body_upload_chapter_api_admin_workbook_upload_post`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | string | yes |  |
| `chapter_dir` | string | yes |  |
| `section_name` | string | no |  |
| `auto_build` | boolean | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Workbook answers

### `GET /api/workbook-answers`

**List My Answers**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_id` | query | integer or null | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `GET /api/workbook-answers/options`

**Answer Options**

Visible exercises that have a workbook page, for the answer selector.

**Authentication:** OAuth2PasswordBearer

**Responses**

- `200`: Successful Response

### `GET /api/workbook-answers/{lab_slug}`

**Get My Answer**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |
| `prompt_key` | query | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

### `PUT /api/workbook-answers/{lab_slug}`

**Save My Answer**

**Authentication:** OAuth2PasswordBearer

**Parameters**

| Parameter | In | Type | Required | Description |
|---|---|---|---|---|
| `lab_slug` | path | string | yes |  |

**Request body** (`application/json`)

**Schema:** `WorkbookAnswerIn`

| Field | Type | Required | Description |
|---|---|---|---|
| `answer` | string | yes |  |
| `prompt_key` | string | no |  |

**Responses**

- `200`: Successful Response
- `422`: Validation Error — `HTTPValidationError`

## Data handling

- Do not send real learner, patient, customer, or institutional data to
  a lab endpoint unless the deployment's data policy explicitly allows it.
- Use synthetic identifiers in examples and test scripts.
- Exports are labelled and audited. Do not remove a label or bypass an
  export reason.
- Report a vulnerability privately to `security@swocts.com`; do not test
  it against another user's data.
