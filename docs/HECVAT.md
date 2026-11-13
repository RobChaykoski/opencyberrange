# HECVAT answer pack (draft)

Status: **Release 5 deliverable.** This is a working answer pack, not a completed
HECVAT Full and not a third-party assessment. An operator must review, sign, and
attach current evidence.

## Scope

The product is a self-hosted web application for cybersecurity training. The
institution normally operates the host, database, and backups; the vendor
supplies software, updates, and support. Answer each question for the deployment
model actually sold.

## Domain answers

### Company and service

- Service: OpenCyberRange / SWOCTS Cyber Range, self-hosted.
- Data centre: institution-selected. No vendor cloud is required.
- Sub-processors: none by default. Optional SMTP is the only outbound service.
- AI/LLM sub-processor: none.

### Data classification and handling

- Data: account identifiers, institutional ID, email, role, enrolment,
  assessment evidence, audit events.
- Sensitive data requested: none (no health, financial, or government ID).
- Encryption in transit: TLS 1.2/1.3 at nginx.
- Encryption at rest: application secrets are encrypted; database and backup
  volume encryption is a host control and must be confirmed per deployment.
- Data minimisation: labs do not receive learner email; SSO can be configured
  with minimal claims.

### Access control

- Roles: admin, instructor, student. TA scoping is a Release 5 gap.
- MFA: TOTP for privileged accounts.
- Passwords: Argon2id; bcrypt legacy upgraded on login.
- Admin actions: audited.
- Tenant isolation: single-tenant deployment. Shared-database multi-tenancy is
  not offered in Release 4.

### Vulnerability and change management

- Pinned dependencies and a signed supply-chain manifest.
- Automated dependency and container scanning in CI.
- Security review of changes; signed release tags.
- Schema changes are reviewed Alembic revisions plus idempotent compatibility
  ALTERs; startup applies them under a PostgreSQL advisory lock. See
  `docs/DATABASE-MIGRATIONS.md`.
- Internal security review: `docs/SECURITY-REVIEW-2026-11.md`.
- Third-party penetration test: not held.

### Business continuity

- Daily database snapshots with a 30-day default retention.
- Restore runbook and erasure-suppression replay.
- HA profile documented separately; single-host is the default.

### Incident response

- Audit trail with actor, action, target, time, and IP.
- Erasure redacts identifying fields while retaining the security record.
- Notification is an institutional process; the DPA template commits to 72-hour
  vendor notification where the vendor hosts.

### Privacy and retention

- Self-service export and erasure.
- Suppression ledger prevents backup resurrection.
- Activity purge and backup retention are configurable.
- Term-end and whole-institution purge/archive are Release 5 gaps.
- Quebec PIA/TRA: institution completes; the product supplies the inventory.

### Accessibility

- WCAG 2.2 AA target; partial conformance with known limitations.
- VPAT/ACR: not signed. Release 5 audit.
- Accommodations: per-student time multiplier and due-date extension, managed by an instructor and audited; pause/resume remains future work.

### AI

- No AI grading, no learner data sent to an LLM, no model training.
- Automated-decision transparency: deterministic flag matching; see
  `docs/AUTOMATED-SCORING.md`.

## Evidence index

| Topic | File |
|---|---|
| Architecture and trust boundaries | `docs/ARCHITECTURE.md` |
| Privacy notice | `docs/PRIVACY-NOTICE.md` |
| Privacy, erasure, backups | `docs/PRIVACY-AND-DATA-DELETION.md` |
| Analytics governance | `docs/ANALYTICS-GOVERNANCE.md` |
| Supply chain | `docs/SUPPLY-CHAIN.md` |
| Database schema and migrations | `docs/DATABASE-MIGRATIONS.md` |
| Security review | `docs/SECURITY-REVIEW-2026-11.md` |
| Compliance posture | `docs/COMPLIANCE.md` |
| Procurement traceability | `docs/PROCUREMENT-REQUIREMENTS.md` |
| DPA template | `docs/DPA-TEMPLATE.md` |
| Accessibility | `docs/ACCESSIBILITY.md` |
| Automated scoring | `docs/AUTOMATED-SCORING.md` |

## Sign-off

| Role | Name | Date |
|---|---|---|
| Security owner | | |
| Privacy owner | | |
| Product owner | | |
