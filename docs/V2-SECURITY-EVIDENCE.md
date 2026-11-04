# V2 security evidence record

**Status:** Active. This is the release evidence companion to
[`V2-SECURITY-OWASP-TOP-10.md`](V2-SECURITY-OWASP-TOP-10.md).

Record one row per verification pass. Do not mark a category “verified” unless
the evidence was produced for the build being released.

## Current pass — 4 November 2026

| Category | Evidence produced | Result |
|---|---|---|
| A01 Broken access control | Analytics permission tests, competition permission tests, profile/erasure tests | Pass |
| A02 Cryptographic failures | Argon2id password path, hashed/encrypted secrets, account export/erasure tests, `Cache-Control: no-store` on PDF export | Pass |
| A03 Injection | SQLAlchemy queries, DOMPurify markdown rendering, CodeQL Python/JavaScript workflow | Pass for covered surfaces |
| A04 Insecure design | Aggregate-only analytics, no public ranking, consent withdrawal, bounded learning-time model | Pass |
| A05 Security misconfiguration | Nginx CSP/HSTS/frame/content-type/referrer/permissions headers; external probe of port 5000 and 8000 failed | Pass |
| A06 Vulnerable components | `pip-audit -r requirements.txt`: no known vulnerabilities; `npm audit --omit=dev`: 0 vulnerabilities | Pass |
| A07 Authentication failures | Login, MFA, lockout, token revocation, and login-streak tests | Pass |
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
HA failover acceptance tests are part of the v3 workstream in
[`V3-HA-LAB-POOL.md`](V3-HA-LAB-POOL.md), not a 2.0 release gate.

The lab-matrix and WireGuard items above are release blockers for 2.0 GA, not
claims that the current preview is insecure. Any accepted exception needs an
owner, expiry, and follow-up issue.
