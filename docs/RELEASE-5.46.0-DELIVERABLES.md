# Release 5.46.0 deliverables

Status: **released and deployed** to development and production on 24
November 2026. Release 5.46.1 follows with the design-token alignment for the
threat-awareness panel.

| Item | Value |
|---|---|
| Version | `5.46.0` |
| Signed tag | `v5.46.0` |
| Release commit | `2c089d66` |
| Alembic | `0065_legacy_kali_columns` (no new migration) |
| Production | Deployed and verified |
| Development | Deployed and verified |
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
| Quality checks | Green |
| Supply-chain lock | Verified with the release key |
| Development Alembic | `0065_legacy_kali_columns` |
| Development drift | 48 operations |
| Production `/api/version` | `5.46.0` |
| Production health | `200` |
| Restore drill | Covered by the 5.46.1 post-deploy drill |
| Rollback images | `pre-v5.46.0` backend and frontend |

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

- [x] Signed tag and verified supply-chain lock.
- [x] Threat-awareness panel reachable on development and production.
- [x] Sample snapshot labelled; no addresses in the API response.
- [x] Production health, version, SSO, and public routes verified.
- [x] Production drift still 48 operations.
- [x] Pre-deploy backup `ocr-backup-20261124-185419.dump`.
- [ ] Restore drill passed (recorded in 5.46.1).
- [x] Rollback images retained.
- [x] Test suite and component regression test pass.
