# ADR 0010: Consent-subsystem tenant RLS

Status: **proposed; gated on the two-tenant pilot**
Date: 24 November 2026

## Context

The consent subsystem is outside the tenant RLS backstop:

- `consent_states`
- `consent_events`
- `consent_revocations`
- `consent_jobs`
- `consent_audits`
- `consent_suppressions`
- `survey_consent_events`

These rows are created and read while a learner is signing in, onboarding, or
exercising a consent-gated feature. The current controls are the consent service,
the revocation orchestrator, the suppression ledger, and the erasure hooks. They
are row-scoped in code, not by PostgreSQL.

Production data review on 24 November 2026: `18` consent states, `18` consent
events, `5` survey consent events, and no null `user_id` values. The other tables
are empty. The data is ready for a tenant backfill.

## Decision

Scope the consent subsystem to the tenant **after** the two-tenant pilot
validates the current 47-table backstop, and only with the pre-read stamping
below. Do not enable consent RLS ahead of the pilot, because the pilot must test
a stable target.

### Pre-read stamping

The consent middleware already decodes the token and loads the user before it
reads consent. It will stamp the tenant from that user before the consent query:

```python
set_tenant(user.institution_id, system_admin=False)
```

The request then continues with the same tenant, which is correct because the
consent gate only applies to authenticated feature APIs.

Paths that create consent during registration must stamp from the newly created
user row before the first consent write. Background consent jobs run as the
system principal and keep `system_admin` true.

### Derivation

| Table | Derivation |
|---|---|
| `consent_states` | `user_id` → `users.institution_id` |
| `consent_events` | `user_id` → `users.institution_id` |
| `consent_revocations` | `user_id` → `users.institution_id` |
| `consent_jobs` | `user_id` → `users.institution_id` |
| `consent_audits` | `user_id` → `users.institution_id`, fallback `default` |
| `consent_suppressions` | `user_id` → `users.institution_id`; subject-only rows are platform-global |
| `survey_consent_events` | `user_id` → `users.institution_id` |

`consent_suppressions` is the one open question. A suppression may exist only as
a `subject_hash` after account erasure, with no `user_id`. The ADR proposes
treating those rows as platform-global (`institution_id = 'default'`) and
documenting that a suppression is not tenant-scoped once the account is gone.
The alternative - deleting suppressions on erasure - defeats their purpose.

### Migration shape

`0068_consent_rls`:

1. Add `institution_id` (nullable) and the index to each table.
2. Backfill from `users`; use `default` only for subject-only suppressions and
   audits with no user.
3. Set `NOT NULL` and the `default` server default.
4. Add the derivation trigger.
5. Enable and force RLS with the four tenant policies.

The runtime `tenant_rls` map gains the same tables, so a fresh restore and the
startup reconciliation agree.

### Tests

- Extend `scripts/check-tenant-isolation.py`; the enforced count becomes 54.
- Extend the two-institution probe with a consent state, a survey consent event,
  and a suppression that is intentionally subject-only.
- Add a middleware test: a gated request stamps the tenant before the consent
  read, and a request for another tenant's consent returns `ConsentRequired` or
  `404` without leaking the row.
- Add a background-job test: the job runs as system and can still read every
  tenant's consent for retention work.

## Consequences

- The consent subsystem joins the same backstop as learner data.
- The pilot must be complete first, so the target does not move during testing.
- Subject-only suppressions remain a documented exception.
- Multi-tenant operation is still deferred until the pilot and this wave both
  pass, and a two-tenant acceptance record is signed.
