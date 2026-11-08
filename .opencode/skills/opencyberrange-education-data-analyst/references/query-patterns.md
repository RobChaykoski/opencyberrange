# Query patterns

These are starting points, not a mandate to bypass the API. The API enforces
authorization and shared definitions; use it first. Use SQL only for analysis the
API does not expose, and never export more fields than the decision needs.

Placeholders: `:course_id`, `:user_id`, `:semester_id`.

## 1. Individual exercise rows

```sql
SELECT
    l.slug,
    l.name,
    l.difficulty,
    l.duration_minutes,
    a.sort_order,
    c.completed_at,
    c.time_spent_minutes,
    c.hints_used,
    c.attempts,
    s.started_at,
    p.difficulty AS pulse_difficulty,
    p.learning AS pulse_learning,
    q.best_score,
    q.latest_score
FROM course_enrollments e
JOIN course_lab_assignments a
  ON a.course_id = e.course_id
JOIN labs l
  ON l.id = a.lab_id
LEFT JOIN lab_completions c
  ON c.user_id = e.user_id
 AND c.lab_id = l.id
 AND c.flag_submitted IS NOT NULL
 AND c.flag_submitted <> ''
LEFT JOIN LATERAL (
    SELECT MIN(started_at) AS started_at
    FROM lab_sessions
    WHERE user_id = e.user_id
      AND lab_id = l.id
      AND is_diagnostic = false
) s ON true
LEFT JOIN LATERAL (
    SELECT difficulty, learning
    FROM exercise_pulse_surveys
    WHERE user_id = e.user_id
      AND lab_id = l.id
      AND course_id = e.course_id
    ORDER BY updated_at DESC NULLS LAST, created_at DESC
    LIMIT 1
) p ON true
LEFT JOIN LATERAL (
    SELECT
        MAX(score) AS best_score,
        (ARRAY_AGG(score ORDER BY completed_at DESC))[1] AS latest_score
    FROM exercise_quiz_attempts
    WHERE user_id = e.user_id
      AND lab_id = l.id
      AND completed_at IS NOT NULL
) q ON true
WHERE e.course_id = :course_id
  AND e.user_id = :user_id
ORDER BY a.sort_order, l.name;
```

## 2. Individual summary

```sql
WITH assigned AS (
    SELECT lab_id
    FROM course_lab_assignments
    WHERE course_id = :course_id
),
completed AS (
    SELECT c.*
    FROM lab_completions c
    JOIN assigned a ON a.lab_id = c.lab_id
    WHERE c.user_id = :user_id
      AND c.flag_submitted IS NOT NULL
      AND c.flag_submitted <> ''
)
SELECT
    (SELECT COUNT(*) FROM assigned) AS assigned,
    COUNT(*) AS completed,
    COUNT(*) FILTER (WHERE hints_used = 0) AS hint_free,
    COUNT(*) FILTER (WHERE attempts = 1) AS first_attempt,
    COUNT(*) FILTER (WHERE attempts > 1) AS reattempted,
    ROUND(AVG(hints_used)::numeric, 2) AS hints_per_completion,
    ROUND(AVG(time_spent_minutes)::numeric, 1) AS mean_time,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY time_spent_minutes) AS median_time
FROM completed;
```

Use medians and IQR for time. Do not use `mean_time` as the headline.

## 3. Peer median per exercise

```sql
WITH peer AS (
    SELECT c.lab_id, c.time_spent_minutes
    FROM lab_completions c
    JOIN course_enrollments e
      ON e.user_id = c.user_id
     AND e.course_id = :course_id
    WHERE c.lab_id IN (
        SELECT lab_id FROM course_lab_assignments WHERE course_id = :course_id
    )
      AND c.flag_submitted IS NOT NULL
      AND c.flag_submitted <> ''
      AND c.time_spent_minutes IS NOT NULL
)
SELECT
    lab_id,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY time_spent_minutes) AS median_time,
    percentile_cont(0.25) WITHIN GROUP (ORDER BY time_spent_minutes) AS p25,
    percentile_cont(0.75) WITHIN GROUP (ORDER BY time_spent_minutes) AS p75,
    COUNT(*) AS n
FROM peer
GROUP BY lab_id;
```

Use only when `n >= 3`. Otherwise use the course median for the same difficulty
band, or show no peer comparison.

## 4. Exercise diagnostics

```sql
SELECT
    l.slug,
    l.difficulty,
    l.duration_minutes,
    COUNT(DISTINCT e.user_id) AS enrolled,
    COUNT(DISTINCT c.user_id) FILTER (
        WHERE c.flag_submitted IS NOT NULL AND c.flag_submitted <> ''
    ) AS completed,
    COUNT(DISTINCT s.user_id) FILTER (WHERE s.is_diagnostic = false) AS started,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY c.time_spent_minutes)
        FILTER (WHERE c.time_spent_minutes IS NOT NULL) AS median_time,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY c.attempts)
        FILTER (WHERE c.attempts IS NOT NULL) AS median_attempts,
    COUNT(*) FILTER (WHERE c.hints_used > 0) AS completions_with_hints,
    COUNT(DISTINCT p.user_id) AS pulse_respondents,
    ROUND(AVG(p.learning)::numeric, 2) AS learning_reported,
    ROUND(AVG(p.difficulty)::numeric, 2) AS difficulty_reported
FROM course_lab_assignments a
JOIN labs l ON l.id = a.lab_id
JOIN course_enrollments e ON e.course_id = a.course_id
LEFT JOIN lab_completions c
  ON c.user_id = e.user_id
 AND c.lab_id = l.id
 AND c.flag_submitted IS NOT NULL
 AND c.flag_submitted <> ''
LEFT JOIN lab_sessions s
  ON s.user_id = e.user_id
 AND s.lab_id = l.id
 AND s.is_diagnostic = false
LEFT JOIN exercise_pulse_surveys p
  ON p.user_id = e.user_id
 AND p.lab_id = l.id
 AND p.course_id = a.course_id
WHERE a.course_id = :course_id
GROUP BY l.slug, l.difficulty, l.duration_minutes
ORDER BY started DESC, l.slug;
```

This can duplicate rows when a learner has multiple sessions or pulse responses.
Use `DISTINCT` staging tables or the API, which already de-duplicates.

## 5. Coaching queue

```sql
WITH roster AS (
    SELECT user_id FROM course_enrollments WHERE course_id = :course_id
),
progress AS (
    SELECT c.user_id, COUNT(*) AS completed
    FROM lab_completions c
    JOIN course_lab_assignments a
      ON a.lab_id = c.lab_id
     AND a.course_id = :course_id
    WHERE c.flag_submitted IS NOT NULL
      AND c.flag_submitted <> ''
    GROUP BY c.user_id
),
checkin AS (
    SELECT
        author_id,
        ROUND(AVG((clarity + engagement + confidence) / 3.0)::numeric, 2) AS feeling
    FROM course_feedback
    WHERE course_id = :course_id
      AND direction = 'student_course'
      AND clarity IS NOT NULL
      AND engagement IS NOT NULL
      AND confidence IS NOT NULL
    GROUP BY author_id
),
coaching AS (
    SELECT subject_user_id, MAX(updated_at) AS last_note
    FROM course_feedback
    WHERE course_id = :course_id
      AND direction = 'instructor_student'
    GROUP BY subject_user_id
)
SELECT
    u.id,
    u.display_name,
    COALESCE(pr.completed, 0) AS completed,
    (SELECT COUNT(*) FROM course_lab_assignments WHERE course_id = :course_id) AS assigned,
    ck.feeling,
    co.last_note
FROM roster r
JOIN users u ON u.id = r.user_id
LEFT JOIN progress pr ON pr.user_id = r.user_id
LEFT JOIN checkin ck ON ck.author_id = r.user_id
LEFT JOIN coaching co ON co.subject_user_id = r.user_id
ORDER BY co.last_note NULLS FIRST, ck.feeling NULLS FIRST;
```

Feeling is self-report only. Do not infer it from progress, hints, or attempts.
The API's `feedback/summary` already returns the roster; prefer it.

## 6. Quiz best and latest

```sql
SELECT
    lab_id,
    MAX(score) AS best_score,
    (ARRAY_AGG(score ORDER BY completed_at DESC))[1] AS latest_score,
    COUNT(*) AS attempts
FROM exercise_quiz_attempts
WHERE user_id = :user_id
  AND completed_at IS NOT NULL
GROUP BY lab_id;
```

Report best and latest separately. A 70% benchmark is practice guidance, not a
gate.

## 7. Data-quality checks

```sql
-- Completion without a session
SELECT
    COUNT(*) AS completions,
    COUNT(*) FILTER (WHERE s.lab_id IS NULL) AS without_session
FROM lab_completions c
JOIN course_enrollments e
  ON e.user_id = c.user_id
 AND e.course_id = :course_id
LEFT JOIN LATERAL (
    SELECT lab_id
    FROM lab_sessions
    WHERE user_id = c.user_id
      AND lab_id = c.lab_id
      AND is_diagnostic = false
    LIMIT 1
) s ON true
WHERE c.flag_submitted IS NOT NULL
  AND c.flag_submitted <> '';
```

```sql
-- Duplicate completions
SELECT user_id, lab_id, COUNT(*) AS rows
FROM lab_completions
WHERE flag_submitted IS NOT NULL
  AND flag_submitted <> ''
GROUP BY user_id, lab_id
HAVING COUNT(*) > 1;
```

```sql
-- Opt-in and response coverage
SELECT
    COUNT(*) AS enrolled,
    COUNT(*) FILTER (WHERE u.survey_opt_in) AS opted_in
FROM course_enrollments e
JOIN users u ON u.id = e.user_id
WHERE e.course_id = :course_id;
```

## 8. Wilson interval

```python
from math import sqrt

def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))
```

Use it for small proportions. Do not use it to rank learners or instructors.

## 9. Export discipline

- Select only the fields the decision needs.
- Aggregate before export where possible.
- Do not include flags, credentials, free-text comments, or email addresses.
- Record the purpose, owner, and retention date with the export.
- Keep the SQL or notebook with the analysis so the result is reproducible.
