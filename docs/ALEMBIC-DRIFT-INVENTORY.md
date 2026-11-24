# Alembic drift inventory

Snapshot: `alembic check` against production 5.44.0 on 24 November 2026.
Sequences were excluded; 93 schema operations remained. After the model
cleanup, migration 0063, and migration 0064, development reports 57:
0 added indexes, 0 removed tables, 24 removed columns, 3 nullability changes,
3 changed index expressions, and 27 removed indexes.

This is a classification, not a migration. Do not autogenerate from it.

## Summary

| Category | Count | Action |
|---|---:|---|
| Runtime tenant DDL (`institution_id` columns, indexes, NULL changes) | ~21 columns/indexes, 3 nullability changes | Move into a dedicated tenant-baseline migration |
| Runtime auth table `ws_tickets` | 1 table, 1 index | **Fixed:** model + migration `0064_ws_tickets`; runtime DDL removed |
| Legacy Kali columns | 6 columns | Verify no code references, then drop in a dedicated migration |
| Model `id` index declarations | 24 indexes | **Fixed:** removed `index=True` from 24 model IDs; migration 0061 already dropped the DB indexes |
| Missing FK indexes declared by models | 10 indexes | **Fixed:** migration 0063 adds them |
| Index expression drift | 3 indexes | Align model and DB on ASC/DESC |
| Runtime ledger indexes | 3 indexes | Model does not declare them; keep as runtime DDL or migrate |
| Other legacy indexes | 4 indexes | Review before dropping |

## Fixed in this pass

- Removed `index=True` from 24 `id = Column(Integer, primary_key=True, index=True)`
  declarations. The primary key already has a btree index, and migration 0061
  dropped the redundant database indexes.
- Added migration `0063_missing_fk_indexes` for the 10 model-declared FK indexes
  that restored databases never received:
  `achievements(course_id, lab_id)`, `activity_events(actor_id)`,
  `competition_participants(user_id)`, `course_enrollments(user_id)`,
  `course_lab_assignments(lab_id)`, `flag_attempts(lab_id)`,
  `lab_completions(lab_id)`, `quiz_attempts(quiz_id)`, and
  `survey_responses(course_id)`.
- Added the `WebSocketTicket` model and migration `0064_ws_tickets`; the runtime
  `CREATE TABLE` was removed from startup.

## Remaining categories

### 1. Runtime tenant DDL

`app.services.tenant_rls.ensure_tenant_schema` adds `institution_id` columns,
derivation triggers, indexes, and RLS policies at startup. The model does not
declare every column, so `alembic check` proposes removing them.

Affected examples: `accommodation_events`, `activity_events`,
`course_cohort_members`, `course_completion_resets`, `course_feedback`,
`course_staff`, `exercise_pulse_surveys`, `exercise_quiz_attempts`,
`exercise_quiz_feedback`, `exercise_reactions`, `flag_attempts`, `lti_scores`,
`open_badge_credentials`, `practice_session_questions`, `quiz_attempts`,
`review_requests`, `survey_responses`, `user_accommodations`, and the
readiness/portfolio tables with nullability drift.

Action: create one hand-written tenant-baseline migration that adds the columns,
indexes, triggers, and RLS policies. Then remove the runtime DDL or reduce it to
an assertion that the migration ran.

### 2. WebSocket tickets

Fixed: the `WebSocketTicket` model and migration `0064_ws_tickets` own the
table, and the startup DDL is gone. Development no longer reports a removed
table or `ws_tickets` index.

### 3. Legacy Kali columns

`lab_sessions.kali_terminal_url`, `kali_container_id`, `kali_port`,
`kali_activity_heartbeat`, `kali_last_activity`, and
`labs.provides_kali_terminal` exist in the database but not the model.

Action: confirm no code or report reads them, take a backup, then drop them in a
dedicated migration. Do not combine the drop with a feature release.

### 4. Index expression drift

`ix_achievements_awarded_at`, `ix_lab_completions_lab_completed`, and
`ix_lab_sessions_started_at` are descending in the database and ascending in the
model.

Action: decide whether recent-first queries need DESC. If so, declare
`column.desc()` in the model and add a migration that matches the database.
Otherwise recreate the indexes ascending.

### 5. Runtime and legacy indexes

The ledger indexes (`ix_data_integrity_ledger_entry`, `_occurred`, `_table`) are
created by `db_integrity.py`, not the model. `ix_genitem_lease`,
`ix_labsession_expires`, `uq_active_lab_session_user`, and `ix_revoked_at` are
legacy or runtime indexes the model does not declare.

Action: review each for an active query or invariant. Keep the one-active-session
guard unless a replacement constraint exists. Add the rest to the model or mark
them as runtime-managed in this inventory.

## Verification

```bash
# Guard (CI)
python scripts/check-alembic-safety.py

# Diagnostic only; do not pipe into a migration
docker exec ocr-backend alembic -c alembic.ini check

# Restore-drift check
bash scripts/restore-drill.sh
```

The production snapshot was taken before the model cleanup, migration 0063, and
migration 0064. Development after 0064 reports 57 operations (down from 93), with zero
`id`-index, missing-FK-index, or `ws_tickets` operations. Re-run against
production after the 5.45.0 deploy to confirm the same.
