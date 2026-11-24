# Release 5.44.0 deliverables

Status: **released and deployed** to development and production on 24 November
2026.

| Item | Value |
|---|---|
| Version | `5.44.0` |
| Signed tag | `v5.44.0` |
| Release commit | `47146529` |
| Alembic | `0062_index_dedupe` |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a passed restore drill |

## Shared login throttle

| Deliverable | Detail |
|---|---|
| Shared store | Per-(username, client IP) failure counters use the configured Valkey/Redis store |
| Fallback | Bounded in-process counters when the cache is unavailable |
| Window | 15 minutes; backoff starts at 5 failures and caps at 60 seconds |
| Privacy | Redis keys are SHA-256 hashes, not usernames or IPs |
| Verification | Unit tests for both paths; live production and development checks against Valkey |

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
| Frontend build and tests | Build passed; `35` component tests passed |
| Quality checks | Green |
| Supply-chain lock | Verified with the release key |
| Production login throttle | Valkey/Redis connected; record `1-5`, retry `1`, clear `0` |
| Production `/api/version` | `5.44.0` |
| Production health | `200` |
| Alembic on production | `0062_index_dedupe (head)` |
| Existing routes | `/contract-review`, `/my-evidence`, `/evidence-review`, `/journey`, `/impact`, `/practice` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-173551.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-173923.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.44.0`, `ocr-frontend:pre-v5.44.0` |
| Restore drill | `69` users, `215` labs, `2` courses, `64` enrollments, `134` completions, `497` achievements, `1,575` activity events |

## Known limitations

- The Docker socket and privileged/helper containers remain host-root equivalent.
- RLS gaps remain on `users`, `auth_sessions`, `refresh_tokens`, `rbac_user_roles`, and `service_credentials`; single-host `default` tenant is not exposed.
- Alembic autogenerate remains blocked until the baseline is reconciled.
- The 25 legacy reviewed contracts and 190 pending contracts still need subject-matter sign-off.

## Acceptance checklist

- [x] Signed tag and verified supply-chain lock.
- [x] Production health, version, SSO, and public routes verified.
- [x] Production Valkey throttle check passes.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill passed.
- [x] Rollback images retained.
- [x] Manual and API reference regenerated.
- [x] Coverage audit passes structurally.
- [x] Test suite and component regression test pass.
