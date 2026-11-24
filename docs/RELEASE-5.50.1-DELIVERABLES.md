# Release 5.50.1 deliverables

Status: **released and deployed** to development and production on 24
November 2026.

| Item | Value |
|---|---|
| Version | `5.50.1` |
| Signed tag | `v5.50.1` |
| Release commit | `bd1fd500` |
| Alembic | `0067_course_content_rls` (no migration) |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |

## Live threat snapshot

| Deliverable | Detail |
|---|---|
| FireHOL snapshot | `snapshot` mode, `469,828` reported entries, `148` countries |
| Geolocation | DB-IP Lite country database, local MMDB, CC BY 4.0 |
| Attribution | Written into the snapshot and `THIRD_PARTY_NOTICES.md` |
| Sample banners | Removed for both the infrastructure and ransomware sections |
| Guard | `--require-geoip` refuses an all-unknown snapshot |
| Operations | `docs/THREAT-AWARENESS-OPERATIONS.md` documents DB-IP Lite, GeoLite2, and the HackerTarget 50-lookup limit |

## Verification

| Check | Result |
|---|---|
| Threat snapshot | Loads as `snapshot`, `469,828` entries, `148` countries |
| Top country | United States, `140,032` entries (`29.8%`) |
| Ransomware snapshot | `snapshot`, `291` posts in `7` days, `15` groups |
| Backend tests | Unchanged: `1,196 passed` |
| Frontend tests | Unchanged: `38 passed` |
| Supply-chain lock | Verified with the release key |
| Development drift | `0` expected |
| Production drift | `0` operations |
| Production health | `200` |
| Restore drill | **PASSED** at `0` operations |
| Rollback images | `pre-v5.50.1` backend and frontend |

## Known limitations

- DB-IP Lite is less accurate than a commercial database for some countries.
- The snapshot is a point-in-time file; refresh it on the documented cadence.
- No third-party GeoIP API is called at runtime or in the request path.

## Acceptance checklist

- [x] Signed tag and verified supply-chain lock.
- [x] CI integrity gate passes on the release commit.
- [x] Production reports `snapshot` mode with no sample banner.
- [x] Production health, version, SSO, and public routes verified.
- [x] Production drift is `0`.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill and restore-drift gate at `0` passed.
- [x] Rollback images retained.
