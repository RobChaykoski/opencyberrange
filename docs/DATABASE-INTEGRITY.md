# Database integrity and change attribution

The platform has two complementary database controls:

1. **Signed table checksums** for a point-in-time fingerprint of critical data.
2. **An append-only PostgreSQL change ledger** that records application writes
   with actor attribution and flags manual or uninstrumented writes.

Neither control replaces backups, access control, or a restore drill. Together
they make silent data drift visible.

## What is covered

Critical tables:

`users`, `courses`, `course_enrollments`, `course_lab_assignments`, `labs`,
`levels`, `tracks`, `lab_completions`, `lab_sessions`, `achievements`,
`achievement_celebrations`, `exercise_quiz_attempts`, `exercise_quiz_feedback`,
`course_feedback`, `survey_responses`, `platform_settings`,
`data_integrity_reviews`.

The ledger stores row hashes, not row contents. It never stores a password hash,
a flag, a VPN key, or a free-text comment.

## Checksum manifest

`scripts/database_integrity.py` computes a SHA-256 checksum for each critical
table and a database fingerprint over the table checksums.

```bash
# Run inside the backend container, from the deployment checkout
docker exec -i ocr-backend python - --checksum < scripts/database_integrity.py
docker exec -i ocr-backend python - --quality  < scripts/database_integrity.py
docker exec -i ocr-backend python - --ledger   < scripts/database_integrity.py
```

Write a signed manifest with `DB_INTEGRITY_KEY` set:

```bash
set -a; . /etc/opencyberrange/integrity.env; set +a
docker exec -i -e DB_INTEGRITY_KEY ocr-backend python - \
  --write-manifest /tmp/db-manifest.json < scripts/database_integrity.py
docker cp ocr-backend:/tmp/db-manifest.json ./db-manifest.json
docker exec ocr-backend rm -f /tmp/db-manifest.json
```

Verify a later snapshot by copying the manifest into the container:

```bash
docker cp ./db-manifest.json ocr-backend:/tmp/db-manifest.json
docker exec -i -e DB_INTEGRITY_KEY ocr-backend python - \
  --verify /tmp/db-manifest.json < scripts/database_integrity.py
```

The manifest is point-in-time evidence. Store it outside the database, with the
release record. A manifest is only as trustworthy as the key and the storage
location; commit the fingerprint to the release notes, not the manifest alone.

## Append-only change ledger

`ensure_ledger()` creates:

- `data_integrity_ledger`, with `occurred_at`, `table_name`, `row_pk`,
  `operation`, `row_hash`, `actor_type`, `actor_id`, `request_id`, `prev_hash`,
  and `entry_hash`;
- one `AFTER INSERT OR UPDATE OR DELETE` trigger per critical table;
- an immutable trigger that rejects `UPDATE` and `DELETE` on the ledger;
- a `REVOKE UPDATE, DELETE` on the ledger.

Actor attribution:

| Actor type | Meaning |
|---|---|
| `user` | An authenticated application request. `actor_id` is the signed-in account. |
| `system` | An application job with no user (scheduler, startup, import). The engine sets `application_name=ocr-app`. |
| `unattributed` | A write that bypassed the application, such as manual `psql`, or an uninstrumented path. |

The ledger chain is:

```text
entry_hash = SHA-256(prev_hash || table_name || row_pk || operation ||
                     row_hash || actor_type || actor_id || request_id ||
                     occurred_at)
```

`prev_hash` links each entry to the previous one. A broken link, a changed
`entry_hash`, or a row changed without a ledger entry is a finding.

### Verify the ledger

```bash
docker exec -w /app ocr-backend python /tmp/database_integrity.py --ledger
```

The command reports the entry count, chain status, and a count of unattributed
writes by table and operation. It does not silently fail on an unattributed
write; the operator must review it.

### Resolving an unattributed write

An unattributed write is evidence that a change bypassed the application's actor
context. Common causes are:

- a manual `psql` session or database console;
- a maintenance, migration, or import script run outside the application;
- a backup restore or data transfer;
- a host-side tool or integration that writes directly to PostgreSQL.

Before accepting one, match its time to a deployment, migration, restore, or
maintenance window; check database and host access logs; and confirm the table
and operation are expected.

An administrator records the resolution from **Admin → System → Integrity**.
The review stores:

- the table and operation;
- the reviewer's username and the review timestamp;
- a decision: **Expected**, **Investigated**, or **Escalated**;
- a required note explaining what was checked.

Reviews are written to `data_integrity_reviews`, the admin audit log, and the
append-only ledger. The original ledger entries are never edited or deleted.
`data_integrity_reviews` has its own immutable trigger, so a review cannot be
quietly changed after the fact. If the write is not explained, choose
**Escalated** and follow the operator's security-incident process.

## Data-quality audit

`--quality` checks:

- foreign-key orphans across every table;
- duplicate unique keys for users, labs, enrollments, assignments, completions,
  achievements, celebrations, quiz feedback, course feedback, and settings;
- invalid role, difficulty, direction, and session-status values;
- nulls in critical fields;
- negative attempts, hints, or time;
- empty-flag completions that are **not** intentional hint placeholders;
- quiz scores outside 0–100 and `correct > total`;
- feedback ratings outside 1–5;
- course date inversions;
- active courses without assignments or enrollments;
- archived courses with enrollments;
- invalid JSON in lab, survey, and quiz fields;
- missing default settings;
- password hashes that are missing or not Argon2id/bcrypt.

It exits non-zero only on a critical finding. Warnings and info findings are
printed for review.

## Deleted users

The erasure path is designed so a deleted account does not break a dashboard:

- `course_enrollments`, `lab_completions`, `lab_sessions`, `achievements`,
  `achievement_celebrations`, `exercise_quiz_attempts`,
  `exercise_quiz_feedback`, and `survey_responses` cascade.
- `activity_events.actor_id`, `course_feedback.subject_user_id`,
  `labs.created_by`, `surveys.created_by`, and `competitions.created_by` are set
  to `NULL`.
- `courses.instructor_id` is not nullable; erasure is blocked until owned
  courses are transferred.
- Instructor coaching notes with a `NULL` subject are excluded from the course
  health counts.
- Dashboards render `Deleted user`, `Deleted learner`, or
  `Deleted participant` instead of a blank or a crash.

The quality audit reports orphaned coaching notes and `NULL` creators so the
operator can review them.

## Password storage

- New and changed passwords are hashed with **Argon2id**.
- Legacy bcrypt hashes verify and are upgraded to Argon2id on a successful
  sign-in.
- The database stores a one-way hash only. There is no plaintext password, no
  reversible password encryption, and no password recovery.
- A password reset writes a new hash; it does not reveal the old password.
- The audit flags any `users.hashed_password` value that is missing or not an
  Argon2id/bcrypt hash.
- The administrative user export carries one-way hashes for controlled
  migration. Treat that file as credential material; it contains no plaintext
  password, MFA secret, recovery code, or VPN key.

## Evidence — 8 November 2026

| Environment | Release | Quality result | Notes |
|---|---|---|---|
| Development | 2.5.1 | **0 critical, 0 warning, 2 info** | 36 real completions without a session; 149 seeded labs without a creator |
| Production | 2.5.1 | **0 critical, 0 warning, 3 info** | 116 real completions without a session; 149 seeded labs without a creator; 2 hint placeholders (intentional) |

Development database fingerprint:

```text
ea4f9acb1cd8fa17f28c66841dba7620abcac76f099862c810bbf60cdc3c4c9c
```

Ledger check on development:

- 1 authenticated `user` entry (celebration removal);
- 1 `unattributed` `labs.UPDATE` entry from a deliberate no-op manual SQL update;
- chain **OK**.

The manual update was detected. That is the intended behaviour: an application
write is attributed; a direct SQL write is visible and reviewable.

Production has the ledger installed from the 2.5.0 deployment. The 2.5.1 check
reported 0 entries and a valid chain; entries appear as critical-table writes
occur.

## Known gaps

- **Session coverage.** 36 dev and 116 production completions have no matching
  non-diagnostic session. Completion, hint, attempt, and time signals are
  reliable; `started_rate` is not. The application creates sessions on launch;
  historical rows need a reviewed backfill or an explicit label.
- **Placeholder completions.** A hint request may create a `lab_completions` row
  with an empty flag and a start timestamp. It is intentional and is excluded
  from completion metrics. The audit labels it as info.
- **No creator on seeded labs.** All 149 seeded labs have `created_by = NULL`.
  This is expected for imported content, not a deleted account.
- **Superuser can disable triggers.** A database superuser can drop the ledger
  triggers. The control is tamper-evident, not tamper-proof. Keep the ledger
  backup and the signed manifest off the database host.
- **`application_name` is not a security boundary.** A manual client can set it
  to `ocr-app`. The actor context is the stronger signal; review unattributed
  writes, not just the label.

## Scheduled verification

The repository ships a host-side wrapper and systemd units:

- `scripts/db-integrity-check.sh` runs quality, ledger, and checksum checks and
  writes JSON evidence under `/var/lib/ocr-integrity` by default.
- `deploy/systemd/ocr-db-integrity.service` and `.timer` run it daily at
  02:30 UTC with a randomized delay.
- `deploy/systemd/ocr-db-integrity-alert@.service` records a failed run; point
  it at your monitoring webhook if you have one.

Install steps and overrides are in
[`../deploy/systemd/README.md`](../deploy/systemd/README.md). The wrapper keeps a
single-run lock, skips a missing `DB_INTEGRITY_KEY` for the weekly manifest, and
prunes evidence older than 90 days.

## Admin portal status

**Admin → System → Integrity** shows a live, read-only ledger summary:

- ledger installed and number of entries;
- last recorded write;
- unattributed and unreviewed writes in the last seven days, grouped by table
  and operation;
- the reviewer, decision, and note for any reviewed write;
- number of covered critical tables;
- the status check timestamp.

An administrator can record a review for each unattributed table/operation. The
form requires a decision and a note, and the action is written to the admin audit
log and the append-only ledger. The portal deliberately does not run the full
chain or quality audit in a web request. Those run from the host schedule, and
the signed manifests and JSON output are kept outside the database. The existing
**System → Health** area also shows a one-line **Data integrity** item with an
**Open Integrity** action.

## Runbook

1. **Before a release:** take a database backup, run `--quality`, record the
   fingerprint, and write a signed manifest.
2. **After deployment:** run `--quality` and `--ledger`; confirm the ledger is
   present and the chain is OK. Check **Admin → System → Integrity** for the
   live ledger summary.
3. **On a mismatch:** stop, preserve the database and ledger, compare the
   fingerprint with the release manifest, review unattributed entries, and do
   not re-baseline until the cause is explained.
4. **On the first install of 2.5.1:** the ledger starts empty; the first
   application writes populate it. Existing data is covered by the checksum
   manifest.
