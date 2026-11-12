# Skill DNA

Status: **Available on platform release 2.5.0** and inherited from the
Community / Academic 1.1.3 maintenance line.

Skill DNA is a learner character sheet. It summarises what a learner has
practised in the range across six traits, gives the learner a class, points to a
certification path, and shows **practice affinities** built from the same
activity. It is **descriptive, not predictive**: it is not a grade, a ranking, a
prediction of job performance, or a claim about a learner's ability.

## The six traits

| Trait | Class | What it measures | Certification focus |
|---|---|---|---|
| Explorer | Pathfinder | Breadth across tracks, categories, and labs opened | OSINT, threat intelligence, reconnaissance |
| Builder | Artificer | Hands-on completion, time, and clean solves | AppSec, secure development, web testing |
| Tester | Assessor | Authorised offensive testing: exploitation, privilege escalation, post-exploitation, assessment, and reporting | Web application testing, penetration testing, AppSec |
| Defender | Warden | Defensive, forensics, network-analysis, and OT practice | SOC, network defence, incident response |
| Investigator | Seeker | OSINT, reconnaissance, traffic analysis, and forensics practice | DFIR, malware analysis, forensics |
| Leader | Commander | Event success, courses, badges, advanced labs, teaching | Security leadership, governance, programme delivery |

The class is the highest-scoring trait. Ties break in the order Explorer,
Builder, Tester, Defender, Investigator, Leader. A learner with no activity is a
**Recruit**.

## Practice affinities

The six traits answer "what have I practised?" The affinity panel answers a
different, still positive question: "which kind of security work does my
practice point toward next?" Affinities are not a seventh trait, a job label, or
a second score. They use the same completed-exercise records and are shown beside
the traits.

| Affinity | Evidence used | Example roles |
|---|---|---|
| Offensive Security / Penetration Testing | Web, exploitation, privilege-escalation, post-exploitation, credential-attack, and supporting reconnaissance or enumeration labs | Penetration tester, red team operator, security consultant |
| Defensive Security / SOC | Forensics, network-analysis, and OT labs | SOC analyst, detection engineer, network security analyst |
| DFIR / Investigation | OSINT, forensics, malware, and evidence-handling labs | DFIR analyst, forensic examiner, threat intelligence analyst |
| Security Leadership / Education | Event success, courses, advanced work, and teaching | Security lead, security educator, programme coordinator |

Each affinity reports an evidence level (`no_evidence`, `early`, `growing`,
`strong`) and the raw evidence behind it. The strongest positive affinity is
marked `recommended`. A learner with no offensive labs sees "No direct evidence
yet" for penetration testing, not a negative label.

### Recognising a penetration-testing direction positively

A learner is recognised for **Offensive Security / Penetration Testing** when
they have completed enough offensive core labs. The model looks for:

- completed web, exploitation, privilege-escalation, post-exploitation, or
  credential-attack exercises;
- supporting reconnaissance, enumeration, network, or authentication practice;
- clean solves, plus additional evidence across offensive categories.

The label is deliberately framed as practice: "your completed labs point
toward offensive security", not "you are a penetration tester". It is not
authorisation to test any system, a certification, or a prediction that the
learner will pass an exam. The next step pairs the technical work with scoping,
rules of engagement, and reporting so the learner builds the full professional
practice, not just exploitation technique.

## Reporting

Learning reports use the same six branches for a **skill-tree radar**. The
radar shows the mix of assigned exercises and the mix of completed exercises
for all visible courses or one selected course. It is a curriculum-coverage
view, not a learner score. Learner-level and cohort competency radar remain
planned.

## Momentum and Career Atlas

A development-preview reporting layer sits on top of Cyber DNA without changing
the six trait scores:

- **Momentum** (`2026.1`) compares the recent half of a learner's completed
  exercises with the earlier half and reports where practice is gaining or under
  friction. It uses hints, reattempts, time over the exercise estimate, and
  started-but-unfinished exercises.
- **Career Atlas** (`2026.1`) maps the six branches to career families, role
  ladders, and national salary planning ranges from Canada Job Bank and the U.S.
  Bureau of Labor Statistics.

Both are descriptive and private. They are not grades, rankings, predictions, or
salary promises. The surfaces are gated by
`advanced_dna_insights_enabled` and are off by default in production. See
[Career Atlas and Momentum](CAREER-ATLAS-AND-MOMENTUM.md) for the definitions,
data sources, and review checklist.

## Score model

Each trait is scored from **0 to 99**. Scores are capped, so a very active
learner cannot reach 100: there is always another skill or branch to develop.
Formula version: **2026.14**.

Each branch also has its own recency factor. A branch that has been quiet for
more than 14 days is reduced by up to 10% (floor 0.90), and a new completion or
knowledge check in that branch restores it. The factor is applied per branch, so
practising one area does not hide a quiet area.

| Days since last work in the branch | Factor |
|---|---:|
| 0 to 14 | 1.00 |
| 15 to 30 | 0.99 |
| 31 to 60 | 0.97 |
| 61 to 90 | 0.94 |
| More than 90 | 0.90 |

The profile also reports a **30-day directional trend**. It is rebuilt from
completion and quiz timestamps, so no snapshot table is needed. The spider-chart
point size uses a separate **evidence-strength** value: clean, unaided, advanced,
assessment, and high-scoring quiz work weighs more than a hinted walkthrough.

```text
Explorer = 7 × tracks + 2 × categories + 1.2 × min(opened_labs, 20)
           + 2 × min(tracks, 3)

Builder  = 2.0 × min(completed_labs, 25)
           + 0.04 × min(total_minutes, 1200)
           + 1.0 × min(no_hint_labs, 10)
           + 0.5 × min(perfect_labs, 10)
           + 1.0 × min(builder_labs, 10)

Tester   = 9 × min(offensive_core_labs, 12)
           + 2 × min(offensive_labs, 20)
           + 3 × min(offensive_categories, 4)
           + 1 × min(offensive_no_hint_labs, 10)
           + 3 × min(assessment_labs, 4)

Defender = 9 × min(defender_labs, 12)
           + 3 × min(defender_tracks, 4)
           + 2 × min(categories, 5)

Investigator = 9 × min(investigator_labs, 12)
               + 3 × min(investigator_tracks, 4)
               + 2 × min(categories, 5)

Leader   = 6 × min(courses, 5)
           + 2 × min(achievements, 20)
           + 4 × min(advanced_labs, 10)
           + 8 × min(instructed_courses, 3)
           + 1 × min(likes_given, 10)
```

The Builder score adds knowledge-check participation and accuracy because
understanding is part of hands-on practice:

```text
Builder += 1.5 × min(quiz_labs, 10) + 0.15 × quiz_accuracy
```

`opened_labs` is the union of labs with a session and labs with a completion.
`categories` is the number of distinct lab categories touched. `advanced_labs`
counts completions with difficulty `advanced` or `expert`. `builder_labs`,
`defender_labs`, and `investigator_labs` use the category and track mapping in
`platform/backend/app/services/skill_dna.py`. `offensive_core_labs` covers web,
exploitation, privilege escalation, post-exploitation, and credential attacks.
`assessment_labs` covers assessment and capstone-style penetration-test work.

### Continuing education

The profile reports hands-on minutes from completions in the trailing 12 months
against a **40-hour** target, displayed as hours and a 0-100% bar. The target is
a practice goal, not a certification claim, and it is not used for grading or
access.

### Tier thresholds

| Score | Tier |
|---|---|
| 90-99 | Master |
| 75-89 | Specialist |
| 50-74 | Practitioner |
| 25-49 | Apprentice |
| 1-24 | Initiate |
| 0 | Unranked |

### Why these weights

- Explorer rewards breadth, not just volume, so a learner who tries several
  domains is recognised.
- Builder rewards completion, time on task, and clean solves; hints and retries
  do not reduce the score, but clean work is rewarded.
- Tester rewards authorised offensive practice: core exploitation labs,
  breadth across offensive categories, clean solves, and assessment/reporting
  work. It is not a licence to test real systems; all practice is inside the
  platform's isolated labs.
- Defender and Investigator are deliberately different lenses on overlapping
  content. A forensics lab can feed both, because it is both defensive work and
  investigative work.
- Leader rewards courses, event success, advanced work, and teaching. Joining an
  event is not scored; event exercises count as normal labs and event success
  badges count as achievements. It is not a measure of seniority.

## Content additions and score validity

Reviewed **2026-11-10** after adding the Grade 10-12 Digital Frontier labs.
Reviewed again **2026-11-12** for formula **2026.14**: branch scores and the
overall score are capped at 99, each branch decays from its own last practice
date, the profile reports a 30-day trend and a 40-hour continuing-education
target, and spider-chart points scale with evidence strength.

The new content maps as follows:

| Lab | Category | Branch | Effect |
|---|---|---|---|
| MFA and the Lost Phone | `authentication` | Builder | +1 builder lab, completion, time, quiz |
| Media Provenance | `osint` | Investigator | +1 investigator lab, completion, time, quiz |
| Crypto Rug Pull | `osint` | Investigator | +1 investigator lab, completion, time, quiz |

Two validity points are worth watching:

1. **Event participation is context, not a trait score.**
   The raw `competitions` join count was removed from Leader in 2026.13. Event
   exercises count as normal labs through completion and time, while event
   success badges (first blood, clean sweep, perfect event, placement) count
   through `achievements`. Joining an event without solving anything does not
   raise Leader. A participation certificate is a credential, not a Cyber DNA
   signal; it is not counted in the formula.
2. **Category breadth is shared by Defender and Investigator.**
   An OSINT lab can increase the shared `categories` term and therefore add to
   both branches, even when no defensive lab was completed. The overlap is
   intentional, but if cohort reports start to look inflated, use
   domain-specific category sets rather than the shared count.

Do not change the weights, caps, or six-branch model without a formula-version
bump and a validation sample. Keep reporting the limitations: optional quizzes,
provisional timings, and small cohorts mean the score is a practice summary, not
a measure of ability.

## Titles

Achievements unlock cosmetic titles. Titles are stored as a key on the user
(`users.equipped_title`). A learner can equip one unlocked title; clearing it
returns the current class title. Hidden achievement titles show as **Secret
title** until unlocked.

Rarity is cosmetic:

| Rarity | Source |
|---|---|
| Common | First steps, learning hours, course badges |
| Uncommon | Streaks and lighter achievements |
| Rare | Skill-specific hidden badges and first-blood events |
| Epic | Clean sweeps, 30-hour learning, podium finishes |
| Legendary | Perfect events and event championships |

The catalog lives in `platform/backend/app/services/titles.py`. The title
collection is returned with every Skill DNA profile so the UI can show locked
and unlocked titles without a second request.

## Certification alignment

The profile shows the certification path for the current class using the same
track guidance as `platform/frontend/src/data/certificationPaths.js`:

| Class | Certification path |
|---|---|
| Pathfinder | OSINT |
| Artificer | Web |
| Assessor | Web / offensive security |
| Warden | Network |
| Seeker | Forensics |
| Commander | General foundations |

The path is guidance, not an official mapping. Vendor requirements change;
verify them with the vendor. The roadmap link is Paul Jerimy's Security
Certification Roadmap, with attribution.

## Data sources

- `lab_completions` — completed labs, attempts, hints, time.
- `lab_sessions` — labs opened, including unfinished labs.
- `achievements` — badges, including event success badges (first blood, clean
  sweep, perfect event, placement).
- `competition_participants` — event context; used to show participation but not
  scored in Cyber DNA.
- `course_enrollments` and `courses` — cohort and teaching activity.
- `exercise_reactions` — community likes given.

No new activity tracking is added. The feature reads existing records. Affinity
evidence also exposes `offensive_labs`, `offensive_core_labs`,
`offensive_no_hint_labs`, and `offensive_categories` in the API signals so the
UI and exports use the same numbers.

The JSON profile includes an `affinities` array. Each item has `key`, `label`,
`summary`, `roles`, `evidence_level`, `evidence`, `next_step`, and
`recommended`. The array is ordered by evidence strength, then count, so the first
positive match is the recommended next direction.

## Privacy and limits

- The profile is private to the learner and staff who already have user-detail
  access.
- Scores and affinities are descriptive. Do not use them for admissions, hiring,
  ranking, or high-stakes decisions.
- Affinity evidence is positive: it reports what the learner has practised. It
  never asserts that a learner is authorised to test, is job-ready, or has a
  particular title. The Tester trait and offensive affinity record isolated-lab
  practice; they are not a licence or permission to test any real system.
- A new learner starts at Recruit; the empty state explains how to begin.
- The model can change as the curriculum grows. Record the formula version in
  the API response and the release notes.
- Review the formula and title catalog at least once per release line, and
  update the certification mapping when a track is added or renamed.

## Design notes

- The UI is a restrained character sheet, not a fantasy game: tokens, text
  labels, and operational density from the OpenCyberRange design system.
- The profile uses tabs so the page does not become one long scroll. **Skill
  tree** is its own tab; Overview, Learning record, Account, and Security &
  privacy hold the other tasks.
- The skill tree is a six-branch radar with a text legend and branch cards.
  It never relies on colour alone.
- Each bar exposes a text score and `role="progressbar"` values. The SVG tree
  exposes an accessible label with every branch score.
- The title collection is collapsed by default so the profile stays scannable.
- At narrow widths the class card and trait list stack; the tree legend moves
  below the chart and the title grid reflows to one column.
