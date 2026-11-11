# SWOCTS Cyber Range security policy

SWOCTS Cyber Range is powered by OpenCyberRange. This policy covers the branded deployment and the upstream platform code it runs.

## Supported versions

Security fixes land on the current supported release. The current platform
release is **2.6.0**, with security fixes also maintained on the **1.1.3**
Community / Academic maintenance line where the same defect applies.

| Version | Supported |
|---|---|
| `v2.6.0` / `main` | Yes |
| `v2.5.5` | Security fixes only - upgrade to `v2.6.0` |
| `v2.5.4` | Security fixes only - upgrade to `v2.6.0` |
| `v2.5.1`–`v2.5.3` | Security fixes only - upgrade to `v2.6.0` |
| `v2.4.1` | Security fixes only - upgrade to `v2.6.0` |
| `v2.1.0`–`v2.1.3` | Security fixes only - upgrade to `v2.6.0` |
| `v1.1.x` | Maintenance fixes only - upgrade to `v2.6.0` for the current feature line |
| Pre-1.0 builds | No - upgrade to a supported release |

## Password storage

- New and changed passwords are hashed with **Argon2id** (`pwdlib`).
- Legacy **bcrypt** hashes verify and are upgraded to Argon2id on a successful
  sign-in.
- The database stores a one-way hash only. There is no plaintext password, no
  reversible password encryption, and no password recovery.
- A password reset writes a new hash; it does not reveal the old password.
- The database integrity audit flags any `users.hashed_password` value that is
  missing or is not an Argon2id/bcrypt hash.
- The administrative user export carries one-way hashes for controlled
  migration. Treat the file as credential material. It contains no plaintext
  password, MFA secret, recovery code, trusted device, or VPN key.

## Database integrity and change attribution

- `scripts/database_integrity.py` computes a SHA-256 checksum for each critical
  table and a database fingerprint. A signed manifest is the release evidence
  for a point-in-time snapshot.
- An append-only PostgreSQL ledger records each `INSERT`, `UPDATE`, and `DELETE`
  on a critical table with a row hash, actor type, actor id, request id, and a
  chained entry hash.
- Actor types are `user` (authenticated application request), `system`
  (application job with no user), and `unattributed` (manual SQL or an
  uninstrumented path). Manual writes are reported for review.
- The ledger has an immutable trigger and `UPDATE`/`DELETE` are revoked. A
  broken chain, a changed entry hash, or a row changed without a ledger entry is
  a finding.
- The quality audit covers foreign-key orphans, duplicate keys, invalid enums,
  null critical fields, invalid JSON, bad quiz/feedback ranges, missing settings,
  and password hash format.

Commands and the full runbook are in
[Database integrity and change attribution](docs/DATABASE-INTEGRITY.md).

## Deleted and removed users

- Enrollments, completions, sessions, quiz attempts, quiz feedback, course
  feedback, survey responses, achievements, and celebrations cascade.
- Optional actor/creator references (`activity_events.actor_id`,
  `course_feedback.subject_user_id`, `labs.created_by`, `surveys.created_by`,
  `competitions.created_by`) are set to `NULL`.
- `courses.instructor_id` is not nullable. Account erasure is blocked until the
  instructor transfers owned courses, so students never lose a course record.
- Dashboards and lists render `Deleted user`, `Deleted learner`, or
  `Deleted participant` instead of a blank or a crash.
- Instructor coaching notes with a `NULL` subject are excluded from course-health
  counts.
- The quality audit reports orphaned coaching notes and `NULL` creators for
  review.

## Supply chain

- `supply-chain.lock.json` records SHA-256 hashes for dependency, build,
  deployment, workflow, and lab inputs.
- CI verifies the lock on every quality run. Install, update, and prebuild stop
  on drift. `--check-pins` reports base images without a digest.
- A release lock can be signed with GPG or minisign and verified with
  `scripts/supply_chain.py --check --signature`.
- The lock is a drift detector, not a substitute for `pip-audit`, `npm audit`,
  CodeQL, Trivy, SBOM review, or a signed release tag.

## Recognition and celebration data

- The Celebration Wall is voluntary and anonymous. The wall returns only the
  celebration count, never the celebrator's identity.
- One person can celebrate a win once. Self-celebration is rejected.
- A hidden or unlisted achievement cannot be celebrated.
- Celebrations are not joined to analytics, completion, Cyber DNA, certificates,
  course health, grading, or any learning metric.
- Administrator accounts are excluded from the public wall.

## Event certificates

- Event certificates are issued only to approved accounts that explicitly
  joined the event, and only after the event's `end_at`.
- Participation is available to every eligible participant. First, second,
  third, First Blood, Clean Sweep, and Perfect Event certificates require the
  matching `comp_<competition_id>_<code>` achievement, so a learner cannot claim
  an award they did not earn.
- Certificate IDs are deterministic: `OCR-EVT-<event>-<user>-<award>-<digest>`,
  where the digest is the first ten hex characters of a SHA-256 hash over the
  event, user, and award. Public verification recomputes the digest and rejects
  tampered IDs.
- Public verification returns the event, award, recipient display name, event
  dates, issue date, and certificate ID. It never returns scores, usernames,
  email addresses, student IDs, or account identifiers.
- The certificate holder can disable public verification. When disabled, the
  public verifier returns the generic invalid result and the certificate payload
  omits the verification URL and QR code.
- Event and sponsor logos are accepted only as validated data URLs. The PDF
  renderer decodes them locally, converts WebP and transparency to PNG, and
  never fetches a remote URL. PDF responses use `Cache-Control: no-store`.
- Event certificates are credentials, not learning metrics. They do not affect
  Cyber DNA, course grades, completion, or analytics.

## Authorized testing

Use a dedicated test student and test instructor account for deployment
verification. Do not test with a real learner account or a shared administrator
account. The repository's `scripts/ui-workspace-regression.mjs` expects
`UI_STUDENT_USERNAME` / `UI_STUDENT_PASSWORD` and, optionally,
`UI_INSTRUCTOR_USERNAME` / `UI_INSTRUCTOR_PASSWORD`; it launches one isolated
lab per role, submits only an invalid flag, and stops the lab when it finishes.
Remove temporary accounts and their sessions after the run.

Testing must stay inside the lab network. Do not send enumeration, injection, or
credential traffic to a real host, a public domain, or another learner's
session.

## Security review evidence - 11 November 2026

| Check | Result |
|---|---|
| Deployment baseline | Prod `172.16.16.41` and dev `172.16.16.44` on `eac74283`; frontend assets contain the combined exercise workspace |
| Browser walkthrough | Dedicated test student and instructor accounts launched `RangeBox First Steps`; RangeBox, details, flag, and framed workbook rendered; Expand/Restore, invalid-flag handling, hint request, and Stop were exercised |
| Workspace fix | **Open in new tab** now opens `/rangebox?...` in a new tab instead of navigating the exercise tab |
| Stop/relaunch race | Cleanup for an old session defers to a newer starting/running session for the same lab, so a rapid relaunch keeps its network and RangeBox instead of silently launching VPN-only |
| Workbook CSP | Wiki locations allow the Material for MkDocs Google Fonts stylesheet and font files; the SPA policy remains strict |
| Lab validation | **162 labs, 0 errors, 0 warnings** |
| Automated regression | `scripts/ui-workspace-regression.mjs` records pass/fail checks and screenshots in `ui-workspace-artifacts/` |

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

- authentication, session handling, MFA, password storage and reset, and account deletion;
- authorization between students, instructors and administrators;
- database integrity, the append-only change ledger, and data-quality checks;
- deleted-user handling and dashboard resilience;
- administrative data exports, user imports, and snapshot restore safeguards;
- the supply-chain lock, release builds, and deployment verification;
- the platform API, frontend, installer and upgrade scripts;
- the exercise workspace: workbook iframe authorization, RangeBox session
  query handling, student/instructor role separation, and lab stop/relaunch
  controls;
- container escape or cross-lab isolation failures;
- secrets committed to the repository or shipped in an image;
- event certificate issuance, event and sponsor logo handling, public
  certificate verification, public competition pages, and the Celebration Wall.

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

`pip-audit` and `npm audit --omit=dev` run in CI. At `v2.6.0` the dependency
audit remains a release gate; a finding that cannot be fixed immediately is
recorded with an owner and an expiry in the release notes rather than ignored
silently. The supply-chain lock adds a drift check for the same inputs.

## OWASP Top 10 baseline

The 2.6.0 line uses the [OWASP Top 10 security baseline](docs/V2-SECURITY-OWASP-TOP-10.md)
as a merge and release requirement. It covers the web interface, platform data,
and delivery process, and it names the tests or evidence expected for each
category. Exceptions must be recorded with an owner and expiry; an expired
exception is an open finding. The current pass is recorded in
[V2 security evidence](docs/V2-SECURITY-EVIDENCE.md).

The architecture review in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) scores
each trust boundary with STRIDE and DREAD, including the new database-integrity
and supply-chain controls. The highest residual risks remain host/Docker
compromise, firewall-dependent lab isolation, trusted instructor wiki content,
client-side secrets, and upstream supply-chain compromise.

## Security review evidence — 10 November 2026

| Check | Result |
|---|---|
| CI, CodeQL, Quality, and Trivy on `aadf25b1` | **All green** |
| Lab validation | **162 labs, 0 errors, 0 warnings** |
| Quiz banks | **24 valid** (13 certification, 11 general) |
| Supply-chain lock | **42 files and 162 lab hashes** match release `2.6.0` |
| Event certificate tests | Participation, placement, and trophy listings; JSON and PDF; public verification; tampered IDs; opt-out; `409` before the event ends; `403` for a non-participant |
| Event route smoke | Unauthenticated certificate list returns `401`; unknown `OCR-EVT-` ID returns the generic invalid result |
| Deployment smoke | Dev `172.16.16.44` and prod `172.16.16.41` / `https://ocr.swocts.com` on `2.6.0`; healthy; 162 labs discovered; no backend errors |
| VPN route verifier | All active labs passed after the `/32` and own-`/24` route change |
| Release tag | `v2.6.0` is an annotated, unsigned tag; the supply-chain lock is signed by the release key |

The release tag signature is the only release-engineering exception. The tag
was created without the private release key, which is held outside the
repository. Sign the tag on the release workstation if a signed tag is
required; the lock signature remains valid independently.

## Security review evidence — 8 November 2026

| Check | Result |
|---|---|
| Development database quality (2.5.1) | **0 critical, 0 warning, 2 info** |
| Production database quality (2.5.1) | **0 critical, 0 warning, 3 info** |
| Development database fingerprint | `ea4f9acb1cd8fa17f28c66841dba7620abcac76f099862c810bbf60cdc3c4c9c` |
| Change ledger | Chain OK; an authenticated celebration entry and a deliberate manual `labs.UPDATE` were recorded; the manual write was flagged `unattributed` |
| Password hash audit | Every stored hash is Argon2id or legacy bcrypt; no missing, plaintext, or unknown format |
| Deleted-user paths | Cascade/SET NULL reviewed; null-safe UI fallbacks added; orphaned coaching notes excluded |
| UI validation | Six-trait Cyber DNA, Celebration Wall toggle, dark/light themes, 390 px and 1440 px; no page errors or overflow |
| Supply chain | Lock verified in CI; deploy/prebuild gates wired; unpinned base images reported separately |

Known gaps:

- **Session coverage:** 36 development and 116 production completions have no
  matching non-diagnostic session. Completion, hint, attempt, and time metrics
  are reliable; `started_rate` is not. Historical rows need a reviewed backfill.
- **Hint placeholders:** 2 production rows are intentional empty-flag
  placeholders created when a hint was requested. They are not solved exercises.
- **Seeded labs:** all 149 seeded labs have `created_by = NULL`; this is expected
  imported content, not a deleted account.
- **Ledger limits:** a PostgreSQL superuser can disable triggers. The ledger is
  tamper-evident, not tamper-proof. Keep signed manifests and backups off the
  database host. `application_name` is a fallback label, not a security
  boundary; review unattributed writes.
- **Production ledger:** the ledger is installed on production. The 2.5.1 check
  reported 0 entries and a valid chain; entries appear as critical-table writes
  occur.
