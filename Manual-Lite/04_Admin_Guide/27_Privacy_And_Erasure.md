# Privacy, Erasure, and Backups

This page covers account erasure, the data export, and the backup/restore rules
that keep a deleted account from coming back.

!!! note "Not legal advice"
    These are the platform's technical controls. Have counsel or a DPO review
    the privacy notice, lawful basis, retention schedule, and the rules for
    learners under 18.

## Delete an account

**Admin → Users → Delete** requires typing the username. The same erasure
service runs when a student deletes their own account from
**Profile → Privacy and data**, and when a pending account is rejected.

### What is erased

- Profile, email, name, student ID, organisation, avatar
- Password hash, MFA secret, recovery codes, trusted devices, last-login IP
- VPN keys and client IP (the WireGuard peer is removed)
- Course enrolments, completions, flag attempts, quiz attempts, achievements,
  event entries, completion resets
- Lab sessions (all running containers are destroyed) and WebSocket tickets
- Activity identities: actor, target, label, detail, and IP are cleared

### What is kept

- Activity and audit events, anonymised, for security review
- Authored labs and templates, with `created_by` cleared
- A keyed suppression hash in the erasure ledger
- Backups until their retention period ends

## Deletion guards

| Guard | Why | Fix |
|---|---|---|
| Account owns courses | Deleting it would also delete every enrolled student's course records | Transfer each course in **Admin → Courses → Manage → Assigned instructor** |
| Last usable administrator | The platform would have no administrator | Promote or create another administrator |

## Data export

`GET /api/auth/export` returns the account's personal data as JSON. It includes
the account record, VPN metadata, courses, completions, flag attempts, quiz
attempts, achievements, sessions, events, and activity. Password hashes,
MFA secrets, recovery codes, trusted-device tokens, and the WireGuard private
key are excluded. The download is audited with the fixed purpose "Self-service
subject access request"; the transcript download records "Self-service
transcript request".

### Administrative user export and import

**Admin → Users → Import / Export Users** moves accounts between installations.
Enter a reason before exporting; the reason, exporter, user count, and avatar
setting are written to the audit log. The export includes password hashes so
users keep their passwords, but excludes MFA secrets, recovery codes, trusted
devices, VPN keys, sessions, and learning progress. Treat the file as a secret
and delete it after the import is verified.

The import screen previews the file before writing. It consults the live erasure
ledger, so an erased account is not resurrected. It also never overwrites an
existing administrator: the signed-in admin is protected by user ID and other
existing admins are skipped with a warning.

### Report and backup exports

Activity-log exports, snapshot downloads, learning reports, course and student
reports, and exercise/stress-test reports require a reason of at least five
characters. The reason and exporter are recorded in the audit log. Export
responses use `Cache-Control: no-store`.

## Backups and restores

The erasure ledger is an append-only file on the backend's persistent
`/workbook` volume. It stores keyed hashes, not usernames or emails. PostgreSQL
restores cannot overwrite it.

**Admin → System → Backups** can create and download snapshots, and **Restore
from another system** can upload a plain `.sql` snapshot from another
installation. A full restore replaces every account and record, including the
administrator performing the restore. Take a local snapshot first and be ready
to sign in with an account that exists in the restored data. For cross-version
moves or when local administrators must be preserved, use **Admin → Users →
Import / Export Users** instead.

`scripts/upgrade-from-backup.sh`:

- copies the ledger into each backup;
- skips erased accounts when merging `users-export.json`;
- prunes completed backups older than 30 days after a successful upgrade.

Change the retention with `--backup-retention-days N`, or `0` to keep every
backup.

### After a full restore

A dump can predate a deletion request. Re-apply the live ledger:

```bash
docker compose -f platform/docker-compose.prod.yml -f platform/docker-compose.override.yml \
  cp scripts/purge_erased_accounts.py backend:/tmp/purge_erased_accounts.py
docker compose -f platform/docker-compose.prod.yml -f platform/docker-compose.override.yml \
  exec -T backend python /tmp/purge_erased_accounts.py --dry-run
docker compose -f platform/docker-compose.prod.yml -f platform/docker-compose.override.yml \
  exec -T backend python /tmp/purge_erased_accounts.py
```

The utility refuses to delete an instructor who still owns courses and reports
the account for manual transfer.

### Merging an old user export

```bash
docker compose ... exec -T backend python /tmp/user_transfer.py import \
  /tmp/users-export.json --ledger /workbook/erasure-ledger.jsonl --dry-run
```

`--include-erased` bypasses the ledger and should only be used for a deliberate
disaster recovery.

## Operational checklist

- Keep `ERASURE_LEDGER_KEY` stable. If it is empty, `JWT_SECRET` is used.
- Back up the ledger separately from the database.
- Encrypt backups at rest and delete them when retention ends.
- Store user exports and snapshot downloads as sensitive credential data.
- Review export reasons in the audit log during access reviews.
- Confirm an import cannot overwrite the existing administrators.
- Run a restore drill and confirm the purge utility works.
- Review the 90-day audit and 30-day backup defaults with counsel.

See [Deleting Users](07_Deleting_Users.md) and
[Upgrade and Verify](../00_Server_Deployment/07_Upgrade_And_Verify.md) for the
operational steps.
