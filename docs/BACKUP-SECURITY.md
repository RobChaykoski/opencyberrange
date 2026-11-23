# Backup security

Backups are a copy of the most sensitive data in the platform. This page states
what is stored, what protects it, and what residual risk is accepted.

## What is in a snapshot

- Argon2id password hashes and account metadata.
- Auth sessions and refresh-token state.
- Course, enrolment, completion, achievement, and activity records.
- Learner PII, including email addresses and optional profile fields.
- The erasure suppression ledger and, on the host path, the platform `.env`.

A snapshot is not less sensitive than the live database. Treat the backup volume
as a second database.

## Two backup paths

| Path | Format | Encryption | Purpose |
|---|---|---|---|
| Admin **Create snapshot** (`app/services/backups.py`) | Plain SQL in `/app/backups` (`backups_data` volume) | Host-volume encryption only | Same-host restore and admin download |
| `scripts/backup-production.sh` | Custom-format dump in `~/backups` plus ledger and env | Off-host copies are GPG-encrypted; plaintext is refused unless `BACKUP_ALLOW_PLAINTEXT=1` | Off-host retention and disaster recovery |

The local admin snapshot is deliberately plaintext so a same-host restore does
not depend on a key that may be lost with the host. That is acceptable only when
the host and the `backups_data` volume are encrypted at rest.

## Controls in place

- `backups_data` is mounted only into the backend container, not the frontend or
  a lab.
- The backup directory is forced to mode `700`; snapshots and ledgers are mode
  `600`.
- The download endpoint requires an administrator, a recent re-authentication,
  an export reason, and writes an audit event.
- Delete requires an administrator and a recent re-authentication.
- The host script writes mode `600`, validates the dump with `pg_restore`, and
  prunes only its own filename patterns.
- Off-host copies require `BACKUP_GPG_RECIPIENT`; a plaintext off-host copy
  requires the explicit `BACKUP_ALLOW_PLAINTEXT=1`.
- Admin snapshots are pruned after `OCR_BACKUP_RETENTION_DAYS` (default 30).
  Host snapshots default to 14 days.

## Decision: local plaintext, encrypted volume

The local admin snapshot stays plaintext. Encrypting it in the application would
create a key-recovery problem for the same-host restore path: a lost key turns a
recoverable host into an unrecoverable one. The required control is
**encryption at rest on the host**:

- Full-disk encryption, or a LUKS-backed volume for `/var/lib/docker` and the
  `backups_data` volume.
- Root-only access to the host and the Docker volumes.
- The backup directory is not exported over NFS/SMB except through the host
  script's GPG path.
- Off-host copies use GPG and a recipient key held outside the platform host.

If an institution cannot encrypt the host volume, it must either enable the
off-host GPG path and disable local admin snapshots, or accept the risk in
writing with an owner and an expiry.

## Threat model

| Threat | Control | Residual |
|---|---|---|
| Host disk or volume image is stolen | Host/volume encryption | A compromised root can read the plaintext snapshot |
| Admin account is compromised | Admin role, recent re-auth, export reason, audit | A compromised admin can download until the account is disabled |
| Backup is copied to an unencrypted share | Off-host path requires GPG; local path stays on the host | A root operator can copy it manually; that is an insider risk |
| Backup is restored over production | Restore requires re-auth, validation, and a pre-restore safety snapshot | A privileged operator can still make a destructive mistake |
| Backup is stale or unreadable | Retention, last-backup check, restore drill | A backup that is never drilled is not proven recoverable |

## Required before production

- [ ] The host and the `backups_data` volume are encrypted at rest.
- [ ] `backups_data` is chowned to backend UID `10001` and mode `700`.
- [ ] A fresh admin snapshot and an immediate restore drill pass.
- [ ] The off-host GPG path is configured and the recipient key is held
      off-host.
- [ ] The admin download and delete paths require recent re-authentication.
- [ ] Retention matches the institution's data-retention policy.
- [ ] The backup owner and the restore owner are named.

## If a backup is exposed

1. Treat every credential, session, and learner record in the snapshot as
   disclosed.
2. Revoke sessions and refresh tokens; rotate database and service credentials.
3. Rotate the backup GPG recipient and re-encrypt the retained set.
4. Preserve the audit trail and the backup access logs.
5. Notify the privacy office and follow the institutional incident process.

## Related

- [Backup and restore testing](BACKUP-RESTORE-TEST.md)
- [Retention policies](RETENTION-POLICIES.md)
- [Deployment runbook](DEPLOYMENT-RUNBOOK.md)
- `scripts/backup-production.sh`
- `platform/backend/app/services/backups.py`
