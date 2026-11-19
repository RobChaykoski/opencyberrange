# Database schema and Alembic migrations

Audience: operators upgrading a deployment, and reviewers answering change-
management or disaster-recovery questions. Current schema head: **0040**
(`0040_settings_change_control`). Revisions 0034-0040 add the security event store,
RBAC tables, break-glass grants, portfolio share tokens,
`users.institution_id`, tenant columns/triggers/RLS on learner-data tables,
scoped service credentials, server-side sessions, rotating refresh tokens, MFA
lifecycle fields, password rehash stamps, the per-user security version that
invalidates stale tokens on authority changes, enrollment uniqueness, and
append-only consent evidence, and ticket-gated settings change control with
encrypted change evidence and a one-way production cutover record. The runtime
role must not be a superuser, or PostgreSQL RLS is bypassed.

## Short version for operators

- **Back up before every upgrade.** The upgrade script takes a timestamped
  database dump and a schema-only dump before it changes the tree.
- **Migrations run automatically when the backend starts.** You do not normally
  run `alembic upgrade head` by hand.
- **Do not run two different platform versions against one database.** Finish
  the upgrade and health check before starting another version.
- **There is no supported `alembic downgrade` path.** To roll back, restore the
  pre-upgrade database backup and redeploy the previous release.
- **A migration does not delete learner data.** Destructive data changes require
  an explicit operator action (retention purge or account erasure).

## Database identities

The platform uses separate PostgreSQL identities so the runtime role cannot
bypass tenant RLS and so schema work is auditable:

| Identity | Purpose | Key attributes |
|---|---|---|
| `ocr_migrator` | Owns schema objects; runs Alembic and inline startup DDL | `BYPASSRLS`, no `SUPERUSER`, no `CREATEDB` |
| `ocr_runtime` | Backend request traffic and background jobs | `NOBYPASSRLS`, no `SUPERUSER` |
| `ocr_reporting` | Cross-institution reporting | read-only, `BYPASSRLS` |
| `ocr_backup` | `pg_dump` and restore verification | read-only, `BYPASSRLS` |
| `ocr_audit` | Security, consent, and change-ledger review | read-only, selected tables, `BYPASSRLS` |

`DATABASE_URL` must use `ocr_runtime`; `MIGRATOR_DATABASE_URL` must use
`ocr_migrator`. Production refuses to start when the migrator URL is missing or
identical to the runtime URL, and it refuses to serve when the runtime role is a
superuser or has `BYPASSRLS`.

`BACKUP_DATABASE_URL` is optional and should use `ocr_backup` in production.
When it is unset, the admin **Create snapshot** action falls back to
`MIGRATOR_DATABASE_URL`, then to `DATABASE_URL`. It must not use the runtime
role when forced RLS is enabled: `pg_dump` fails on tables such as
`accommodation_events` because the runtime role cannot read every tenant row.

Create or refresh the roles after the first deployment of this release:

```bash
cd ~/opencyberrange/platform   # production
export OCR_DB_MIGRATOR_PASSWORD='...'
export OCR_DB_RUNTIME_PASSWORD='...'
export OCR_DB_REPORTING_PASSWORD='...'
export OCR_DB_BACKUP_PASSWORD='...'
export OCR_DB_AUDIT_PASSWORD='...'
bash ../scripts/bootstrap-db-roles.sh \
  -f docker-compose.prod.yml -f docker-compose.adopt.yml \
  -f docker-compose.override.yml
```

Development runs the same script from the repository root with no compose
flags. Store the passwords in the deployment `.env`; the bootstrap script reads
them from the environment and never writes them to the SQL file. Set the
reporting, backup, and audit URLs in the operator's backup/reporting tooling, not
in the backend container.

The bootstrap SQL is idempotent and can be re-run after an upgrade. It moves
existing tables, sequences, views, functions, and types to `ocr_migrator`, grants
runtime DML plus default privileges for future objects, and grants read access
to the reporting, backup, and audit roles.


## What happens at backend startup

The backend uses a hybrid schema step. The order is deliberate:

1. **Advisory lock.** `_initialize_schema()` takes PostgreSQL advisory lock
   `20261110` with a 30-second `lock_timeout`, so two workers or replicas cannot
   race on DDL. Non-PostgreSQL test databases skip the lock.
2. **`Base.metadata.create_all`.** Creates any table that does not exist. This
   is safe on an empty database and adds new tables on an existing one; it does
   not alter existing columns.
3. **Inline compatibility migrations.** `app/main.py` runs idempotent
   `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` and similar statements for columns
   added since the baseline. These keep an older database usable even if it has
   never been stamped by Alembic.
4. **Alembic stamp or upgrade.** `_stamp_or_upgrade_alembic()` reads
   `alembic_version` under the same advisory lock:
   - no row → `alembic stamp head` (adopt the current schema as the baseline);
   - a row → `alembic upgrade head`.
5. **Startup continues.** A failure in step 4 is logged and does not abort
   startup, because step 3 has already made the schema current for this release.
   Check the logs after an upgrade; a warning there is a reason to investigate.

Why hybrid: the project supports old single-host installs that predate Alembic,
and it must also support fresh databases. `create_all` plus inline ALTERs keeps
those installs working; Alembic then records the revision for future migrations.
This is documented rather than hidden because it changes the normal Alembic
contract: **the inline step, not Alembic alone, is the schema source of truth
for this release.**

## Checking the schema version

```bash
docker exec ocr-db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -c "SELECT version_num FROM alembic_version;"
```

Expected after this release: `0039_db_invariants`.

The upgrade verification script also checks for schema drift and reports it.

## Operator rules

| Situation | Action |
|---|---|
| Normal upgrade | Run `scripts/upgrade-from-backup.sh`; it backs up, updates, rebuilds, and verifies |
| Backend restarts | No manual migration; startup is idempotent |
| Two API replicas | Both may start; the advisory lock serializes them |
| Migration warning in logs | Keep the service up, capture the log, check `alembic_version`, and open an issue |
| Need to roll back | Stop the stack, restore the pre-upgrade dump, redeploy the previous release |
| Fresh install | No manual step; startup creates and stamps the schema |
| Manual `stamp` | Only for recovery, with a backup and a written reason |

Do not run `alembic upgrade head` while the backend is serving traffic. The
startup path already does it under a lock; a second manual upgrade can race and
is not supported.

## Maintainer workflow for a new revision

1. Add the migration under `platform/backend/alembic/versions/` with a unique
   revision id and `down_revision` pointing at the current head.
2. Add the corresponding idempotent inline ALTER in `app/main.py` so an old
   install that has never been stamped still gets the column.
3. Test on a copy of a real database, not only an empty one.
4. Update this page if the head changes.
5. Run the backend suite with `TEST_DATABASE_URL` set to a scratch database.

## Compliance mapping

| Requirement | How this helps |
|---|---|
| Change management | Every schema change is a reviewed file with a revision id and a release note |
| Disaster recovery | The pre-upgrade dump and restore path are documented and exercised |
| Data minimisation / retention | Migrations add structure; they do not silently delete records |
| Auditability | `alembic_version`, startup logs, and the integrity ledger record what ran |
| Availability | The advisory lock prevents duplicate-DDL startup failures during rolling restarts |

## Limits

- The hybrid path is not a substitute for a formal migration audit. A reviewer
  should read the revision files for the release they deploy.
- The startup step is not zero-downtime for every migration. A long index build
  can delay readiness; the health check will fail until it finishes.
- A failed Alembic step is logged but non-fatal. That keeps an existing install
  online, but it also means the version table can lag the actual schema. Check
  the logs rather than assuming the revision always matches.
- Backups contain personal data and password hashes. Handle them as restricted
  data and apply the retention policy in
  `docs/PRIVACY-AND-DATA-DELETION.md`.
