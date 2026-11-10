# SWOCTS Cyber Range: Privacy, Erasure, and Backups

SWOCTS Cyber Range is powered by OpenCyberRange. This document covers the branded deployment and the platform code it runs.

This document describes the platform's technical controls for the GDPR right
to erasure (Article 17), the right of access/portability (Articles 15 and 20),
and the backup/restore behaviour that makes erasure durable. It is an
engineering reference, not legal advice. A privacy notice, records of
processing, and a retention schedule still need review by counsel or a DPO.

The user-facing PIPEDA-aligned notice is
[PRIVACY-NOTICE.md](PRIVACY-NOTICE.md). Privacy questions and requests go to
[privacy@swocts.com](mailto:privacy@swocts.com).

## What data exists

| Category | Storage | On erasure |
|---|---|---|
| Identity: username, email, name, student ID, organisation, avatar | `users` | Deleted |
| Credentials and security: password hash, TOTP secret, recovery codes, trusted devices, last-login IP | `users` | Deleted |
| VPN: private/public keys and client IP | `wireguard_configs` | Deleted and peer removed |
| Learning: enrolments, completions, flag attempts, quiz attempts, achievements, competition entries, completion resets | User-linked tables | Deleted |
| Lab sessions and containers | `lab_sessions` + Docker | All sessions destroyed and rows deleted |
| Survey consent state and history | `users.survey_*`, `survey_consent_events` | Deleted (cascades with the account) |
| Privacy preferences: under-18 reporting flag, public certificate verification | `users.is_minor`, `users.certificates_public` | Deleted with the account |
| Report manifests: report ID, filename, SHA-256, HMAC signature, type, course, generator | `report_exports` | Deleted when the course is deleted; a deleted generator is set to `NULL` |
| Integrity reviews: reviewer username snapshot, decision, note, timestamp | `data_integrity_reviews` | Retained as security evidence; not linked by foreign key, so deleting a reviewer does not rewrite the review |
| WebSocket tickets | `ws_tickets` | Deleted |
| Activity feed | `activity_events` | Anonymised: actor, target, label, detail and IP removed |
| Invite addresses | `invite_codes.email` | Scrubbed |
| Courses owned by an instructor | `courses` | **Not deleted**; erasure is blocked until they are transferred |
| Authored labs/templates | `labs.created_by`, `exercise_templates.created_by` | Kept; author link nulled |
| Security audit stream | container logs | Retained for a short, documented period; new erasure entries do not include the erased identifier |
| Backups | `database.dump`, `users-export.json`, `erasure-ledger.jsonl` | Rotated on a 30-day default; restores re-apply the live ledger |

Downloaded certificate or transcript PDFs are generated on demand and are not
stored by the platform. Once a user downloads one, the platform cannot revoke
that copy.

## Reporting privacy

Two account settings limit where a learner's information can appear:

- **Under-18 reporting privacy** (`users.is_minor`). When enabled, the learner's
  individual activity is excluded from instructor reports, course analytics,
  coaching queues, public leaderboards, celebration walls, and competition
  scoreboards. Their own dashboard and progress remain available. The setting is
  a privacy declaration, not age verification.
- **Public certificate verification** (`users.certificates_public`). When
  disabled, the public verification page returns the same generic invalid result
  as an unknown certificate, and the certificate payload omits the verification
  URL and QR code. The learner's own certificate and PDF still work.

Both settings are controlled from **Profile → Security & privacy**. Reports also
exclude under-18 learners by default; an instructor cannot override that from
the report page. The report manifest records the report ID, file checksum, and
server signature, not learner data.

## User-initiated erasure

Profile → **Privacy and data** → **Delete my account**.

The request requires:

1. the current password;
2. a live TOTP code or an unused recovery code when MFA is enabled; and
3. typing `DELETE`.

Deletion is immediate and irreversible. The UI offers a JSON data export
first. Students are deleted straight away. An instructor who owns courses
receives a `409 owned_courses` response listing the courses; an administrator
must transfer each course in **Admin → Courses → Manage → Assigned
instructor** and then the instructor can delete the account. The last usable
administrator cannot delete themselves.

## Administrator-initiated erasure

**Admin → Users → Delete** requires typing the username. It applies the same
guards and the same erasure service as the self-service path. Rejecting a
pending account also uses it.

Deleting a course is a separate action and is never part of account erasure.
That distinction protects other students' enrolments, assignments, and
achievements.

## What is retained, and why

- **Anonymised activity events.** The event type and timestamp remain for
  security and operational history; the identity, label, detail and IP are
  removed.
- **Anonymised audit records.** Administrative audit lines keep the acting
  administrator, action and timestamp. New erasure audit entries deliberately
  omit the erased person's username.
- **Authored content.** Labs and templates survive with `created_by = NULL`;
  they are course material, not account data.
- **Suppression ledger.** A keyed hash of the erased username and email is kept
  so a restore cannot resurrect the account. This is a suppression list, not a
  profile.
- **Backups.** A backup taken before the deletion can still contain the
  account until it ages out of the retention window. Restores must re-apply the
  live suppression ledger (below). The default retention is 30 days.

The current retention defaults are: activity/audit review up to 90 days and
backups 30 days. Adjust these to match the institution's retention schedule.

## Data export

### Self-service subject access and portability

`GET /api/auth/export` returns a JSON document containing the account record,
VPN metadata, courses, completions, flag attempts, quiz attempts,
achievements, lab sessions, competition entries, and activity history.
Password hashes, TOTP secrets, recovery codes, trusted-device tokens, and the
WireGuard private key are excluded. The export updates `data_exported_at` and is
audited with the fixed purpose "Self-service subject access request". Profile →
**Privacy and data** offers the same export to the learner.

Downloaded certificate and transcript PDFs are generated on demand and are not
stored by the platform. The transcript download is audited with the purpose
"Self-service transcript request".

### Administrative user migration

Admin → Users → **Import / Export Users** moves accounts between installations.
The export contains the account and profile fields needed to recreate the user,
including the password hash so the learner keeps their existing password. It
does **not** contain MFA secrets or recovery codes, trusted devices, VPN peer
keys, lab sessions, course enrolment, completions, achievements, or other
learning progress.

Every administrative user export requires a reason of at least five characters.
The audit record stores the reason, the exporting administrator, the user count,
and whether avatars were included. The JSON file also embeds `reason` and
`exported_by`. Treat the file as credential material and delete it after the
import has been verified.

The importer supports a preview before writing. It consults the erasure
suppression ledger by default, so an erased account is not resurrected by an
older export. Existing administrator accounts are never overwritten: the
signed-in administrator is protected by user ID and other existing
administrators are skipped with a warning. Use the user panel for deliberate
administrator changes.

### Report, activity, and backup exports

Activity-log exports, database snapshot downloads, learning reports, course,
student, and assignment reports, and exercise/stress-test reports all require
an operator-supplied reason. The reason and exporter are written to the audit
log along with the format and scope. Export responses use
`Cache-Control: no-store`.

## Suppression ledger and backups

The ledger is an append-only JSONL file at `ERASURE_LEDGER_PATH`
(default `/workbook/erasure-ledger.jsonl`). It lives on the persistent
`/workbook` volume, outside PostgreSQL, so a `pg_restore` cannot overwrite it.
Each line contains a timestamp, the actor type, and HMAC-SHA256 hashes of the
normalised username and email. Set `ERASURE_LEDGER_KEY` to a dedicated stable
key, or leave it empty to use `JWT_SECRET`. Changing the key invalidates old
entries.

### Restore procedure

A snapshot can be restored from **Admin → System → Backups**. The same screen
can upload a plain `.sql` snapshot from another installation through **Restore
from another system**. A full restore replaces every account and record,
including the administrator performing the restore, so take a local snapshot
first and be prepared to sign in with an account that exists in the restored
data. Use the portable user import for cross-version moves or when the local
administrators must be preserved.

A database dump can predate a deletion. After any full restore:

```bash
docker compose -f platform/docker-compose.prod.yml -f platform/docker-compose.override.yml \
  cp scripts/purge_erased_accounts.py backend:/tmp/purge_erased_accounts.py
docker compose ... exec -T backend python /tmp/purge_erased_accounts.py --dry-run
docker compose ... exec -T backend python /tmp/purge_erased_accounts.py
```

The purge utility reads the **live** ledger, finds matching accounts, and runs
the same erasure service. It does not touch Docker or WireGuard. It will refuse
to delete an instructor who still owns courses, and reports that account for
manual transfer.

### User export merge

The admin interface path is **Admin → Users → Import / Export Users**. Preview
the file first, then import. The importer consults the live ledger, skips erased
accounts, and refuses to overwrite existing administrators. The JSON export
requires an audited reason and contains password hashes, so handle it as
sensitive data.

The command-line equivalent is `scripts/user_transfer.py import`:

```bash
python /tmp/user_transfer.py import /tmp/users-export.json \
  --ledger /workbook/erasure-ledger.jsonl --dry-run
```

Use `--include-erased` only for a deliberate disaster-recovery restore; it
undoes erasure and should require a documented decision.

### Backup retention

`scripts/upgrade-from-backup.sh` copies the ledger into each backup and prunes
completed `ocr-*` backups older than 30 days after a successful upgrade. Use
`--backup-retention-days N` to change this or `0` to disable pruning. The
in-browser admin backup copies the ledger beside the dump as well.

Backups contain password hashes and personal data. Restrict access, encrypt
them at rest where possible, and delete them once the retention period ends.

## Operational checklist

- [ ] Publish a privacy notice and link it from registration and the footer.
- [ ] Record the lawful basis for each processing purpose (contract for the
      account, legitimate interest for security logs).
- [ ] Maintain a retention schedule for activity, audit, logs, and backups.
- [ ] Define the high-school/minor consent process (parental consent rules vary
      by member state).
- [ ] Keep `ERASURE_LEDGER_KEY` stable and backed up separately from the DB.
- [ ] Run a restore drill and confirm `purge_erased_accounts.py` works.
- [ ] Review export reasons in the audit log as part of the access review.
- [ ] Confirm imported accounts never overwrite the existing administrators.
- [ ] Store user exports and database snapshots as sensitive credential data.
- [ ] Review the 90-day audit and 30-day backup defaults with counsel.
- [ ] Document the breach-notification and data-subject-request procedures.
