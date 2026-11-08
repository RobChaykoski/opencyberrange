# Programme reports

Status: **Professional 2.5.0 and Enterprise preview**
Audience: programme leads, instructors, accreditation reviewers, approved
researchers

These are the five programme-level questions the product must answer without
manual spreadsheet work. Each report is defined here so the UI, exports, API,
and tests share one meaning. The capabilities that deliver them are described in
[Professional and Enterprise priorities](PROFESSIONAL-PRIORITIES.md).

| # | Question | Primary capability | Current state |
|---|---|---|---|
| 1 | Which labs are failing? | Exercise Health Analytics | Course exercise drill-down available; programme report planned |
| 2 | Which tracks are strongest? | Radar / Spider Web Reporting | Course and all-course skill-tree coverage radar delivered; programme ranking and learner/cohort radar planned |
| 3 | Which competencies are weakest? | Competency Framework Engine | Six-domain performance available; explicit competencies planned |
| 4 | How long does competency development take? | Competency Framework Engine | Median time per exercise available; time-to-competency planned |
| 5 | Which students become top performers? | Instructor Intervention Dashboard | Growth indicators available; private sustained-performance view planned |

## How to run what exists today

| Report | Where |
|---|---|
| Course learning summary and RAG | Sidebar → Reports & analytics → course row |
| Course exercise health | Course → Analytics → Exercises |
| Course trend and feedback | Course → Analytics → Overview |
| Learner growth and domain profile | Learner analytics / Profile |
| Cross-course CSV/PDF | Reports & analytics → Export CSV / Export PDF |
| Survey and pulse results | Instructor survey page |

The programme reports below add the missing cross-course, cross-cohort, and
competency views. Until they ship, use the existing course drill-down plus the
CSV export.

## Report 1: Which labs are failing?

**Definition:** A lab is failing when learners start it but do not complete it,
or complete it with unusually high friction, and the pattern is sustained across
a cohort or time window.

**Fields:**

- Lab, track, level, course, cohort.
- Learners assigned, learners started, learners completed.
- `lab_start_rate` = started learner-lab pairs / assigned learner-lab pairs.
- Completion rate = completed / started.
- Abandonment rate = started pairs without a completion / started pairs.
- Re-attempt count = flag attempts per started learner-lab pair, with median and
  share needing 3 or more.
- Hints per completion and hint-free rate.
- Median time to completion and time to first attempt.
- Feedback: difficulty, learning value, clarity, positive rate.
- Sample size, evidence level, and trend.

**Filters:** course, cohort, track, lab, date range, assigned-only.

**Default sort:** highest abandonment rate with at least the minimum sample
size, then highest hint pressure.

**Actions:** open the lab, review the workbook, inspect learner evidence, add to
the authoring queue.

**Guardrail:** a failing lab is a review prompt, not a judgement about the
instructor or the learner.

## Report 2: Which tracks are strongest?

**Definition:** Track strength is the track's ability to produce completed,
low-friction, durable learning across its labs.

**Fields:**

- Track, number of labs, assigned learners, started learners, completions.
- Completion rate, abandonment rate, median time, first-attempt rate,
  hint-free rate.
- Competency coverage: how much of the track maps to each competency.
- Feedback score and trend.
- Evidence level.

**Filters:** course, cohort, programme, date range.

**Default sort:** completion rate, then first-attempt rate, with sample-size
suppression.

**Guardrail:** a strong track is not a ranking of instructors or learners. Show
the evidence and the sample size.

## Report 3: Which competencies are weakest?

**Definition:** A competency is weak when learners have enough evidence but low
completion, low first-attempt success, high hint dependency, or weak radar
evidence compared with the cohort's own baseline.

**Fields:**

- Competency, domain, mapped tracks and labs.
- Learners with evidence, completions, completion rate.
- First-attempt rate, hint-free rate, median time.
- Radar score and evidence level (`no evidence`, `early`, `growing`, `strong`).
- Feedback signal.
- Change from the previous period.

**Filters:** course, cohort, programme, competency, date range.

**Default sort:** weakest evidence-adjusted score first, suppressing
insufficient samples.

**Guardrail:** do not turn a missing evidence axis into a zero. Show “no
evidence yet”.

## Report 4: How long does competency development take?

**Definition:** Time from a learner's first evidence in a competency to the
point where the competency reaches the defined development threshold.

**Threshold (configurable in the Competency Framework):**

- at least N completed exercises mapped to the competency (default 3);
- across at least two labs or levels;
- with the required evidence mix (for example, one first-attempt completion or
  one hint-free completion);
- maintained within the programme's evidence window.

**Fields:**

- Competency and cohort.
- Learners reaching the threshold.
- Median and interquartile range of elapsed days from first evidence to
  threshold.
- Median active learning hours, separate from calendar days.
- Proportion reaching the threshold within the course or programme window.
- Censored learners (not yet reached) shown separately, never silently dropped.
- Evidence level.

**Filters:** course, cohort, programme, competency, start date, threshold
profile.

**Guardrail:** calendar time and active learning time are different measures.
Report both. Do not compare cohorts with different threshold profiles without a
label.

## Report 5: Which students become top performers?

**Definition:** A private, evidence-based view of learners with sustained high
performance, used to offer stretch work and peer-support opportunities.

**Eligibility:**

- at least the minimum number of completed exercises in the window (default 5);
- completion rate at or above the programme threshold;
- first-attempt rate and hint-free rate above the cohort median;
- positive growth trend across at least two windows;
- no unresolved integrity or academic-conduct flag.

**Fields:**

- Learner (instructor-only), cohort, evidence count.
- Completion rate, first-attempt rate, hint-free rate, median time.
- Growth indicators and radar profile.
- Feedback and intervention history.
- Confidence label.

**Filters:** course, cohort, programme, date range, minimum evidence.

**Guardrails:**

- This is **not** a public leaderboard, grade, prediction, or permanent label.
- The default view is a support and stretch list, not a ranking.
- Small cohorts are suppressed or shown only to the assigned instructor.
- Learners can see their own evidence and ask for a correction.
- The instructor makes every decision; no automated notification or sanction.

## Common requirements

- **Cohort-size suppression:** do not show a group below the configured minimum.
- **Evidence labels:** every metric shows sample size and confidence.
- **Medians and distributions:** time and attempt data use median and IQR, not
  averages alone.
- **Filters persist:** course, cohort, date range, track, and competency survive
  drill-down and export.
- **Retention and consent:** follow [Analytics governance](ANALYTICS-GOVERNANCE.md)
  and the [Data dictionary](DATA-DICTIONARY.md).
- **Exports:** CSV and PDF preserve the on-screen definitions and filters.
- **Empty states:** explain whether there is no data, insufficient evidence, or
  a filter that excludes everything.
- **Accessibility:** every chart has a table alternative.
- **Audit:** report views and exports of learner-level data are logged.

## Acceptance tests

For each report:

1. A course with no data returns an explanatory empty state.
2. A cohort below the suppression threshold hides learner-level rows.
3. A lab with starts and no completions appears as failing with a sample size.
4. A completed lab with high hints appears in hint pressure, not only in
   abandonment.
5. A competency with no mapped evidence shows “no evidence yet”.
6. Time-to-competency separates reached and censored learners.
7. The top-performer view is visible only to an authorised instructor.
8. CSV and PDF exports match the screen's filters and definitions.
9. The report is reproducible from the same data snapshot.
10. No report exposes a learner's identity in an aggregate view.
