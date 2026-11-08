# Individual success metrics

Use this reference to turn exercise and course records into a **student success
profile**: a small set of indicators and one next step. It is for the student and
their instructor. The dean sees aggregates, not this profile.

The profile is descriptive. It is not a grade, a diagnosis, a prediction, or a
reason to rank learners.

## What the exercise catalogue already gives us

Every lab carries:

- `difficulty` (`beginner`, `intermediate`, `advanced`);
- `duration_minutes` (the estimate);
- `objectives` (what the learner should be able to do);
- `hints` (count and text);
- `flag`, workbook, and category;
- `counts_toward_certificate` (default true; bonus labs set false).

The current catalogue (149 labs, 2026-11-08) is:

| Field | Finding |
|---|---|
| Difficulty | 70 beginner, 71 intermediate, 8 advanced |
| Duration estimate | median 120 min, mean 85 min, range 15–180 |
| Hints | median 5, range 0–7; 147 labs have hints |
| Objectives | median 4 per lab; 148 labs have them |
| Prerequisites | **0 of 149 labs define them** |

The two immediate consequences:

1. **Duration is coarse.** A 120-minute estimate is common, so "time over
   estimate" is weak on its own. Compare a learner with the peer median for the
   same exercise first, and use the estimate second.
2. **Readiness is invisible.** Without prerequisites, the course cannot warn
   that a learner skipped a foundation exercise. Use track/level order and the
   course assignment order as the temporary readiness proxy.

## What the instructor course view already gives us

`GET /api/analytics/courses/{course_id}/overview` returns course-level:

- enrolled, started, and completed learners;
- completion, started, and abandonment rates;
- median time, learning hours, time over estimate;
- hints per completion, hint-free rate;
- first-attempt and reattempt rates, median attempts;
- pulse responses, learning reported, difficulty reported;
- confidence gain (proxy), reactions, RAG status and reasons;
- domain performance and skill-tree mix.

`GET /api/analytics/courses/{course_id}/exercises` returns per exercise:

- completion, started-to-complete, abandonment;
- median time, time to first attempt, time to completion;
- median attempts, hint pressure, first-attempt rate, reattempt recovery;
- pulse responses, learning and difficulty reported, unclear comments;
- RAG, reasons, and flags (`high_hint_pressure`, `high_attempt_burden`,
  `low_completion`);
- per-exercise reactions.

`GET /api/analytics/student/me` returns the learner's own summary, growth,
domains, recent exercises, and coaching prompts. Use it as the student-side
source of truth.

## The individual success profile

Do not collapse this into one score. Show eight small dimensions and one next
step.

| Dimension | Question | Primary signals |
|---|---|---|
| **Progress** | Are they moving through the assigned work? | Completed / assigned, certificate progress, active weeks |
| **Pace** | Is the work taking longer than expected? | Time vs peer median, time over estimate, time to first attempt |
| **Independence** | Can they proceed without hints? | Hint-free rate, hints per completion, first-attempt rate |
| **Persistence** | Do they recover after a wrong attempt? | Reattempt recovery, completion after difficulty, attempts |
| **Understanding** | Can they explain and apply it? | Quiz participation, best/latest quiz score, learning reported |
| **Experience** | Is the work clear and appropriately challenging? | Clarity, challenge fit, relevance, usefulness, ease of use |
| **Capability** | What practice is accumulating? | Cyber DNA traits, breadth, depth, affinities |
| **Support** | Is the feedback loop closing? | Coaching notes, response to unclear points, check-in status |

### Progress

```text
progress = completed_assigned / assigned
certificate_progress = certificate_required_completed / certificate_required_assigned
active_weeks = weeks with at least one completion or session
```

Use counts for small cohorts. A learner at 4/8 is "halfway", not "50% weak".

### Pace

```text
time_ratio = learner_time / peer_median_time_for_same_exercise
time_over_estimate = learner_time / exercise_duration_minutes
```

Prefer `time_ratio` when the peer median is based on at least 3 completions.
`time_over_estimate` is a secondary signal because the catalogue estimate is
coarse. A ratio above 1.5 is a prompt to check scope, prerequisites, and access —
not a judgement about ability.

### Independence

```text
hint_free_rate = completions_with_zero_hints / completions
hints_per_completion = total_hints / completions
first_attempt_rate = completions_with_one_attempt / completions
```

High hint use is not a failure. It becomes a coaching signal when it is paired
with low first-attempt success, long time, or low learning reported. Check
whether the learner is using hints to learn or to skip.

### Persistence

```text
reattempt_recovery = completions_with_more_than_one_attempt / completions
```

A learner with high reattempt recovery is persisting. Recognise it. Do not
penalise attempts in the profile. A learner with many attempts and no completion
needs a smaller next step, not a lower label.

### Understanding

```text
quiz_participation = learners_with_a_completed_attempt / enrolled
quiz_best = best completed attempt score
quiz_latest = most recent completed attempt score
learning_reported = mean pulse learning (1–5)
```

Report best and latest separately. Best shows mastery; latest shows current
understanding. A 70% benchmark is practice guidance, not a pass/fail gate.

### Experience

```text
challenge_fit = max(0, 100 - abs(mean_difficulty - 3) * 25)
```

Use the course check-in for clarity, relevance, usefulness, ease of use, and
confidence. Use the exercise pulse for difficulty and learning. Show n. Fewer
than five responses is an early signal.

### Capability

Use Cyber DNA exactly as defined in `docs/SKILL-DNA.md`:

- five traits, each 0–100;
- class and affinities;
- movement between two snapshots with the same formula version;
- breadth (distinct tracks/categories) and depth (advanced/completed cleanly).

Never rank by trait or affinity. Never use Cyber DNA for admissions, hiring,
discipline, or a high-stakes decision.

### Support

```text
coaching_coverage = students_with_at_least_one_coaching_note / enrolled
response_to_unclear = unclear comments with an instructor response / unclear comments
checkin_status = opted in and submitted / opted in
```

A learner with no coaching note and a flat progress line needs an instructor
contact, not a louder dashboard.

## Diagnostic patterns and interventions

Use the pattern, not a single metric. Pick one next step.

| Pattern | Likely meaning | Next step |
|---|---|---|
| Low progress + no activity for 7+ days | Disengagement or a blocker | Instructor sends a short check-in; choose one 15–30 minute exercise; confirm access |
| Low progress + high time ratio | Scope, prerequisite, or access issue | Break the exercise into observe / hypothesise / verify; check prerequisites; offer accommodation |
| High hints + low first-attempt rate | Concept gap or hint dependency | Socratic coaching; explain-back; pair the learner with a peer; revisit the prerequisite |
| High reattempt recovery | Persistence | Recognise the persistence; add a similar-but-different transfer task; do not penalise attempts |
| High completion + low quiz accuracy | Completion without understanding | Add a knowledge check or teach-back; apply the concept in a new context |
| High completion + high quiz + low challenge | Under-stretched | Advanced exercise, new track, or peer-teaching role |
| Low learning reported + high difficulty | Design or scaffolding issue | Add a worked example, reduce scope, add a hint checkpoint, or move the prerequisite earlier |
| High completion + low satisfaction | Experience issue | Check relevance, workload, clarity, and time estimate; ask what to change |
| Flat Cyber DNA + high completion | Curriculum coverage gap | Assign exercises in the target traits; review the course skill-tree mix |
| No coaching + low response rate | The loop is not closing | Instructor outreach; in-class check-in; one coaching note per student per cycle |

## Thresholds

Use **relative** thresholds first:

- compare the learner with their own previous three exercises;
- compare with the course median for the same exercise;
- compare with the course median for the same difficulty band.

Use absolute thresholds only where they are meaningful:

- quiz benchmark: 70% (practice guidance, not a gate);
- completion: assigned work completed vs assigned;
- inactivity: 7 days without a completion or session;
- coaching: at least one note per student per cycle;
- response rate: below 50% is an attention signal, 50–69% watch, 70%+ healthy.

Never use a threshold to label a person. Use it to choose a next step. With fewer
than five learners or three data points, say "early signal" and do not compare.

## Data gaps to fix

These are product and data-quality issues, not learner issues.

1. **Session coverage is incomplete.** On the development course, completion was
   77.1% while `started_rate` was 2.1%; many completions have no matching
   `lab_sessions` row. Until fixed, use completion-, hint-, attempt-, and
   time-based metrics, and label started rate as unreliable.
2. **No prerequisites.** Add optional `prerequisites: [slug, ...]` to `lab.yaml`
   and surface readiness in the course assignment order. Until then, use the
   track/level order.
3. **Duration estimates are coarse.** Recalibrate from observed medians per
   exercise, or show peer median beside the estimate.
4. **Pulse response is thin.** Many completions have no pulse. Keep it optional;
   use the course check-in for experience and the pulse for exercise-level
   signals.
5. **`started_rate` is misleading.** It is started learner-exercise pairs divided
   by total possible pairs, not started learners divided by enrolled. Rename it
   or add a separate `started_learners_rate`.
6. **Certificate flag is implicit.** Only one lab sets
   `counts_toward_certificate`; make the field explicit for bonus labs.
7. **Quiz score needs two views.** Show best and latest; do not collapse them.
8. **Cyber DNA needs a formula version.** Never compare snapshots across formula
   changes.

## Privacy and responsible use

- The success profile belongs to the student and their instructor. The dean sees
  aggregates.
- Do not show one student's profile to another student, or to an instructor who
  does not teach the course.
- Do not include flags, credentials, personal data, or identifiable screenshots.
- Do not use the profile for admissions, hiring, discipline, or public ranking.
- State the sample size and the limitation beside every score.
- Give the learner a route to correct their data and to opt out of surveys.

## Implementation

### API

Add a student-success endpoint scoped to the course:

```text
GET /api/courses/{course_id}/students/{user_id}/success-profile
```

Authorization: the student for their own record; the course instructor or an
administrator with an explicit support purpose. Return aggregates and the
student's own exercise rows only. Do not return other learners.

Suggested payload:

```json
{
  "student": {"id": 12, "display_name": "..."},
  "course": {"id": 3, "code": "DEMO-CAREER"},
  "progress": {"completed": 7, "assigned": 16, "certificate_completed": 0, "certificate_required": 16},
  "pace": {"time_ratio": 1.4, "time_over_estimate": 1.8, "peer_n": 3},
  "independence": {"hint_free_rate": 41.0, "hints_per_completion": 0.7, "first_attempt_rate": 41.0},
  "persistence": {"reattempt_recovery": 59.0, "median_attempts": 2.0},
  "understanding": {"quiz_participation": true, "quiz_best": 67, "quiz_latest": 67, "learning_reported": 3.8},
  "experience": {"clarity": 4.0, "challenge_fit": 88.0, "relevance": 4.0, "usefulness": 4.0, "ease_of_use": 3.5, "n": 3},
  "capability": {"formula_version": "2026.11", "traits": [{"key": "builder", "score": 42}], "affinities": []},
  "support": {"coaching_notes": 1, "last_coaching_at": "...", "checkin_status": "submitted"},
  "next_step": {"type": "exercise", "slug": "...", "reason": "..."},
  "n": 3,
  "limitations": ["Small cohort", "Session start records incomplete"],
  "generated_at": "..."
}
```

### UI

Use a compact card on the instructor's course **People** or **Feedback** view,
and on the student's own **My learning** page:

1. **One next step** at the top.
2. Progress and pace.
3. Independence and persistence.
4. Understanding and experience.
5. Cyber DNA movement.
6. Support and feedback.
7. "What this does not prove" line.

Do not use a single ring, grade, or rank. Do not use red/green for the learner;
use neutral labels and a next-step tone.

### Tests

- The profile requires the right role.
- A student sees only their own profile.
- An instructor sees only their course.
- Small samples are labelled.
- Quiz best and latest are separate.
- Cyber DNA comparison is blocked across formula versions.
- The next step is present when the profile is not empty.

## Current development evidence (test data, 2026-11-08)

Use these only to calibrate the model; they are not production claims.

- **Course 1 (CYB-3350):** 6 learners, 8 exercises, completion 77.1%,
  hint-free 48.6%, first-attempt 51.4%, reattempt 48.6%, no pulse responses,
  RAG amber. Five of eight exercises had high hint pressure.
- **Course 3 (DEMO-CAREER):** 3 learners, 16 exercises, completion 45.8%,
  time over estimate 54.5%, hint-free 40.9%, first-attempt 40.9%, reattempt
  59.1%, learning 3.83/5, difficulty 2.5/5, RAG red. Several exercises had only
  one of three learners, so their percentages are noisy.
- **Catalogue:** 149 labs, 70 beginner / 71 intermediate / 8 advanced; median
  duration 120 minutes; zero prerequisites; 147 labs with hints.

These findings support three design choices:

1. show **counts and n** before percentages;
2. use **peer median time** before the catalog estimate;
3. treat **hint pressure and reattempt recovery** as the first individual
   coaching signals, not completion alone.
