# Release 5.54.1 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.54.1` |
| Signed tag | `v5.54.1` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.54.0` |

## Fixed

| Area | Detail |
|---|---|
| Briefing pop-out workbook link | `App.vue` loads the wiki origin from `/api/config/public` after the route mounts. The pop-out now computes the workbook URL from the shared `wikiBaseUrl` ref, so a relative first URL is replaced with the configured origin when the config arrives. |
| Regression test | The pop-out test mounts the route, checks the initial relative link, then sets the wiki origin and asserts the link changes to the configured absolute URL. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `668 passed`, `559 skipped` (no backend source change) |
| Frontend tests | `70 passed` (24 files) |
| Frontend lint | `0 errors`; existing bare-string warnings remain baselined |
| Frontend build | Passed; bundle budget passed |
| Publication audit | `0 findings` |
| Link check | No broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match release `5.54.1` |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.54.1` | Deployed and verified |
| Production | `5.54.1` | Deployed and verified |

The change is frontend-only. Alembic stays at `0067_course_content_rls`, and
the lab and workbook definitions are unchanged.
