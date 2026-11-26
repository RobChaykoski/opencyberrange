# Release 5.52.4 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.52.4` |
| Signed tag | `v5.52.4` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.3` |

## Fixed and changed

| Area | Detail |
|---|---|
| Workbook new tab | `openWorkbook` refreshed the wiki cookie with `await` before `window.open`. Browsers treat that as a programmatic popup and block it. The tab opens synchronously; the cookie is refreshed after it, and the cookie is already set on login and when a lab opens. |
| Workspace regression | Stop now accepts the in-app **Stop exercise** confirmation instead of assuming `window.confirm`. The workbook size check follows `Expand workbook` / `Shrink workbook`, the framed workbook must render more than 400 characters and not be a login page, and KasmVNC WebRTC teardown messages are ignored. |

## Verification

| Check | Result |
|---|---|
| Workspace regression | **25 passed, 0 failed** on production (student, desktop + mobile) |
| Framed workbook | Rendered *Exercise 1.1 — Signing In and Opening RangeBox* (11,066 characters), not the login shell |
| RangeBox | VNC connected; no horizontal overflow at 1440 px |
| Mobile | Tabs layout, section jump bar, no horizontal overflow |
| Frontend tests | `56 passed` (21 files) |
| Frontend lint | `0 errors` |
| Frontend build | Passed |
| UI string budget | Passed (`5,412` budgeted strings) |
| Bundle budget | Passed |
| Link check | `1,224` Markdown files, no broken links |
| Backend tests | `637 passed`, `559 skipped` (unchanged backend) |
| Supply-chain lock | Updated and signed |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.4` | Deployed and verified |
| Production | `5.52.4` | Deployed and verified |

Post-deploy checks: `/api/version` reports `5.52.4` on both hosts, backend and
frontend containers are healthy, `nginx -t` passes, and the production wiki
rebuilt 14 sites. Production rollback images are tagged `pre-v5.52.4`.
Development rollback is a rebuild of `v5.52.3`, because the split-layout update
path does not create `pre-` tags.
