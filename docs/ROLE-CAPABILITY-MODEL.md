# Role capability and reporting model

Status: **design baseline** (19 November 2026).

This page defines the skills each role needs to use OpenCyberRange well, and the
reports each role should hold. It is deliberately about capability and
authorisation, not only about dashboards. A report that a role cannot interpret,
or should not see, is a design failure.

## The design skill

The design skill is the ability to turn a learning or operational need into a
safe, understandable, evidence-backed interface. It is the core skill behind
every report in this platform.

It has seven parts:

| Part | What it means in practice |
|---|---|
| Learning design | Start from the learning outcome and the evidence that proves it. Do not start from the data that happens to exist. |
| Information design | Summary first, detail on request, plain language, consistent labels, and no false precision. |
| Privacy by design | Collect the minimum, use it for the stated purpose, aggregate early, and make deletion and correction possible. |
| Security by design | Least privilege, defence in depth, auditable access, and no sensitive data in URLs, logs, or exports. |
| Evidence design | Every claim links to a source, a time window, a method, and a confidence level. |
| Systems thinking | Understand how a change in one report changes incentives, workload, and learner behaviour elsewhere. |
| Ethics and accessibility | Design for the least powerful user, the smallest screen, the slowest connection, and the learner under stress. |

A report is not finished when it renders. It is finished when the intended role
can make a better decision with it, and no one else can make a harmful one.

## Cross-cutting skills

Every role that touches learner data needs these:

- **Privacy literacy**: purpose limitation, data minimisation, retention,
  de-identification, re-identification risk, subject access, correction, and
  erasure.
- **Security literacy**: threat modelling, least privilege, credential hygiene,
  safe export, phishing and impersonation awareness, and incident reporting.
- **Data literacy**: denominators, sample size, missing data, confidence,
  correlation versus causation, and small-cell suppression.
- **Learning literacy**: constructive alignment, formative feedback, cognitive
  load, accessibility, and the difference between evidence and inference.
- **Communication**: writing for the audience, uncertainty, disagreement, and
  escalation without blame.
- **Ethics and safeguarding**: bias, power imbalance, minor protection,
  trauma-informed language, and the limits of automated judgement.
- **AI literacy**: what a model can and cannot infer, hallucination risk,
  prompt injection, and human review of AI-assisted output.

## Role profiles

### Privacy office

**Purpose:** protect learners and the institution, not to block teaching.

**Must-have skills**

- Data mapping and records of processing.
- DPIA and privacy-by-design review.
- Consent, retention, erasure, and subject-access handling.
- De-identification and re-identification risk assessment.
- Vendor and processor oversight.
- Breach assessment and notification.
- Clear writing for learners, instructors, and regulators.

**Reports they should hold**

- Data inventory and classification by course and system.
- Consent coverage and revocation status, aggregate by cohort.
- Retention and erasure evidence, including failed or blocked erasures.
- Access-to-PII report: who can see learner-level data, and why.
- Minor-safeguard report: under-18 exclusions and age-gate coverage.
- Third-party processor and cross-border transfer inventory.
- Privacy incident and subject-request trends.

**What they should not need**

- Raw grades, flag values, or free-text mentor notes. Use aggregate counts,
  sampled evidence under a documented process, or a lawful, purpose-bound
  request.

### Auditor

**Purpose:** prove that the platform did what it claims, reproducibly.

**Must-have skills**

- Evidence integrity, chain of custody, and sampling.
- Control frameworks and mapping.
- Segregation of duties and access review.
- Change management and release evidence.
- Log analysis and reproducibility.
- Independence, scepticism, and clear findings.

**Reports they should hold**

- Grade, completion, and certificate audit trails.
- Access-review and privileged-role reports.
- Change ledger, migration history, and signed-release evidence.
- Control coverage and training-to-control mapping.
- Backup, restore, and retention evidence.
- Exception and override logs, including who approved them.

**What they should not need**

- Learner free-text or unnecessary personal data. Audit against identifiers and
  evidence hashes wherever possible.

### Mentor

**Purpose:** help a learner recover, progress, and stay connected.

**Must-have skills**

- Coaching and formative feedback.
- Reading evidence without over-claiming.
- Motivational interviewing and referral.
- Safeguarding and escalation.
- Bias awareness and cultural humility.
- Privacy boundaries in a helping relationship.

**Reports they should hold**

- Assigned learners only: progress, readiness, support queue, context flags,
  actions, outcomes, and follow-ups.
- Aggregate cohort trends, with small-cell suppression.
- Their own caseload and overdue follow-ups.

**What they should not need**

- Other mentors' caseloads, disciplinary records, or unrelated course data.
- Automated "risk" labels without the evidence and the learner's context.

### Teaching assistant

**Purpose:** keep the lab and feedback loop working without making final
judgements beyond their delegation.

**Must-have skills**

- Assessment literacy and rubric application.
- Lab troubleshooting and environment triage.
- Triage of stuck learners and hint/attempt patterns.
- Accessible feedback and academic-integrity awareness.
- Clear escalation to the instructor.

**Reports they should hold**

- Lab health, failed sessions, and common technical failures.
- Learners stuck at the same step, with evidence.
- Hint and attempt patterns, not inferred character judgements.
- Grading or feedback queue for work explicitly delegated to them.
- Course progress and completion exceptions.

**What they should not need**

- Final grade authority unless delegated in writing.
- Readiness bands or support notes outside their assigned course.

### Administrator

**Purpose:** keep the platform secure, available, recoverable, and auditable.

**Must-have skills**

- Identity, role, and permission administration.
- Backup, restore, and disaster recovery.
- Incident response and change management.
- Database safety and least-privilege operations.
- Release and supply-chain verification.
- Clear communication during an incident.

**Reports they should hold**

- Platform health, release status, and failed jobs.
- Backup and restore evidence.
- Security events, access changes, and tenant-isolation status.
- User and role inventory, with least-privilege exceptions.
- Data-integrity and retention-job status.

**What they should not need**

- Learner grades, mentor notes, or free-text evidence unless a specific,
  logged incident requires it.

## Report access matrix

| Report family | Privacy office | Auditor | Mentor | Teaching assistant | Administrator |
|---|---|---|---|---|---|
| Student activity | Aggregate | Sampled / hash | Assigned learners | Assigned course | Aggregate |
| Grades | No | Yes, evidence-bound | Assigned learners | Delegated queue | No |
| Completion and certificates | Aggregate | Yes | Assigned learners | Assigned course | Aggregate |
| Readiness and support record | Aggregate / safeguards | Sampled | Assigned learners | No | No |
| Lab health | Aggregate | Yes | Assigned course | Assigned course | Yes |
| Consent, retention, erasure | Yes | Yes | No | No | Operational status |
| Access and privileged roles | Yes | Yes | Own access | Own access | Yes |
| Security events | Aggregate / incident | Yes | No | No | Yes |
| NICE and competency coverage | Aggregate | Yes | Assigned course | Assigned course | Catalogue |

## Privacy rules that apply to every report

1. **Purpose before data.** State the decision the report supports.
2. **Minimum necessary.** Prefer counts, bands, and hashes over raw records.
3. **Small-cell suppression.** Do not publish a cell that could identify a
   learner; use a threshold (for example, fewer than five) and combine.
4. **Separate learning evidence from operational telemetry.** A failed lab is
   not a failed learner.
5. **No automated high-stakes decisions.** Readiness is a support prompt. Grades,
   admissions, employment, and discipline stay human.
6. **Auditable access.** Log who viewed or exported a report, when, and why.
7. **Export labels.** Every export carries its purpose, owner, date, and
   retention.
8. **Correction path.** A learner can see and challenge wrong data.
9. **Retention by default.** Reports expire; evidence is retained only as long
   as the policy says.
10. **Accessible by design.** Keyboard, screen reader, colour-independent, and
    plain-language summaries.

## Curriculum implications

These skills should be explicit learning outcomes, not hidden assumptions:

- **IAM track**: access review, least privilege, separation of duties, evidence
  for an auditor, privacy of identity attributes.
- **Vulnerability Management track**: risk communication, asset ownership,
  exception ethics, and patch evidence that an auditor can reproduce.
- **SOC track**: evidence handling, minimisation, escalation, and the difference
  between a detection and a disciplinary finding.
- **Platform Engineering track**: secure defaults, secret handling, audit logs,
  and privacy-preserving telemetry.
- **Every track**: a short evidence-and-communication outcome, because a
  technically correct result that cannot be explained is not workforce-ready.

## Build next

1. Add a `report_access` policy per report and role, with tests.
2. Add small-cell suppression and export labels to the report service.
3. Add a privacy-office dashboard: data inventory, consent, retention, erasure,
   minor safeguards, and processor inventory.
4. Add an auditor evidence pack: signed manifest, access review, change ledger,
   and control coverage.
5. Add mentor and teaching-assistant scoped views that cannot widen beyond the
   assigned course.
6. Add report-access audit events and a retention job for report exports.
