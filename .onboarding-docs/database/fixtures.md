# Fixtures

Fixtures are development and test data. Never run a development seed against
production.

## Seed order

`init_platform.py` is the supported, idempotent entry point:

```bash
cd platform
docker compose --env-file .env -f docker-compose.dev.yml exec -T backend \
  python /app/app/scripts/init_platform.py
```

It runs:

1. `seed_curriculum.py` — tracks and levels.
2. `discover_labs.py` — register every `lab.yaml`.
3. `seed_example_course.py` — example course shell.
4. `seed_achievements.py` — default achievements.

## Additional development fixtures

| Script | Data | Safety |
|---|---|---|
| `seed_demo_class.py` | instructor, six students, demo course | development only; requires demo passwords |
| `seed_feature_test_data.py` | feature-flag and UI data | development only |
| `seed_analytics_demo.py` | analytics baseline | development only |
| `seed_dna_fixtures.py` | DNA evidence and consent | development only; can purge non-consenting DNA |
| `seed_quizzes.py` | quiz banks | idempotent where implemented |
| `seed_level_quizzes.py` | level checks | idempotent where implemented |
| `seed_devfest_competition.py` | event competition | development only |
| `seed_sso_demo.py` | SSO test users | only with the `sso` profile |
| `simulate_student.py` | synthetic activity | development only |
| `seed_prebuilt_class.py` | prebuilt class | development only |

Example:

```bash
docker compose --env-file .env -f docker-compose.dev.yml exec \
  -e DEMO_INSTRUCTOR_PASSWORD=... -e DEMO_STUDENT_PASSWORD=... \
  backend python /app/app/scripts/seed_demo_class.py
```

## Test fixtures

The pytest suite creates its own users and courses through SQLAlchemy fixtures.
It never touches the live `ocr-db`. Set `TEST_DATABASE_URL` to a disposable
PostgreSQL:

```bash
export TEST_DATABASE_URL="postgresql://ocr_test:ocr_test@127.0.0.1:5432/ocr_test"
cd platform/backend
python -m pytest -q
```

When the variable is unset, DB-backed tests skip cleanly.

## Reset a development database

```bash
cd platform
docker compose --env-file .env -f docker-compose.dev.yml down
docker volume rm platform_postgres_data platform_workbook_data platform_wiki_data
docker compose --env-file .env -f docker-compose.dev.yml up -d
```

This is destructive. Never run it on a host with data you need.

## Adding a fixture

- Make it idempotent.
- Require an explicit environment password; never hard-code one.
- Print no secret.
- Keep it in `app/scripts/` and document it here.
- Do not import it into production startup.

## Related

- [Local development](../local-development.md)
- [Database overview](subsystem-overview.md)
- [Seed example course](../../platform/backend/app/scripts/seed_example_course.py)
