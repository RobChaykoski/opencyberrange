# Host and hardware

## Operating system

| Profile | Supported host OS | Status |
|---|---|---|
| Community / Academic | Ubuntu 22.04 LTS, Ubuntu 24.04 LTS | supported |
| Professional | Ubuntu 24.04 LTS | certified |
| Enterprise | Ubuntu 24.04 LTS | certified; inherits Professional |
| Next | Ubuntu 26.04 LTS | test candidate only |

Do not use the snap Docker package on a host that needs host networking or
WireGuard. Install Docker Engine from Docker's official repository and verify
`docker compose version` works.

## Minimum and recommended sizing

| Load | CPU | RAM | Disk | RangeBox |
|---|---:|---:|---:|---|
| Evaluation, one or two learners | 4 cores | 8 GB | 50 GB | disabled |
| Small class | 4-8 cores | 16 GB | 100 GB | enabled |
| Production classroom, 20+ concurrent | 8+ cores | 64 GB | 500 GB + ~200 GB images | enabled |

The database connection budget scales with workers:

```text
(DB_POOL_SIZE + DB_MAX_OVERFLOW) * OCR_UVICORN_WORKERS
  + reserved slots < PostgreSQL max_connections
```

The production default is one worker and a 10 + 10 pool. Raise the pool with
the worker count, or lower the pool; never raise workers alone.

## Host prerequisites

- Docker Engine 24+ with Compose v2.
- Git.
- A non-root operator account with sudo for installation.
- `platform/.env` with generated secrets.
- Absolute `LABS_HOST_PATH` pointing at `platform/labs`.
- TLS certificate or a reverse proxy that terminates TLS.
- Open ports 80/443 (and 8443 if the separate workbook origin is used).
- 51820/UDP only if the built-in WireGuard VPN is used.
- Timezone UTC is recommended for logs and scheduled jobs.

## Kernel and virtualization

- KVM is only required for KVM-backed labs and some RangeBox images.
- Check `lsmod | grep kvm` and `kvm-ok` on Ubuntu.
- Most exercises are Docker-only and do not need nested virtualization.
- If KVM is unavailable, disable the KVM-dependent labs or use a host that
  supports it; do not silently fall back to emulation in production.

## Disk layout

| Path | Purpose | Notes |
|---|---|---|
| Docker root | images, containers, volumes | 200 GB+ for prebuilt lab images |
| `platform/certs` | TLS certificate and key | keep private |
| `platform/labs` | lab definitions | mounted read-only into backend |
| `platform/.env` | runtime secrets | `chmod 600`, never commit |
| `/var/lib/ocr-ha` | optional HA status snapshot | read-only into backend |
| Backups | database snapshots | separate or off-host preferred |

## Host hardening checklist

- [ ] SSH key-only access; no password login for the operator.
- [ ] Firewall allows only 80/443, 8443, 51820/UDP (if VPN), and SSH from a
      management network.
- [ ] Docker daemon is not exposed on a public interface.
- [ ] `platform/.env` is root/operator readable only.
- [ ] Unattended security upgrades are enabled for the host.
- [ ] Time is synchronized.
- [ ] Backups are configured and a restore has been tested.
- [ ] Monitoring and disk alerts are connected to a real destination.

## Related

- [OS support](../../docs/OS-SUPPORT.md)
- [Supported versions](../../docs/SUPPORTED-VERSIONS.md)
- [Ubuntu 24.04 migration](../../docs/V2-UBUNTU-24.04-MIGRATION.md)
- [Ubuntu next candidate](../../docs/UBUNTU-NEXT-UPGRADE-CANDIDATE.md)
- [Deployment topology and sizing](../../docs/DEPLOYMENT-TOPOLOGY-AND-SIZING.md)
