# SWOCTS Cyber Range 1.0 release record (powered by OpenCyberRange)

## Release identity

- Version: `1.0.0`
- Release date: 2026-11-04
- Tag: `v1.0.0`
- Version source: `platform/backend/app/version.py`
- Runtime policy: `versions.yaml`

## Scope

OpenCyberRange 1.0 is a stable self-hosted teaching release. It covers the platform services, curriculum, learner experience, instructor and admin workflows, privacy tooling, certificates, competitions, and backup/restore operations.

## Supported deployment

- Docker Compose production stack (`platform/docker-compose.prod.yml`).
- PostgreSQL 15 in the current supported stack, with the upgrade path recorded in `versions.yaml`.
- WireGuard learner access and optional WSTunnel access.

## Release gates

| Gate | Status |
| --- | --- |
| Backend test suite | Passed |
| Frontend lint and build | Passed |
| Test-stack deployment | Passed |
| Production upgrade | Passed |
| Persistent snapshot collection | Passed |
| Snapshot survives backend recreation | Passed |
| Restore drill | Passed |
| Personal-data export state | Passed |
| Profile summary serialization | Passed |

## Upgrade procedure

1. Create a snapshot from **Admin → System → Backups**.
2. Record the current Git commit.
3. Pull `v1.0.0`.
4. Rebuild and recreate the stack.
5. Verify:
   - `/health` returns `status: healthy` and `version: 1.0.0`.
   - The previous snapshot still appears in the Backups tab.
   - A new daily snapshot is collected in `/app/backups`.
6. Run a login and certificate smoke test.

## Rollback procedure

1. Stop the stack.
2. Check out the previous release tag or recorded commit.
3. Restore the pre-upgrade snapshot if the database schema changed.
4. Rebuild and start the stack.
5. Verify health and authentication.

## Backup policy

- Snapshot directory: `/app/backups`, mounted as the `backups_data` volume.
- Automatic collection: every 24 hours, first run on startup when no snapshot exists.
- Retention: 30 days by default.
- Configuration:
  - `OCR_BACKUP_DIR`
  - `OCR_BACKUP_INTERVAL_HOURS` (`0` disables automatic collection)
  - `OCR_BACKUP_RETENTION_DAYS` (`0` keeps every snapshot)
- The erasure suppression ledger is copied beside each dump.

## Known limitations and follow-up work

- Snapshot encryption at rest remains an operator responsibility.
- Accessibility conformance should be re-audited after any major UI change.
- Sponsor logos are stored in the database, not object storage.
- Multi-worker rate limiting requires a shared `RATELIMIT_STORAGE_URI`.
