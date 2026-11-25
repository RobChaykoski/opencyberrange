# Release 5.51.1 deliverables

Status: **released and deployed** to development and production on 25 November
2026.

| Item | Value |
|---|---|
| Version | `5.51.1` |
| Signed tag | `v5.51.1` |
| Release date | 25 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.51.0` (development-only; catalogue route collision) |

## Fixed

| Item | Detail |
|---|---|
| Tools route | The catalogue moved from `/tools` to `/toolbox`. Nginx serves the static `/tools/` directory for CyberChef, OT scan, and the ZAP planner, so `/tools` redirected to a 403 directory page instead of the SPA. Static tool URLs under `/tools/...` are unchanged. |
| Navigation and tests | Sidebar link, router, sidebar test, browser smoke and manual screenshot script now use `/toolbox`. |

## Included from 5.51.0

| Area | Detail |
|---|---|
| Navigation | Workspace, Learn, Tools, Your progress, Explore |
| Tools | Shared catalogue, ZAP scan planner, ZAP in the active-lab toolbar |
| Threat map | Interactive, privacy-safe aggregate map with hotspot list, challenge and opt-in OpenStreetMap link |
| Labs | Arkime `network-2-7-arkime-session-triage` and ZAP `web-11-11-zap-baseline-triage` |
| Data | 217 lab definitions, 206 workbook-mapped labs |

## Verification

| Check | Result |
|---|---|
| Frontend tests | `50 passed` |
| Frontend lint | `0 errors` (warnings are pre-existing) |
| Frontend build | Passed |
| Bundle budget | Passed |
| UI string budget | Passed |
| Backend tests | `1,196 passed` |
| Lab harness | ZAP lab `3/3` |
| ZAP baseline scan | 11 warnings, including Directory Browsing (10033) and Cookie No HttpOnly (10010) |
| Link check | `1,215` Markdown files, no broken links |
| Manual build | Passed |
| Supply-chain lock | Updated and signed |
| Production `/toolbox` | `200` |
| Production registered labs | `217` |
| Production restore drill | **PASSED**, 217 labs |
| Production restore-drift gate | **PASSED** at `0` |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.51.1` | Deployed and verified |
| Production | `5.51.1` | Deployed and verified |

Post-deploy checks: `/api/version` on both hosts, `/toolbox` `200`, `/tools/zap-scan/` `200`, nginx test, backend/frontend health, wiki builder, new lab prebuild, 217 registered labs, pre/post backups, restore drill and restore-drift gate at `0`.

## Known limitations

- The browser smoke was run in local mock mode; a live deployment run needs
  deployment credentials.
- The threat map links to OpenStreetMap but does not embed map tiles.
- The ZAP lab uses a synthetic Flask target, not the planned Juice Shop target.
- The 192 baseline-derived competency contracts still need subject-matter
  review.
