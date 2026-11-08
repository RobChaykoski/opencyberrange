# Feeling vs doing

A quick face is a useful **conversation prompt**, not a measurement of the
student. It answers "how does the course feel right now?" beside "how is the work
going?" The pair is more useful than either signal alone.

## The rule

- **Doing** comes from progress: completed / assigned, pace, independence, and
  persistence.
- **Feeling** comes only from **explicit self-report**: the course check-in
  (clarity, engagement, confidence) or a comparable question. Never infer it from
  completion, hints, attempts, time, or clicks.
- Show a **text label** with the face. The face is a secondary cue, never the only
  carrier of meaning.
- Keep the pair private to the student and their instructor. The dean sees
  aggregate counts, not individual faces.
- Never use feeling as a grade, a discipline signal, or a prediction.

## The two axes

### Feeling (self-reported)

Use the mean of the check-in ratings that describe the experience, not the
difficulty rating:

```text
feeling = mean(clarity, engagement, confidence)   # 1–5, only fields present
```

| Mean | Indicator | Label | Tone |
|---|---|---|---|
| 4.0–5.0 | 🙂 | Positive | positive |
| 3.0–3.9 | 😐 | Mixed | watch |
| 1.0–2.9 | 🙁 | Low | attention |
| no rating | ○ | No check-in | muted |

If the student completed the survey but did not share per-student ratings, say
**Check-in, no rating** rather than guessing. The anonymous survey path may not
expose per-student answers; respect that.

### Doing (progress)

```text
doing = completed_assigned / assigned
```

| Progress | Label | Tone |
|---|---|---|
| 70–100% | On track | positive |
| 30–69% | Building | watch |
| 0–29% | Needs a step | attention |
| no assignments | No assignments | muted |

## The four useful combinations

| | Feeling positive | Feeling low |
|---|---|---|
| **Doing on track** | **Thriving.** Keep the challenge; ask them to explain a concept or help a peer. | **Hidden struggle.** They are finishing but not enjoying it. Check in privately; ask what feels unclear or heavy. |
| **Doing behind** | **Effort without traction.** Motivation is there, but the next step is too large. Reduce scope, confirm prerequisites, pick one small exercise. | **Needs support.** Check for access, schedule, confidence, and a blocker. Choose one small next step and a review date. |

If feeling is unknown, the next step is a question, not a label: "How is the
course feeling?" If doing is unknown, confirm the assignment list first.

## Where to use it

- **Instructor coaching queue:** face + text label + progress; sort by the
  combination, not by a composite score.
- **Student success profile:** show feeling beside progress, pace, independence,
  persistence, understanding, capability, and support. It is context, not a
  separate grade.
- **Course check-in:** keep the questions short and optional; explain who sees
  what.
- **Dean executive view:** show aggregate counts only — for example, "12 positive,
  5 mixed, 3 low, 4 no check-in" — with n and a note that it is self-report.
  Do not show individual faces to the dean.

## UI rules

- Always pair the face with a word: `🙂 Positive`, `😐 Mixed`, `🙁 Low`,
  `○ No check-in`.
- Add an accessible label that includes the student, the feeling, the doing
  state, and the suggested conversation.
- Do not use colour alone. Do not use emoji alone. Do not animate the face.
- Make the "no check-in" state neutral, not a failure.
- Keep the legend visible: "Feeling is self-reported; doing is progress. Neither
  is a grade."
- Do not show the face on public pages, certificates, or leaderboards.

## Data quality and ethics

- Check-in participation is opt-in. A low response rate is a finding about the
  loop, not evidence that students are unhappy.
- Small samples: fewer than five responses is an early signal; show counts and n.
- Self-report is affected by workload, mood, accessibility, and the wording of the
  question. It is not a clinical measure.
- Do not deanonymise survey responses to fill a missing face. Use "No check-in".
- Do not compare one student's feeling with another's in a public or ranked view.
- Give the student a route to correct their data and to opt out.

## Language

Use:

- "Reports low confidence this week."
- "Feeling is mixed while progress is on track."
- "No check-in yet; ask how it is going."
- "The evidence suggests a private check-in would help."

Avoid:

- "Unhappy student."
- "At risk."
- "Not engaged" (unless there is explicit evidence and a defined meaning).
- "Should be doing better."
- A face with no label, or a label with no next step.

## Definition of done

- The face is derived only from explicit self-report.
- The text label is present and accessible.
- The doing state is shown beside it.
- The pair leads to one conversation or next step.
- The legend explains that neither is a grade.
- The dean view uses aggregates only.
- Small samples and missing check-ins are labelled.
