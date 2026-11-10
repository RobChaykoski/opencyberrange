# V2 Learning Analytics and Research Dashboard

> **Version note:** This document keeps its historical V2/V3 filename. The
> current platform release is **2.6.0**; Community / Academic, Professional, and
> Enterprise are edition profiles on that release.

Status: Phase 1 implemented in this development tree; Phase 2 and Phase 3 planned

## Purpose

V2 should help learners understand their own progress, help educators improve teaching, and give approved researchers de-identified evidence about how people learn cybersecurity. It must not become a high-stakes prediction or ranking system.

The dashboard should answer three different questions for three different audiences:

- **Learner:** How am I improving, where am I stuck, and what should I try next?
- **Educator:** Where is the cohort struggling, which exercises are too easy or too hard, and what should I change?
- **Researcher:** What patterns are measurable across cohorts, with consent and privacy safeguards?

## Principles

1. **Within-person growth over cross-person ranking.** Students see their own trajectory, not a public league table.
2. **Aggregate before identifying.** Educator and research views use minimum cohort sizes and suppress small groups.
3. **No automated high-stakes decisions.** Analytics may suggest support, never grade, punish, or label a learner.
4. **Consent and purpose limitation.** Research exports require explicit consent and an approved research purpose.
5. **Define every metric once.** One metric dictionary powers the UI, exports, and documentation.
6. **Prefer medians and distributions.** Time and attempt data are skewed; medians and IQR are safer than averages alone.
7. **Show uncertainty.** Small samples, missing data, and partial attempts are labelled rather than hidden.

## Existing data available

| Source | Useful fields |
| --- | --- |
| `lab_completions` | completed_at, attempts, hints_used, time_spent_minutes, started_at |
| `flag_attempts` | attempt timestamps, correctness, lab |
| `lab_sessions` | started_at, stopped_at, status, lab, user |
| `activity_events` | lab started/stopped/completed, hint events, timestamps |
| `quiz_attempts` | score, correct, total, passed, taken_at |
| `course_enrollments` | course, learner, enrolled_at, seat |
| `course_lab_assignments` | which exercises belong to a course |
| `course_completion_resets` | invalidated completions after instructor reset |
| `achievements` | achievement type, course, lab, awarded_at |

V2 should add a small number of analytics-specific structures if needed:

- Nightly aggregate snapshot tables for fast dashboards.
- An explicit research-consent record separate from survey consent.
- Optional exercise hint timestamps if hint usage needs event-level timing.

## Core metric definitions

The authoritative metric contract, consent boundaries, retention schedule,
research governance, and export schemas live in
[Analytics governance](ANALYTICS-GOVERNANCE.md). The minimum event envelope and
Exercise Health fields are in
[Analytics event schema](ANALYTICS-EVENT-SCHEMA.md). This section keeps the
short definitions used by the dashboard.

### Completion

- **Assigned completion rate:** completed assigned exercises / assigned exercises.
- **Started completion rate:** completed exercises / exercises with at least one session.
- **Completion funnel:** not started → started → attempted flag → completed.
- **Time to completion:** completion timestamp minus first session or start time, capped and outlier-flagged.

### Time spent

- Use `time_spent_minutes` where present, otherwise active session duration.
- Report **median**, **interquartile range**, and **percentage over estimated duration**.
- Separate active lab time from long idle gaps where session data allows.

### Hint usage

- **Hints per completed exercise:** total hints / completions.
- **Hint-free completion rate:** completions with zero hints / completions.
- **Hint dependency signal:** change in hints per exercise from a learner's first exercises to later exercises.
- **Exercise hint pressure:** share of learners needing at least one hint on a specific exercise.

### Reattempts

- **Attempts per completion:** total flag attempts / completions.
- **First-attempt success rate:** completions with attempts = 1 / completions.
- **Reattempt recovery rate:** learners who fail once and later complete.
- **Exercise reattempt burden:** median attempts and share requiring 3+ attempts.

### Success rates

- **Exercise success rate:** completions / learners who started.
- **Cohort success rate:** learners completing / learners assigned.
- **Quiz pass rate:** passed quiz attempts / quiz attempts.
- **Achievement attainment:** learners earning a badge / eligible learners.

### Student growth indicators

Growth should be calculated within a learner and require a minimum amount of evidence.

- **Hint reduction:** hints per exercise in the most recent N exercises vs the first N.
- **Attempt efficiency:** first-attempt rate in recent work vs earlier work.
- **Time efficiency:** median time vs estimated duration in recent work vs earlier work.
- **Persistence:** completion after two or more failed attempts.
- **Breadth:** number of tracks or skill areas with at least one completion.
- **Consistency:** active weeks with meaningful progress.
- **Recovery:** improvement after a difficult exercise or a low quiz score.

Each indicator needs a confidence label: `emerging`, `developing`, `consistent`, or `insufficient evidence`.

## Layer 2: competency growth by domain

Track competency evidence for six domains:

| Domain | Track mapping |
| --- | --- |
| Web Security | `web`, `software-security` |
| OSINT | `osint` |
| Forensics | `forensics` |
| Malware | `malware` |
| OT / ICS | `ot` |
| AI Security | `ai` |

For each domain report:

- Started and completed exercises.
- Completion rate.
- Median time.
- Hint-free and first-attempt rates.
- Growth status and evidence level (`no evidence`, `early`, `growing`, `strong`).

These are evidence summaries, not mastery badges. A learner with no evidence in a domain should see “no evidence yet”, not a zero score.

## Activity analytics

Capture these automatically from existing activity:

| Metric | Source | Use |
| --- | --- | --- |
| Lab starts | `lab_sessions` | Popularity and reach |
| Completions | `lab_completions` | Success |
| Abandonment rate | started learner-lab pairs without a completion | Difficulty or friction |
| Average/median completion time | `lab_completions.time_spent_minutes` | Effort |
| Learning hours | timed completions plus bounded session windows for unfinished exercises | Cumulative effort, shown privately to the learner and in aggregate to instructors |
| Hint usage | `lab_completions.hints_used` | Learning support needs |
| Workbook downloads | explicit activity event from workbook links | Engagement |
| Retry attempts | `lab_completions.attempts`, `flag_attempts` | Friction |
| Time between steps | session start → first flag attempt → completion | Knowledge gaps |

“Workbook downloads” requires an explicit event because the workbook is static. Use a small authenticated tracking endpoint when a learner opens or downloads a workbook resource; do not scrape reverse-proxy logs.

### Category 1: engagement metrics

These are the core engagement measures used by the Professional and Enterprise
reports. They are **not** Community / Academic features.

| Metric | Why it matters | Definition | State |
|---|---|---|---|
| Lab start rate | Interest | Learner-lab pairs with at least one session / assigned learner-lab pairs | Data available; report pending |
| Completion rate | Success | Completed learner-lab pairs / assigned pairs, with started-to-complete as a second view | Implemented |
| Abandonment rate | Difficulty | Started learner-lab pairs without a completion / started pairs | Implemented |
| Average time | Effort | Median active minutes per completed exercise; mean is secondary and outlier-flagged | Implemented as median |
| Re-attempt count | Friction | Flag attempts per started learner-lab pair; median and share needing 3+ | Implemented from attempts data |
| Workbook views | Preparation | Authenticated workbook-open events per learner or exercise | Implemented event capture |
| Hint usage | Knowledge gaps | Hints per completion, hint-free rate, and exercise hint pressure | Implemented |
| Return visits | Engagement | Learners active on 2+ distinct days in the window / active learners | Planned |

Every metric is reported with its sample size. A missing denominator is shown as
“insufficient evidence”, not zero.

## Small-cohort suppression

Course and exercise analytics use an administrator-configurable minimum cohort
size, `analytics_min_cohort_size` (default **5**). The setting is available in
**Admin → Settings → Security**.

The API and UI distinguish three states:

- **available** — the cohort meets the minimum and metrics are shown with `n`.
- **suppressed** — the cohort is between one and the minimum; counts may remain
  visible, but percentages, medians, feedback, confidence, and skill-tree
  activity are hidden.
- **no_evidence** — the cohort has no activity yet; counts show zero and metrics
  remain null rather than being reported as measured zeroes.

Suppression applies consistently to the course overview, exercise table,
pulse-comment access, cross-course reports, CSV export, and PDF export. Reports
show separate suppressed and no-evidence course counts and exclude those rows
from aggregate totals.

The thresholds follow the education-data guidance: use a minimum of 5
observations for a headline percentage, 3 for a peer median, and 10 for a cohort
trend. Do not compare a learner-based completion rate with the started-pair
rate. Do not rank learners, instructors, or courses.

The five Professional priority engines that consume these metrics are described
in [Professional and Enterprise priorities](PROFESSIONAL-PRIORITIES.md). The
programme-level report definitions are in [Programme reports](PROGRAMME-REPORTS.md).

## Quick pulse survey

After a successful exercise completion, ask three questions only:

1. **How difficult was this exercise?**
   - Much too easy, Easy, Appropriate, Difficult, Much too difficult
2. **How much did you learn?**
   - Very little, Little, Moderate, Significant, Extensive
3. **Was anything unclear?**
   - Optional text box, capped and moderated by the course instructor.

One response per learner and exercise, with course context. The survey must be skippable and must not block the next exercise permanently.

An optional fourth prompt asks which topic the learner wants covered next. Those choices feed the **Trending topics** report.

## Quick exercise reaction

Learners also get a one-tap **Like / Dislike** control while an exercise is open.
It is separate from the pulse survey:

- It is available as soon as the exercise has been started, not only after a
  successful flag.
- It is not gated by survey consent and does not collect free text.
- One reaction is kept per learner and exercise; choosing the same reaction
  again clears it.
- Reports show aggregate likes, dislikes, and positive rate. They do not show
  learner names.

The reaction is intended as a fast teaching signal, not a rating of a learner or
a substitute for the pulse survey's learning and difficulty questions.

## Learning hours and engagement badges

Learning hours are calculated from the same records analytics already uses:

- a valid completion's `time_spent_minutes` when present;
- otherwise, merged session windows for that learner and exercise, bounded by
  `stopped_at`, `expires_at`, and the current time, with an eight-hour cap per
  exercise.

A learner/exercise pair is counted once, so a completed exercise is not also
counted from its session. The total is shown to the learner and as a course or
cross-course aggregate. It is not a public ranking.

Global achievements recognise 1, 5, 15, and 30 tracked learning hours. Sign-in
streak achievements recognise 3, 7, and 30 consecutive UTC calendar days with a
successful login. Both are idempotent and awarded outside a course scope.

## Survey management

The instructor survey page provides:

- A **Quick Pulse history** summary across the instructor's courses.
- A custom survey builder with scale, multiple-choice, and text questions.
- Course attachment at creation time.
- Response counts and per-question aggregates.
- Recent submission history and free-text responses.
- A delete action for surveys the instructor owns.
- An explicit note that participation is opt-in.

Students see available course surveys on their dashboard only after opting in under **Privacy and data**, and the API rejects submissions from learners who have not opted in.

## Reporting page

A dedicated **Reports & analytics** page gives instructors and administrators a
cross-course view. It opens at `/reports` from the sidebar: admins find it in the
**Admin** section, instructors find it in the **Instructor** section. It is a
separate route rather than an Admin Panel tab, so reviewing reports does not
change the Admin tab you were using.

- Course-level RAG status and reason.
- Completion, abandonment, learning reported, confidence gain, and pulse counts.
- Learning hours and aggregate exercise likes/dislikes.
- Trending topics across courses.
- Direct links to each course analytics tab.
- CSV and PDF export for course review, including learning hours and feedback totals.

The page is a reporting surface, not a ranking: it summarises teaching signals and links back to the evidence.

## RAG status

Use Red/Amber/Green to summarise teaching signals, not to label learners.

- **Red:** abandonment ≥ 50%, completion < 50%, median attempts ≥ 5, or learning reported ≤ 2.
- **Amber:** learners are succeeding but strained — for example high completion with low learning or high reported difficulty.
- **Green:** strong completion and high learning reported.

Every status needs a reason list so an educator can see why it was assigned.

## Learning impact indicators

Show three separate outcomes:

- **Learning Reported:** average pulse learning score (1–5).
- **Completion Rate:** completed / assigned or started, clearly labelled.
- **Confidence Gain:** a transparent performance-growth proxy derived from hint, first-attempt, and time trends.

Do not multiply these into one authoritative score. Present them side by side and explain that Confidence Gain is not a validated psychological measure.

## AI practice prompts

Generate ready-to-copy prompts for a learner’s own AI assistant when the analytics detect friction:

- High hint usage → Socratic hint-coaching prompt.
- High reattempt rate → debugging-coach prompt.
- Long time vs estimate → three-phase scoping prompt.
- Started but incomplete → restart-with-a-plan prompt.
- Strong performance → teach-back prompt.

Prompts must never include flags, account details, or another learner’s data. They must explicitly ask the AI not to reveal the final answer.

## Student view

Add a **Learning analytics** section to the student dashboard:

- Current completion and weekly progress.
- Median time compared with the exercise estimate, not with other students.
- Hint usage and first-attempt trend.
- Reattempt recovery.
- Growth cards with plain-language explanations.
- Suggested next action, such as revisiting a hint, trying a related exercise, or taking a break.
- A private “what this does not mean” note explaining that indicators are not grades.

Students should be able to see the underlying exercises behind every number.

## Educator view

Add an **Analytics** tab to each course:

### Overview

- Assigned vs started vs completed.
- Median time and time-over-estimate distribution.
- Hint usage and first-attempt rate.
- Achievement distribution.
- Weekly activity trend.

### Exercise drill-down

- Completion funnel per exercise.
- Median attempts, median time, hint pressure.
- Learning hours and like/dislike totals per exercise.
- Common stuck point: high starts, low completions.
- Difficulty vs estimated duration.
- Reattempt recovery.

### Cohort view

- Distribution bands, not individual ranking.
- Learners needing support, shown to the instructor only.
- Small-group suppression where a band could identify one learner.
- Export as CSV/PDF for course review.

### Teaching improvement prompts

- “This exercise has high hint pressure; consider adding a worked example.”
- “This exercise has a long median time but high completion; consider splitting it.”
- “This cohort recovers well after failed attempts; keep the current difficulty.”

## Research view

A separate, role-gated **Research** workspace:

- Cohort builder by course, term, track, and exercise set.
- Consent-filtered datasets only.
- De-identified learner IDs generated per study.
- Minimum cell size (recommended k ≥ 5, configurable).
- Aggregate tables, distributions, and confidence intervals.
- Export manifest with generated date, filters, consent version, and data dictionary.
- Audit event for every export.
- No names, emails, usernames, IP addresses, or free-text fields unless separately approved.

Research should support questions such as:

- Does hint usage decline as learners gain experience?
- Which exercise designs produce the most reattempt recovery?
- How does time-on-task relate to completion across course formats?
- Do quiz outcomes align with hands-on completion?

## Proposed architecture

### API

- `GET /api/analytics/student/me`
- `GET /api/analytics/courses/{course_id}/overview`
- `GET /api/analytics/courses/{course_id}/exercises`
- `GET /api/analytics/courses/{course_id}/cohort`
- `GET /api/analytics/research/cohorts`
- `POST /api/analytics/research/export`
- `GET /api/analytics/metrics` (metric dictionary)

All endpoints require authentication. Course endpoints require instructor/admin access. Research endpoints require a research role and consent-aware filtering.

### Storage

Start with SQL aggregates over existing tables. Add nightly materialized snapshots only when dashboards become slow:

- `analytics_daily_course`
- `analytics_daily_exercise`
- `analytics_learner_growth`

Each snapshot needs a schema version and metric-definition version so historical dashboards do not silently change meaning.

### Frontend

- Student: cards and sparklines, no comparative ranking.
- Educator: tabs for Overview, Exercises, Cohort, and Export.
- Researcher: cohort builder, suppression notices, export manifest.

## Privacy and governance

- Add explicit `research_opt_in` consent, separate from survey consent.
- Record consent version and timestamp.
- Respect account erasure and the suppression ledger.
- Keep instructor access scoped to their own courses.
- Apply minimum cohort size to every aggregate.
- Log analytics exports as audited events.
- Document retention for analytics snapshots and exports.
- Review with the institutional REB/privacy office before enabling research exports.
- Publish a plain-language student notice explaining what is measured and what is not.

## Phased delivery

### Phase 1: Metric foundation

- Metric dictionary and shared SQL helpers.
- Student self-view.
- Course overview and exercise drill-down.
- Tests for metric formulas and permissions.

### Phase 2: Growth and teaching insight

- Within-person growth indicators.
- Exercise stuck-point analysis.
- Cohort bands and support prompts.
- CSV/PDF educator export.

### Phase 3: Research workspace

- Research consent.
- De-identified cohort builder.
- Minimum-cell suppression.
- Export manifest and audit trail.

### Phase 4: Longitudinal analysis

- Term-over-term cohorts.
- Pre/post comparisons where a course has a quiz.
- Data quality monitoring and missing-data reports.

## Open decisions

1. Should research consent be a new explicit setting, or can survey consent cover analytics research?
2. What minimum cohort size should the institution require: 5, 10, or another threshold?
3. Should educators see individual learner growth indicators or only cohort distributions and support flags?
4. Do we need event-level hint timestamps, or is `hints_used` per completion sufficient for V2?
5. Which export formats are required first: CSV, PDF, or both?
6. Which research questions must the first release support?
