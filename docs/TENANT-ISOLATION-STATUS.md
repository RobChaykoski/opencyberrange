# Tenant isolation status

The Authorization Service is the first tenant check. PostgreSQL row-level
security is the database backstop for learner-owned records. This page records
what is enforced and what remains.

The current deployment is the **Community / Academic** edition (`lite`,
single-host): it runs with one `default` institution, so the RLS backstop is
transparent to normal use. The backstop is edition-agnostic; multi-tenant
Enterprise operation remains deferred past Release 5.

## Enforced with tenant columns, derivation triggers, and forced RLS

`platform/backend/app/services/tenant_rls.py`, applied by migration
`0041_tenant_rls_legacy` and at startup:

**Original set (0035)**

- `courses`
- `course_enrollments`
- `lab_sessions`
- `lab_completions`
- `achievements`
- `learner_snapshots`
- `portfolio_share_tokens`
- `dna_evidence_records`
- `dna_snapshots`

**Legacy learner tables (0041)**

- `flag_attempts`
- `review_requests`
- `survey_responses`
- `user_accommodations`
- `accommodation_events`
- `exercise_quiz_attempts`
- `exercise_quiz_feedback`
- `exercise_reactions`
- `exercise_pulse_surveys`
- `course_feedback`
- `course_completion_resets`
- `course_cohort_members`
- `quiz_attempts`
- `open_badge_credentials`
- `lti_scores`
- `activity_events`

That is **25 tables**. The tenant is derived from the owning user or course by a
trigger; a client cannot choose `institution_id`. Background jobs run as the
system principal, an unauthenticated request sees only the default institution,
and administrators run in system mode. A regression test asserts the column,
forced RLS, and all four policies on every table, and probes two newly migrated
tables from two institutions.

## Deliberately not RLS-scoped

These are classified rather than forgotten. Applying tenant RLS to them would
break authentication or remove a global security control.

| Family | Tables | Why |
|---|---|---|
| Authentication and identity | `auth_sessions`, `refresh_tokens`, `revoked_tokens`, `sso_sessions`, `sso_login_tickets`, `external_identities`, `rbac_user_roles`, `service_credentials`, `instructor_api_keys`, `wireguard_configs` | Read *before* a tenant context exists; the tenant is resolved from them. Protected by token, role, and secret handling. |
| Security and platform operations | `security_events`, `data_integrity_ledger`, `production_cutovers`, `settings_change_requests`, `retention_runs`, `break_glass_grants`, `impersonation_sessions` | Global by design. `security_events` has its own forced RLS and append-only policies. |
| Consent subsystem | `consent_states`, `consent_events`, `consent_audits`, `consent_jobs`, `consent_revocations`, `consent_suppressions`, `survey_consent_events` | Learner-owned, but the consent gate runs during onboarding and sign-in while the tenant is being established. Already protected by the revocation orchestrator, suppression ledger, and erasure path. Candidate for the next RLS wave after the consent read path is tenant-stamped. |
| Course-owned content | `course_cohorts`, `course_lab_assignments`, `course_requirements`, `survey_attachments`, `exercise_sets`, `report_exports` | Institution-owned rather than learner-personal; scoped by the course in services. A later migration can derive `institution_id` from `course_id`. |
| Shared definitions | `labs`, `competitions`, `exercise_templates`, `surveys` | Platform-wide catalogue or shared content; not personal data. Competition participation is learner-owned and already covered through `competition_participants` scoping at the service layer. |

## Required next migration

For the remaining course-owned content:

1. Add `institution_id` derived from `course_id` (no user owner required).
2. Backfill, then set `NOT NULL`.
3. Enable and force RLS with the tenant policy.
4. Extend the two-institution probe test.

For the consent subsystem, first stamp the tenant before the onboarding/sign-in
consent reads, then apply the same pattern.

## Verification

```bash
cd platform/backend
pytest -q tests/test_tenant_rls.py tests/test_horizontal_privilege.py tests/test_idor_matrix.py
```

`tests/test_tenant_rls.py` checks every enforced table for the column, forced
RLS, and the four policies, and proves cross-tenant `SELECT`/`DELETE` denial on
newly migrated learner tables.
