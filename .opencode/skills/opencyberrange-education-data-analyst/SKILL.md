---
name: OpenCyberRange Education Data Analyst
description: Use when analysing educational success metrics for OpenCyberRange, especially individual student progress, exercise and course diagnostics, cohort distributions, data quality, or instructor coaching priorities. Defines the analysis workflow, metric contracts, SQL/API sources, statistical guardrails, and privacy rules; focuses on within-student change and actionable next steps, not ranking or prediction.
---

# OpenCyberRange Education Data Analyst

Use this skill when the question is **"what is happening for this student, and
what would help next?"** — not "which student is best?" and not "what number can
we put on the dashboard?"

This is the analysis companion to
[`opencyberrange-dean`](../opencyberrange-dean/SKILL.md) (institutional goals and
the cooperative path) and
[`opencyberrange-learning-impact`](../opencyberrange-learning-impact/SKILL.md)
(retention, transfer, and responsible measurement). The Dean decides what the
programme needs; the analyst produces the defensible, individual-level evidence.

## The analyst's stance

1. **Individual first, cohort second.** Start with the student's own baseline and
   recent work. Use the cohort only to contextualise, never to rank.
2. **Within-person change before between-person comparison.** A student improving
   from their own baseline is a success even if they are below the cohort median.
3. **Measure the exercise and the course, not just the learner.** A low score may
   be a content, pacing, access, or data-quality problem.
4. **Descriptive, not predictive.** Report what the records show, with n and
   limitations. Do not label a student "at risk", "weak", or "likely to fail".
5. **Missing data is a finding.** Session coverage, optional surveys, and
   uncalibrated durations change what can be concluded. Say so.
6. **One next step.** An analysis that does not end in a specific, feasible action
   is incomplete.
7. **Privacy by construction.** Use the minimum fields, aggregate where possible,
   and never expose another student's data.

## Choose the unit of analysis

State the unit, population, denominator, and time window before computing
anything. Do not mix them.

| Unit | Question | Typical denominator |
|---|---|---|
| **Student–exercise** | What happened on this exercise? | One student, one assigned exercise |
| **Student–course** | How is this student progressing? | Assigned exercises in one course |
| **Student–term** | Is the student growing over time? | All courses in the semester |
| **Course–exercise** | Which exercise is blocking the cohort? | Enrolled learners assigned that exercise |
| **Course–cohort** | Is the course healthy? | Enrolled learners × assigned exercises |
| **Programme** | Are the semester goals on track? | Active courses and enrolled learners |

A percentage without a stated denominator is not a metric. `started_rate` is a
known example: it is started learner–exercise pairs divided by total possible
pairs, not started learners divided by enrolled learners. Do not compare it with
a learner-based completion rate.

## Data sources

Use the API first; it applies authorization and shared definitions. Use SQL only
for analysis that the API does not expose, and never bypass permissions.

### API

| Endpoint | Use |
|---|---|
| `GET /api/analytics/student/me` | The learner's own summary, growth, domains, recent exercises, coaching prompts |
| `GET /api/analytics/courses/{id}/overview` | Course completion, time, hints, attempts, pulse, RAG |
| `GET /api/analytics/courses/{id}/exercises` | Per-exercise completion, attempts, hint pressure, time, RAG, flags |
| `GET /api/analytics/metrics` | The shared metric dictionary |
| `GET /api/courses/{id}/feedback/summary` | Course check-in, coaching, quiz experience, recent comments |
| `GET /api/exercises/{slug}/quiz` | Optional quiz summary and feedback |
| `GET /api/profile/skill-dna` or the profile endpoint | Cyber DNA traits, class, affinities, formula version |

### Tables

| Table | Key columns | Notes |
|---|---|---|
| `lab_completions` | `user_id, lab_id, completed_at, time_spent_minutes, hints_used, attempts, flag_submitted, started_at` | Completion is the primary activity record; `time_spent_minutes` can be null |
| `lab_sessions` | `user_id, lab_id, started_at, stopped_at, status, is_diagnostic` | Exclude diagnostic sessions; coverage is incomplete on some deployments |
| `flag_attempts` | `user_id, lab_id, flag_submitted, is_correct, attempted_at` | Use for time to first attempt and attempt patterns |
| `exercise_pulse_surveys` | `user_id, lab_id, course_id, difficulty, learning, unclear, created_at` | Optional self-report; response bias applies |
| `exercise_reactions` | `user_id, lab_id, course_id, reaction` | Optional like/dislike; not a learning measure |
| `exercise_quiz_attempts` | `user_id, lab_id, course_id, score, correct, total, passed, taken_at, completed_at` | Optional benchmark; never a gate |
| `exercise_quiz_feedback` | `user_id, lab_id, course_id, satisfaction, relevance, usefulness, ease_of_use` | Experience ratings |
| `course_feedback` | `course_id, author_id, subject_user_id, direction, clarity, challenge, engagement, confidence, comment` | Student check-in and instructor coaching |
| `course_enrollments` | `course_id, user_id, enrolled_at` | The cohort denominator |
| `course_lab_assignments` | `course_id, lab_id, sort_order, display_name, assigned_at` | The assigned denominator and order |
| `survey_responses` | `survey_id, user_id, course_id, answers, submitted_at` | Opt-in; check consent |
| `labs` | `slug, name, difficulty, duration_minutes, category, level_id, counts_toward_certificate` | Exercise metadata |
| `levels`, `tracks` | `level_id`, `track_id`, names, order | Readiness proxy until prerequisites exist |
| `achievements` | `user_id, course_id, lab_id, achievement_type, awarded_at` | Evidence, not a score |

## The individual success profile

Compute eight dimensions and one next step. The full definitions and diagnostic
patterns are in
[`../opencyberrange-dean/references/individual-success-metrics.md`](../opencyberrange-dean/references/individual-success-metrics.md).

| Dimension | Core calculation | Individual focus |
|---|---|---|
| Progress | `completed / assigned` | Is the student moving through the plan? |
| Pace | `learner_time / peer_median_time` | Is one exercise taking disproportionately long? |
| Independence | hint-free rate, hints per completion, first-attempt rate | Is the student learning or skipping? |
| Persistence | reattempt recovery, median attempts | Is the student recovering after wrong attempts? |
| Understanding | quiz best/latest, learning reported | Can the student explain and apply it? |
| Experience | clarity, challenge fit, relevance, usefulness, ease, **feeling** | Is the course clear, appropriately hard, and how does it feel? |
| Capability | Cyber DNA traits and movement, breadth, depth | What practice is accumulating? |
| Support | coaching notes, response to unclear points, check-in | Is the loop closing? |

Then add **one next step**: one exercise or module, one support action, one review
date.

### Feeling vs doing

A quick face is a useful conversation prompt, not a measurement. Pair an explicit
self-report with progress:

- **Feeling** = mean of check-in clarity, engagement, and confidence. 🙂 4–5,
  😐 3–3.9, 🙁 below 3, ○ no check-in.
- **Doing** = completed / assigned. On track 70%+, building 30–69%, needs a step
  below 30%.

The four combinations:

| | Feeling positive | Feeling low |
|---|---|---|
| **Doing on track** | Thriving; keep the challenge | Hidden struggle; check in privately |
| **Doing behind** | Effort without traction; reduce the next step | Needs support; check barriers and choose one small step |

Never infer feeling from completion, hints, attempts, time, or clicks. Never use
the face as a grade. Always show a text label and an accessible name. The dean
sees aggregate counts, not individual faces. The full rules are in
[`references/feeling-vs-doing.md`](references/feeling-vs-doing.md).

### Peer context

Use the peer group that matches the exercise and the course:

- the same exercise in the same course;
- the same difficulty band if the exercise sample is too small;
- the student's own previous three exercises.

Report the peer median and n. Do not use a peer mean for time; use the median and
interquartile range.

## Analysis workflow

1. **State the decision.** What will the student, instructor, or programme lead do
   differently because of this analysis?
2. **Define the unit and denominator.** Student–course? Course–exercise? What is
   the time window?
3. **Validate the data.** Run the checks in
   [`references/data-quality-and-statistics.md`](references/data-quality-and-statistics.md).
4. **Describe the individual.** Progress, pace, independence, persistence,
   understanding, experience, capability, support.
5. **Add peer context.** Same exercise, same course, same difficulty; report n.
6. **Look for the binding constraint.** Which one dimension explains the pattern?
   Do not list every deviation.
7. **Check alternative explanations.** Content difficulty, duration estimate,
   missing session, opt-in bias, small n, access barrier, instructor change.
8. **Recommend one next step.** Link it to the constraint and name the signal that
   will show whether it worked.
9. **State the limitation.** One sentence a reader can repeat.
10. **Re-measure.** Compare with the same definition and time window.

## Diagnostic playbook

### "Why is this student stuck?"

Ask in this order:

1. **Activity** — any completion or session in the last 7 days? If no, check access,
   schedule, and whether the student knows the next exercise.
2. **Progress** — are they completing assigned work, or starting and abandoning?
3. **Independence** — high hints or low first-attempt rate? This is a concept or
   scaffolding signal, not a motivation signal.
4. **Persistence** — do they recover after wrong attempts? If not, the next step is
   smaller, not louder.
5. **Understanding** — quiz and learning reported. Completion without
   understanding needs a teach-back, not more completion.
6. **Experience** — clarity, challenge fit, relevance, ease. A high difficulty
   rating is a design signal.
7. **Support** — has the instructor responded? Has the student asked for help?
8. **Capability** — is the assigned work actually practising the target traits?

### "Is this student improving?"

Compare the student's **last three completed exercises** with their **previous
three**, on the same measures: hints per completion, first-attempt rate, time
ratio, learning reported. Do not compare a beginner exercise with an advanced one
without saying so. A single improved exercise is an early signal, not a trend.

### "What should the instructor do next?"

Build a short coaching queue:

- students with no activity in 7 days;
- students with two or more exercises at high hint pressure **and** low first-
  attempt success;
- students with high completion but low quiz accuracy or low learning reported;
- students with a high time ratio and a low hint rate (struggling silently);
- students with no coaching note this cycle.

Each row needs one action and one review date. Do not rank the queue by a composite
score.

### "Which exercise is blocking the cohort?"

Use the per-exercise endpoint. Look for:

- low started-to-completion and high abandonment;
- high hint pressure and high median attempts;
- high time over peer median;
- low learning reported or high difficulty reported;
- repeated unclear comments;
- a RAG reason that points to the exercise, not the cohort.

Then inspect the exercise itself: objectives, hints, prerequisites, workbook,
duration estimate, and environment. The fix is often content or scaffolding, not
student effort.

### "Did the intervention work?"

Use a pre/post comparison for the same students and the same measure. State the
intervention, the comparison group if any, and the confounders. A pre/post change
is not causation. If there is no comparison, say "consistent with" rather than
"caused by". Watch for regression to the mean when the intervention targeted the
lowest scores.

## Statistical guardrails

- Use **medians and interquartile ranges** for time, hints, and attempts. Use
  proportions for completion and participation.
- For a proportion with small n, report the **Wilson 95% interval**, not just the
  point estimate.
- Minimum reporting: **5** observations for a headline percentage, **3** for a
  peer median, **10** for a cohort trend. Below that, show counts and n.
- Do not run significance tests on tiny samples. Do not report a p-value as proof
  of a learning effect.
- Do not create a composite "success score" unless the weights are explicit,
  stable, and reviewed. Prefer the eight-dimension profile.
- Check for **selection bias**: pulse, quiz, and survey participation are optional;
  respondents may differ from non-respondents.
- Check for **missing sessions**: completion can exist without a session. Do not
  infer start behaviour from completion alone.
- Check for **duplicate rows** before aggregating. Define whether to keep the first,
  last, or best completion.
- Check **time zones** and week boundaries. Use UTC consistently.
- Watch for **multiple comparisons**: reviewing many exercises will produce
  apparent patterns by chance. Prefer consistent, multi-signal findings.

## Reporting rules

- Lead with the decision, then the evidence, then the limitation.
- Show `n` beside every percentage and every peer comparison.
- Use counts for small cohorts; suppress percentages that could identify a person.
- Use neutral language: "the evidence suggests", "early signal", "not enough
  history", "the data cannot tell us".
- Never write "at risk", "weak student", "failing", or "predicted to fail".
- Never rank students, instructors, or courses publicly.
- Separate the student's own progress from the cohort context.
- Give the student a route to correct their data and to opt out of surveys.

## Privacy and ethics

- The individual profile belongs to the student and their instructor. The dean
  sees aggregates.
- Use the minimum fields. Do not export names, emails, flags, credentials, or
  free-text comments unless the purpose requires them.
- Free-text comments can self-identify. Aggregate or paraphrase before sharing.
- Store analysis outputs with an owner, purpose, and retention date.
- Do not use the analysis for admissions, hiring, discipline, or high-stakes
  decisions.
- Follow the platform's consent and erasure rules.

## Templates

- `assets/individual-success-brief-template.md` — one student, one page, one next
  step.
- `assets/cohort-analysis-template.md` — distributions, exercise diagnostics, and
  course health without ranking.
- `assets/data-quality-memo-template.md` — what the data can and cannot support.

## Query patterns

See [`references/query-patterns.md`](references/query-patterns.md) for SQL/Python
examples for the individual profile, peer medians, exercise diagnostics, and
coaching queue.

## References

- `references/feeling-vs-doing.md` — the quick face indicator, the four
  combinations, UI rules, and ethics.
- `references/data-quality-and-statistics.md` — checks, small-sample methods, and
  confounders.
- `references/query-patterns.md` — SQL and Python starting points.
- `../opencyberrange-dean/references/individual-success-metrics.md` — the eight
  dimensions, formulas, diagnostic patterns, and current data gaps.

## Definition of done

An analysis is done when:

- the decision and unit of analysis are stated;
- the denominator and time window are explicit;
- the data-quality checks are recorded, including missing sessions and opt-in
  bias;
- the individual's own baseline is shown before the cohort comparison;
- every percentage has n, and small samples are labelled;
- the binding constraint is named, with alternative explanations considered;
- there is exactly one next step and one review date;
- the limitation is stated in one sentence;
- feeling is explicit self-report, labelled with text, and shown beside doing;
- no student, instructor, or course is ranked;
- the output is privacy-safe and uses the agreed templates.

## Related skills

- `opencyberrange-dean` — semester goals, programme view, forecasting, and the
  cooperative learning path.
- `opencyberrange-learning-impact` — retention, transfer, and responsible
  measurement.
- `opencyberrange-course-content-management` — course model and feedback loop.
- `opencyberrange-inclusive-curriculum` — access and representation in the
  scenario.
- `opencyberrange-design` and `opencyberrange-design-tester` — how the analysis
  appears in the UI.
- `opencyberrange-student-tester` — student-facing review.
