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

### Accepted informational findings (current tree)

The 8 November 2026 run above is retained as historical evidence. The current
tree (159 labs) carries the same informational classes, reviewed and accepted:

- **Session coverage gap.** Some completions have no matching non-diagnostic
  session. This is a known coverage gap, not data loss; completion, hint,
  attempt, and time signals remain reliable.
- **No creator on seeded labs.** Seeded and discovered labs have
  `created_by = NULL` by design; this is not a deleted account.
- **Production hint placeholders.** Two hint placeholders are intentional
  authoring placeholders, not missing content.

None is a broken reference, data-loss condition, or reason to block a release.
No backfill or reference repair is required.

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

## Ledger size and retention

The ledger is append-only, so size is a capacity plan, not a cleanup afterthought.
Measure it monthly:

```sql
select pg_size_pretty(pg_total_relation_size('data_integrity_ledger')) as total,
       count(*) as rows,
       min(occurred_at) as oldest,
       max(occurred_at) as newest
from data_integrity_ledger;
```

Also record rows per day and bytes per row:

```sql
select date_trunc('day', occurred_at) as day, count(*)
from data_integrity_ledger
group by 1 order by 1 desc limit 30;
```

### Thresholds

| Signal | Warning | Action |
|---|---|---|
| Rows | 5 million or 2 GB | Plan an archive or partition |
| Rows | 10 million or 5 GB, or >20% of the database | Archive in the next maintenance window |
| Growth | More than 2x the previous month | Find the write source before archiving |
| Oldest entry | Older than the retention window | Archive the oldest months |

The default retention window is **24 months**. Keep longer when an incident,
audit, or legal hold references the rows. Always keep the last 90 days.

### Archive procedure

The ledger's immutable trigger rejects `DELETE`, which is intentional. Archive
with a controlled maintenance procedure, not an ad-hoc query:

1. Take a database backup and a signed checksum manifest.
2. Export the rows to be removed:
   `pg_dump -t data_integrity_ledger --data-only --where="occurred_at < '...'"`.
3. Record the cutoff, the last retained `entry_hash`, and the archive file's
   SHA-256 in the release or operations record.
4. In a maintenance window, as the database owner, disable the immutable
   trigger on the ledger only, delete in batches, then re-enable it in the same
   transaction block.
5. Recompute the chain over the retained window and record the archive boundary
   as a documented chain start. A verifier must accept a recorded boundary, not
   silently re-baseline.
6. Run `VACUUM (ANALYZE) data_integrity_ledger` and re-check table size.
7. Never delete rows that are under review, within the last 90 days, or part of
   an open incident.

At more than 10 million rows, switch to a monthly **range partition** on
`occurred_at` and detach old partitions. That avoids `DELETE`, keeps the
immutable trigger on each partition, and makes retention a metadata operation.
The migration is a schema change: schedule it with a release, not during an
incident.

The signed daily manifests and the off-host checksum evidence are the long-term
record. The ledger is the working evidence window; it is not the archive.

### Archive tool

`scripts/archive-ledger.py` exports the ledger in date chunks and verifies them:

```bash
# Dry run: export and hash, no deletion
docker cp scripts/archive-ledger.py ocr-backend:/tmp/archive-ledger.py
docker exec -w /app -e PYTHONPATH=/app ocr-backend \
  python /tmp/archive-ledger.py --before 2024-01-01 --chunk-days 30

# Verify every chunk and the manifest signature
docker exec -w /app -e PYTHONPATH=/app ocr-backend \
  python /tmp/archive-ledger.py --verify /tmp/ledger-archive/ledger-archive-2024-01-01.json

# Delete after a reviewed archive
docker exec -w /app -e PYTHONPATH=/app ocr-backend \
  python /tmp/archive-ledger.py --before 2024-01-01 --apply --confirm-delete
```

The tool refuses to archive newer than `--keep-days` (default 90), records each
chunk's row range, count, first/last entry hash, and gzip SHA-256, and records
the new chain boundary. Set `DB_INTEGRITY_KEY` to sign the manifest. Verify the
chunks before deleting; a chunk that fails its hash or row count must be
re-exported.

### Update validation (quick)

Run this after every upgrade, before accepting the release:

```bash
docker cp scripts/database_integrity.py ocr-backend:/tmp/database_integrity.py
docker exec -w /app -e PYTHONPATH=/app ocr-backend \
  python /tmp/database_integrity.py --dimensions
```

It validates the change-table triggers, the ledger `prev_hash` chain (quick
link check), the curriculum dimensions (tracks, levels, labs, chapters,
courses), lab metadata completeness, and the unattributed ratio. It exits
non-zero on a missing trigger, a chain break, duplicate lab slugs, labs without
a level, or an invalid difficulty. `scripts/deploy-updates.sh` runs the same
check after the containers are healthy.

## When the data is way off

"Way off" is a measurable condition, not a feeling. Treat any of these as a
stop-the-line finding:

- the checksum fingerprint differs from the release manifest;
- the ledger chain is broken, or an `entry_hash` changed;
- the quality audit reports a **critical** finding;
- unattributed writes spike above the normal daily baseline, or above 20% of a
  day's writes;
- counts diverge from the expected shape (for example, completions exceed
  visible labs, or labs in the database do not match the repository);
- impossible values appear: negative attempts or time, scores outside 0-100,
  future timestamps, or a course with no owner.

Triage in this order:

1. **Preserve.** Take a database snapshot, copy the ledger range, and keep the
   backend and database logs for the window. Do not reset the ledger or the
   fingerprint.
2. **Bound the window.** Compare the first bad row or fingerprint time with
   deployments, migrations, restores, imports, and maintenance access.
3. **Classify.** Expected (a documented migration or restore), investigated
   (explained but worth a note), or escalated (unexplained). Record the decision
   in **Admin -> System -> Integrity**.
4. **Repair only with a reviewed script.** Prefer a targeted repair and a
   re-run of `--quality` and `--ledger`. Restore from backup only when data was
   lost; a restore also rolls back unrelated legitimate writes.
5. **Re-baseline last.** A new fingerprint or a new ledger chain start is a
   documented decision with a reviewer, a reason, and a date, never a silent
   reset.
6. **Communicate.** Record the affected tables, the time window, the decision,
   and the evidence location in the incident or release note.

If the cause is not explained, stop the release. A broken chain or a critical
quality finding is not a cosmetic warning.

## Metadata drag and missing information during upgrades

Metadata lags for four common reasons:

1. **New columns.** Alembic adds a column with a NULL default; old rows stay
   NULL until a backfill or the next write.
2. **Discovery does not delete.** `discover_labs.py` updates labs found under
   `/labs`; a lab removed from the repository remains in the database until an
   administrator marks it inactive.
3. **Version fields.** `content_version`, `competency_model_version`, and
   `lab_difficulty_snapshot` record the version at write time. Old rows keep the
   old version by design; that is provenance, not corruption.
4. **Chapter and workbook drift.** A renamed chapter or workbook path leaves old
   `chapter_id` or `workbook` values until the lab metadata is refreshed.

### Before an upgrade

- Take a backup and a signed checksum manifest.
- Run `--quality` and `--ledger`; save the output.
- Export the lab metadata you will compare afterwards:
  `select slug, content_version, chapter_id, workbook, mitre_attack, mapped_skills from labs order by slug;`
- Record the repository lab count and the database lab count.

### After an upgrade

1. Confirm `alembic current` is the expected head.
2. Run `discover_labs.py` to reconcile lab metadata from `lab.yaml`.
3. Run `--quality` and `--ledger`; compare with the pre-upgrade output.
4. Check the new columns for unexpected NULLs. NULL is acceptable when the value
   did not exist at write time (for example, an old completion has no
   competency snapshot); it is a finding when a current row should have it.
5. Compare the lab count: repository labs plus intentional demo or hidden rows
   should equal the database count. Mark removed labs inactive after review;
   do not delete rows that have completions.
6. Refresh `chapter_id` and `workbook` for renamed content with a reviewed
   update, not a blind mass update.
7. Re-run the checksum and write a new signed manifest.

### Backfill rules

- Back up first, and work on a copy when the change is large.
- Backfill one field and one reason at a time; record the SQL and the reviewer.
- Never invent a `competency_mapping` for an old completion. Leave it NULL and
  label the row as pre-versioned evidence; recompute only if the mapping is
  deterministic and the source data is intact.
- Do not mass-update `content_version` to hide drift. It is a provenance field.
- After a backfill, run `--quality` and `--ledger` again and record the new
  fingerprint.

### Field sources of truth

| Field | Source |
|---|---|
| Lab title, difficulty, time, tools, hints, flag | `platform/labs/<Track>/<lab>/lab.yaml` |
| Chapter and workbook | `curriculum-manifest.yaml` and the workbook tree |
| Competency snapshot | `competency-mapping.yaml` at completion time |
| Content version | The release that authored the lab |
| Course ownership | `courses.instructor_id` (never NULL) |

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
