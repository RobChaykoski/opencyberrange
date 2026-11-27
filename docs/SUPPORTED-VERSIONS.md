# Supported Versions

This file records the platform baseline, the target for the latest-supported-GA
upgrade, and the reason for every exception. It is the human-readable companion
to `versions.yaml`.

Last reviewed: **2026-11-27**. Current **platform release: 5.58.0**. Development and production are on the
signed `v5.58.0` tag. **Community /
Academic**, **Professional**, and **Enterprise** are edition profiles on that
release, not separate platform version lines. **Community / Academic 1.1.3**
remains a supported maintenance line for existing single-host installations. See
[Editions](EDITIONS.md), [Release tags](RELEASES.md), and
[ADR 0004](decisions/0004-single-platform-release-version.md). The execution
order for majors is in [Upgrade waves](UPGRADE-WAVES.md).

The separate HA control-plane repository has its own version and is described by
compatibility with platform Release 5.37.0. Enterprise ships OIDC, SAML, and
LDAP single sign-on; multi-tenancy, LTI, and the per-student accommodation
engine remain post-5.36 candidates.

Host baseline: **Ubuntu 24.04 LTS is certified.** See [OS-SUPPORT.md](OS-SUPPORT.md)
and [V2-24.04-BUILD-OUT.md](V2-24.04-BUILD-OUT.md). Ubuntu 22.04 remains the
compatibility path for existing 1.1.x deployments.

Valkey **9.1.3** is the current rate-limit store for both deployments. Ubuntu
26.04 LTS remains a **test candidate** until it passes its promotion gates;
production remains Ubuntu 24.04 LTS. See the
[Ubuntu 26.04 Valkey vs Redis test plan](UBUNTU-26.04-VALKEY-REDIS-TEST-PLAN.md).

Dependency audit on **2026-11-13**: `npm audit` reported **0 vulnerabilities**
and `pip-audit -r platform/backend/requirements.txt` reported **no known
vulnerabilities**. The Release 4 dependency pass updated pytest 9.2.0, httpx
0.28.1, pymdown-extensions 13.0, matplotlib >=3.11.2, pywinrm >=0.5.0,
upload-artifact v7, build-push-action v7, and setup-buildx-action v4. Earlier
safe updates included FastAPI 0.162.2, SQLAlchemy 2.1.8, Pydantic 2.14.3, and
psycopg 3.3.8. The frontend majors were then upgraded: Vue Router 5.4.0,
ESLint 10.14.0, `@eslint/js` 10.0.1, `eslint-plugin-vue` 10.12.0, and
`vue-eslint-parser` 10.4.2. Release 4 adds `ldap3==2.9.1` and
`python3-saml==1.16.0`. The optional SSO test stack adds
Dex v2.42.0 and osixia/openldap 1.5.0; both are profile-gated and are not
started unless `--profile sso` is requested.

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
| Host OS | Community / Academic profile: Ubuntu 22.04 and 24.04 LTS; Professional and Enterprise profiles: Ubuntu 24.04 LTS | 24.04 for Professional/Enterprise profiles | Validation in progress | Community / Academic supports both LTS releases; the Professional profile is deployed and KVM ready, with network/VPN and recovery gates remaining; Enterprise inherits the Professional baseline. See [Host OS support](OS-SUPPORT.md) and the [24.04 build-out plan](V2-24.04-BUILD-OUT.md) |
| Python | 3.13 | 3.14 | 3.13 current; 3.14 evaluation | Check wheel availability before the 3.13 security window |
| Node.js | 22 LTS | 24 LTS | Compatibility testing | Build-only change; runtime stays on the pinned nginx digest |
| PostgreSQL | 15 | 17 | Planned major upgrade | Separate deployment, dump/restore, RLS and trigger verification |
| Valkey | 9.1.3 | 9.1.3 | Supported | Shared rate-limit counters; no persistence |
| Backend base | `python:3.13-slim` (digest pinned) | 3.13 slim digest | Applied in Wave 1 | CI runs the same minor |
| Frontend builder | `node:22-alpine` | Pin a digest | Applied in Wave C | Required by Vite 8 |
| Frontend server | `nginx:alpine` (digest pinned) | Pin a supported stable digest | Applied | Verify nginx config compatibility |

## Backend dependencies

| Component | Current | Planned wave | Notes |
|---|---|---|---|
| FastAPI | 0.162.2 (Starlette 1.10) | Wave C (done) | |
| Uvicorn | 0.54.0 | Wave C (done) | |
| Pydantic | 2.14.3 | Wave C (done) | |
| python-multipart | 0.0.33 | Wave A (done) | |
| slowapi | 0.1.10 | Wave A (done) | Verified on Starlette 1.x |
| cryptography | 50.0.2 | Wave A (done) | Fernet and JWT tested |
| PyJWT | 2.15.1 | Wave B (done) | Replaced python-jose |
| pwdlib + bcrypt | 0.3.1 + 5.0.0 | Wave B (done) | Argon2id; legacy bcrypt rehashed on login |
| SQLAlchemy | 2.1.8 | Wave C (done) | |
| Alembic | 1.20.1 | Wave C (done) | |
| psycopg (v3) | 3.3.8 | Wave C (done) | SQLAlchemy 2.1 defaults to psycopg3 |
| docker SDK | 7.2.0 | Wave C (done) | |
| aiohttp / requests | 3.14.5 / 2.34.2 | Wave A (done) | |
| APScheduler | 3.11.3 | 4 | Stay on 3.x unless 4.x is justified |
| fpdf2 / matplotlib / qrcode | 2.9.0 / >=3.11.2 / 8.2 | Wave A/C (done) | Transcript, charts, QR |

## Frontend dependencies

The lockfile is newer than the declared ranges. The locked versions are the
baseline; Wave 5 updates the runtime and Wave 1 updates the toolchain.

| Component | Locked | Planned wave | Notes |
|---|---|---|---|
| Vue | 3.5.45 | 3.5 patch line | |
| Vue Router | 5.4.0 | Wave 1 (done) | Applied with the 2.4.1 frontend upgrade |
| Axios | 1.21.0 | Wave A (done) | |
| Chart.js / vue-chartjs | 4.6.1 / 5.3.4 | 5 | |
| marked | 18.1.3 | Wave A (done) | |
| DOMPurify | 3.4.17 | Wave A (done) | Keep sanitisation tests |
| noVNC | 1.7.0 | Wave C (done) | Required for Vite 8 (Rolldown); legacy RangeBox viewer |
| KasmVNC | 1.5.2 | 5.13 | RangeBox Kali/Ubuntu/REMnux transport and vendored browser client; GPL-2.0 |
| sortablejs | 1.15.7 | 5 | |
| Vite | 8.3.6 | Wave C (done) | Rolldown; Node 22+ |
| @vitejs/plugin-vue | 6.0.10 | Wave C (done) | Pairs with Vite 8 |
| ESLint / plugin-vue | 10.14.0 / 10.12.0 | Wave 1 (done) | ESLint 10 flat config; vue-eslint-parser 10.4.2 |
| globals | 17.14.0 | 1 | |

## Infrastructure, docs, and CI

| Component | Current | Target | Notes |
|---|---|---|---|
| PostgreSQL image | `postgres:15-alpine` | `postgres:17-alpine` digest | Wave 6 |
| MkDocs | 1.6.1 | Newest compatible 1.x | Do not move to 2.0 until Material supports it |
| Material for MkDocs | 9.8.0 | Newest 9.x | |
| pymdown-extensions | 13.0 | Newest compatible | Required by Material 9.8 |
| CodeQL action | v4 | Current major | Renovate |
| Trivy action | 0.36.0 | Current | Renovate |
| checkout action | v7 | Current major | Renovate |

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

See [UPGRADE-TO-LATEST-GA-PLAN.md](archive/UPGRADE-TO-LATEST-GA-PLAN.md) for the full
wave plan, gates, and rollback procedure.
