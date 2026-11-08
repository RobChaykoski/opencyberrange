# SWOCTS Cyber Range security policy

SWOCTS Cyber Range is powered by OpenCyberRange. This policy covers the branded deployment and the upstream platform code it runs.

## Supported versions

Security fixes land on the current supported release. The current platform
release is **2.2.0**, with security fixes also maintained on the **1.1.3**
Community / Academic maintenance line where the same defect applies.

| Version | Supported |
|---|---|
| `v2.2.0` / `main` | Yes |
| `v2.1.0`–`v2.1.3` | Security fixes only - upgrade to `v2.2.0` |
| `v1.1.x` | Maintenance fixes only - upgrade to `v2.2.0` for the current feature line |
| Pre-1.0 builds | No - upgrade to a supported release |

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Report privately through GitHub's [private vulnerability reporting](https://github.com/RobChaykoski/opencyberrange/security/advisories/new)
or by email to the repository owner listed on the GitHub profile.

Include:

- the affected version or commit;
- the component (platform API, frontend, installer, a lab image);
- reproduction steps or a proof of concept;
- the impact you believe it has;
- whether the issue is already public.

You can expect an acknowledgement within five business days and a status update
within ten. Please give a reasonable window for a fix before disclosing.

## Scope

In scope:

- authentication, session handling, MFA, password reset and account deletion;
- authorization between students, instructors and administrators;
- administrative data exports, user imports, and snapshot restore safeguards;
- the platform API, frontend, installer and upgrade scripts;
- container escape or cross-lab isolation failures;
- secrets committed to the repository or shipped in an image;
- the certificate verification and public competition pages.

Out of scope:

- **Intentionally vulnerable lab content.** Labs deliberately contain weak
  applications, fake credentials, command injection and similar flaws. Finding
  them is the exercise, not a vulnerability report. A lab that can reach the
  host, the platform database, or another student's lab *is* in scope.
- Denial of service against a deployment you do not own.
- Findings that require a compromised administrator account unless they cross a
  privilege boundary.
- Missing hardening headers with no demonstrated impact.

## Administrative exports and restores

- Every administrative or instructor data export requires an operator-supplied
  reason of at least five characters. The reason, exporter, record count, and
  format are written to the audit log. Self-service subject-access and
  transcript exports record a fixed purpose instead of prompting.
- The administrative **Import / Export Users** export includes password hashes so
  migrated learners keep their existing passwords. It excludes MFA secrets and
  recovery codes, trusted devices, VPN peer keys, lab sessions, and learning
  progress. Treat the JSON file as credential material: transfer it over a
  secure channel, restrict access, and delete it after a successful import.
- User imports never overwrite an existing administrator account. The signed-in
  administrator is protected by user ID, other existing administrators are
  skipped with a warning, and the erasure suppression ledger is consulted before
  any account is created.
- **Restore from another system** is restricted to administrators, accepts only
  plain `.sql` snapshots, caps uploads at 512 MB, and applies the file in a single
  transaction with `ON_ERROR_STOP=1`. A full restore replaces every account and
  record in the target installation; cross-version moves should use the portable
  user export instead.

## Lab safety

Every target in this repository is fictional and isolated. Do not test against
real hosts, real credentials, or any system you do not own. Reporters must not
include real personal data, live secrets, or malware samples in an issue; use a
synthetic reproduction.

## Dependency posture

`pip-audit` and `npm audit --omit=dev` run in CI. At `v1.1.0` both report zero
known advisories. When an advisory cannot be fixed immediately, it is recorded
with an owner and an expiry in the release notes rather than ignored silently.

## OWASP Top 10 baseline

The 2.2.0 line uses the [OWASP Top 10 security baseline](docs/V2-SECURITY-OWASP-TOP-10.md)
as a merge and release requirement. It covers the web interface, platform data,
and delivery process, and it names the tests or evidence expected for each
category. Exceptions must be recorded with an owner and expiry; an expired
exception is an open finding. The current pass is recorded in
[V2 security evidence](docs/V2-SECURITY-EVIDENCE.md).
