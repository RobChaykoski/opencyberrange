# Release 5.46.2 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.46.2` |
| Signed tag | `v5.46.2` |
| Release commit | Pending tag |
| Alembic | `0065_legacy_kali_columns` (no migration) |
| Production | Pending |
| Development | Pending |
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
| Supply-chain lock | Pending |
| Development `/api/version` | Pending |
| Production `/api/version` | Pending |
| Production health | Pending |
| Restore drill | Pending |
| Rollback images | Pending |

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] CI integrity gate passes on the release commit.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Production drift still 48 operations.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill passed.
- [ ] Rollback images retained.
