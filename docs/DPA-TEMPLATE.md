# Data Processing Addendum (DPA) — template

> **Release 5 deliverable.** Template only. Not legal advice. Replace every
> `[BRACKETED]` field and have qualified counsel review this against the
> institution's governing statute (FIPPA/MFIPPA, Quebec Law 25, PIPEDA, FERPA, or
> a US state law) before signature. This template is drafted for a
> **self-hosted deployment** where the institution operates the software; delete
> or rewrite the hosting and sub-processor clauses if the vendor hosts it.

This Data Processing Addendum ("DPA") forms part of the agreement between:

- **Institution:** [INSTITUTION LEGAL NAME], a [province/state] institution
  ("Institution"), acting as the information manager / controller for student
  records; and
- **Service Provider:** [VENDOR LEGAL NAME] ("Service Provider"), providing the
  OpenCyberRange / SWOCTS Cyber Range software and related support.

## 1. Definitions

- **Personal Information** means information about an identifiable individual,
  including student education records, account data, assessment evidence, and
  any identifier linked to a student.
- **Student Records** means records the Institution discloses to the Service
  Provider for the purpose of operating the platform, including enrolment,
  progress, submissions, scores, and support correspondence.
- **Processing** means any operation on Personal Information, including storage,
  access, transmission, and deletion.
- **Sub-processor** means a third party engaged by the Service Provider that
  processes Student Records.
- **Security Incident** means unauthorised access to, disclosure of, loss of, or
  alteration of Student Records in the Service Provider's control.

## 2. Roles and scope

1. The Institution is the information manager/controller and determines the
   purposes of processing.
2. The Service Provider is a service provider/processor and processes Student
   Records only on the Institution's documented instructions, solely to provide,
   secure, support, and maintain the platform.
3. The Service Provider must not process Student Records for advertising,
   profiling, resale, model training, product analytics, or any other commercial
   purpose.
4. The Service Provider must not sell, rent, or disclose Student Records to any
   third party except as required by law or authorised in writing by the
   Institution.

## 3. Student intellectual property

1. Students and the Institution retain all right, title, and interest in
   submissions, answers, rubrics, course materials, and any intellectual
   property created by students or faculty.
2. The Institution grants the Service Provider a limited, non-exclusive,
   revocable licence to host, copy, transmit, and display Student Records solely
   as necessary to operate the platform for the Institution.
3. The Service Provider acquires **no commercial rights** in student work and
   must not use it to develop, train, benchmark, or improve any product or model
   for itself or a third party.
4. On termination, the licence ends and the return/destruction obligations in
   section 9 apply.

## 4. FERPA (United States)

Where FERPA applies, the Service Provider is designated a "school official" with
a legitimate educational interest, and agrees to:

1. Use education records only for the purposes authorised by the Institution.
2. Maintain the confidentiality required by FERPA.
3. Not redisclose education records except as permitted by FERPA or instructed
   by the Institution.
4. Assist the Institution with access, amendment, and destruction requests.
5. Return or destroy education records at termination.

## 5. Canadian provincial statutes (FIPPA / MFIPPA / Law 25 / PIPEDA)

1. **Purpose limitation.** Student Records are collected, used, and disclosed
   only for the educational purposes described in Schedule A.
2. **Data minimisation.** The Service Provider must not request fields the
   Institution has not approved; the default configuration collects the minimum
   needed to operate the platform.
3. **Residency.** Student Records are stored in [REGION] unless the Institution
   approves another region in writing. If the Service Provider hosts the
   platform, Schedule C lists every storage region and sub-processor.
4. **Quebec Law 25.** Before any transfer of Student Records outside Quebec, the
   Institution completes a Privacy Impact Assessment. The Service Provider must
   supply the information reasonably required for that assessment.
5. **Automated decisions.** The platform's scoring is deterministic; it does not
   use an AI model to grade. Where the Institution uses platform output in a
   decision with significant effect, the Institution provides the human-review
   route and the Law 25 notice. The Service Provider supplies the primary
   factors and audit evidence described in section 7.
6. **Breach notification.** The Service Provider notifies the Institution
   without undue delay and in any event within **72 hours** of confirming a
   Security Incident, with the information the Institution needs to meet its
   statutory notification duties.

## 6. Security program

The Service Provider maintains the controls in Schedule B, including:

1. Encryption in transit with TLS 1.2 or 1.3.
2. Encryption at rest for backups and database volumes where the Service
   Provider controls the host; where the Institution self-hosts, the Institution
   is responsible for volume encryption and the Service Provider documents the
   requirement.
3. Role-based access control with least privilege, unique accounts, and MFA for
   administrative access.
4. Logging and monitoring of administrative and authentication events, with
   retention sufficient for investigation.
5. Vulnerability management, dependency pinning, signed releases, and a software
   supply-chain inventory.
6. Secure development and change management, including review of security-
   relevant changes.
7. Business continuity and disaster recovery, including tested backups.
8. Personnel confidentiality obligations and background checks where lawful.

## 7. Audit, transparency, and assistance

1. **Audit rights.** The Institution may audit the Service Provider's compliance
   on [30] days' notice, no more than [once] per year, or more often after a
   Security Incident. The Service Provider may satisfy this with a current
   HECVAT, SOC 2 report, ISO 27001 certificate, or a completed security
   questionnaire plus a written attestation.
2. **Access and correction.** The Service Provider assists with subject-access,
   correction, and erasure requests within [10] business days or the statutory
   period, whichever is shorter.
3. **Export.** The Institution may export Student Records in a machine-readable
   format at any time and on termination.
4. **Automated scoring evidence.** On request, the Service Provider supplies the
   calculation basis for an automated result: the rule applied, the inputs, the
   timestamp, and any manual override and reason.
5. **No AI training.** The Service Provider confirms that no Student Records are
   sent to an external AI/LLM provider, and that no student work is used to
   train a model. If that changes, it requires the Institution's prior written
   consent and a zero-retention AI addendum.

## 8. Sub-processors

1. Schedule C lists every sub-processor and its location.
2. The Service Provider must give [30] days' notice before adding or replacing a
   sub-processor and must not proceed if the Institution objects on reasonable
   privacy or security grounds.
3. The Service Provider remains liable for its sub-processors' performance.
4. The default self-hosted deployment has **no analytics, error-logging, or AI
   sub-processor**. Email delivery is optional and is the only likely external
   service.

## 9. Retention, return, and destruction

1. Student Records are retained for the period in Schedule A, or as instructed
   by the Institution.
2. At termination or on written instruction, the Service Provider returns the
   Student Records in a machine-readable format and destroys its copies within
   [30] days, including backups, except where law requires retention.
3. Destruction is certified in writing. The Institution may request a
   destruction log.
4. A suppression ledger prevents a restored backup from resurrecting a deleted
   account; the Service Provider describes this mechanism in Schedule B.

## 10. Security incidents

1. Notify the Institution's [SECURITY CONTACT] without undue delay and within
   72 hours of confirmation.
2. Provide the nature of the incident, the data and individuals affected, the
   likely consequences, and the containment and remediation steps.
3. Cooperate with the Institution's investigation and regulatory notification.
4. Do not notify affected individuals or regulators on the Institution's behalf
   without written authorisation, unless legally required.

## 11. Confidentiality and personnel

1. Personnel with access to Student Records are bound by written confidentiality
   obligations.
2. Access is limited to personnel who need it to provide the service.
3. The Service Provider trains personnel on privacy and security obligations.

## 12. Liability, term, and governing law

1. This DPA survives termination for as long as Student Records remain in the
   Service Provider's possession.
2. Liability for breach of this DPA is [subject to the limitation in the main
   agreement / not limited for privacy breaches — counsel to choose].
3. This DPA is governed by the laws of [PROVINCE/STATE] and the courts of
   [VENUE].
4. If a conflict exists between this DPA and the main agreement on the handling
   of Student Records, this DPA controls.

## Schedule A — Processing details

| Item | Detail |
|---|---|
| Purpose | Deliver cybersecurity training, exercises, assessment evidence, and support |
| Data subjects | Students, instructors, teaching assistants, administrators |
| Data categories | Account identifiers, institutional ID, email, role, enrolment, lab/quiz attempts, completion records, support messages, audit events |
| Sensitive data | None requested by default. The Institution must not upload health, financial, or government-ID data. |
| Retention | Institution-defined; platform defaults documented in `docs/PRIVACY-NOTICE.md` |
| Special restrictions | No advertising, no sale, no model training, no unrelated analytics |
| Return format | JSON export (`GET /api/auth/export`; admin user transfer) |

## Schedule B — Security control summary

| Domain | Control | Evidence |
|---|---|---|
| Access | Role-based access; admin, instructor, student | `app/auth.py`, `app/models.py` |
| Admin MFA | TOTP enrollment for privileged accounts | `app/routers/auth.py`, `app/services/totp.py` |
| Passwords | Argon2id; bcrypt legacy upgraded on login | `app/auth.py` |
| Secrets | Fernet-encrypted WireGuard keys, TOTP secrets, IdP secrets, OIDC ID tokens | `app/crypto.py` |
| Transit | TLS 1.2/1.3 at nginx | `platform/frontend/nginx-ssl.conf` |
| Sessions | Short-lived JWT, revocation list, trusted devices | `app/auth.py`, `app/models.py` |
| Audit | Activity and admin audit trail; erasure anonymises it | `app/services/activity.py`, `app/services/audit.py` |
| Erasure | Suppression ledger + backup restore protection | `app/services/erasure.py`, `erasure_ledger.py` |
| Backups | Daily snapshot, 30-day default retention, restore runbook | `app/services/backups.py`, `docs/PRIVACY-AND-DATA-DELETION.md` |
| Supply chain | Pinned dependencies, signed release manifest, vulnerability scans | `docs/SUPPLY-CHAIN.md`, `versions.yaml` |
| Isolation | Per-session Docker networks; management-plane firewall rules | `app/services/docker_manager.py`, `docs/ARCHITECTURE.md` |
| Tenant isolation | **Single-tenant deployment**; shared-database multi-tenancy is not offered | `docs/PROCUREMENT-REQUIREMENTS.md` |
| AI | No AI grading; no student data sent to an LLM | `docs/AUTOMATED-SCORING.md` |

## Schedule C — Sub-processors and locations

| Sub-processor | Service | Location | Data |
|---|---|---|---|
| None (self-hosted default) | — | Institution's region | — |
| [SMTP PROVIDER, if enabled] | Transactional email | [REGION] | Email address and message content |

## Schedule D — Institution contacts

| Role | Contact |
|---|---|
| Privacy officer / DPO | [NAME, EMAIL, PHONE] |
| Security contact | [NAME, EMAIL, PHONE] |
| Contract owner | [NAME, EMAIL, PHONE] |

## Signature

| Institution | Service Provider |
|---|---|
| Name: | Name: |
| Title: | Title: |
| Signature: | Signature: |
| Date: | Date: |
