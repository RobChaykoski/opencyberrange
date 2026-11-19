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
| Restore drills | **PASSED** pre-cutover, post-cutover, post-5.17.5, final, 5.17.6, 5.17.7, 5.19.0, 5.20.0, 5.21.0, and 5.22.0 |
| Final restored state | 87 users (47 human + 40 stress-test), 2 courses, 210 labs, 41 enrollments, 124 completions, 463 achievements |
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
