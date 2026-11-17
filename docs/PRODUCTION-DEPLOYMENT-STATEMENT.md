# Production deployment statement

**Statement date:** 17 November 2026

This is the authoritative statement for the current production deployment. If
another document disagrees, this page and the signed tag win.

## Release identity

| Item | Value |
|---|---|
| Edition | **Community / Academic** (`lite` entitlement, single-host) |
| Release | **5.17.6** |
| Signed tag | **`v5.17.6`** |
| Runtime code commit | `d2b2285d` (signed tag `v5.17.6`) |
| Alembic revision | **`0041_tenant_rls_legacy`** |
| Development host | `172.16.16.44` |
| Production host | `172.16.16.41` / `https://ctfd.swocts.com` |
| Repository | `RobChaykoski/opencyberrange` (`main`) |
| Pre-cutover backup | `~/backups/ocr-backup-20261116-181526.dump` |
| Post-cutover backup | `~/backups/ocr-backup-20261116-192307.dump` |
| 5.17.5 backup | `~/backups/ocr-backup-20261116-223835.dump` |
| Final backup (post-cleanup) | `~/backups/ocr-backup-20261117-012455.dump` |
| 5.17.6 backup | `~/backups/ocr-backup-20261117-025053.dump` |
| Restore drills | **PASSED** (pre-cutover, post-cutover, post-5.17.5, final, and 5.17.6) |

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
- `/api/version` returns `5.17.5`.
- Registered labs: **210**.
- Admin **System → Health → Release status** reports **Up to date** against
  `v5.17.5`.
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

## 5.17.6 additions

- Production settings UX: **Run ceiling test** now checks the ticket and reason
  before the confirmation prompt, shows an inline hint beside the RangeBox
  capacity card, highlights Production change control, and focuses the missing
  field. Verified with 16/16 Playwright checks on the production presentation.
- Workbook: added the required Analysis Questions to all 19 level-11 pathway
  pages. Coverage remains **201 of 210**.
- Achievements: `ad_pathfinder` (all nine AD exercises) and
  `appsec_architect` (all ten AppSec exercises) are live global completion
  badges, visible in the catalogue and manual.
- Manual: 53 screenshots refreshed on dev with Privacy Mode explicitly on for
  admin and instructor views; populated pending and locked demo states.
- Counts clarified: **210 registered labs** = **170 public** + **40
  course-scoped**.
- Removed the revoked `Test-api` service identity and its service credential
  (ticket `123456`); users returned to **47**.
- Validation: 909 backend tests, frontend lint/tests/build, 38/38 UI smoke
  checks, link/doc-asset/workbook/lab/quiz/security checks pass.

## 5.17.5 additions

- Documentation cleanup: documentation skill, docs index, category hubs,
  archive, CODEOWNERS, SUPPORT, and PRIVACY. Current-state counts reconciled to
  **210 labs, 13 tracks, 25 tenant-RLS tables**.
- Password-prompt verification: login, re-authentication, change-password,
  account deletion, admin reset, MFA disable, and the cutover gate accept the
  correct password and reject wrong, oversized, control-character, and
  injection-shaped input.
- Live deployed check on development: correct login, re-authentication, and
  change-password returned `200`; wrong, oversized, and newline inputs returned
  `401`; the temporary verification account was removed.
- Bounded, log-safe login input and `maxlength` on password prompts.
- Manual screenshots audited for synthetic data; a refresh to the current build
  is pending demo credentials.
- Workbook: `CH_WIN11_AD_Pathway` and `CH_WEB11_AppSec_Pathway` added, raising
  coverage to **201 of 210** labs; the workbook wiki was rebuilt and the new
  chapters are served. Each of the 19 pages includes the required Analysis
  Questions.
- Pathway achievements: `ad_pathfinder` (all nine AD exercises) and
  `appsec_architect` (all ten AppSec exercises) are global completion badges,
  registered in the catalogue and covered by a regression test.
- Live harness: all **19 new pathway labs** pass one clean run. The AD solver now
  waits for the LDAP bootstrap and disables LDIF line wrapping.
- Residual smoke-test account `smoke_tester` removed; users 48 → 47, real users
  and learner data preserved.

## 5.17.3 additions

- Migration `0041_tenant_rls_legacy` extends forced tenant RLS to 16 legacy
  learner tables (25 enforced tables total).
- The 9 Active Directory (`windows-11-*`) and 10 modern application-security
  (`web-11-*`) pathway labs are implemented; the catalogue is 210 labs.
- The Community / Academic edition keeps a single `default` institution while
  the RLS backstop remains edition-agnostic.

## Verification record

- `GET /api/version` → `5.17.6`
- `GET /health` → `200`
- `alembic current` → `0041_tenant_rls_legacy (head)`
- Registered labs → `210` (170 public, 40 course-scoped)
- Release status → `current` / `v5.17.6`
- Cutover → `deployment_mode=production`, `data_collection_mode=production`
- 5.17.6 backup/restore → **PASSED** (47 users, 210 labs, 41 enrollments, 124 completions, 463 achievements)

## Related documents

- [Release 5 production readiness](RELEASE-5-PRODUCTION-READINESS.md)
- [Deployment runbook](DEPLOYMENT-RUNBOOK.md)
- [Validation report](VALIDATION-REPORT.md)
- [Backup and restore test](BACKUP-RESTORE-TEST.md)
- [Deployment topology and sizing](DEPLOYMENT-TOPOLOGY-AND-SIZING.md)
