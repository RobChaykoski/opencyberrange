# Backup and restore testing

Backup creation is not evidence of recoverability. This page records both.

## Current evidence

| Item | Value |
|---|---|
| Pre-cutover backup | `~/backups/ocr-backup-20261116-181526.dump` |
| Post-cutover backup | `~/backups/ocr-backup-20261116-192307.dump` |
| 5.17.5 backup | `~/backups/ocr-backup-20261116-223835.dump` |
| Final backup (post-cleanup) | `~/backups/ocr-backup-20261117-012455.dump` |
| 5.17.6 backup | `~/backups/ocr-backup-20261117-025053.dump` |
| 5.17.7 backup | `~/backups/ocr-backup-20261117-035821.dump` |
| 5.19.0 backup | `~/backups/ocr-backup-20261119-034307.dump` |
| 5.20.0 backup | `~/backups/ocr-backup-20261119-042354.dump` |
| 5.21.0 backup | `~/backups/ocr-backup-20261119-045654.dump` |
| 5.22.0 backup | `~/backups/ocr-backup-20261119-051707.dump` |
| 5.24.2 backup | `~/backups/ocr-backup-20261119-062853.dump` |
| 5.25.0 backup | `~/backups/ocr-backup-20261119-065728.dump` |
| 5.26.0 backup | `~/backups/ocr-backup-20261119-072711.dump` |
| 5.27.0 backup | `~/backups/ocr-backup-20261119-083401.dump` |
| 5.27.1 backup | `~/backups/ocr-backup-20261119-194808.dump` |
| 5.27.2 backup | `~/backups/ocr-backup-20261119-201613.dump` |
| 5.27.3 backup | `~/backups/ocr-backup-20261119-205049.dump` |
| 5.39.0 pre-deploy backup | `~/backups/ocr-backup-20261124-033307.dump` |
| 5.39.0 post-deploy backup | `~/backups/ocr-backup-20261124-033536.dump` |
| 5.40.0 pre-deploy backup | `~/backups/ocr-backup-20261124-043101.dump` |
| 5.40.0 post-deploy backup | `~/backups/ocr-backup-20261124-043218.dump` |
| 5.41.0 pre-deploy backup | `~/backups/ocr-backup-20261124-060903.dump` |
| 5.41.0 post-deploy backup | `~/backups/ocr-backup-20261124-061257.dump` |
| 5.42.0 pre-deploy backup | `~/backups/ocr-backup-20261124-161705.dump` |
| 5.42.0 post-deploy backup | `~/backups/ocr-backup-20261124-162049.dump` |
| 5.42.0 post-reboot backup | `~/backups/ocr-backup-20261124-162948.dump` |
| 5.43.1 pre-deploy backup | `~/backups/ocr-backup-20261124-170800.dump` |
| 5.43.1 post-deploy backup | `~/backups/ocr-backup-20261124-171127.dump` |
| 5.44.0 pre-deploy backup | `~/backups/ocr-backup-20261124-173551.dump` |
| 5.44.0 post-deploy backup | `~/backups/ocr-backup-20261124-173923.dump` |
| 5.45.0 pre-deploy backup | `~/backups/ocr-backup-20261124-181940.dump` |
| 5.45.0 post-deploy backup | `~/backups/ocr-backup-20261124-182316.dump` |
| 5.46.0 pre-deploy backup | `~/backups/ocr-backup-20261124-185419.dump` |
| 5.46.0 post-5.46.1 pre-deploy backup | `~/backups/ocr-backup-20261124-190258.dump` |
| 5.46.1 post-deploy backup | `~/backups/ocr-backup-20261124-190626.dump` |
| 5.46.2 pre-deploy backup | `~/backups/ocr-backup-20261124-191033.dump` |
| 5.46.2 post-deploy backup | `~/backups/ocr-backup-20261124-191400.dump` |
| 5.47.0 pre-deploy backup | `~/backups/ocr-backup-20261124-201516.dump` |
| 5.47.0 post-deploy backup | `~/backups/ocr-backup-20261124-201850.dump` |
| 5.48.0 pre-deploy backup | `~/backups/ocr-backup-20261124-203634.dump` |
| 5.48.0 post-deploy backup | `~/backups/ocr-backup-20261124-203951.dump` |
| 5.49.0 pre-deploy backup | `~/backups/ocr-backup-20261124-205252.dump` |
| 5.49.0 post-deploy backup | `~/backups/ocr-backup-20261124-205618.dump` |
| Restore drills | **PASSED** pre-cutover, post-cutover, post-5.17.5, final, 5.17.6, 5.17.7, 5.19.0, 5.20.0, 5.21.0, 5.22.0, 5.27.0, 5.27.1, 5.27.2, 5.27.3, 5.39.0, 5.40.0, 5.41.0, 5.42.0, 5.43.1, 5.44.0, 5.45.0, 5.46.0, 5.46.1, 5.46.2, 5.47.0, 5.48.0, and 5.49.0 |
| Final restored state | 69 users, 2 courses, 215 labs, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events |
| Restored tables compared | users, labs, courses, course_enrollments, lab_completions, achievements, review_requests, activity_events |
| Backup retention | 14 days by default (`RETENTION_DAYS`) |

The drill restored the dump into a scratch database, compared row counts, and
dropped the scratch database. The live database was not modified.

## Procedure

```bash
# 1. Take a fresh backup
bash scripts/backup-production.sh

# 2. Immediately restore the newest dump to a scratch database
bash scripts/restore-drill.sh
```

A drill must run immediately after a backup. Comparing a backup to a live
database that has taken new writes will show expected drift (for example, a new
user) and is not a restore failure.

## Snapshot identity

The admin **Create snapshot** action must dump with a role that can bypass
tenant RLS. Release 5.21.0 prefers `BACKUP_DATABASE_URL`, then
`MIGRATOR_DATABASE_URL`, then `DATABASE_URL`. The host backup script uses the
database superuser. Never point the snapshot path at the runtime role on a
database with forced RLS: `pg_dump` fails on tables such as
`accommodation_events`.

## Data at rest

The local `backups_data` volume holds plaintext SQL, including password hashes,
sessions, and PII. It is protected by the host/volume encryption decision, mode
`700/600`, admin-only download with recent re-authentication, and the audit log.
The off-host path is GPG-encrypted. Read
[Backup security](BACKUP-SECURITY.md) before enabling downloads or moving the
volume.

## What the drill proves

- the dump is readable by `pg_restore`;
- the schema and table data restore;
- the compared tables have the same row counts at the backup point;
- the scratch database can be created and dropped without touching production.

It does **not** prove application-level correctness, external object storage,
WireGuard peer state, or the erasure ledger. Those are separate checks.

## Restore checklist before a production cutover

- [ ] Fresh backup and checksum.
- [ ] Immediate restore drill passes.
- [ ] Erasure ledger and platform `.env` copied off-host.
- [ ] Previous container images retained for rollback.
- [ ] Restore owner and maintenance window recorded.
- [ ] Post-restore sign-in, course, lab, and certificate smoke tests pass.
