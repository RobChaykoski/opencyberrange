# Reporting Templates and Language

Use this reference with the `OpenCyberRange Learning Impact` skill.

A report is not a data dump. It is a decision aid. Lead with the decision, then
the evidence, then the limits.

## 1. The five-part report

Every learning-impact report follows the same shape:

1. **Decision** — what this report will help someone decide.
2. **Headline** — one sentence with the main result and its uncertainty.
3. **Evidence** — the metrics, distributions, and comparison.
4. **Limits** — what the data cannot show.
5. **Next action** — one change, one owner, one review date.

If a section is missing, the report is not finished.

## 2. Language rules

| Instead of | Write |
|---|---|
| "weak learner" | "not yet consistent on this task" |
| "slow" | "longer decision latency on this task; accuracy was high" |
| "poor memory" | "lower delayed recall at 14 days" |
| "low IQ" or "low ability" | never use |
| "failed" | "did not meet the criterion on this attempt" |
| "cheating with hints" | "used hints; the hint policy allowed it" |
| "average learner" | "the median learner in this cohort" |
| "the training works" | "the cohort improved on this task; the design cannot rule out novelty" |
| "obviously" / "simply" | remove |
| "normal" | "typical" or state the comparison |

Additional rules:

- Use "learner", "participant", or the role name, not "user" or "candidate".
- State the task and the time limit before the number.
- Put the limitation next to the claim, not in a footnote nobody reads.
- Do not use red/green alone to signal performance.
- Do not include flags, credentials, personal data, or screenshots of a real
  learner's screen.
- Do not compare a named learner to named peers.

## 3. Learner report template

Use `templates/learner-report.md`.

Required content:

- What you practised and why it matters.
- Two strengths, with evidence.
- One next step, with a specific practice task and cadence.
- Your retention checkpoint date.
- How to ask for help or request a correction.
- What data was collected and how long it is kept.

Do not include:

- a diagnosis or label;
- a public rank;
- a comparison to named peers;
- a single "cyber score";
- a prediction about employment or aptitude.

Example headline:

> "You solved the DNS troubleshooting task without hints and your 14-day
> check-in was similar to your first attempt. The next step is to practise the
> same procedure on a different name-resolution failure."

## 4. Instructor cohort report template

Use `templates/cohort-report.md`.

Required content:

- Cohort, n, and missing data.
- Distribution for each primary metric (median and IQR, or proportion).
- Item or task difficulty.
- The most common misconception, with an example.
- Hint dependency and where it clustered.
- Access notes (extra time, alternative input, low-bandwidth).
- One teaching change and the evidence for it.

Do not include:

- an individual league table;
- a ranking of learners by speed;
- a claim that a small difference is meaningful.

Example table:

| Task | n | Criterion met | Median time to first correct decision | Hints per learner |
|---|---:|---:|---:|---:|
| DNS record lookup | 22 | 68% | 51 s (IQR 33–84) | 1.2 |
| Stale-name diagnosis | 21 | 43% | 96 s (IQR 61–150) | 2.4 |

Interpretation: the second task needs more scaffolding or a clearer worked
example; the data do not show that the learners lack ability.

## 5. Organisation capability brief template

Use `templates/organization-brief.md`.

Required content:

- The capability question the organisation asked.
- The cohort and the roles represented.
- Time-to-competence (median sessions or active hours to criterion).
- Retention risk at the agreed delay.
- Recommended practice cadence.
- Support needs and coordination requirements.
- What the programme did **not** measure.
- A limitation and a review date.

Do not include:

- individual learner data;
- a claim that the organisation is "secure";
- a compliance certification claim;
- a prediction of incident reduction without evidence.

Example headline:

> "Staff reached the incident-triage criterion after a median of three
> sessions. At 30 days, 61% still met the criterion without the workbook.
> A monthly 45-minute revisit is the minimum cadence supported by this cohort."

## 6. Chart guidance

- Show distributions, not only bars of averages. A dot plot or box plot is
  better than a single bar.
- Always label `n`.
- Use the same scale when comparing tasks.
- Do not use 3D, gradients, or decorative icons for data.
- Do not use colour alone; add labels or patterns.
- Put the unit and the time limit in the axis label.
- Show the baseline or comparison, not just the post score.
- For small cohorts, show every point rather than a summary shape that implies
  precision.

## 7. Report red flags

A report is probably overclaiming if it contains:

- a single composite score with no components;
- "learning styles" or "digital natives";
- a claim that a short workshop "builds a security culture";
- a ranking of individuals by speed or hints;
- a percentage with no `n`;
- "retention" with no delay;
- "working memory" with no instrument or proxy definition;
- "engagement" measured only by clicks or time on page;
- a causal claim from a one-group pre/post design;
- a recommendation that is not linked to a metric.

## 8. Review checklist

- [ ] The decision is stated in one sentence.
- [ ] The headline includes the uncertainty or the limitation.
- [ ] Every number has a task, an `n`, and a unit.
- [ ] Speed is paired with accuracy.
- [ ] Load is paired with support.
- [ ] Retention has a delay.
- [ ] Reprioritisation has an injected change.
- [ ] The learner version contains no diagnosis, label, or rank.
- [ ] The organisation version contains no individual data.
- [ ] The next action has an owner and a review date.
- [ ] Flags, credentials, and personal data are absent.
