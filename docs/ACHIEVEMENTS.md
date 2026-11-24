# Achievements and recognition

Status: **v1 engine and catalogue; community-signal and telemetry triggers planned**.

Achievements are **recognition, not currency**. They never add to the Legacy
Score, never unlock permissions, and never appear in a ranking. They exist to
tell a learner: *the community noticed how you behaved*.

That constraint is what makes secret achievements safe. If an achievement paid
points, the fastest path would be to farm it. Because it pays nothing, the only
reason to pursue one is that it describes something worth being.

## Design principles

Achievements reward:

- curiosity;
- integrity;
- mentorship;
- innovation;
- service;
- persistence;
- collaboration.

Achievements never reward:

- time spent;
- points earned;
- lab farming;
- attendance;
- streaks;
- content volume.

## Two visibilities

| Visibility | Before earning | After earning |
|---|---|---|
| **Public** | title and criteria are visible | title, criteria, and earned date |
| **Secret** | only a count of undiscovered secrets | title and a short earned message |
| **Mythic** | nothing at all | title and message only |

No secret achievement exposes a progress bar, a percentage, or a hint. The API
returns secret **keys and messages only after they are earned**. The catalogue
is server-side; the browser never receives the trigger.

## Categories

| Category | Examples |
|---|---|
| The Hidden Helpers | First Responder, No One Left Behind, The Bridge, Ripple Effect |
| Curiosity | The Rabbit Hole, What Happens If…, Cartographer |
| Builders | Left It Better, Hidden Foundation, Toolmaker, Architect |
| Integrity | The Honest Report, Responsible, Trust Earned |
| Community Legends | Campfire Keeper, The Welcome Committee, Community Builder |
| Real-World Impact | Digital Citizen, Small Business Shield, Municipal Guardian, Healthcare Defender |
| Secret Social | The Coffee Chat, The Connector, Behind the Scenes |
| Legendary | The Lighthouse, The Steward, The Legend, The Myth |

## The hidden achievement

One achievement has no public criteria, no hint, and no progress display:
**Legacy**. It is awarded only when a learner has, over at least three years,
protected an organization, taught a learner, mentored a contributor, and built
something that others used. When it is earned, the message is:

> The community is better because you were here.

## Evaluation

Every rule is deterministic and reads only **verified** records:

| Rule | Source | Trigger |
|---|---|---|
| `build_reach_100` | verified build contribution | reach of 100 or more |
| `tool_reach_10` | verified tool or integration | used by 10 or more |
| `architect_365` | verified build or protect contribution | still used 365 days after verification |
| `digital_citizen` | verified service contribution | first non-profit support |
| `small_business_shield` | verified service contributions | five small-business or non-profit supports |
| `lighthouse` | verified mentoring | 100 learners mentored by a non-instructor |
| `steward_3_years` | verified contributions | activity in three distinct years |
| `myth` | verified contributions | 10,000 people reached, 100 organizations, or five years |
| `legacy` | verified contributions | protect + teach + mentor + build used, over three years |

Rules that need telemetry the platform does not yet collect — optional-resource
views, alternative-solution discovery, question answering, introductions, study
groups, peer thanks — are **manual** in v1. An administrator records the award
with an evidence reference and a note, and the action is audited. They are not
inferred from clicks.

Time-based and percentile-based rules are deliberately deferred:

- **Trust Earned** needs a stewardship history, not a snapshot.
- **The Legend** needs a top-percentile threshold. Percentiles are comparative
  and can be gamed in a small cohort, so v1 does not award it.
- **The Myth** has a time component but also a scale component; the scale
  component is required before it can fire.

## Anti-gaming rules

1. **No score, no currency.** Achievements never feed the Legacy Score.
2. **Verified inputs only.** Raw activity, attendance, and self-reports do not
   trigger an award.
3. **Idempotent.** One award per learner per achievement, ever.
4. **No progress for secrets.** A secret cannot be ground down.
5. **Manual awards need evidence.** A manual award requires an evidence
   reference and a note, and is attributed to the administrator.
6. **No public trophy case by default.** Sharing is a later, opt-in feature.
7. **No automated accusation.** Integrity achievements are awarded for
   self-reporting and responsible disclosure, never inferred from suspicion.
8. **Small cohorts are excluded from percentile rules.** A top-1% rule requires
   a cohort large enough for the percentile to mean something.

## Data model

```text
achievement_awards
  id, institution_id, user_id
  achievement_key, source (auto|manual)
  awarded_at, awarded_by_id
  evidence_ref, note
  seen_at
  unique (user_id, achievement_key)
```

The catalogue is `app/data/achievements.yaml`. It is never sent wholesale to a
client. The API filters it by visibility and earned state.

This layer is separate from the course micro-credentials in the `achievements`
table. A course badge records completion; a recognition award records behaviour.
Neither changes the other.

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/recognition/me` | earned awards, public unearned, secret count |
| POST | `/api/recognition/evaluate` | re-evaluate rules, return newly earned |
| POST | `/api/recognition/seen` | clear the celebration queue |
| POST | `/api/recognition/{learner_id}/award` | administrator manual award |

## Privacy

- A learner sees their own awards.
- An instructor sees that a learner earned a public award only where course
  scope allows; secret awards stay private unless the learner shares them.
- Awards are excluded from public transcripts and verification pages until the
  learner explicitly opts in.
- Under-18 learners are excluded from public recognition surfaces.
- No achievement is ever used as a grade, a prerequisite, or a disciplinary
  signal.

## Delivery

| Phase | Deliverable |
|---|---|
| 6.1 | Catalogue, deterministic rules, private awards, learner view, admin manual award |
| 6.2 | Community signals: accepted answers, welcomes, introductions, study groups, peer thanks |
| 6.3 | Optional-resource and alternative-solution telemetry, with consent and retention limits |
| 6.4 | Opt-in public trophy case and transcript section |

## Acceptance criteria

- A verified contribution can trigger a public award exactly once.
- A secret award is never described before it is earned.
- Achievements do not change the Legacy Score or any permission.
- A manual award requires an evidence reference and an administrator note.
- A learner can dismiss the celebration without losing the award.
- No endpoint returns a cross-learner achievement ranking.
