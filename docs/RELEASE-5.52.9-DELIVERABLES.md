# Release 5.52.9 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.52.9` |
| Signed tag | `v5.52.9` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.8` |

## Fixed and added

| Area | Detail |
|---|---|
| Split-layout deploy | The backend sync keeps `run-state`, so exercise-tester and impersonation state survives a deploy. |
| Refresh helper | `scripts/refresh-threat-snapshots.sh` downloads the current DB-IP Lite database, regenerates both snapshots into a review directory, validates them, and prints a diff. It never commits or deploys. |
| Cadence | The operations guide documents a weekly cron; a weekly OpenCode check prompts a reviewed signed release. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `651 passed`, `559 skipped` (DB-backed tests need `TEST_DATABASE_URL`) |
| Refresh helper syntax | `bash -n` passed |
| Publication audit | `0 findings` |
| API manual | Current |
| Link check | `1,229` Markdown files, no broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.9` | Deployed and verified |
| Production | `5.52.9` | Deployed and verified |
