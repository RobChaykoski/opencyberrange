# Supported Versions

This file records the platform baseline, the target for the latest-supported-GA
upgrade, and the reason for every exception. It is the human-readable companion
to `versions.yaml`.

Last reviewed: **2026-11-01**.

## Policy

- Target the newest **stable, generally available** release that is still
  supported upstream and compatible with the rest of the stack.
- Do not use alpha, beta, release-candidate, nightly, or `-rolling` tags for
  platform services. `kalilinux/kali-rolling` remains the deliberate RangeBox
  exception.
- Prefer the latest patch/minor in a supported major. Move majors one wave at a
  time.
- Pin exact versions and image digests for platform services.
- Do not upgrade intentionally vulnerable lab software.
- Every exception needs an owner, a reason, and an expiry/review date.

## Platform runtime

| Component | Current | Target | Status | Notes |
|---|---|---|---|---|
| Python | 3.11 | 3.13 | Compatibility testing | Re-evaluate 3.14 after Wave 0/2 wheels |
| Node.js | 18 (EOL) | 22 LTS | Compatibility testing | Re-evaluate 24 LTS after Wave 0 |
| PostgreSQL | 15 | 17 | Planned major upgrade | Separate deployment, dump/restore |
| Backend base | `python:3.11-slim` | Pin a 3.13 slim digest | Wave 1 | Check psycopg2/cryptography/matplotlib wheels |
| Frontend builder | `node:18-alpine` | `node:22-alpine` | Wave 1 | Required before Vite major |
| Frontend server | `nginx:alpine` | Pin a supported stable digest | Wave 1 | Verify nginx config compatibility |

## Backend dependencies

| Component | Current | Planned wave | Notes |
|---|---|---|---|
| FastAPI | 0.109.0 | 2 | Upgrade with Starlette/Pydantic |
| Uvicorn | 0.27.0 | 2 | |
| Pydantic | 2.5.3 | 2 | Validate models/OpenAPI |
| python-multipart | 0.0.6 | 2 | Security-relevant |
| slowapi | 0.1.9 | 2 | Check Starlette compatibility |
| cryptography | 41.0.7 | 3 | Test Fernet and JWT |
| python-jose | 3.3.0 | 3 | Decide PyJWT vs maintained fork |
| passlib + bcrypt | 1.7.4 + 4.0.1 | 3 | Highest risk: passlib is unmaintained |
| SQLAlchemy | 2.0.25 | 3 | |
| Alembic | 1.13.1 | 3 | Migrate against a restore |
| psycopg2-binary | 2.9.9 | 3 | Evaluate psycopg 3 separately |
| docker SDK | 6.1.3 | 4 | Test against the host engine |
| aiohttp / requests | 3.9.3 / 2.31.0 | 4 | |
| APScheduler | 3.10.4 | 4 | Stay on 3.x unless 4.x is justified |
| fpdf2 / matplotlib / qrcode | 2.7.9 / >=3.10 / 7.4.2 | 4 | Transcript, charts, QR |

## Frontend dependencies

The lockfile is newer than the declared ranges. The locked versions are the
baseline; Wave 5 updates the runtime and Wave 1 updates the toolchain.

| Component | Locked | Planned wave | Notes |
|---|---|---|---|
| Vue | 3.5.30 | 5 | |
| Vue Router | 4.6.4 | 5 | |
| Axios | 1.13.6 | 5 | |
| Chart.js / vue-chartjs | 4.5.1 / 5.3.3 | 5 | |
| marked | 17.0.5 | 5 | |
| DOMPurify | 3.3.3 | 5 | Keep sanitisation tests |
| noVNC | 1.6.0 | 5 | Smoke-test the console |
| sortablejs | 1.15.7 | 5 | |
| Vite | 5.4.21 | 1 | Vite 6/7 needs Node 22+ and plugin major |
| @vitejs/plugin-vue | 4.6.2 | 1 | Pair with Vite |
| ESLint / plugin-vue | 9.39.5 / 9.33.0 | 1 | ESLint 9 flat config |
| globals | 15.15.0 | 1 | |

## Infrastructure, docs, and CI

| Component | Current | Target | Notes |
|---|---|---|---|
| PostgreSQL image | `postgres:15-alpine` | `postgres:17-alpine` digest | Wave 6 |
| MkDocs | 1.6.1 | Newest compatible 1.x | Do not move to 2.0 until Material supports it |
| Material for MkDocs | 9.7.4 | Newest 9.x | |
| pymdown-extensions | 10.8 | Newest compatible | |
| CodeQL action | v3 | Current major | Renovate |
| Trivy action | 0.28.0 | Current | Renovate |
| checkout action | v4 | Current major | Renovate |

## Out of scope

The following remain on their current bases in this programme:

- `platform/labs/**` — including ~148 Ubuntu 22.04 images, Alpine 3.18/3.19,
  PHP 8.1, MySQL 8.0, and Python 3.11 mock services.
- `RangeBox/**`, `UbuntuBox/**`, `RemnuxBox/**`.

Some of those pins are intentionally vulnerable. They need a separate lab
upgrade programme with per-lab solve tests.

## Exceptions and review

| Exception | Reason | Review |
|---|---|---|
| Kali rolling in RangeBox | Rolling is the intended upstream channel | Each RangeBox rebuild |
| Frozen lab service versions | Intentionally vulnerable exercise targets | Separate lab programme |
| MkDocs 1.x | MkDocs 2.0 is incompatible with Material | When Material supports 2.x |
| APScheduler 3.x | 4.x is a major API rewrite | Revisit after platform waves |

See [UPGRADE-TO-LATEST-GA-PLAN.md](UPGRADE-TO-LATEST-GA-PLAN.md) for the full
wave plan, gates, and rollback procedure.
