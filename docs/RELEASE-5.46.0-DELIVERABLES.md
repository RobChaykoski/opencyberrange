# Release 5.46.0 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.46.0` |
| Signed tag | `v5.46.0` |
| Release commit | Pending tag |
| Alembic | `0065_legacy_kali_columns` (no new migration) |
| Production | Pending |
| Development | Pending |
| Supply-chain lock | Refreshed and signed with the release key |

## Host-agent spike

| Deliverable | Detail |
|---|---|
| Agent skeleton | `platform/labd/ocr_labd.py`: loopback, bearer-token, fixed operation list |
| Refused surface | No arbitrary `exec`, image build, volume, or host-filesystem call |
| Mutations | Return `501` until each operation is validated |
| Service unit | `deploy/systemd/ocr-labd.service` with `NoNewPrivileges` and `ProtectSystem=strict` |
| CI check | `scripts/check-labd-agent.py` verifies health, auth rejection, capabilities, `501`, and `404` |
| Decision | ADR 0007 accepted for a spike; production keeps the pre-baked helper and restricted socket proxy |

## Threat awareness

| Deliverable | Detail |
|---|---|
| Panel | `/threat-awareness` shows feed and country counts with shares |
| API | `GET /api/threat-awareness`, authenticated, cached by file mtime |
| Aggregation | Country and feed counts only; individual addresses are rejected |
| Minimum bucket | Non-zero buckets below 25 are refused |
| Refresh | `scripts/fetch-threat-feed.py`, offline, with optional local GeoIP |
| Shipped data | Labelled **sample** snapshot; a live refresh is an explicit operations action |
| Decision | ADR 0008 rejects the GPL-3.0 Global Threat Map integration |
| Attribution | FireHOL and the rejected project recorded in `THIRD_PARTY_NOTICES.md` |

## Operations

| Deliverable | Detail |
|---|---|
| Restore-drift gate | `scripts/check-restore-drift.sh` restores a dump, migrates it, and enforces the 48-operation budget |
| Dependency currency | `scripts/check-dependency-currency.py` runs in the weekly audit workflow |
| Patch cadence | `docs/DEPENDENCY-WORKFLOW.md` defines weekly, monthly, quarterly, and major-upgrade steps |
| Contract drafts | 25 unsigned drafts seeded on development for subject-matter sign-off |
| Dependency bump | `psycopg[binary] 3.3.9`, `redis 8.2.0` |

## Verification

| Check | Result |
|---|---|
| Backend tests | `1,189 passed` (includes 7 threat-awareness tests) |
| Frontend build | Passed |
| Frontend tests | `37 passed` |
| i18n budget | `5,299` bare strings across `104` files (baseline updated in review) |
| Quality checks | Pending |
| Supply-chain lock | Pending |
| Development Alembic | `0065_legacy_kali_columns` expected |
| Development drift | 48 operations expected |
| Production `/api/version` | Pending |
| Production health | Pending |
| Restore drill | Pending |
| Rollback images | Pending |

## Known limitations

- The threat panel ships with a sample snapshot until an operator refreshes it.
- Country attribution needs a local GeoIP database; without one, entries are
  counted as unknown.
- The host agent performs no lab work yet; mutations return `501`.
- The Docker socket and privileged/helper containers remain host-root equivalent.
- 48 Alembic drift operations remain: 18 runtime tenant columns, 20 tenant
  indexes, 3 nullability changes, and 7 runtime/legacy indexes.
- The 25 legacy reviewed contracts and 190 pending contracts still need
  subject-matter sign-off.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] Threat-awareness panel reachable on development and production.
- [ ] Sample snapshot labelled; no addresses in the API response.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Production drift still 48 operations.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill passed.
- [ ] Rollback images retained.
- [ ] Test suite and component regression test pass.
