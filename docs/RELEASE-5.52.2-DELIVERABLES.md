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
| Backend tests | Pending |
| Wiki cookie flow | `204` with `wiki_session`; authenticated wiki `200`, unauthenticated `302` to login |
| Supply-chain lock | Updated and signed |
| Migration manifest | Regenerated from LF content; `opengrc:doctor` migration integrity now passes |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.2` | Pending |
| Production | `5.52.2` | Pending |

Post-deploy checks: `/api/version` `5.52.2` on both hosts, production and
development containers healthy, and the workspace verified at 1440 px and
1100 px widths. Rollback images are tagged `pre-v5.52.2` on both hosts.
