# SWOCTS Cyber Range: V2 security evidence record

> **Version note:** This document keeps its historical V2/V3 filename. The current platform release is **2.5.0**; Community / Academic, Professional, and Enterprise are edition profiles on that release.

This evidence record applies to the SWOCTS Cyber Range deployment, powered by OpenCyberRange.

**Status:** Active. This is the release evidence companion to
[`V2-SECURITY-OWASP-TOP-10.md`](V2-SECURITY-OWASP-TOP-10.md).

Record one row per verification pass. Do not mark a category “verified” unless
the evidence was produced for the build being released.

## Current pass — 9 November 2026

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
