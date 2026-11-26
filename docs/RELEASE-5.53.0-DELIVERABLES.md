# Release 5.53.0 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.53.0` |
| Signed tag | `v5.53.0` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.10` |

## Added

| Area | Detail |
|---|---|
| HA status endpoint | `GET /api/admin/system/ha` reads the host collector's `/var/lib/ocr-ha/status.json`, sanitises the known fields, caches for 15 seconds, applies the 90-second staleness rule, and returns `ok` / `warning` / `error` / `unknown`. Admin-only, no query parameters, no write path. |
| Admin card | `HaStatusCard.vue` shows this node, preferred node, replication, Redis, witness, last failover, and the snapshot age. It renders the seven documented states, has no promote/failover control, and is hidden when HA is not configured. |
| Attention entries | `/api/admin/system/status` adds HA replication and witness items only when the snapshot exists; single-node installs are unchanged. |
| Operations reference | The HA repository now contains the source-allowlisted witness endpoint, the 30-second `ocr-ha-status` collector and systemd units, and the read-only API mount. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `666 passed`, `559 skipped` |
| HA status tests | `11 passed` |
| Frontend tests | `63 passed` (22 files) |
| Frontend lint | `0 errors` |
| Frontend build | Passed |
| UI string budget | Passed (`5,419` budgeted strings; reviewed +7) |
| Bundle budget | Passed |
| HA repository tests | Passed, including the witness endpoint and collector manifest |
| Publication audit | `0 findings` |
| API manual | Current |
| Link check | `1,230` Markdown files, no broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.53.0` | Deployed and verified |
| Production | `5.53.0` | Deployed and verified |

The HA card remains hidden until the host collector and witness endpoint are
installed; the platform deploy is safe without them.
