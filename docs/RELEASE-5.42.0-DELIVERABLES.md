# Release 5.42.0 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.42.0` |
| Signed tag | `v5.42.0` |
| Release commit | Pending tag |
| Alembic | `0062_index_dedupe` |
| Production | Pending |
| Development | Pending |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a restore drill |

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
| Backend tests | Pending |
| Frontend build and tests | Pending |
| Quality checks | Pending |
| Supply-chain lock | Pending |
| Production `/api/version` | Pending |
| Production health | Pending |
| Alembic on production | Pending |
| Public version and health | Pending |
| Existing routes | Pending |
| Review API | Pending |
| SSO | Pending |
| Duplicate DB indexes | Pending production check |
| Restore drill | Pending |
| Rollback images | Pending |

## Known limitations

- The Docker socket and privileged helper containers remain host-root
  equivalent. This release moves ephemeral state but does not isolate the Docker
  control path.
- `alembic check` still reports drift because runtime tenant DDL and legacy
  restores are outside the migration graph. Do not use autogenerate until the
  baseline is reconciled.
- Admin institution scoping and shared login throttling remain open.
- Host kernel, Docker, containerd, and systemd updates need a maintenance window
  and sudo. Unattended security upgrades are active.
- The 190 pending competency contracts and 25 legacy reviewed contracts still
  need subject-matter sign-off.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] Migration `0062` applied on development and production.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill passed.
- [ ] Rollback images retained.
- [ ] Manual and API reference regenerated.
- [ ] Coverage audit passes structurally.
- [ ] Test suite and component regression test pass.
