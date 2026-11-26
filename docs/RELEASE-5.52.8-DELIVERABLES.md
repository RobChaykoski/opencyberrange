# Release 5.52.8 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.52.8` |
| Signed tag | `v5.52.8` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.7` |

## Changed

| Area | Detail |
|---|---|
| Curated threat feeds | The hostile-infrastructure snapshot now combines the FireHOL iplists with DShield (30-day subnets via FireWALL-E), Blocklist.de, abuse.ch Feodo Tracker (aggressive), OffSeq Mirage (CC BY 4.0), and IPsum level 3 (Unlicense). `519,839` reported entries across `152` countries and `13` categories; generated `2026-11-26T17:02:49Z`. |
| Ransomware snapshot | Refreshed from the RansomLook aggregate endpoints: `325` posts in seven days across `15` groups; generated `2026-11-26T17:02:51Z`. |
| Split-layout deploy | `scripts/deploy-updates.sh` now syncs release content under `backend/app/data` instead of excluding the whole directory. Backups and the external-dataset cache stay untouched. |
| Refresh cadence | Operations guidance recommends a weekly snapshot with the daily feeds and RansomLook every one to three days. |

The map remains aggregated and address-free. Feeds are ingested on an
operations host; there is no runtime egress.

## Verification

| Check | Result |
|---|---|
| Threat snapshot validation | `snapshot` mode, `519,839` entries, `152` countries, `13` categories |
| Feed categories | FireHOL (7), DShield, Blocklist.de, Feodo, OffSeq Mirage, IPsum (`13` total) |
| Ransomware validation | `snapshot` mode, `325` window posts, `15` groups |
| Backend tests | `651 passed`, `559 skipped` (DB-backed tests need `TEST_DATABASE_URL`) |
| Publication audit | `0 findings` |
| API manual | Current |
| Link check | `1,228` Markdown files, no broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.8` | Deployed and verified |
| Production | `5.52.8` | Deployed and verified |
