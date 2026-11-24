# Alembic drift inventory

Snapshot: `alembic check` against production 5.44.0 on 24 November 2026.
Sequences were excluded; 93 schema operations remained. After the model cleanups, migrations 0063-0065, and the model-index/nullability alignment, development reports 38:
0 added indexes, 0 removed tables, 18 removed columns, 0 nullability changes,
0 changed index expressions, and 20 removed indexes.

This is a classification, not a migration. Do not autogenerate from it.

## Summary

| Category | Count | Action |
|---|---:|---|
| Runtime tenant DDL (`institution_id` columns, indexes) | 18 columns, 20 indexes | Move into a dedicated tenant-baseline migration |
| Runtime auth table `ws_tickets` | 1 table, 1 index | **Fixed:** model + migration `0064_ws_tickets`; runtime DDL removed |
| Legacy Kali columns | 6 columns | **Fixed:** no code references; migration `0065_legacy_kali_columns` drops them |
| Model `id` index declarations | 24 indexes | **Fixed:** removed `index=True` from 24 model IDs; migration 0061 already dropped the DB indexes |
| Missing FK indexes declared by models | 10 indexes | **Fixed:** migration 0063 adds them |
| Index expression drift | 3 indexes | **Fixed:** model indexes now declare `DESC` |
| Runtime ledger indexes | 3 indexes | **Fixed:** declared in the `DataIntegrityLedger` model |
| Other legacy indexes | 4 indexes | **Fixed:** declared in the models; the one-active-session partial unique index is retained |

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
- Dropped the six legacy Kali columns in migration `0065_legacy_kali_columns`; no
  application code referenced them.
- Declared `DESC` on the three recent-first indexes so the model matches the
  database.
- Declared the seven runtime/legacy indexes in the models: the three
  `data_integrity_ledger` indexes, `ix_genitem_lease`, `ix_labsession_expires`,
  `ix_revoked_at`, and the partial unique `uq_active_lab_session_user` guard.
- Aligned `portfolio_share_tokens`, `readiness_lab_reviews`, and
  `readiness_student_notes` to the database's `NOT NULL DEFAULT 'default'`
  `institution_id`.

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
`review_requests`, `survey_responses`, and `user_accommodations`.

Action: create one hand-written tenant-baseline migration that adds the columns,
indexes, triggers, and RLS policies. Then remove the runtime DDL or reduce it to
an assertion that the migration ran.

### 2. WebSocket tickets

Fixed: the `WebSocketTicket` model and migration `0064_ws_tickets` own the
table, and the startup DDL is gone. Development no longer reports a removed
table or `ws_tickets` index.

### 3. Legacy Kali columns

Fixed: `0065_legacy_kali_columns` drops the six columns. The repository had no
application, report, or frontend references. The deploy takes a pre-deploy
backup, and the downgrade restores the original types.

### 4. Index expression drift

Fixed: the model now declares `awarded_at DESC`, `started_at DESC`, and
`completed_at DESC`. The database already matched those expressions.

### 5. Runtime and legacy indexes

Fixed: the model now declares all seven. The three ledger indexes remain useful
for integrity queries. `ix_genitem_lease` supports the worker claim query,
`ix_labsession_expires` supports the reaper, and `ix_revoked_at` supports token
purge. `uq_active_lab_session_user` is a partial unique index over
`user_id` for `starting`/`running` sessions; it is the one-active-session guard
and stays in place.

## Verification

```bash
# Guard (CI)
python scripts/check-alembic-safety.py

# Diagnostic only; do not pipe into a migration
docker exec ocr-backend alembic -c alembic.ini check

# Restore-drift check
bash scripts/restore-drill.sh
```

Development and production both report 38 operations after 5.47.0: 18 runtime
tenant columns and 20 tenant indexes. The restore-drift gate now defaults to 38.
