# Release 5.51.2 deliverables

Status: **released and deployed** to development and production on 25 November
2026.

| Item | Value |
|---|---|
| Version | `5.51.2` |
| Signed tag | `v5.51.2` |
| Release date | 25 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.51.1` |

## Changed

| Area | Detail |
|---|---|
| Practice exams | Full-width question navigation with separate **Previous question** and **Next question** controls. The submit action is isolated in its own panel, labelled **Submit for final mark**, warns about unanswered questions, and asks for confirmation before ending the attempt. |
| Analyst answers | Replaced the long exercise selector with a searchable, track-grouped library, saved-state badges, and a two-pane editor that opens the most recent saved answer. |
| Journey & mission | Removed the hard-coded light archive surface that appeared as a large white block in dark and high-contrast themes. The archive now uses theme tokens, observation counts, and a two-column layout; the current mission shows its tradition, summary, competencies, and first step. |
| Documentation | Updated the user manual, README, SECURITY supported versions, LICENSING release status, changelog, release index, and deployment runbook. |

## Verification

| Check | Result |
|---|---|
| Frontend tests | `50 passed` (20 files) |
| Frontend lint | `0 errors` |
| Frontend build | Passed |
| Backend tests | `637 passed`, `559 skipped` (DB-backed tests need `TEST_DATABASE_URL`) |
| UI string budget | Passed |
| Link check | `1,217` Markdown files, no broken links |
| Browser smoke | Passed in mock-API mode at desktop and mobile widths, dark and light themes; no console or page errors |
| Supply-chain lock | Updated and signed |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.51.2` | Deployed and verified |
| Production | `5.51.2` | Deployed and verified |

Post-deploy checks: `/api/version` `200` on both hosts, backend/frontend
containers healthy, production `nginx -t` passed, **217** registered labs and
**206** workbook-mapped labs, and **14** production wiki sites rebuilt.
Production pre/post backups: `ocr-backup-20261126-014950.dump` and
`ocr-backup-20261126-015407.dump`. Development pre-deploy backup:
`ocr-backup-20261126-014516.dump`. Rollback images are tagged
`pre-v5.51.2` on both hosts.

The development run ended with a non-blocking warning when the updater tried to
copy `ocr-platform.service` without sudo. The existing unit remained enabled and
active, and the deployed containers restarted healthy.
