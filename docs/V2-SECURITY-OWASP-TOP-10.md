# SWOCTS Cyber Range: V2 security baseline (OWASP Top 10)

> **Version note:** This document keeps its historical V2/V3 filename. The current platform release is **2.5.0**; Community / Academic, Professional, and Enterprise are edition profiles on that release.

This baseline applies to the SWOCTS Cyber Range deployment, powered by OpenCyberRange.

**Status:** Active for the 2.1.4 line. Applies to the web interface, platform data,
and the project delivery process. The 1.1 line keeps its existing maintenance
policy; fixes that apply there are merged forward.

This document turns the [OWASP Top 10 (2021)](https://owasp.org/Top10/) into
concrete requirements for OpenCyberRange. It is a baseline, not a claim of
certification. A change is not ready to merge until the applicable requirements
and evidence below are satisfied.

## How to use this document

1. Identify which categories the change touches.
2. Add the required tests or record why a control is not applicable.
3. Put the evidence in the pull request.
4. If a requirement cannot be met, record an exception with an owner and expiry.

Security requirements apply to new work first. Existing code is brought into
line when it is touched, or sooner if a risk is rated high.

## Requirements by OWASP category

### A01: Broken access control

**Interface**

- Every route that reads or changes learner, course, competition, or account
  data checks authentication and ownership/role on the server.
- Student, instructor, and admin boundaries are explicit. Hiding a control in
  the UI is never the only control.
- Public pages expose only the minimum fields needed (for example certificate
  verification and the celebration wall).
- Object identifiers are not trusted from the client; the server resolves the
  object and verifies access.

**Data**

- Cohort, course, and learner analytics are scoped by enrollment or instructor
  ownership before aggregation.
- Deleted-user references are cascaded or nulled; dashboards render explicit
  deleted-user labels; coaching notes with a null subject are excluded from
  course-health counts.
- Research or cross-course views require an explicit role grant.
- Exports repeat the same authorization checks as the screen that offered them.
- Administrative user imports never overwrite an existing administrator. The
  signed-in administrator is protected by user ID, other administrators are
  skipped with a warning, and new administrator creation remains an explicit
  action.
- Full snapshot restore is restricted to administrators and is a deliberate,
  destructive replacement; the UI warns that the signed-in administrator will be
  replaced.

**Project and tests**

- Add a positive and a negative authorization test for each new endpoint.
- Keep the existing permission tests for analytics, competitions, certificates,
  profile, and account deletion green.
- Report and export endpoints repeat the same ownership checks as their screens.
  Cover course reports, per-student and per-assignment reports, per-student flag
  attempts, dashboard CSV/PDF, analytics PDF, and admin exports with negative
  outsider/student tests. See `tests/test_authorization_matrix.py`.
- Public certificate verification returns only the fields needed to verify the
  award, never account identifiers. See `tests/test_certificate_verify.py`.
- Review new query parameters that accept IDs or filters for tenant/cohort
  leakage.

**Evidence:** endpoint tests with an allowed and a denied identity; pull-request
note naming the role check.

### A02: Cryptographic failures

**Interface**

- TLS is terminated with a valid certificate. HSTS is enabled on the TLS
  listener.
- Sensitive responses use `Cache-Control: no-store`.
- Secrets and tokens are never placed in URLs, logs, or client-side storage
  beyond the documented token flow.

**Data**

- Password hashes use Argon2id; legacy hashes are upgraded on successful login.
- Passwords are one-way only: no plaintext, reversible encryption, or recovery
  path. The integrity audit rejects a missing or non-Argon2id/bcrypt hash.
- TOTP secrets, recovery codes, trusted-device tokens, and WireGuard private
  keys are encrypted or hashed at rest.
- Backups are treated as sensitive data and encrypted at rest where the host
  supports it.
- New personal data is included in the account export and erasure path.
- Administrative migration exports contain password hashes but exclude MFA
  secrets, trusted devices, VPN keys, sessions, and learning progress. Export
  responses use `Cache-Control: no-store`, and the file is treated as credential
  material.

**Project and tests**

- Do not commit secrets; Trivy secret scanning and review remain required.
- Verify export/erasure coverage when a model stores personal data.
- Confirm no secret value is written to application logs.

**Evidence:** migration or model note, export/erasure test, scanner result.

### A03: Injection

**Interface**

- Vue templates use text interpolation for untrusted values. `v-html` is only
  allowed for content that is sanitized with DOMPurify or generated from a
  trusted, documented renderer.
- User-supplied URLs, markdown, workbooks, and lab content are treated as
  untrusted.
- SQL is built with SQLAlchemy expressions or bound parameters.

**Data**

- Dynamic SQL, migrations, and scripts use bound parameters.
- File paths, slugs, and identifiers are validated before filesystem or shell
  use.
- Log entries encode or redact control characters from untrusted input.

**Project and tests**

- Add an XSS regression test for any new rich-text or markdown surface.
- Keep CodeQL enabled for Python and JavaScript/TypeScript.
- Validate lab content with `scripts/validate-lab.py` before publishing.
- CSV and spreadsheet exports pass every dynamic cell through
  `app.services.spreadsheet_safety`; test formula-leading cells (`=`, `+`, `-`,
  `@`, tab, CR/LF) and full-width compatibility forms. See
  `tests/test_spreadsheet_safety.py` and `tests/test_activity_admin.py`.

**Evidence:** sanitizer call, parameterized query, or test output.

### A04: Insecure design

**Interface**

- New learner-facing metrics explain what they are and are not. They are not
  grades, diagnoses, or public rankings.
- Destructive actions require confirmation and show the impact.
- Optional feedback and surveys explain visibility and consent.

**Data**

- Collect the minimum data needed. Prefer aggregate counters over new
  individual tracking.
- Define retention and deletion for new stores before shipping.
- Small-group reporting must suppress or aggregate cells that could identify a
  learner.

**Project and tests**

- Write the abuse case and the failure mode in the change request.
- Add a rollback or disable path for new integrations and background jobs.
- Review privacy impact for any new personal data field.

**Evidence:** design note, threat-model bullet, or privacy review.

### A05: Security misconfiguration

**Interface**

- Nginx keeps `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
  `Permissions-Policy`, CSP, and HSTS on the TLS listener.
- A deny-all `robots.txt`, `noindex` page metadata, `X-Robots-Tag`, and a
  user-agent map return `403` to known search and AI crawlers. See
  [Anti-scraping and crawler controls](ANTI-SCRAPING.md).
- CSP changes are reviewed against the actual scripts and fonts in use.
- Debug mode, stack traces, and permissive CORS are not enabled in production.

**Data**

- Database and Redis are not exposed publicly.
- Default credentials are changed during setup; demo credentials are never
  shipped as production defaults.
- `LAB_ALLOW_ON_DEMAND_BUILD=false` in production.

**Project and tests**

- Trivy configuration scanning stays enabled.
- Compose and environment changes include a configuration review.
- New settings have safe defaults and are documented in the deployment manual.

**Evidence:** config diff, scanner result, or deployment check.

### A06: Vulnerable and outdated components

**Interface and data**

- Frontend and backend dependencies are pinned and upgraded deliberately.
- Container base images are rebuilt on a regular cadence.

**Project and tests**

- Dependabot remains enabled for Python, npm, and Docker.
- `pip-audit` and `npm audit --omit=dev` must stay clean or carry a documented
  exception with an owner and expiry.
- CodeQL, Trivy, and the dependency-audit workflow remain required checks.
- A major runtime or framework upgrade needs a build, test, and rollback note.

**Evidence:** audit output, Dependabot PR, or exception record.

### A07: Identification and authentication failures

**Interface**

- Login errors do not reveal whether an account exists.
- MFA challenges are shown only after the password step succeeds.
- Session expiry and revocation are visible and actionable.

**Data**

- JWTs are signed, expire, and are checked against the revocation table.
- Login, registration, password reset, and MFA endpoints are rate-limited.
- Failed-attempt lockout and administrator approval remain enforced server-side.
- Admin password resets require the administrator's own password, revoke the
  target's sessions, force a password change, and are audited. The general
  profile update endpoint rejects password changes.
- Login streak tracking uses calendar dates only; it does not add new
  authentication signals.

**Project and tests**

- Add tests for both success and failure paths when authentication changes.
- Never log passwords, MFA codes, recovery codes, or full tokens.
- Review cookie and token storage whenever the frontend auth flow changes.

**Evidence:** auth test output and a note on rate limits or lockout.

### A08: Software and data integrity failures

**Interface**

- Uploaded images are validated by type and size before storage or display.
- Client-side state is not trusted for scores, completions, or permissions.

**Data**

- Lab images and compose files are built from reviewed sources.
- Database migrations are idempotent and run before traffic is served.
- Critical tables have a signed SHA-256 checksum manifest and an append-only
  change ledger with actor attribution. Manual or uninstrumented writes are
  recorded as `unattributed` and reported.
- A data-quality audit checks orphans, duplicate keys, invalid enums, null
  critical fields, invalid JSON, bad quiz/feedback ranges, and password hash
  format.
- Backups are verified by a restore drill, not only by file creation.
- Cross-system snapshot uploads are administrator-only, restricted to plain
  `.sql` files, capped at 512 MB, stored in the backup volume, and applied in a
  single transaction with `ON_ERROR_STOP=1`.
- Achievement and completion writes remain idempotent.

**Project and tests**

- CI builds the changed images and runs the test suite.
- Upgrade scripts create a backup before applying changes.
- New background jobs are safe to retry.

**Evidence:** migration note, restore check, or idempotency test.

### A09: Security logging and monitoring failures

**Interface**

- Security-relevant actions are recorded without secrets or unnecessary
  personal data.
- User-facing errors give an actionable message without exposing internals.

**Data**

- Authentication, authorization failures, admin actions, account deletion, and
  mail-setting changes are logged.
- The integrity ledger records the actor type, actor id, request id, row hash,
  and chained entry hash for every critical-table write.
- Every data export records the operator-supplied reason, exporter, format, and
  scope. Self-service exports and transcripts record a fixed purpose instead of
  prompting the learner.
- Logs redact IP addresses where the privacy policy requires it.
- Retention and access to logs are documented.

**Project and tests**

- New sensitive actions emit an activity or audit event.
- Do not log request bodies that may contain passwords or tokens.
- Include a monitoring or detection note for new abuse paths.

**Evidence:** log/event name and a redaction check.

### A10: Server-side request forgery

**Interface**

- User-supplied URLs are not fetched by the browser or server without an
  allowlist or explicit confirmation.
- Workbook and resource links open in a controlled way and are validated.

**Data**

- Server-side fetches block loopback, link-local, private, and metadata
  endpoints unless the feature is explicitly an internal integration.
- Webhooks and import URLs use an allowlist and timeouts.

**Project and tests**

- Add a negative test for private-address and redirect targets when a new
  server-side fetch is introduced.
- Keep the Peer Manager API internal-only.

**Evidence:** URL validation test or integration boundary note.

## Security testing matrix

| Layer | Required check | When |
|---|---|---|
| Backend unit/integration | `pytest -q` with PostgreSQL | Every change |
| Authorization | Allowed and denied identity tests | Every endpoint change |
| Frontend | `npm run lint` and `npm run build` | Every UI change |
| Static analysis | CodeQL for Python and JavaScript/TypeScript | Every PR and scheduled |
| Dependencies | `pip-audit`, `npm audit --omit=dev` | Every PR and weekly |
| Containers/config | Trivy filesystem, secret, and config scan | Every PR and scheduled |
| Lab content | `scripts/validate-lab.py` | Every lab change |
| Manual | Exercise the changed screen or endpoint | Every change |
| Release | Backup, migration, health check, rollback note | Every production release |

## Pull-request definition of done

- [ ] The change lists the OWASP categories it touches.
- [ ] New endpoints have allowed/denied authorization tests.
- [ ] New personal data is covered by export, erasure, and retention notes.
- [ ] New rich text or markdown is sanitized, with an XSS regression test.
- [ ] New dependencies or images pass the audit and scan workflows.
- [ ] New settings have safe defaults and deployment documentation.
- [ ] Security-relevant actions emit an audit/activity event.
- [ ] Any unmet requirement has an owner, expiry, and accepted-risk note.

## Exceptions

An exception is acceptable only when it is written down:

- the requirement that cannot be met;
- why the compensating control is sufficient;
- the owner;
- the expiry date;
- the follow-up issue.

Expired exceptions are treated as open findings. A release note may not silently
drop one.

## Review cadence

- **Every release:** confirm the matrix was run and record the result.
- **Quarterly:** review this document against the current OWASP Top 10 and the
  platform's actual attack surface.
- **After an incident:** add the missed control to this document and to the test
  matrix.

OWASP Top 10 is the floor, not the ceiling. The platform also relies on its
WireGuard and container isolation model, backup and erasure procedures, and the
responsible-disclosure process in [SECURITY.md](../SECURITY.md).
