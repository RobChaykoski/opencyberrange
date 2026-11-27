# Quizzes

## Purpose

Check understanding with short exercise quizzes, certification-style question
banks, and practice exams. Quiz results are evidence inputs, not a replacement
for an instructor decision.

## Code map

| Concern | Location |
|---|---|
| Quiz router | `platform/backend/app/routers/quiz.py` |
| Exercise quiz | `platform/backend/app/routers/exercise_quiz.py` |
| Question banks | `platform/backend/app/routers/question_bank.py` |
| Certification quiz | `platform/backend/app/services/certification_quiz.py` |
| Practice | `platform/backend/app/services/practice.py`, `routers/practice.py` |
| Model | `platform/backend/app/models/practice.py`, `lab.py` |
| Banks | `platform/backend/app/data/certification-question-banks.yaml` |

## API surface

| Method | Path | Notes |
|---|---|---|
| GET | `/api/exercises/quizzes` | available quizzes for a lab or track |
| POST | `/api/exercises/quizzes/{id}/submit` | submit answers |
| GET | `/api/exercises/quizzes/{id}/result` | result and feedback |
| GET/POST | `/api/exercises/quiz-feedback` | learner feedback |
| GET | `/api/admin/question-banks` | admin bank list |
| POST | `/api/admin/question-banks/validate` | validate a bank |
| GET | `/api/practice/*` | practice exams and sessions |

## Behaviour that matters

- **Server-side scoring.** Correct answers are never sent to the browser before
  submission.
- **Bank validation.** Question banks are validated for references, categories,
  and answer keys by `scripts/check-question-banks.py` and
  `scripts/check-quiz-banks.py`.
- **Coverage.** Every track with a fallback bank still offers a check; lab-specific
  banks cover the labs listed in `Workbook/COVERAGE.md`.
- **Feedback is optional.** A quiz can require a check and still accept a
  satisfaction response separately.
- **No LLM grading.** Quiz scoring is deterministic; subjective work uses the
  rubric and human review path.

## Persistent state

| Store | Data |
|---|---|
| `exercise_quiz_attempts` | question keys, answers, score, completion |
| `exercise_quiz_feedback` | satisfaction/relevance/usefulness/ease |
| Question bank YAML | source content, not learner state |
| `activity_events` | quiz activity |

## Fixtures and tests

- Seed banks: `seed_quizzes.py`, `seed_level_quizzes.py`.
- Validate content:

```bash
python scripts/check-question-banks.py
python scripts/check-quiz-banks.py
```

- Focused tests:

```bash
cd platform/backend
python -m pytest tests/test_exercise_quiz.py tests/test_certification_quiz.py \
  tests/test_question_bank_api.py tests/test_practice.py -q
```

## Extension checklist

- Add the bank entry and validate it.
- Keep the answer key out of the API response.
- Add a test for the correct, incorrect, and partial cases.
- Update the workbook and the competency contract if the quiz becomes required
  evidence.

## Related

- [Flags and scoring](../flags-and-scoring/README.md)
- [Competency and evidence](../competency-and-evidence/README.md)
- [Certification question banks](../../../../docs/CERTIFICATION-QUESTION-BANKS.md)
- [Practice exams](../../../../docs/PRACTICE-EXAMS.md)
