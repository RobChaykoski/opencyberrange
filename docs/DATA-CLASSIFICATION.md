# Data classification

SWOCTS Cyber Range uses four handling classes. Classification is metadata that
tells people how to handle an export. Institutions may make it enforceable for
downloads with `data_label_enforcement_enabled`; RBAC, tenant, and consent
checks still apply first. See [Export data labels](DATA-LABELS.md).

| Class | Meaning | Examples |
|---|---|---|
| **Public** | Safe for anyone, including visitors | Public certificate verification metadata, public badges, published workbook pages |
| **Internal** | Staff/operator use; not for public release | Aggregate course analytics above the cohort threshold, platform settings, backup manifests |
| **Confidential** | Learner, instructor, or institutional records | Account profile, enrolments, completions, attempts, certificates, instructor reports, portfolio snapshots |
| **Restricted** | Credentials, security evidence, private intelligence, or data that could cause serious harm | Password hashes, MFA secrets, recovery codes, WireGuard private keys, IdP client secrets, Cyber DNA/GPS derived intelligence, AI memory, consent revocation audits |

## Inventory

| Data set | Classification | Retention | Export handling |
|---|---|---|---|
| Account identity (username, email, name, student ID, organisation, avatar) | Confidential | Account lifetime; erased with the account | Account export, labelled |
| Password hash, MFA secret, recovery codes, trusted devices | Restricted | Account lifetime; never exported | Excluded from exports |
| VPN public/private key, assigned client IP | Restricted | Account lifetime; peer removed on erasure | Private key never exported; metadata labelled |
| Course enrolment, completions, flag attempts, quiz attempts, achievements, certificates | Confidential | Institution schedule; course retention workflow | Transcript/report exports, labelled |
| Lab sessions and container metadata | Confidential | Operationally bounded; erased with the account | Included only where the account export needs session history |
| Cyber DNA evidence, snapshots, behaviour/interest/affinity | Restricted | Consent lifetime; deleted on revocation | Never included in an employer-facing or public export; account export carries consent state, not derived payloads |
| Cyber GPS directions, readiness, routes | Restricted | Consent lifetime; computed on demand, no persisted cache | Not exported |
| Portfolio and career/report snapshots | Confidential | Consent lifetime; deleted on revocation or account erasure | Portfolio export, labelled; employer sharing is opt-in |
| AI coach conversations, prompt context, embeddings, memory | Restricted | Consent lifetime; purge on revocation (tables activate when the feature ships) | Not exported |
| Consent state/history, revocation proof, suppression ledger | Restricted | Account lifetime; proof audit survives under a keyed subject hash | Consent section in the account export; no deleted payload |
| Activity/audit events | Internal | Short documented window (up to 90 days default) | Admin export with recorded reason |
| Security/audit/privacy event store | Restricted | 365 days recommended; append-only, operator archive/prune | Admin query API; never a learner export |
| Authentication sessions and refresh-token hashes | Restricted | Session/token lifetime plus audit window | Auth service; admin metadata only; never a learner export |
| RBAC role catalog and permission grants | Internal | Release lifetime | Admin and authorization service; never a learner export |
| Settings change sets (ticket/reason encrypted; secret values redacted) | Internal | Audit retention; at least one year, institution schedule | Admin/auditor; never a learner export |
| Production cutover evidence (ticket/notes encrypted; counts and hash only) | Restricted | Permanent audit evidence | Admin/auditor; never a learner export |
| Database integrity ledger | Restricted | Release/audit schedule | Not a learner export |
| Reports and report manifests | Confidential | Course/institution schedule | PDF/CSV label + manifest |
| Backups | Restricted | 30 days by default | Operator-only, access-controlled |
| Aggregate learning analytics | Internal | Institution schedule; small cohorts suppressed | Reports/exports, labelled |
| Published workbook/wiki pages | Public | Content lifecycle | Published as static pages |
| Public certificate verification and badges | Public | Certificate/badge lifetime | Public viewer |

## Where classification is applied

- **Export labels:** Admin -> Settings -> Data labels sets the classification
  stamped on PDF, CSV, JSON, Markdown, and HTML exports. See
  [Export data labels](DATA-LABELS.md).
- **HTTP headers:** attachment, PDF, and CSV responses carry
  `X-Data-Classification`, `X-Data-Organisation`, `X-Data-Handling`,
  `X-Data-Source`, and optionally `X-Export-Generated-At`.
- **Access control:** the Authorization Service decides who can read a record
  using RBAC, tenant, owner/share scope, and consent. When label enforcement is
  on, it also decides whether the export may be downloaded. Classification does
  not grant access.
- **Security events:** every export allow/deny, consent change, RBAC change,
  break-glass use, and sensitive authentication event is recorded in the
  append-only store described in [Security event store](SECURITY-EVENTS.md).
- **Data dictionary:** table-by-table definitions live in
  [Data dictionary](DATA-DICTIONARY.md).
- **Change control:** production settings changes are ticket-gated change sets.
  Ticket numbers and reasons are Fernet-encrypted, secret values are redacted,
  and every apply/revert is a security event. The one-way production cutover
  removes sample/test accounts, records an evidence hash, and cannot be
  reversed from the application. See [Data dictionary](DATA-DICTIONARY.md).

## Limits

- Labels do not encrypt or redact a file. A recipient who receives a
  Confidential or Restricted export can still read it.
- Backup archives, Open Badge credentials, and public certificates are separate
  formats; badges and public verification are public by design.
- Lab content is public only when its visibility is `public`; draft, course, and
  pending-review labs are internal or confidential until published.
