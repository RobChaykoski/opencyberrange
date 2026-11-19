# Cyber Workforce Risk Score (CWRS)

Status: **pilot implementation** (19 November 2026). The instructor support queue uses a provisional CWRS. Offline calibration and the full rubric remain. This is the canonical formula for the
[student risk engine](STUDENT-RISK-ENGINE.md). It replaces the earlier ad-hoc
weights and bands.

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

CWRS is an instructor support index. It is not a grade, a prediction of dropout,
or an automated decision. It answers:

> Which learner needs a human check-in first, and which evidence should the
> instructor review?

Higher is worse.

## 1. Bands

| CWRS | Band | Meaning | Default response |
|---:|---|---|---|
| 0–29 | **Healthy** | No strong support signal | No action |
| 30–49 | **Monitor** | Early signal | Check at the next class |
| 50–69 | **Elevated** | Clear signal or several weak signals | Contact this week |
| 70–84 | **High risk** | Multiple strong signals or one severe signal | Contact within two working days |
| 85–100 | **Critical intervention** | Severe, sustained, or compounding risk | Contact within one working day |

The label is a support prompt. Do not use "dropout", "failing", or "at risk of
leaving" in the UI.

## 2. Core formula

Each component is normalised to **0–100**, where 0 is no concern and 100 is the
highest concern.

```text
CWRS base =
  Performance risk      × 0.35
+ Engagement risk       × 0.20
+ Progression risk      × 0.15
+ Competency risk       × 0.15
+ Behavioural risk      × 0.10
+ Infrastructure risk   × 0.05

CWRS = clamp(CWRS base - portfolio bonus - acceleration bonus, 0, 100)
```

Round to a whole number. Store the unrounded base, bonuses, and formula version.

## 3. Performance risk — 35%

Measures actual ability. Higher concern means lower performance.

| Metric | Weight | Risk conversion |
|---|---:|---|
| Lab success rate | 30% | `100 - success_rate` |
| Assessment scores | 30% | `100 - assessment_average` |
| Evidence quality | 25% | `100 - reviewed_artifact_quality` |
| Retake count | 15% | `100 - retake_score` |

`retake_score` is 100 for no retakes, 75 for one, 50 for two, 25 for three, and 0
for four or more on the same unit.

Example scores: lab 65, assessment 70, evidence 80, retake 90.

```text
risk = 35×0.30 + 30×0.30 + 20×0.25 + 10×0.15
     = 10.5 + 9.0 + 5.0 + 1.5
     = 26
```

The conversion is deliberately inverted: a score of 65 becomes a risk of 35.

Use a 28-day window. Compare with the learner's own previous four weeks as well
as the course median. A single hard lab is not a pattern.

## 4. Engagement risk — 20%

Most support needs appear here first.

| Indicator | Weight | Risk conversion |
|---|---:|---|
| Days since last sign-in | 35% | 0–3 days = 0; 4–7 = 25; 8–14 = 60; 15+ = 100 |
| Weekly activity | 25% | `100 - (active_days / expected_days × 100)` |
| Time in labs | 25% | `100 - (learner_median / cohort_median × 100)`, capped 0–100 |
| Discussion participation | 15% | `100 - participation_rate`, optional |

`discussion participation` is optional. Do not penalise a learner who does not
use discussion, is neurodivergent, is learning in a second language, or has
caregiving or work constraints. If the course does not require discussion, set
the weight to 0 and redistribute it to weekly activity.

**Context flags.** A planned absence, illness, bereavement, placement,
accommodation, or institution closure pauses engagement and progression risk for
the stated period. The flag is visible in the explanation.

## 5. Progression risk — 15%

Measures cohort alignment, not speed.

```text
gap  = max(0, expected_labs_completed - actual_labs_completed)
risk = min(100, gap / expected_labs_completed × 100)
```

Example: expected 42, actual 28.

```text
gap  = 14
risk = 14 / 42 × 100 = 33
```

Use the course schedule and the cohort median, not the fastest learner. A learner
who is ahead has risk 0. A learner who is behind because of a documented context
flag is not penalised.

## 6. Competency risk — 15%

Map evidence to the learner's target role and compare with the role thresholds.

Example target: SOC Analyst.

| Skill | Threshold | Learner | Shortfall |
|---|---:|---:|---:|
| KQL | 80 | 58 | 22 |
| Hunting | 75 | 81 | 0 |
| IR | 75 | 68 | 7 |
| Reporting | 70 | 85 | 0 |

Use a normalised shortfall, not a raw average:

```text
shortfall_i = max(0, threshold_i - score_i) / threshold_i
competency_risk = 100 × weighted_average(shortfall_i)
```

For the example with equal weights:

```text
shortfall = [22/80, 0, 7/75, 0] = [0.275, 0, 0.0933, 0]
average   = 0.0921
risk      = 9.2
```

Do not assert a different value without showing the formula. If the institution
wants a harsher penalty for a critical skill, add a **criticality multiplier** to
that requirement and record it in the role profile. Do not hide the multiplier.

If a required skill has no evidence, mark it **unmeasured**. Do not treat it as a
zero score. Use coverage and confidence to qualify the result.

## 7. Behavioural risk — 10%

This is **learning behaviour**, not personality, attitude, or conduct.

| Signal | Points |
|---|---:|
| Multiple missed deadlines | +20 |
| Assignment abandonment | +20 |
| Consistent incomplete submissions | +15 |
| Team participation failure with a recorded role | +15 |

Cap at 100.

Rules:

- Count a pattern, not one bad week.
- Do not infer motivation, mental health, disability, family situation, or
  "attitude".
- Do not use protected attributes or proxies.
- A team participation failure needs a recorded role and a specific missed
  commitment, not a quiet learner.
- Record the learner's context before scoring.

### Integrity is not a support-risk input

Repeated plagiarism or academic misconduct belongs in the institution's
integrity process, not in CWRS. Adding +50 to a support score conflates conduct
with need and can bias the result.

If an integrity concern exists, open a separate integrity case, follow the
policy, and keep it out of the support dashboard. The instructor may still see
that a case exists if authorised, but it must not change the CWRS.

## 8. Infrastructure risk — 5%

This component exists only for **learner-specific** technical friction.

| Situation | Value |
|---|---:|
| Learner-specific broken environment | 100 |
| Learner-specific degraded environment | 50 |
| No learner-specific issue | 0 |

Do not count a platform-wide outage, a missing image that affects everyone, a
scheduled maintenance window, or a known lab defect. In those cases set the
component to 0 and raise a **lab health** flag.

A learner must not be penalised for the platform. The 5% weight does not make a
platform outage safe to include.

## 9. Portfolio bonus

The portfolio bonus rewards reviewed practical evidence, not volume.

```text
portfolio_bonus = min(15, reviewed_artifact_quality / 100 × 15)
```

Requirements:

- at least three reviewed artifacts across at least two artifact types;
- no unreviewed artifact counts;
- the quality score is the median of instructor-reviewed artifacts;
- cap at 15 points;
- if the base CWRS is 85 or above, cap the portfolio bonus at 8 points.

Example: 12 incident reports, 15 threat hunts, and 9 detections do not earn a
bonus by themselves. A reviewed quality score of 92 earns 13.8 points.

The bonus is a risk reduction, not a grade. It must never hide a critical
performance or safety flag.

## 10. Acceleration bonus

Acceleration tracks positive momentum.

Inputs:

- consecutive successful completions;
- faster completion against the learner's own baseline;
- competency growth over the recent window.

Range: **-100 to +100**.

```text
acceleration_bonus = clamp(acceleration_score, 0, 100) × 0.10
```

Cap at 10 points. A negative acceleration does not add a second penalty; the
performance and progression components already capture decline.

Example: KQL improves from 45 to 75 and IR from 60 to 88. A growth score of +42
contributes 4.2 points of risk reduction.

Do not reward speed at the expense of quality. A fast, wrong solve is not
acceleration.

## 11. Final formula

```text
CWRS =
  clamp(
    Performance×0.35
    + Engagement×0.20
    + Progression×0.15
    + Competency×0.15
    + Behaviour×0.10
    + Infrastructure×0.05
    - Portfolio bonus
    - Acceleration bonus,
    0,
    100
  )
```

Total bonus is capped at 20 points. A Critical Intervention score cannot be
reduced below 85 by bonuses while a critical safety or integrity flag is open.

## 12. Three parallel scores

Do not collapse everything into one number. Maintain three scores with the same
0–100 bands:

| Score | Purpose | Inputs |
|---|---|---|
| **Academic risk** | Will the learner complete the course? | Performance, engagement, progression, course deadlines |
| **Technical risk** | Is the learner mastering the skills? | Performance, competency, portfolio, acceleration |
| **Employment risk** | Is the learner ready for the target role? | Job-profile match, competency, portfolio, communication, team scenario |

Example:

```text
Academic risk:    18   Healthy
Technical risk:   62   Elevated
Employment risk:  71   High risk
```

This tells the instructor: the learner will probably pass the course, but is not
yet ready for a SOC Analyst role.

Each score has its own explanation. Do not average them into a single "student
score". The three views answer different questions.

Suggested component weights:

| Score | Weights |
|---|---|
| Academic risk | Performance 40%, engagement 30%, progression 30% |
| Technical risk | Performance 45%, competency 35%, portfolio/acceleration 20% |
| Employment risk | Job-profile match 50%, competency 25%, portfolio 15%, communication/team 10% |

These weights are configurable and versioned. Do not change them without a
calibration record.

## 13. Intervention engine

The score should trigger a workflow, not a verdict.

| CWRS | Action | Owner | SLA |
|---:|---|---|---|
| 50+ | Instructor alert with evidence and suggested actions | Instructor | This week |
| 70+ | Student success alert; draft outreach for instructor approval | Instructor + success team | Two working days |
| 85+ | Critical intervention workflow; case owner; coordinator notified | Instructor + programme coordinator + success team | One working day |

Rules:

- Alerts are deduplicated per learner and cooldown for seven days.
- A context flag suppresses the alert for its window.
- A platform incident suppresses infrastructure-driven alerts.
- Student-facing messages are drafted, not sent automatically, unless the
  learner has opted into automated nudges.
- Every recommended action is a suggestion from a reviewed library, not an
  automatic assignment.
- The case records the action, owner, outcome, and follow-up date.
- A dismissed alert is feedback, not a failure.

Recommended action library:

- guided retry of the prerequisite lab;
- KQL/detection fundamentals practice set;
- extension or reduced-scope plan;
- lab reset or environment check;
- study plan with weekly check-in;
- referral to the institution's support service, where appropriate and lawful.

Do not recommend a mental-health, financial, or medical intervention from a risk
score. Use the institution's safeguarding path.

## 14. Confidence and minimum evidence

- No score until at least three assessment points or two active weeks.
- **High** confidence: four active weeks, at least three strong components, no
  overlapping platform incident.
- **Medium**: two strong components, or one missing week.
- **Low**: fewer than three assessment points, a small cohort, or a recent
  platform incident.
- Small cohorts (fewer than five learners) use absolute thresholds and mark the
  score provisional.
- Under-18 learners follow the existing analytics exclusion; an authorised
  instructor may still see an individual support record.

## 15. Explainability

The learner and instructor view must show:

- the three scores and bands;
- each component, value, weight, and contribution;
- bonuses and the evidence behind them;
- flags and context;
- what is missing or provisional;
- the last action and outcome;
- the formula version and window.

Example (core CWRS blend):

```text
CWRS 67 — Elevated (High confidence)
  Performance      78  × 35% = 27.3
  Engagement       90  × 20% = 18.0
  Progression      85  × 15% = 12.8
  Competency       70  × 15% = 10.5
  Behavioural      60  × 10% =  6.0
  Infrastructure    0  ×  5% =  0.0
  Base                          74.6
  Portfolio bonus               -6.0
  Acceleration bonus            -1.6
  Final                         67.0
```

When the three-score model is active, show that score's own weights and label the
view **Academic**, **Technical**, or **Employment**. Do not mix the core blend
with a three-score blend in one calculation.

## 16. Data model

| Table | Purpose |
|---|---|
| `cwrs_snapshots` | Learner, course, score type, formula version, window, score, band, confidence, components, bonuses |
| `cwrs_flags` | Snapshot, flag type, severity, evidence reference, state |
| `cwrs_context_flags` | Learner, course, type, start, end, note, author |
| `cwrs_overrides` | Snapshot, instructor, old band, new band, reason, created_at |
| `cwrs_actions` | Flag, instructor, action, note, outcome, created_at |
| `lab_health_incidents` | Platform incident window, lab, scope, excluded from infrastructure risk |

## 17. Governance and fairness

- CWRS is a support tool. It must not be used for grading, admissions,
  employment, or disciplinary action.
- Do not use protected attributes or proxies.
- Review false positives and false negatives each term.
- Check for disparate impact across cohorts; stop and fix the model if a group
  is over-flagged without a learning-related cause.
- Publish the rubric and the context-flag policy to learners.
- Give the learner a way to correct wrong data.
- Retain scores under the course retention policy; aggregate or delete after.
- Never share CWRS with an employer.
- A human makes every decision.

## 18. Implementation phases

1. **Phase 1 — offline calibration.** Generate the three scores for past courses
   and compare with instructor-confirmed cases. Do not show them to learners.
2. **Phase 2 — read-only dashboard.** Show scores, components, flags, and
   evidence to authorised instructors.
3. **Phase 3 — context and overrides.** Add context flags, overrides, actions,
   and outcomes.
4. **Phase 4 — intervention workflow.** Add alerts, cooldowns, recommendations,
   and case ownership.
5. **Phase 5 — learner view and calibration.** Show learners their own support
   record and correction path; tune only with a documented change record.

## 19. Acceptance criteria

- The three scores use the documented weights and are shown separately.
- Every score has a component breakdown, confidence, and window.
- No score is shown without the minimum evidence.
- Platform incidents do not raise a learner's score.
- Bonuses require reviewed evidence and are capped.
- An instructor can record context and override with a reason.
- The learner can see and correct their own data.
- The score is versioned and never shared with an employer.
- A human makes the support decision.

## 20. Anti-patterns

- A single number with no explanation.
- Punishing a learner for a platform outage.
- Treating "no evidence" as "low performance".
- Putting plagiarism in a support-risk score.
- Inferring attitude, motivation, or mental health.
- Rewarding artifact quantity instead of reviewed quality.
- A permanent "critical" label without review.
- An automatic message to the learner.
- Hiding the score from the learner while showing it to everyone else.
