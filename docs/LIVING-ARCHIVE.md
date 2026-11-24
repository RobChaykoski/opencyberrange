# The Living Archive

Status: **v1 observation engine; reflections and long-horizon history planned**.

The archive does not ask a learner to declare who they are. It observes what
verified contribution becomes and describes the pattern later.

This is the core correction to every talent platform: a self-assessment measures
aspiration. Observation measures behaviour.

## The rule

- A learner chooses a **mission**, not an archetype.
- The archive reads **verified contribution** only.
- Until there is enough evidence, the archive says **undetermined**.
- The result is a **private observation**, not a public label, score, or rank.
- No percentage is shown. The archive tells a story with counts.

## Signals

Each contribution has one primary tradition. A contribution is never double
counted, so the observation is explainable.

| Tradition | Example signals |
|---|---|
| Protection | incident exercises, risk reduction, detection rules, remediation, MFA rollout |
| Creation | labs, tools, workbooks, integrations, platforms |
| Discovery | research, publications, reverse engineering, OSINT |
| Stewardship | documentation, playbooks, monitoring, maintenance, returning to old work |
| Illumination | workshops, mentoring, teach-backs, course material, presentations |
| Connection | community events, judging, introductions, study groups |
| Service | non-profit support, small-business support, service hours, student support |
| Judgment | policy, threat models, architecture reviews, responsible disclosure |

Signals that the platform does not yet collect honestly — optional-resource
views, peer thanks, introductions — are **manual** recognition in v1. They are
not inferred from clicks.

## Thresholds

The archive needs more than one good day.

| Status | Rule |
|---|---|
| Undetermined | fewer than 3 verified contributions, or fewer than 2 distinct kinds |
| Emerging | at least 3 verified contributions across 2 kinds, with a clear leader |
| Recognized | at least 6 verified contributions across 3 kinds, over at least 180 days |

A tie between two traditions stays **undetermined**. The archive does not guess.

Thresholds are deliberately small for a young programme. They should rise as
the community matures; the values are configuration, not a universal truth.

## What the learner sees

```text
The Living Archive

You may be walking the Path of Stewardship.

• You returned to maintain work after the first version.
• Your verified work in this path reached 240 people.
• This is an observation from verified contribution, not a label.

7 verified contributions across 4 kinds. An observation, not a score.
```

When recognized:

```text
The Keepers have taken notice.

Many communities begin; few endure.
```

No percentages. No "Stewardship 73%". No comparison with another learner.

## Optional reflections

A reflection is **evidence, not a required form**. After a workshop or a
project, a learner may answer an optional question:

- Why did you volunteer your time?
- What part of this work mattered most to you?
- What decision would you change if you had another chance?

A reflection is stored with the contribution and read by a human reviewer. It
is **not** keyword-scored, and it never changes a tradition by itself. A
reflection can support a manual recognition award, where an administrator records
a reason and an evidence reference.

## Emergent identity

| Stage | What the learner sees |
|---|---|
| Year 1 | Path unclear. The archive is observing. |
| Year 2 | Strong signs of Discovery. |
| Year 3 | The Cartographers have taken notice. |
| Year 4 | Recognized tradition: Cartographer. |
| Year 5 | Historian's note: your contributions became reference material for others. |

The years are illustrative. The thresholds are contribution and time, not a
calendar promise.

## Anti-gaming

1. **Verified contribution only.** Self-reported activity is pending.
2. **One primary tradition per contribution.** No double counting.
3. **Breadth requirement.** Three contributions of one kind do not make a path.
4. **Tie means undetermined.** The archive does not manufacture a result.
5. **No reflection mining.** Free text is for human reading, not keyword scores.
6. **No public label.** A learner can see their own observation; nobody else
   sees it without consent.
7. **No reward loop.** The archive changes no score, permission, or grade.

## API

`GET /api/archive/me` returns:

```json
{
  "status": "emerging",
  "tradition": {
    "id": "stewardship",
    "title": "Stewardship",
    "archetype": "The Keepers",
    "future_view": "..."
  },
  "alternative": null,
  "notes": ["..."],
  "observed": {"contributions": 7, "kinds": 4, "days": 120},
  "disclaimer": "Traditions are inferred; they are not selected or scored."
}
```

The endpoint is self-only and cache-disabled. It never returns another learner's
observation.

## Privacy

- The observation is a private self-view.
- It is excluded from public profiles, transcripts, and verification pages.
- Under-18 learners are excluded from any shared archive surface.
- An instructor sees contribution evidence for learners they own or staff; the
  inferred tradition is not shown as a label in a roster.
- The archive never becomes a grade, a prerequisite, or a disciplinary signal.

## Delivery

| Phase | Deliverable |
|---|---|
| 6.1 | Observation from verified contributions, thresholds, narrative notes, private self-view |
| 6.2 | Optional reflections attached to a contribution, with human review only |
| 6.3 | Long-horizon timeline and "historian's note" from maintained artifacts |
| 6.4 | Learner-consented archive page for a portfolio or transcript |

## Acceptance criteria

- A learner cannot select a tradition or archetype anywhere in the UI.
- With no verified contribution, the archive says undetermined.
- Three contributions of one kind do not produce an emerging tradition.
- A tie stays undetermined.
- The payload contains no percentage and no ranking.
- The learner sees counts and narrative notes, not a score.
- The observation never changes the Legacy Score or a permission.
