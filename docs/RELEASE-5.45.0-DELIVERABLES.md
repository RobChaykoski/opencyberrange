# Release 5.45.0 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.45.0` |
| Signed tag | `v5.45.0` |
| Release commit | Pending tag |
| Alembic | `0065_legacy_kali_columns` |
| Production | Pending |
| Development | Pending |
| Supply-chain lock | Refreshed and signed with the release key |

## Schema alignment

| Deliverable | Detail |
|---|---|
| Model `id` cleanup | Removed 24 redundant `id` index declarations; migration 0061 already dropped the database indexes |
| Missing FK indexes | Migration `0063_missing_fk_indexes` adds 10 model-declared FK indexes |
| WebSocket tickets | `WebSocketTicket` model and migration `0064_ws_tickets`; startup DDL removed |
| Legacy Kali columns | Migration `0065_legacy_kali_columns` drops six unused columns; downgrade restores their types |
| Descending indexes | `awarded_at`, `started_at`, and `completed_at` expressions now declare `DESC` to match the database |
| Drift inventory | Classified 93 production operations down to 48 on development |
| Host isolation | ADR 0007 records the `ocr-labd` host-agent recommendation and options |

Remaining drift after 0065:

- 18 runtime `institution_id` columns.
- 20 tenant `institution_id` indexes.
- 3 nullability changes.
- 7 runtime or legacy indexes.

These require the tenant-baseline migration and a schema-ownership decision; they
are documented in [Alembic drift inventory](ALEMBIC-DRIFT-INVENTORY.md).

## Verification

| Check | Result |
|---|---|
| Backend tests | `1,182 passed` |
| Frontend build and tests | Pending |
| Quality checks | Pending |
| Supply-chain lock | Pending |
| Development Alembic | `0065_legacy_kali_columns` |
| Development drift | 48 operations (down from 93) |
| Development Kali columns | `0` |
| Production `/api/version` | Pending |
| Production health | Pending |
| Production drift | Pending |
| Restore drill | Pending |
| Rollback images | Pending |

## Known limitations

- The Docker socket and privileged/helper containers remain host-root equivalent.
- The tenant `institution_id` columns/RLS and 7 runtime/legacy indexes still live
  outside the migration graph.
- RLS gaps remain on `users`, `auth_sessions`, `refresh_tokens`,
  `rbac_user_roles`, and `service_credentials`.
- The 25 legacy reviewed contracts and 190 pending contracts still need
  subject-matter sign-off.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] Migrations `0063`-`0065` applied on production.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Production drift re-checked.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill passed.
- [ ] Rollback images retained.
- [ ] Test suite and component regression test pass.
