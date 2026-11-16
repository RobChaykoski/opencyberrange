# Consent revocation and data destruction

OpenCyberRange treats consent withdrawal as a data-destruction workflow, not a
best-effort delete. A revocation must stop processing immediately, remove
derived intelligence, preserve the educational record, prove what happened, and
survive a backup restore or event replay.

## Three tiers

| Tier | Guarantee | Implementation |
|---|---|---|
| 1. Stop processing | The feature is blocked before the revoke request returns. | `consent_states.granted=false` and `revocation_in_progress=true`; DNA ingest, DNA APIs, GPS, portfolio, and derived-report endpoints check it. |
| 2. Delete derived data | Registered targets are purged and verified. | `app/consent/` orchestrator, durable `consent_jobs` queue, transactional purge groups, verification at 0h/24h/7d. |
| 3. Suppress resurrection | Deleted data cannot return from a backup, replay, cache, or recomputation. | Append-only file ledger `consent-suppression.jsonl`, `enforce_suppressions()` sweep, and ingest-time suppression checks. |

## Data inventory

Derived intelligence is removable. Educational records are retained.

| Removed on revocation | Retained |
|---|---|
| `dna_evidence_records` | `lab_completions` |
| `dna_snapshots` | `flag_attempts` and quiz attempts |
| `learner_snapshots` of kind `portfolio` / `career_dossier` | certificates and level awards |
| Future `ai_conversations`, `ai_embeddings`, `ai_memory` | `achievements` |
| Future `portfolio_share_tokens`, `public_profiles` | course enrolment and transcript |
| Future learner-level analytics/segmentation/research rows | course progress |

`app/consent/registry.py` is the single inventory. A privacy-sensitive table
must appear in `PRIVACY_TABLES` and have a purge + verification hook in
`app/consent/hooks.py`. `assert_privacy_targets_registered()` runs in tests and
the admin metrics endpoint fails the `privacy_registry_complete` flag if a
target is missing.

## Consent types

| Type | Default | Removes |
|---|---|---|
| `cyber_dna` | granted | competency evidence, DNA snapshots, derived reports |
| `cyber_gps` | granted | direction/gap/readiness views (computed on demand) |
| `portfolio` | granted | stored portfolio and career snapshots |
| `portfolio_sharing` | not granted | share tokens and public profiles when those tables ship |
| `ai_coach` | not granted | conversations, embeddings, and AI memory when those tables ship |
| `research` | not granted | learner analytics, segmentation, research rows when those tables ship |

Defaults preserve the existing behaviour of DNA, GPS, and portfolio. Revocation
is explicit, versioned, and durable. Re-granting allows new activity; it never
restores deleted data.

## Revocation transaction

1. Append a committed suppression entry to the file ledger and fsync it.
2. Transactionally write `consent_states`, `consent_events`,
   `consent_revocations`, one `consent_jobs` row per target, the DB suppression
   mirror, and the proof-only `consent_audits` row.
3. Call the `before_profile_purge` hook: set the persisted lock and clear caches.
4. Commit. The HTTP response is `202` with the revocation and current state.

If the ledger write fails, the request fails before any database change. If the
database transaction fails after the ledger write, a `cancelled` ledger entry is
appended so a future restore cannot suppress a live account.

## Purge and verification

- The scheduler drains `consent_jobs` every minute; administrators can run
  `POST /api/consent/admin/run-jobs`.
- All targets for one revocation execute in **one database transaction**. If a
  target raises, the transaction rolls back and no table is partially purged.
  The revocation is marked `failed`, jobs retry with backoff, and a later pass
  re-runs the whole group.
- After all purge targets complete, verification jobs are queued at once, 24
  hours, and 7 days.
- A verification counts remaining rows for every target. Non-zero marks the
  revocation failed, re-queues the purge, and keeps the feature locked.
- Passing verification writes/updates the audit row: `jobs_completed`,
  `verification_slots`, `verified`, and `verified_at`. The audit stores proof
  only, never deleted payloads.

## Suppression and restore protection

`CONSENT_SUPPRESSION_PATH` defaults to
`/workbook/consent-suppression.jsonl` (the persistent workbook volume). Entries
contain an HMAC subject hash, consent type, consent version, status, and
timestamp — no user id, username, email, or deleted data.

- `emit_completion_event()` checks both the live consent state and the ledger,
  so an at-least-once event replay cannot recreate DNA evidence.
- `enforce_suppressions()` scans DNA evidence, DNA snapshots, learner
  snapshots, consent state, and suppression rows. For any subject with a
  committed suppression it flips a restored `granted` row back to revoked,
  runs the purge targets, verifies them, and records a `suppression_sweep`
  audit slot.
- A later `cancelled` entry (explicit re-grant or a failed transaction) wins,
  so suppression history remains complete without blocking a new consent.

Run the sweep from the scheduler or `POST /api/consent/admin/enforce-suppressions`.

## API

The learner-facing dashboard is **Profile → Security & privacy → AI and career
data**. It lists each consent, the live removal state, what revocation removes,
what remains, the latest audit proof, and recent consent history, and refreshes
automatically while a removal is queued, running, or verifying.

Learner:

- `GET /api/consent/` — states, revocation history, remaining education records
- `GET /api/consent/types` — available types, defaults, removed/kept lists
- `POST /api/consent/{type}/revoke` — immediate block + queued destruction
- `POST /api/consent/{type}/grant` — re-enable processing
- `GET /api/consent/revocations` — own proof records

Administrator / privacy officer (policy-checked):

- `GET /api/consent/admin/revocations`
- `POST /api/consent/admin/run-jobs`
- `POST /api/consent/admin/enforce-suppressions`
- `GET /api/consent/admin/metrics`

Blocked surfaces return `403` with `X-Consent-Status: revoked` or
`revocation_in_progress`. The DNA router, DNA event adapter, GPS endpoint,
portfolio/snapshot endpoints, competency/readiness endpoints, and account
export all use the same check.

## Metrics and SLA

`GET /api/consent/admin/metrics` returns:

- total/complete/pending/failed revocations
- `purge_verification_rate` (target 100%)
- revocation SLA target (60 minutes), measured average, and how many runs met it
- active suppression entries
- `privacy_registry_complete`
- current derived-row counts

## Operational notes

- The queue is PostgreSQL-backed (`consent_jobs` with leases and
  `FOR UPDATE SKIP LOCKED`). This fits the self-hosted deployment and avoids an
  Azure Service Bus dependency; the executor seam can be replaced later.
- The scheduler is leader-elected by the existing startup lock, so only one
  worker drains the queue.
- Account erasure still uses `app/services/erasure.py`; Cyber DNA erasure is
  invoked there. Consent revocation is narrower and never deletes completions,
  certificates, achievements, or the account.
- Not yet present in this code tree: AI coach tables, employer share tokens,
  and learner-level research datasets. Their cleanup hooks are registered and
  activate automatically when those tables exist.

## Tests

`tests/test_consent_revocation.py` covers immediate blocking, atomic purge,
mid-purge rollback, ledger-failure rollback, idempotent revoke, re-grant,
suppression replay, restore sweep, scheduled verification, export proof,
educational-record retention, and registry completeness. `tests/test_security_policy.py`
covers self, scoped, shared, read-only auditor, privacy-officer, and
admin-private-default denial.
