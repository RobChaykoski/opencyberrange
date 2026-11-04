# Security policy

## Supported versions

Security fixes land on the current supported release line. At the time of
writing that is `v1.1.x` (tag `v1.1.0` and later on the 1.1 maintenance line).
The `main` branch carries the 2.0 development line, and fixes land on 1.1 first
and are merged forward.

| Version | Supported |
|---|---|
| `v1.1.x` | Yes |
| `v1.0.x` | Security fixes only — upgrade to `v1.1.x` |
| `v2.0.x` / `main` | Yes for development builds; next feature release |
| Pre-1.0 builds | No — upgrade to `v1.1.x` |

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

The 2.x line uses the [OWASP Top 10 security baseline](docs/V2-SECURITY-OWASP-TOP-10.md)
as a merge and release requirement. It covers the web interface, platform data,
and delivery process, and it names the tests or evidence expected for each
category. Exceptions must be recorded with an owner and expiry; an expired
exception is an open finding. The current pass is recorded in
[V2 security evidence](docs/V2-SECURITY-EVIDENCE.md).
