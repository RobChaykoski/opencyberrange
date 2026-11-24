# Release 5.42.0 deliverables

Status: **released and deployed** to development and production on 24 November
2026.

| Item | Value |
|---|---|
| Version | `5.42.0` |
| Signed tag | `v5.42.0` |
| Release commit | `31ed83ab` |
| Alembic | `0062_index_dedupe` |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a passed restore drill |

## Learner-visible contract state

| Deliverable | What it does | Where |
|---|---|---|
| Contract status API | Compact status, provisional flag, and next-review date per lab | Track and lab payloads |
| Exercise notice | Explains that the skills credited are provisional when the contract is pending, stale, overdue, or changes-requested | Exercise page |
| Mapping review badge | Marks stale, overdue, and changes-requested labs in the exercise list | Track page |
| Evidence notice | Marks each evidence card provisional when its lab contract is not current | My Evidence |
| No reviewer exposure | The learner payload excludes reviewer identity, rationale, drafts, and snapshots | Service |

## Review export and release gate

| Deliverable | What it does | Where |
|---|---|---|
| Manifest exporter | Writes a pseudonymous signed-review manifest and a private administrator export | `scripts/export-contract-reviews.py` |
| Overrides writer | Writes the signed snapshot, hashes, and reviewer reference into the overrides file | `scripts/export-contract-reviews.py` |
| Offline gate | Refuses reviewed YAML without a matching signed review; checks contract, lab, and taxonomy hashes and the next-review date | `--check` |
| Shared integrity module | One hashing implementation for the service and the gate | `app.services.competency_contract_integrity` |
| Generator round-trip | Accepts the full signed evidence list and assessment criteria | `scripts/generate-competency-contracts.py` |

The 25 contracts marked reviewed before the signed-review cycle still need a
signature. The gate reports them; it does not grandfather them.

## Workbook reliability

| Deliverable | Detail |
|---|---|
| Cookie race | Open a blank window, refresh the HttpOnly wiki cookie, then navigate the window to the workbook. |

## Security and database hardening

| Deliverable | Detail |
|---|---|
| Cross-worker state | Exercise-tester, impersonation, and stress-run state under `/app/run-state` (mode 750) |
| Fernet validation | `WG_ENCRYPTION_KEY` and previous rotation keys validated at startup |
| Topology input | `security_opt` string-list and `http_port` range/type checks |
| Password-breach digest | HIBP SHA-1 marked `usedforsecurity=False` |
| Index hygiene | Migrations `0061` and `0062` remove redundant indexes and add instructor and lab-session hot-path indexes |
| Model hygiene | Duplicate index declarations removed so `create_all` does not recreate them |

## Verification

| Check | Result |
|---|---|
| Backend tests | `1,176 passed` |
| Frontend build and tests | Build passed; `35` component tests passed |
| Quality checks | Green |
| Supply-chain lock | Verified with the release key |
| Production `/api/version` | `5.42.0` |
| Production health | `200` |
| Alembic on production | `0062_index_dedupe (head)` |
| Public version and health | `5.42.0` and `200` |
| Existing routes | `/journey`, `/impact`, `/practice`, `/my-evidence`, `/evidence-review`, `/contract-review` return `200` |
| Review API | `/api/competency-reviews/catalogue` is gated (`401` unauthenticated) |
| SSO | Authentik OIDC provider present; `sso_enabled` true |
| CSP | `frame-src` includes dynamic lab targets; `frame-ancestors 'self'` |
| Database index hygiene | Duplicate exact index sets: `0`; hot indexes present: `2` |
| Cross-worker state | `/app/run-state` mode `750`, owned by `ocr` |
| Restore drill | 69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events |
| Rollback images | `opencyberrange-backend:pre-v5.42.0`, `ocr-frontend:pre-v5.42.0` |

## Known limitations

- The Docker socket and privileged helper containers remain host-root
  equivalent. This release moves ephemeral state but does not isolate the Docker
  control path.
- `alembic check` still reports drift because runtime tenant DDL and legacy
  restores are outside the migration graph. Do not use autogenerate until the
  baseline is reconciled.
- Admin institution scoping and shared login throttling remain open.
- Host kernel 6.8.0-151 and Docker 29.10.0 were applied on 24 November; only a
  non-security `libsqlite3-0` update remains. Unattended security upgrades are
  active.
- The 190 pending competency contracts and 25 legacy reviewed contracts still
  need subject-matter sign-off.

## Acceptance checklist

- [x] Signed tag and verified supply-chain lock.
- [x] Migration `0062` applied on development and production.
- [x] Production health, version, SSO, and public routes verified.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill passed.
- [x] Rollback images retained.
- [x] Manual and API reference regenerated.
- [x] Coverage audit passes structurally.
- [x] Test suite and component regression test pass.
