# Privacy

This page is a plain-language summary for the **Community / Academic** edition
of SWOCTS Cyber Range, powered by OpenCyberRange. The institution that operates
a deployment is the data controller for its learners and staff. The detailed
notice and the technical controls govern; this page only orients you.

## What the platform stores

- **Account:** username, email, display name, role, password hash (never the
  password), optional MFA secret, session and refresh-token records.
- **Learning:** course membership, lab sessions, completions, quiz attempts,
  hints, achievements, certificates, and workbook state.
- **Optional profiling:** Cyber DNA, Cyber GPS, and the professional portfolio
  are **explicit opt-in**. They default to not granted and are not processed
  until the learner consents.
- **Security and audit:** sign-in and administrative events, consent changes,
  exports, and an append-only change ledger. These records are retained or
  anonymised rather than silently deleted.
- **Surveys and feedback:** responses and cohort feedback, with suppression for
  small cohorts.

The platform does not collect keystrokes, mouse movement, or exhaustive terminal
history. It does not ship default third-party analytics or advertising trackers.

## Consent and control

- Optional profiling is off until the learner opts in.
- A learner can revoke consent; the platform blocks the feature immediately,
  purges the derived data transactionally, and records proof of destruction
  without keeping the deleted payload.
- A learner can export their personal data and request erasure subject to the
  institution's retention and legal obligations.

## Retention and erasure

Retention is set by the institution and enforced by the platform's retention
policy and scheduled jobs. Account erasure removes learner-owned rows and
anonymises audit records so the security history remains intact. Courses owned
by an instructor must be transferred first so other learners do not lose their
records.

## Sub-processors and optional services

- **Password breach check:** off by default. When enabled, only the first five
  characters of a locally computed SHA-1 digest are sent to the Have I Been Pwned
  range API; the password never leaves the server.
- **AI coaching:** uses the institution's configured provider. Optional
  profiling consent is separate and explicit.
- **SSO:** the institution's identity provider receives authentication traffic.

## Screenshots and documentation

Every screenshot in this repository and the user manual uses synthetic demo data
(`alex_chen`, `jordan_lee`, `sso-student`, `example.edu`). Do not contribute a
screenshot that contains a real learner, instructor, email, IP, token, or host.

## Detailed documents

- [Privacy notice](docs/PRIVACY-NOTICE.md)
- [Privacy and data deletion](docs/PRIVACY-AND-DATA-DELETION.md)
- [Data classification](docs/DATA-CLASSIFICATION.md)
- [Data labels](docs/DATA-LABELS.md)
- [Consent revocation and destruction](docs/CONSENT-REVOCATION.md)
- [Retention policies](docs/RETENTION-POLICIES.md)
- [Survey privacy](docs/SURVEY-PRIVACY.md)
- [Data processing agreement template](docs/DPA-TEMPLATE.md)
- [Tenant isolation status](docs/TENANT-ISOLATION-STATUS.md)

## Contact

Use the institution's privacy contact for a deployment-specific request. For a
repository or platform privacy defect, follow [SECURITY.md](SECURITY.md) rather
than opening a public issue with personal data.
