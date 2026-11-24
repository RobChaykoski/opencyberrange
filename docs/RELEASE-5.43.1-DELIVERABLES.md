# Release 5.43.1 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.43.1` |
| Signed tag | `v5.43.1` |
| Release commit | Pending tag |
| Alembic | `0062_index_dedupe` |
| Production | Pending |
| Development | Pending |
| Supply-chain lock | Refreshed and signed with the release key |

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
| Frontend build and tests | Pending |
| Quality checks | Pending |
| Supply-chain lock | Pending |
| Helper image on production | Present; `ip`, `iptables`, `bridge`, `tc`, `conntrack` verified |
| Production `/api/version` | Pending |
| Production health | Pending |
| Alembic on production | Pending |
| Restore drill | Pending |

## Known limitations

- The Docker socket and privileged/helper containers remain host-root equivalent.
- Admin institution scoping and shared login throttling remain open.
- `alembic check` still reports drift; do not use autogenerate.
- The 25 legacy reviewed contracts and 190 pending contracts still need
  subject-matter sign-off.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] Helper build runs on a fresh checkout without the executable bit.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill passed.
- [ ] Rollback images retained.
- [ ] Test suite and component regression test pass.
