# Competency matrix and lab health dashboard

Status: **pilot implementation** (19 November 2026). The instructor dashboard now exposes the support queue, lab health, on-demand capability detail, a support-record workflow, lab-health review history, and case follow-ups. Release 5.20.0 adds context flags, support actions with outcomes, flag states, and a calibration view. Release 5.21.0 adds case ownership, priority, overdue and due-soon follow-ups, and a Follow-ups view. Release 5.22.0 adds instructor calibration reviews of the provisional band. Full validation remains. Builds on the existing
[competency framework](COMPETENCY-FRAMEWORK.md),
[instructor analytics](INSTRUCTOR-ANALYTICS.md), and
[role readiness](ROLE-READINESS-SCORING.md).

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

Two views answer two different questions:

- **Competency matrix** — what can this learner do, and where is the evidence
  thin?
- **Lab health dashboard** — is the exercise working, or is the platform,
  workbook, or difficulty the problem?

Neither view is a leaderboard. Neither replaces the evidence.

## 1. Capability framework

The matrix is a presentation layer over the existing competency taxonomy, not a
second taxonomy. Eight capabilities give learners and instructors a readable
summary:

| Capability | Underlying competencies (examples) |
|---|---|
| SOC operations | SIEM, alert triage, log analysis, escalation |
| Cloud security | Cloud identity, storage, posture, logging |
| Threat hunting | Hypothesis, ATT&CK mapping, telemetry, evidence |
| Incident response | Triage, containment, eradication, recovery, reporting |
| IAM | Authentication, authorization, RBAC/ABAC, PAM, SSO |
| GRC | Control mapping, risk register, audit evidence, notification |
| Automation | Python, APIs, SOAR, CI/CD, detection-as-code |
| Architecture | Threat modeling, trust boundaries, segmentation, design review |

Each capability has sub-skills. Example:

```text
Cloud security
  Identity and access
    IAM policy review
    Conditional access
    Workload identity
  Storage
    Public access review
    Versioning and retention
    Encryption
  Detection
    Cloud audit logs
    Sign-in anomalies
    Resource changes
```

A learner sees a score for each capability and can expand to the sub-skills. The
score is backed by the same five competency dimensions used elsewhere:

- knowledge 20%
- execution 30%
- troubleshooting 20%
- documentation 15%
- communication 15%

## 2. Student matrix

Example:

| Capability | Score | Confidence | Evidence |
|---|---:|---|---|
| SOC operations | 93 | High | 9 labs, 6 detections, 2 clean solves |
| Detection engineering | 90 | High | 4 Sigma rules, 2 tuned alerts |
| Incident response | 82 | Medium | 1 capstone, 2 timelines |
| Cloud security | 71 | Medium | 3 cloud labs, 1 policy fix |
| IAM | 44 | Low | 1 lab, no access-review artifact |
| GRC | 58 | Low | 1 control matrix, no audit response |
| Automation | 66 | Medium | 2 scripts, no CI evidence |
| Architecture | 40 | Low | 1 threat model draft |

The matrix immediately shows the next best move: IAM and architecture are the
weakest measured capabilities, and GRC has low confidence rather than proven
weakness.

Rules:

- Show **no evidence** instead of zero when nothing is measured.
- Show confidence beside every score.
- Pair colour with a text label and sample size.
- Let the learner expand a cell to the evidence.
- Keep the matrix private to the learner and authorised instructors.
- Do not compare learners publicly.

## 3. How capability scores are computed

1. Map each lab, quiz, workbook, capstone, and team scenario to competencies
   using the existing contracts.
2. Roll competencies up to capabilities using a versioned mapping file.
3. Use the existing five-dimension competency score; do not invent a second
   score.
4. Weight capstone and team-scenario evidence more than a single quiz.
5. Mark a capability **provisional** when fewer than three competencies or two
   evidence types contribute.
6. Decay older evidence only under the existing Cyber DNA rules; do not apply a
   second decay.
7. Store the mapping and formula version with every snapshot.

The matrix must be reproducible from the evidence. If two reviewers cannot
reconstruct the number, the mapping is wrong.

## 4. Lab health dashboard

The dashboard tracks infrastructure and learning health together.

### Infrastructure

| Signal | Healthy | Warning | Degraded |
|---|---|---|---|
| Spawn success | ≥ 98% | 90–97% | < 90% |
| Image availability | All required images present | One optional image missing | Required image missing |
| Median spawn time | < 60 s | 60–120 s | > 120 s |
| Session drops | < 2% | 2–5% | > 5% |
| Network/tap health | Reachable | Intermittent | Down |

### Learning

| Signal | Meaning |
|---|---|
| Start rate | Learners who opened the lab |
| Completion rate | Learners who submitted a correct flag |
| Abandonment | Started but inactive beyond the window |
| Attempts | Median attempts and share with 3+ |
| Hint pressure | Median hints and share with 3+ |
| Time | Median time to completion and time before abandonment |
| Feedback | Difficulty, clarity, and learning-value ratings |
| Error signatures | Repeated setup, command, or file-not-found errors |

### Good challenge or broken instructions?

Low success is not automatically a defect. Use the pattern:

| Pattern | Likely meaning | Action |
|---|---|---|
| Low success, low hints, long time, positive clarity | Good challenge | Keep; add a stretch hint |
| Low success, high hints, short time, negative clarity | Instructions or prerequisite gap | Review workbook and prerequisites |
| Low success, high technical failures | Platform or image problem | Fix infrastructure first |
| High success, low time, low learning value | Too easy | Raise difficulty or add a variant |
| Low start rate | Discoverability or scheduling | Check catalogue placement and course plan |
| High abandonment after one step | Broken step or missing target | Inspect the step and the lab logs |

A lab with a 47% success rate can be excellent or broken. The dashboard must
show the supporting signals before it labels the lab unhealthy.

## 5. Red flags

A red flag is a prompt to inspect, not a verdict:

- success rate below the cohort baseline by more than two standard deviations;
- abandonment above 30% after the first graded step;
- more than 20% of learners reporting a technical error;
- a single error signature in more than 10% of attempts;
- median time more than twice the estimate with low completion;
- hint pressure above the 90th percentile with negative clarity;
- a lab that was healthy last term and is now degraded.

Each flag includes the sample size, the comparison baseline, and a link to the
lab, workbook, image, and recent sessions.

## 6. Dashboard layout

```text
Lab health
  Filters: course, track, level, date range, status
  Summary: healthy / warning / degraded / no data

  Lab                         Success  Abandon  Hints  Time   Status
  Sentinel Intro               96%      4%      0.8    38m    Healthy
  Threat Hunt 101              92%      6%      1.1    52m    Healthy
  OAuth Attack                 47%      22%     4.2    71m    Degraded
  IAM Policy Lab               61%      18%     3.4    65m    Warning

  Selected lab: OAuth Attack
    Infrastructure: healthy
    Learning: low success, high hints, negative clarity
    Error cluster: "consent page returns 403" (18% of attempts)
    Recommended action: review the consent step and the Keycloak client
```

The selected lab panel must show:

- infrastructure status and recent incidents;
- learning signal chart;
- top error signatures;
- feedback themes with sample size;
- affected learners (authorised view only);
- a review action and owner;
- history of previous fixes and whether they worked.

## 7. Data model

Reuse existing completion, attempt, hint, quiz, feedback, and session tables.
Add only:

| Table | Purpose |
|---|---|
| `capability_definitions` | Capability, version, description, order |
| `capability_mappings` | Capability to competency, weight, version |
| `capability_snapshots` | Learner, capability, score, coverage, confidence, formula version |
| `lab_health_snapshots` | Lab, window, success, abandonment, hints, time, errors, status |
| `lab_health_reviews` | Lab, reviewer, finding, action, outcome, created_at |
| `lab_error_signatures` | Lab, normalized error, count, first_seen, last_seen |

Do not duplicate the competency taxonomy or the evidence ledger.

## 8. API shape

```json
{
  "learner": "s42",
  "capabilities": [
    {
      "id": "soc-operations",
      "label": "SOC operations",
      "score": 93,
      "confidence": "high",
      "coverage": 0.88,
      "evidence_count": 17,
      "provisional": false
    }
  ],
  "formula_version": "capability-2027.1"
}
```

```json
{
  "lab": "oauth-attack",
  "window": "2026-11-01/2026-11-18",
  "status": "degraded",
  "success_rate": 0.47,
  "abandonment_rate": 0.22,
  "median_hints": 4.2,
  "median_minutes": 71,
  "sample_size": 32,
  "signals": ["low_success", "high_hints", "negative_clarity"],
  "errors": [
    {"signature": "consent page returns 403", "share": 0.18}
  ]
}
```

## 9. Instructor workflow

1. Review the degraded lab and the supporting signals.
2. Decide: infrastructure, workbook, prerequisites, difficulty, or a healthy
   challenge.
3. Record the decision and the owner.
4. Fix or annotate the lab.
5. Recheck after the next cohort or the next 20 attempts.
6. Keep the review history so the same issue is not rediscovered each term.

For learner support, the same loop applies:

1. Open a case from the support queue when a learner needs a human check-in.
2. Assign an owner, a priority, and the next follow-up date.
3. Record the action and its outcome in the append-only support record.
4. Work the **Follow-ups** view; overdue and due-soon cases are prompts, not
   compliance failures.
5. Close the case when the support loop is complete.

Never ask instructors to troubleshoot by email. The dashboard is the shared
record.

## 10. Guardrails

- Minimum sample size for a lab health status; below it, show **no data**.
- Compare a lab with its own baseline and the course baseline, not with a
  different course.
- Distinguish technical failure from learning difficulty.
- Do not rank learners by capability score.
- Do not publish lab failure rates to learners.
- Suppress small cohorts in aggregate views.
- Under-18 learners follow the existing analytics exclusion.
- A low score with low coverage is **unmeasured**, not weak.
- A degraded lab is not proof that the instructor or the learners failed.

## 11. Implementation phases

1. **Phase 1 — capability mapping.** Publish the 8 capabilities and map the
   existing competencies to them. No UI change.
2. **Phase 2 — learner matrix.** Add the expandable matrix to the profile with
   score, confidence, and evidence links.
3. **Phase 3 — lab health v1.** Combine infrastructure and learning signals,
   with the good-challenge/broken-instructions distinction.
4. **Phase 4 — error signatures and reviews.** Add normalized errors, review
   actions, and history.
5. **Phase 5 — calibration.** Compare the matrix and lab health flags with
   instructor judgement and adjust.

## 12. Acceptance criteria

- The matrix uses the existing competency scores and evidence.
- Every capability cell expands to evidence.
- No score is shown without confidence and coverage.
- A lab cannot be marked degraded from success rate alone.
- Technical failures are separated from learning difficulty.
- The dashboard has a table view and keyboard access.
- A lab review records the action and the outcome.
- No public learner ranking is produced.
