# Metrics and evidence

One metric definition, one denominator, one source. The UI, exports, and reports
must agree. If they disagree, fix the definition before adding a chart.

## Metric contract

| Metric | Definition | Source | Use | Limitation |
|---|---|---|---|---|
| Completion rate | Completed learner–exercise pairs / possible pairs | `course_overview` | Progress | Activity, not capability |
| Started-to-complete | Completed / started | `course_exercises` | Persistence after starting | Session coverage is incomplete |
| Abandonment rate | Started without completion / started | `course_overview`, `course_exercises` | Friction | Depends on session coverage |
| Median time | Median `time_spent_minutes` on completions | `course_overview` | Pace | Self-reported or tracked; nulls |
| Time over estimate | Completions over `duration_minutes` / timed completions | `course_overview` | Pacing signal | Catalogue estimates are coarse |
| Hints per completion | Total hints / completions | `course_overview` | Independence | Hint use can be learning |
| Hint-free rate | Completions with zero hints / completions | `course_overview` | Independence | Rewards not asking for help |
| First-attempt rate | Completions with one flag attempt / completions | `course_overview` | Independence | Hints and prior knowledge differ |
| Reattempt rate | Completions with more than one attempt / completions | `course_overview` | Persistence | Attempts are not penalised |
| Persistence | Exercises completed after more than one attempt | `analytics/metrics` | Persistence | Count, not a score |
| Breadth | Distinct tracks with a completion | `analytics/metrics` | Capability coverage | Not depth |
| Learning reported | Mean pulse learning (1–5) | `exercise_pulse_surveys` | Experience | Optional self-report |
| Difficulty reported | Mean pulse difficulty (1–5) | `exercise_pulse_surveys` | Challenge fit | Optional self-report |
| Challenge fit | `max(0, 100 - abs(difficulty - 3) * 25)` | Pulse | Experience | Self-report |
| Confidence gain | Mean of hint, attempt, and time trend statuses × 100 | `analytics` | Growth proxy | Not a validated psychological score |
| Response rate | Unique respondents / enrolled | `feedback/summary` | Loop health | Opt-in |
| Clarity / engagement / confidence | Mean check-in ratings (1–5) | `feedback/summary` | Experience | Opt-in, small samples |
| Coaching coverage | Students with at least one coaching note / enrolled | `feedback/summary` | Instructor loop | A note is not proof of learning |
| Knowledge-check participation | Learners with a completed attempt / enrolled | `exercise_quiz_metrics` | Understanding | Optional benchmark |
| Knowledge-check accuracy | Mean best score | `exercise_quiz_metrics` | Understanding | Best score hides latest |
| Cyber DNA trait | 0–100 per trait, formula `2026.11` | `skill_dna.py` | Capability practice | Descriptive, capped, versioned |
| Cyber DNA movement | Trait change between snapshots, same formula version | Skill DNA snapshots | Capability trend | No cross-version comparison |
| Feeling | Mean check-in clarity, engagement, confidence | `feedback/summary` | Quick conversation prompt | Self-report only |
| Doing | Completed / assigned | `feedback/summary` students array | Progress | Small cohorts are noisy |

## Denominators that commonly go wrong

- **Assigned exercises** = `course_lab_assignments` rows, not all labs.
- **Enrolled learners** = `course_enrollments` rows for the course.
- **Started** = unique learner–exercise pairs with a non-diagnostic session.
- **Completed** = learner–exercise pairs with a non-empty `flag_submitted`.
- **Respondents** = unique learners with a check-in, pulse, reaction, or survey.
- **Timed completions** = completions with `time_spent_minutes` not null.
- **Certificate required** = labs where `counts_toward_certificate` is true.

Do not compare a pair-based rate with a learner-based rate. Do not compare a
course with a different cohort size or delivery mode without saying so.

## Sample-size rules

| Evidence | Minimum | Label |
|---|---|---|
| Headline percentage | 5 observations | Otherwise show counts and n |
| Peer median time | 3 completions | Otherwise use the course median or no comparison |
| Trend | 3 weekly points | Otherwise "early signal" |
| Cohort trend | 10 learners and 6 weekly points | Otherwise "insufficient history" |
| Feeling | 5 check-in responses | Otherwise counts and "early signal" |

Show `n` beside every percentage and peer comparison. Suppress percentages that
could identify a person in a small cohort.

## Cyber DNA rules

- Read `docs/SKILL-DNA.md` first.
- Report the five traits, class, and affinities with evidence levels.
- Report movement between two snapshots with the same formula version.
- Never rank by trait, class, or affinity.
- Never use Cyber DNA for admissions, hiring, discipline, or high-stakes
  decisions.
- Affinities are positive practice directions, not job labels.

## Feeling vs doing

- Feeling is explicit self-report; doing is progress.
- Pair 🙂 positive, 😐 mixed, 🙁 low, ○ no check-in with On track / Building /
  Needs a step.
- Never infer feeling from completion, hints, attempts, time, or clicks.
- Always show a text label and an accessible name.
- The dean sees aggregate counts, not individual faces.
- Full rules: `opencyberrange-education-data-analyst/references/feeling-vs-doing.md`.

## Data-quality flags to show

- **Session-start coverage incomplete** — completion can exist without a session.
  Do not use started rate until verified.
- **Small cohort** — fewer than 5 learners; show counts and suppress percentages.
- **Early signal** — fewer than 5 responses or 3 weekly points.
- **Optional feedback** — pulse, quiz, and survey respondents may differ from
  non-respondents.
- **Coarse duration** — median estimate is 120 minutes; prefer peer median time.
- **No prerequisites** — readiness is a track/level proxy, not a true prerequisite
  check.
- **Formula version** — do not compare Cyber DNA across versions.

## Reporting language

Use:

- "The evidence suggests…"
- "This is an early signal (n=…)."
- "The data cannot tell us…"
- "At the current pace, the projection is… (band …, method …)."
- "Two courses are driving the gap."

Avoid:

- "Students are failing."
- "This instructor is below average."
- "The forecast predicts 12 students will fail."
- "The programme will hit 68%."
- A single RAG colour with no reason.
