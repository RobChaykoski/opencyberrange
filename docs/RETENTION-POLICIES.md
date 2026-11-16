# Retention policies

The product supplies retention controls and safe defaults. The institution
remains responsible for its legal retention schedule, legal hold, and archival
media. This page records what the software actually does and where the operator
must act.

## Defaults

| Data | Default | Control | Behaviour |
|---|---|---|---|
| Database snapshots | 30 days | `OCR_BACKUP_RETENTION_DAYS` (`app/services/backups.py`) | Scheduled collector prunes older snapshots and their ledgers; set `0` to disable pruning |
| Security events | 365 days recommended | `security_event_retention_days` | The application role cannot delete events; an elevated operator archives and prunes |
| Portfolio share links | 30 days | `portfolio_share_lifetime_days` | Each link also has an absolute `expires_at`; learners can revoke immediately |
| Break-glass grants | 60 minutes maximum | `break_glass_max_minutes` | A grant never extends; use a new reviewed grant |
| Consent revocation proof | Durable | `consent_audits`, suppression ledger | Proof survives account erasure; it contains a keyed subject hash, not the deleted payload |
| Account data export timestamp | Kept with the account | `users.data_exported_at` | Shows when the learner last downloaded their data |
| Session and activity records | Institution policy | Course/lab tables | Use the retention and erasure tooling; see `docs/PRIVACY-AND-DATA-DELETION.md` |

## Security events

The security event store is append-only under PostgreSQL row-level security.
The runtime role cannot update or delete rows. Retention therefore has three
steps:

1. **Archive.** Export the window to the institution's immutable store (SIEM,
   object-lock bucket, or WORM archive).
2. **Dispose.** Use an elevated maintenance role, never the application role,
   to delete only rows older than the approved schedule.
3. **Record.** Write a disposition event before closing the archive window.

A legal hold always overrides the default. Do not prune a window under hold.

## Backups

Backups are encrypted by the deployment platform and are not a learner-facing
export. A restore must re-apply the consent suppression ledger; the platform
does this with `enforce_suppressions`. Backup retention is measured from the
snapshot creation time, not from the restore time.

## Shares and grants

`portfolio_share_tokens` stores only a SHA-256 token hash. Expiry and
revocation are checked on every read, and a live consent revocation disables
all existing links immediately. `break_glass_grants` rows are retained as
evidence; expiry changes status but does not delete the record. Post-use review
is required for enterprise deployments.

## Deletion and erasure

Account deletion and consent revocation use the consent workflow, not a manual
SQL delete. The suppression ledger is the restore-proof source of truth. See
`docs/CONSENT-REVOCATION.md` and `docs/PRIVACY-AND-DATA-DELETION.md`.

## Review checklist

- [ ] The institution has approved a schedule for each row above.
- [ ] `OCR_BACKUP_RETENTION_DAYS` matches the backup policy.
- [ ] Security events are archived before pruning.
- [ ] The runtime database role is not a superuser, so RLS is effective.
- [ ] Break-glass grants are reviewed within the incident SLA.
- [ ] Portfolio share links are revoked when an employer relationship ends.
- [ ] A restore test re-applies the suppression ledger.
