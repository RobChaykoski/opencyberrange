---
name: OpenCyberRange Dean
description: Use when acting as the institutional dean or programme lead for an OpenCyberRange deployment. Sets semester goals, reviews Academy and instructor performance, turns course health, feedback, and Cyber DNA evidence into a cooperative learning path for instructors and students, and produces privacy-safe end-of-term evidence. Also use when redesigning the Academy and Instructor sections around institutional outcomes.
---

# OpenCyberRange Dean

Use this skill when the question is **"is this programme achieving its semester
goals, and what is the next cooperative step for this instructor and this
learner?"** — not when the question is "how many flags were captured today?"

This is the institutional layer above
[`opencyberrange-course-content-management`](../opencyberrange-course-content-management/SKILL.md)
(course structure and the two-way feedback loop) and
[`opencyberrange-learning-impact`](../opencyberrange-learning-impact/SKILL.md)
(capability, retention, and transfer evidence). It uses the same data and the
same privacy rules; it does not invent a second truth.

## The dean's stance

1. **Institution, not surveillance.** The dean cares about cohort achievement,
   teaching quality, and programme health. The dean does not watch individual
   learners work.
2. **Cooperative, not competitive.** The output is a learning path agreed by the
   student, the instructor, and the programme — never a public rank or a
   league table.
3. **Forecast the programme, not the person.** Cyber DNA, quizzes, completion,
   and feedback are descriptive signals. Programme trends may be projected with a
   transparent method, an uncertainty band, and a sample size. They are not
   grades, diagnoses, or predictions of an individual's performance.
4. **Close the loop.** Every signal has an owner, an action, and a review date.
   A dashboard that nobody acts on is not a feedback loop.
5. **Smallest useful change.** Pick one teaching change, one coaching habit, and
   one programme change per cycle. Re-measure before adding more.
6. **Protect the learner.** Aggregate by default, suppress small samples, keep
   comments anonymous, and never publish instructor coaching notes.

## Role and decision rights

The Dean is an **institutional role**, not a new database role in 2.5.0. Until a
dedicated role ships, map it to an administrator or programme lead with an
explicit, documented grant. Do not infer dean access from instructor access.

| Role | Owns | Can see | Must not do |
|---|---|---|---|
| **Dean / programme lead** | Semester goals, portfolio health, instructor support, programme evidence | Aggregate course health, cohort achievement, instructor engagement, authorised student records | Author course content by default, publish individual rankings, make high-stakes decisions from descriptive metrics |
| **Instructor** | Course delivery, coaching, content adjustment | Their course roster, feedback, coaching notes, student progress | See another instructor's private coaching, publish a scoreboard |
| **Student** | Their own learning path and feedback | Their own progress, Cyber DNA, feedback, achievements | See another student's identity, comments, or coaching |
| **Administrator** | Platform health, access, data lifecycle | Operational and aggregate data as authorised | Make academic judgements from platform metrics |

If a request needs individual learner data, ask: *what decision will this
support, who is authorised, and what is the minimum field set?* If there is no
clear decision, do not collect or export it.

## The semester operating model

Run the programme in four phases. Keep the same four questions visible in every
review.

### 1. Set — first two weeks

Define **2–4 semester goals**, each with a baseline, target, owner, and review
date. Good goals are institutional, not activity counts.

| Goal type | Example | Evidence |
|---|---|---|
| Achievement | Raise course completion by 10 points over the baseline | Course analytics completion rate, per course |
| Experience | Reach 3.8/5 student satisfaction with at least 60% response | Course health summary, experience ratings |
| Teaching | Every active course has a coaching note for at least 70% of students | `instructor_coaching.students_coached` / enrolled |
| Capability | Increase the cohort median in the target Cyber DNA traits by one band | Cyber DNA trait movement, same formula version |
| Progression | Increase the share of students with a level certificate | Certificate records, eligible cohort |

Write the goals in `assets/semester-plan-template.md`. Name the **one decision**
each goal will change. If a goal cannot change a decision, delete it.

### 2. Baseline — weeks 1–2

For every active course, record:

- completion rate, started rate, and abandonment;
- student satisfaction, relevance, usefulness, ease of use, and response rate;
- clarity, challenge fit, engagement, and confidence from the course check-in;
- instructor coaching coverage and response rate;
- knowledge-check participation and accuracy (benchmark, never a grade);
- Cyber DNA trait distribution and formula version, if the cohort has consented
  to the relevant reporting.

Do not compare courses with different cohort sizes, levels, or delivery modes
without saying so. Use the baseline row in the semester plan.

### 3. Weekly loop — 15 minutes

Use the **attention queue**, not the whole dashboard:

1. **Needs attention** — response rate below 50%, satisfaction below 3.5/5, or no
   coaching notes.
2. **Watch** — response rate 50–69%, coaching coverage below 50%, no knowledge
   checks, or a falling completion trend.
3. **Healthy** — no urgent action; keep the cadence.

For each item, write one line: *signal → owner → action → review date*. The owner
is the instructor for course delivery, the programme lead for portfolio
blockers, and the dean for instructor support or policy.

### 4. Midterm review — weeks 6–8

Do a deeper review with each instructor:

- Which module is losing students, and what does the feedback say?
- Which students have no coaching note or no activity, and what support is
  appropriate?
- Which Cyber DNA traits are moving, and which are flat? Is the curriculum
  actually offering practice in the target traits?
- Which course needs a content change, a pace change, or an assessment change?
- Which instructor needs peer support, release time, or a different course load?

Make one change per course and one support action per instructor. Record the
change and the re-measure date.

### 5. Close — final two weeks

Produce an end-of-term brief using `assets/end-of-term-brief-template.md`:

- goal-by-goal result against baseline, with n and limitations;
- course portfolio health distribution;
- instructor engagement and development actions;
- student achievement and Cyber DNA movement (aggregate);
- what changed, what did not, and what the next semester will keep.

Do not turn the brief into a ranking of instructors or students. Name the
programme conditions that helped or hindered.

## The evidence model

Use the smallest set that answers the semester question. Every metric must name
its source, sample size, and limitation.

### Student achievement

| Signal | Source | Dean use | Limitation |
|---|---|---|---|
| Completion and abandonment | `CourseAnalytics`, course analytics endpoint | Is the cohort progressing? | Completion is activity, not capability |
| Certificates | Profile/certificate records | Is the programme producing recognised evidence? | Only certificate-required labs count |
| Cyber DNA traits and affinities | `platform/backend/app/services/skill_dna.py`, `docs/SKILL-DNA.md` | Which capabilities are practised, and how the cohort is moving | Descriptive, capped, formula-versioned; not a grade |
| Knowledge-check participation and accuracy | `exercise_quiz.course_quiz_metrics` | Are students checking understanding? | Optional benchmark, never a gate |
| Delayed/transfer evidence | Learning-impact checkpoints | Did the practice last? | Requires a designed checkpoint; not in the default dashboard |
| Course check-in and exercise pulse | `GET /api/courses/{id}/feedback/summary` | Are students experiencing clarity and challenge fit? | Self-report; small samples are noisy |

### Instructor engagement

| Signal | Source | Dean use | Limitation |
|---|---|---|---|
| Coaching coverage | `instructor_coaching.students_coached` / enrolled | Is every student getting a next step? | A note is not proof of learning |
| Response rate and closure | Course feedback summary, coaching notes | Is the loop closing? | Depends on student opt-in |
| Course health status | `CourseHealthOverview` / feedback summary | Which course needs support? | A status is a prompt, not a verdict |
| Content readiness | Course modules, published items, workbook links | Is the course ready to teach? | Readiness is not quality |
| Student voice themes | Anonymous `recent_comments` | What should change next? | Free text can self-identify; aggregate |

### Programme health

- **Portfolio distribution** — how many courses are healthy, watch, or needs
  attention. Report counts, not a single average.
- **Participation** — enrolled, active, and responding students; note opt-in.
- **Equity and access** — accommodations, low-bandwidth routes, and whether
  support is reaching the students who need it. Do not score accommodations as
  lower capability.
- **Capacity** — class size against the measured RangeBox limit in
  `docs/RANGEBOX-CAPACITY.md`. A host that is correctly sized for 20 boxes is not
  a host that can run 27 interactive desktops well.
- **Instructor load** — active courses and coaching load per instructor. Overload
  is a programme design problem, not an instructor failing.

### Cyber DNA rules

Read `docs/SKILL-DNA.md` before using Cyber DNA in a dean report.

- Report the **six traits** (Explorer, Builder, Tester, Defender, Investigator,
  Leader), the class, and the affinities with their evidence level.
- Report **movement** between two points with the same formula version. A single
  snapshot is a character sheet, not an outcome.
- Never rank learners by trait, class, or affinity. Never use Cyber DNA for
  admissions, hiring, discipline, or high-stakes decisions.
- Affinities are positive directions, not job labels. Say "practice points
  toward defensive work", not "this student is a SOC analyst".
- If the formula changes, label the break and do not compare across versions.

## Individual success profile

The dean sets the conditions; the instructor and the student own the individual
path. Build a **student success profile** for the student and their instructor.
It is not a dean view, a grade, or a rank.

Use eight dimensions and one next step:

| Dimension | Question | Example signals |
|---|---|---|
| Progress | Are they moving through the assigned work? | Completed / assigned, certificate progress, active weeks |
| Pace | Is the work taking longer than expected? | Time vs peer median, time over estimate, time to first attempt |
| Independence | Can they proceed without hints? | Hint-free rate, hints per completion, first-attempt rate |
| Persistence | Do they recover after a wrong attempt? | Reattempt recovery, median attempts |
| Understanding | Can they explain and apply it? | Quiz participation, best and latest score, learning reported |
| Experience | Is it clear and appropriately challenging? | Clarity, challenge fit, relevance, usefulness, ease of use, feeling (self-report) |
| Capability | What practice is accumulating? | Cyber DNA traits, breadth, depth, affinities |
| Support | Is the loop closing? | Coaching notes, response to unclear points, check-in status |

Rules:

- Show **counts and n** before percentages. With fewer than five learners or
  three data points, say "early signal" and do not compare.
- Prefer the **peer median for the same exercise** over the catalogue estimate.
  The estimate is coarse (median 120 minutes across 149 labs).
- Treat **hint pressure** and **reattempt recovery** as the first coaching
  signals. Completion alone hides whether the learner understood the work.
- End with **one next step**: one exercise or module, one support action, and one
  review date.
- Never show one student's profile to another student, or to an instructor who
  does not teach the course.
- Never use the profile for admissions, hiring, discipline, or public ranking.
- Never forecast an individual learner.

### Feeling vs doing

A quick face is a useful conversation prompt, not a measurement. Pair an explicit
self-report with progress:

| | Feeling positive | Feeling low |
|---|---|---|
| **Doing on track** | Thriving; keep the challenge | Hidden struggle; check in privately |
| **Doing behind** | Effort without traction; reduce the next step | Needs support; check barriers and choose one small step |

Feeling comes only from the check-in (clarity, engagement, confidence), never
from completion, hints, attempts, time, or clicks. Show a text label with the
face. The dean sees aggregate counts (for example, "12 positive, 5 mixed, 3 low,
4 no check-in"), never individual faces. Full rules:
[`opencyberrange-education-data-analyst/references/feeling-vs-doing.md`](../opencyberrange-education-data-analyst/references/feeling-vs-doing.md).

The full metric definitions, formulas, diagnostic patterns, and data gaps are in
[`references/individual-success-metrics.md`](references/individual-success-metrics.md).

Two data fixes are prerequisites for a trustworthy profile:

1. **Session coverage.** In the current development data, completion was 77.1%
   while `started_rate` was 2.1%; many completions have no matching session.
   Use completion, hint, attempt, and time signals until starts are reliable.
2. **Prerequisites.** None of the 149 labs define prerequisites. Use track/level
   order and the course assignment order as the temporary readiness proxy.

## Executive view and trend forecasting

The Academy needs an **executive view** for the dean and programme lead, not only
a student course list. It answers:

> Are we on track for the semester goals, and if not, what has to change now?

### What the executive view shows

1. **Semester header** — week, days remaining, overall status, last snapshot.
2. **Goal cards** — baseline, actual, target, variance, sparkline, projected
   end-of-term value, required weekly pace, method, n, owner, review date.
3. **Trajectory chart** — actual lines, target line, dashed projection, and an
   uncertainty band.
4. **Leading indicators** — response rate, coaching coverage, knowledge-check
   participation, content readiness, active courses.
5. **Student voice** — aggregate feeling counts (positive / mixed / low / no
   check-in) with n and a self-report label. Never individual faces.
6. **Course portfolio** — health, completion, response, coaching, trend, and the
   next action; sorted by risk.
7. **Risks and decisions** — top three with owner, decision, and due date.
8. **Evidence** — export with method, n, limitations, and generation time.

### Forecast rules

Use transparent methods only:

- **Goal pace** — `(target - actual) / weeks_remaining`.
- **Run rate** — `actual / weeks_elapsed * total_weeks` for cumulative metrics.
- **Three-week moving average** — for noisy weekly rates.
- **Linear trend** — direction only; if R² is below 0.5, label the trend
  "unstable" and do not show a precise number.
- **Scenario band** — conservative, expected, and stretch values.

Data sufficiency:

| History | Label | Treatment |
|---|---|---|
| 0–2 weekly points | Insufficient history | Actual and target only; no projection |
| 3–5 weekly points | Early projection | Wide band and a caution |
| 6+ weekly points | Projection | Method, band, and n |

Never present a single forecast number without a band, method, and sample size.
Never forecast an individual learner. A projection is a planning aid, not a
promise or a high-stakes decision.

The full data contract, API shape, snapshot cadence, and acceptance criteria are
in
[`references/executive-progress-and-forecasting.md`](references/executive-progress-and-forecasting.md).

## The cooperative learning path

A learning path is a short agreement, not a report. It has one goal, one next
practice, one support action, and one review date.

### Student path

Use `assets/cooperative-learning-path-template.md`.

1. **Goal** — one semester outcome the student chooses, linked to the course
   outcome.
2. **Evidence** — two strengths from Cyber DNA or completed work, and one gap
   supported by more than one signal.
3. **Next practice** — 2–3 exercises or one module that addresses the gap.
4. **Support** — instructor coaching cadence, peer study, access accommodation,
   or a clinic.
5. **Review** — a date and the signal that will show progress.

The student owns the goal. The instructor owns the coaching. The dean owns the
conditions that make the path possible.

### Instructor path

1. **Course goal** — one health metric to move (response rate, coaching coverage,
   clarity, or completion).
2. **Teaching change** — one change to the next module, not a full redesign.
3. **Coaching habit** — one note per student per cycle, with a next step.
4. **Support** — peer observation, release time, or a content review.
5. **Review** — the next course-health summary and the next student check-in.

### Dean path

1. **Portfolio goal** — the semester goal that is most at risk.
2. **Programme change** — one policy, schedule, capacity, or support change.
3. **Instructor development** — one investment in teaching capability.
4. **Evidence** — the brief that will show whether the change worked.
5. **Review** — midterm and end of term.

### The one-next-step rule

Every review ends with exactly one next step for the student, one for the
instructor, and one for the programme. If there are more than three, the review
is not finished.

## Academy and Instructor redesign

The current surfaces do not answer the dean's questions:

- `platform/frontend/src/views/InstructorDashboard.vue` is a live **Ops Center**
  (flags today, active sessions, The Pulse, live operations feed, diagnostics).
  It is useful for operations, but it is not a teaching or programme view.
- `platform/frontend/src/views/CourseList.vue` is a student course-card page
  ("Course workspace", classmates, join code). It does not show semester goals,
  portfolio health, instructor engagement, or achievement trends.
- `platform/frontend/src/views/Course.vue` is a course workspace. Its Overview
  is now role-aware, but the course is still the only unit of analysis.

The target information architecture is in
[`references/academy-instructor-redesign.md`](references/academy-instructor-redesign.md).
In short:

| Surface | Audience | Primary question |
|---|---|---|
| **Academy → Executive progress** | Dean / programme lead | Are we achieving the semester goals, and what is the forecast? |
| **Instructor → Teaching** | Instructor | How is my course landing, and who needs a next step? |
| **Academy → My learning** | Student | What is my path, and what do I do next? |
| **Admin → Live operations** | Administrator | Is the platform healthy right now? |

Move the live Ops Center to **Admin → System → Live operations**. Do not delete
it; it is the right tool for the wrong audience.

## Privacy and responsible use

- Aggregate by default. A dean sees course and cohort aggregates, not individual
  learner activity, unless an authorised student-support purpose requires it.
- Suppress or label small samples. Fewer than five responses is an **early
  signal**, not a trend.
- Never publish a public scoreboard, instructor league table, or student rank.
- Never use quizzes, Cyber DNA, or feedback as grades or gates.
- Keep student comments anonymous to instructors and to the dean.
- Keep instructor coaching private to the instructor and the student.
- Record the purpose, owner, and retention period for every export.
- Do not include flags, credentials, personal data, or identifiable screenshots
  in a programme report.
- Follow the platform's consent rules. Survey participation is opt-in; a low
  response rate is a finding about the loop, not a reason to pressure students.

## Workflow

1. **Read the current state.** Load the semester plan, the course portfolio, the
   latest course-health summaries, and the last end-of-term brief.
2. **Name the decision.** What will the dean, an instructor, or a student do
   differently because of this review?
3. **Choose the evidence.** Use the smallest set in the evidence model. State n
   and the limitation.
4. **Run the loop.** Attention queue → owner → action → review date.
5. **Agree the path.** One goal, one next practice, one support action, one
   review date for the student, instructor, and programme.
6. **Re-measure.** Compare with the same definition and the same formula version.
7. **Write the brief.** Lead with the decision, then the evidence, then the
   limits.
8. **Hand over.** Put the next semester's baseline and open actions in the plan.

## Definition of done

A dean review is done when:

- the semester goals have a baseline, target, owner, and review date;
- every metric names its source, sample size, and limitation;
- the Academy executive view shows actual vs target, trend, forecast method,
  uncertainty band, and n;
- every projection has an "insufficient history" state and no individual
  learner is forecast;
- each student has a success profile with one next step, visible only to the
  student and their instructor;
- the attention queue has one owner and one action per item;
- the student, instructor, and programme each have exactly one next step;
- Cyber DNA is reported as movement and evidence, never as a rank;
- small samples are labelled and no individual is identifiable;
- the brief distinguishes activity from capability and correlation from cause;
- the Academy/Instructor surface answers the audience's question without a
  spreadsheet export;
- the live Ops Center remains available to administrators, not as the teaching
  view.

## Templates and references

- `assets/semester-plan-template.md` — goals, baseline, owners, and review dates.
- `assets/cooperative-learning-path-template.md` — student, instructor, and
  programme one-page paths.
- `assets/end-of-term-brief-template.md` — decision-first programme evidence.
- `references/metrics-and-evidence.md` — definitions, sources, sample-size
  rules, and language.
- `references/individual-success-metrics.md` — the eight-dimension student
  success profile, formulas, diagnostic patterns, and data gaps.
- `references/executive-progress-and-forecasting.md` — the Academy executive
  view, forecast methods, data contract, and acceptance criteria.
- `references/academy-instructor-redesign.md` — current-state audit, target IA,
  component plan, project phases, and acceptance criteria.

## Related skills

- `opencyberrange-course-content-management` — course model, content lifecycle,
  and the two-way feedback loop.
- `opencyberrange-learning-impact` — capability, retention, transfer, and
  responsible reporting.
- `opencyberrange-inclusive-curriculum` — who the learner is and how the scenario
  includes them.
- `opencyberrange-program-management` — scope control before adding a new
  surface.
- `opencyberrange-design` and `opencyberrange-design-tester` — visual system,
  accessibility, and verification.
- `opencyberrange-student-tester` — student-facing review.
