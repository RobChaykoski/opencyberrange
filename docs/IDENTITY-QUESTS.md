# Identity and Quests

Status: **planning**. This is the learner-facing layer above the competency and
evidence model. It changes the first question from "which course?" to "who are
you trying to become?".

A learner chooses an identity. The platform proposes quests around that identity.
A quest is a short, evidence-producing path through labs, scenarios, workbook
answers, and a capstone. It is not a course, and it does not replace the
catalogue.

## Traditions are observed, then a mission

A learner does **not** choose a tradition. The archive infers a tradition from
verified contribution, because people answer aspirationally about who they are
but behave more honestly over time.

The learner chooses a **mission** — a journey such as *Protect healthcare* or
*Build security tools*. The mission is concrete. The tradition explains why it
matters, and it appears only when the evidence supports it.

A tradition is a durable direction of practice that survives changes in tools
and job titles:

| Tradition | Archetype | What it carries forward |
|---|---|---|
| Protection | The Guardians | incident response, detection, forensics, crisis response |
| Creation | The Builders | engineering, automation, tools, platforms |
| Discovery | The Cartographers | research, intelligence, analysis, reverse engineering |
| Stewardship | The Keepers | governance, documentation, maintenance, continuity |
| Illumination | The Lighthouses | teaching, mentoring, curriculum, technical writing |
| Connection | The Bridgekeepers | community, events, facilitation, partnerships |
| Service | The Citizens | outreach, volunteering, non-profit and public support |
| Judgment | The Wardens | architecture, threat modelling, risk and privacy decisions |

A journey names the tradition it belongs to so the archive can explain a
pattern. That name is context, not a self-label. A tradition may contain
several journeys.

This is the eight-tradition frame from [The Age of Foundations](FOUNDATIONS.md).

## Why identity first

Courses and labs are content. An identity is a direction. A learner who wants to
become **The Investigator** needs a different first quest from a learner who
wants to become **The Builder**, even when both start with the same network
fundamentals.

Identity is a **lens**, not a permanent label:

- a learner can choose more than one identity;
- a learner can change identity at any time;
- the platform keeps the evidence, not the label;
- the identity never appears on a public profile or a ranking;
- an instructor can suggest an identity, but the learner chooses.

## Identities

| Identity | Direction | Existing affinity or role family | Example quests |
|---|---|---|---|
| **The Defender** | Detect, triage, contain, and recover | Defensive security / SOC | alert triage, detection rule, incident timeline |
| **The Investigator** | Reconstruct what happened from evidence | DFIR / Investigation | memory triage, timeline, finding for a non-specialist |
| **The Builder** | Design and build resilient systems | Application security / product security | secure design note, code review, threat model |
| **The Operator** | Run platforms, networks, identity, and cloud | Platform / network engineering | service health, IAM change, cloud control |
| **The Leader** | Turn technical work into programme decisions | Security leadership / education | risk register, decision brief, team debrief |
| **The Researcher** | Explain adversary behaviour and new risk | Threat intelligence / malware / AI | sample triage, intelligence product, experiment |
| **The Teacher** | Help others learn and practise | Security education | teach-back, rubric review, mentoring note |
| **The Entrepreneur** | Turn security capability into a product or service | Consulting / product | client scoping, offer design, delivery plan |
| **The Hacker** | Find and demonstrate weaknesses safely | Offensive security / red team | enumeration, exploitation, authorised report |
| **The Guardian** | Govern risk, privacy, and compliance | GRC / privacy / audit | control mapping, impact assessment, evidence pack |

The names are invitations, not diagnoses. A learner who chooses **The Guardian**
can still practise offensive labs; the identity shapes the recommended path, not
the permission model.

## Quest model

```text
quest
  identity
  title, promise, duration
  competency targets
  required evidence
  steps
  capstone
  version, review status
```

A step is one of:

| Step type | Example | Evidence |
|---|---|---|
| Lab | complete a specific exercise | flag, validation, artifact |
| Workbook | answer an analyst prompt | rubric-scored answer |
| Scenario | respond to an inject or incident | decision record, timeline, report |
| Artifact | upload a rule, query, report, or SBOM | hash, review state |
| Reflection | explain a decision or gap | rubric-scored note |
| Capstone | integrate the quest | reviewed capstone package |

A quest has:

- **one identity** and one or more competency targets;
- **three to seven steps** so it fits a term or a short sprint;
- **at least one written evidence step**, not only flags;
- **a capstone or integration step** for advanced quests;
- **a review status** and a version;
- **no hidden prerequisite** that the learner cannot see.

## Generation rules

The platform can generate a quest from:

1. the chosen identity;
2. the learner's accepted evidence and current gaps;
3. the reviewed lab contracts and available scenarios;
4. the learner's target role or course, if any;
5. the instructor's constraints, if the quest is assigned.

Rules:

- **Deterministic first.** The quest template and selection rules are data, not
  a model prompt.
- **Evidence-aware.** Prefer a step that fills a missing competency or a
  documentation gap.
- **No dead ends.** Every step must be available, or the quest says what
  prerequisite to complete first.
- **Learner choice.** The platform proposes two or three quests; the learner
  picks one.
- **Instructor review.** A new quest template is reviewed like curriculum.
- **Adaptation.** Completing a step updates the next recommendation, but the
  quest version stays stable for reporting.
- **No AI-only grade.** A generated quest can suggest, not certify.

## Data model

```text
identities
  id, label, promise, summary, affinity_key, role_family, status

quest_templates
  id, identity_id, version, title, promise, duration, review_status

quest_steps
  quest_id, order, step_type, target_type, target_id, required, evidence_rule

quest_enrollments
  learner_id, quest_id, version, chosen_at, status, source

quest_progress
  enrollment_id, step_id, status, evidence_id, completed_at

quest_recommendations
  learner_id, identity_id, quest_id, reason, generated_at
```

Reuse `evidence_records` for proof. A quest step links to an evidence id; it does
not copy the evidence.

## UI

### First visit

```text
Who are you trying to become?

[ The Defender ] [ The Investigator ] [ The Builder ] [ The Operator ]
[ The Leader ]  [ The Researcher ]  [ The Teacher ] [ The Entrepreneur ]
[ The Hacker ]  [ The Guardian ]

You can choose more than one, and change your mind later.
```

### Quest board

```text
Your quests
  The Investigator · Quest 2 of 4
  Reconstruct a host timeline              [Continue]
  Evidence: timeline, finding, reflection

Suggested next
  The Investigator · Memory triage          [Preview]
  Why: 2 of 4 evidence steps complete; documentation is the current gap.
```

### Identity card

- the identity name and promise;
- the competencies it develops;
- the quests completed and in progress;
- the evidence the learner can show;
- a **change identity** control;
- no public label or score.

## Relationship to courses and labs

- A course can contain one or more quests.
- An instructor can assign a quest to a cohort.
- A lab can appear in several quests.
- A quest does not change lab permissions or certificate rules.
- The transcript records quests, evidence, and artifacts, not only completions.
- The Career Atlas and Cyber DNA remain descriptive views; identity is the
  learner's chosen direction, not a prediction.

## Safeguards

- Identity is not a diagnosis, a personality test, or a permanent label.
- Multiple identities are allowed; switching does not erase evidence.
- No public identity ranking or learner comparison.
- Under-18 learners are excluded from public or shared identity surfaces.
- Small-cohort suppression applies to any aggregate identity view.
- A quest recommendation explains why it was chosen and what evidence it fills.
- An instructor can remove a generated quest that is misaligned.
- No quest requires a real external target or live malware.

## Delivery phases

| Phase | Deliverable |
|---|---|
| 6.2 | Identity catalogue, learner identity selection, quest preview from existing labs and evidence |
| 6.3 | Quest enrollment, deterministic generation, instructor assignment, progress and evidence links |
| 6.4 | Scenario/team quests, capstone integration, transcript quest section |

## Acceptance criteria

- A learner can choose one or more identities and change them.
- A generated quest names its competency targets and evidence.
- Every quest step points to an available lab, scenario, or writing task.
- A completed step links to an evidence record; no duplicate evidence copy.
- An instructor can review, assign, and remove a quest.
- A transcript can show quests, evidence, and artifacts without a public label.
- No identity or quest creates a ranking, a public label, or a permission change.
