# Database subsystem

The platform uses PostgreSQL 15 as its transactional system of record. The
database stores accounts, courses, labs, sessions, completions, evidence,
consent, security events, and audit history. It does not store lab images or
learner filesystem data.

## Service

| Item | Value |
|---|---|
| Container | `ocr-db` |
| Image | `postgres:15-alpine` |
| Port | 5432, internal only |
| Volume | `postgres_data` |
| Role separation | application, migrator, backup |
| Migrations | Alembic, `platform/backend/alembic/` |
| RLS | tenant isolation on protected tables |
| Integrity | append-only ledger and triggers |

## Folder map

| Page | Use it for |
|---|---|
| [Schema and ownership](schema-and-ownership.md) | domain table groups, RLS, ledger |
| [Migrations](migrations.md) | Alembic workflow and safety checks |
| [Fixtures](fixtures.md) | seed scripts and test data |
| [Backup and restore](backup-and-restore.md) | snapshots, restore drill, suppression ledger |

## Connect

```bash
cd platform
docker compose --env-file .env -f docker-compose.prod.yml exec db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

For a read-only inspection from the host:

```bash
docker exec -it ocr-db psql -U labuser -d labdb
```

Do not expose 5432 to a network. Do not use the application role for schema
changes.

## Roles

| Role | Use |
|---|---|
| application | runtime queries, constrained by RLS |
| migrator | `alembic upgrade`, DDL |
| backup | `pg_dump`, read-only enough for snapshots |
| admin | break-glass maintenance, not for the app |

`scripts/check_db_roles.py` verifies the role separation. The runtime role is
not a superuser, so RLS is effective.

## Health and integrity

```bash
docker exec -i ocr-backend python - < scripts/database_integrity.py --dimensions
docker exec -i ocr-backend python - < scripts/database_integrity.py --quality
docker exec -i ocr-backend python - < scripts/database_integrity.py --ledger
```

Expected: `PASS`, zero critical findings, and a continuous ledger chain.

## Related

- [Data dictionary](../../docs/DATA-DICTIONARY.md)
- [Database integrity](../../docs/DATABASE-INTEGRITY.md)
- [Database migrations](../../docs/DATABASE-MIGRATIONS.md)
- [Tenant isolation status](../../docs/TENANT-ISOLATION-STATUS.md)
- [Retention policies](../../docs/RETENTION-POLICIES.md)
