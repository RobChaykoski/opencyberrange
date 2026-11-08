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
`course_feedback`, `survey_responses`, `platform_settings`.

The ledger stores row hashes, not row contents. It never stores a password hash,
a flag, a VPN key, or a free-text comment.

## Checksum manifest

`scripts/database_integrity.py` computes a SHA-256 checksum for each critical
table and a database fingerprint over the table checksums.

```bash
# Run inside the backend container
docker exec -w /app ocr-backend python /tmp/database_integrity.py --checksum
docker exec -w /app ocr-backend python /tmp/database_integrity.py --quality
docker exec -w /app ocr-backend python /tmp/database_integrity.py --ledger
```

Write a signed manifest with `DB_INTEGRITY_KEY` set:

```bash
DB_INTEGRITY_KEY=... python scripts/database_integrity.py \
  --write-manifest /secure/evidence/db-manifest.json
```

Verify a later snapshot:

```bash
DB_INTEGRITY_KEY=... python scripts/database_integrity.py \
  --verify /secure/evidence/db-manifest.json
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
| Production | 2.4.1 | **0 critical, 0 warning, 3 info** | 116 real completions without a session; 149 seeded labs without a creator; 2 hint placeholders (intentional) |

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

Production does not yet have the ledger because it is still on 2.4.1. The 2.5.1
deployment installs it.

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

## Runbook

1. **Before a release:** take a database backup, run `--quality`, record the
   fingerprint, and write a signed manifest.
2. **After deployment:** run `--quality` and `--ledger`; confirm the ledger is
   present and the chain is OK.
3. **On a mismatch:** stop, preserve the database and ledger, compare the
   fingerprint with the release manifest, review unattributed entries, and do
   not re-baseline until the cause is explained.
4. **On the first install of 2.5.1:** the ledger starts empty; the first
   application writes populate it. Existing data is covered by the checksum
   manifest.
