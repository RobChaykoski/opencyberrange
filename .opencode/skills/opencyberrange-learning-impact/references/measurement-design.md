# Measurement Design

Use this reference with the `OpenCyberRange Learning Impact` skill.

The goal is not to produce a number. It is to answer a decision question with
evidence that is strong enough for that decision and honest about its limits.

## 1. Start with the decision

Write one sentence before choosing a metric:

> "We will use this report to decide whether to ___."

Examples:

- add a spaced revisit before the certification assessment;
- reduce the number of simultaneous alerts in Level 2;
- add a 10-minute check-in for learners who show high load and repeated errors;
- tell a partner organisation how much practice time to schedule per month.

If the sentence cannot be written, stop. The data will become a dashboard that
nobody acts on.

## 2. Choose a design

| Design | What it supports | Minimum requirement | Main limit |
|---|---|---|---|
| **Pre / post** | Change after a programme | Equivalent forms and a baseline | No control group; maturation and novelty |
| **Pre / post / delayed** | Retention | 7-, 30-, or 90-day checkpoint | Attrition at follow-up |
| **Within-subject crossover** | Comparing two lab designs | Counterbalanced order and equivalent tasks | Order and fatigue effects |
| **Switching replication** | Causal-ish evidence for a design change | Multiple alternations between conditions | Complexity and carry-over |
| **Quasi-experiment** | Comparing cohorts or delivery modes | Comparable groups and a pre-measure | Selection bias |
| **A/B in the platform** | Optimising a specific interaction | Random assignment and a stable outcome | Ethics of withholding support |

For most OpenCyberRange programmes, the practical sequence is:

1. pre / immediate post;
2. add a 7- or 30-day delayed checkpoint;
3. add one design comparison (for example, spaced versus massed practice) when
   the programme has enough learners.

## 3. Build equivalent forms

Equivalent forms measure the same construct with different surface details.

Check:

- [ ] same skill and difficulty;
- [ ] different hostnames, artefacts, wording, and flag;
- [ ] no copy-paste walkthrough;
- [ ] same scoring rubric;
- [ ] same time limit and aid policy;
- [ ] pilot both forms with a small group.

If the delayed form is easier, the retention index will look better than it is.
If it is harder, the programme will look worse. Publish the equivalence check.

## 4. Timing

| Checkpoint | When | What it answers |
|---|---|---|
| **Pre** | Before the learning event | Baseline and prior knowledge |
| **Immediate post** | Within 15 minutes of the event | Initial acquisition and confusion |
| **Delayed** | 7, 30, or 90 days | Retention and decay |
| **Transfer** | After the delayed checkpoint, or as a separate task | Application in a new context |

Rules:

- State the delay in every report. "Retention" without a delay is meaningless.
- Avoid same-day retests as retention evidence.
- Use a fixed window (for example, 7 ± 1 days) and report deviations.
- Do not compare a 7-day retention rate with a 90-day rate.
- If the learner reviews the workbook between checkpoints, record it.

## 5. Sample size and reporting uncertainty

- Do not compare groups with fewer than **10 learners per group**. Report
  descriptive statistics instead.
- For a cohort report, always include `n` and the number of missing responses.
- Use **median and interquartile range** for latency, load, and time-to-criterion.
  These distributions are usually skewed.
- Use **mean and standard deviation** only when the distribution is reasonably
  symmetric and the audience understands it.
- Report a confidence interval when making a comparison. A simple bootstrap
  interval is enough; do not imply more precision than the sample supports.
- Do not run multiple comparisons and report only the significant one. State the
  metric set in advance.

A useful default:

```text
n = 24
median time to first correct decision = 42 s (IQR 28–71)
accuracy = 71% (17/24 correct on the first attempt)
retention at 14 days = 58% (14/24), 4 learners did not return
```

This is more honest than "average performance: 62%."

## 6. Control the obvious confounds

| Confound | Mitigation |
|---|---|
| Prior knowledge | Pre-checkpoint and stratify or adjust |
| Practice effect | Equivalent forms and counterbalancing |
| Fatigue | Short sessions, time-of-day recording, rest breaks |
| Interface novelty | Practice task before measurement |
| Language | Plain language and translated instructions where needed |
| Device and bandwidth | Low-bandwidth path; record the mode |
| Accommodation | Extra time and alternative input; never score the accommodation as ability |
| Instructor differences | Record the instructor or delivery mode |
| Lab bugs | Exclude broken sessions and report the exclusion rule |
| Attrition | Report who did not return and why, if known |
| Reactivity | Tell learners what is measured and why |

## 7. Accessibility is part of validity

A measurement that penalises a disabled learner is measuring the environment,
not the capability.

- Offer extra time by default for timed tasks, or make the time limit a separate
  reported condition.
- Allow keyboard-only, screen-reader, captions, and alternative response modes.
- Provide a no-device or low-bandwidth route.
- Do not require a personal device, webcam, or microphone.
- Record the accommodation and analyse it as a covariate, not as a failure.
- Test the instrument with assistive technology before the cohort runs.

## 8. Data collection checklist

- [ ] Pseudonymous learner ID, not a name or email.
- [ ] Server-side timestamps with a timezone.
- [ ] Explicit event types; no inferred "probably clicked."
- [ ] Explicit correctness from the rubric, not from a heuristic.
- [ ] Task identifiers that map to the workbook and lab.
- [ ] Hint and aid events with the policy recorded.
- [ ] Interruption and reprioritisation events defined in the scenario.
- [ ] A retention period and a deletion route.
- [ ] A named data owner.
- [ ] A learner-facing explanation of what is collected.

## 9. Analysis plan

Write this before looking at the data:

1. **Primary question** and **primary metric**.
2. **Secondary metrics** and how they will be interpreted.
3. **Exclusions** (for example, sessions shorter than two minutes or broken
   labs).
4. **Comparison** (baseline, prior cohort, or condition).
5. **Uncertainty** method (IQR, confidence interval, or bootstrap).
6. **Decision rule** (what result would change the programme).
7. **Limitations** to state regardless of the result.

## 10. Common design mistakes

- Measuring completion and calling it learning.
- Using the same lab as the post-test and the delayed test.
- Adding a timer and calling the result "quick thinking."
- Measuring "working memory" without a validated instrument or a clear proxy.
- Running a reprioritisation exercise that never changes the priorities.
- Comparing two small cohorts and declaring a winner.
- Reporting a single composite score that hides the trade-offs.
- Collecting more data than the decision needs.
- Reporting a learner's worst session as their ability.
- Forgetting that a lab bug is not a learner error.

## 11. Pilot checklist

Before a full cohort:

- [ ] Run the task with 3–5 people from the target audience.
- [ ] Time the task and check the time limit.
- [ ] Confirm the pre and post forms are equivalent.
- [ ] Confirm the delayed task is not a reskin.
- [ ] Confirm the reprioritisation change is noticed.
- [ ] Confirm the instruments work with a screen reader and keyboard.
- [ ] Confirm the data export contains the fields the report needs.
- [ ] Ask participants what the questions meant to them.
- [ ] Revise the wording before scaling.
