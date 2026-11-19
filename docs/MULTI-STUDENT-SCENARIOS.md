# Multi-student incident scenarios

Status: **proposal** (18 November 2026). This is a design for collaborative
exercises; it is not implemented in the platform yet.

Presentation follows [progressive disclosure](INFORMATION-DESIGN-PROGRESSIVE-DISCLOSURE.md): summary first, detail on request, and the learner controls what stays visible.

The current catalogue is strong on individual lab work. Real incident response
is collaborative, and the communication gap is one of the ten employer gaps.
This design adds a facilitated, role-based scenario without turning the platform
into a chat product.

## 1. Learning goal

A team must handle one incident from first alert to post-incident review. Each
learner sees a different slice of the evidence. The team has to ask for the
right information, make a decision, record it, and explain it to a different
audience.

The scenario tests:

- technical triage and evidence handling;
- role-appropriate communication;
- coordination under incomplete information;
- cloud, identity, and storage judgement;
- compliance and notification discipline;
- a defensible decision record.

## 2. Example scenario: hospital cloud breach

A phishing email leads to an OAuth consent grant. The attacker uses the token to
read a storage account that contains patient documents. The team must contain
the incident, preserve evidence, decide whether notification is required, and
brief the CIO.

| Role | Sees | Can do | Cannot see |
|---|---|---|---|
| **SOC Analyst** | SIEM alerts, sign-in events, endpoint telemetry, initial ticket | Triage, escalate, request more logs | Legal advice, executive budget, full HR context |
| **Incident Commander** | Timeline, status board, decision log, injects, team messages | Declare severity, assign tasks, approve containment, run the debrief | Raw secrets, full patient records |
| **Cloud Engineer** | Cloud console, IAM policies, storage configuration, audit logs | Disable keys, revoke sessions, change bucket policy, rotate secrets | Compliance advice, executive discussion |
| **Compliance Officer** | Data classification, retention policy, notification matrix, evidence checklist | Approve evidence handling, flag notification duties, request records | Raw endpoint telemetry unless requested |
| **CIO** | Business impact, service status, executive summary, cost of containment | Approve downtime, authorise external communication, set priorities | Raw logs, secrets, patient data |

The Cloud Engineer can contain the incident, but only the Incident Commander can
authorise it. The Compliance Officer can require preservation before cleanup.
The CIO sees the business impact, not the packet capture.

## 3. Shared workspace

The scenario provides one shared workspace with role-scoped views:

- **Incident board** — severity, status, owner, next review time.
- **Timeline** — every event, decision, and evidence item, with a visibility
  label (`team`, `command`, `compliance`, `private`).
- **Evidence locker** — immutable artifacts with hashes and chain-of-custody
  entries.
- **Decision log** — decision, owner, rationale, alternatives, time.
- **Requests** — "ask the cloud engineer for the bucket policy", "ask
  compliance whether notification is required".
- **Announcements / injects** — facilitator-controlled events.
- **Reports** — technical finding, executive summary, notification record.

The timeline is the primary assessment artifact. A correct answer with no
timeline is not a pass.

## 4. Information asymmetry

Asymmetry is the point of the exercise, but it must be fair:

- Every role receives enough information to contribute.
- Missing information can be requested through a named role, not guessed.
- A request has a response time, so the team learns to parallelise.
- The facilitator can release a clue to one role, a subgroup, or the whole team.
- No role receives the flag or the answer. The answer is the quality of the
  investigation and the decision record.

## 5. Scenario flow

1. **Alert** — the SOC Analyst receives a suspicious sign-in and a storage-read
   anomaly.
2. **Triage** — the team classifies severity and opens the incident.
3. **Scoping** — the Cloud Engineer checks IAM, consent grants, and bucket
   policy. The Compliance Officer checks data classification.
4. **Containment** — revoke sessions, disable the key, restrict the bucket.
5. **Eradication** — remove the malicious app consent and the persistence path.
6. **Notification decision** — the Compliance Officer and CIO decide whether
   external notice is required, with legal review.
7. **Recovery** — restore service, verify the fix, monitor for recurrence.
8. **Post-incident review** — timeline, root cause, control gaps, actions.
9. **Executive brief** — five-minute read-out with impact, decisions, and
   remaining risk.

## 6. Injects

Injects keep the scenario moving and test communication:

- A second sign-in from a new country appears after containment.
- The bucket contains a file that may be patient data; compliance must decide
  how to handle it.
- The CIO asks for a status update in ten minutes.
- A journalist calls the help desk.
- A backup restore fails.
- The attacker's token is still valid after the first revocation attempt.

Each inject has a trigger, a target role, a visible artifact, and a scoring
note. The facilitator can pause, replay, or skip an inject.

## 7. Platform mechanics

A future implementation needs:

- a scenario run with a team, start/end time, and facilitator;
- role assignment per learner;
- a role-scoped view over the same underlying records;
- artifact visibility and request/approval;
- shared timeline and decision log;
- scheduled and manual injects;
- evidence hashing and immutable storage;
- a debrief export with all role views merged;
- an instructor console to observe, inject, and score.

The scenario must not require learners to share a password or a browser session.
Each learner signs in with their own account and sees only their role view.

## 8. Proposed data model

| Table | Purpose |
|---|---|
| `scenario_definitions` | Scenario, version, roles, injects, rubric |
| `scenario_runs` | One facilitated run, team, facilitator, state, timestamps |
| `scenario_role_assignments` | Learner, run, role |
| `scenario_artifacts` | Evidence item, source, hash, visibility, role scope |
| `scenario_timeline_entries` | Event, actor, time, visibility, linked artifact |
| `scenario_decisions` | Decision, owner, rationale, alternatives, time |
| `scenario_requests` | Requesting role, target role, state, response |
| `scenario_injects` | Inject, trigger, target, content, release time |
| `scenario_reports` | Technical report, executive summary, notification record |
| `scenario_scores` | Rubric scores, evidence links, facilitator notes |

Use the existing tenant and course boundary. Do not create a second identity
system. Reuse the platform's audit and consent rules.

## 9. Assessment rubric

| Dimension | Weight | Evidence |
|---|---:|---|
| Technical accuracy | 25% | Correct scope, containment, root cause |
| Evidence handling | 20% | Hashes, chain of custody, timeline quality |
| Decision quality | 20% | Rationale, alternatives, timing |
| Role communication | 20% | Audience-appropriate summary and updates |
| Compliance judgement | 10% | Notification and retention decisions |
| Team coordination | 5% | Requests, handoffs, no duplicated work |

A team can pass with an imperfect technical fix if the evidence and decisions
are defensible. A team cannot pass by guessing the answer with no record.

## 10. Facilitation

The facilitator needs:

- a runbook with the intended timeline and inject schedule;
- a role briefing for each learner, delivered before the run;
- an observer view that shows all role views without editing them;
- a pause/resume control;
- a debrief script;
- a safe way to remove a participant or reset the run.

The first delivery can be instructor-led with the existing platform plus a
shared document. The role-scoped platform view is phase two.

## 11. Security and privacy

- Never use real patient, learner, or institutional data. Use synthetic records
  and clearly labelled fake identifiers.
- No real secrets in scenario artifacts. Secrets are generated per run.
- Role views enforce authorisation on the server, not only in the UI.
- The facilitator cannot read a learner's private notes unless the scenario says
  so.
- The debrief export redacts secrets and personal data.
- Retain scenario records under the course retention policy and allow erasure.

## 12. Implementation phases

1. **Phase 1 — instructor-led.** One scenario definition, PDF role briefs,
   shared timeline in the LMS, manual scoring. No platform change.
2. **Phase 2 — role views.** Scenario run, role assignment, shared timeline,
   artifact visibility, instructor observer.
3. **Phase 3 — injects and requests.** Scheduled injects, role requests,
   decision log, automatic rubric capture.
4. **Phase 4 — debrief and analytics.** Merge role views, export the timeline,
   compare cohorts, and feed the communication and IR competency evidence.

## 13. Acceptance criteria

- Each learner can sign in separately and sees only their role view.
- A request to another role is recorded and answered.
- The timeline, decisions, and evidence survive a page refresh.
- The facilitator can inject an event and pause the run.
- The debrief merges all views without leaking a private note.
- No real secret or personal data appears in any artifact or export.
- The scenario can be run twice with the same definition and different teams.

## 14. Anti-patterns

- A group chat with no roles and no record.
- A single shared login.
- Hiding the rubric until the end.
- Rewarding the fastest guess.
- Using real malware, real patient data, or real cloud credentials.
- Making the facilitator the only source of truth.
