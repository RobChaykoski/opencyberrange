# Release 5.44.0 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.44.0` |
| Signed tag | `v5.44.0` |
| Release commit | Pending tag |
| Alembic | `0062_index_dedupe` |
| Production | Pending |
| Development | Pending |
| Supply-chain lock | Refreshed and signed with the release key |

## Shared login throttle

| Deliverable | Detail |
|---|---|
| Shared store | Per-(username, client IP) failure counters use the configured Valkey/Redis store |
| Fallback | Bounded in-process counters when the cache is unavailable |
| Window | 15 minutes; backoff starts at 5 failures and caps at 60 seconds |
| Privacy | Redis keys are SHA-256 hashes, not usernames or IPs |
| Verification | Unit tests for both paths; live development check against Valkey |

## Admin tenant isolation

| Deliverable | Detail |
|---|---|
| Pending accounts | Cross-tenant test proves another tenant's pending accounts are hidden |
| Locked accounts | Cross-tenant test proves another tenant's locked accounts are hidden |
| User details | Cross-tenant test proves another tenant's details return 404 |
| Activity log | Cross-tenant test proves another tenant's events are hidden |
| Existing coverage | User list, stats, courses, and role-promotion guards already covered |

## Alembic safety

| Deliverable | Detail |
|---|---|
| Guard | One linear head, no merge revisions, no autogenerate usage in workflows or scripts |
| CI | `python scripts/check-alembic-safety.py` runs in the quality job |
| Guide | [Alembic baseline and drift](ALEMBIC-BASELINE.md) documents the runtime tenant DDL and legacy-restore drift |
| Rule | Hand-write migrations until the baseline is reconciled |

## Verification

| Check | Result |
|---|---|
| Backend tests | `1,182 passed` |
| Frontend build and tests | Pending |
| Quality checks | Pending |
| Supply-chain lock | Pending |
| Development Valkey throttle | `record` 1-5, retry 1, clear 0 |
| Production `/api/version` | Pending |
| Production health | Pending |
| Alembic on production | Pending |
| Existing routes | Pending |
| SSO | Pending |
| Restore drill | Pending |
| Rollback images | Pending |

## Known limitations

- The Docker socket and privileged/helper containers remain host-root equivalent.
- RLS gaps remain on `users`, `auth_sessions`, `refresh_tokens`, `rbac_user_roles`, and `service_credentials`; single-host `default` tenant is not exposed.
- Alembic autogenerate remains blocked until the baseline is reconciled.
- The 25 legacy reviewed contracts and 190 pending contracts still need subject-matter sign-off.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Production Valkey throttle check passes.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill passed.
- [ ] Rollback images retained.
- [ ] Manual and API reference regenerated.
- [ ] Coverage audit passes structurally.
- [ ] Test suite and component regression test pass.
