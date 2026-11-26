# Release 5.53.1 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.53.1` |
| Signed tag | `v5.53.1` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.53.0` |

## Fixed

| Area | Detail |
|---|---|
| HA status data path | The backend service mounts `/var/lib/ocr-ha:/var/lib/ocr-ha:ro` in the production and development compose. The host collector writes the snapshot there; the card stays hidden until the file exists. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `666 passed`, `559 skipped` |
| Frontend tests | `63 passed` (22 files) |
| Compose YAML | Parses for production and development |
| Publication audit | `0 findings` |
| API manual | Current |
| Link check | `1,232` Markdown files, no broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.53.1` | Deployed and verified |
| Production | `5.53.1` | Deployed and verified |

The HA card remains hidden until the witness endpoint and host collector are
installed and `/var/lib/ocr-ha/status.json` exists.
