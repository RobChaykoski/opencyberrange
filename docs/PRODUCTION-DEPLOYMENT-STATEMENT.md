# Production deployment statement

**Statement date:** 20 November 2026

This is the authoritative statement for the current production deployment. If
another document disagrees, this page and the signed tag win.

## Release identity

| Item | Value |
|---|---|
| Edition | **Community / Academic** (`lite` entitlement, single-host) |
| Release | **5.28.3** |
| Signed tag | **`v5.28.3`** |
| Runtime code commit | `3e159055` (signed tag `v5.28.3`) |
| Previous release | `5.28.2` (signed tag `v5.28.2` at `3820fab3`) |
| Alembic revision | **`0048_performance_indexes`** |
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
| 5.27.3 backup | `~/backups/ocr-backup-20261119-205049.dump` |
| 5.27.4 backup | `~/backups/ocr-backup-20261120-003040.dump` |
| 5.27.5 backup | `~/backups/ocr-backup-20261120-010356.dump` |
| 5.27.6 backup | `~/backups/ocr-backup-20261120-011049.dump` |
| 5.27.7 backup | `~/backups/ocr-backup-20261120-011640.dump` |
| 5.28.0 backup | `~/backups/ocr-backup-20261120-014044.dump` |
| 5.28.1 backup | `~/backups/ocr-backup-20261120-014655.dump` |
| 5.28.2 backup | `~/backups/ocr-backup-20261120-015031.dump` |
| 5.28.3 backup | `~/backups/ocr-backup-20261120-015521.dump` |
| Restore drills | **PASSED** (pre-cutover, post-cutover, post-5.17.5, final, 5.17.6, 5.17.7, 19 November deploy, 5.19.0, 5.20.0, 5.21.0, 5.22.0, 5.27.0, 5.27.1, 5.27.2, 5.27.3, 5.27.4, 5.27.5, 5.27.6, 5.27.7, 5.28.0, 5.28.1, 5.28.2, and 5.28.3) |

## 5.28.3 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.28.3` | `5.28.3` |
| Startup validation | `validate_settings()` ran at lifespan start | same |
| Labs registered | 211 | 211 |
| `verify-lab-builds.sh` | standby prebuild 174/178 | **0 errors** |

No schema change. Backup `~/backups/ocr-backup-20261120-015521.dump`; restore
drill passed.

## 5.28.2 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.28.2` | `5.28.2` |
| Labs registered | 211 | 211 |
| Admin request bodies | Pydantic models for restore, bulk toggle, compose, impersonation launch, stress start/cancel | same |
| `verify-lab-builds.sh` | standby prebuild running | **0 errors** |

No schema change. Backup `~/backups/ocr-backup-20261120-015031.dump`; restore
drill passed.

## 5.28.1 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.28.1` | `5.28.1` |
| Labs registered | 211 | 211 |
| Retention counts | course 1: 6/42/37/95/0/2/61; course 2: zeros | same query |
| `GET /admin/users` side effects | none (Peer Manager sync removed) | same |
| `verify-lab-builds.sh` | standby prebuild running | **0 errors** |
| Public entry | — | `200` |

No schema change. Backup `~/backups/ocr-backup-20261120-014655.dump`; restore
drill passed with 211 labs, 46 enrolments, 124 completions, 465 achievements,
and 1,386 activity events.

## 5.28.0 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.28.0` | `5.28.0` |
| Labs registered | 211 | 211 |
| ICS lab | `ot-3-1-ics-pcap-forensics`, OT level 3, public | same |
| `verify-lab-builds.sh` | standby prebuild running | **0 errors** (211 labs) |
| Public entry | — | `200` |

The new lab carries 17 guided challenges over 22 MB of licensed captures
(TRITON/TRISIS BSD-3-Clause, Industroyer2 CC BY 4.0, GOOSE FDI CC BY 4.0,
CISA ICSNPP BSD-3-Clause). Its analyst image was verified over SSH with
`tshark` returning the 896 TriStation frames, and the guide serves 17
challenges.

The standby prebuild continues to close the remaining lab-image gap; run
`bash scripts/verify-lab-builds.sh` on `.44` when it completes.

## 5.27.7 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.7` | `5.27.7` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| Authenticated smoke | login → `/api/auth/me` `200` → mutation `404` | same code path |
| Mutating request decode | 1 signature decode + 1 revocation check | same |
| Spawn limits | 10/minute per user (IP fallback) | same |
| Public entry | — | `200` |

No schema change. Backup `~/backups/ocr-backup-20261120-011640.dump`; restore
drill passed with 67 users, 210 labs, 2 courses, 46 enrolments, 124
completions, 465 achievements, and 1,386 activity events.

## 5.27.6 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.6` | `5.27.6` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| Unknown-user login | 5 × `401`, then `429` with `Retry-After: 1` | same code path |
| Production startup guards | — | completed; RLS, invariants, RBAC, ledger all installed |
| Socket proxy `EXEC` | `1` (explicit) | `1` (explicit) |
| Public entry | — | `200` |

No schema change. Backup `~/backups/ocr-backup-20261120-011049.dump`; restore
drill passed with 67 users, 210 labs, 2 courses, 46 enrolments, 124
completions, 465 achievements, and 1,386 activity events.

## 5.27.5 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.5` | `5.27.5` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| `WG_SERVER_ADDRESS` | `10.1.0.1` | `10.0.0.1` |
| `wg0` address | `10.1.0.1/24` | `10.0.0.1/24` |
| Client `AllowedIPs` | lab `/24` + `10.1.0.1/32` | lab `/24` + `10.0.0.1/32` |
| Public entry | — | `200` |

No schema change. Backup `~/backups/ocr-backup-20261120-010356.dump`; restore
drill passed with 67 users, 210 labs, 2 courses, 46 enrolments, 124
completions, 465 achievements, and 1,386 activity events.

Existing downloaded VPN configs must be re-downloaded to pick up the server
host route; the dev configs also change to the `10.1.0.1` server address.

## 5.27.4 deployment verification

Deployed on 20 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.4` | `5.27.4` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| `next_quiz` in dashboard payload | present | present |
| Built bundle contains **Take a quiz** | yes | yes |
| Public entry `https://ctfd.swocts.com` | — | `200` |
| Redis rate-limit store | replica of production | `NOAUTH` without password |

No schema change. The backup was taken immediately after the deploy and the
restore drill passed with 67 users, 210 labs, 2 courses, 46 enrolments, 124
completions, 465 achievements, and 1,386 activity events.

## 5.27.3 deployment verification

Deployed on 19 November 2026 to development and production.

| Check | Development | Production |
|---|---|---|
| `/api/version` | `5.27.3` | `5.27.3` |
| Alembic | `0048_performance_indexes` (head) | `0048_performance_indexes` (head) |
| Performance indexes | 5 present | 5 present |
| Build asset | `index-Da4XZRrW.js` | `index-Da4XZRrW.js` |
| Asset cache | `public, max-age=31536000, immutable` | same |

Warm dev measurements before/after the change: `/api/labs` 77 ms → 45 ms,
student dashboard 99 ms → 77 ms, `/api/auth/me` remains around 28 ms without a
Peer Manager round-trip.

The pre-deploy production backup is
`~/backups/ocr-backup-20261119-205049.dump` (2.4 MB, 1,700 objects). The restore
drill passed with 67 users, 210 labs, 46 enrolments, 124 completions, 465
achievements, and 1,386 activity events.

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
