# Basic learning analytics

The instructor dashboard and lab records use five minimum metrics. They are
derived from the existing session, completion, and flag-attempt tables, so no
new learner tracking is required.

| Metric | Definition |
|---|---|
| Lab started | A learner opened a lab session or submitted a flag attempt for a lab. |
| Lab completed | A passing `LabCompletion` exists for the learner and lab. |
| Completion time | `LabCompletion.time_spent_minutes`, with session timestamps as the fallback for elapsed time. |
| Pass / fail | A completion is a pass; incorrect flag attempts are failures. |
| Retry count | `LabCompletion.attempts`, or the count of flag attempts in the window. |

## Instructor dashboard

The top of the instructor dashboard shows a rolling **last 7 days** view:

- **Students Active** — distinct learners with a session, flag attempt, or
  completion in the window.
- **Labs Completed** — passing completions in the window.
- **Average Score** — mean participation score for those completions. The score
  starts at 100, subtracts 10 per retry and 5 per hint, and is clamped to 0-100.
- **Struggling Students** — distinct learners with at least one of: a completion
  score below 70, three or more attempts on a completion, a started lab with no
  completion in the window, or five or more incorrect flag attempts without a
  completion.

The metrics use the same cohort scope as the rest of the instructor dashboard:
instructors see their own active courses; administrators see the platform.

## Lab-level metric sources

Per-lab drill-down is available from the existing exercise analytics endpoint:
`GET /api/analytics/courses/{course_id}/exercises`. It reports started and
completed learners, median completion time, first-attempt rate, median attempts,
hint pressure, abandonment rate, and health status.

## Privacy

The metrics are aggregate counts and medians. The dashboard does not expose raw
flags, passwords, or learner answers, and it keeps the existing small-cohort
suppression rules in the analytics endpoints.
