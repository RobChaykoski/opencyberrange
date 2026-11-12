# Release 5 scope: enterprise procurement and compliance

Status: **planned.** Release 4 is limited to SSO (OIDC/SAML/LDAP), the network
device topology engine, and the security, privacy, and accessibility
corrections already on the Release 4 branch. Everything below is Release 5.

Source requirements: the university procurement pack covering FERPA, COPPA,
GDPR/UK GDPR, CCPA/SOPIPA, PIPEDA/FIPPA/MFIPPA, Quebec Law 25, AODA/WCAG 2.2 AA,
the EU AI Act, GDPR Article 22, HECVAT, LTI 1.3 Advantage, and Canadian data
localization.

## 1. Identity and LMS integration

- **LTI 1.3 core launch** — OIDC third-party initiated login, signed `id_token`
  validation, issuer/client/deployment binding, replay protection.
- **LTI Advantage AGS 2.0** — line items, score passback, result retrieval, and
  an instructor-review gate before any score leaves the platform.
- **NRPS 2.0** — roster sync with the minimum claims (`sub`, role, context).
  Email and display name are opt-in per institution.
- **Deep Linking 2.0** — resource selection from the LMS.
- **Canadian Access Federation** — CAF metadata onboarding and test plan.
- **LTI admin console** — per-LMS registration, key rotation, enable/disable,
  and a delivery log.

Exit criteria: a launch and a grade passback pass against at least one real LMS
(Canvas, Brightspace, or Moodle) in a staging tenant, with PII-minimal claims.

## 2. Multi-tenancy and RBAC

- **Tenant isolation** — a tenant key on every learner-owned table, enforced in
  the session/query layer, with a migration and a cross-tenant test suite.
  Alternatively, a documented single-tenant appliance with one database per
  institution.
- **TA role** — section/course scoping, no global roster access, no account
  administration.
- **Permission matrix** — university admin, instructor, TA, student; audited on
  every privileged action.
- **Per-tenant retention and purge** — term-end purge, contract-termination
  archive export, and anonymisation, with a dry-run preview.

Exit criteria: a cross-tenant access test cannot read another tenant's rows;
TA access is denied outside the assigned section.

## 3. Accommodation engine

- Per-student time multiplier (1.5x, 2x, custom) attached to the user and
  applied consistently to labs, quizzes, and assignments.
- Pause/resume clock with a recorded reason and an audit trail.
- Per-student due-date extensions that persist across a course.
- Instructor/administrator UI, export coverage, and a WCAG 2.2 AA review.

Exit criteria: the same student receives the multiplier and extension in every
assessment type, and the values survive export/import.

## 4. Automated decision transparency

- A per-submission notice that the result was produced by deterministic logic.
- The primary factors shown to the student (flag match, rubric criterion,
  attempt, time).
- A "request human review" workflow routed to the instructor, with status and
  outcome.
- An append-only score ledger: calculation inputs, rule version, timestamp,
  reviewer, and override reason.
- A bias/validation note limited to what the product actually does: deterministic
  flag matching and equal-access testing. No writing-style model exists.

Exit criteria: a student can see why a result was produced and obtain a human
decision; the override is auditable.

## 5. Procurement artifacts

- **HECVAT Full** — complete and review the draft in `docs/HECVAT.md`.
- **VPAT 2.5 / ACR** — commission an accessibility audit against the current
  build; publish the signed report.
- **SOC 2 Type II** — engage an auditor and operate the controls over the
  observation window.
- **ISO 27001** — optional; requires an accredited body and an operating ISMS.
- **DPA** — counsel review of `docs/DPA-TEMPLATE.md`, with the institution's
  FIPPA/MFIPPA/Law 25 schedules completed.
- **Quebec PIA and TRA support pack** — data inventory, transfer map, and
  automated-decision statement for the institution's assessment.
- **Canadian hosting** — a documented deployment profile with a Canadian region,
  encrypted volumes, and a sub-processor register.

Exit criteria: no procurement claim is made that is not backed by a dated
artifact or an external report.

## 6. Security and retention operations

- Whole-institution archive export.
- Term-end and contract-end purge jobs with a dry run and a certificate of
  destruction.
- Encryption-at-rest profile for database volumes and backups (LUKS or an
  encrypted object store), documented per deployment.
- Sub-processor register and a PII-stripping rule for any optional outbound
  service (SMTP is the only default candidate).

Exit criteria: an operator can produce an export, purge a term, and show the
encryption profile without touching the database by hand.

## Not in Release 5 by default

- A general-purpose AI grader. The product does not grade free text and does not
  send learner work to an LLM. Adding one would trigger the EU AI Act high-risk
  and Article 22 work as a separate program.
- SOC 2 or ISO certification before an auditor has issued a report.

## Release boundaries

| Release | Contents |
|---|---|
| Release 4 | SSO (OIDC/SAML/LDAP), network device topology engine, API exposure fixes, SSO privacy export/erasure, institution sign-in accessibility |
| Release 5 | LTI 1.3 Advantage, multi-tenancy/TA/RBAC, accommodation engine, automated-decision transparency, HECVAT/VPAT/SOC 2/ISO/DPA/PIA artifacts |
