# Release 5.51.0 deliverables

Status: **superseded by 5.51.1 before production**; the tools catalogue moved
from `/tools` to `/toolbox` after nginx served the static `/tools/` directory as
a 403.

| Item | Value |
|---|---|
| Version | `5.51.0` |
| Signed tag | `v5.51.0` |
| Release date | 25 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |

## Navigation and labels

| Deliverable | Detail |
|---|---|
| Learner sidebar | Workspace, Learn, Tools, Your progress, Explore |
| Label alignment | Analyst answers, Journey & mission, Impact & recognition, Evidence portfolio, Threat map, Course workspace, Exercise authoring, Career GPS, Cyber DNA |
| Admin labels | Course catalogue, Exercise library, Sessions & activity, System health, Platform settings |
| Tool placement | Tools is global and sits above the long progress groups |
| Manual | Navigation, instructor, admin, glossary and screenshots updated |

## Tools

| Deliverable | Detail |
|---|---|
| Tools catalogue | `/tools` (superseded by `/toolbox` in 5.51.1) for CyberChef, OT scan, ATT&CK Navigator and ZAP |
| Shared panel | Every card uses the same allow-listed, sandboxed panel |
| ZAP planner | `/tools/zap-scan/`, with baseline/full commands, reports, authorisation gate and triage checklist |
| Lab toolbar | ZAP added beside CyberChef, OT scan and ATT&CK |
| Verification | 27/27 browser checks at desktop and mobile widths |

## Threat map

| Deliverable | Detail |
|---|---|
| Map | Country bubble map over the aggregated FireHOL snapshot |
| Interaction | Region and bucket filters, hotspot list, selected-country panel, local challenge |
| Privacy | Aggregate counts only; no address, host, learner, lab, packet or flow |
| External link | Opt-in OpenStreetMap link; no tile fetch |
| Tests | Map, challenge, tool catalogue and sidebar tests |

## Labs

| Deliverable | Detail |
|---|---|
| Arkime | `network-2-7-arkime-session-triage`, DET-08 |
| ZAP | `web-11-11-zap-baseline-triage`, MAS-06 |
| ZAP target | Disposable Flask practice app with a public export directory and synthetic token |
| ZAP workbook | Web 11 workbook page with scanner triage, manual confirmation, remediation and retest |
| Harness | ZAP lab passed 3/3 clean runs |
| ZAP scan | Baseline returned 11 warnings, including Directory Browsing (10033) and Cookie No HttpOnly (10010) |

## Verification

| Check | Result |
|---|---|
| Frontend tests | `50 passed` |
| Frontend lint | `0 errors` (warnings are pre-existing) |
| Frontend build | Passed |
| Bundle budget | Passed |
| UI string budget | Passed |
| Backend tests | `1,196 passed` |
| Lab harness | ZAP lab `3/3`; Arkime lab already `3/3` |
| Link check | `1,215` Markdown files, no broken links |
| Manual build | Passed |
| Supply-chain lock | Updated and signed |
| ZAP lab static validation | `21/22`, with one resource-limit INFO |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.51.0` | Deployed briefly, then superseded by 5.51.1 |
| Production | `5.51.0` | Not deployed; 5.51.1 was the production release |

Post-deploy checks: `/api/version` on both hosts, nginx test, backend/frontend
health, wiki builder, new lab prebuild, backup and restore drill.

## Known limitations

- The browser smoke was run in local mock mode; a live deployment run needs
  deployment credentials.
- The threat map links to OpenStreetMap but does not embed map tiles.
- The ZAP lab uses a custom Flask practice target, not the planned Juice Shop
  target. The target is synthetic and offline.
- The 192 baseline-derived competency contracts still need subject-matter
  review.
