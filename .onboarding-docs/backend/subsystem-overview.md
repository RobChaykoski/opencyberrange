# Backend subsystem

The backend is a FastAPI application that owns authentication, authorization,
courses, labs, sessions, scoring, analytics, consent, competency evidence, and
administrative operations. It also orchestrates lab containers and the
scheduler.

## Folder map

```text
platform/backend/
├── app/
│   ├── main.py              app factory, middleware, router mounts, startup seeds
│   ├── auth.py              JWT, password hashing, current-user dependencies
│   ├── database.py          engine, session factory, dependencies
│   ├── config.py            pydantic settings from environment
│   ├── models/              SQLAlchemy models by domain
│   ├── schemas/             Pydantic request/response models
│   ├── routers/             HTTP endpoints by domain
│   ├── services/            domain logic and integrations
│   ├── security/            permissions, tenant, route audit, dependencies
│   ├── consent/             consent middleware, registry, service, router
│   ├── cyber_dna/           DNA bounded context
│   ├── modules/             optional/devtool modules mounted after core routers
│   ├── data/                curriculum, competency, NICE, rubrics, datasets
│   └── scripts/             seed, discovery, backfill, simulation scripts
├── alembic/                 migrations
├── tests/                   pytest suite
├── Dockerfile
├── requirements.txt
└── pytest.ini
```

## Request lifecycle

1. nginx forwards `/api/*` to Uvicorn on `127.0.0.1:8000`.
2. Starlette middleware: request id, security events, consent enforcement,
   impersonation, export labels, CORS.
3. FastAPI dependency resolution: `get_current_user`, active/approved checks,
   role or permission dependency, tenant context.
4. Router validates input with Pydantic, calls a service, and serialises a
   response schema.
5. SQLAlchemy session commits; the integrity ledger trigger records instrumented
   changes.
6. The response returns through nginx.

## Major components

| Component | Router | Service / model |
|---|---|---|
| Login and tokens | `routers/auth.py` | `auth.py`, `services/auth_sessions.py`, `services/reauth.py` |
| Registration and approval | `routers/auth.py`, `routers/admin.py` | `services/input_safety.py`, `models/auth.py` |
| Roles, permissions, tenancy | `routers/admin.py`, `security_admin.py` | `services/rbac.py`, `services/authorization.py`, `security/` |
| Courses and enrolment | `routers/courses.py` | `services/course_planning.py`, `models/course.py` |
| Labs and sessions | `routers/labs.py`, `rangebox.py` | `services/docker_manager.py`, `lab_preflight.py`, `models/lab.py` |
| Flags and scoring | `routers/labs.py` | `models/lab.py`, `services/achievements.py` |
| Quizzes and practice | `routers/quiz.py`, `exercise_quiz.py`, `question_bank.py` | `services/certification_quiz.py`, `services/practice.py` |
| Analytics and reports | `routers/analytics.py`, `dashboard.py`, `instructor.py`, `reports.py` | `services/analytics_report.py`, `pdf_report.py`, `report_integrity.py` |
| Competency and evidence | `routers/evidence.py`, `competency_reviews.py` | `services/competency_*`, `evidence*`, `models/evidence.py` |
| Consent and privacy | `consent/`, `routers/auth.py` | `services/erasure.py`, `erasure_ledger.py`, `privacy.py` |
| Cyber DNA and GPS | `cyber_dna/`, `routers/profile.py` | `services/cyber_gps.py`, `skill_dna.py` |
| SSO and LTI | `routers/sso.py`, `lti.py` | `services/oidc.py`, `saml_auth.py`, `ldap_auth.py`, `lti.py` |
| Admin and governance | `routers/admin.py`, `governance.py`, `audit.py` | `services/audit.py`, `security_events.py`, `system_metrics.py` |
| Uploads and workbook | `routers/workbook.py`, `instructor.py`, `admin.py` | `services/workbook_builder.py`, `lab_upload.py`, `exercise_transfer.py` |

## Configuration

All configuration is environment-driven through `app/config.py`. Never hard-code
secrets. The required production variables are in
[`platform/.env.example`](../../platform/.env.example). The most important:

```text
DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, REPORT_SIGNING_KEY
DOCKER_HOST, LABS_HOST_PATH, WG_*
OCR_UVICORN_WORKERS, DB_POOL_SIZE, DB_MAX_OVERFLOW
RATELIMIT_STORAGE_URI
CORS_ORIGINS, PUBLIC_BASE_URL, SERVER_PUBLIC_HOST
ENVIRONMENT, OCR_DEPLOYMENT_MODE, OCR_AUTHZ_STRICT
```

## Run

```bash
cd platform
docker compose --env-file .env -f docker-compose.dev.yml up -d --build backend
docker compose --env-file .env -f docker-compose.dev.yml logs -f backend
```

Direct host run is possible but not the supported path. The container has the
correct Python version, dependencies, mounts, and environment.

## Test

```bash
cd platform/backend
python -m pytest -q
```

See [Testing and quality gates](../testing-and-quality-gates.md) for the
database-backed setup and focused suites.

## Persistent storage

The backend owns no local database file. It writes to:

- PostgreSQL through SQLAlchemy;
- `workbook_data` for Exercise Studio and erasure/suppression proof;
- `backups_data` for snapshots;
- `/labs` read-only for lab definitions;
- Docker through the socket proxy for lab containers.

## Feature pages

Start at [backend features](features/README.md). Each page names the router,
services, models, endpoints, storage, fixtures, and extension points.

## Design rules

- Routers stay thin; domain logic belongs in `services/`.
- Authorization is a dependency, not a branch inside the handler.
- Consent is enforced in middleware, with route checks as defence in depth.
- Every protected route has an auth or permission dependency; `OCR_AUTHZ_STRICT`
  enforces it at startup.
- Tenant scope comes from the session, never from a client-supplied header.
- Learner data leaves only through labelled, scoped exports.
- Generated data files are regenerated by scripts.

## Related

- [Backend architecture diagram](subsystem-technical-architecture-diagram.md)
- [API error codes](../../docs/API-ERROR-CODES.md)
- [Auth lifecycle](../../docs/AUTH-LIFECYCLE.md)
- [Authorization service](../../docs/AUTHORIZATION-SERVICE.md)
- [Database integrity](../../docs/DATABASE-INTEGRITY.md)
