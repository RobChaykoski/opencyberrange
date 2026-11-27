# Backup and restore

## What to back up

A complete restore set is:

1. PostgreSQL dump or physical snapshot.
2. `workbook_data` — Exercise Studio state and the erasure/suppression ledger.
3. `platform/.env` — secrets and endpoints.
4. `platform/certs` — TLS certificate and key.
5. The signed release tag and image digests.

The database alone is not a complete restore set.

## Snapshot mechanism

| Item | Default |
|---|---|
| Snapshot store | `backups_data` |
| Retention | 30 days (`OCR_BACKUP_RETENTION_DAYS`) |
| Backup role | dedicated `BACKUP_DATABASE_URL` |
| Integrity | manifest and checksum |
| Restore test | required after a volume, host, or major-version change |

The admin UI can request a backup and list snapshots. The backup service is in
`platform/backend/app/services/backups.py` and `backup_sql.py`.

## Restore drill

1. Provision a disposable host or database.
2. Restore the database snapshot.
3. Restore `workbook_data`, especially the suppression ledger.
4. Restore `platform/.env` and certificates.
5. Start the platform with the same release tag.
6. Run `database_integrity.py --dimensions`, `--quality`, and `--ledger`.
7. Sign in as an administrator and confirm the catalogue and a sample course.
8. Re-apply the suppression ledger: `enforce_suppressions`.
9. Confirm a revoked learner's derived data does not reappear.
10. Record the result in `docs/BACKUP-RESTORE-TEST.md`.

## Do not

- Do not restore only PostgreSQL and declare success.
- Do not restore a database over a live one.
- Do not skip the consent suppression step.
- Do not use `docker compose down -v` on a host with data.
- Do not prune prebuilt lab images.

## Commands

```bash
# Example: logical dump inside the db container
docker exec -t ocr-db pg_dump -U labuser -d labdb -Fc > labdb.dump

# Inspect the backup volume
docker run --rm -v platform_backups_data:/backups alpine ls -lh /backups
```

Use the supported backup service for a real deployment; the commands above are
for inspection and drills.

## Tests

```bash
cd platform/backend
python -m pytest tests/test_backups.py tests/test_backup_sql.py \
  tests/test_purge_erased_accounts.py -q
```

## Related

- [Backup and restore testing](../../docs/BACKUP-RESTORE-TEST.md)
- [Backup security](../../docs/BACKUP-SECURITY.md)
- [Retention policies](../../docs/RETENTION-POLICIES.md)
- [Privacy and data deletion](../../docs/PRIVACY-AND-DATA-DELETION.md)
