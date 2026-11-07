# Skill DNA

Status: **Released in 1.1.3, 2.1.4, and 3.0.3** across Community / Academic,
Professional, and Enterprise.

Skill DNA is a learner character sheet. It summarises what a learner has
practised in the range across five traits, gives the learner a class, points to
a certification path, and shows **practice affinities** built from the same
activity. It is **descriptive, not predictive**: it is not a grade, a ranking, a
prediction of job performance, or a claim about a learner's ability.

## The five traits

| Trait | Class | What it measures | Certification focus |
|---|---|---|---|
| Explorer | Pathfinder | Breadth across tracks, categories, and labs opened | OSINT, threat intelligence, reconnaissance |
| Builder | Artificer | Hands-on completion, time, and clean solves | AppSec, secure development, web testing |
| Defender | Warden | Defensive, forensics, network-analysis, and OT practice | SOC, network defence, incident response |
| Investigator | Seeker | OSINT, reconnaissance, traffic analysis, and forensics practice | DFIR, malware analysis, forensics |
| Leader | Commander | Events, courses, badges, advanced labs, teaching | Security leadership, governance, programme delivery |

The class is the highest-scoring trait. Ties break in the order Explorer,
Builder, Defender, Investigator, Leader. A learner with no activity is a
**Recruit**.

## Practice affinities

The five traits answer "what have I practised?" The affinity panel answers a
different, still positive question: "which kind of security work does my
practice point toward next?" Affinities are not a sixth trait, a job label, or a
second score. They use the same completed-exercise records and are shown beside
the traits.

| Affinity | Evidence used | Example roles |
|---|---|---|
| Offensive Security / Penetration Testing | Web, exploitation, privilege-escalation, post-exploitation, credential-attack, and supporting reconnaissance or enumeration labs | Penetration tester, red team operator, security consultant |
| Defensive Security / SOC | Forensics, network-analysis, and OT labs | SOC analyst, detection engineer, network security analyst |
| DFIR / Investigation | OSINT, forensics, malware, and evidence-handling labs | DFIR analyst, forensic examiner, threat intelligence analyst |
| Security Leadership / Education | Events, courses, advanced work, and teaching | Security lead, security educator, programme coordinator |

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

Learning reports use the same five branches for a **skill-tree radar**. The
radar shows the mix of assigned exercises and the mix of completed exercises
for all visible courses or one selected course. It is a curriculum-coverage
view, not a learner score. Learner-level and cohort competency radar remain
planned.

## Score model

Each trait is scored from 0 to 100. Scores are capped, so a very active learner
cannot exceed 100. Formula version: **2026.11**.

```text
Explorer = 7 × tracks + 2 × categories + 1.2 × min(opened_labs, 20)
           + 2 × min(tracks, 3)

Builder  = 2.0 × min(completed_labs, 25)
           + 0.04 × min(total_minutes, 1200)
           + 1.0 × min(no_hint_labs, 10)
           + 0.5 × min(perfect_labs, 10)
           + 1.0 × min(builder_labs, 10)

Defender = 9 × min(defender_labs, 12)
           + 3 × min(defender_tracks, 4)
           + 2 × min(categories, 5)

Investigator = 9 × min(investigator_labs, 12)
               + 3 × min(investigator_tracks, 4)
               + 2 × min(categories, 5)

Leader   = 12 × min(competitions, 5)
           + 6 × min(courses, 5)
           + 2 × min(achievements, 20)
           + 4 × min(advanced_labs, 10)
           + 8 × min(instructed_courses, 3)
           + 1 × min(likes_given, 10)
```

`opened_labs` is the union of labs with a session and labs with a completion.
`categories` is the number of distinct lab categories touched. `advanced_labs`
counts completions with difficulty `advanced` or `expert`. `builder_labs`,
`defender_labs`, and `investigator_labs` use the category and track mapping in
`platform/backend/app/services/skill_dna.py`.

### Tier thresholds

| Score | Tier |
|---|---|
| 90–100 | Master |
| 75–89 | Specialist |
| 50–74 | Practitioner |
| 25–49 | Apprentice |
| 1–24 | Initiate |
| 0 | Unranked |

### Why these weights

- Explorer rewards breadth, not just volume, so a learner who tries several
  domains is recognised.
- Builder rewards completion, time on task, and clean solves; hints and retries
  do not reduce the score, but clean work is rewarded.
- Defender and Investigator are deliberately different lenses on overlapping
  content. A forensics lab can feed both, because it is both defensive work and
  investigative work.
- Leader rewards community and cohort participation, events, advanced
  work, and teaching. It is not a measure of seniority.

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
| Warden | Network |
| Seeker | Forensics |
| Commander | General foundations |

The path is guidance, not an official mapping. Vendor requirements change;
verify them with the vendor. The roadmap link is Paul Jerimy's Security
Certification Roadmap, with attribution.

## Data sources

- `lab_completions` — completed labs, attempts, hints, time.
- `lab_sessions` — labs opened, including unfinished labs.
- `achievements` — badges and competition awards.
- `competition_participants` — event participation.
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
  particular title.
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
- The skill tree is a five-branch radar with a text legend and branch cards.
  It never relies on colour alone.
- Each bar exposes a text score and `role="progressbar"` values. The SVG tree
  exposes an accessible label with every branch score.
- The title collection is collapsed by default so the profile stays scannable.
- At narrow widths the class card and trait list stack; the tree legend moves
  below the chart and the title grid reflows to one column.
