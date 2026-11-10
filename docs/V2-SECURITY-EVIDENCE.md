# SWOCTS Cyber Range: V2 security evidence record

> **Version note:** This document keeps its historical V2/V3 filename. The current platform release is **2.5.4**; Community / Academic, Professional, and Enterprise are edition profiles on that release.

This evidence record applies to the SWOCTS Cyber Range deployment, powered by OpenCyberRange.

**Status:** Active for the 2.5.4 line. This is the release evidence companion to
[`V2-SECURITY-OWASP-TOP-10.md`](V2-SECURITY-OWASP-TOP-10.md).

Record one row per verification pass. Do not mark a category “verified” unless
the evidence was produced for the build being released.

## Current pass — 10 November 2026 (2.5.4)

| Category | Evidence produced | Result |
|---|---|---|
| A01 Broken access control | Authorization matrix covers report/export routes, certificate verification, admin surfaces, course analytics, and the new instructor learning snapshot. Instructor PDF export is explicitly scoped to owned courses; outsider and student identities receive `403`. `tests/test_authorization_matrix.py`, `tests/test_certificate_verify.py`, `tests/test_certificate_verify_input.py` | Pass for covered paths |
| A02 Cryptographic failures | Release signing key rotated for 2.5.4. `v2.5.4` is a signed annotated tag and `supply-chain.lock.json.asc` verifies with the committed public key. Active fingerprint: `095B D8B5 6802 771D A27E 759E 1BAE 4CD3 1609 A1BF`. The first candidate key was discarded before use and no artifact was signed with it. JWT and database secrets are non-default in the status check. TLS termination remains at Cloudflare/OPNsense; NPM Force SSL is intentionally off. | Pass |
| A03 Injection | Scenario markdown is sanitized and external links are validated before rendering. CSV exports neutralize formula-leading cells. Lab metadata is schema-validated, and CodeQL is green for Python and JavaScript/TypeScript. `tests/test_input_safety.py`, `tests/test_spreadsheet_safety.py`, `tests/test_activity_admin.py`, `tests/test_lab_metadata_schema.py`, `scripts/validate-lab.py --all` | Pass for covered surfaces |
| A04 Insecure design | Analytics remains aggregate-only with minimum-cohort suppression and no public learner ranking. The new instructor learning snapshot reuses scoped session/completion/attempt data and returns counts/medians, not learner answers. `tests/test_analytics.py`, `tests/test_competency_radar.py`, `tests/test_instructor_learning_metrics.py` | Pass |
| A05 Security misconfiguration | Nginx CSP, HSTS, frame, content-type, referrer, and permissions headers remain enforced. External probes to ports 5000 and 8000 remain blocked. NPM Force SSL is intentionally off because Cloudflare/OPNsense already terminate and enforce TLS. UI smoke against `https://ocr.swocts.com` passed (`42741914124`). `scripts/check-nginx-security-headers.py`, `/api/admin/system/status` | Pass |
| A06 Vulnerable components | Trivy filesystem/secret/config scan and CodeQL are green on the 2.5.4 commits. The 8 November dependency audit reported no known Python or production npm vulnerabilities; no dependency pins changed in this pass. | Pass for scanned inputs; dependency audit not rerun in this pass |
| A07 Authentication failures | Login, MFA, lockout, token revocation, profile, and admin re-authentication/session-revocation tests remain green in the backend suite. No authentication contract changed in 2.5.4. `tests/test_auth.py`, `tests/test_mfa.py`, `tests/test_token_revocation.py`, `tests/test_profile.py` | Pass for covered paths |
| A08 Integrity failures | Alembic migrations `0007_lab_metadata` and `0008_mitre_attack` are additive and applied on both OCR stacks. Supply-chain lock covers 37 files and 149 labs and verifies with the rotated release key. The database integrity ledger remains active. | Pass |
| A09 Logging/monitoring failures | Report/export reason logging, activity events, and admin audit actions are unchanged and included in the authorization matrix. The key rotation is recorded in the release evidence and supply-chain docs; no secret material is committed. | Pass for covered paths |
| A10 SSRF | External URL handling rejects unsafe schemes and private targets; no new server-side fetch was added. Peer Manager remains internal and port 5000 is not externally exposed. `tests/test_input_safety.py` | Pass |
| Supply chain | `supply-chain.lock.json` regenerated for 2.5.4 and signed with the rotated key. Public key committed; private key remains outside the repository under a release-owner-controlled path. | Pass |

Manual evidence:

- CI, Quality checks, CodeQL, and Trivy are green on the 2.5.4 release commits.
- UI smoke: run `42741914124`, success against `https://ocr.swocts.com` on `2.5.4`.
- Backend non-DB suite: **176 passed**.
- DB-backed metadata, instructor-metrics, course-focus, analytics, competency, and authorization tests passed against disposable PostgreSQL.
- Lab validation: **149 labs, 0 errors, 0 warnings**.
- Lab release proof: **149 pass, 0 review, 0 fail**.
- Supply-chain check: **37 files, 149 labs**, signature verified.
- Public OCR and CTFd-host OCR both report `/api/version` **2.5.4** and healthy containers.

Residual notes:

- Full lab-matrix, KVM, WireGuard, firewall-persistence, and restore drills remain real-host certification gates.
- Public certificate verification necessarily exposes the recipient name; it returns no account identifiers.
- NPM Force SSL remains intentionally off; TLS enforcement is at Cloudflare/OPNsense.
- The CTFd host `.41` also runs an OCR stack; 2.5.4 does not change CTFd.
- A full axe/WCAG pass for the new dashboard and MITRE panel remains a follow-up; the UI smoke passed.

## Code-scanning remediation — 10 November 2026

The open alert set on `main` was **595** (69 CodeQL, 526 Trivy). The earlier
100-alert count was a single page of the paginated API, not the repository
total.

Platform CodeQL fixes:

- About licence/SBOM downloads, stress-test event reads, exercise-test run
  state, and workbook chapter deletion now select an existing path from a
  directory listing instead of joining a request value.
- Lab ZIP uploads rebuild the target and each entry from single basename
  components, reject `.`/`..`, and verify containment with `os.path.commonpath`.
- Lab relocation and workbook extraction rebuild paths from sanitized
  components.
- Stack traces and daemon/exception details are no longer returned from RangeBox
  status, Docker disk usage, image cleanup, lab discovery, workbook upload and
  build, or bundled-walkthrough processing.
- Seed scripts require `DEMO_FEATURE_PASSWORD`,
  `DEMO_ANALYTICS_PASSWORD`, `CAREER_DEMO_PASSWORD`,
  `DEMO_INSTRUCTOR_PASSWORD`, and `DEMO_STUDENT_PASSWORD` from the environment;
  they no longer print or write those values. Audit details redact
  password/secret/token/key fields.
- `admin-vnc.html` builds DOM nodes with `textContent` instead of interpolating
  the query-string value into `innerHTML`.
- The `py/bad-tag-filter` finding on the requirements-specifier regex is a
  documented false positive and is suppressed inline.
- Lab and template target applications are excluded from CodeQL because their
  command injection, SQL injection, path traversal, and reflected XSS are the
  exercise content. Lab structure remains gated by `scripts/validate-lab.py` and
  `scripts/lab-release-proof.py`.

Trivy fixes and policy:

- Removed the informational `EXPOSE 22` from lab/template images; Compose owns
  published ports.
- Removed `RUN cd` from two lab builds.
- Replaced fake Stripe, Plaid, SendGrid, internal-API, and JWT values with
  explicit `FAKE_*_DO_NOT_USE` markers, including generated wiki HTML/JSON.
- Added [`.trivyignore.yaml`](../.trivyignore.yaml) with path-scoped, documented
  suppressions for intentional lab root users, missing container healthchecks,
  recommended-package installs needed by simulated services, weak lab database
  credentials, and the privileged platform components that need the Docker
  socket, privileged ports, or raw sockets. The Trivy workflow passes the file
  through `trivyignores`.
- Added Dockerfile healthchecks to the backend and frontend images to match
  their Compose probes.

Local verification:

- `trivy fs --scanners misconfig,secret --ignorefile .trivyignore.yaml` reports
  **0** findings.
- `scripts/validate-lab.py --all`: **149 labs, 0 errors, 0 warnings**.
- `scripts/lab-release-proof.py`: **149 pass, 0 review, 0 fail**.
- Backend targeted suites: **47 passed, 3 DB-backed skipped**.
- Frontend lint: **0 errors**; production build succeeded.

## Previous pass — 9 November 2026

| Category | Evidence produced | Result |
|---|---|---|
| A01 Broken access control | Report/export authorization matrix: course PDF reports, per-student and per-assignment reports, per-student flag attempts, instructor dashboard CSV/PDF, analytics PDF, and admin user/activity/backup exports. An outsider instructor and a student both receive `403`; owner/admin positives pass. `tests/test_authorization_matrix.py` | Pass for covered paths |
| A01/A02 | Public certificate verification returns only recipient, track/level, completion counts, dates, and issuer fields. `username`, `email`, `student_id`, and `user_id` are asserted absent; malformed and oversized IDs are rejected before database work. `tests/test_certificate_verify.py`, `tests/test_certificate_verify_input.py` | Pass |
| A03 Injection | CSV formula injection: every dynamic cell in dashboard and admin activity CSV exports passes through `neutralize_cell`/`neutralize_row`. Leading `=`, `+`, `-`, `@`, tab, CR/LF, and full-width forms are prefixed with an apostrophe. `tests/test_spreadsheet_safety.py`, `tests/test_activity_admin.py` | Pass |
| A01/A05 | Exercise Tester is a dev-only module (`kind=devtool`), stripped from shipped editions by the build manifests and only mounted for the explicit dev-tool prefixes. Confirm the module is disabled in production profiles; it is not an end-user surface. | Reviewed; production profiles omit the module |

The new authorization, CSV, and certificate assertions are DB-gated and run in CI with `TEST_DATABASE_URL`; the spreadsheet-safety unit tests also run without a database.

Residual privacy note: certificate verification is intentionally public and
deterministic. It is rate-limited to 30 requests/minute and returns no account
identifiers, but the recipient name is necessarily public to make the
certificate verifiable. If recipient-name unlinkability becomes a requirement,
issue longer random verification tokens instead of the current deterministic
certificate ID.

## Previous pass — 8 November 2026

| Category | Evidence produced | Result |
|---|---|---|
| A01 Broken access control | Deleted-user lifecycle review: cascade and `SET NULL` references, course-transfer block, null-safe dashboard labels, orphaned-coaching exclusion | Pass for covered paths |
| A02 Cryptographic failures | Password storage audit: Argon2id for new hashes, bcrypt legacy verify-and-upgrade, no plaintext or reversible storage, hash-format check | Pass |
| A08 Integrity failures | Signed table checksums, append-only change ledger with actor attribution, immutable ledger trigger, database quality audit on dev and production | Pass; 0 critical / 0 warning on both |
| A09 Logging/monitoring failures | Ledger records actor type, actor id, request id, row hash, and chained entry hash; a deliberate manual `labs.UPDATE` was detected as `unattributed` | Pass for covered tables |
| Supply chain | `supply-chain.lock.json` verified in CI; install, update, and prebuild gates wired | Pass |

Manual evidence:

- Development database fingerprint:
  `ea4f9acb1cd8fa17f28c66841dba7620abcac76f099862c810bbf60cdc3c4c9c`.
- Development quality: 0 critical, 0 warning, 2 info (36 completions without a
  session; 149 seeded labs without a creator).
- Production quality: 0 critical, 0 warning, 3 info (116 completions without a
  session; 149 seeded labs without a creator; 2 intentional hint placeholders).
- Frontend build and lint pass; six-trait Cyber DNA, Celebration Wall toggle,
  dark/light, 390 px and 1440 px checks show no page errors or overflow.

## Previous pass — 6 November 2026

| Category | Evidence produced | Result |
|---|---|---|
| A01 Broken access control | Admin user export/import tests; signed-in administrator and other-administrator overwrite protection; role-protected export endpoints | Pass |
| A02 Cryptographic failures | Administrative export carries password hashes with `Cache-Control: no-store`; self-service export excludes secrets; backup downloads are audited | Pass |
| A08 Integrity failures | Uploaded `.sql` snapshot validation (extension and 512 MB cap); staged upload test; single-transaction restore with `ON_ERROR_STOP=1` | Pass |
| A09 Logging/monitoring failures | Export reason recorded for user, activity, backup, report, and test-report exports; self-service and transcript exports record fixed purposes | Pass |

Backend suite: 177 passed in the verification environment. Frontend production
build passed. Existing restore-drill and dependency-audit evidence from the
4 November pass still applies.

## Previous pass — 4 November 2026

| Category | Evidence produced | Result |
|---|---|---|
| A01 Broken access control | Analytics permission tests, competition permission tests, profile/erasure tests | Pass |
| A02 Cryptographic failures | Argon2id password path, hashed/encrypted secrets, account export/erasure tests, `Cache-Control: no-store` on PDF export | Pass |
| A03 Injection | SQLAlchemy queries, DOMPurify markdown rendering, CodeQL Python/JavaScript workflow | Pass for covered surfaces |
| A04 Insecure design | Aggregate-only analytics, no public ranking, consent withdrawal, bounded learning-time model | Pass |
| A05 Security misconfiguration | Nginx CSP/HSTS/frame/content-type/referrer/permissions headers; deny-all `robots.txt`; `X-Robots-Tag` and `noindex` metadata; crawler user agents return `403`; external probe of port 5000 and 8000 failed | Pass |
| A06 Vulnerable components | `pip-audit -r requirements.txt`: no known vulnerabilities; `npm audit --omit=dev`: 0 vulnerabilities | Pass |
| A07 Authentication failures | Login, MFA, lockout, token revocation, and login-streak tests; admin resets require re-authentication, revoke target sessions, force a password change, and reject password changes on the general update endpoint | Pass for covered paths |
| A08 Integrity failures | Restore drill into temporary database, image type/size validation, idempotent migrations | Pass |
| A09 Logging/monitoring failures | Activity/audit events for security actions, redacted IP handling, no secret logging in tested paths | Pass for covered paths |
| A10 SSRF | No user-supplied server-side fetch in the reporting/feedback path; Peer Manager remains internal and port 5000 is externally blocked | Pass |

## 24.04 platform evidence

- Host: Ubuntu 24.04.5 LTS, kernel 6.8.0-147-generic.
- KVM: `vmx` visible, `/dev/kvm` present.
- Platform service: active.
- VPN firewall service: active.
- WireGuard service: active.
- External probes to ports 5000 and 8000 failed.
- Representative lab spawn: `windows-1-1-basic-port-scan` reached `running`,
  then stopped and cleaned up.
- Restore drill: production dump restored into a temporary database; user count
  matched and the temporary database was dropped.

## Open evidence items

- Full lab matrix: multi-container, capture, shared-container, RangeBox,
  UbuntuBox, and REMnuxBox exercises.
- WireGuard client tunnel and reboot-persistence check.
HA failover acceptance tests are part of the Enterprise preview workstream in
[`V3-HA-LAB-POOL.md`](V3-HA-LAB-POOL.md), not a 2.1.4 release gate.

The lab-matrix and WireGuard items above are release blockers for 2.1.4 GA, not
claims that the current preview is insecure. Any accepted exception needs an
owner, expiry, and follow-up issue.
