# SWOCTS Cyber Range security policy

SWOCTS Cyber Range is powered by OpenCyberRange. This policy covers the branded deployment and the upstream platform code it runs.

## Supported versions

Security fixes land on the current supported release. The current platform
release is **5.27.1** (`v5.27.1`, signed annotated tag), with security fixes also
maintained on the **1.1.3** Community / Academic maintenance line where the
same defect applies.

| Version | Supported |
|---|---|
| `v5.19.x` | Yes — current Community / Academic release |
| `v5` / `main` | Yes |
| `v4` | Security fixes only - upgrade to `v5` |
| `v2.7.0` | Security fixes only - upgrade to `v5` |
| `v2.6.0` | Security fixes only - upgrade to `v4` |
| `v2.5.5` | Security fixes only - upgrade to `v4` |
| `v2.5.4` | Security fixes only - upgrade to `v4` |
| `v2.5.1` - `v2.5.3` | Security fixes only - upgrade to `v4` |
| `v2.4.1` | Security fixes only - upgrade to `v4` |
| `v2.1.0` - `v2.1.3` | Security fixes only - upgrade to `v4` |
| `v1.1.x` | Maintenance fixes only - upgrade to `v4` for the current feature line |
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

## Password breach checks

- The admin setting **Settings -> Security -> Password Breach Check** is off by
  default so offline and institutional installs do not make an unannounced
  third-party request.
- When enabled, new passwords are checked against the Have I Been Pwned Pwned
  Passwords range API. Only the first five hexadecimal characters of a locally
  computed SHA-1 digest are sent; the full password and the full digest never
  leave the server. Requests use `Add-Padding`, and the response is matched
  locally by suffix.
- The check covers registration, password change, admin user creation, admin
  password reset, and first-run setup. A listed password is rejected with a
  generic `400` message that does not reveal the breach count.
- The check fails open on timeout, connection failure, or an unexpected HTTP
  response. A network problem must not block account creation or recovery.
- SHA-1 is used only as the range-query index. Stored passwords remain Argon2id;
  no plaintext, full hash, or breach response is logged or persisted.
- See `app/services/password_breach.py` and `tests/test_password_breach.py`.

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

## Sessions, refresh tokens, MFA, and reauthentication

- Every login creates a server-side session bound to the tenant captured at
  login. Access JWTs carry the session id; changing the account's tenant
  invalidates existing sessions.
- Refresh tokens are opaque, hashed, single-use, and rotate within a family.
  Replaying a rotated token revokes the entire family and session and writes a
  `critical` event.
- Recovery codes are hashed, single-use, TTL-limited, replaced as a set, and
  cleared on MFA disable/reset.
- MFA failures have their own counter and lock (`mfa_max_failed_attempts`,
  `mfa_lockout_minutes`), separate from password lockout.
- Lost-authenticator recovery uses `POST /api/admin/users/{id}/mfa/reset`, which
  requires the `mfa.reset` permission, the operator's password + MFA, a written
  reason, tenant visibility, and full session/token revocation for the target.
- Privacy, role, MFA, break-glass, service-identity, and export operations
  require a recent password + MFA reauthentication
  (`reauth_window_minutes`, default 15). The API returns
  `X-Reauth-Required: true`; the SPA opens a reauthentication dialog.
- New passwords use Argon2id with explicit 64 MiB / 3 iterations / 4 lanes /
  32-byte hash / 16-byte salt parameters. Successful login upgrades legacy
  hashes, checks for parameter drift, and rehashes hashes older than
  `password_rehash_days` (default 365).
- Full details are in `docs/AUTH-LIFECYCLE.md`.

## Authorization, tenants, and break-glass

- Roles are resolved from the database on every request. A role claim in a JWT,
  request body, query parameter, or custom header is never trusted.
- `docs/AUTHORIZATION-SERVICE.md` documents the single decision point:
  RBAC + tenant boundary + resource owner/share + learner consent + optional
  break-glass.
- `app/security/permissions.yaml` is the reviewed permission catalog. Private
  DNA/GPS/AI permissions are granted to **no** role, including `admin`.
  `python -m app.scripts.review_permissions --check` is the release gate.
- Non-system roles are confined to their `institution_id`. `institution_admin`
  is not a system administrator.
- **25 learner-owned tables** carry a server-derived `institution_id` and forced
  PostgreSQL RLS, covering courses, enrollments, sessions, completions,
  achievements, snapshots, DNA, portfolio shares, flag attempts, reviews,
  surveys, accommodations, exercise interactions, feedback, quiz attempts,
  badges, LTI scores, and activity events. See
  [Tenant isolation status](docs/TENANT-ISOLATION-STATUS.md). The runtime role
  must not be a superuser.
- Service identities use hashed, scoped, expiring tokens with no password
  login. They cannot receive private learner permissions.
- [Tenant isolation status](docs/TENANT-ISOLATION-STATUS.md) lists the enforced
  tables and classifies the remaining authentication, consent, course-content,
  and platform-operation tables.
- Break-glass access is off by default, MFA-gated, reasoned, time-bound,
  optionally second-approved, scoped to one permission and learner/course, and
  every use is a `critical` security event. It never overrides a revoked
  consent.
- The startup route audit reports protected endpoints without an
  authentication/permission dependency. Production and enterprise deployments
  set `OCR_AUTHZ_STRICT=1`, which refuses startup when a protected route lacks
  an authorization dependency.

## Security event store

- Security, audit, and privacy events are written to an append-only
  `security_events` table. PostgreSQL RLS is enabled and forced; `UPDATE` and
  `DELETE` affect zero rows and there is no delete API.
- Reads are tenant-scoped by the `ocr.institution_id` GUC; a system
  administrator sets `ocr.system_admin`.
- The runtime database role must not be a superuser. Superusers bypass RLS;
  startup logs a warning when this is detected.
- Coverage includes sign-in success/failure, MFA failure, password change,
  registration, consent grant/revoke, export allow/deny, admin actions, RBAC
  changes, break-glass request/approval/use/revoke, and portfolio share
  create/use/revoke. Sensitive HTTP requests without a richer event are caught
  by a fallback middleware.
- A five-minute security-operations loop expires stale break-glass grants and
  writes deduplicated threshold alerts for repeated authentication failures,
  denied requests, export denials, and break-glass use.
- The admin **Security** console exposes events, break-glass, service
  identities, and the role catalog.
- See `docs/SECURITY-EVENTS.md` and `docs/RETENTION-POLICIES.md`.

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

## Consent enforcement and revocation

- Every request to a derived-data API passes through
  `app/consent/middleware.py` before its service is called. The path matrix maps
  Cyber DNA, Cyber GPS, portfolio snapshots/sharing, AI coaching, and research
  APIs to their consent domain. Routers retain their own checks as defense in
  depth, but no service is expected to implement its own consent decision.
- A missing or invalid token passes through to the normal authentication
  dependency. A valid token with revoked consent receives `403` with
  `X-Consent-Status` and a stable `ConsentRequired` payload. An unexpected
  enforcement failure returns `503` (fail closed).
- Revocation writes a suppression proof to `CONSENT_SUPPRESSION_PATH` before any
  database change, then locks the feature and queues purge work. All targets for
  one revocation run in one database transaction; a mid-purge failure rolls back
  every table. Verification runs immediately, at 24 hours, and at 7 days.
- `enforce_suppressions()` scans derived rows and flips a restored `granted`
  state back to revoked, then purges and verifies the data. The ledger contains
  an HMAC subject hash and consent type, never a username, email, or deleted
  payload.
- The proof-only audit records the consent type/version, completed targets,
  verification slots, and timestamps. It never stores the deleted data.
- See [Consent revocation and data destruction](docs/CONSENT-REVOCATION.md).

## Authorization policy

- `app/security/` provides an atomic permission catalog, seeded role grants, and
  deny-by-default policy checks for self-owned, course-scoped, explicitly shared,
  and read-only resources.
- Auditors are read-only. Privacy officers may execute revocation work. An
  administrator does not receive private AI/DNA/GPS data by default; the owner or
  an explicit share is required.
- Existing routers keep their current role dependencies. New privacy surfaces use
  `require_permission()`, and the consent admin endpoints already use
  `privacy.audit.view` / `privacy.revocation.execute`.
- See [RBAC and policy-based authorization](docs/RBAC-PBAC.md).

## Exercise ZIP import

- Imports use the same validator as instructor uploads: size and zip-bomb
  limits, path-traversal rejection, required `lab.yaml` and
  `docker-compose.yml`, at least one service, and compose build-context checks.
- An imported exercise is always `visibility="draft"` and owned by the importer.
  It is never published automatically.
- Exports replace the flag with `OCR{REPLACE_ME}` by default. A trusted admin can
  request the original flag for backup; that archive is credential material.
  Instructor exports never include the flag. Imports generate a new flag unless
  one is supplied and return it once.
- See [Exercise export and import](docs/EXERCISE-EXPORT-IMPORT.md).

## Docker control-plane permissions

- The backend talks to Docker through `tecnativa/docker-socket-proxy`, not the
  host socket. `CONTAINERS`, `IMAGES`, `NETWORKS`, `VOLUMES`, `INFO`, `POST`,
  `EXEC`, and read-only `SYSTEM` accounting are enabled; `BUILD` remains off so
  a compromised backend cannot submit build recipes.
- `SYSTEM` is used only for `/system/df` so **Admin → Disk Management** can show
  image, container, volume, and build-cache sizes. It does not enable mutation.
- The proxy is attached only to the internal `docker_control` network. Lab
  containers and the frontend are not on it.

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

> **Historical evidence.** The dated sections below record the deployment and
> test state at the time. Hostnames (`ocr.swocts.com`), versions, and lab counts
> in them are not current. See the
> [production deployment statement](docs/PRODUCTION-DEPLOYMENT-STATEMENT.md) and
> [validation report](docs/VALIDATION-REPORT.md) for the current state.

## Security review evidence - 11 November 2026

| Check | Result |
|---|---|
| Deployment baseline | Prod `172.16.16.41` and dev `172.16.16.44` on `2835303b`; frontend assets contain the combined exercise workspace and the WEB01 wiki pages are published |
| Browser walkthrough | Dedicated test student and instructor accounts launched `RangeBox First Steps`; **44/44 checks passed** for the workspace layout, VNC connection, Expand/Restore, both new-tab controls, hint request, invalid-flag handling, Stop, and the mobile fallback |
| Workspace fix | **Open in new tab** now opens `/rangebox?...` in a new tab instead of navigating the exercise tab |
| Stop/relaunch race | Cleanup for an old session defers to a newer starting/running session for the same lab, so a rapid relaunch keeps its network and RangeBox instead of silently launching VPN-only |
| Workbook CSP | Wiki locations allow the Material for MkDocs Google Fonts stylesheet and font files; the SPA policy remains strict |
| Lab validation | **162 labs, 0 errors, 0 warnings** |
| Automated regression | `scripts/ui-workspace-regression.mjs` records pass/fail checks and screenshots in `ui-workspace-artifacts/` |

## Security review evidence - 15 November 2026

| Check | Result |
|---|---|
| Consent revocation | 19 tests cover immediate blocking, transactional purge/rollback, idempotency, re-grant, suppression replay, restore sweep, scheduled verification, export proof, and policy boundaries |
| Consent middleware | Unit coverage for the path matrix, revoked/regranted access, token pass-through, and CORS preflight |
| Exercise transfer | Round-trip ZIP, flag scrubbing/regeneration, metadata preservation, draft status, missing-`lab.yaml` rejection, and admin/instructor export permissions |
| Disk Management | Live dev check returns image/container/volume/build-cache usage after enabling read-only `SYSTEM` on the socket proxy |
| RangeBox workspace | Drag-to-resize desktop/details and workspace/workbook dividers with persisted layout; frontend lint and production build pass |
| Backend regression | `703 passed` in the verification copy; `ruff check app tests` clean |
| Supply chain | `supply-chain.lock.json` regenerated for the proxy change and re-signed with the release key |

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

`pip-audit` and `npm audit --omit=dev` run in CI. The dependency audit remains
a release gate; a finding that cannot be fixed immediately is
recorded with an owner and an expiry in the release notes rather than ignored
silently. The supply-chain lock adds a drift check for the same inputs.

## OWASP Top 10 baseline

The current 5.17 line uses the [OWASP Top 10 security baseline](docs/V2-SECURITY-OWASP-TOP-10.md)
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

## 2.7.0 release evidence - 11 November 2026

| Check | Result |
|---|---|
| Deployment | Dev `172.16.16.44` and prod `172.16.16.41` / `https://ctfd.swocts.com` on `ce7c25bb`, version `2.7.0`, healthy, WireGuard client route present |
| Quiz banks | Four Beginner banks seeded (5/5/4/4 questions, pass 70); `has_quiz=true` on all four levels; Stage 2 submission **100% (5/5)** on both hosts |
| Learning smoke | `scripts/ui-learning-smoke.mjs` **13/13** on completed and fresh accounts on both hosts |
| Target reveal | VPN-only labs expose the computed IP; RangeBox sessions keep `hostnames` without an IP, on both hosts |
| Non-Beginner lab | Malware `malware-1-1-eicar-triage` spawned, flag accepted, and the next lab unlocked on development |
| Supply-chain lock | **42 files and 164 lab hashes** match release `2.7.0` |
| CI | CI, Quality checks, CodeQL, and Trivy green on `ce7c25bb` |
| Release tag | `v2.7.0` is an annotated, unsigned tag on `ce7c25bb`; sign it on the release workstation if required |

## Security review evidence - 10 November 2026

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
