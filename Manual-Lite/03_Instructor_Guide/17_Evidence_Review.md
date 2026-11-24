# Evidence Review

Evidence review is the instructor surface for written and automatically
collected evidence. It turns a completion into a reviewed capability record.

## Who can use it

Instructors and administrators can open **Evidence review** from the left
navigation. Instructors see evidence for learners in the courses they own or
staff. Administrators see the institution. A learner sees only their own evidence
elsewhere in the product.

## Operations summary

Above the queue, the page shows the current workload: awaiting review, accepted,
rejected, learners with evidence, and the age of the oldest waiting record. It
also shows the source and rubric mix, the strongest and weakest competencies,
workbook/documentation coverage, the 30-day confidence trend, and the accepted
rate.

For an instructor, aggregate breakdowns are hidden when the visible scope has
fewer than five learners. The totals and the queue remain usable; the dashboard
does not become a window into an individual learner.

## The queue

The left column lists evidence with status **collected** or **in review**. Each
row shows:

- the learner;
- the source type and source id;
- the rubric id and version;
- when it was collected.

Select a row to open the evidence record.

## Reading a record

The record shows:

- learner identity and source;
- rubric version, confidence, provenance, visibility, and formula version;
- any artifact hash;
- the learner's submitted answer, when the evidence came from a workbook;
- competency links, criteria, and weights;
- the rubric criteria, level descriptors, and weights;
- previous decisions.

The rubric is loaded from the version the evidence was collected with. A newer
rubric does not rewrite an old decision.

## Recording a decision

1. Score each rubric criterion from 0 to 3.
2. Choose **accept**, **request more evidence**, or **reject**.
3. Add notes. A rejection requires a next step for the learner.
4. Choose **Record decision**.

An accepted decision requires every criterion to be scored. The weighted score
is stored on the review row. The decision is appended; the evidence content is
not edited.

## Automatic evidence

Correct flags and passed exercise knowledge checks are accepted automatically by
the platform. They use the `automatic-check` rubric and a system review, so they
do not wait in the instructor queue. Workbook answers use the `analyst-answer`
rubric and do wait for a human review.

## Appeals

A learner can appeal a **rejected** evidence record once. The appeal appears in
the **Appeals awaiting review** list beside the queue. Open it to read the
learner's reason and the original decision.

Choose **accept** to return the evidence to `in review` for a second decision, or
**reject** to uphold the original decision. Both choices require notes. An
accepted appeal does not change the rubric score by itself; it reopens the record
so a reviewer can score it again.

## What a decision means

- **Accept** means the evidence meets the recorded rubric at the scored level.
- **Request more evidence** means the record is not sufficient yet; the learner
  gets a next step.
- **Reject** means the evidence does not meet the rubric; the learner gets a
  reason and a next step.

A decision is not a grade, a rank, or a prediction of employment. It is a
reviewed practice record that can contribute to competency coverage.

## Troubleshooting

| Problem | What to check |
|---|---|
| The queue is empty | No evidence with status `collected` or `in review` is in your scope. |
| A record cannot be reviewed | It may already have a final decision. Open the review history. |
| The rubric is missing | The recorded rubric version is not in the registry. Do not score it; report the version to an administrator. |
| The learner answer is not visible | The evidence may be an automatic flag or quiz record, not a workbook answer. |

## Related pages

- [Workbook answers](../02_Student_Guide/24_Workbook_Answers.md) for the learner
  workflow.
- [Evidence Engine](https://github.com/RobChaykoski/opencyberrange/blob/main/docs/EVIDENCE-ENGINE.md)
  for the data model and review rules.
- [External Skills Frameworks](../02_Student_Guide/25_External_Skills_Frameworks.md)
  for the NICE, CS2023, CAE-CD, and SFIA 9 vocabulary.
