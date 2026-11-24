# Alembic drift inventory

Snapshot history: **93 → 48 → 38 → 0** schema operations.

The first snapshot was taken against production 5.44.0. After the model cleanups,
migrations `0063`-`0066`, and the model-index/nullability alignment, development
and production report **0 operations**. The restore-drift gate now defaults to
`0`, so any new drift fails the check.

`app.services.tenant_rls.ensure_tenant_schema` still owns derivation triggers,
backfill derivations, and RLS policies. The columns and indexes it used to create
at startup are now owned by migration `0066_tenant_baseline`.

## Summary

| Category | Count | Status |
|---|---:|---|
| Runtime tenant DDL (`institution_id` columns, indexes) | 18 columns, 20 indexes | **Fixed:** model columns plus migration `0066_tenant_baseline` |
| Runtime auth table `ws_tickets` | 1 table, 1 index | **Fixed:** model + migration `0064_ws_tickets`; runtime DDL removed |
| Legacy Kali columns | 6 columns | **Fixed:** no code references; migration `0065_legacy_kali_columns` drops them |
| Model `id` index declarations | 24 indexes | **Fixed:** removed `index=True` from 24 model IDs; migration 0061 dropped the DB indexes |
| Missing FK indexes declared by models | 10 indexes | **Fixed:** migration `0063_missing_fk_indexes` adds them |
| Index expression drift | 3 indexes | **Fixed:** model indexes declare `DESC` |
| Runtime ledger indexes | 3 indexes | **Fixed:** declared in the `DataIntegrityLedger` model |
| Other legacy indexes | 4 indexes | **Fixed:** declared in the models; the one-active-session partial unique index is retained |
| Tenant nullability | 3 columns | **Fixed:** aligned to `NOT NULL DEFAULT 'default'` |

## Fixed in this pass

- Removed `index=True` from 24 `id = Column(Integer, primary_key=True, index=True)`
  declarations. The primary key already has a btree index, and migration 0061
  dropped the redundant database indexes.
- Added migration `0063_missing_fk_indexes` for the 10 model-declared FK indexes
  that restored databases never received.
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
- Added `institution_id` to the 18 models that lacked it and declared the two
  remaining readiness indexes.
- Added migration `0066_tenant_baseline`: idempotent column, default, `NOT NULL`,
  and index creation for the 20 tenant tables. It is a no-op where the runtime
  DDL already ran and it gives a fresh restore the same schema.
- Reviewed the data before the baseline: every row in the 20 tables had
  `institution_id = 'default'` with no nulls on development and production.

## Remaining

None for autogenerate drift.

Not covered by this inventory:

- RLS policy gaps on `users`, `auth_sessions`, `refresh_tokens`,
  `rbac_user_roles`, and `service_credentials`. Multi-tenant use remains
  deferred.
- Triggers and RLS policies remain runtime-managed by `tenant_rls` rather than
  migration-managed.

## Verification

```bash
# Guard (CI)
python scripts/check-alembic-safety.py

# Diagnostic only; must report zero
docker exec ocr-backend alembic -c alembic.ini check

# Restore-drift check (defaults to 0)
bash scripts/check-restore-drift.sh
```
