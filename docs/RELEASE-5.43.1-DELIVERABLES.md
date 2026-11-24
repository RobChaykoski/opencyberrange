# Release 5.43.1 deliverables

Status: **released and deployed** to development and production on 24 November
2026.

| Item | Value |
|---|---|
| Version | `5.43.1` |
| Signed tag | `v5.43.1` |
| Release commit | `34b3cbd9` |
| Alembic | `0062_index_dedupe` |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a passed restore drill |

## Fix

| Deliverable | Detail |
|---|---|
| Helper build path | The in-place deploy and installer run `scripts/build-helper-images.sh` by path with bash instead of requiring the executable bit. |
| Script mode | The build script is marked executable in the repository. |
| Result | A fresh deploy or install cannot skip the pinned `ocr-lab/netprobe:1.0` image. |

This patch follows 5.43.0, where the production helper image was built manually
after the deploy check skipped the script. The runtime 5.43.0 platform was
healthy, but a fresh deployment would have skipped the helper image.

## Verification

| Check | Result |
|---|---|
| Backend tests | Unchanged from 5.43.0 (`1,176 passed`) |
| Frontend build and tests | Build passed; `35` component tests passed |
| Quality checks | Green |
| Supply-chain lock | Verified with the release key |
| Helper image on production | Present; `ip`, `iptables`, `bridge`, `tc`, and `conntrack` verified |
| Production `/api/version` | `5.43.1` |
| Production health | `200` |
| Alembic on production | `0062_index_dedupe (head)` |
| Existing routes | `/contract-review`, `/my-evidence`, `/evidence-review`, `/journey`, `/impact`, `/practice` return `200` |
| SSO | Authentik OIDC provider present; `sso_enabled` true |
| Pre-deploy backup | `~/backups/ocr-backup-20261124-170800.dump` |
| Post-deploy backup | `~/backups/ocr-backup-20261124-171127.dump` |
| Rollback images | `opencyberrange-backend:pre-v5.43.1`, `ocr-frontend:pre-v5.43.1` |
| Restore drill | `69` users, `215` labs, `2` courses, `64` enrollments, `134` completions, `497` achievements, `1,575` activity events |

## Known limitations

- The Docker socket and privileged/helper containers remain host-root equivalent.
- Admin institution scoping and shared login throttling remain open.
- `alembic check` still reports drift; do not use autogenerate.
- The 25 legacy reviewed contracts and 190 pending contracts still need
  subject-matter sign-off.

## Acceptance checklist

- [x] Signed tag and verified supply-chain lock.
- [x] Helper build runs on a fresh checkout without the executable bit.
- [x] Production health, version, SSO, and public routes verified.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill passed.
- [x] Rollback images retained.
- [x] Test suite and component regression test pass.
