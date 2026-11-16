# Production deployment statement

**Statement date:** 16 November 2026

This is the authoritative statement for the current production deployment. If
another document disagrees, this page and the signed tag win.

## Release identity

| Item | Value |
|---|---|
| Release | **5.17.0** |
| Signed tag | **`v5.17.0`** |
| Tag commit | `17c9a7e8` |
| Runtime code commit | `291d831b` (backend rebuilt; docs commit follows) |
| Alembic revision | **`0040_settings_change_control`** |
| Development host | `172.16.16.44` |
| Production host | `172.16.16.41` / `https://ctfd.swocts.com` |
| Repository | `RobChaykoski/opencyberrange` (`main`) |
| Pre-deploy backup | `~/backups/ocr-backup-20261116-172935.dump` |

## Deployment state

- Backend: healthy, `/health` returns `200`.
- Frontend: healthy.
- Database and Valkey: healthy.
- `/api/version` returns `5.17.0` with the Release 5.17 name.
- Registered labs: **191**.
- Admin **System → Health → Release status** reports **Up to date** against
  `v5.17.0`.
- `ENVIRONMENT=production`.
- WireGuard encryption key is set.
- API docs remain disabled (`enable_api_docs=false`).

## Cutover status

**The one-way production cutover has not been executed.**

Current production platform settings:

| Setting | Value |
|---|---|
| `deployment_mode` | `development` |
| `data_collection_mode` | `sample` |

The code is deployed and verified, but production still carries the
development/sample configuration. Sample accounts and sample course data may
still be present. Do not describe the deployment as a completed production
cutover until the cutover checklist is signed.

## Cutover gate

The cutover requires all of the following:

1. an approved change ticket or recorded reason;
2. the operator password;
3. the exact phrase `GO PRODUCTION`;
4. both acknowledgements in the cutover dialog;
5. a fresh backup and a successful restore drill;
6. removal or disablement of sample accounts and sample data;
7. post-cutover verification of sign-in, RBAC, labs, certificates, exports, and
   the release status panel.

## Verification record

- `GET /api/version` → `5.17.0`
- `GET /health` → `200`
- `alembic current` → `0040_settings_change_control (head)`
- Registered labs → `191`
- Release status → `current` / `v5.17.0`
- CI on `17c9a7e8` → all workflows green

## Related documents

- [Release 5 production readiness](RELEASE-5-PRODUCTION-READINESS.md)
- [Deployment runbook](DEPLOYMENT-RUNBOOK.md)
- [Validation report](VALIDATION-REPORT.md)
- [Backup and restore test](BACKUP-RESTORE-TEST.md)
- [Deployment topology and sizing](DEPLOYMENT-TOPOLOGY-AND-SIZING.md)
