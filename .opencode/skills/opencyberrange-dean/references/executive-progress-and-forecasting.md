# Executive progress and trend forecasting

The Academy executive view answers one question for the dean or programme lead:

> **Are we on track for the semester goals, and if not, what has to change now?**

It is a **programme** view. It is not a learner tracker, an instructor league
table, or a promise about the future.

## What the executive view shows

Use this order on the page. The first screen must answer "are we on track?"
without a scroll.

1. **Semester header** — semester name, week number, days remaining, overall
   status (`on track`, `watch`, `off track`, `insufficient data`), and the date of
   the last snapshot.
2. **Goal cards** — 2–4 semester goals. Each card shows:
   - baseline, actual, target, and variance;
   - a sparkline of the last 6–8 weekly points;
   - the projected end-of-term value;
   - the gap to target and the required weekly pace;
   - the forecast method and sample size;
   - the owner and the next review date.
3. **Trajectory chart** — one line per selected goal metric over the semester,
   with the target line and a projection segment. Use a dashed projection line
   and a shaded uncertainty band.
4. **Leading indicators** — response rate, coaching coverage, knowledge-check
   participation, content readiness, and active courses. These move before
   completion and satisfaction do.
5. **Course portfolio** — one row per course: health status, completion,
   response rate, coaching coverage, trend direction, and the next action. Sort
   by risk, not by name.
6. **Risks and decisions** — the top three items with owner, decision, and due
   date. This is the part the dean acts on.
7. **Evidence** — export the current view with the method, n, and limitations.

## Metric definitions

Use one definition everywhere. Do not let a chart and a card disagree.

| Metric | Definition | Direction | Source |
|---|---|---|---|
| Completion rate | Learners with at least one completed certificate-required lab / enrolled learners | Higher | Course analytics |
| Started rate | Learners with a lab session / enrolled learners | Higher | Course analytics |
| Abandonment rate | Started but not completed / started | Lower | Course analytics |
| Student satisfaction | Mean of post-quiz satisfaction, relevance, usefulness, and ease-of-use ratings | Higher | Quiz feedback |
| Response rate | Unique feedback respondents / enrolled learners | Higher | Course feedback summary |
| Clarity | Mean course check-in clarity (1–5) | Higher | Survey responses |
| Challenge fit | 100 − abs(mean difficulty − 3) × 25, floored at 0 | Higher | Exercise pulse |
| Coaching coverage | Students with at least one instructor coaching note / enrolled | Higher | Course feedback summary |
| Knowledge-check participation | Learners with at least one completed attempt / enrolled | Higher | Quiz attempts |
| Cyber DNA trait movement | Change in a trait score between two snapshots using the same formula version | Context | Skill DNA |

**Do not** use a single "programme score" that hides the distribution. Report the
portfolio as counts of healthy / watch / attention, then the metric.

## Forecast methods

Use transparent methods that a programme lead can explain. Do not use a
black-box model.

### 1. Goal pace

The required weekly change to hit the target:

```text
required_weekly = (target - actual) / weeks_remaining
```

Compare it with the current weekly rate. If the required pace is more than 1.5×
the current pace, the goal is **off track**, not "stretch".

### 2. Run rate

For cumulative metrics such as completion:

```text
projected = actual / weeks_elapsed * total_weeks
```

This is simple and explainable. It is only valid when the weekly rate is stable;
show the weekly points so the reader can see the assumption.

### 3. Three-week moving average

For noisy weekly rates such as response rate or coaching coverage:

```text
projected = mean(last 3 weekly values)
```

Do not use a single week. Do not use a moving average when there are fewer than
three points.

### 4. Linear trend (direction only)

Fit a least-squares line to the weekly points. Show the slope direction and R².
If R² is below 0.5, label the trend **unstable** and do not present a precise
end-of-term number. Use the trend to say "improving / flat / falling", not to
promise a value.

### 5. Scenario band

Show three values instead of one:

- **conservative** — lower of the run rate and the 3-week average, or the lower
  quartile of weekly changes;
- **expected** — the chosen method's projection;
- **stretch** — the target pace.

The band is the honest answer. A single projected number is not.

## Data sufficiency

| Condition | Label | What to show |
|---|---|---|
| 0–2 weekly points | **Insufficient history** | Actual and target only; no projection |
| 3–5 weekly points | **Early projection** | Projection with a wide band and a caution |
| 6+ weekly points | **Projection** | Projection, band, and method |
| < 5 survey responses | **Early signal** | No trend; show n and "not enough responses" |
| < 10 active learners in a cohort | **Small cohort** | Suppress percentages that could identify a person; show counts |

Never forecast an individual learner. If an instructor needs to support a
student, that is a private course-level conversation, not a dean forecast.

## Data contract

The executive view needs a stable weekly series. Do not recompute history from
mutable rows without a snapshot.

### Tables

```text
programme_goals
  id, semester_id, name, metric_key, baseline, target, direction,
  owner_id, review_date, created_at, updated_at

programme_health_snapshots
  id, captured_at, semester_id, course_id (nullable), metric_key,
  value, sample_size, source, formula_version

semesters
  id, name, starts_on, ends_on, status
```

`course_id` is null for programme-level metrics. `metric_key` is the shared
definition above. `formula_version` protects comparisons when a definition or
Cyber DNA formula changes.

### Endpoint

```text
GET /api/programme/overview?semester_id=...
```

Return:

```json
{
  "semester": {"name": "...", "week": 6, "weeks_total": 14, "days_remaining": 56},
  "status": "watch",
  "goals": [
    {
      "metric": "completion_rate",
      "baseline": 54.0,
      "actual": 62.0,
      "target": 75.0,
      "variance": -13.0,
      "projected": 68.0,
      "band": [64.0, 71.0],
      "required_weekly": 1.625,
      "current_weekly": 1.0,
      "method": "run_rate",
      "points": 6,
      "sample_size": 84,
      "confidence": "early",
      "owner": "..."
    }
  ],
  "leading_indicators": {},
  "courses": [],
  "risks": [],
  "generated_at": "..."
}
```

The API must enforce authorization and return aggregates only. It must include
`sample_size`, `method`, and `formula_version` in every forecast object.

## Snapshot cadence

- Capture weekly, on the same weekday, at the same time.
- Capture after the week closes, not mid-week, so the point is comparable.
- Store the metric definition version and the source table.
- Backfill only from immutable events; never overwrite a historical snapshot.
- If a course is added mid-semester, start its series at its first full week and
  label it "partial term".

## Executive review language

Use these frames:

- "At the current pace, the programme is projected to reach 68% completion
  (band 64–71%), 7 points below the 75% target. The required pace is 1.6 points
  per week; the current pace is 1.0."
- "Response rate is an early signal (n=12, 3 weeks). Do not treat the change as a
  trend yet."
- "Two courses are driving the gap. The next decision is X, owned by Y, due Z."

Avoid:

- "The programme will hit 68%."
- "Students in course A are weaker."
- "The forecast predicts 12 students will fail."
- "Instructor X is below average."
- A single RAG colour with no reason.

## Anti-patterns

- A single hero number with no distribution.
- A straight-line forecast from two points.
- A forecast with no sample size or method.
- Comparing courses with different cohort sizes or delivery modes without a note.
- Ranking instructors by satisfaction or completion.
- Using Cyber DNA as a progress target without the same formula version.
- Hiding a small cohort behind a percentage.
- A dashboard with no owner, action, or review date.

## Acceptance criteria

- The first screen answers "on track / watch / off track / insufficient data".
- Every goal card shows baseline, actual, target, variance, projection, method,
  n, and review date.
- Every projection has a band or an explicit "insufficient history" state.
- The trajectory chart has a table alternative and a text summary.
- The course portfolio sorts by risk and shows the next action.
- The export includes the method, n, limitations, and generation time.
- No individual learner is identifiable; small cohorts are suppressed or
  labelled.
- The view is keyboard operable, screen-reader labelled, and usable at 390 px.
- The API and UI have tests for the forecast math, empty states, and permissions.

## Implementation phases

1. **Data contract** — add `semesters`, `programme_goals`, and
   `programme_health_snapshots`; add the weekly snapshot job; document the
   definitions.
2. **Executive API** — aggregate the snapshots, compute goal pace, run rate,
   moving average, trend, and band; add permission tests.
3. **Academy executive view** — goal cards, trajectory chart, leading indicators,
   portfolio table, risk list, export.
4. **Instructor teaching view** — course health, coaching queue, next action.
5. **Student path view** — my progress, next exercise, Cyber DNA growth, feedback.
6. **Evidence** — end-of-term brief and export verification.

Do not build the chart before the snapshot contract exists. A beautiful chart
over inconsistent history is worse than no chart.
