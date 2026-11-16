# Tenant isolation status

The Authorization Service is the first tenant check. PostgreSQL row-level
security is the database backstop for learner-owned records. This page records
what is enforced and what remains.

## Enforced with tenant columns, derivation triggers, and forced RLS

`platform/backend/app/services/tenant_rls.py` covers:

- `courses`
- `course_enrollments`
- `lab_sessions`
- `lab_completions`
- `achievements`
- `learner_snapshots`
- `portfolio_share_tokens`
- `dna_evidence_records`
- `dna_snapshots`

The tenant is derived from the owning user or course by a trigger. A client
cannot choose `institution_id`. Background jobs run as the system principal;
an unauthenticated HTTP request sees only the default institution.

## Service-layer scoping without tenant RLS

The following families are scoped in the service or router, but are not yet in
the forced-RLS list. They need a migration and a two-tenant regression test
before this page can call tenant isolation complete:

- `flag_attempts`
- `activity_events`
- `review_requests`
- `accommodations`
- `survey_responses` and survey definitions
- certificate and achievement evidence tables not covered above
- `security_events`, `audit_logs`, and break-glass records
- any optional AI, research, or analytics table that stores a `user_id`

Some of these are deliberately global (platform settings, shared lab content,
security operations). Global is not the same as unscoped learner data. The
review must classify each table as global, institution-owned, or user-owned.

## Required next migration

1. Classify every remaining table by ownership.
2. Add `institution_id` with a derivation trigger for user/course-owned rows.
3. Backfill from the owner, then set `NOT NULL`.
4. Enable and force RLS with the tenant policy.
5. Add a two-institution test that proves cross-tenant `SELECT`, `UPDATE`, and
   `DELETE` are blocked.
6. Add the table to the privacy/erasure registry if it holds learner data.
7. Record the migration and test in the release evidence.

Until that migration lands, this page must not be read as a claim that every
tenant-owned table is protected by database RLS.

## Verification

```bash
cd platform/backend
pytest -q tests/test_tenant_rls.py tests/test_horizontal_privilege.py tests/test_idor_matrix.py
```

The current tests cover the enforced tables and the high-risk object families.
They do not replace the missing migration for the tables listed above.
