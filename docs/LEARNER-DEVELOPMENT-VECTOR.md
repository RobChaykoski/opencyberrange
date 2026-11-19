# Learner Development Vector (LDV)

Status: **proposal** (18 November 2026). Complements the snapshot views in
[CWRS](CYBER-WORKFORCE-RISK-SCORE.md), [learning signals](LEARNING-SIGNAL-INDICES.md),
and [competency matrix](COMPETENCY-MATRIX-AND-LAB-HEALTH.md).

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

A snapshot answers "where is the learner now?" The LDV answers:

> **Which direction is the learner moving, how fast, and is the movement
> stable?**

The LDV is a trajectory, not a grade. It is descriptive and coaching-oriented.
It is not a prediction of employment, completion, or dropout.

## 1. Snapshot versus vector

| View | Question | Example |
|---|---|---|
| Snapshot | Where is the learner now? | KQL 75, IR 68, cloud 71 |
| Delta | What changed since last time? | KQL +12, IR +4, cloud −2 |
| **LDV** | What is the direction, speed, and shape of change? | KQL rising fast; IR flat; cloud slipping |

A single delta can be noise. The LDV uses a window of points, a direction, a
velocity, and a stability measure.

## 2. Dimensions

Use a fixed, versioned dimension set so vectors are comparable over time.

| Group | Dimensions |
|---|---|
| **Capability** | SOC operations, detection engineering, cloud security, incident response, IAM, GRC, automation, architecture |
| **Practice** | curiosity, persistence, investigation, automation, communication, collaboration |
| **Outcome** | academic risk, technical risk, employment risk, role readiness |

Do not mix the groups into one number. The vector has named components.

Example:

```text
Learner s42 — 8-week LDV

Capability
  detection engineering   +18   rising
  incident response       +9    rising slowly
  cloud security          +1    flat
  IAM                     -4    slipping
  GRC                     +6    rising

Practice
  curiosity               +8    rising
  persistence             +11   rising
  investigation           +14   rising
  automation              +20   rising fast
  communication           +5    rising slowly
  collaboration           -6    slipping

Outcome
  technical risk          -12   improving
  employment risk         -7    improving
  academic risk           +3    stable
```

## 3. Vector definition

For each dimension `d`, keep a time series of scored observations:

```text
p_d(t) = score at time t
```

Derive:

- **Level** — the latest value.
- **Delta** — latest minus the value at the start of the window.
- **Velocity** — slope of a robust regression over the window, points per week.
- **Acceleration** — change in velocity between the two most recent halves of
  the window.
- **Stability** — volatility of the residuals around the trend; high volatility
  means the direction is uncertain.
- **Coverage** — share of the window with observations.

The LDV is the tuple of these values for every dimension, plus the window and
formula version.

Do not show a projection as a fact. If a projection is shown, label it
**illustrative only**, use a range, and explain the assumption.

## 4. Example calculation

For KQL over eight weeks:

```text
week  1   2   3   4   5   6   7   8
score 45  50  52  61  64  70  72  75
```

- Level: 75
- Delta: +30
- Velocity: about +4.2 points/week
- Acceleration: positive in the first half, flattening in the second
- Stability: moderate
- Coverage: 8/8 weeks

Narrative:

> KQL is rising quickly and has moved from awareness to independent practice.
> The pace flattened in the last two weeks; a harder detection lab would test
> whether the plateau is real.

## 5. Trajectory shapes

| Shape | Meaning | Coaching response |
|---|---|---|
| **Rising fast** | Rapid improvement | Add a stretch task; avoid overconfidence |
| **Rising steady** | Healthy progress | Maintain the plan |
| **Flat** | No change | Check for a plateau, prerequisite gap, or lack of practice |
| **Slipping** | Decline | Check context, workload, and recency; offer support |
| **Volatile** | Inconsistent evidence | Increase sample size before acting |
| **Recovering** | Decline followed by improvement | Reinforce the recovery and the habit |
| **No evidence** | Nothing to judge | Offer an opportunity, not a label |

A flat line after a high score is not failure. It may mean the learner has
reached the current ceiling.

## 6. Use in the platform

### Learner profile

Show a compact **development** card:

```text
Development (last 8 weeks)
  Rising      Detection engineering +18, automation +20
  Steady      Incident response +9, GRC +6
  Slipping    IAM -4, collaboration -6
  Flat        Cloud security +1
```

Expand for the vector, the evidence, and one suggested next step per group.

### Coaching

Use the vector to choose the next action:

- rising fast → harder variant or a new domain;
- flat with high level → stretch goal;
- flat with low level → prerequisite or guided practice;
- slipping → context check before an intervention;
- volatile → more evidence, not a stronger label.

### Risk and readiness

- Use velocity in the acceleration bonus, not as a separate risk penalty.
- A rising readiness vector can support a portfolio narrative.
- A slipping critical competency is a support prompt.
- Never use the vector to predict a grade or a job outcome.

### Cohort view

Show aggregate direction, not individual rankings:

```text
Cohort direction: detection engineering rising, IAM flat, GRC slipping
```

This helps the instructor adjust teaching, not label learners.

## 7. Visual design

- Use a sparkline or slope chart per dimension, not a radar for the vector.
- Show the window and the number of observations.
- Use a text label beside every trend: rising, steady, flat, slipping, volatile.
- Do not rely on colour alone.
- Keep the default to three or four dimensions; the rest behind "Show all".
- Provide a table fallback: dimension, start, latest, delta, velocity, stability.
- On mobile, show the latest value, delta, and one trend label.

## 8. Confidence and missing data

- Require at least four observations for a velocity.
- Require at least six for an acceleration.
- Mark a dimension **insufficient evidence** rather than drawing a line through
  two points.
- A gap in the window lowers confidence; it does not mean the learner stopped.
- A context flag (absence, illness, placement) is shown on the chart.
- Use the same window for all dimensions in one view.

## 9. Data model

| Table | Purpose |
|---|---|
| `ldv_series` | Learner, dimension, observed_at, score, source, confidence |
| `ldv_vectors` | Learner, window, formula version, payload, created_at |
| `ldv_annotations` | Learner, dimension, window, note, author, context flag |

Reuse existing competency, signal, risk, and readiness snapshots as the source.
Do not create a second scoring engine.

## 10. API shape

```json
{
  "learner": "s42",
  "window": "2026-09-23/2026-11-18",
  "formula_version": "ldv-2027.1",
  "dimensions": {
    "detection_engineering": {
      "level": 88,
      "delta": 18,
      "velocity": 2.6,
      "acceleration": -0.4,
      "stability": "moderate",
      "coverage": 1.0,
      "shape": "rising"
    },
    "iam": {
      "level": 44,
      "delta": -4,
      "velocity": -0.6,
      "acceleration": -0.2,
      "stability": "low",
      "coverage": 0.75,
      "shape": "slipping"
    }
  }
}
```

## 11. Guardrails

- The LDV is not a prediction. Do not label a learner "will fail" or "will be
  hired".
- Do not use the vector for grades, admissions, or employment.
- Do not compare learners publicly.
- Do not infer motivation, mental health, disability, or attitude.
- A slipping line may be a context issue; check before intervening.
- A rising line may be a easier assessment, not mastery; verify with a new
  context.
- Use confidence and coverage; do not draw a trend from two points.
- Keep the formula and dimension set versioned.
- Let the learner see and correct their own data.

## 12. Implementation phases

1. **Phase 1 — series.** Store the existing competency, signal, risk, and
   readiness snapshots in a time series with a shared dimension key.
2. **Phase 2 — offline vector.** Compute direction, velocity, and stability for
   past courses; review with instructors.
3. **Phase 3 — learner card.** Show three to four dimensions with a table
   fallback.
4. **Phase 4 — coaching.** Add a suggested next step per shape and a context
   annotation.
5. **Phase 5 — calibration.** Compare the vector with instructor judgement and
   adjust the window and stability thresholds.

## 13. Acceptance criteria

- The LDV uses a fixed, versioned dimension set.
- Every dimension has level, delta, velocity, stability, and coverage.
- No trend is drawn from fewer than four observations.
- The learner can see the evidence and the window.
- The vector is not used as a prediction or a grade.
- A context flag is visible on the chart.
- The chart has a text label and a table fallback.
- The default view shows no more than four dimensions.

## 14. Anti-patterns

- Calling a single delta a trajectory.
- Drawing a trend through two points.
- A radar chart that hides direction.
- A "predicted readiness" without a range and assumption.
- Comparing learners by vector length.
- Treating a plateau as failure.
- Treating a slip as a motivation problem.
- Showing twenty dimensions at once.
