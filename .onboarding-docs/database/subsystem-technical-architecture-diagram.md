# Database technical architecture

```mermaid
flowchart TB
    subgraph App["ocr-backend"]
        ORM["SQLAlchemy sessions<br/>app role"]
        MIG["Alembic<br/>migrator role"]
        BK["Backup service<br/>backup role"]
    end

    subgraph PG["PostgreSQL 15 (ocr-db)"]
        subgraph Domains["Domain tables"]
            Identity["users, auth_sessions, external_identities"]
            Learning["courses, enrollments, labs, sessions, completions"]
            Evidence["evidence_records, reviews, appeals, contracts"]
            Consent["consent_states, events, revocations, suppressions"]
            Security["security_events, RBAC, audit, break-glass"]
            Analytics["activity, snapshots, readiness, achievements"]
            Integrations["identity providers, LTI, settings"]
        end
        RLS["Row-level security<br/>tenant policy"]
        Ledger["data_integrity_ledger<br/>append-only hash chain"]
        Triggers["ocr_integrity_* triggers"]
        Migrations["alembic_version"]
    end

    subgraph Store["Host storage"]
        Vol[("postgres_data")]
        Backups[("backups_data")]
    end

    ORM --> RLS
    RLS --> Domains
    MIG --> Migrations
    MIG --> Domains
    BK --> Backups
    Domains --> Triggers --> Ledger
    PG --> Vol
```

## Request-to-row path

1. `get_current_user` sets the tenant context from the session.
2. SQLAlchemy opens a transaction with the application role.
3. PostgreSQL applies RLS for the tenant on protected tables.
4. The write fires an integrity trigger for instrumented tables.
5. The trigger writes a ledger entry with the previous hash and the entry hash.
6. Commit.

## Why the ledger exists

The ledger is tamper-evident evidence that a critical row changed. It records
the table, primary key, operation, row hash, actor, request id, and a hash chain.
`database_integrity.py --ledger` verifies the chain and reports unattributed
writes.

## Related

- [Schema and ownership](schema-and-ownership.md)
- [Migrations](migrations.md)
- [Backup and restore](backup-and-restore.md)
- [Database integrity](../../docs/DATABASE-INTEGRITY.md)
