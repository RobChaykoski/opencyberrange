# Release 5.52.1 deliverables

Status: **release prepared; deployment verification pending.**

| Item | Value |
|---|---|
| Version | `5.52.1` |
| Signed tag | `v5.52.1` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.0` |

## Fixed and changed

| Area | Detail |
|---|---|
| WireGuard verifier | Fixed the operator script to support the current `lab/24,server/32` allowed-IP set instead of assuming one network. |
| WireGuard peers | Synced two active student configs that had no Peer Manager peer. Re-verified 11 clients and 217 active labs. |
| Accessibility | Added a global visible focus ring for links, buttons, native inputs, selects, textareas, nav items, and tabbable elements. |
| Admin and instructor UI | Added the restrained accent hero surface used by the student dashboard/profile, and raised subtitle contrast from muted to secondary. |
| Documentation | Updated version and release records, security supported versions, licensing status, and the deployment runbook. |

## Verification

| Check | Result |
|---|---|
| WireGuard route verifier | `PASS` for 11 clients across 217 labs |
| WireGuard peers | 11 configs, 11 peers |
| Frontend tests | `56 passed` (21 files) |
| Frontend lint | `0 errors` |
| Frontend build | Passed |
| UI string budget | Passed |
| Link check | `1,221` Markdown files, no broken links |
| Backend tests | `637 passed`, `559 skipped` (DB-backed tests need `TEST_DATABASE_URL`) |
| Production logs today | No 5xx responses and no backend exceptions |
| Supply-chain lock | Updated and signed |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.1` | Pending |
| Production | `5.52.1` | Pending |

Post-deploy checks: `/api/version` on both hosts, nginx test, backend/frontend health, VPN route verification, and pre/post backups.
