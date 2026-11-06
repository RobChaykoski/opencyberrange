# Migrating Users from Another Installation

Use the user transfer utility to move accounts from an earlier SWOCTS Cyber Range
or OpenCyberRange installation into this updated build. The utility exports usernames, email
addresses, password hashes, roles, approval state, profile names, and the other
portable account fields.

It does **not** export plaintext passwords, MFA secrets, recovery codes,
trusted devices, VPN peer keys, lab sessions, or completion history.

!!! danger "The export file is sensitive"
    The JSON file contains password hashes and personal data. Transfer it over a
    secure channel, keep it readable only by you, and delete it after the import
    succeeds. Do not attach it to a ticket or commit it to the repository.

## Prerequisites

- Admin access to the old installation and this one.
- Both backend containers running.
- A backup of the target database before importing.

The utility is `scripts/user_transfer.py`. It uses `psycopg2`, which is already
installed in the backend image.

## Migrate from the admin interface

The same portable export is available in the web interface:

1. On the old installation, open **Admin → Users** and expand **Import / Export Users**.
2. Leave **Include profile avatars** off unless you need them. Enter a short
   **Reason for export** (for example, "migrating accounts to the new server"),
   then click **Download users JSON**. The reason is written to the audit log.
   Treat the downloaded file as sensitive.
3. On the new installation, open the same panel, choose the JSON file, and
   click **Preview** to see what would change.
4. Click **Import** when the preview looks right. Enable **Update existing
   usernames** only when you intend to overwrite matching accounts.

The preview and import report counts for created, updated, skipped, and errored
rows, plus any username, email, or student-ID conflicts. Existing administrator
accounts are never overwritten by an import, including the administrator
performing it; those rows are skipped with a warning.

To restore a complete snapshot from another installation, open **Admin → System
→ Backups**, expand **Restore from another system**, upload a plain `.sql`
snapshot, and choose whether to restore it immediately. A full snapshot restore
replaces every account and record, so it is intended for same-version recovery,
not for moving users between versions. Use the user export for that.

## 1. Export from the old installation

Run these commands from the old repository root. The default backend service
name in this project is `backend`; use the service name or container name that
matches the old deployment.

```bash
docker compose cp scripts/user_transfer.py backend:/tmp/user_transfer.py
docker compose exec -T backend python /tmp/user_transfer.py export -o /tmp/users-export.json
docker compose cp backend:/tmp/users-export.json ./users-export.json
```

If the old installation does not have `scripts/user_transfer.py`, copy the file
from this repository to the old server first.

**What you should see:** a count such as `exported 87 user(s)` and a warning
that the file contains password hashes.

## 2. Import into the new installation

Run these commands from this repository root. Transfer `users-export.json` to
the new server first.

```bash
docker compose cp users-export.json backend:/tmp/users-export.json
docker compose exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json --dry-run
```

Review the dry-run counts and warnings. Then run the real import:

```bash
docker compose exec -T backend python /tmp/user_transfer.py import /tmp/users-export.json
```

**What you should see:** counts for created, updated, skipped, and errored
accounts. By default, an account that already exists in the target is skipped.

## Updating existing accounts

Use `--update` when the target already has the same usernames and you want the
exported profile names, roles, approval state, and password hashes to replace
the target values:

```bash
docker compose exec -T backend python /tmp/user_transfer.py import \
  /tmp/users-export.json --update
```

`--update` matches by username. If an email address belongs to a different
username in the target, the row is skipped and reported instead of overwriting
the other account.

## What is preserved

| Field | Imported |
|-------|----------|
| Username, email, student ID | Yes |
| First name, last name, organisation | Yes |
| Password hash | Yes — users keep their existing password |
| Role and admin flag | Yes |
| Active, approved, locked state | Yes |
| Failed attempts and lock timestamp | Yes |
| Registration date | Yes for new accounts |
| Scoreboard visibility and notification preferences | Yes |
| Avatar | Only with `--include-avatars` |

If the old schema has no `role` column, the exporter derives `admin` from
`is_admin` and otherwise uses `student`.

## What is not migrated

- MFA/TOTP enrollment and recovery codes — users must re-enroll.
- Trusted devices and active sessions.
- WireGuard VPN peers and configs — users download a new config.
- Course enrollments, completions, achievements, and lab history.

Those records are tied to the old installation's database and, for VPN, to the
old server's keys. Migrating them requires a separate database-level decision.

## Verify the import

1. Confirm the count in the Admin **Users** table matches the export.
2. Sign in with a migrated student account.
3. Sign in with a migrated instructor or admin account and confirm the role is
   correct.
4. If a migrated account was locked in the old installation, unlock it from the
   Admin panel after confirming the user is legitimate.
5. Ask affected users to re-enroll MFA and download a new VPN config.

## Troubleshooting

| Symptom | Meaning |
|---------|---------|
| `email ... already belongs to ...` | Another target account owns that email. Resolve the conflict first. |
| `student_id ... already belongs to ...` | Another target account owns that student ID. Resolve it or clear the exported value. |
| User created but cannot sign in | Check the account is approved and active; verify the old hash is bcrypt. |
| Role is wrong | The old schema may have had no `role`; set it from the Admin panel. |
| MFA does not work | MFA is intentionally not migrated; re-enroll the user. |

## Clean up

Delete the export file from both servers and from your workstation:

```bash
rm -f users-export.json
docker compose exec -T backend rm -f /tmp/users-export.json
```

Do not leave the file in a shared downloads directory.
