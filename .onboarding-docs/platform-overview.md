# Platform overview

SWOCTS Cyber Range is a self-hosted teaching platform for hands-on
cybersecurity. It combines a lab runtime, a course and cohort model, a
competency and evidence layer, and an instructor reporting surface. It is built
on the OpenCyberRange codebase and is designed to run on a single Linux host
with Docker Compose.

The platform is not a generic LMS and not a CTF scoreboard. The teaching loop is
the product:

```text
course -> exercise -> lab session -> evidence -> competency -> report
```

## Who uses it

| Persona | What they do |
|---|---|
| Learner | Joins a course, starts an isolated lab, submits a flag or evidence, and builds a transcript |
| Instructor | Authors or assigns exercises, monitors a cohort, reviews evidence, and exports reports |
| Administrator | Manages users, roles, catalogue, sessions, settings, backups, and security events |
| Auditor / privacy officer | Reviews access, consent, retention, and control evidence |
| Operator | Deploys, upgrades, backs up, restores, and monitors the host |
| Developer | Extends the backend, frontend, labs, or integrations |

## What the platform owns

- Lab catalogue, lab sessions, RangeBox desktops, and runtime isolation.
- Courses, enrolment, assignments, learner progress, and submissions.
- Competency contracts, evidence, rubrics, reviews, and readiness signals.
- Instructor analytics, reports, and privacy-safe exports.
- Consent, deletion, suppression, and tenant isolation for its own data.
- SSO, LTI, and identity integration for its own users.

## What it deliberately does not own

- **OpenGRC** is the system of record for governance, risk, compliance, control
  catalogues, and audit evidence. The platform exports aggregate, stable
  evidence; it does not copy the GRC database or send learner rows.
- **OpenDetectionEngine / OpenDLP** own data sources, classifiers, and DLP
  policy.
- **DefectDojo** owns findings, deduplication, and remediation tracking.
- **Authentik / OpenIAM** own operational SSO and identity governance for the
  wider ecosystem.
- Learner data never enters a federation bundle, warehouse, or AI prompt.

See [Ecosystem tooling map](../docs/ECOSYSTEM-TOOLING-MAP.md) for the ownership
split.

## Deployment shape

The supported production shape is **one Linux host running Docker Compose**.
There is no supported split-database or active-active multi-host topology in
Release 5. High availability is an optional, read-only control plane with a
standby database and a witness; it does not change the single-host reference
shape.

| Component | Container | Access |
|---|---|---|
| Edge and SPA | `ocr-frontend` (nginx + built Vue app) | 80/443, 8443 workbook origin |
| API and orchestration | `ocr-backend` (FastAPI + scheduler) | `127.0.0.1:8000` only |
| Database | `ocr-db` (PostgreSQL 15) | internal 5432 |
| Rate-limit store | `ocr-valkey` (Valkey 9.1.3) | internal 6379 |
| Docker control | `ocr-docker-proxy` | internal `docker_control` network |
| Wiki builder | one-shot `wiki-builder` | tools profile, writes `wiki_data` |
| Optional SSO test stack | `ocr-ldap`, `ocr-dex` | `sso` profile |
| Lab targets | per-session containers | isolated per-session bridge |
| RangeBox | per-session desktop container | VNC 6080, proxied by the backend |

The backend is never exposed directly to learners. nginx terminates TLS and
proxies `/api`. The database, Valkey, and Docker socket stay private.

## Hardware and operating system

| Use | CPU | RAM | Disk | Notes |
|---|---:|---:|---:|---|
| Evaluation / a few learners | 4 cores | 8 GB | 50 GB | RangeBox disabled |
| Small class | 4-8 cores | 16 GB | 100 GB | RangeBox enabled |
| Production classroom (20+ concurrent) | 8+ cores | 64 GB | 500 GB | ~200 GB extra for prebuilt lab images |

Host OS baseline:

- **Ubuntu 24.04 LTS** is certified for Professional and Enterprise profiles.
- **Ubuntu 22.04 LTS** remains supported for the Community / Academic profile
  and as an upgrade source.
- **Ubuntu 26.04 LTS** is a test candidate, not production.
- Docker Engine 24+ with the Compose v2 plugin.
- KVM is only needed for KVM-backed labs; most exercises are Docker-only.

Full sizing and connection-budget notes:
[Deployment topology and sizing](../docs/DEPLOYMENT-TOPOLOGY-AND-SIZING.md).

## Software stack

| Layer | Technology | Purpose |
|---|---|---|
| Web app | Vue 3, Vue Router 5, Vite 8, Axios, ECharts, marked + DOMPurify, noVNC | Learner, instructor, and admin UI |
| Edge | nginx (Alpine, digest-pinned) | TLS, SPA, `/api` proxy, wiki origin, security headers |
| API | FastAPI 0.165, Uvicorn 0.54, Pydantic 2.14 | REST API, auth, validation, OpenAPI |
| Data access | SQLAlchemy 2.1, psycopg 3, Alembic 1.20 | ORM, migrations, PostgreSQL access |
| Auth | PyJWT, pwdlib/Argon2id, bcrypt legacy rehash, pyotp | Tokens, password hashing, MFA |
| Background work | APScheduler, Docker SDK, aiohttp/requests | Session expiry, cleanup, lab orchestration |
| Database | PostgreSQL 15 | Transactional system of record |
| Cache | Valkey 9.1.3 | Shared rate-limit counters only, no persistence |
| Lab runtime | Docker Compose projects via socket proxy | Isolated per-session lab networks |
| VPN | WireGuard + Peer Manager | Per-learner `/32` route to a lab `/24` |
| Docs | MkDocs + Material | Manual and workbook publishing |
| Optional SSO | Dex, OpenLDAP, OIDC, SAML 2.0, LDAP/AD | Institution sign-in |
| Reporting | fpdf2, matplotlib | PDF/CSV reports with integrity manifests |
| Monitoring | Prometheus + Grafana on a separate host | Metrics and alerting |

Exact versions and image digests: [`versions.yaml`](../versions.yaml).

## Repository concepts

| Concept | Meaning |
|---|---|
| Track | A curriculum strand such as Windows, Web, Forensics, or Software Security |
| Lab | A directory under `platform/labs/<Track>/<slug>/` with `lab.yaml` and a compose file |
| Exercise | The platform's database record for a lab, with visibility and ordering |
| Session | One learner's running lab instance, on an isolated network |
| RangeBox | A per-session desktop container for browser-accessible tools |
| Course | A cohort with an instructor, invite code, assignments, and retention |
| Competency contract | The evidence types and weights for a lab |
| Evidence record | Append-only proof that a competency was observed |
| Consent domain | A switch that blocks derived features and purges data on revocation |
| Tenant | The institution boundary used by row-level security and policy |

## Non-negotiables

These are design constraints, not preferences. Read the full list in
the workspace bootstrap (`.opencode/bootstrap.md`, outside this repository).

- Signed releases only; no ad-hoc production edits.
- Keep data planes private: backend on loopback, PostgreSQL, Valkey, and Docker
  control internal only.
- Least privilege in the catalogue: visibility and course checks come first.
- Consent wins. A revoked learner's replayed completion writes zero DNA
  evidence.
- No learner rows, secrets, tokens, or live addresses in documentation,
  federation bundles, or AI prompts.
- No employer/recruiter view, public learner ranking, or LLM-only grading.
- Generated files are regenerated, never hand-edited.

## Where to go next

- [Local development](local-development.md)
- [Platform architecture](platform-technical-architecture-diagram.md)
- [Backend](backend/subsystem-overview.md)
- [Frontend](frontend/subsystem-overview.md)
- [Deployment](deployment/subsystem-overview.md)
