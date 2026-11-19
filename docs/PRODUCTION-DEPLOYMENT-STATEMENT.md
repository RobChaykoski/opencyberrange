# Production deployment statement

**Statement date:** 19 November 2026

This is the authoritative statement for the current production deployment. If
another document disagrees, this page and the signed tag win.

## Release identity

| Item | Value |
|---|---|
| Edition | **Community / Academic** (`lite` entitlement, single-host) |
| Release | **5.27.2** |
| Signed tag | **`v5.27.2`** |
| Runtime code commit | `57d654b0` (signed tag `v5.27.2`) |
| Previous release | `5.27.0` (signed tag `v5.27.0` at `ac18f7bd`) |
| Alembic revision | **`0047_lab_nice_metadata`** |
| Development host | `172.16.16.44` |
| Production host | `172.16.16.41` / `https://ctfd.swocts.com` |
| Repository | `RobChaykoski/opencyberrange` (`main`) |
| Pre-cutover backup | `~/backups/ocr-backup-20261116-181526.dump` |
| Post-cutover backup | `~/backups/ocr-backup-20261116-192307.dump` |
| 5.17.5 backup | `~/backups/ocr-backup-20261116-223835.dump` |
| Final backup (post-cleanup) | `~/backups/ocr-backup-20261117-012455.dump` |
| 5.17.6 backup | `~/backups/ocr-backup-20261117-025053.dump` |
| 5.17.7 backup | `~/backups/ocr-backup-20261117-035821.dump` |
| 19 November deploy backup | `~/backups/ocr-backup-20261119-024418.dump` |
| 5.19.0 backup | `~/backups/ocr-backup-20261119-034307.dump` |
| 5.20.0 backup | `~/backups/ocr-backup-20261119-042354.dump` |
| 5.21.0 backup | `~/backups/ocr-backup-20261119-045654.dump` |
| 5.22.0 backup | `~/backups/ocr-backup-20261119-051707.dump` |
| 5.24.2 backup | `~/backups/ocr-backup-20261119-062853.dump` |
| 5.25.0 backup | `~/backups/ocr-backup-20261119-065728.dump` |
| 5.26.0 backup | `~/backups/ocr-backup-20261119-072711.dump` |
| 5.27.0 backup | `~/backups/ocr-backup-20261119-083401.dump` |
| 5.27.1 backup | `~/backups/ocr-backup-20261119-194808.dump` |
| 5.27.2 backup | `~/backups/ocr-backup-20261119-201613.dump` |
| Restore drills | **PASSED** (pre-cutover, post-cutover, post-5.17.5, final, 5.17.6, 5.17.7, 19 November deploy, 5.19.0, 5.20.0, 5.21.0, 5.22.0, 5.27.0, 5.27.1, and 5.27.2) |

## 5.27.2 deployment verification

Deployed on 19 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.2` | `5.27.2` |
| Alembic | `0047_lab_nice_metadata` (head) | `0047_lab_nice_metadata` (head) |
| Build asset | `index-ddrlmI9g.js` | `index-ddrlmI9g.js` |
| Export fix | shared download helper present | shared download helper present |

The pre-deploy production backup is
`~/backups/ocr-backup-20261119-201613.dump` (2.4 MB, 1,700 objects). The restore
drill passed with 68 users, 210 labs, 47 enrolments, 124 completions, 465
achievements, and 1,383 activity events.

## 5.27.1 deployment verification

Deployed on 19 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.1` | `5.27.1` |
| Alembic | `0047_lab_nice_metadata` (head) | `0047_lab_nice_metadata` (head) |
| NICE review endpoint | present (`401` unauthenticated) | present (`401` unauthenticated) |
| NICE lab metadata rows | 210 | 210 |
| Manual API reference | includes `POST /api/nice/labs/{lab_id}/review` | includes the same endpoint |
| Build asset | `index-fNwqPTTY.js` | `index-fNwqPTTY.js` |
| Training-stack containers | expected dev stack | none |

The pre-deploy production backup is
`~/backups/ocr-backup-20261119-194808.dump` (2.4 MB, 1,700 objects). The restore
drill passed with 68 users, 210 labs, 47 enrolments, 124 completions, 465
achievements, and 1,383 activity events.

## 5.27.0 deployment verification

Deployed on 19 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.0` | `5.27.0` |
| Alembic | `0047_lab_nice_metadata` (head) | `0047_lab_nice_metadata` (head) |
| NICE lab metadata rows | 210 | 210 |
| NICE lab mappings | 2,484 | 2,484 |
| Manual stylesheet | 18,073 bytes | 18,073 bytes |
| Build asset | `index-DLCEIH0n.js` | `index-DLCEIH0n.js` |

The pre-deploy production backup is
`~/backups/ocr-backup-20261119-083401.dump` (2.3 MB, 1,694 objects).

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

## 5.17.7 additions

- Fixed admin course management: **Manage students** now opens the Instructor
  Panel course workspace at the selected course, where the working Enroll
  Students flow lives. **View course page** opens the learner-facing page.
- Added a **Review** column to Admin > Exercises for the competency-contract
  state, with content version, review date, and flag presence in the tooltip.
- Verified with 8/8 Playwright checks from the admin path and 38/38 general UI
  smoke checks.
- Production data after the load test: the **40 `stresstest_*` accounts** were
  erased through the normal erasure path on 2026-11-17 (suppression ledger
  updated), leaving **47 accounts** (44 students, 2 instructors, 1 admin),
  **2 courses**, and **46 enrollments**.

### Saturday readiness tuning (2026-11-17)

- PostgreSQL now runs with `shared_buffers=2GB`, `effective_cache_size=24GB`,
  `work_mem=32MB`, `maintenance_work_mem=1GB`, `max_connections=200`, and
  `random_page_cost=1.1`. The running container had been using stock defaults
  because the compose override replaces the tuned `postgres` command.
- Backend scaled from **1 to 4 uvicorn workers**; the 20+20 pool keeps the
  ceiling at 160 connections under the new 200 limit. Rate-limit counters are
  shared through Valkey, so limits stay global across workers.
- A fresh pre-change backup `ocr-backup-20261117-041146.dump` was taken and
  synced off-host before the cleanup and restart.
- Prebuilt the **22 missing lab images** (3 Identity, 10 Web-11 application
  security, and 9 Windows-11 Active Directory) so a first spawn does not wait
  for an image build.
- Login and registration limits now follow the live competition window
  automatically: **40/minute** login and **20/minute** registration per IP from
  `EVENT_BURST_BUFFER_MINUTES` (default 30) before the DevFest event until the
  same margin after it, with the strict limits outside it. The check is cached
  per worker and falls back to strict limits if the database read fails.
- The RangeBox live cap is pinned to **15** (the measured ceiling) for the
  mixed-desktop event. Clear `MAX_CONCURRENT_RANGEBOXES` to return to the 75%
  setting.

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

### Post-release content update

- Commit `e9b2c602` adds original study material for browser-side trust
  boundaries (XSS/CSRF), API security, and IoT/embedded security, plus seven
  original Web track knowledge-check questions. External platforms remain
  references only; no scenarios, questions, answers, flags, screenshots, or
  assets were copied.
- This is a content and documentation update on the 5.17.6 runtime; it does not
  change the schema, migrations, or application code.

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

- `GET /api/version` → `5.17.7`
- `GET /health` → `200`
- `alembic current` → `0041_tenant_rls_legacy (head)`
- Registered labs → `210` (170 public, 40 course-scoped)
- Release status → `current` / `v5.17.7`
- Cutover → `deployment_mode=production`, `data_collection_mode=production`
- 5.17.7 backup/restore → **PASSED** (87 users, 2 courses, 210 labs, 41 enrollments, 124 completions, 463 achievements)

## Related documents

- [Release 5 production readiness](RELEASE-5-PRODUCTION-READINESS.md)
- [Deployment runbook](DEPLOYMENT-RUNBOOK.md)
- [Validation report](VALIDATION-REPORT.md)
- [Backup and restore test](BACKUP-RESTORE-TEST.md)
- [Deployment topology and sizing](DEPLOYMENT-TOPOLOGY-AND-SIZING.md)
