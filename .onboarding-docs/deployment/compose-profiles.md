# Compose profiles

All compose files live under `platform/`. The default `docker compose` file is
not committed as `docker-compose.yml`; deployment scripts select a file
explicitly.

## Files

| File | Use | Notes |
|---|---|---|
| `docker-compose.dev.yml` | local development | bind-mounts source, Uvicorn reload, Vite |
| `docker-compose.prod.yml` | production / production-like | code baked into images, no bind mount |
| `docker-compose.override.yml` | host-specific overrides | `WG_SERVER_ADDRESS`; db entrypoint reset |
| `docker-compose.release5-local.yml` | Release 5 local exercise | do not mix with prod |
| `docker-compose.adopt.yml` | optional in-place adoption | used by `deploy-inplace.sh` if present |

The in-place deploy script composes:

```bash
docker compose \
  -f platform/docker-compose.prod.yml \
  [-f platform/docker-compose.adopt.yml] \
  [-f platform/docker-compose.override.yml] \
  ...
```

## Services

| Service | Container | Profile | Purpose |
|---|---|---|---|
| `db` | `ocr-db` | always | PostgreSQL 15 |
| `redis` | `ocr-valkey` | always | Valkey rate-limit counters |
| `docker-socket-proxy` | `ocr-docker-proxy` | always | restricted Docker API |
| `backend` | `ocr-backend` | always | FastAPI, scheduler, orchestration |
| `frontend` | `ocr-frontend` | always | nginx, SPA, TLS, `/api` proxy |
| `wiki-builder` | one-shot | `tools` | MkDocs build into `wiki_data` |
| `ldap` | `ocr-ldap` | `sso` | OpenLDAP test directory |
| `dex` | `ocr-dex` | `sso` | OIDC test IdP |

## Common commands

Development:

```bash
cd platform
docker compose --env-file .env -f docker-compose.dev.yml up -d --build
docker compose --env-file .env -f docker-compose.dev.yml logs -f backend
```

Production-like:

```bash
cd platform
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
docker compose --env-file .env -f docker-compose.prod.yml ps
```

Build the wiki:

```bash
docker compose --env-file .env -f docker-compose.dev.yml --profile tools \
  run --rm wiki-builder
```

SSO test stack:

```bash
docker compose --env-file .env -f docker-compose.dev.yml --profile sso up -d ldap dex
```

Run a one-off backend command:

```bash
docker compose --env-file .env -f docker-compose.prod.yml exec -T backend \
  python /app/app/scripts/discover_labs.py
```

## Rules

- Do not mix `dev` and `prod` files in one project.
- Do not add a service to production without a healthcheck and a network rule.
- Keep `docker_control` internal.
- The `wiki-builder` is a one-shot tool; it must not stay running.
- The `sso` profile is a demo/reference stack. It is not a production IdP.
- Any new port must be justified in [Network and ports](network-and-ports.md).

## Related

- [Deployment runbook](../../docs/DEPLOYMENT-RUNBOOK.md)
- [Docker deploy manual](../../Manual-Lite/00_Server_Deployment/08_Docker_Deploy_Manual.md)
- [MkDocs governance](../../docs/MKDOCS-GOVERNANCE.md)
