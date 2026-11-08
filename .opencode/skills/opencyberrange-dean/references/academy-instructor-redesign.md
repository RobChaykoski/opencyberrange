# Academy and Instructor redesign

The current Academy and Instructor surfaces were built for a student course list
and live platform operations. They do not answer the questions a dean,
programme lead, or instructor now needs to ask.

## Current-state audit

| Surface | File | What it shows | Problem |
|---|---|---|---|
| Academy landing | `platform/frontend/src/views/CourseList.vue` | Student course cards, classmates, join code | No programme goals, portfolio health, instructor engagement, achievement trend, or forecast |
| Instructor landing | `platform/frontend/src/views/InstructorDashboard.vue` | "Ops Center": flags today, active sessions, The Pulse, live feed, diagnostics | Live operations, not teaching intelligence; no course health or coaching queue |
| Course workspace | `platform/frontend/src/views/Course.vue` | Overview, Content, Feedback, Achievements, Analytics | Course is the only unit; no semester or programme context |
| Course analytics | `platform/frontend/src/components/CourseAnalytics.vue` | Completion, time, hints, attempts, feedback, exercise signals | Useful course detail, but buried in one course and not executive |
| Course feedback | `platform/frontend/src/components/CourseFeedbackPanel.vue` | Check-in, coaching, quiz experience, anonymous comments | Good loop; no quick feeling/doing view or programme roll-up |
| Reports | `platform/frontend/src/views/Admin.vue` and report views | Exports, all-course reports | Not a semester executive view; no forecast |

The live Ops Center is valuable. It is the right tool for an administrator, not
the primary teaching view.

## Target information architecture

| Route / surface | Audience | Primary question | Landing content |
|---|---|---|---|
| **Academy → Executive progress** | Dean / programme lead | Are we on track, and what is the forecast? | Semester header, goal cards, trajectory, leading indicators, student voice, portfolio, risks |
| **Academy → Course portfolio** | Dean / programme lead | Which course needs support? | Course table, health, response, coaching, next action |
| **Instructor → Teaching** | Instructor | How is my course landing, and who needs a next step? | Course health, coaching queue with feeling/doing, content readiness, next actions |
| **Academy → My learning** | Student | What is my path, and what do I do next? | Progress, next exercise, Cyber DNA growth, feedback, achievements |
| **Admin → Live operations** | Administrator | Is the platform healthy now? | The existing Ops Center, moved unchanged |

Routes can be tabs on the existing pages. Keep `/courses` working for students;
add staff-only tabs rather than breaking deep links.

## Executive progress view

Use the order below. The first screen must answer "are we on track?".

### 1. Semester header

- Semester name, week number, days remaining.
- Overall status: `on track`, `watch`, `off track`, `insufficient data`.
- Last snapshot date and the method note.

### 2. Goal cards

Two to four cards. Each shows:

- baseline, actual, target, variance;
- a six-to-eight-week sparkline;
- projected end-of-term value;
- gap and required weekly pace;
- method, n, owner, review date;
- a status chip with a reason.

If there are fewer than three weekly points, show "insufficient history" and no
projection. A projection needs a band, a method, and a sample size.

### 3. Trajectory chart

- One line per selected goal metric.
- Solid actual line, dashed projection, shaded band.
- Target line.
- A text summary and a table alternative.

### 4. Leading indicators

- Response rate.
- Coaching coverage.
- Knowledge-check participation.
- Content readiness.
- Active courses.

These move before completion and satisfaction.

### 5. Student voice

- Aggregate feeling counts: positive, mixed, low, no check-in.
- n and a self-report label.
- Never individual faces or names in the dean view.

### 6. Course portfolio

One row per course:

- course code and name;
- health status and reason;
- completion, response rate, coaching coverage;
- knowledge-check participation;
- trend direction and projection state;
- next action and owner.

Sort by risk, not by name. Do not rank instructors.

### 7. Risks and decisions

Top three items with decision, owner, due date, and the signal that will show
whether the decision worked.

### 8. Evidence

Export with method, n, limitations, generation time, and the source snapshot.
The export is a programme document, not a learner record.

## Instructor teaching view

The instructor landing should answer "what do I teach next?" not "what is the
platform doing?".

### Course health strip

- My active courses.
- Completion, response rate, coaching coverage.
- Students with no check-in.
- Students with no coaching note this cycle.
- Courses needing attention.

### Coaching queue

One row per student, private to the instructor:

- progress (completed / assigned);
- feeling (self-reported) with a text label;
- doing state (on track / building / needs a step);
- the combination insight (thriving, hidden struggle, effort without traction,
  needs support);
- last coaching note and next review date;
- one suggested action.

Use the feeling/doing rules in
`opencyberrange-education-data-analyst/references/feeling-vs-doing.md`.

### Course content readiness

- Published modules and items.
- Missing workbook links or lab slugs.
- Upcoming assignments.
- Courses with no knowledge check.

### Next actions

- One course change.
- One coaching habit.
- One content fix.
- One review date.

## Student view

- My learning path and next exercise.
- Progress by course and certificate.
- Cyber DNA traits, movement, and affinities.
- Feedback status and instructor notes addressed to me.
- Achievements.
- One next step.

Do not show other students, public ranks, or instructor-only coaching.

## Component plan

| Component | Responsibility | Reuse |
|---|---|---|
| `ProgrammeOverview.vue` | Mode-aware programme/teaching summary | `CourseHealthOverview`, `CourseFeedbackPanel` data |
| `SemesterHeader.vue` | Week, days remaining, status, snapshot | New |
| `GoalCard.vue` | Baseline, actual, target, projection, band, n | New |
| `TrajectoryChart.vue` | Actual, target, projection, band, table alternative | New |
| `PortfolioTable.vue` | Course rows and risk sort | `CourseAnalytics` data |
| `AttentionQueue.vue` | Signals, owner, action, review date | New |
| `StudentVoiceStrip.vue` | Aggregate feeling counts | `CourseFeedbackPanel` |
| `StudentSuccessPanel.vue` | Eight-dimension individual profile | `CourseFeedbackPanel` students array |
| `FeelingDoingBadge.vue` | Face + text + accessible label | Used by the coaching queue |
| `EvidenceExport.vue` | Method, n, limitations, generation time | Existing report/export plumbing |

Build `FeelingDoingBadge.vue` first: it is small, reusable, and immediately
useful in the existing coaching list.

## Data mapping

| UI element | Source | Notes |
|---|---|---|
| Course list | `GET /api/courses/` | Admin sees all; instructor sees their courses; student sees enrolled |
| Course health | `GET /api/analytics/courses/{id}/overview` | Requires instructor/admin |
| Exercise diagnostics | `GET /api/analytics/courses/{id}/exercises` | Per-exercise completion, hints, attempts, time, RAG |
| Feedback and coaching | `GET /api/courses/{id}/feedback/summary` | Students see own; instructors see roster and aggregates |
| Individual profile | New course-scoped success endpoint or the feedback `students` array | Student own; instructor their course |
| Cyber DNA | Profile/Skill DNA endpoint | Formula version required |
| Goals and snapshots | New `semesters`, `programme_goals`, `programme_health_snapshots` | See the executive forecasting reference |
| Live operations | Existing instructor dashboard endpoints | Move to Admin, keep unchanged |

## Project phases

### Phase 1 — Data contract and truth

- Add `semesters`, `programme_goals`, `programme_health_snapshots`.
- Add a weekly snapshot job.
- Fix session-start coverage and add `prerequisites` to lab metadata.
- Define metrics in one place and test the denominators.
- Deliverable: a trusted weekly series.

### Phase 2 — Executive API

- `GET /api/programme/overview?semester_id=...`.
- Goal pace, run rate, moving average, trend direction, band.
- Permission tests and small-sample states.
- Deliverable: the data behind the executive view.

### Phase 3 — Academy executive view

- Semester header, goal cards, trajectory, leading indicators, student voice,
  portfolio, risks, export.
- Empty, loading, error, insufficient-history, and small-cohort states.
- Deliverable: the dean landing page.

### Phase 4 — Instructor teaching view

- Course health strip, coaching queue, content readiness, next actions.
- Feeling/doing badge and accessible labels.
- Move the Ops Center to Admin with a redirect.
- Deliverable: the instructor landing page.

### Phase 5 — Student path view

- My learning path, next exercise, Cyber DNA growth, feedback.
- Deliverable: the student landing page.

### Phase 6 — Evidence and verification

- End-of-term brief, export, UI smoke, screenshots, accessibility checks.
- Deliverable: release evidence.

## Acceptance criteria

- The Academy landing answers "on track / watch / off track / insufficient data"
  above the fold for a dean.
- Every goal card shows baseline, actual, target, variance, projection, method,
  band, n, owner, and review date.
- Every projection has an insufficient-history state.
- The course portfolio sorts by risk and shows the next action.
- The instructor view shows a private coaching queue with feeling and doing.
- The student view shows only their own data.
- No public ranking, instructor league table, or individual forecast.
- The live Ops Center remains available under Admin.
- Mobile (390 px), keyboard, screen reader, dark/light themes, and reduced motion
  are verified.
- The export includes method, n, limitations, and generation time.

## Privacy and authorization

- Dean/programme lead: aggregate programme and course data; individual records
  only with an explicit support purpose and role grant.
- Instructor: their course roster, feedback, coaching, and student profiles.
- Student: their own profile and feedback.
- Administrator: platform operations, not academic judgement.
- Never expose a student's feeling, comment, or coaching to another student.
- Never use the executive view to rank instructors or students.

## Definition of done

- The surface answers its audience's question without a spreadsheet export.
- The data-quality caveats are visible, not buried.
- The feeling/doing indicator is self-report-only, labelled, and accessible.
- The live Ops Center is still available to administrators.
- The documentation and release notes describe the move and the new views.
