# Production deployment statement

**Statement date:** 16 November 2026

This is the authoritative statement for the current production deployment. If
another document disagrees, this page and the signed tag win.

## Release identity

| Item | Value |
|---|---|
| Release | **5.17.1** |
| Signed tag | **`v5.17.1`** |
| Tag commit | `b9d99d2a` |
| Runtime code commit | `b9d99d2a` |
| Alembic revision | **`0040_settings_change_control`** |
| Development host | `172.16.16.44` |
| Production host | `172.16.16.41` / `https://ctfd.swocts.com` |
| Repository | `RobChaykoski/opencyberrange` (`main`) |
| Pre-deploy backup | `~/backups/ocr-backup-20261116-181526.dump` |
| Restore drill | **PASSED** on 16 November 2026 |

## Deployment state

- Backend: healthy, `/health` returns `200`.
- Frontend: healthy.
- Database and Valkey: healthy.
- `/api/version` returns `5.17.1` with the Release 5.17.1 name.
- Registered labs: **191**.
- Admin **System → Health → Release status** reports **Up to date** against
  `v5.17.1`.
- `ENVIRONMENT=production`.
- `OCR_DEPLOYMENT_MODE=production`.
- `OCR_AUTHZ_STRICT=true`.
- WireGuard encryption key is set.
- Cyber DNA, Cyber GPS, and portfolio consent defaults are **false** (opt-in).
- API docs remain disabled (`enable_api_docs=false`).

## Cutover status

**The one-way production cutover has not been executed.**

Current production platform settings:

| Setting | Value |
|---|---|
| `deployment_mode` | `development` |
| `data_collection_mode` | `sample` |

The code, production environment guards, and consent defaults are deployed and
verified, but production still carries the development/sample data
configuration. Sample accounts and sample course data may still be present. Do
not describe the deployment as a completed production cutover until the cutover
checklist is signed.

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

- `GET /api/version` → `5.17.1`
- `GET /health` → `200`
- `alembic current` → `0040_settings_change_control (head)`
- Registered labs → `191`
- Release status → `current` / `v5.17.1`
- Backup restore drill → `PASSED`
- CI on `b9d99d2a` → all workflows green

## Related documents

- [Release 5 production readiness](RELEASE-5-PRODUCTION-READINESS.md)
- [Deployment runbook](DEPLOYMENT-RUNBOOK.md)
- [Validation report](VALIDATION-REPORT.md)
- [Backup and restore test](BACKUP-RESTORE-TEST.md)
- [Deployment topology and sizing](DEPLOYMENT-TOPOLOGY-AND-SIZING.md)
