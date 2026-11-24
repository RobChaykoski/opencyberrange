# Release 5.46.2 deliverables

Status: **released and deployed** to development and production on 24
November 2026.

| Item | Value |
|---|---|
| Version | `5.46.2` |
| Signed tag | `v5.46.2` |
| Release commit | `f7cbe946` |
| Alembic | `0065_legacy_kali_columns` (no migration) |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |

## Release metadata fix

| Change | Detail |
|---|---|
| Integrity manifest | `software-integrity.json` regenerated; `release` now `5.46.2` instead of the stale `5.45.0` |
| Root cause | Releases 5.46.0 and 5.46.1 bumped the lock but did not regenerate the manifest that copies the lock's `release` field |
| CI gate | The existing "Verify runtime integrity manifest is current" step now passes |
| Checklist | Added the ordered release-preparation steps to `docs/RELEASES.md` |
| Stability check | Two consecutive generations produce the same SHA-256 |

## Verification

| Check | Result |
|---|---|
| Manifest stability | `1B693FDFD72C02DB76B4269024D737EC10470944FFFF31710BE1BFCCE67623D5` on repeated runs |
| Manifest release | `5.46.2` |
| Backend tests | Unchanged: `1,189 passed` |
| Frontend build and tests | Unchanged: build passed, `37 passed` |
| Supply-chain lock | Verified with the release key |
| Development `/api/version` | `5.46.2` |
| Production `/api/version` | `5.46.2` |
| Production health | `200` |
| Restore drill | **PASSED** at 48 operations |
| Rollback images | `pre-v5.46.2` backend and frontend |

## Acceptance checklist

- [x] Signed tag and verified supply-chain lock.
- [x] CI integrity gate passes on the release commit.
- [x] Production health, version, SSO, and public routes verified.
- [x] Production drift still 48 operations.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill and restore-drift gate passed.
- [x] Rollback images retained.
