# SWOCTS Cyber Range privacy notice

**Effective 8 November 2026**

This notice explains how the SWOCTS Cyber Range handles personal information.
It supplements the [SWOCTS Privacy Policy](https://www.swocts.com/privacy) and
is written to align with Canada's *Personal Information Protection and
Electronic Documents Act* (PIPEDA). It is a platform-level notice, not legal
advice.

**Privacy contact:** [privacy@swocts.com](mailto:privacy@swocts.com)

## Scope

This notice applies to the SWOCTS Cyber Range training platform, including its
web interface, APIs, lab environments, VPN access, courses, exercises,
certificates, surveys, and support channels. The separate
[SWOCTS Privacy Policy](https://www.swocts.com/privacy) also covers SWOCTS
events, workshops, volunteer sign-ups, mailing lists, and the SWOCTS Hub
website.

## Accountability and contact

SWOCTS is responsible for the personal information described here. Privacy
questions, access requests, correction requests, consent withdrawals, and
complaints can be sent to the SWOCTS Privacy Officer at
[privacy@swocts.com](mailto:privacy@swocts.com). We will respond within a
reasonable time and, where required, work with the Office of the Privacy
Commissioner of Canada.

## What we collect

- **Account details:** username, email address, name, organisation, and student
  identifier where an institution provides one.
- **Authentication and security data:** password hashes, optional MFA secrets
  and recovery codes, trusted devices, session records, login timestamps, and
  IP addresses.
- **Learning activity:** course enrolment, lab starts, flag attempts,
  completions, hints, quiz attempts, achievements, certificates, and transcript
  records.
- **Optional feedback and surveys:** pulse responses, course check-ins,
  free-text comments, and research responses only where the learner has opted
  in.
- **VPN and lab access data:** WireGuard public keys, assigned client addresses,
  and session records needed to operate isolated exercises.
- **Support and operational records:** messages sent to administrators, audit
  events, backups, and diagnostic logs.

We collect only the information needed for the purposes below.

## Why we use it

- To create and secure accounts and authenticate users.
- To deliver courses, exercises, labs, workbooks, and certificates.
- To show learners their progress and give instructors authorised course
  visibility.
- To operate the VPN, lab orchestration, backups, and platform security.
- To investigate misuse, protect the service, and meet legal or institutional
  obligations.
- To run optional surveys or research only with the required consent.

We do not sell personal information. We do not use learner data for advertising,
and we do not use optional survey or research data for purposes that were not
disclosed when consent was collected.

## Consent and withdrawal

Creating an account and using the platform provides the information needed to
operate the training service. Optional features, including account email,
surveys, feedback publication, and research participation, are separate
choices. You can withdraw optional consent from **Profile → Privacy and data**
or by contacting [privacy@swocts.com](mailto:privacy@swocts.com). Withdrawal may
limit optional features but does not affect access to core learning records
where retention is required by the institution or law.

## Disclosure and transfers

We may disclose personal information to the learner's institution and its
authorised instructors, to service providers that host, secure, or support the
platform under confidentiality obligations, and to legal or regulatory
authorities where required by law. Where information is processed outside
Canada, we take reasonable steps to protect it at a comparable level.

## Retention

Account, course, and learning records are kept for the period required by the
institution's retention schedule. Operational audit and activity records are
retained for a short documented period. Backups default to 30 days. Account
deletion removes identity, credential, VPN, learning, survey, and session data,
anonymises activity events, and keeps a suppression hash so a restore cannot
resurrect the account. See
[Privacy, Erasure, and Backups](PRIVACY-AND-DATA-DELETION.md) and the
[Data dictionary](DATA-DICTIONARY.md) for the field-level schedule.

Optional survey and research data follow the consent given at collection. A
research extract requires ethics approval, a documented purpose, de-identified
data, and a destruction date. See
[Analytics governance](ANALYTICS-GOVERNANCE.md).

## Safeguards

Safeguards include role-based access control, Argon2id password hashing,
optional MFA, encrypted transport, isolated lab networks, audit logging,
restricted administrative access, and encrypted backup handling. Course and
exercise analytics are suppressed when the cohort is below the configured
minimum, defaulting to 5 learners; the interface shows "Suppressed" or "No
evidence" rather than a zero. No system is perfectly secure; report suspected
issues to [privacy@swocts.com](mailto:privacy@swocts.com).

## Your rights under PIPEDA

Subject to applicable exceptions, you may:

- request access to personal information we hold about you;
- request correction of inaccurate or incomplete information;
- withdraw optional consent;
- request export or deletion of your account data;
- challenge our compliance with PIPEDA.

Some requests require identity verification. Learners can export or delete their
account from **Profile → Privacy and data**. Others can write to
[privacy@swocts.com](mailto:privacy@swocts.com). If a concern is not resolved,
it may be raised with the Office of the Privacy Commissioner of Canada.

## Cookies and local storage

The platform uses browser storage for the signed-in session, theme, privacy-mode
preference, and similar interface state. It does not use advertising trackers.
Blocking required storage may prevent sign-in or other core features from
working.

## Institutional deployments

Where the platform is operated by a Canadian public institution, Ontario's
FIPPA or MFIPPA, institutional privacy policies, and research ethics
requirements may also apply. Operators should review this notice with their
privacy office and adjust retention, consent, and contact details to match the
deployment.

## Changes

We may update this notice as the platform or legal requirements change. The
effective date will be revised and, where appropriate, the change will be
announced in the platform or by email.
