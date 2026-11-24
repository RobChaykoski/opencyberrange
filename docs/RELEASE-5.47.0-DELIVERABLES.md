# Release 5.47.0 deliverables

Status: **released and deployed** to development and production on 24
November 2026.

| Item | Value |
|---|---|
| Version | `5.47.0` |
| Signed tag | `v5.47.0` |
| Release commit | `ae0264b9` |
| Alembic | `0065_legacy_kali_columns` (no new migration) |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |

## Threat intelligence

| Deliverable | Detail |
|---|---|
| Ransomware section | Aggregated totals and top group counts on `/threat-awareness` |
| API | `GET /api/ransomware-activity`, authenticated and cached by file mtime |
| Source endpoints | RansomLook `/api/stats` and `/api/hot` only |
| Excluded data | Victim names, post links, crypto addresses, peer addresses |
| Refresh | `scripts/fetch-ransomware-feed.py`, offline snapshot with CC BY 4.0 attribution |
| Source policy | ADR 0009: Global Threat Map rejected, RansomLook aggregates accepted, Violations Watch rejected |

## Host agent

| Deliverable | Detail |
|---|---|
| Status | `GET /v1/status/<lab_id>` with a validated id and fixed `docker inspect` |
| Stop | `POST /v1/stop` behind `--enable-stop`; refused with `501` by default |
| Idempotency | An already-stopped container returns success |
| Audit | Denials, missing containers, failures, and stops are recorded |
| Validation | Status checked against a live development container; stop checked against a disposable `alpine` container |
| CI | Fake-runtime and mocked-Docker checks cover status, stop, invalid ids, disabled mutations, and runtime failures |

## Database model alignment

| Deliverable | Detail |
|---|---|
| Runtime indexes | Seven indexes declared in the models, including the partial unique one-active-session guard |
| Nullability | Three `institution_id` columns aligned to `NOT NULL DEFAULT 'default'` |
| Drift | Development falls from 48 to 38 operations, all tenant `institution_id` DDL |
| Migration | None; model metadata only |

## Verification

| Check | Result |
|---|---|
| Backend tests | `1,196 passed` |
| Frontend tests | `38 passed` |
| Frontend build | Passed |
| i18n budget | `5,310` bare strings across `104` files |
| Development drift | `38` operations |
| Production drift | `38` operations |
| Threat routes | `/threat-awareness` `200`; `/api/ransomware-activity` `401` without a token |
| Supply-chain lock | Verified with the release key |
| Restore drill | **PASSED** at 38 operations |
| Rollback images | `pre-v5.47.0` backend and frontend |

## Known limitations

- Both intelligence panels ship with labelled sample snapshots until an operator refreshes them.
- The ransomware snapshot shows group names and counts only; it is not an assessment of any group's claims.
- The host agent is not installed in production; status and stop are validated on development only.
- 38 Alembic drift operations remain: 18 tenant columns and 20 tenant indexes.
- The 25 legacy and 190 pending contracts still need subject-matter sign-off.

## Acceptance checklist

- [x] Signed tag and verified supply-chain lock.
- [x] CI integrity gate passes on the release commit.
- [x] Ransomware section renders with sample data and no victim fields.
- [x] Production health, version, SSO, and public routes verified.
- [x] Production drift is 38 operations.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill and restore-drift gate passed.
- [x] Rollback images retained.
