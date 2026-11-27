# Software metadata and versions

Status: **current for release 5.57.0** (26 November 2026).

Latest-version checks were made on 26 November 2026 from PyPI, the npm
registry, GitHub releases, and endoflife.date. "Latest available" is the
newest upstream release observed at that time, not an instruction to upgrade.
The platform policy prefers the latest supported patch/minor within a tested
major line; major upgrades need their own wave.

## Product identity

| Item | Value |
|---|---|
| Product | SWOCTS Cyber Range (powered by OpenCyberRange) |
| Release | `5.57.0` |
| Latest signed release | `v5.57.0` (current) |
| Signed tag | `v5.57.0` |
| Release date | 26 November 2026 |
| Edition profile | Community / Academic (`lite`, single-host) |
| Licence | PolyForm Noncommercial License 1.0.0 |
| Repository | `RobChaykoski/opencyberrange` |
| API contract | [openapi.json](openapi.json) — OpenAPI 3.1.0, 490 paths, 548 operations |
| API capability index | [API-CAPABILITIES.md](API-CAPABILITIES.md) |
| Data dictionary | [DATA-DICTIONARY.md](DATA-DICTIONARY.md) |

## Runtime and infrastructure

| Component | Role | Current / pinned | Latest available | Source / note |
|---|---|---|---|---|
| Host OS | Platform host | Ubuntu 24.04.5 LTS | Ubuntu 26.04.1 LTS (26.04 LTS) | endoflife.date; 26.10 is current non-LTS |
| Python | Backend runtime | 3.13.18 | 3.15.2 | endoflife.date; 3.14.10 is the evaluation target |
| Node.js | Frontend build stage | 22 (pinned `node:22-alpine` digest) | 24.22.3 LTS; 26.13.1 current | endoflife.date; production runtime is nginx |
| PostgreSQL | Primary database | 15.19 | 19.0 | endoflife.date; 17.12 is the planned target |
| Valkey | Rate-limit cache | 9.1.3 | 9.2.1 | GitHub release; BSD-3-Clause |
| nginx | Edge, TLS, SPA, API proxy, wiki | 1.31.8 | 1.31.10 | `nginx -v`; `nginx:alpine` pinned by digest |
| Docker Engine | Container runtime | 29.10.0 | 29.10.1 | GitHub release |
| Docker Compose | Stack orchestration | 5.8.0 | 5.8.0 | GitHub release |
| MkDocs | Workbook/wiki build | pinned by `ocr-wiki-builder` | `mkdocs==1.6.1` in builder | Builder image |
| Material for MkDocs | Wiki theme | pinned by builder | 9.8.0 | Builder image |

## Backend dependencies

| Package | Pinned | Latest available | Notes |
|---|---:|---:|---|
| FastAPI | 0.165.0 | 0.165.0 | API framework |
| Uvicorn | 0.54.0 | 0.54.0 | ASGI server |
| SQLAlchemy | 2.1.9 | 2.1.9 | ORM / SQL |
| Alembic | 1.20.1 | 1.20.1 | Migrations |
| Pydantic | 2.14.4 | 2.14.4 | Validation |
| pydantic-settings | 2.16.3 | 2.16.3 | Settings |
| psycopg | 3.3.9 | 3.3.9 | PostgreSQL driver |
| PyJWT | 2.15.1 | 2.15.1 | JWT |
| cryptography | 50.0.2 | 50.0.2 | Crypto primitives |
| docker (SDK) | 7.2.0 | 7.2.0 | Docker API client |
| APScheduler | 3.11.3 | 3.11.3 | Scheduler |
| slowapi | 0.1.10 | 0.1.10 | Rate limiting |
| redis | 8.2.0 | 8.2.0 | Valkey-compatible client |
| fpdf2 | 2.9.0 | 2.9.0 | PDF reports |
| matplotlib | 3.11.2 | 3.11.2 | Report plots |
| aiohttp | 3.14.5 | 3.14.5 | WebSocket proxy |
| requests | 2.34.2 | 2.34.2 | Outbound HTTP |
| python-multipart | 0.0.33 | 0.0.34 | Uploads |
| email-validator | 2.3.0 | 2.4.0 | Email validation |
| PyYAML | 6.0.3 | 6.0.4 | YAML |
| python-dateutil | 4.0.0 | 4.0.0 | Date parsing |
| qrcode | 8.2 | 8.2 | QR generation |
| ldap3 | 2.9.1 | 2.9.1 | Optional LDAP |
| python3-saml | 1.16.0 | 1.16.0 | Optional SAML |

## Frontend dependencies

| Package | Installed | Latest available | Notes |
|---|---:|---:|---|
| Vue | 3.5.46 | 3.5.46 | SPA framework |
| vue-router | 5.5.1 | 5.5.3 | Routes |
| axios | 1.21.1 | 1.21.1 | API client |
| DOMPurify | 3.5.0 | 3.5.0 | Sanitisation |
| ECharts | 6.1.0 | 6.1.0 | Charts |
| marked | 18.3.0 | 18.3.0 | Markdown |
| SortableJS | 1.15.7 | 1.15.7 | Track reorder |
| @novnc/novnc | 1.7.0 | 1.7.0 | RangeBox desktop |
| Vite | 8.3.8 | 8.4.0 | Build |
| Vitest | 4.1.12 | 5.1.2 | Tests |
| ESLint | 10.15.0 | 10.15.0 | Lint |
| eslint-plugin-vue | 10.12.1 | 10.12.1 | Vue lint |
| @vitejs/plugin-vue | 6.0.11 | 6.0.11 | Vue build |
| @vue/test-utils | 2.6.0 | 2.6.0 | Component tests |
| jsdom | 26.1.0 | 31.0.1 | Test DOM |
| @eslint/js | 10.0.1 | 10.0.1 | ESLint config |
| globals | 17.14.0 | 17.14.0 | ESLint globals |
| vue-eslint-parser | 10.4.2 | 10.4.2 | ESLint parser |

## Images and build inputs

| Image | Current | Latest / note |
|---|---|---|
| `python:3.13-slim` | digest `e48f59cd…` | Python 3.13.18 runtime; 3.15.2 available |
| `node:22-alpine` | digest `1314fb30…` | Node 22 build stage; 24.22.3 LTS available |
| `nginx:alpine` | digest `fed7e14…`, nginx 1.31.8 | 1.31.10 available |
| `postgres:15-alpine` | PostgreSQL 15.19 | 19.0 available; 17.12 planned |
| `valkey/valkey:9.1.3-alpine` | Valkey 9.1.3 | 9.2.1 available |
| `tecnativa/docker-socket-proxy:0.3.0` | pinned | Docker socket proxy |
| `ocr-wiki-builder:latest` | MkDocs 1.6.1 + Material 9.8.0 | Built from `platform/wiki-builder` |
| `osixia/openldap:1.5.0` | optional SSO | Pinned image |
| `ghcr.io/dexidp/dex:v2.42.0` | optional SSO | Pinned image |
| `prom/node-exporter:v1.9.1` | optional monitoring add-on | Pinned digest |

## APIs and integrations

| Surface | Exposure | Authentication | Notes |
|---|---|---|---|
| REST API | `https://<platform-host>/api` | OAuth2 Bearer JWT (SPA); cookie for wiki subrequests | 490 paths / 548 operations in OpenAPI 3.1 |
| OpenAPI schema | `/openapi.json` when enabled | Public read on the API origin | Exported to [openapi.json](openapi.json) |
| RangeBox VNC | WebSocket `/api/rangebox/*` | Single-use WebSocket ticket | OpenAPI does not describe WebSocket handshakes |
| Wiki | `/wiki/*` and `:8443` | `wiki_session` HttpOnly cookie, nginx auth subrequest | Read-only MkDocs output |
| WireGuard | UDP `51820` | Per-user peer key | `/32` client, learner `/24` route |
| LTI 1.3 | `/api/lti/*` | Signed launch, AGS/NRPS OAuth | Optional LMS integration |
| OIDC/SAML/LDAP | Browser + backend | Provider configuration, encrypted secrets | Optional institutional SSO |
| SMTP | Backend outbound | Deployment credentials | Password reset and notices |
| HIBP | Backend outbound, optional | Admin opt-in; SHA-1 prefix only | No password or full hash leaves the server |
| GitHub releases | Backend outbound, optional | Public read | Admin release-status comparison |

## Update policy

- Keep runtime and base-image versions pinned.
- Prefer the latest supported patch/minor inside the tested major line.
- Treat PostgreSQL, Python, Node, nginx, and host-OS majors as separate upgrade
  waves with a backup, restore drill, and lab validation.
- Refresh the supply-chain lock and re-sign it after any change to a pinned
  dependency, image, workflow, or covered content file.
- Do not use a vulnerable lab image as a platform runtime dependency; lab images
  are intentionally frozen when the exercise requires old software.

## Sources

- `versions.yaml`
- `platform/backend/requirements.txt`
- `platform/frontend/package-lock.json`
- `platform/backend/Dockerfile`, `platform/frontend/Dockerfile`
- `platform/docker-compose.prod.yml`
- PyPI, npm registry, GitHub releases, and endoflife.date, checked 26 November 2026
