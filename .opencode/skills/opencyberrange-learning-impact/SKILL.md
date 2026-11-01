---
name: OpenCyberRange Learning Impact
description: Use when designing, instrumenting, analysing, or reporting the learning impact of OpenCyberRange hands-on cybersecurity training. Covers delayed recall and transfer, working-memory load, rapid decision quality, reprioritisation, calibration, and collaboration; defines learner, instructor, and organisation reports; and provides a data contract for future timing and coordinated-support features. Treats every measure as a proxy, never a diagnosis or a public ranking.
---

# OpenCyberRange Learning Impact

Use this skill when the question is **"did the hands-on training change what
people can do, and will it last?"** — not when the question is "did they finish
the lab?"

It is the reporting companion to `opencyberrange-inclusive-curriculum` (who the
learner is and what the scenario teaches) and `opencyberrange-design` (how the
platform presents it). It does not replace either.

## What this skill is for

- Designing a measurement plan for a course, lab sequence, or organisation
  cohort.
- Choosing metrics that reflect reinforcement learning rather than attendance.
- Instrumenting the platform to capture timing, decisions, hints, and
  reprioritisation without surveillance.
- Producing learner, instructor, and organisation reports that are honest about
  uncertainty.
- Preparing the data contract for future features: paced delivery, timed
  exercises, coordinated support, and cohort dashboards.

## The measurement stance

1. **Measure capability, not completion.** A finished lab is an activity
   record. A delayed, unaided performance is evidence.
2. **Every psychological measure is a proxy.** Time-on-task is not working
   memory. Decision latency is not intelligence. Name the observable, the
   construct it stands in for, and the limits.
3. **Pair speed with accuracy.** A fast wrong decision is not fluency. Report
   decision latency only beside correctness, and never as a standalone score.
4. **Pair load with support.** High mental demand is a design signal, not a
   learner defect. Ask whether the interface, the scenario, or the time pressure
   caused it.
5. **Measure retention after a delay.** Immediate post-test scores mostly
   measure the last ten minutes. Schedule 7-, 30-, and 90-day checkpoints when
   the programme allows.
6. **Test transfer, not recall of the exact lab.** Use equivalent but different
   systems, artefacts, and wordings. If the learner only recognises the lab, the
   training has not transferred.
7. **Report distributions, never a single hero number.** Include n, spread, and
   the comparison or baseline. Do not rank individuals publicly.
8. **Do not diagnose.** These metrics are not clinical instruments and must not
   be used to label a person's memory, attention, intelligence, or mental
   health.
9. **Collect the minimum.** Pseudonymous IDs, event-level data only where it
   answers a stated question, and a retention limit. No keystroke logging by
   default.
10. **Design for access.** Extra time, alternative input, screen readers, and
    low-bandwidth paths must not be scored as lower capability.

## The metric model

Use five families. Pick the smallest set that answers the reporting question.

| Family | Question it answers | Core measures |
|---|---|---|
| **Retention and recall** | Can they still do it later, without the walkthrough? | Delayed checkpoint score, retention index, hint-free delayed success, error recurrence |
| **Working-memory load** | How much of the task is spent holding state rather than solving? | NASA-TLX mental demand, interruption recovery time, re-read/pause indicators, aid use |
| **Rapid decision quality** | Can they choose correctly under time pressure? | Median and p90 decision latency, accuracy, correct decisions per minute, timeout rate |
| **Reprioritisation** | Can they reorder work when the situation changes? | Top-3 alignment with expert ranking, time to re-plan, abandoned low-value work, recovery after interruption |
| **Transfer and calibration** | Can they apply it in a new context, and do they know when they are unsure? | Novel-context checkpoint, hint-free transfer task, confidence–accuracy gap, Brier score |

Supporting measures: completion, time-to-criterion, hint dependency, help-seeking
quality, collaboration/handoff quality, and return practice. Use them as context,
not as the headline.

### The four psychological measures in plain language

- **Long-term success and recall:** performance on a delayed, equivalent task.
  Report the delay, the task, and whether aids were allowed.
- **Short-term working memory:** the *load* the task places on the learner.
  Measure with a validated self-report (for example the mental-demand subscale
  of NASA-TLX) and behavioural interruption-recovery time. Do not call it a
  working-memory capacity score.
- **Thinking quickly:** decision latency under a stated time limit, always
  paired with accuracy and a definition of "correct."
- **Reprioritisation:** the ability to change the order of work after new
  evidence. This needs a scenario that injects a change; it cannot be inferred
  from a static lab.

## Minimum viable measurement set

If you can only instrument five things, instrument these:

1. A **pre** checkpoint and an **immediate post** checkpoint on equivalent
   tasks.
2. A **delayed** checkpoint at 7 or 30 days.
3. **Decision events** with task, correctness, and latency.
4. **Hint requests** and **flag attempts** with timestamps.
5. One **reprioritisation event** in a scenario that forces a change.

Everything else is optional until the reporting question requires it.

## Reporting tiers

| Audience | Report | Must include | Must not include |
|---|---|---|---|
| **Learner** | Progress and next practice | Strengths, one next step, practice cadence, support options | Labels, diagnoses, public rank, raw comparison to named peers |
| **Instructor** | Cohort teaching report | Distribution, item difficulty, misconceptions, hint dependency, access notes | Individual league tables |
| **Organisation** | Capability and readiness brief | Time-to-competence, retention risk, recommended cadence, support needs, limitations | Claims that the training "fixed" security, individual performance data |

Use `references/reporting-templates.md` and the files in `templates/`.

## Workflow

1. **State the decision.** What will someone do differently because of this
   report? If there is no decision, do not collect the data.
2. **Choose the family or families.** Most programmes need retention plus one of
   load, speed, or reprioritisation. Do not measure all five by default.
3. **Design the task.** Build equivalent forms and a delayed checkpoint. For
   reprioritisation, add a scripted change.
4. **Instrument the event.** Use the schema in
   `references/platform-integration.md`. Capture server-side timestamps and
   explicit correctness, not inferred clicks.
5. **Pilot with a small group.** Check that the measures behave as expected and
   that accessibility accommodations do not distort the result.
6. **Analyse with uncertainty.** Report n, median or mean as appropriate, spread,
   and the comparison. Do not compare groups smaller than the minimum stated in
   `references/measurement-design.md`.
7. **Write for the audience.** Use the matching template. Lead with the decision,
   then the evidence, then the limits.
8. **Act and re-measure.** Change one thing (pace, scaffolding, scenario
   complexity) and check whether the metric moved.

## Rules for responsible use

- Never use these metrics for hiring, promotion, discipline, or public ranking.
- Never present a single session as a stable trait.
- Never report a speed metric without accuracy and task conditions.
- Never report a load metric as a learner deficit.
- Never claim causation from a single-group pre/post design.
- Never include flags, credentials, personal data, or identifiable screenshots
  in a report.
- Always state the delay, the task equivalence, the aids allowed, and the n.
- Always give the learner a route to challenge or correct their data.

## Definition of done

A learning-impact report is done when:

- the decision it supports is stated in one sentence;
- each metric names its construct, observable, formula, and limitation;
- speed is paired with accuracy, and load with support;
- retention has a stated delay and an equivalent task;
- reprioritisation has an injected change, not a static checklist;
- the report includes n, spread, and a limitation;
- the learner version contains no diagnosis, label, or public rank;
- access accommodations are described and do not lower the score;
- the data collection has a purpose, a retention period, and an owner.

## References

- `references/metrics-catalogue.md` — definitions, proxies, formulas, and misuse.
- `references/measurement-design.md` — designs, timing, equivalence, sample size,
  and confounds.
- `references/reporting-templates.md` — learner, instructor, and organisation
  reports, plus language and chart guidance.
- `references/ethics-privacy-validity.md` — consent, equity, security, and
  validity threats.
- `references/platform-integration.md` — event schema, timing, coordinated
  support, and roadmap.
- `assets/metrics-schema.json` — machine-readable metric contract.
- `scripts/compute_session_metrics.py` — reference calculator for one session.
- `templates/` — fill-in report templates.
