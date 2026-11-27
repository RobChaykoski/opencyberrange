# Deployment

This subsystem covers the host, the Compose profile, ports, volumes, TLS, and
the release procedure. Start with the [platform overview](../platform-overview.md)
if you have not read it.

## Supported shape

One Linux host running Docker Compose. The reference services are `ocr-frontend`,
`ocr-backend`, `ocr-db`, `ocr-valkey`, `ocr-docker-proxy`, and the optional
one-shot `wiki-builder`. SSO adds `ocr-ldap` and `ocr-dex` under the `sso`
profile.

There is no supported split-database or active-active multi-host topology in
Release 5. HA is an optional read-only control plane with a standby database.

## Folder map

| Page | Use it for |
|---|---|
| [Host and hardware](host-and-hardware.md) | OS, CPU, RAM, disk, Docker version |
| [Network and ports](network-and-ports.md) | Public and internal ports, TLS, ProxyHeaders |
| [Compose profiles](compose-profiles.md) | dev, prod, tools, sso, override, local |
| [Storage and volumes](storage-and-volumes.md) | PostgreSQL, workbook, wiki, backups, certs |
| [Release and deploy](release-and-deploy.md) | Signed tag, in-place deploy, rollback, verification |

## Configuration

The runtime configuration is `platform/.env`, created from
`platform/.env.example`. Secrets are generated, never committed. The most
important variables:

```text
JWT_SECRET
SETUP_TOKEN
POSTGRES_PASSWORD / DATABASE_URL
WG_SERVER_ENDPOINT / WG_SERVER_PUBLIC_KEY / WG_API_KEY / WG_ENCRYPTION_KEY
SERVER_PUBLIC_HOST / PUBLIC_BASE_URL / CORS_ORIGINS
LABS_HOST_PATH
OCR_DOCKER_PROXY_EXEC
RATELIMIT_STORAGE_URI
```

See [`.env.example`](../../platform/.env.example) for every variable and its
comment.

## Start and verify

```bash
cd platform
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
docker compose --env-file .env -f docker-compose.prod.yml ps
curl -fsS http://127.0.0.1:8000/health
```

Expected services: `ocr-db`, `ocr-valkey`, `ocr-backend`, `ocr-frontend` healthy.
Then open the public address and complete the setup wizard with `SETUP_TOKEN`.

## Seed and discover

```bash
docker compose --env-file .env -f docker-compose.prod.yml exec -T backend \
  python /app/app/scripts/init_platform.py
```

`init_platform.py` is idempotent: curriculum, labs, example course, and
achievements. It does not create accounts.

## In-place release

The host deploy script is `scripts/deploy-inplace.sh`. It expects:

- `platform/docker-compose.prod.yml`
- optional `platform/docker-compose.adopt.yml`
- optional `platform/docker-compose.override.yml`

It builds images, applies migrations, recreates services, and verifies health.
Run the dry run first:

```bash
bash scripts/deploy-inplace.sh --dry-run
bash scripts/deploy-inplace.sh
```

Record the deployment in `docs/PRODUCTION-DEPLOYMENT-STATEMENT.md` and add a
release deliverables page.

## Non-negotiables

- Signed releases only. No ad-hoc host edits.
- Keep PostgreSQL, Valkey, and the Docker socket private.
- Back up the database, the erasure ledger, and the platform `.env` together.
- Do not run `docker image prune -a`; it deletes prebuilt lab images.
- A restore drill is required after a volume, host, or major-version change.

## Related documents

- [Deployment runbook](../../docs/DEPLOYMENT-RUNBOOK.md)
- [Deployment topology and sizing](../../docs/DEPLOYMENT-TOPOLOGY-AND-SIZING.md)
- [Reverse proxy](../../docs/REVERSE-PROXY.md)
- [Backup and restore testing](../../docs/BACKUP-RESTORE-TEST.md)
- [OS support](../../docs/OS-SUPPORT.md)
- [Supported versions](../../docs/SUPPORTED-VERSIONS.md)
