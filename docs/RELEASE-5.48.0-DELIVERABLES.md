# Release 5.48.0 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.48.0` |
| Signed tag | `v5.48.0` |
| Release commit | Pending tag |
| Alembic | `0066_tenant_baseline` |
| Production | Pending |
| Development | Pending (schema at `0066`, drift `0`) |
| Supply-chain lock | Refreshed and signed with the release key |

## Tenant baseline

| Deliverable | Detail |
|---|---|
| Migration | `0066_tenant_baseline`: idempotent `institution_id` column, default, `NOT NULL`, and index for 20 tables |
| Models | `institution_id` declared on the 18 models that lacked it; two readiness indexes added |
| Data review | Every row in the 20 tables is non-null and `institution_id = 'default'` on development and production |
| Drift | Development and production move from 38 operations to **0** |
| Restore-drift gate | Default tightened from 48 to 0 |
| Runtime DDL | Columns/indexes now migration-owned; triggers, derivations, and RLS stay in `tenant_rls` |
| Downgrade | Refuses to drop a tenant column that holds non-default data |

## Verification

| Check | Result |
|---|---|
| Backend tests | `1,196 passed` |
| Frontend tests | `38 passed` |
| Alembic safety guard | Single head `0066_tenant_baseline` |
| Development drift | `0` operations |
| Production drift | Pending |
| Restore-drift gate | Pending at baseline `0` |
| Production health | Pending |
| Rollback images | Pending |

## Known limitations

- RLS gaps remain on `users`, `auth_sessions`, `refresh_tokens`,
  `rbac_user_roles`, and `service_credentials`.
- Triggers and RLS policies remain runtime-managed; only columns and indexes are
  in the migration graph.
- Multi-tenant use stays deferred until the RLS gaps close.
- The 25 legacy and 190 pending contracts still need subject-matter sign-off.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] CI integrity gate passes on the release commit.
- [ ] Production migration reaches `0066_tenant_baseline`.
- [ ] Production drift is `0`.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill and restore-drift gate at `0` passed.
- [ ] Rollback images retained.
