# Ubuntu 26.04 LTS and Valkey 9.1.3 vs Redis 7.2 test plan

Status: **planned — not certified, not deployed**

Requested label: **Ubuntu 26.06**
Actual upstream baseline: **Ubuntu 26.04 LTS (Resolute Raccoon)**
Ubuntu 26.04 LTS was released on 23 April 2026 and is supported until May
2031. Ubuntu does not publish a 26.06 LTS; the existing
`ubuntu-next.yml` workflow uses the `ubuntu-26.04` runner for this label.

## Goal

Decide whether the platform should keep `redis:7.2-alpine` or move to
`valkey/valkey:9.1.3-alpine` as the shared rate-limit store, and certify the
result on Ubuntu 26.04 LTS before changing the production pin.

The store is used only for SlowAPI/`limits` rate-limit counters. It is not a
system of record, not a queue, and not a cache for learner data.

## Current state

- Production Compose runs `redis:7.2-alpine` as `ocr-redis`.
- The backend uses `RATELIMIT_STORAGE_URI=redis://redis:6379/0`.
- Counters are ephemeral: `--save "" --appendonly no`.
- The health check is `redis-cli ping`.
- Redis 7.2 is BSD-3-Clause. Redis 7.4 and later are RSALv2/SSPLv1.
- Valkey 9.1.3 is BSD-3-Clause, RESP-compatible, and includes security fixes
  released on 26 October 2026.
- The 26.04 workflow already renders production Compose and builds both
  images; it does not yet test the rate-limit store.

## Decision to make

Adopt Valkey 9.1.3 only if it passes the functional, security, licence, and
host gates below. Otherwise keep Redis 7.2 and record the reason.

Keeping the Compose service name `redis` and the `redis://` URI is intentional
for the test: Valkey is protocol-compatible, and `limits`/`redis-py` already
speak the Redis wire protocol. A rename to `valkey` is a separate cleanup and
should not be mixed into the certification.

## Test matrix

| Host | Store | Purpose |
| --- | --- | --- |
| Ubuntu 24.04 LTS | `redis:7.2-alpine` | Current production baseline |
| Ubuntu 24.04 LTS | `valkey/valkey:9.1.3-alpine` | Drop-in compatibility |
| Ubuntu 26.04 LTS | `redis:7.2-alpine` | Isolate host changes from store changes |
| Ubuntu 26.04 LTS | `valkey/valkey:9.1.3-alpine` | Target combination |
| Ubuntu 26.04 LTS | `valkey/valkey:9.0.7-alpine` | Fallback if 9.1 regresses |
| Ubuntu 26.04 LTS | `valkey/valkey:8.1.11-alpine` | Conservative fallback |

Use `9.1.3-alpine3.24` or the pinned digest, not `latest`. Record the image
digest in the test report.

## Functional checks

1. Container starts with `--save "" --appendonly no`.
2. Health check returns `PONG` using `valkey-cli` or the image's compatible
   `redis-cli`.
3. `PING`, `SET`/`GET`, `INCR`, `EXPIRE`, and `TTL` behave as expected.
4. `INFO server` reports the Valkey version and confirms the expected build.
5. SlowAPI/`limits` can read and write counters through
   `RATELIMIT_STORAGE_URI=redis://redis:6379/0`.
6. A rate-limited route returns `429` after the configured threshold and the
   counter expires.
7. Restarting the backend does not reset counters while the store stays up.
8. Two backend workers share the same counter. Run the check with two
   processes or two containers, because the production default is one worker.
9. Authentication, flag submission, quiz submission, and report endpoints
   show no new errors in the backend log.
10. The store container restarts cleanly and the backend reconnects.

## Ubuntu 26.04 host gates

These are independent of Valkey and must pass before production promotion:

- Docker Engine and Compose v2 install and start.
- systemd cgroup v2 behaviour; 26.04 removed cgroup v1 support.
- nftables and Docker isolation rules persist across reboot.
- WireGuard peer management and firewall persistence.
- KVM availability and Windows lab VMs.
- Installer scripts, `setup-range-server.sh`, `install-platform.sh`, and
  `deploy-updates.sh`.
- Backup and restore drill.
- Large-cohort session, VPN, and rate-limit load.
- `check-nginx-security-headers.py` and the UI smoke workflow.

Ubuntu 26.04 uses APT 3.1, which removed `apt-key`; the installer must use
`Signed-By` keyrings. Dracut is the default initramfs tool. Review both before
the host drill.

## CI design

Add a matrix job to `.github/workflows/ubuntu-next.yml` or a separate
`.github/workflows/valkey-next.yml`:

```yaml
strategy:
  fail-fast: false
  matrix:
    include:
      - runner: ubuntu-24.04
        store: redis
        image: redis:7.2-alpine
      - runner: ubuntu-24.04
        store: valkey
        image: valkey/valkey:9.1.3-alpine
      - runner: ubuntu-26.04
        store: redis
        image: redis:7.2-alpine
      - runner: ubuntu-26.04
        store: valkey
        image: valkey/valkey:9.1.3-alpine
```

The job should:

1. Start the selected store as a service container on port 6379.
2. Render Compose with `RATELIMIT_STORAGE_URI` pointed at the service.
3. Run the backend test suite with `TEST_DATABASE_URL`.
4. Run `scripts/check-rate-limit-store.py` against the live store.
5. Build the backend and frontend images.
6. Upload the store version, image digest, test output, and rate-limit
   evidence to the workflow summary.

A test-only Compose override keeps production unchanged:

```yaml
# platform/docker-compose.valkey-test.yml
services:
  redis:
    image: valkey/valkey:9.1.3-alpine
    container_name: ocr-valkey-test
    command: ["valkey-server", "--save", "", "--appendonly", "no"]
    healthcheck:
      test: ["CMD-SHELL", "valkey-cli ping | grep -q PONG"]
```

Run it with:

```bash
docker compose -f docker-compose.prod.yml \
  -f docker-compose.valkey-test.yml up -d redis backend
```

Do not change the production Compose file until the decision gate passes.

## Probe script

Add `scripts/check-rate-limit-store.py` with these checks:

- connect with the same Redis client library the backend uses;
- `PING`;
- `SET`/`GET` a namespaced test key;
- `INCR` and `EXPIRE`, then confirm `TTL` is positive;
- read `INFO server` and print `redis_version` or `valkey_version`;
- delete only the test key;
- exit non-zero on any mismatch.

The script must not scan or delete production keys.

## Performance check

Rate limiting is a low-throughput path. Measure rather than assume:

- `redis-benchmark` or `valkey-benchmark` for 10k `INCR`/`GET` operations.
- Backend p95 latency for login, flag submission, and a rate-limited route.
- Container RSS and CPU at idle and under the benchmark.
- Two-worker counter sharing.

Acceptance: no functional errors, and p95 latency within 10% of the Redis 7.2
baseline on the same host. A performance win is not required; compatibility is.

## Licence and documentation

If Valkey is adopted:

- update `versions.yaml` (`runtime.redis` -> Valkey pin and status);
- update `platform/docker-compose.prod.yml` image, command, and health check;
- update `README.md`, `LICENSING.md`, `THIRD_PARTY_NOTICES.md`, and the
  deployment manual;
- add the Valkey BSD-3-Clause notice and keep the Redis trademark note;
- update `docs/SUPPLY-CHAIN.md` and the supply-chain lock;
- record the image digest in `versions.yaml` and the release notes.

If Redis 7.2 is retained:

- record the failed gate and the reason in this document;
- keep the Redis 7.2 pin and do not move to Redis 7.4+ without a licence
  review.

## Phases

| Phase | Work | Exit criterion |
| --- | --- | --- |
| 0. Prep | Confirm 26.04 runner, read Valkey 9.1 notes, capture Redis baseline | Baseline report committed |
| 1. CI matrix | Add store matrix and probe script | Four matrix cells green |
| 2. Local/dev | Run Compose override on dev, exercise rate limits | Functional checks pass |
| 3. Host drill | 26.04 VM: Docker, nftables, WireGuard, KVM, reboot, restore | Host gates pass |
| 4. Decision | Weigh compatibility, licence, performance, support | ADR accepted |
| 5. Release | Pin, docs, supply chain, dev then prod | `/api/version` and store health verified |

## Acceptance criteria

- All backend tests pass with Valkey 9.1.3.
- Rate-limit counters are shared across backend workers and survive backend
  restarts.
- `429` responses and window expiry behave identically to Redis 7.2.
- No new errors or warnings in backend, store, or proxy logs.
- Health checks pass with the Valkey image.
- Trivy, CodeQL, Quality, and supply-chain checks are green.
- Ubuntu 26.04 host gates pass, including reboot and restore.
- Licence and notice files are updated before the pin changes.

## Rollback

The store holds only counters. Rollback is:

1. Set the Compose image back to `redis:7.2-alpine` and the original command.
2. Restore the original health check.
3. Recreate only the store and backend containers.
4. Confirm `/health` and a rate-limited route.

No database migration or learner-data rollback is involved.
