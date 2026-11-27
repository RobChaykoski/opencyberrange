# Flags and scoring

## Purpose

Let a learner prove completion with a flag, limit abuse, record the attempt,
award the completion, and feed achievements and analytics without turning the
platform into a public ranking.

## Code map

| Concern | Location |
|---|---|
| Exercise router | `platform/backend/app/routers/curriculum.py` (`POST /labs/{lab_id}/submit-flag`, hint) |
| Lab model | `platform/backend/app/models/lab.py` (`FlagAttempt`, `LabCompletion`) |
| Achievements | `platform/backend/app/services/achievements.py`, `models/achievement.py` |
| Rate limit | `platform/backend/app/routers/curriculum.py` flag limiter |
| Analytics input | `LabCompletion` consumers in `routers/analytics.py`, `courses.py` |

## API surface

| Method | Path | Notes |
|---|---|---|
| POST | `/api/exercises/labs/{lab_id}/submit-flag` | submit `flag`; returns success/failure |
| GET | `/api/exercises/labs/{lab_id}/hint` | progressive hint, may cost points |
| GET | `/api/exercises/progress` | learner progress |

## Behaviour that matters

- **Flag hash, not plaintext.** The database stores a hash. The lab definition
  contains the source flag for the authoring and build flow; do not expose it.
- **Attempt limits.** A per-user/lab window and a maximum attempt count prevent
  brute force.
- **Hint placeholders.** A hint-only completion has an empty flag and is not
  counted as a solved exercise.
- **One completion per learner/lab.** Duplicate attempts are rejected or
  treated as idempotent.
- **Course scope.** A course-scoped lab is only solvable when assigned and
  enrolled.
- **Achievements.** Completion can unlock level certificates and badges; badges
  are derived, not purchased.
- **No learner ranking.** Course scoreboards are course-scoped and opt-in; there
  is no public global leaderboard.

## Persistent state

| Store | Data |
|---|---|
| `labs` | `flag_hash`, visibility, difficulty, chapter |
| `flag_attempts` | user, lab, attempt count, hint use, timestamps |
| `lab_completions` | user, lab, flag submitted, attempts, time, completion time |
| `achievements` | awarded badge/achievement |
| `activity_events` | completion activity |

## Fixtures and tests

- Seed a lab and solve it through the API in a test.
- Development data: `seed_feature_test_data.py`, `simulate_student.py`.
- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_flag_submit.py tests/test_flag_hint.py \
  tests/test_achievements.py tests/test_achievement_catalogue.py \
  tests/test_lab_outcomes.py -q
```

## Extension checklist

- Keep the flag out of logs and error messages.
- Keep the hash comparison constant-time.
- Add a test for wrong flag, repeated attempt, hint-only, and cross-course.
- Update the lab manifest and workbook if the flag flow changes.
- Regenerate lab outcomes if scoring semantics change.

## Related

- [Labs and sessions](../labs-and-sessions/README.md)
- [Quizzes](../quizzes/README.md)
- [Analytics and reports](../analytics-and-reports/README.md)
- [Learner-visible scores](../../../../docs/LEARNER-VISIBLE-SCORES.md)
