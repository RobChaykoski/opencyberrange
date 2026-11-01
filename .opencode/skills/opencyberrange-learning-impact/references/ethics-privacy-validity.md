# Ethics, Privacy, and Validity

Use this reference with the `OpenCyberRange Learning Impact` skill.

Learning metrics are only useful if people trust them. Trust comes from purpose
limitation, honest claims, accessible design, and a clear route to challenge the
data.

## 1. Purpose limitation

Collect data only for a stated decision.

Before adding an event, answer:

- What decision will this support?
- Who will see it?
- How long will it be kept?
- What happens if it is wrong?
- Can the learner opt out without losing access to the learning?

If the answer is "it might be useful later," do not collect it.

## 2. Consent and transparency

- Tell learners what is measured, why, and who sees it.
- Use plain language, not a wall of legal text.
- Make participation in measurement separate from participation in the course
  where possible.
- Offer an opt-out that does not remove access to the labs.
- Explain that the measures are proxies, not assessments of their intelligence
  or mental health.
- Give a route to correct or delete data.

## 3. No diagnosis

These metrics are not clinical instruments.

Do not use them to infer or label:

- attention-deficit or learning disorders;
- intelligence, aptitude, or "potential";
- personality, motivation, or resilience;
- mental-health status;
- employability.

Do not let a language model generate a psychological profile from event logs.
An LLM can summarise counts; it cannot diagnose a person.

## 4. Privacy and security

- Use pseudonymous IDs by default.
- Do not store names, emails, or student numbers in the analytics table.
- Do not collect keystrokes, screen recordings, webcam, or microphone data by
  default.
- Do not include flags, credentials, or answers in a report that leaves the
  platform.
- Encrypt data at rest and in transit.
- Restrict access to the smallest group that needs it.
- Set a retention period and delete on schedule.
- Do not send learner-level data to a third-party analytics service without a
  reviewed agreement and consent.

## 5. Equity and access

A metric can be biased by the environment rather than the learner.

- Provide extra time and alternative input for timed tasks.
- Test with a screen reader and keyboard only.
- Provide captions and transcripts for audio or video.
- Offer a no-device or low-bandwidth path.
- Avoid cultural references that require local knowledge.
- Report results by accommodation status rather than treating accommodation as
  a failure.
- Check whether a task assumes a particular device, home environment, or
  uninterrupted time.
- Do not compare cohorts with different access conditions without saying so.

## 6. Psychological safety

- Errors are data, not moral failures.
- Never publish a public ranking of speed, hints, or errors.
- Do not use the metrics in discipline, promotion, or hiring decisions.
- Give feedback privately and specifically.
- Normalise help-seeking; hint use is a behaviour to coach, not a stain.
- Give learners a way to say "this task was unfair" and have it reviewed.
- Avoid surprise timers. State the time limit before the task.

## 7. Validity threats

| Threat | What it looks like | Mitigation |
|---|---|---|
| **Construct validity** | Time-on-task is called "working memory" | Define the proxy and its limits |
| **Teaching to the test** | Learners memorise the exact lab | Equivalent forms and transfer tasks |
| **Reactivity** | Learners behave differently because they are measured | Transparent purpose and low-stakes framing |
| **Novelty effect** | A new interface produces a temporary gain | Delayed checkpoint and a practice task |
| **Attrition** | The learners who return are the confident ones | Report return rate and compare starters with completers |
| **Selection** | Cohorts differ before the programme | Pre-checkpoint and stratification |
| **Small n** | A two-person difference is called a trend | Report descriptives, not significance |
| **Multiple comparisons** | Many metrics, one significant result | Pre-specify the primary metric |
| **Instrument drift** | The rubric changes between waves | Version the rubric and the task |
| **Lab bugs** | Broken sessions are scored as errors | Exclude with a stated rule |

## 8. Causal claims

A one-group pre/post design cannot rule out:

- normal development or prior experience;
- concurrent training or workplace practice;
- the novelty of the lab;
- the instructor's attention;
- changes in the assessment.

Use "improved on this task" rather than "the training caused." If a causal claim
is needed, use a comparison group, randomisation, or a switching replication, and
state the assumptions.

## 9. Data governance checklist

- [ ] A named data owner.
- [ ] A written purpose for each event.
- [ ] A retention period.
- [ ] A deletion procedure.
- [ ] An access list.
- [ ] A pseudonymisation method.
- [ ] A breach response route.
- [ ] A learner-facing explanation.
- [ ] A correction route.
- [ ] A review of third-party processors.

## 10. Report ethics checklist

- [ ] No diagnosis or label.
- [ ] No individual public ranking.
- [ ] No claim of causation from a weak design.
- [ ] No flag, credential, or personal data.
- [ ] `n`, spread, and missing data are visible.
- [ ] The limitation is next to the claim.
- [ ] The learner can correct the record.
- [ ] The report states who owns the next action.
