# Release 5.52.7 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.52.7` |
| Signed tag | `v5.52.7` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.6` |

## Changed

| Area | Detail |
|---|---|
| Hostile infrastructure snapshot | Regenerated from the FireHOL feeds with DB-IP Lite `2026-11` country attribution. `467,952` reported entries across `147` countries; generated `2026-11-26T16:47:21Z`. |
| Ransomware activity snapshot | Regenerated from the RansomLook aggregate endpoints. `325` posts in the last seven days across `15` groups; generated `2026-11-26T16:47:27Z`. |
| Refresh cadence | `docs/THREAT-AWARENESS-OPERATIONS.md` now suggests RansomLook every one to three days (weekly at minimum) and FireHOL weekly with the monthly DB-IP file. |

Both snapshots remain aggregated and address-free, and are still shipped as
signed release artifacts rather than fetched at runtime.

## Verification

| Check | Result |
|---|---|
| Threat snapshot validation | `snapshot` mode, `467,952` entries, `147` countries |
| Ransomware snapshot validation | `snapshot` mode, `325` window posts, `15` groups |
| Publication audit | `0 findings` |
| API manual | Current |
| Link check | `1,226` Markdown files, no broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.7` | Deployed and verified |
| Production | `5.52.7` | Deployed and verified |
