# Data quality and statistics

Run these checks before interpreting a student's profile. A finding about the
data is as important as a finding about the student.

## Data-quality checks

| Check | Definition | Why it matters |
|---|---|---|
| Session coverage | Completions with a matching non-diagnostic session / completions | `started_rate` is unreliable when this is low |
| Completion uniqueness | Duplicate `(user_id, lab_id)` completions | Multiple rows inflate counts |
| Time completeness | Completions with `time_spent_minutes` / completions | Time metrics ignore nulls |
| Duration calibration | Median `time_spent_minutes` / `duration_minutes` per exercise | Estimates may be coarse |
| Pulse response rate | Pulse responses / completions | Self-report is optional |
| Quiz participation | Learners with a completed attempt / enrolled | Understanding evidence is optional |
| Check-in response rate | Unique check-in respondents / enrolled | Feeling data is opt-in |
| Coaching coverage | Students with a coaching note / enrolled | The loop may not be closing |
| Diagnostic sessions | `is_diagnostic = true` / sessions | Exclude from learning metrics |
| Opt-in rate | `survey_opt_in = true` / enrolled | Low opt-in limits feeling data |
| Formula version | Cyber DNA `formula_version` | Never compare across versions |

### Current known gaps

- **Session starts are incomplete.** On the development course, completion was
  77.1% while `started_rate` was 2.1%. Use completion, hints, attempts, and time
  until fixed.
- **Prerequisites are absent.** None of the 149 labs define them. Use track/level
  order and course assignment order as a proxy.
- **Duration is coarse.** Median estimate is 120 minutes. Prefer peer median time
  for the same exercise.
- **Pulse and quiz are optional.** Respondents may differ from non-respondents.
- **`started_rate` is pair-based.** It is started learner–exercise pairs divided by
  total possible pairs, not started learners divided by enrolled.

## Descriptive statistics

Use:

- **Median and interquartile range** for time, hints, and attempts.
- **Counts and proportions** for completion, participation, and coaching.
- **Within-person change** for growth: last three exercises vs previous three.
- **Peer median** for context: same exercise, same course, same difficulty.
- **Distributions** for cohorts: median, IQR, and n; not a single average.

Avoid:

- Means for skewed time data.
- A single composite score without explicit weights.
- Ranking by any metric.
- Comparing courses with different cohorts or delivery modes without a note.

## Small samples

For a proportion `p` with `n` observations, use the Wilson 95% interval:

```text
z = 1.96
denom = 1 + z^2 / n
centre = (p + z^2 / (2n)) / denom
margin = z * sqrt((p * (1 - p) + z^2 / (4n)) / n) / denom
interval = [max(0, centre - margin), min(1, centre + margin)]
```

Report the interval when `n` is small or the proportion is near 0 or 1. Do not run
a significance test on a handful of students.

| Evidence | Minimum | Label |
|---|---|---|
| Headline percentage | 5 observations | Otherwise show count and n |
| Peer median | 3 completions | Otherwise use the course median or no comparison |
| Trend | 3 weekly points | Otherwise "early signal" |
| Cohort trend | 10 learners and 6 weekly points | Otherwise "insufficient history" |
| Feeling | 5 responses | Otherwise counts and "early signal" |

## Bias and confounders

- **Selection bias.** Pulse, quiz, and survey participation are optional.
  Respondents may be more engaged or more available.
- **Missing data.** Completions without sessions, null time, and skipped pulse
  questions are not missing at random.
- **Regression to the mean.** Students selected because they scored lowest will
  tend to improve without an intervention. Use a comparison if possible.
- **Multiple comparisons.** Reviewing many exercises will produce apparent
  patterns by chance. Prefer consistent, multi-signal findings.
- **Hawthorne effect.** Learners may change behaviour because they are being
  observed.
- **Instrument change.** Duration estimates, definitions, and Cyber DNA formulas
  can change. Do not compare across versions.
- **Course design.** A difficult exercise, a missing prerequisite, or an access
  barrier can look like a student problem.
- **Instructor change.** A new instructor or a changed schedule can move the
  metrics.

## Within-person analysis

Compare the same student over time:

1. Last three completed exercises vs the previous three.
2. Hint-free rate, first-attempt rate, time ratio, learning reported.
3. Same difficulty band where possible.
4. Note the exercise mix; a harder set can explain a lower score.

A single improved exercise is an early signal, not a trend. A single bad exercise
is not evidence of decline.

## Causal language

- Pre/post without a comparison: "consistent with", not "caused by".
- With a comparison group: name the group and the confounders.
- With a small n: "early signal", not "effect".
- With missing data: "the data cannot tell us".

## Output checks

Before sharing:

- Does every percentage have `n`?
- Is the denominator stated?
- Is the time window stated?
- Is the individual's own baseline shown before the peer comparison?
- Are small samples labelled?
- Is the next step specific and feasible?
- Is the limitation one sentence a reader can repeat?
- Is any individual identifiable in an aggregate?
- Is the output free of flags, credentials, and personal data?
