# Storage and volumes

## Docker volumes

| Volume | Mount | Contents | Backup |
|---|---|---|---|
| `postgres_data` | `/var/lib/postgresql/data` | PostgreSQL cluster | yes, with the erasure ledger and `.env` |
| `workbook_data` | `/workbook` | Exercise Studio state, erasure ledger, suppression ledger | yes |
| `wiki_data` | `/usr/share/nginx/wiki` (read-only in frontend) | Built MkDocs tree | rebuildable, but keep for release evidence |
| `backups_data` | `/app/backups` | Database snapshots and manifests | yes, preferably off-host |
| `ldap_data` | `/var/lib/ldap` | optional SSO test directory | only for the test stack |
| `ldap_config` | `/etc/ldap/slapd.d` | optional SSO test configuration | only for the test stack |

## Host bind mounts

| Host path | Container path | Purpose |
|---|---|---|
| `platform/labs` | `/labs` (read-only) | lab definitions and compose files |
| `platform/templates` | `/app/templates` (read-only) | Exercise Studio templates |
| `platform/certs` | `/etc/nginx/certs` (read-only) | TLS certificate and key |
| `/var/lib/ocr-ha` | `/var/lib/ocr-ha` (read-only) | optional HA status snapshot |
| `platform/.env` | not mounted | runtime configuration |
| `curriculum-manifest.yaml` | `/app/curriculum-manifest.yaml` | chapter display IDs |
| `curriculum-frameworks.yaml` | `/app/curriculum-frameworks.yaml` | competency/framework map |

## What lives where

| Data | Store | Notes |
|---|---|---|
| Users, courses, labs, sessions, completions, evidence, consent, audit | PostgreSQL | transactional system of record |
| Rate-limit counters | Valkey | ephemeral; no RDB/AOF |
| Exercise Studio state | `workbook_data` | survives container recreation |
| Erasure and suppression proof | `workbook_data` | append-only; must survive restore |
| Wiki output | `wiki_data` | build artifact; frontend mounts read-only |
| Database snapshots | `backups_data` | keep off-host when possible |
| Browser token and refresh token | browser `localStorage` | client side; not server storage |
| Impersonation state | browser `sessionStorage` | clears on tab close |
| Wiki session | HttpOnly cookie | scoped by `WIKI_COOKIE_DOMAIN` |
| Lab target state | per-session containers | ephemeral |
| Lab images | Docker image store | prebuilt; do not prune |

## Permissions

- The backend container runs as UID 10001 in production.
- Keep `backups_data` writable by that UID.
- The workbook volume must be writable for Exercise Studio and the erasure
  ledger.
- The labs mount is read-only.
- `platform/.env` must be `chmod 600`.

## Backup set

A complete restore set is:

1. PostgreSQL dump or snapshot.
2. `workbook_data` (especially the erasure/suppression ledger).
3. `platform/.env` (secrets and endpoints).
4. `platform/certs` (TLS).
5. The signed release tag and image digests.

The database alone is not enough. A restore must re-apply the consent
suppression ledger.

## Destructive commands to avoid

```bash
# Never in production:
docker image prune -a          # deletes prebuilt lab images
docker volume rm platform_postgres_data
docker compose down -v
```

Use the retention and cleanup tools in the admin UI or the documented scripts.

## Related

- [Retention policies](../../docs/RETENTION-POLICIES.md)
- [Backup and restore testing](../../docs/BACKUP-RESTORE-TEST.md)
- [Backup security](../../docs/BACKUP-SECURITY.md)
- [Database subsystem](../database/subsystem-overview.md)
- [Privacy and data deletion](../../docs/PRIVACY-AND-DATA-DELETION.md)
