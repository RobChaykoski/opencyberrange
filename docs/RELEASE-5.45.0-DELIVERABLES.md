# Release 5.45.0 deliverables

Status: **released and deployed** to development and production on 24 November
2026.

| Item | Value |
|---|---|
| Version | `5.45.0` |
| Signed tag | `v5.45.0` |
| Release commit | `a50305fb` |
| Alembic | `0065_legacy_kali_columns` |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a passed restore drill |

## Schema alignment

| Deliverable | Detail |
|---|---|
| Model `id` cleanup | Removed 24 redundant `id` index declarations; migration 0061 already dropped the database indexes |
| Missing FK indexes | Migration `0063_missing_fk_indexes` adds 10 model-declared FK indexes |
| WebSocket tickets | `WebSocketTicket` model and migration `0064_ws_tickets`; startup DDL removed |
| Legacy Kali columns | Migration `0065_legacy_kali_columns` drops six unused columns; downgrade restores their types |
| Descending indexes | `awarded_at`, `started_at`, and `completed_at` expressions now declare `DESC` to match the database |
| Drift inventory | Classified 93 production operations down to 48 on development and production |
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
| Frontend build and tests | Build passed; `35` component tests passed |
| Quality checks | Green |
| Supply-chain lock | Verified with the release key |
| Development Alembic | `0065_legacy_kali_columns` |
| Production Alembic | `0065_legacy_kali_columns` |
| Development drift | 48 operations (down from 93) |
| Production drift | 48 operations (down from 93) |
| Legacy Kali columns | `0` on production |
| Missing FK indexes | `10` present on production |
| Production `/api/version` | `5.45.0` |
| Production health | `200` |
| Existing routes | `/contract-review`, `/my-evidence`, `/evidence-review`, `/journey`, `/impact`, `/practice` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-181940.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-182316.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.45.0`, `ocr-frontend:pre-v5.45.0` |
| Restore drill | `69` users, `215` labs, `2` courses, `64` enrollments, `134` completions, `497` achievements, `1,575` activity events |

## Known limitations

- The Docker socket and privileged/helper containers remain host-root equivalent.
- The tenant `institution_id` columns/RLS and 7 runtime/legacy indexes still live
  outside the migration graph.
- RLS gaps remain on `users`, `auth_sessions`, `refresh_tokens`,
  `rbac_user_roles`, and `service_credentials`.
- The 25 legacy reviewed contracts and 190 pending contracts still need
  subject-matter sign-off.

## Acceptance checklist

- [x] Signed tag and verified supply-chain lock.
- [x] Migrations `0063`-`0065` applied on production.
- [x] Production health, version, SSO, and public routes verified.
- [x] Production drift re-checked at 48 operations.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill passed.
- [x] Rollback images retained.
- [x] Test suite and component regression test pass.
