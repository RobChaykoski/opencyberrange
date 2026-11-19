# Reporting roadmap by tier and role

Status: **planning baseline** (19 November 2026).

The report catalogue is grouped by the decision it supports, not by the table it
reads. Each report has a named owner role, a purpose, a minimum data set, and an
access rule. The role capability model is in
[`ROLE-CAPABILITY-MODEL.md`](ROLE-CAPABILITY-MODEL.md).

## Design rules

- A report exists for a decision, not for completeness.
- Every report has a role matrix entry and an access audit event.
- Prefer aggregate, band, and hash over raw learner rows.
- Suppress small cells and combine categories that could identify a learner.
- Label exports with purpose, owner, date, and retention.
- Separate learning evidence from platform telemetry.
- No report makes a grade, admission, employment, or disciplinary decision.

## Tier 1: core teaching and audit evidence

| Report | Primary roles | Source | Status |
|---|---|---|---|
| Student Activity Audit | Auditor, teaching assistant, mentor | Activity events, lab sessions | Existing / extend evidence links |
| Grade Audit | Auditor, instructor, teaching assistant (delegated) | Grades, rubric, overrides | Existing / add override and appeal trail |
| Course Completion | Instructor, administrator, auditor | Enrollments, completions, requirements | Existing |
| Lab Completion | Instructor, teaching assistant, auditor | Lab completions, attempts, hints | Existing |
| Certificate Audit | Auditor, administrator | Open Badge credentials, issuance log | Existing / add revocation and signature evidence |

Tier 1 is the minimum credible evidence pack. It must be reproducible, signed
where exported, and available without exposing mentor notes.

## Tier 2: workforce readiness differentiators

| Report | Primary roles | Source | Status |
|---|---|---|---|
| NICE Workforce Readiness | Mentor, instructor, employer-facing reviewer | NICE mappings, completions, evidence | New foundation in 5.24.0 |
| Skills Gap Analysis | Mentor, instructor, curriculum owner | Competency scores, NICE tasks, lab coverage | Planned |
| Competency Matrix | Instructor, mentor, learner (own view) | Competency contracts and radar | Existing |
| Employer Readiness Transcript | Learner, employer with consent, auditor | Verified evidence, competency, NICE alignment | Planned |

These reports must show confidence, coverage, and the difference between
"not measured" and "weak". They are not a ranking.

## Tier 3: OpenGRC integration

| Report | Primary roles | Source | Status |
|---|---|---|---|
| Control Coverage Report | Auditor, compliance, privacy office | Control catalogue, course/assessment mapping | Planned |
| Training-to-Control Mapping | Auditor, curriculum owner | Lab and assessment to control mapping | Planned |
| Framework Coverage Report | Auditor, compliance | NIST CSF, NICE, ISO 27001, SOC 2 mapping | Planned |
| Compliance Evidence Report | Auditor, privacy office | Signed evidence pack, access, retention | Planned |

OpenGRC is the system of record for controls. OpenCyberRange should export
evidence with stable identifiers and hashes, not duplicate the GRC database.

## Tier 4: enterprise ecosystem

| Report | Primary roles | Source | Status |
|---|---|---|---|
| Asset Ownership Report | Administrator, asset owner, auditor | Ralph asset inventory | Planned |
| Endpoint Compliance Report | Administrator, endpoint owner, auditor | Fleet device posture | Planned |
| Identity Access Review Report | Privacy office, auditor, IAM analyst | OpenIAM / Authentik roles, groups, app access | Planned |
| Data Classification Report | Privacy office, data owner, auditor | OpenDLP classification results | Planned |

Tier 4 reports must never copy raw endpoint, identity, or DLP content into
OpenCyberRange. Store counts, classifications, and evidence references.

## Role-to-tier view

| Role | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---|---|---|---|
| Privacy office | Aggregate | Aggregate | Evidence and mapping | Classification and access |
| Auditor | Full evidence | Verified evidence | Full evidence | Attestation and counts |
| Mentor | Assigned learners | Assigned learners | No | No |
| Teaching assistant | Assigned course | Assigned course | No | No |
| Administrator | Platform evidence | Aggregate | Integration status | Integration status |

## Implemented foundation

Release 5.25.0 adds the report access policy layer:

- `app/services/report_access.py` is the single report-to-role map.
- Course reports now return `403` for roles outside the policy.
- Report catalog entries are filtered by role.
- Report views and exports write `REPORT_VIEWED`, `REPORT_EXPORTED`, and
  `REPORT_ACCESS_DENIED` audit events with purpose, owner, audience, and
  retention.
- Aggregate exercise rows below the configured minimum cell size are blanked and
  marked `suppressed`.
- Report manifests now carry an expiry date based on the policy retention.
- Exports carry `X-Report-Purpose`, `X-Report-Owner`, `X-Report-Audience`,
  `X-Report-Retention-Days`, and `X-Report-Expires-At`.
- CSV exports include purpose, owner, audience, and retention comment rows.
- Classification labels use the institution's configured taxonomy and optional
  framework references, not a hardcoded universal scheme.

Known limitation: mentor and teaching-assistant course assignments are not yet a
separate table. They are limited to courses they own until a course-staff
assignment model is added. That is deliberately conservative.

## Delivery order

1. **Report access policy and audit** — one policy layer for every report, with
   role checks and access events. This is a prerequisite for all later tiers.
2. **Tier 1 completion** — override/appeal trail, certificate revocation and
   signature evidence, reproducible export bundle.
3. **Tier 2 readiness** — NICE coverage, skills gap, confidence, and employer
   transcript with learner consent.
4. **Tier 3 control mapping** — start with one framework and a small control set;
   do not build a generic GRC clone.
5. **Tier 4 connectors** — one integration at a time, read-only, aggregate by
   default.

## Acceptance criteria for any new report

- Named primary role and decision.
- Documented data minimisation and retention.
- Small-cell suppression and re-identification review.
- Access audit event on view and export.
- Export label with purpose, owner, date, and retention.
- Accessible summary and a machine-readable export.
- A test that a role outside the matrix receives 403.
- A test that an aggregate report does not leak learner-level rows.
- A review date and owner.
