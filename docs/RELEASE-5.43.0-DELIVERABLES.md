# Release 5.43.0 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.43.0` |
| Signed tag | `v5.43.0` |
| Release commit | Pending tag |
| Alembic | `0062_index_dedupe` |
| Production | Pending |
| Development | Pending |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a restore drill |

## Dependency refresh

| Package | From | To |
|---|---|---|
| FastAPI | 0.162.2 | 0.165.0 |
| SQLAlchemy | 2.1.8 | 2.1.9 |
| Pydantic | 2.14.3 | 2.14.4 |
| pydantic-settings | 2.16.2 | 2.16.3 |

## Docker helper hardening

| Deliverable | Detail |
|---|---|
| Pinned helper image | `ocr-lab/netprobe:1.0` on a digest-pinned Alpine 3.20 base |
| Baked tools | `iproute2`, `iptables`, `bridge-utils` |
| Runtime package installs | Removed from the host-network, isolation, GRETAP, and TC helpers |
| Helper pulls | Replaced `alpine:latest` and `alpine:3.19` with the pinned image |
| Build path | In-place deploy, development sync, and fresh install build the helper before the platform starts |

The helpers still run privileged or host-network containers because they must
read host routes and install host firewall rules. The helper image removes
runtime package installation and image drift; it does not make the backend
host-root-equivalent issue disappear. That remains a host-isolation decision.

## Verification

| Check | Result |
|---|---|
| Backend tests | `1,176 passed` |
| Frontend build and tests | Pending |
| Quality checks | Pending |
| Supply-chain lock | Pending |
| Helper image build | Pending production |
| Helper tools | `ip`, `iptables`, `bridge`, `tc`, `conntrack` present on development |
| Development lab spawn | `linux-1-1-ssh-service-detection` reached `running` and stopped |
| Helper isolation logs | Host network and lab egress rules ensured with no helper errors |
| Production `/api/version` | Pending |
| Production health | Pending |
| Alembic on production | Pending |
| Existing routes | Pending |
| SSO | Pending |
| Restore drill | Pending |
| Rollback images | Pending |

## Known limitations

- The Docker socket and privileged/helper containers remain host-root equivalent.
- Admin institution scoping and shared login throttling remain open.
- `alembic check` still reports drift because runtime tenant DDL and legacy
  restores are outside the migration graph. Do not use autogenerate.
- The 25 legacy reviewed contracts and 190 pending contracts still need
  subject-matter sign-off.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] Helper image built on production with the pinned base.
- [ ] Migration `0062` already applied; current on development and production.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill passed.
- [ ] Rollback images retained.
- [ ] Manual and API reference regenerated.
- [ ] Coverage audit passes structurally.
- [ ] Test suite and component regression test pass.
