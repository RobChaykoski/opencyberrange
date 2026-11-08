# Professional and Enterprise priorities

Status: **Active scope**
Applies to: **Professional 2.2.0** and **Enterprise preview only**
Not in: Community / Academic profile

These five capabilities are the top priorities for the Professional edition and
are inherited by Enterprise. They are the product answer to the five reporting
questions in [Programme reports](PROGRAMME-REPORTS.md).

| Priority | Ranking | Primary question |
|---|---|---|
| Competency Framework Engine | 5 stars | Which competencies are weakest, and how long does development take? |
| Student Feedback Engine | 5 stars | What is helping or hurting learning? |
| Radar / Spider Web Reporting | 5 stars | Which tracks and competencies are strong or weak? |
| Exercise Health Analytics | 5 stars | Which labs are failing? |
| Instructor Intervention Dashboard | 4 stars | Which learners need support now? |

## 1. Competency Framework Engine

**Problem:** Tracks and labs are not the same as competencies. Without an
explicit framework, reports cannot say which competency is weak or when it has
developed.

**Capability:**

- Define competencies, domains, observable evidence, and progression levels.
- Map tracks, levels, labs, exercises, and quiz outcomes to competencies.
- Record evidence from completions, first-attempt success, hint-free work,
  quizzes, and instructor review.
- Version the framework so historical reports stay reproducible.
- Expose the definitions to reports, radar charts, accreditation exports, and
  the learner profile.

**Data:** existing track, level, lab, completion, hint, attempt, and quiz
records, plus new competency definitions and mappings.

**Guardrails:** evidence is descriptive. It does not award a professional
certification, grade a learner, or make an automated high-stakes decision.

**Feeds:** radar reporting, time-to-competency, accreditation support, learner
profile, intervention dashboard.

## 2. Student Feedback Engine

**Problem:** Likes, pulse surveys, and free text are separate signals. They need
one consent-aware model tied to exercises and competencies.

**Capability:**

- Structured feedback per exercise: difficulty, learning value, clarity,
  confidence, and optional comment.
- Track and competency context so feedback can explain a weak report.
- Consent, moderation, retention, and erasure rules.
- Aggregate views that suppress small groups and never expose a learner's
  identity without explicit consent.
- Feedback trends for instructors and curriculum authors.

**Data:** existing pulse surveys, exercise reactions, custom surveys, and
consent records, extended with competency context.

**Guardrails:** feedback is voluntary, skippable, and never used as a grade.
Free text is moderated and capped.

## 3. Radar / Spider Web Reporting

**Problem:** A single completion percentage hides whether a cohort is strong in
web security but weak in forensics.

**Capability:**

- Learner radar across the competency domains.
- Cohort and programme radar with cohort-size suppression.
- Compare a cohort with its own earlier baseline or with an approved programme
  benchmark, not with named learners.
- Confidence/evidence labels for every axis.
- Accessible table fallback for the chart.

**Delivered in 2.2.0:** the course and all-course skill-tree radar in Learning
reports, using the five Skill DNA branches. Learner-level and cohort
competency radar remain.

**Data:** competency evidence from the Competency Framework Engine.

**Guardrails:** within-person and aggregate comparison only. No public
leaderboard. Axes with insufficient evidence show “no evidence yet”, not zero.

## 4. Exercise Health Analytics

**Problem:** Instructors need to know which labs are failing, where learners
abandon, and which exercises are too easy, too hard, unclear, or broken.

**Capability:**

- Lab start rate, completion rate, abandonment rate, re-attempt count, median
  time, hint usage, and feedback sentiment.
- Trend over time and comparison with the exercise's own baseline.
- Authoring queue for labs with high abandonment, high hint pressure, or poor
  feedback.
- Drill-down from programme to track to lab to learner evidence.

**Data:** sessions, completions, flag attempts, hints, learning time, workbook
events, reactions, and pulse responses.

**Guardrails:** a red signal is a review prompt, not proof that an exercise is
bad. Always show sample size and evidence level.

## 5. Instructor Intervention Dashboard

**Problem:** Instructors discover struggling learners too late, usually after a
deadline.

**Capability:**

- Explainable support signals: no start, stalled start, repeated failed
  attempts, high hint pressure, long idle time, negative feedback, and declining
  growth.
- Cohort view with drill-down to the learner's own evidence.
- Suggested next action (review the workbook, book a check-in, reset the lab,
  adjust the deadline) with a human decision.
- Intervention log so support is coordinated and auditable.
- Private “sustained high performance” view for stretch opportunities, not a
  public ranking.

**Data:** engagement metrics, competency evidence, feedback, and instructor
actions.

**Guardrails:** no automated grade, punishment, label, or notification. The
instructor decides. The learner can see their own evidence and correct errors.

## Delivery order

1. Competency Framework Engine — everything else depends on the definitions.
2. Student Feedback Engine — attach feedback to the framework.
3. Exercise Health Analytics — use feedback and existing activity data.
4. Radar / Spider Web Reporting — render the competency evidence.
5. Instructor Intervention Dashboard — combine the signals into action.

Each priority needs a written plan, acceptance tests, privacy review, and a
release gate before it is marked delivered.

## Not in Community / Academic profile

Community / Academic continues to receive lab and workbook improvements,
exercise authoring, bug fixes, maintenance, and security updates. It does not
receive these five engines or their reporting surfaces.
