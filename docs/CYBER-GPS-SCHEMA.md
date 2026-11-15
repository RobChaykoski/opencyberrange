# Cyber GPS data model

The career-guidance layer separates four questions so the recommendation logic
can change without rewriting learner history:

| Layer | Question | Source of truth |
| --- | --- | --- |
| Observed evidence | What did the learner actually do? | `lab_sessions`, `lab_completions`, `flag_attempts`, `exercise_quiz_attempts`, workbook events |
| Cyber DNA | Who does the learner appear to be? | Computed from evidence by `services/skill_dna.py` |
| Competencies | What can the learner demonstrate? | `services/competency_assessment.py`, competency taxonomy |
| Recommendations | What should the learner do next? | `services/growth_velocity.py`, `services/cyber_gps.py`, `services/career_explorer.py` |

The rule is one-way: recommendations read evidence; they never write back into
it. A later change to scoring or career data cannot silently alter the record of
what a learner completed.

## Evidence

Every completed lab is one evidence row. The database enforces one completion
per learner and lab, so a learner cannot inflate a profile by replaying the same
exercise. The row stores:

- `completed_at`, `attempts`, `hints_used`, `time_spent_minutes`;
- `lab_difficulty_snapshot` and `competency_mapping`, captured at completion time.

Snapshots matter: if the catalog later relabels a lab as "advanced", the
learner's history does not retroactively become harder or easier.

Sessions and flag attempts supply time-to-first-attempt and abandonment
signals. They are not used to award credit.

## Cyber DNA

`build_skill_dna` produces the six branches, class, titles, affinities, recency,
and a 30-day trend. It is a within-person profile: branch scores are compared
with the learner's own prior state, not with another learner.

## Competencies

`build_competency_assessment_profile` maps evidence to the curriculum's
competency taxonomy. Each competency carries its own evidence count and
confidence; a competency with one completion is labelled as early evidence.

## Growth velocity

`build_growth_velocity` compares the last 30 days with the 30 days before it,
and also exposes 30/60/90-day windows for trend charts:

- improvement: completions in the window;
- hint discipline: hints per completion (lower is better);
- challenge stretch: average difficulty from the completion snapshot;
- consistency: distinct active days and weeks.

Each signal carries a direction and a human-readable detail. The response also
contains one to three opportunities with a reason and a route, so the dashboard
can show a next step rather than a bare number.

## Confidence gating

Recommendations must not outrun the evidence.

| Evidence (distinct solved labs) | Label | What the UI may show |
| --- | --- | --- |
| 0-2 | Not enough evidence yet | Counts, starter path, no percentages or named roles |
| 3-7 | Early signal | Trends and branch direction, no named career roles |
| 8-14 | Building evidence | Career directions as "worth exploring" |
| 15+ | Established pattern | Role matches and pathway recommendations |

Thresholds live in `services/growth_velocity.py` (`MIN_PERCENT_EVIDENCE`,
`MIN_CAREER_EVIDENCE`) and are returned with the data so the frontend does not
re-implement them.

## Recommendation contract

A recommendation is only useful if the learner can see why it exists. The
dashboard shows:

- the observation ("two labs in the last 30 days");
- the reason ("your recent work is all beginner level");
- one action with a destination.

The planned `learner_snapshots` table will store the whole payload and the
factor weights used at the time, so a later scoring change does not rewrite an
old report. Until that table exists, the API builds the payload on read.

## Privacy and anti-gaming rules

1. **Personal scope.** Growth velocity and DNA are returned only to the
   requesting learner. The public profile and Celebration Wall do not expose
   them.
2. **No ranking.** The data never feeds a leaderboard or a cohort comparison.
   Instructors see aggregates with small-cohort suppression, not a growth
   league table.
3. **Minimum denominators.** No percentage is shown without at least three
   completions; no career role is named without eight.
4. **Immutable evidence.** Difficulty and competency mappings are snapshotted
   at completion; hints and attempts are recorded by the lab lifecycle, not by
   the learner.
5. **No silent reuse.** A recommendation or score change ships with its reason
   text and a schema version so a report can be explained later.
6. **No predictive claims.** "Learners like you succeed as X" is not supported
   by this release. A prediction layer would need cohort consent, calibration,
   and an explicit opt-in; it is deferred.

## Deferred

- A persisted `learner_snapshots` table with JSONB payloads and factor weights.
- NICE work-role mapping in the public transcript.
- Employer-facing transcript export with DNA, competencies, and confidence.
- The cohort-based prediction layer. It is not part of Release 5 and must not be
  represented as available.
