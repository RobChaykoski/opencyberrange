# Program layer: organizations, scenarios, transcript, and analytics

Status: **planning**. This page defines the institution-grade layer above the
evidence ledger. It does not replace the Evidence Engine; it consumes it.

The program layer answers four questions:

1. **Persistent Organizations** — what environment is the learner working in?
2. **Scenario Engine** — what is happening in that environment over time?
3. **Cyber Transcript** — what can the learner show, and how was it verified?
4. **Program analytics** — how is the cohort and the programme doing?

## Related designs

- [Identity and Quests](IDENTITY-QUESTS.md) is the learner-facing direction.
- [Impact and Legacy](IMPACT-AND-LEGACY.md) is the contribution ledger.
- [Achievements and recognition](ACHIEVEMENTS.md) is the values-based board.

## Objective 1: Persistent Organizations

A persistent organization is a long-lived, synthetic institution that a cohort
works inside across labs, scenarios, and a capstone. It is not a one-off lab
container. It has state, versions, and a reset policy.

### Templates

| Template | Example users | Example assets | Scenario fit |
|---|---|---|---|
| Hospital | clinicians, IT, records, biomedical | EHR, imaging, medical devices, identity | ransomware, data breach, insider threat |
| Municipality | clerks, public safety, IT, finance | GIS, citizen portal, SCADA/OT, email | BEC, ransomware, supply chain |
| Manufacturing | plant operators, engineers, OT, IT | PLC/HMI, MES, ERP, remote access | OT incident, supply chain, insider |
| University | faculty, students, research, IT | SIS, LMS, research data, email | data breach, BEC, insider, research espionage |
| Financial Institution | tellers, fraud, IT, risk | core banking, payment switch, IAM, email | BEC, fraud, ransomware, supply chain |

### Required domains

Each organization contains:

- **Users** — synthetic identities, roles, managers, and join/leave events.
- **Assets** — hosts, servers, endpoints, medical/OT devices, cloud resources.
- **Identity** — directory, groups, service accounts, MFA state, privileges.
- **Email** — mailboxes, distribution lists, message history, attachments.
- **Cloud** — tenants, subscriptions, storage, SaaS, logs.
- **SOC** — detections, alerts, cases, SIEM indexes, response playbooks.
- **Business processes** — payments, admissions, shipping, payroll, approvals.

### Data model

```text
organization_templates
organization_versions
organizations
org_users
org_assets
org_identities
org_mailboxes
org_messages
org_cloud_resources
org_soc_alerts
org_soc_cases
org_business_processes
org_links
```

Every object carries:

- `organization_id`, `version`, `synthetic` flag, `created_at`;
- a stable `object_key` used by scenarios and logs;
- a content hash for lineage and reset verification;
- no real person, credential, customer, or production host.

### Lifecycle

1. Instructor selects a template and a version.
2. The platform creates an organization instance for a course or cohort.
3. Scenarios attach to the instance and mutate it within a run.
4. The instructor can reset the instance to the version hash.
5. The instance can be archived but not silently edited after a run.

## Objective 2: Scenario Engine

A scenario is a versioned sequence of events and injects against an
organization. It defines what the learner must notice, decide, and do, and what
evidence proves it.

### Scenario types

- **Ransomware** — initial access, lateral movement, encryption, backup attack,
  containment and recovery.
- **Insider Threat** — data staging, exfiltration, privilege misuse, HR and
  legal context.
- **Data Breach** — exposed service, data access, notification decision,
  regulator and patient/customer impact.
- **Business Email Compromise** — phishing, mailbox rule, payment change,
  approval bypass, recovery.
- **Supply Chain Attack** — dependency compromise, vendor access, build
  provenance, disclosure.

### Scenario definition

```text
metadata: id, version, title, organization template, difficulty, duration
roles: incident lead, analyst, communications, legal, engineering
phases: preparation, detection, triage, containment, eradication, recovery, review
injects: time, actor, channel, content, expected observation
triggers: learner action, timer, log event, evidence submission
expected evidence: artifact type, rubric, competency ids, confidence
assessment: deterministic checks, rubric, team decision record
```

### Runtime

```text
scenario_run
  organization instance + scenario version + participants
  state machine: phase, clock, inject queue, open decisions
  event log: inject, learner action, system change, evidence
  reset: restore organization version, keep the run audit
```

Requirements:

- deterministic seed and replay;
- no live malware or real internet target;
- every inject and learner action is timestamped and attributable to a role;
- team scenarios record a decision log, not individual chat surveillance;
- an instructor can pause, reset, or inject a new event;
- the evidence adapter records artifacts, not keystrokes or screen capture.

### Data model

```text
scenarios
scenario_versions
scenario_runs
scenario_participants
scenario_injects
scenario_events
scenario_decisions
scenario_artifacts
```

## Objective 4: Cyber Transcript

The transcript is the read view over the evidence ledger, completions,
artifacts, rubric reviews, and role readiness. It replaces the achievement wall
as the primary learner record, while badges remain portable credentials.

The detailed proposal is in
[Digital Cyber Transcript](DIGITAL-CYBER-TRANSCRIPT.md). The program layer adds:

- the organization and scenario context to each artifact;
- team role and decision records;
- framework coverage that cites evidence, never certification;
- a verified PDF, signed JSON, Open Badge, LinkedIn summary, and GitHub
  portfolio view;
- learner-controlled visibility and revocation.

A capability transcript contains:

| Section | Source |
|---|---|
| Competencies | accepted evidence linked to taxonomy ids |
| Evidence | evidence records with rubric, reviewer, confidence, and artifact hash |
| Confidence | evidence count, coverage, and review status |
| Role readiness | role profiles and readiness gates |
| Artifacts | reports, hunts, rules, architecture reviews, risk assessments, SBOMs |
| Verification | transcript id, hash, signature, public verification URL |

## Program analytics

The analytics layer answers cohort and programme questions without ranking
individual learners.

### Strongest and weakest competencies

- Aggregate accepted evidence per competency.
- Report the learner count and acceptance rate, not just a count.
- A competency with no evidence is **unmeasured**, not weak.
- A weakest list requires a minimum evidence denominator and small-cohort
  suppression.

### Graduation readiness

- Use a target role profile and its readiness gates.
- Report the share of learners meeting the gate, with the evidence coverage.
- Suppress a cohort below five learners.
- A readiness percentage is a curriculum match, not a hiring prediction.

### Program effectiveness

- Evidence acceptance rate and review turnaround.
- Competency coverage across the programme.
- Documentation and communication evidence coverage.
- Completion, active learners, and intervention outcomes.
- Trend over time, not a single point.

### Instructor prompts

The following statements are valid **questions**, not automated labels:

| Statement | Safe answer |
|---|---|
| "These 12 students are struggling with lateral movement." | A competency gap with evidence count and affected labs; no public label. |
| "These 5 appear to be copying answers." | A private integrity queue of exact duplicate hashes or text similarity, with human review and no automated accusation. |
| "These 9 are ready for advanced content." | A readiness group with the evidence threshold and prerequisites; count only, no ranking. |
| "This cohort is weak in documentation." | Workbook and communication evidence coverage against the rubric, with the denominator. |
| "Average confidence is declining." | A confidence trend over time, with evidence volume and cohort size. |

No statement above is published as a learner label. The instructor opens the
underlying evidence record and decides.

## Lineage

The program layer keeps three distinct lineage chains:

### Data lineage

```text
source activity -> adapter -> normalized evidence -> hash
```

Examples: a flag attempt, a passed knowledge check, a workbook answer, an
artifact upload, or a scenario inject. The adapter name and version are stored.
Replaying the source does not duplicate evidence.

### Evidence lineage

```text
evidence -> competency links -> review -> appeal -> transcript reference
```

The record keeps its rubric version, reviewer, decision, and supersession link.
A correction is a new record; nothing is rewritten.

### Learning lineage

```text
competency -> lab contract -> track/chapter -> role profile -> credential
```

This is the curriculum chain that turns a lab into a learning outcome. It is
derived from the reviewed contracts and mappings, not from free text.

## Student capabilities

The SOC and detection pathway should let a learner demonstrate:

| Capability | Evidence |
|---|---|
| Investigate incidents | timeline, triage note, containment recommendation |
| Write Sigma rules | rule, positive test, false-positive test, tuning note |
| Use Sentinel | KQL query, analytic rule, incident work item, workbook |
| Present findings | executive brief, decision record, rubric review |
| Work in teams | role record, decision log, peer and instructor debrief |

These are mapped to `IR-001`, `IR-009`, `TH-008`, `CLD-006`, `PROF-005`, and
`PROF-006`, and to the scenario/team artifacts above.

## Delivery phases

| Phase | Deliverable |
|---|---|
| 6.1 | Program analytics v1: strongest/weakest competencies, documentation coverage, confidence trend, review backlog; transcript phase 1 from existing completions and evidence |
| 6.2 | Persistent organization templates for the five institution types; scenario engine MVP with one ransomware and one BEC scenario; team decision record |
| 6.3 | Transcript artifacts, signing, public verification, LinkedIn/GitHub/Open Badge export; scenario library and federation-ready bundles |

## Safeguards

- Aggregate only; no individual ranking or public label.
- Small-cohort suppression below five learners.
- Under-18 learners excluded from analytics and public surfaces.
- Integrity signals are private, evidence-based, and human-reviewed. No
  automated accusation.
- No real PII, credentials, customer data, live malware, or production systems.
- Every artifact has a hash, a review state, and a visibility state.
- The learner controls transcript sharing and can revoke it.
