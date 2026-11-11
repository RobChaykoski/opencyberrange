# SWOCTS Cyber Range privacy notice

**Effective 11 November 2026**

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
- **RangeBox session metadata:** the desktop image name, container identifier,
  local VNC port, session start and stop times, and heartbeat needed to keep the
  desktop alive and clean it up. The platform does not record the desktop screen
  or the learner's terminal session by default.
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

## Our privacy practices

We apply these practices across the platform:

- **Privacy by design and by default.** Optional feedback, surveys, and research
  are off until the learner opts in. Course and exercise analytics are
  suppressed below the configured minimum cohort (default 5 learners), and the
  interface shows "Suppressed" or "No evidence" instead of a misleading zero.
  Public rankings are not used, and celebrations are voluntary and anonymous.
- **Data minimisation and purpose limitation.** We collect the account,
  learning, security, VPN, and support data needed to run the training service.
  We do not collect keystrokes, screen recordings, or browsing history outside
  the platform. We do not sell personal information or use it for advertising,
  and optional data is used only for the purpose disclosed at collection.
- **Least-privilege access.** Learners see their own records. Instructors see
  the courses they own or are authorised to support. Administrative access is
  restricted and audited, and exports require a recorded reason.
- **Separate identity from analytics.** Class-level analytics and reports use
  counts, medians, and minimum-cohort suppression. Individual records are
  available only to the learner and authorised instructors, and reports are
  designed for a stated teaching decision rather than ranking.
- **Retention and deletion.** Account deletion removes identity, credential,
  VPN, learning, survey, and session data, anonymises activity events, and keeps
  a keyed suppression hash so a restore cannot resurrect the account. Backups
  default to 30 days, and audit and activity records are kept for a short
  documented period. Instructor deletion is blocked until owned courses are
  transferred.
- **Security safeguards.** We use Argon2id password hashing, optional MFA,
  session revocation, role-based authorization, encrypted transport, encrypted
  WireGuard key storage, isolated per-lab networks, audit logging, restricted
  administrative access, and access-controlled backup handling. No system is
  perfectly secure.
- **Operational logging.** We record sign-in, security, export, and
  administrative events, including IP addresses and account identifiers where
  needed for security and audit. We do not use advertising trackers or
  third-party behavioural analytics. Logs are restricted and retained for a
  documented period.
- **Vendors and transfers.** Hosting, network, and support providers process
  personal information only under confidentiality and security obligations.
  Where information is processed outside Canada, we take reasonable steps to
  provide comparable protection. Operators should document their hosting
  location and subprocessors.
- **Requests and complaints.** Learners can export or delete their account from
  **Profile → Privacy and data**. Access, correction, consent withdrawal, and
  other requests go to [privacy@swocts.com](mailto:privacy@swocts.com). We
  verify identity, respond within a reasonable time, and escalate unresolved
  concerns to the Office of the Privacy Commissioner of Canada where required.
- **Accountability and assessment.** The SWOCTS Privacy Officer is accountable
  for these practices. Staff with access receive privacy and security guidance.
  Institutional operators should complete a privacy impact assessment,
  document the lawful basis, and review retention, consent, and minors'
  requirements before deployment.

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

## RangeBox and the exercise workspace

The combined exercise workspace shows the learner's RangeBox desktop, the
exercise brief and targets, the flag form, and the workbook in one page. It does
not add third-party analytics, advertising, or behavioural tracking.

- The RangeBox desktop runs in an isolated container attached to the learner's
  own lab network. Session metadata is used for operation, capacity, and
  cleanup.
- Instructors and administrators can see session status and progress. A
  privileged support view of a learner's desktop or account is role-gated and
  recorded in the audit log; it is not part of normal course monitoring.
- Screenshots, notes, or exported evidence that a learner creates are under the
  learner's control. They may contain lab tokens, cookies, or synthetic personal
  data and should be redacted before sharing.
- The workbook is served from the same platform origin and is available only to
  an authenticated account with access to the exercise.
- Automated deployment tests use dedicated synthetic student and instructor
  accounts; their screenshots and records are not learner records and are
  removed after the check.

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

## Learners under 18

Where the platform is used in a high-school or youth programme, the institution
or programme operator is responsible for obtaining any required parent or
guardian consent and for limiting collection to what the programme needs.
Learners under 18 should not be included in optional research, public
showcases, or external reporting without the required consent.

A learner can mark their account as under 18 on the registration form or later
in **Profile → Security & privacy**. When this setting is on, the platform
excludes that learner's individual activity from instructor reports, course
analytics, coaching queues, public leaderboards, and competition scoreboards.
The learner's own dashboard and progress remain available to them. The setting
is a privacy declaration by the account holder; it does not verify age. The
institution remains responsible for any consent or age-verification requirement
that applies to its programme.

## Suspected privacy incidents

Report suspected privacy or security incidents to
[privacy@swocts.com](mailto:privacy@swocts.com). We will contain and assess the
incident, preserve the relevant evidence, notify the institution and affected
individuals, and notify regulators where required by law.

## Changes

We may update this notice as the platform or legal requirements change. The
effective date will be revised and, where appropriate, the change will be
announced in the platform or by email.
