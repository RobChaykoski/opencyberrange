# Release 5.52.2 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.52.2` |
| Signed tag | `v5.52.2` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.1` |

## Fixed and changed

| Area | Detail |
|---|---|
| Exercise workspace | RangeBox and exercise details share the left column; the workbook is a full-height right pane, so the lower exercise pane matches the desktop width. The wide-screen splitter is capped so the desktop keeps most of the height. |
| Workbook iframe | The workspace now awaits the wiki session cookie before revealing the iframe. The previous first request raced the cookie and rendered the wiki login shell as a white page with a skip link and logo. |
| Exercise feedback | **Was this exercise useful?** appears only after the exercise is completed. |
| Workspace chrome | Knowledge check and the CyberChef, OT Scan, ATT&CK, and ZAP launchers collapse into one **Tools** menu. Briefing, targets, and the flag lead; evidence, disclosures, and hints follow. |
| Accessibility | Administrator and instructor tables use `scope="col"` on header cells. |
| Documentation | Updated version, release records, supported versions, licensing status, and the deployment runbook. |

## Verification

| Check | Result |
|---|---|
| Frontend tests | `56 passed` (21 files) |
| Frontend lint | `0 errors` |
| Frontend build | Passed |
| UI string budget | Passed (`5,412` budgeted strings) |
| Bundle budget | Passed (largest chunk `540 KB`) |
| Link check | `1,222` Markdown files, no broken links |
| Backend tests | `637 passed`, `559 skipped` (DB-backed tests need `TEST_DATABASE_URL`) |
| Wiki cookie flow | `204` with `wiki_session`; authenticated wiki `200`, unauthenticated `302` to login |
| Supply-chain lock | Updated and signed |
| Migration manifest | Regenerated from LF content; `opengrc:doctor` migration integrity now passes |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.2` | Deployed and verified |
| Production | `5.52.2` | Deployed and verified |

Post-deploy checks: `/api/version` reports `5.52.2` on both hosts, backend and
frontend containers are healthy, `nginx -t` passes, lab discovery is
idempotent, and the production wiki rebuilt 14 sites. Production pre-deploy
backup: `ocr-backup-20261126-035257.dump`. Development pre-deploy backup:
`ocr-backup-20261126-035105.dump`. Rollback images are tagged `pre-v5.52.2` on
both hosts. The manual three-role browser pass still needs dedicated test
accounts; the layout is covered by the frontend build, component tests, and the
wide/tab breakpoint logic at 1200 px.
