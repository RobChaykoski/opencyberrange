# Academy, instructor, and reporting IA

Status: design proposal for the next feature line. The current 5.3.0 build is
unchanged. This document follows the project design, education-data, and
program-management skills: preserve routes and permissions, use existing tokens,
measure learning rather than rank learners, and aggregate before identifying.

## Current state (audit)

- **Admin** is one flat tab row: Users, Pending, Courses, Exercises, Live
  activity, System, Settings. Seven peer items with different jobs, and
  "Courses" means both catalogue management and the instructor workspace.
- **Academy** in the sidebar is only Courses and Exercises. Workbooks are
  reachable from the dashboard, not the Academy section.
- **Instructor** has two top tabs: Courses (which then has six sub-tabs) and
  Exercises. There is no cross-course view, so an instructor with several
  courses cannot see the programme as a whole.
- **Reports** already have course cards, course selection, a skill chart, and
  signed exports. Missing: date-range control, cohort/student filters, and
  trend lines over time.
- Course assignments are per-course lab rows. There is no first-class
  "cohort" or "exercise group" that a requirement can target.

## Proposed navigation

### Admin

| Group | Items | Job |
|---|---|---|
| **People** | Users, Pending approvals, Access review | Identity and account state |
| **Learning** | Courses, Exercise library, Requirements, Workbooks | Content and delivery |
| **Operations** | Live activity, System (Health/Metrics/Backups/Integrity), Reviews queue | Run the service |
| **Configuration** | Platform settings, Identity providers, LTI platforms, Modules | Configure once |

Keep the existing tab keys and routes (`?tab=users`, `?tab=courses`, …) so links
and tests do not break; group them visually and rename labels only.

### Academy (learner and instructor sidebar section)

- **My learning**: Dashboard, My courses, Workbooks
- **Explore**: Exercise library, Events, Celebration wall
- **Tools**: CyberChef, RangeBox

Move Workbooks into Academy, and stop mixing programme events with a learner's
own courses.

### Instructor

Top level:

1. **Overview** — all my courses, trends, and actions.
2. **Courses** — list, create, and open a course.
3. **Learners** — cross-course roster with course/cohort filters.
4. **Reports** — programme trends and exports.
5. **Reviews** — pending human-review queue across courses.
6. **Settings** — defaults and notification preferences.

Course workspace (opened from Courses):

| Tab | Contents |
|---|---|
| Overview | Course health cards, trend chart, next actions |
| Learners | Enrolled learners, cohort, consent/accommodation flags, history |
| Exercise plan | Exercise groups, requirements, assignment matrix |
| Reports | Course diagnostics, exercise health, coaching queue |
| Reviews | Human-review requests for this course |
| Settings | Course details, retention, staff, visibility |

## Requirements and multiple exercise groups

The missing concept is a **cohort** (a learner group inside one course) and an
**exercise set** (an ordered group of exercises). A requirement connects them.

```text
Course
  ├── Cohort A (Grade 9) ── Requirement: Core set, 80% by 2026-12-01
  ├── Cohort B (Grade 10) ─ Requirement: Advanced set, 5 exercises by 2027-01-15
  └── Cohort C (staff) ──── Requirement: Awareness set, optional

Exercise set "Core"      = [web-1-1, web-1-2, linux-1-1, ...]
Exercise set "Advanced"  = [web-3-1, linux-4-1, ...]
```

Data model (new migration):

- `course_cohorts(id, course_id, name, description, created_at)`
- `course_cohort_members(cohort_id, user_id)` with a unique pair
- `exercise_sets(id, course_id, name, description, sort_order)`
- `exercise_set_items(set_id, lab_id, sort_order, required)`
- `course_requirements(id, course_id, cohort_id, set_id, rule_type,
  threshold, due_at, note)` where `rule_type` is `complete_all`,
  `complete_percent`, or `complete_count`

Resolution rule at launch: a learner may start an exercise when it appears in a
set targeted at any cohort they belong to, or when individually assigned as
today. Existing `course_lab_assignments` remain supported and appear as an
implicit "individual assignments" group. Reports show requirement coverage by
cohort and flag learners with no matching cohort.

## Reporting and trends

Metric contracts follow the education-data skill: always state unit, population,
denominator, and window.

**Cards (per course and across courses):**

- Enrolled learners; learners with at least one start (coverage denominator).
- Exercise completion: completed learner–exercise pairs / assigned pairs.
- Evidence coverage: learners with a completion or review decision.
- Median time to completion (only for completed pairs; show n).
- Attempts per completion and hint use per completion.
- Review requests: pending, approved, rejected.
- "Needs a next step" list: exercises with low start coverage, high attempt
  counts, high hint use, or many pending reviews. These are content/pacing
  signals, not learner rankings.

**Trend charts:**

- Completion rate by week, with the denominator shown in the tooltip.
- Active learners by day/week.
- Starts vs completions by exercise group.
- Attempts and hints per completion over time.
- Review volume and decision time.

**Controls:**

- Date presets (7/30/90 days, term) plus a calendar range.
- Course multi-select and cohort select.
- Exercise set / individual exercise select.
- Student search only inside a course the user can manage.
- Compare toggle: current window vs previous equal-length window.

Charts are inline SVG or the existing chart library, using current tokens. No
new chart framework.

## Privacy and safety

- Aggregate by default. Suppress any cohort or slice with fewer than **5**
  learners; show "suppressed (n<5)" rather than a value.
- Never rank learners. Individual views are for the learner and the instructor
  who manages that course, never a cross-course leaderboard.
- Respect privacy mode: mask names/emails in tables, tooltips, exports, and
  chart labels; pseudonymous IDs only.
- Exports require a reason (already implemented) and inherit suppression.
- Do not expose another course's learners through an instructor filter.
- Sampling and trend data are aggregate; the metrics table added in 5.3.0 has no
  learner identifiers.
- Retention: report aggregates follow the course retention date; individual
  history follows the existing erasure/retention rules.

## Phases

1. **Navigation and labels (1–2 days)** — group Admin, move Workbooks into
   Academy, add the instructor Overview shell. Routes and APIs unchanged.
2. **Cross-course instructor overview (3–4 days)** — cards + trend chart using
   the existing report payloads; date presets and course filter.
3. **Cohorts, exercise sets, and requirements (5–7 days)** — migration, admin/
   instructor editors, assignment resolution, coverage report.
4. **Reporting depth and privacy (4–5 days)** — student/exercise filters,
   previous-window comparison, suppression rules, export updates.

Each phase is independently shippable. Phase 3 changes assignment semantics and
needs its own migration and regression tests.

## Open decisions

1. Are "exercise groups" **cohorts inside one course** (recommended: one course
   can serve Grade 9 and Grade 10 with different sets), or **separate courses**
   per group?
2. Should a requirement be completion-only, or also score/time/hint thresholds?
3. Is the suppression threshold 5 appropriate for the institution?
