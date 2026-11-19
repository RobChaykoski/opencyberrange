# Learning signal indices

Status: **proposal** (18 November 2026). A descriptive layer for curiosity,
persistence, investigation, automation, communication, and collaboration. It does
not change the Cyber DNA formula or override assessment evidence.

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

These indices answer:

- Did the learner go beyond the minimum?
- Did the learner keep working through difficulty?
- Did the learner investigate rather than guess?
- Did the learner remove repetitive work?
- Did the learner explain the work clearly?
- Did the learner work effectively with others?

They are **positive signals**, not a personality test and not a grade.

## 1. Principles

- Measure learning actions that already happen in the platform.
- Never collect keystrokes, mouse movement, or exhaustive terminal history.
- Count meaningful actions, not clicks.
- Normalise against the opportunity the learner had.
- Show confidence and evidence count beside every index.
- Use the index to start a conversation, not to label a learner.
- A low index is not a deficit; it may mean the learner had less time, a
  different learning strategy, or no opportunity.

### The six indices

| Index | What it represents |
|---|---|
| **Curiosity** | Learns beyond the minimum requirements |
| **Persistence** | Overcomes obstacles |
| **Investigation** | Finds evidence systematically |
| **Automation** | Eliminates repetitive work |
| **Communication** | Explains findings effectively, including written evidence |
| **Collaboration** | Works with others effectively |

## 2. Curiosity Index

Measures voluntary exploration beyond the assigned path.

| Input | Example signal | Weight |
|---|---|---:|
| Documentation opened | Workbook or reference sections opened and read | 25% |
| Optional labs completed | Non-required labs completed | 30% |
| Additional references accessed | External references opened from a lab or workbook | 20% |
| Extra investigations performed | Optional hunt, quiz, or analysis completed | 25% |

Normalisation:

- Count distinct resources, not repeat opens.
- Cap each input at a reasonable daily maximum to prevent click farming.
- Compare with the learner's available optional content, not an absolute
  maximum.
- Do not count a resource that was opened for less than the reading threshold.
- Do not count a link that failed to load.

Example:

```text
Documentation  8 of 12 available sections   = 67
Optional labs  3 of 5 available             = 60
References     6 distinct, capped at 8      = 75
Extra work     2 of 4 opportunities         = 50

Curiosity = 67×0.25 + 60×0.30 + 75×0.20 + 50×0.25
          = 16.75 + 18 + 15 + 12.5
          = 62.3 -> 62
```

## 3. Persistence Index

Measures effective effort through difficulty.

| Input | Definition | Weight |
|---|---|---:|
| Attempts before success | Attempts on the eventually successful lab, normalised against difficulty | 35% |
| Time spent troubleshooting | Active time before success, compared with the lab estimate | 30% |
| Recovery after failure | Successful completion after a failed attempt or a hint | 35% |

Normalisation:

- Use the learner's own baseline and the lab difficulty.
- Do not reward brute force. A hundred random attempts is not persistence.
- Cap the attempt contribution; repeated failure with no reflection should not
  raise the index.
- Recovery counts only when the learner completes after a failure, not when they
  abandon and return much later without a successful solve.
- Exclude time when the tab is hidden or the session is idle.

Example:

```text
Attempts        2nd attempt success on a standard lab = 80
Troubleshooting 48 min vs 45 min estimate             = 70
Recovery        2 recoveries in 3 difficult labs      = 75

Persistence = 80×0.35 + 70×0.30 + 75×0.35
            = 28 + 21 + 26.25
            = 75.25 -> 75
```

## 4. Investigation Index

For threat hunting and investigation work.

| Input | Definition | Weight |
|---|---|---:|
| Queries executed | Distinct, purposeful queries against the lab data | 25% |
| Evidence collected | Artifacts preserved with a source and timestamp | 25% |
| Hypotheses tested | Hypothesis, test, result, and decision recorded | 30% |
| MITRE mappings | Technique mapped with a justification | 20% |

Normalisation:

- Count distinct, purposeful actions, not repeated identical queries.
- A query must return a result or be recorded as a negative result.
- Evidence must have a source, timestamp, and hash or stable reference.
- A hypothesis must have a test and an outcome; a guess is not a hypothesis.
- A MITRE mapping must include the technique ID and a reason.
- Use the hunt rubric, not raw counts alone.

Example:

```text
Queries       6 distinct, 2 negative but documented = 70
Evidence      4 artifacts with source and hash      = 80
Hypotheses    3 tested, 2 recorded decisions        = 75
ATT&CK        2 mappings with justification         = 65

Investigation = 70×0.25 + 80×0.25 + 75×0.30 + 65×0.20
              = 17.5 + 20 + 22.5 + 13
              = 73
```

## 5. Automation Index

Measures whether the learner moves from repeated manual work to reviewed,
repeatable automation.

| Input | Definition | Weight |
|---|---|---:|
| Automation artifacts | Working scripts, playbooks, workflows, or pipelines | 40% |
| Reuse | The artifact replaces a repeated manual action and is used more than once | 25% |
| Quality | Error handling, idempotency, logging, least privilege, tests | 20% |
| Documentation | A short README, usage note, and known limits | 15% |

Normalisation:

- Count working, reviewed artifacts, not lines of code.
- A script that only runs once is a draft, not automation.
- A copied script with no review does not count.
- Dangerous automation (unbounded loops, hard-coded secrets, destructive
  commands) is rejected and does not raise the index.
- Cap each artifact at one contribution per course.

Example:

```text
Artifacts  3 reviewed scripts/playbooks       = 80
Reuse      2 used in more than one lab         = 75
Quality    tests and error handling present    = 70
Docs       README and limits documented        = 85

Automation = 80×0.40 + 75×0.25 + 70×0.20 + 85×0.15
           = 32 + 18.75 + 14 + 12.75
           = 77.5 -> 78
```

A learner who performs every task manually scores low on this index even when
their lab results are strong. That is the point: the index measures a different
capability.

## 6. Communication Index

Measures whether the learner can explain findings to the right audience.

| Input | Definition | Weight |
|---|---|---:|
| Documentation quality | The reviewed report sub-index below | 60% |
| Briefing quality | A short technical or executive brief with Q&A | 25% |
| Audience adaptation | The same finding explained to an engineer, a manager, and an auditor | 15% |

### 6.1 Documentation sub-index

| Input | Definition | Weight |
|---|---|---:|
| Technical accuracy | Findings match the evidence and are reproducible | 30% |
| Completeness | The required sections are present and sufficient | 20% |
| Evidence references | Sources, timestamps, hashes, and links are traceable | 25% |
| Executive summary | A decision-maker can understand impact, risk, and next action | 15% |
| Structure and clarity | Logical order, concise language, no unsupported claims | 10% |

Rubric anchors:

- **90–100:** an auditor could follow the report and reproduce the finding.
- **75–89:** strong, with minor gaps in evidence or summary.
- **60–74:** usable, but a reviewer must ask for missing evidence.
- **40–59:** incomplete or hard to follow.
- **0–39:** absent, unsupported, or misleading.

### 6.2 Briefing rubric

| Criterion | Weight |
|---|---:|
| States the impact and the decision needed in the first minute | 30% |
| Separates confirmed facts from assumptions | 25% |
| Answers questions without jargon | 25% |
| Names the next action, owner, and time | 20% |

### 6.3 Audience adaptation

The learner explains one finding three ways:

- to an engineer: commands, evidence, reproduction;
- to a manager: impact, risk, cost, decision;
- to an auditor: control, evidence, gap, remediation.

The same facts must remain consistent. Changing the level of detail is the
skill; changing the facts is a failure.

Example:

```text
Documentation   80 × 0.60 = 48.0
Briefing        75 × 0.25 = 18.75
Adaptation      70 × 0.15 = 10.5

Communication = 77.25 -> 77
```

Rules:

- A reviewed report is required. Self-assessed or unreviewed documents do not
  count.
- AI-assisted writing is allowed only when the learner verifies the facts,
  sources, and commands and discloses the assistance.
- Copy-pasted reports with no evidence are excluded.
- The executive summary is scored separately from the technical body.
- The index is not a writing-style grade; clarity matters, but the evidence
  matters more.

## 7. Collaboration Index

Measures how the learner works with others in a team scenario or shared
exercise.

| Input | Definition | Weight |
|---|---|---:|
| Role contribution | The learner performed the duties of their assigned role | 30% |
| Handoffs and requests | Information was requested, handed over, and acknowledged | 25% |
| Peer review and feedback | The learner reviewed a peer's work and gave useful feedback | 20% |
| Coordination | The learner avoided duplicate work and surfaced blockers | 15% |
| Shared artifact | The learner contributed to the team timeline, decision log, or report | 10% |

Normalisation:

- Use a team scenario with named roles. A group chat with no roles does not
  count.
- Score the behaviour, not popularity.
- A quiet learner can score well through a written role contribution.
- A learner who does extra work outside their role is not automatically
  collaborative; role discipline matters.
- A learner who is absent or has a context flag is not scored.
- Use the facilitator's record, not peer popularity votes.

Example:

```text
Role contribution   85 × 0.30 = 25.5
Handoffs            80 × 0.25 = 20.0
Peer review         70 × 0.20 = 14.0
Coordination        75 × 0.15 = 11.25
Shared artifact     90 × 0.10 =  9.0

Collaboration = 79.75 -> 80
```

Rules:

- Require at least one reviewed team scenario.
- Do not use message count as a proxy for collaboration.
- Do not penalise a learner for a teammate who did not participate.
- Record the role, the commitments, and the outcome.
- Provide a correction and appeal path.

## 8. Confidence and coverage

Every index reports:

- **Confidence:** high, medium, or low based on the number of distinct evidence
  items and the observation window.
- **Coverage:** the share of the index inputs that had an opportunity to be
  observed.
- **Window:** the date range used.
- **Version:** the formula version.

No index is shown when:

- the learner has fewer than two active weeks;
- the course did not offer the relevant opportunity;
- the data source was unavailable;
- the learner is in a small cohort and the index would identify them.

## 9. Use in the platform

### Learner profile

Show the six indices as a small **learning signals** card:

```text
Curiosity       62   Medium confidence
Persistence     75   High confidence
Investigation   73   Medium confidence
Automation      78   Medium confidence
Communication   77   High confidence
Collaboration   80   Medium confidence
```

Expand for the evidence and the next opportunity. Do not show a composite
"learning score".

### Risk and readiness

- Positive signals can support the portfolio and acceleration bonus in
  [CWRS](CYBER-WORKFORCE-RISK-SCORE.md).
- They cannot cancel a critical performance or safety flag.
- Investigation is relevant evidence for threat-hunting, detection, and IR role
  readiness.
- Automation is relevant for DevSecOps, detection engineering, and cloud roles.
- Communication is relevant for GRC, consulting, IR, and architecture roles.
- Collaboration is relevant for incident command, consulting, and team-based
  roles.
- Curiosity is not a substitute for required work.

### Achievements

Suggested badges:

- **Curious Mind** — high curiosity with at least three optional activities.
- **Persistent Problem Solver** — recovery after failure on three difficult
  labs.
- **Investigator** — a reviewed hunt with hypotheses, evidence, and ATT&CK
  mapping.
- **Automation Builder** — two reviewed, reused automation artifacts.
- **Evidence Writer** — a reviewed report with a strong evidence trail and
  executive summary.
- **Team Anchor** — a reviewed team scenario with strong role contribution and
  handoffs.

Badges use the existing catalogue metadata and should be gold or silver, not
platinum, unless the evidence is externally reviewed.

### Instructor view

Show the indices beside the CWRS explanation, not as a separate ranking. The
instructor can use them to spot a learner who is quietly exploring or persisting
despite a low quiz score, or a learner who explains the work well but is
overlooked because they are quiet in chat.

## 10. Anti-gaming

- Cap each input per day and per lab.
- Count distinct resources, not page reloads.
- Require a minimum reading time or a completed action.
- Do not count links that fail or pages that are immediately closed.
- Use reviewed artifacts for investigation evidence.
- Detect identical copied queries or reports and exclude them from quality
  scoring.
- Do not reward attempts without progress.
- Do not reward script length; reward working, reviewed, reused automation.
- Do not reward message count; reward role contribution and handoffs.
- Recalculate historically when the formula changes; store the version.

## 11. Privacy and fairness

- Only learning actions, never keystrokes, mouse movement, or full terminal
  history.
- Do not infer personality, motivation, disability, or mental health.
- Do not use the indices for grading, admissions, or hiring.
- Do not compare learners publicly.
- A low index does not mean a low-value learner. It may reflect access,
  confidence, language, or time.
- The learner can see and correct their own data.
- Retention follows the course policy.

## 12. Data model

| Table | Purpose |
|---|---|
| `learning_signal_snapshots` | Learner, index, score, confidence, coverage, window, formula version |
| `learning_signal_events` | Learner, index input, source, timestamp, dedupe key, metadata |
| `learning_signal_reviews` | Learner, index, reviewer, note, correction |

Reuse existing workbook, lab, quiz, hunt, and evidence records where possible.
Do not create a parallel activity log.

## 13. API shape

```json
{
  "learner": "s42",
  "window": "2026-10-21/2026-11-18",
  "formula_version": "signals-2027.1",
  "indices": {
    "curiosity": {"score": 62, "confidence": "medium", "coverage": 0.75},
    "persistence": {"score": 75, "confidence": "high", "coverage": 0.83},
    "investigation": {"score": 73, "confidence": "medium", "coverage": 0.70},
    "automation": {"score": 78, "confidence": "medium", "coverage": 0.80},
    "communication": {"score": 77, "confidence": "high", "coverage": 0.90},
    "collaboration": {"score": 80, "confidence": "medium", "coverage": 0.70}
  }
}
```

## 14. Implementation phases

1. **Phase 1 — event collection.** Define the deduplicated events for each input
   and confirm the sources exist.
2. **Phase 2 — offline calculation.** Generate the six indices for past courses
   and review the distributions with instructors.
3. **Phase 3 — learner card.** Show the indices with confidence, coverage, and
   evidence.
4. **Phase 4 — readiness and badges.** Use investigation, automation,
   communication, and collaboration evidence in role readiness and add the
   badges.
5. **Phase 5 — calibration.** Tune the weights and caps with reviewed examples.

## 15. Acceptance criteria

- Every index has a definition, formula, confidence, coverage, and window.
- No index is computed from keystrokes or mouse telemetry.
- A learner with no opportunity is not scored.
- The learner can see and correct the evidence.
- The indices are not used for grades, admissions, or hiring.
- A low index is presented as a question, not a deficit.
- The formula is versioned and reproducible.
