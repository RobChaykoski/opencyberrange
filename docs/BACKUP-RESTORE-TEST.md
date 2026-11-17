# Backup and restore testing

Backup creation is not evidence of recoverability. This page records both.

## Current evidence

| Item | Value |
|---|---|
| Pre-cutover backup | `~/backups/ocr-backup-20261116-181526.dump` |
| Post-cutover backup | `~/backups/ocr-backup-20261116-192307.dump` |
| 5.17.5 backup | `~/backups/ocr-backup-20261116-223835.dump` |
| Final backup (post-cleanup) | `~/backups/ocr-backup-20261117-012455.dump` |
| Restore drills | **PASSED** pre-cutover, post-cutover, post-5.17.5, and final |
| Final restored state | 47 users, 210 labs, 41 enrollments, 463 achievements |
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
