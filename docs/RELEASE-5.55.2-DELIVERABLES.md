# Release 5.55.2 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.55.2` |
| Signed tag | `v5.55.2` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.55.1` |

## Fixed

| Area | Detail |
|---|---|
| Pathway mapping | The pathway data uses manifest ids (`webpt`, `linpt`, `winpt`, `netfor`) while the catalogue uses database slugs (`web`, `linux`, `windows`, `network`). A shared canonical mapping now translates them before the visibility filter. |
| Penetration Tester | The focused catalogue now shows Web, Linux, Windows, and Network instead of returning an empty set. |
| SOC Analyst | The focus again includes the core Windows, Linux, and Network tracks alongside Forensics and Identity. |
| Role readiness | Next-workbook selection and completed-role evidence count use the same canonical mapping, so work in the mapped tracks is no longer ignored. |
| Regression tests | The catalogue and alias tests assert the full Penetration Tester set and the canonical slug translation. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `671 passed`, `562 skipped` |
| Frontend tests | `77 passed` (25 files) |
| Frontend lint | `0 errors`; bare-string budget passes |
| Frontend build | Passed; bundle budget passes |
| Publication audit | `0 findings` |
| Link check | No broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match release `5.55.2` |

## Mapping checks

| Pathway | Canonical tracks |
|---|---|
| Penetration Tester | `web`, `linux`, `windows`, `network` |
| SOC Analyst | `network`, `windows`, `linux`, `forensics`, `identity` |
| Cybersecurity Foundations | `high-school`, `network`, `linux`, `identity`, `osint`, `ai` |

The mapping is a name translation, not an access rule. The backend still
intersects the pathway set with the tracks the learner is allowed to see.

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.55.2` | Deployed and verified |
| Production | `5.55.2` | Deployed and verified |

The change is backend pathway metadata and filtering. It has no database
migration and does not change lab definitions.
