# Production deployment statement

**Statement date:** 16 November 2026

This is the authoritative statement for the current production deployment. If
another document disagrees, this page and the signed tag win.

## Release identity

| Item | Value |
|---|---|
| Release | **5.17.2** |
| Signed tag | **`v5.17.2`** |
| Runtime code commit | the commit tagged `v5.17.2` (`git tag -v v5.17.2`) |
| Alembic revision | **`0040_settings_change_control`** |
| Development host | `172.16.16.44` |
| Production host | `172.16.16.41` / `https://ctfd.swocts.com` |
| Repository | `RobChaykoski/opencyberrange` (`main`) |
| Pre-cutover backup | `~/backups/ocr-backup-20261116-181526.dump` |
| Post-cutover backup | `~/backups/ocr-backup-20261116-192307.dump` |
| Restore drills | **PASSED** (pre-cutover and post-cutover) |

## Production cutover: COMPLETE

The one-way production cutover was executed on **16 November 2026 at
19:21:54 UTC** by the `swocts` administrator.

| Item | Value |
|---|---|
| Change ticket | `123456` |
| Approver | Robert Chaykoski |
| Actor | `swocts` |
| Cutover record | `production_cutovers` id 1, `password_confirmed=true` |
| Evidence hash | `4f76c44efa7a30f70cb098e8da333013ce1aca79db5aee30a53bc78329afcfdf` |
| Ticket hash (SHA-256 of `123456`) | `8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92` |
| Security event | `production.cutover` #395 (critical, success) |
| Audit action | `PRODUCTION_CUTOVER` |

Post-cutover platform settings:

| Setting | Value |
|---|---|
| `deployment_mode` | **`production`** |
| `data_collection_mode` | **`production`** |
| `settings_change_ticket_mode` | **`required`** |

Settings changes now require a ticket and are recorded as revertible change
sets. The cutover cannot be reversed from the application.

## Test-account cleanup

Three unambiguous QA accounts were erased through the product erasure path
before the cutover. Real users and learner data were preserved.

| Account | Role | Result |
|---|---|---|
| `qa_tester_1114` | student | erased |
| `qa_tester_1115` | student | erased |
| `qa_release_check_20261116` | admin | erased |

- Accounts: **50 → 47**; administrators: **2 → 1** (`swocts`).
- Suppression ledger: 3 `committed` entries with hashed identities.
- Audit: 3 × `USER_DELETED` under ticket `123456` / approver Robert Chaykoski.
- Security event: `production.test_account_cleanup` #366.

Two accounts were deliberately retained by the operator: `smoke_tester`
(`smoke@swocts.com`, deployment smoke account) and `tester`
(`sgcloudca@gmail.com`, ambiguous one-off). They are not real-user data loss
risks, but they are not production identities; remove `smoke_tester` in
Admin → Users when convenient.

## Deployment state

- Backend: healthy, `/health` returns `200`.
- Frontend: healthy.
- Database and Valkey: healthy.
- `/api/version` returns `5.17.2`.
- Registered labs: **191**.
- Admin **System → Health → Release status** reports **Up to date** against
  `v5.17.2`.
- `ENVIRONMENT=production`.
- `OCR_DEPLOYMENT_MODE=production`.
- `OCR_AUTHZ_STRICT=true`.
- WireGuard encryption key is set.
- Cyber DNA, Cyber GPS, and portfolio consent defaults are **false** (opt-in).
- API docs remain disabled (`enable_api_docs=false`).

## 5.17.2 fix

`ReauthDialog.vue` posted to `/api/auth/reauth` through a client whose base URL
is already `/api`, so every re-authentication attempt hit
`/api/api/auth/reauth` and returned `404 Not Found`. This blocked the cutover's
re-auth challenge and every other re-authentication-gated action. 5.17.2 posts
to `/auth/reauth` and the regression test asserts the corrected path.

## Verification record

- `GET /api/version` → `5.17.2`
- `GET /health` → `200`
- `alembic current` → `0040_settings_change_control (head)`
- Registered labs → `191`
- Release status → `current` / `v5.17.2`
- Cutover → `deployment_mode=production`, `data_collection_mode=production`
- Post-cutover backup/restore → **PASSED** (47 users)

## Related documents

- [Release 5 production readiness](RELEASE-5-PRODUCTION-READINESS.md)
- [Deployment runbook](DEPLOYMENT-RUNBOOK.md)
- [Validation report](VALIDATION-REPORT.md)
- [Backup and restore test](BACKUP-RESTORE-TEST.md)
- [Deployment topology and sizing](DEPLOYMENT-TOPOLOGY-AND-SIZING.md)
