# Local development

This page gets the platform running from a clean checkout. It assumes Docker
Desktop or Docker Engine with Compose v2.

## Prerequisites

| Tool | Version | Why |
|---|---|---|
| Git | any current | clone and branch |
| Docker Engine / Desktop | 24+ | containers |
| Docker Compose | v2 | orchestration |
| Java 17+ | only for the Karate security suite | blackbox tests |
| Python 3.13 | only for host-side scripts | validation and generation |
| Node.js 22 | only for frontend work outside Docker | Vite dev server |

You do not need Python or Node on the host to run the full stack; both are in
the images. You do need them for the fastest edit/test loop.

## 1. Clone and prepare

```bash
git clone https://github.com/RobChaykoski/opencyberrange.git opencyberrange
cd opencyberrange/platform
cp .env.example .env
chmod 600 .env
```

Generate the required secrets:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"   # JWT_SECRET, SETUP_TOKEN, WG_API_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(24))" # POSTGRES_PASSWORD
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" # WG_ENCRYPTION_KEY
```

Fill at least these values in `platform/.env`:

| Variable | Local value |
|---|---|
| `JWT_SECRET` | fresh 64-char hex |
| `SETUP_TOKEN` | fresh one-time token |
| `POSTGRES_PASSWORD` | fresh password |
| `DATABASE_URL` | `postgresql://labuser:<password>@db:5432/labdb` |
| `SERVER_PUBLIC_HOST` | `localhost` or your LAN address |
| `CORS_ORIGINS` | `https://localhost,http://localhost` |
| `LABS_HOST_PATH` | absolute path to `platform/labs`, e.g. `/home/you/opencyberrange/platform/labs` |
| `RATELIMIT_STORAGE_URI` | `redis://redis:6379/0` |
| `WG_ENCRYPTION_KEY` | the generated Fernet key |
| `WG_SERVER_ENDPOINT` | your host IP:51820, or a placeholder if VPN is not used |

`LABS_HOST_PATH` must be absolute. An empty value mounts `:/labs:ro` and lab
discovery fails.

## 2. Start the stack

Use the development compose file, which bind-mounts the backend and frontend
source:

```bash
cd platform
docker compose --env-file .env -f docker-compose.dev.yml up -d --build
docker compose --env-file .env -f docker-compose.dev.yml ps
```

For a production-like local run, use `docker-compose.prod.yml` instead. Do not
mix the two files in one project.

Wait for `ocr-db`, `ocr-valkey`, `ocr-backend`, and `ocr-frontend` to report
healthy. The backend is reachable only on loopback:

```bash
curl -fsS http://127.0.0.1:8000/health
```

Expected: `{"status":"healthy","database":"up"}`.

Open `https://localhost` (accept the self-signed certificate) or `http://localhost`
if TLS is not configured. The first visit shows the setup wizard. Use the
`SETUP_TOKEN` from `.env` to create the first administrator.

Remove `SETUP_TOKEN` after setup and restart the backend.

## 3. Seed curriculum, labs, and an example course

`init_platform.py` is idempotent and runs the correct order:

```bash
docker compose --env-file .env -f docker-compose.dev.yml exec -T backend \
  python /app/app/scripts/init_platform.py
```

It seeds tracks and levels, discovers every `lab.yaml` from `/labs`, creates the
example course shell, and seeds default achievements. It does **not** create
user accounts.

Re-run discovery after adding or changing a lab:

```bash
docker compose --env-file .env -f docker-compose.dev.yml exec -T backend \
  python /app/app/scripts/discover_labs.py
```

## 4. Frontend hot reload

The development compose file runs the Vite dev server in the frontend
container. If you prefer to run it on the host:

```bash
cd platform/frontend
npm ci
npm run dev
```

Vite proxies `/api` to `http://backend:8000`, which only resolves inside the
Compose network. For host development, either add a hosts entry, change the
proxy target to `http://127.0.0.1:8000`, or run the frontend in Compose. The
supported path is the Compose dev service.

## 5. Backend hot reload

The dev compose file bind-mounts `platform/backend` into `/app` and starts
Uvicorn with reload. Edit a router or service and watch the container log:

```bash
docker compose --env-file .env -f docker-compose.dev.yml logs -f backend
```

If you run the backend directly on the host, create a virtual environment and
set `DATABASE_URL`, `JWT_SECRET`, and the other required variables from `.env`.
The supported path is the container.

## 6. Sample data and fixtures

All fixtures below are **development/test only**. Never run them against
production.

| Fixture | Purpose | Command |
|---|---|---|
| `init_platform.py` | curriculum, labs, example course, achievements | see above |
| `seed_demo_class.py` | demo instructor, six students, course, enrolments | `docker compose exec -e DEMO_INSTRUCTOR_PASSWORD=... -e DEMO_STUDENT_PASSWORD=... backend python /app/app/scripts/seed_demo_class.py` |
| `seed_feature_test_data.py` | feature-flag and UI test data | `docker compose exec backend python /app/app/scripts/seed_feature_test_data.py` |
| `seed_analytics_demo.py` | analytics and reporting baseline | `docker compose exec backend python /app/app/scripts/seed_analytics_demo.py` |
| `seed_dna_fixtures.py` | Cyber DNA evidence and consent fixtures | `docker exec -w /app -e PYTHONPATH=/app ocr-backend python -m app.scripts.seed_dna_fixtures --purge-non-consenting` |
| `seed_quizzes.py` / `seed_level_quizzes.py` | quiz banks and level checks | `docker compose exec backend python /app/app/scripts/seed_quizzes.py` |
| `seed_devfest_competition.py` | event competition data | `docker compose exec backend python /app/app/scripts/seed_devfest_competition.py` |
| `simulate_student.py` | synthetic learner activity | `docker compose exec backend python /app/app/scripts/simulate_student.py` |

`seed_demo_class.py` requires `DEMO_INSTRUCTOR_PASSWORD` and
`DEMO_STUDENT_PASSWORD`; it never prints them.

## 7. Persistent data in development

| Volume | Contents |
|---|---|
| `platform_postgres_data` | PostgreSQL data |
| `platform_workbook_data` | Exercise Studio state and the erasure ledger |
| `platform_wiki_data` | Built MkDocs workbook |
| `platform_backups_data` | Database snapshots |

Reset a development database completely:

```bash
cd platform
docker compose --env-file .env -f docker-compose.dev.yml down
docker volume rm platform_postgres_data platform_workbook_data platform_wiki_data
docker compose --env-file .env -f docker-compose.dev.yml up -d
```

This is destructive. Never do it on a host with data you need.

## 8. Build the workbook wiki

```bash
cd platform
docker compose --env-file .env -f docker-compose.dev.yml --profile tools \
  run --rm wiki-builder
```

The output is written to `wiki_data` and served read-only by nginx at `/wiki`.

## 9. Common local failures

| Symptom | Cause | Fix |
|---|---|---|
| `LABS_HOST_PATH` empty or relative | Compose mounted `:/labs` | set an absolute path and recreate backend |
| Backend cannot reach database | `.env` password and `DATABASE_URL` differ | make them match, recreate db and backend |
| Frontend loads but API calls 502 | backend unhealthy | check backend logs and `/health` |
| Setup wizard says invalid token | `SETUP_TOKEN` changed after first run | use the current value or clear it on a fresh DB |
| JSON rates behave inconsistently | `RATELIMIT_STORAGE_URI=memory://` with multiple workers | use `redis://redis:6379/0` |
| Lab will not start | missing image or Docker proxy | prebuild images, check proxy and `OCR_DOCKER_PROXY_EXEC` |
| Self-signed certificate warning | expected on LAN | accept once; do not disable TLS verification globally |

## Where to go next

- [Testing and quality gates](testing-and-quality-gates.md)
- [Deployment](deployment/subsystem-overview.md)
- [Backend features](backend/features/README.md)
- [Database fixtures](database/fixtures.md)
