# Deployment topology and database sizing

## Supported topology

The supported production shape is **one Linux host running Docker Compose**.
The services are:

| Service | Role | Exposure |
|---|---|---|
| `ocr-frontend` | nginx, SPA, TLS, 8443 workbook origin | 443/TCP, 8443/TCP |
| `ocr-backend` | FastAPI, lab orchestration, scheduler | internal only |
| `ocr-db` | PostgreSQL 15 | internal only |
| `ocr-valkey` | shared rate-limit counters | internal only |
| `ocr-docker-proxy` | restricted Docker socket proxy | internal only |
| `ocr-wireguard` / Peer Manager | VPN peers | 51820/UDP, internal API |
| `ocr-wstunnel` | optional browser terminal transport | 5555/TCP when enabled |

Lab containers are created per session on isolated networks. They are not
published on host ports. The platform does not support a split database or
multi-host HA topology in Release 5.

## Sizing

| Resource | Evaluation | Production (20+ concurrent learners) |
|---|---|---|
| CPU | 4 cores | 8 or more |
| RAM | 32 GB | 64 GB |
| Disk | 100 GB | 500 GB |
| Prebuilt images | optional | ~200 GB |
| Backup space | separate or off-host | separate or off-host |

The backend derives its worker count from host CPU. Size the database
connection budget before increasing workers:

```text
(DB_POOL_SIZE + DB_MAX_OVERFLOW) × OCR_UVICORN_WORKERS
  + reserved slots < PostgreSQL max_connections
```

The production Compose default is a 20 + 20 pool. Do not raise workers without
raising PostgreSQL `max_connections` or lowering the pool.

## Database sizing notes

- PostgreSQL 15 is the current supported major. PostgreSQL 17 is a planned
  dump/restore upgrade, not an in-place change.
- The database stores accounts, courses, lab sessions, completions, consent
  evidence, security events, and audit history. It does not store lab images or
  learner filesystem data.
- Keep the `backups_data` volume writable by backend UID `10001`.
- Back up the database, the erasure ledger, and the platform `.env` together;
  the database alone is not a complete restore set.
- A restore drill is required after a volume, host, or major-version change.
  See [Backup and restore testing](BACKUP-RESTORE-TEST.md).

## Network rules

- Expose only 443/TCP, 8443/TCP, and 51820/UDP to learners; 5555/TCP only when
  WSTunnel is deliberately enabled.
- Keep 5432/TCP, 6379/TCP, and the Docker socket internal.
- Do not run `docker image prune -a`; it deletes prebuilt lab images.
- The 8443 workbook origin is a separate browser origin with its own storage and
  CSP allowance.
