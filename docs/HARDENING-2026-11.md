# Hardening and refactor — November 2026

Status: **implemented and deployed to development (`172.16.16.44`)** on
12 November 2026. Production was not changed.

## What changed

### 1. Single-worker default and one health probe

- The backend image now defaults to `OCR_UVICORN_WORKERS=1`. Multi-worker is a
  documented scale-out path: raise the worker count together with
  `DB_POOL_SIZE` and `DB_MAX_OVERFLOW`.
- The Compose healthcheck is the single source of truth. It uses the image's
  Python instead of `curl`.
- The Dockerfile `HEALTHCHECK` was removed so the two probes cannot drift.

### 2. Non-root runtime and Docker socket proxy

- The backend image is multi-stage: build tools stay in the build stage; the
  runtime stage has no `gcc` or headers.
- The runtime user is `ocr` (UID 10001). `/app/backups` and `/workbook` are
  owned by that user so named volumes inherit write access.
- The backend no longer mounts `/var/run/docker.sock`. It talks to
  `tecnativa/docker-socket-proxy` over `DOCKER_HOST=tcp://docker-socket-proxy:2375`.
- The proxy is on the `docker_control` network, which only the backend joins.
  `BUILD` stays off unless on-demand lab builds are enabled.
- Verified on development: the backend runs as UID 1000 (dev override), the
  proxy reports Docker 29.9.3, and a full `docker compose` lifecycle
  (network create, container run/logs/stop/remove, network remove) succeeds
  through the proxy.

### 3. Postgres-backed tests

The CI backend job already runs the suite against PostgreSQL 17 with
`TEST_DATABASE_URL`. `tests/conftest.py` now also accepts
`OCR_TEST_DATABASE_URL` for local or alternate runners.

### 4. Alembic stamp and upgrade path

- Startup still applies the inline compatibility patches, then calls
  `_stamp_or_upgrade_alembic()` under the schema advisory lock.
- A database with no `alembic_version` row is stamped at head; an existing
  version is upgraded to head.
- New revisions:
  - `0013_achievement_event_metadata` — achievement group/tier/difficulty/points
    and `competitions.experience_key`.
  - `0014_performance_indexes` — `ix_labsession_expires`, `ix_revoked_at`,
    `ix_genitem_lease`.
- Verified on development: the database is at `0014_performance_indexes`, and
  the new columns and indexes exist.

### 5. Fernet key rotation

- Secrets now use a `v1:` envelope over a `MultiFernet`.
- `WG_ENCRYPTION_KEY` is the current key; `WG_ENCRYPTION_KEY_PREVIOUS` is a
  comma-separated list of old keys used only for decryption.
- Legacy bare Fernet tokens still decrypt.
- `python -m app.scripts.reencrypt_secrets --dry-run|--apply` rewrites old rows
  onto the current key. Malformed rows are reported for manual review instead of
  stopping the pass.
- Verified on development: a new secret round-trips with the `v1:` prefix, and
  the re-encryption pass moved 2 stored secrets and then reported 0 remaining.

### 6. Performance and stability

- Report PDF generation now runs in `run_in_threadpool`, so a large export does
  not block the event loop or the single worker.
- `users.avatar_data`, `competitions.logo_data`, and
  `competition_sponsors.logo_data` are deferred, so list endpoints do not drag
  large base64 blobs.
- The course roster query eager-loads `CourseEnrollment.user` instead of one
  query per learner.
- PostgreSQL connections set `statement_timeout` (default 30s,
  `DB_STATEMENT_TIMEOUT_MS`).
- Token-revocation pruning moved from every logout to an hourly scheduler task.
  `revoke_token` now only writes the revocation row.

### 7. Valkey replaces Redis

- `valkey/valkey:9.1.3-alpine` (BSD-3-Clause) replaces `redis:7.2-alpine` as the
  rate-limit store. The service name stays `redis` and the URI stays
  `redis://...`, because `redis-py` is RESP-compatible.
- `versions.yaml`, the install/deploy scripts, the production Compose file, the
  licence checker, the About page, and the generated about/SBOM data were
  updated. `THIRD_PARTY_LICENSES/valkey-BSD-3-Clause.txt` replaces the Redis
  notice.
- Verified on development: `/api/about` reports Valkey 9.1.3 and the backend
  uses `redis://valkey:6379/0`.

## Development deployment notes

- `platform/docker-compose.dev.yml` is the checked-in development shape.
- The development host has a deployment-specific `docker-compose.override.yml`
  that only sets `OCR_BUILD_REVISION`; the old Redis override was removed.
- The backend bind mount is owned by the host user, so the dev Compose runs the
  container as `${OCR_UID:-1000}:${OCR_GID:-1000}`. After the first `up`, chown
  the workbook volume once:
  `docker run --rm -v opencyberrange_workbook_data:/workbook alpine chown -R 1000:1000 /workbook`.
- Backups on development live in `backend/backups`; that directory must be
  writable by the runtime UID.

## Next

1. Drain the remaining inline `ALTER TABLE` blocks in `main.py` one Alembic
   revision at a time. Add `scripts/check-no-inline-migrations.py` only after the
   inline section is empty, so the guard does not fail on legacy lines.
2. Rehearse a PostgreSQL major-version upgrade now that Alembic owns the schema.
3. Run a real backup and restore drill from the `backups_data` volume, including
   the integrity-ledger verification.
4. Audit the frontend nginx configuration and the `ui-*.mjs` smoke suites; this
   pass covered the backend.
5. Add the remaining §8.1 eager-load fixes in `analytics.py`, `dashboard.py`,
   and `admin.py`, using `stress_test.py` query-count diffs as the gate.

## Verification commands

```bash
cd platform/backend
python -m pytest -q
python -m ruff check app tests/test_crypto_rotation.py tests/test_alembic_baseline.py
python -m app.scripts.reencrypt_secrets --dry-run
```

```bash
python scripts/check-licences.py
python scripts/check-data-dictionary.py
python scripts/check-question-banks.py
python scripts/check-devfest-plan.py
```

## Rollback

- Development Compose backups:
  `docker-compose.yml.bak-hardening-20261112` and
  `docker-compose.override.yml.bak-hardening-20261112`.
- The schema changes are additive. Rolling back the image does not remove the
  new columns or indexes; they are harmless to the previous code.
- To restore the old rate-limit store, point `RATELIMIT_STORAGE_URI` at a Redis
  service again. The counters are ephemeral, so no data migration is needed.
- Do not roll back `WG_ENCRYPTION_KEY` after running `reencrypt_secrets --apply`
  unless the previous key is still in `WG_ENCRYPTION_KEY_PREVIOUS`.
