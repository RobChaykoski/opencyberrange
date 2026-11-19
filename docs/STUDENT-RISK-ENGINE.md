# Student risk engine

Status: **pilot implementation** (19 November 2026). The read-only support queue and lab health are live in the instructor dashboard; calibration remains. This is an instructor support tool, not
a prediction of dropout and not an automated academic decision.

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

The dashboard answers one question:

> Which learners need a human check-in first, and why?

It does not answer "who will fail" or "who should be removed".

## 1. Design principle

A risk score is only useful if it is **explainable, actionable, and fair**. The
instructor must see the evidence and the suggested next step, not a black-box
number. The learner must be able to correct wrong data.

A false "critical" label can harm a learner. The engine therefore favours
precision over recall, suppresses weak evidence, and never acts on its own.

## 2. Inputs and weights

The canonical score is the [Cyber Workforce Risk Score](CYBER-WORKFORCE-RISK-SCORE.md):

| Input | Weight | What it measures |
|---|---:|---|
| Performance | 35% | Recent quiz and lab outcomes against the cohort and the learner's own baseline |
| Engagement | 20% | Sign-in and active-learning recency and consistency |
| Progression | 15% | Required work completed against the expected pace |
| Competency | 15% | Capability gaps against the target role |
| Behavioural | 10% | Observable learning behaviour, not personality |
| Infrastructure | 5% | Learner-specific technical friction only |

Portfolio and acceleration bonuses are applied after the weighted base and are
capped. See the CWRS page for the full formula.

### Infrastructure is not a student deficit

A lab that fails for the whole cohort is a platform problem. It must not lower a
learner's risk score. The engine therefore:

- excludes incidents that are already known platform outages;
- counts only repeated, lab-specific failures that other learners did not hit;
- shows the infrastructure contribution separately;
- suppresses the input when the sample is too small.

If the platform is the cause, the output is a **lab health flag** for the
instructor, not a learner risk flag.

## 3. Normalisation

Each input is converted to a 0–100 concern score, where a higher value means
more need for support.

- **Cohort-relative:** compare the learner with the current course cohort, not
  with an absolute standard.
- **Own-baseline:** compare the learner with their own previous four weeks so a
  strong learner who suddenly stops is visible.

- **Recency:** weight the last 14 days more than older work.
- **Minimum evidence:** no score until the learner has at least three
  assessment points, or two weeks of activity.
- **Small cohorts:** if fewer than five learners are enrolled, use absolute
  thresholds and mark the result provisional.

The engine stores the formula version and the input snapshot with every score so
an instructor can see why the number changed.

## 4. Bands and flags

| Band | CWRS | Meaning | Suggested action |
|---|---:|---|---|
| **Critical intervention** | 85–100 | Severe, sustained, or compounding risk | Contact within one working day |
| **High risk** | 70–84 | Multiple strong signals or one severe signal | Contact within two working days |
| **Elevated** | 50–69 | Clear signal or several weak signals | Contact this week |
| **Monitor** | 30–49 | Early signal | Check at the next class |
| **Healthy** | 0–29 | No strong support signal | No action |

Example flags:

| Flag | Example trigger |
|---|---|
| **Technical struggle** | Failed four KQL or detection labs in the recent window |
| **Disengaged** | No sign-in for 14 days |
| **Falling behind** | 15 required labs behind the cohort median |
| **Repeated lab friction** | Three failed starts on the same lab while peers succeed |
| **No submission** | Missed two consecutive required artifacts |
| **Team isolation** | No team-scenario activity while the team is active |

Do not use "potential dropout" as a label in the UI. Use "needs support" and
name the evidence.

## 5. Explainability

Every row expands to:

- the score and band;
- the six contributions with their values and weights;
- the portfolio and acceleration bonuses, with evidence;
- the flags that fired;
- the evidence links (lab attempts, quiz results, sign-in recency, assignment
  status);
- what is missing or provisional;
- three suggested actions, ordered by likely impact;
- the last instructor action and its outcome.

Example:

```text
Jane — High risk (76)

Performance      85 × 35% = 29.8
Engagement       90 × 20% = 18.0
Progression      85 × 15% = 12.8
Competency       80 × 15% = 12.0
Behavioural      70 × 10% =  7.0
Infrastructure    0 ×  5% =  0.0
Base                        79.6
Portfolio bonus             -2.0
Acceleration bonus          -1.6
Final                       76.0

Flags
  Failed four detection labs in 10 days
  No sign-in for 12 days
  Two required artifacts missing

Suggested actions
  1. Check in about the detection lab sequence and offer a guided retry.
  2. Confirm whether the absence is planned; record the outcome.
  3. Offer the next capstone milestone or a reduced-scope path.
```

The instructor can acknowledge, snooze, reassign, or dismiss a flag with a
reason. The outcome is recorded and used to calibrate the engine later.

## 6. Dashboard

The instructor dashboard should:

- default to the highest-risk learners, with a clear "why" column;
- allow filtering by course, cohort, flag, and band;
- show counts, not public rankings;
- show the data freshness time;
- preserve the row position when new data arrives so the list does not jump;
- show a "no action needed" state for learners with too little evidence;
- export a support list with the evidence links for a case meeting;
- support keyboard navigation and a table view for screen readers.

Do not show the risk score to other learners. Do not publish a leaderboard of
risk.

## 7. Instructor workflow

1. **Review** the flag and the evidence.
2. **Decide** whether the signal is real; dismiss false positives with a reason.
3. **Contact** the learner using the institution's channel.
4. **Plan** a support action: guided retry, extension, study plan, lab reset,
   referral.
5. **Follow up** and record whether the risk moved.
6. **Review** the flag after the intervention.

The engine measures the *process*, not the learner's worth. A dismissed flag is
a successful correction, not a failure.

## 8. Privacy and fairness

- Use the minimum data needed. Do not ingest protected attributes.
- Do not infer a disability, mental-health condition, immigration status, or
  financial situation.
- Do not expose the score to employers or other learners.
- Retain scores for the course review period, then aggregate or delete under
  the retention policy.
- Show a learner their own support flags and let them correct wrong data.
- Review false positives and false negatives each term.
- Test for disparate impact across cohorts; if a group is over-flagged without
  a learning-related cause, stop and fix the model.
- A human makes every decision. The score is a prompt, not a verdict.

## 9. Data model

| Table | Purpose |
|---|---|
| `risk_snapshots` | Learner, course, formula version, score, band, inputs, created_at |
| `risk_flags` | Snapshot, flag type, severity, evidence reference, state |
| `risk_actions` | Flag, instructor, action, note, outcome, created_at |
| `risk_feedback` | Flag, label (true/false/uncertain), reviewer, reason |
| `lab_health_incidents` | Platform incident window, lab, scope, to exclude from learner risk |

Reuse the existing course, enrollment, completion, quiz, and activity tables.
Do not duplicate them.

## 10. Evaluation

Before calling the engine useful:

- compare flags with instructor-confirmed cases;
- measure precision at the Critical and High bands;
- review a sample of false positives with instructors;
- review a sample of missed cases;
- check stability across weeks and cohorts;
- check fairness across available cohorts;
- record the calibration decision and the formula version.

A high-risk flag that instructors dismiss 80% of the time is noise. Remove or
retune it.

## 11. Implementation phases

1. **Phase 1 — offline report.** Generate the score and flags for one course as
   a CSV, with no learner-facing change, and calibrate with instructors.
2. **Phase 2 — read-only dashboard.** Show the sorted list, evidence, and
   suggested actions. No automated messages.
3. **Phase 3 — workflow.** Add acknowledge, dismiss, contact, and follow-up
   records.
4. **Phase 4 — calibration.** Compare outcomes, tune weights, and document the
   validation.
5. **Phase 5 — course-level lab health.** Separate platform friction from
   learner risk and show it on the same screen.

## 12. Acceptance criteria

- Every score has a breakdown and evidence links.
- No score is shown without the minimum evidence.
- A platform-wide lab failure does not lower learner scores.
- An instructor can dismiss a flag with a reason.
- The learner can see and correct their own data.
- The dashboard has a table view and keyboard access.
- The formula is versioned and the calibration record is stored.
- No score is shared outside the teaching team without consent.

## 13. Anti-patterns

- Calling the output "dropout probability".
- Sorting learners publicly.
- Penalising learners for platform outages.
- Using the score for admissions, grading, or employment.
- Hiding the inputs from the instructor.
- Sending an automatic "you are at risk" message.
- Never reviewing false positives.
