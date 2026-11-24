# Impact and Legacy

Status: **v1 scoring, design for the wider guild layer**.

The competency and evidence model answers **what can this person do**. It is
necessary for accreditation, transfer, and employer trust. It is not the reason
a learner gets out of bed on a Saturday.

This page defines the second measure: **what did this person choose to do with
their capability, and did it last?**

## Separate capability from impact

| Measure | Question | Where it lives |
|---|---|---|
| Capability | What can the learner do? | Evidence ledger, rubrics, role readiness |
| Impact | What did they build, protect, teach, or serve? | Contribution ledger, this page |
| Trust | Can they be relied on? | Stewardship record |
| Meaning | How many people were affected? | Meaning Index |

Capability is reviewed. Impact is **verified and adopted**. Trust is earned
slowly and lost quickly. None of the three is a public ranking.

## The five components

| Component | Question | Example contributions |
|---|---|---|
| **Build** | What did you create? | lab, detection rule, tool, workbook, playbook, integration, research |
| **Protect** | What did you secure? | assessment, remediation, MFA rollout, policy, recovery exercise, monitoring |
| **Teach** | Who did you help learn? | workshop, mentoring, course material, teach-back, publication |
| **Serve** | Who benefited from your time? | non-profit support, community event, student support, service hours |
| **Stewardship** | Were you trusted? | responsible disclosure, maintenance, privacy care; penalties for misconduct |

### Dimension inputs in v1

| Dimension | Base | Reach means | Quality means |
|---|---|---|---|
| Build | creation effort by type | people who use it | reviewer rating of the artifact |
| Protect | risk-reduction type | people or systems protected | reviewer rating of the reduction |
| Teach | preparation effort by type | people who retained the material | feedback rating |
| Serve | service type | people served | impact rating |

For Teach, the reviewer records **retained learners**, not attendance. The
retention and feedback multipliers in the brief collapse into reach × quality:
a workshop with 120 attendees, 60% retention, and 4.8/5 feedback is entered as
72 retained learners at 4.8/5. This keeps one auditable number per factor
instead of three partially known ones.


A learner profile reads as a story, not a bar chart:

```text
Protected: 8 organizations
Built:     7 tools, 14 labs
Taught:    600 people
Mentored:  24 learners
Legacy:    5,442
Meaning:   1,168
```

## Contribution score

Every verified contribution produces one number:

```text
points = base
       × reach
       × quality
       × longevity
       × validation
       × originality
       × repeat_weight
       × decay
```

### Reconciliation with the v1 brief

The brief contains two reach scales that disagree. Its worked Build example
uses `log10(1000) + 1 = 4`, while its multiplier table lists `101–1,000 = 2.0`.
Version 1 follows the worked example and the "logarithmic growth" guardrail:
reach is one continuous logarithmic curve, not a table. It is monotone,
defensible, and cannot be gamed by crossing a tier boundary.

The brief's Build formula also omits validation. Version 1 applies validation
to every dimension, because a self-reported build is not the same contribution
as an instructor-verified build. This makes the score **lower** than the worked
example, never higher: 50 × 4 × 1.15 × 1.5 × 1.2 = 414, not 345.

### Base

The reviewer sets a base value from a published table, by contribution type.
Base is small, and it is never the whole score. Creating a lab is not worth
more than teaching 200 people.

### Reach

```text
reach = clamp(log10(max(reach_count, 1)) + 1, 1.0, 5.0)
```

Sublinear by design. A thousand users are worth four times one user, not a
thousand times. Ten thousand users cap at five.

### Quality

```text
quality = clamp(rating / 4.0, 0.5, 1.5)
```

A rating below 3.0 excludes the contribution from the score (guardrail 5).
The rating must come from a reviewer, a peer, or adoption, never from the
author.

### Longevity

Longevity measures how long the contribution kept mattering, based on the last
verified use, not on the submission date.

| Time since last verified use | Multiplier |
|---|---|
| under 1 month | 0.5 |
| 1 to 3 months | 1.0 |
| 3 to 6 months | 1.2 |
| 6 to 12 months | 1.5 |
| 12 to 24 months | 1.75 |
| 24 months or more | 2.0 |

### Validation

| Validator | Multiplier |
|---|---|
| self-reported | 0.5 |
| peer reviewed | 1.0 |
| instructor verified | 1.2 |
| industry verified | 1.5 |
| public adoption | 2.0 |

Only a reviewer, administrator, or external verification can move a
contribution to a multiplier above self-reported. Self-reported work is shown
as **pending impact** and earns no place in the legacy total until verified.

### Originality

| Originality | Multiplier |
|---|---|
| copied | 0.25 |
| modified | 0.75 |
| original | 1.0 |
| innovative | 1.5 |

### Repeat weight

The first few contributions of the same kind matter most. The nth verified
contribution of the same `(dimension, kind)` in a rolling 12 months is weighted:

```text
repeat_weight = max(0.1, 1 / (1 + 0.5 × (n - 1)))
```

So 1.0, 0.67, 0.5, 0.4, 0.33 … A learner who mentors one hundred people for
thirty seconds each cannot farm the teaching score.

### Decay

An unused contribution decays. If the last verified use is more than 24 months
old, the score is multiplied by `0.8` for each full year beyond that, with a
floor of `0.25`. Maintaining the work resets the clock and is itself a
stewardship event.

## Stewardship

Stewardship starts at **100** for a verified learner and is capped at **150**.
It is a trust record, not a skill.

| Event | Change |
|---|---|
| responsible disclosure, handled well | +20 |
| project maintained for 24 months | +15 |
| documented handover | +5 |
| abandoned an adopted project | −20 |
| academic dishonesty | −50 |
| plagiarism | −100 |
| malicious conduct | −200 |

The score is banded for display:

| Band | Range |
|---|---|
| Trusted | 90–100 |
| Established | 70–89 |
| Watch | 40–69 |
| Restricted | below 40 |

A negative event is recorded by an administrator with a reason, an evidence
reference, and an appeal path. It is never inferred from a heuristic. Only the
learner, their instructor, and the administrator who recorded it can see it.
It is never published.

## Legacy class

A class is a **self-view**, not a badge or a public title. It names the largest
share of a learner's verified impact:

| Class | Rule |
|---|---|
| Builder | Build is more than half of the verified points |
| Guardian | Protect is more than half |
| Teacher | Teach is more than half |
| Community Champion | Serve is more than half |
| Pathfinder | Build is the largest share and more than half of build points are innovative |
| Steward | No dimension is more than half, and stewardship is Trusted or Established |
| Contributor | No dimension is more than half, and the trust band is lower |

The 50% rule prevents a learner with a broad record from being mislabelled by a
small lead. A broad, trusted record is a Steward; a broad record with a lower
trust band is a Contributor.

A learner can hold one class at a time. The class does not change permissions,
grades, or access.

## Meaning Index

Legacy is a weighted contribution total. Meaning is a simpler, human count:

```text
meaning = organizations_protected × 5
        + learners_mentored        × 2
        + people_taught            × 1
        + open_source_users        × 0.1
        + communities_supported    × 10
        + years_contributing       × 25
```

It is reported beside the legacy score because a large legacy total with no
people affected is a warning sign, not a triumph.

## Anti-gaming controls

1. **Logarithmic reach.** No linear reward for volume.
2. **Repeat caps.** Diminishing weight for repeated contributions of one kind.
3. **Downstream validation.** No full credit without a reviewer or adoption.
4. **Decay.** Unused work loses weight.
5. **Quality threshold.** Rating below 3.0 or missing validation is excluded.
6. **Self-report ceiling.** Self-reported work is pending, never full credit.
7. **No time-based rewards.** Hours logged, streaks, and screen time are not
   contribution. Service hours are verified by the organization served.
8. **One ledger, no duplicate credit.** A lab, rule, or workshop appears once.
   Re-importing it does not create a second contribution.
9. **Human review for penalties.** Stewardship never falls from an automated
   signal.
10. **No leaderboard.** The platform never ranks learners by legacy or meaning.

## What this is not

- It is not a replacement for grades, evidence, or completion records.
- It is not a hiring prediction or a certification.
- It is not a measure of a person's worth.
- It does not reward presence, streak length, or content volume.
- It cannot be earned by a learner alone: verification requires another person.

## Privacy

- A learner sees their own contributions, score, band, and class.
- An instructor sees the learners they own or staff, for verification.
- An administrator sees the institution.
- Aggregates are suppressed below five learners.
- Under-18 learners are excluded from public or shared impact surfaces.
- No individual impact total appears on a public profile, transcript, or
  verification page without explicit learner consent.

## Data model (v1)

```text
impact_contributions
  id, institution_id, user_id
  dimension (build|protect|teach|serve)
  kind, title, summary
  base_points, reach_count, quality_rating
  validation_level, originality
  occurred_at, last_used_at, verified_at, verified_by_id
  status (draft|submitted|verified|rejected)
  evidence_id, content_hash, notes

stewardship_events
  id, institution_id, user_id
  points_delta, category, reason
  occurred_at, recorded_by_id, evidence_ref, visibility
```

`impact_contributions` reuses `evidence_records` where proof exists. It does
not copy the evidence. A verified contribution is linked, not duplicated.

## Delivery

| Phase | Deliverable |
|---|---|
| 6.1 | Contribution ledger v1: self-submission, reviewer verification, scoring, stewardship events, learner view, cohort suppression |
| 6.2 | Adoption tracking from lab runs, downloads, and course use; automatic reach and longevity |
| 6.3 | Guild surfaces: mentoring, workbook review, content contribution, service projects with partner verification |
| 6.4 | Transcript and portfolio section for verified impact, with learner consent |

## Acceptance criteria

- A learner can submit a contribution and see it as pending.
- A reviewer can verify, rate, and set reach; the score recomputes.
- Self-reported work never earns full credit.
- Repeated contributions of one kind produce diminishing points.
- An unused contribution decays after 24 months.
- A stewardship penalty requires a reason and an evidence reference.
- No endpoint returns a learner ranking.
- Cohort aggregates suppress below five learners.
- The learner can see why a score changed.
