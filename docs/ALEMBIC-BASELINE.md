# Alembic baseline and drift

## Rule

Hand-write Alembic migrations. Do **not** run
`alembic revision --autogenerate` against this schema until the baseline is
reconciled.

`alembic check` is a diagnostic report, not a release gate. CI runs
`scripts/check-alembic-safety.py`, which verifies a single linear head and
rejects autogenerate usage in workflows and scripts.

## Why the graph drifts

- `app.services.tenant_rls.ensure_tenant_schema` adds `institution_id` columns,
  derivation triggers, and RLS policies at application startup. Those changes are
  not represented in the migration chain.
- A database restored from an older dump can retain legacy columns, indexes, and
  defaults that the current models no longer declare. Examples include
  `labs.provides_kali_terminal` and the `lab_sessions.kali_*` columns.
- Some model defaults and index expressions differ from the migration text even
  when the data shape matches.

Autogenerate sees the live database as the source of truth and proposes dropping
anything the model does not declare. On this schema that is destructive.

## Reconciliation plan

1. Restore a current production dump into a scratch database.
2. Run `alembic check` and capture the full operation list.
3. Classify each item:
   - runtime tenant DDL that should move into migrations;
   - legacy columns/indexes to drop after a data and dependency review;
   - model-only default or index-expression differences.
4. Write one forward migration per category. Do not combine the cleanup with a
   feature release.
5. Add a restore-drift check: restore a dump, migrate to head, and compare the
   resulting schema with the model.
6. Only after the schema matches may a new table use autogenerate, and only with a
   reviewed diff.

## Current guard

```bash
python scripts/check-alembic-safety.py
```

It prints the single head, confirms the revision graph is linear, and scans
`.github/workflows` and `scripts/` for autogenerate usage.
