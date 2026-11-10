# Demo feature-test data

Status: **development only**
Script: `platform/backend/app/scripts/seed_feature_test_data.py`
Created: 2026-11-08

This seed exists to exercise surveys, feedback, reporting, cohort suppression,
and de-anonymisation controls with realistic volumes. It must never run against
production.

## Safety guard

The script refuses to run unless both conditions are true:

- `--dev` is passed; and
- `OCR_DEMO_SEED_ALLOWED=1` is set.

It also refuses when `OCR_ENV`/`APP_ENV` says production, when
`DEPLOYMENT_MODE` is production, or when `DATABASE_URL` contains `prod`.

Every record uses a `demotest_` or `DEMOTEST-` prefix. `--cleanup` removes only
those records.

## What it creates

| Item | Count / shape |
|---|---|
| Instructors | 3 (`demotest_instructor_01`–`03`) |
| Students | 60 (`demotest_student_01`–`60`) |
| Courses | 6 (`DEMOTEST-A`–`F`) |
| Large cohort | `DEMOTEST-A`, 25 learners |
| Threshold cohort | `DEMOTEST-B`, 5 learners |
| Small cohort | `DEMOTEST-C`, 3 learners |
| No-evidence cohort | `DEMOTEST-D`, 0 learners |
| Struggling cohort | `DEMOTEST-E`, 12 learners |
| Strong cohort | `DEMOTEST-F`, 8 learners |
| Labs | 9 synthetic labs across web, network, and forensics |
| Assignments | 2 per course |
| Completions | Varied completion, attempt, hint, and time profiles |
| Flag attempts | Correct and incorrect attempts |
| Pulse surveys | Difficulty, learning, unclear text, topic interest |
| Reactions | Like/dislike |
| Course feedback | Student check-ins and instructor coaching notes |
| Exercise quizzes | Attempts and post-quiz feedback |
| Survey | 1 survey, attached to the large and small cohorts |
| Consent | `SurveyConsentEvent` opt-ins |
| Achievements | First-blood awards |
| Resets | Course completion resets in threshold/struggling cohorts |
| Competition | 1 sprint with labs and opt-in participants |

## Run

Inside the development backend container:

```bash
docker exec -e OCR_DEMO_SEED_ALLOWED=1 -e PYTHONPATH=/app \
  -e DEMO_FEATURE_PASSWORD='<development password>' ocr-backend \
  python -m app.scripts.seed_feature_test_data --dev --yes
```

Cleanup:

```bash
docker exec -e OCR_DEMO_SEED_ALLOWED=1 -e PYTHONPATH=/app ocr-backend \
  python -m app.scripts.seed_feature_test_data --dev --cleanup --yes
```

`DEMO_FEATURE_PASSWORD` is required for a seed run. The script never prints or
writes the password to disk.

## Verification performed on development

| Check | Result |
|---|---|
| `DEMOTEST-A` overview | `available`, completion 86.0% |
| `DEMOTEST-B` overview | `available` at the 5-learner threshold |
| `DEMOTEST-C` overview | `suppressed`, completion `null`, pulse `null` |
| `DEMOTEST-D` overview | `no_evidence`, metrics `null` |
| `DEMOTEST-E` overview | `available`, completion 4.2% (struggling profile) |
| `DEMOTEST-F` overview | `available`, completion 93.8% (strong profile) |
| `DEMOTEST-C` exercise rows | `suppressed` |
| `DEMOTEST-B` exercise rows | per-exercise `suppressed` where the lab cohort is small |
| `DEMOTEST-C` pulse comments | `comments: []`, `cohort_state: suppressed` |
| Reports overview as admin | `DEMOTEST-C` counted as suppressed; `DEMOTEST-D` as no evidence |
| `DEMOTEST-C` feedback summary | `cohort_state: suppressed`, `has_data: false`, clarity `null` |
| Survey responses | `DEMOTEST-C` omitted and listed under `suppressed_courses`; only `DEMOTEST-A` visible |
| De-anonymisation scan | No student username or email in the suppressed overview, exercise, or comment payloads |

## Production rule

Do **not** run this script on production. If demo data is found on production,
stop, record the affected accounts/courses, and remove them with `--cleanup`
only after a written decision. Dummy data is not release evidence.
