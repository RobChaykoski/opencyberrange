# Task: Backend test-suite completion (router coverage audit + DB-path tests)

## Why
The scaffold is already in place — do NOT rebuild it: `platform/backend/tests/conftest.py` (async client fixture + `db` marker + `TEST_DATABASE_URL`), `pytest.ini`, `requirements-dev.txt` (pytest, pytest-asyncio, httpx), ~97 test files, and CI runs `pytest -q` against a real `postgres:17-alpine` service. What is missing is *guaranteed coverage*: 32 router modules exist and there is no enforced mapping between them and tests, so new endpoints can ship untested.

## Hard rules (do not violate)
1. **Tests must be hermetic.** Every test that touches the database uses the existing `db` marker/fixture pattern from `conftest.py` and cleans up after itself (or relies on the per-test transaction rollback if conftest provides it — read conftest first and follow its contract exactly). No test may depend on execution order or on data left by another test.
2. **No new global state.** Do not add module-level clients, shared DB sessions, or monkeypatched settings that leak across tests.
3. **Assert behavior, not internals.** Assert HTTP status + response JSON shape (field names/types), and for write endpoints assert the persisted effect via a follow-up read through the API — not by poking ORM objects directly unless the endpoint's contract is internal state.
4. **Follow existing test style.** Read 2–3 of the strongest existing test files first (e.g. `tests/test_admin_users.py`, `tests/test_analytics.py`) and match their fixture usage, naming, and assertion style. Consistency beats personal preference.
5. **Style.** `ruff check app tests` clean. No `skip` without a comment explaining why; no commented-out tests left behind.

## Procedure
1. **Audit the mapping.** List all 32 router modules in `app/routers/`: about, accommodations, admin, analytics, audit, auth, competitions, courses, curriculum, curriculum_admin, dashboard, exercise_quiz, exercise_tester, identity, instructor, labs, lti, modules, open_badges, planning, profile, public_config, question_bank, quiz, rangebox, reports, reviews, settings, setup, sso, workbook. For each, list which test files cover it and which endpoints are untested. Produce a gap table (router → endpoint → covered?/missing).
2. **Fill gaps by risk order.** Priority: (a) any write endpoint with no test at all, (b) auth-adjacent routers (auth, sso, identity, admin) — assert both the success path and the 401/403 path, (c) read endpoints that build aggregate data (analytics, reports, dashboard), (d) remaining simple GETs. For each gap add a focused test file `tests/test_<router>_<area>.py` with at minimum: one happy-path test per endpoint group, one unauthorized/unauthenticated test for protected routes.
3. **DB-backed verification.** Every test that writes must run under the `db` marker so it executes against Postgres in CI (and is skipped locally when `TEST_DATABASE_URL` is unset — confirm conftest already does this; if not, add it).
4. **Optional gate (only if trivial):** add `pytest-cov` to `requirements-dev.txt` and a `--cov=app --cov-report=term-missing` line in CI as *informational* (do NOT set a hard `fail_under` threshold yet — record the baseline number in the PR description instead).

## Definition of done
- [ ] Gap table complete; every router has at least one test file, and every write endpoint has at least one DB-backed test.
- [ ] Auth-adjacent routers each have an explicit 401/403 negative test.
- [ ] `pytest -q` green locally with `TEST_DATABASE_URL` set to a local Postgres 17, and green in CI on a pushed branch.
- [ ] `ruff check app tests` clean.

## Commit shape
Group by router domain: e.g. "test(backend): cover instructor + planning routers" — max ~4–5 commits total.
