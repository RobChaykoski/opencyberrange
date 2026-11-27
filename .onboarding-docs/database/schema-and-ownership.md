# Schema and ownership

The schema is organised by bounded context. A table belongs to exactly one
domain; cross-domain reads go through a service, not a join from an unrelated
router.

## Domain groups

| Domain | Representative tables | Owner |
|---|---|---|
| Identity | `users`, `auth_sessions`, `external_identities`, `invite_codes` | Auth |
| Authorization | role and permission tables, break-glass, impersonation | Security |
| Courses | `courses`, `course_enrollments`, `course_lab_assignments`, `course_staff`, `course_feedback` | Curriculum |
| Catalogue | `tracks`, `levels`, `labs` | Curriculum |
| Sessions | `lab_sessions`, `flag_attempts`, `lab_completions` | Lab runtime |
| Practice | `exercise_quiz_attempts`, `exercise_quiz_feedback`, question banks | Curriculum |
| Evidence | `evidence_records`, `evidence_reviews`, `evidence_appeals`, `competency_contract_reviews` | Competency |
| Consent | `consent_states`, `consent_events`, `consent_revocations`, `consent_jobs`, `consent_suppressions` | Privacy |
| Cyber DNA | `dna_evidence_records`, `dna_snapshots`, competency/affinity tables | DNA |
| Analytics | `activity_events`, snapshots, readiness, achievements | Analytics |
| Security | `security_events`, audit, break-glass, service identities | Security |
| Integrations | identity providers, LTI registrations, settings | Integrations |
| Platform | `platform_settings`, retention jobs, production cutovers | Platform |
| Integrity | `data_integrity_ledger` | Database |

The generated [data dictionary](../../docs/DATA-DICTIONARY.md) lists every table
and column. `scripts/check-data-dictionary.py` fails if a model table is missing
from it.

## Tenant isolation

- Tenant-scoped tables carry `institution_id`.
- RLS is enabled on protected tables.
- The session's institution is the source; never a client header.
- The platform admin is the only cross-tenant role, and private data still
  requires break-glass.
- `scripts/check-tenant-isolation.py` proves the boundary on development.

## Append-only tables

| Table | Rule |
|---|---|
| `evidence_records` | never overwrite; add a record or a review |
| `security_events` | runtime role cannot update or delete |
| `data_integrity_ledger` | immutable trigger; hash chain |
| `consent_suppressions` | append-only proof of deletion |
| `dna_snapshots` | immutable snapshot |

## Naming and keys

- Integer surrogate primary keys.
- Unique natural keys where the domain requires them (`users.username`,
  `users.email`, `labs.slug`).
- `ON DELETE CASCADE` for learner-owned rows; `SET NULL` for actor references
  that must survive account deletion.
- Timestamps are UTC.
- JSON columns are validated on write and checked by the quality audit.

## Changing the schema

1. Update the SQLAlchemy model.
2. Add an Alembic migration.
3. Update the data dictionary.
4. Add a test for the constraint and the tenant boundary.
5. Run the Alembic safety check and the DB invariants.
6. Do not use `--autogenerate` blindly; the repository guards the revision graph.

## Related

- [Migrations](migrations.md)
- [Database integrity](../../docs/DATABASE-INTEGRITY.md)
- [Tenant isolation status](../../docs/TENANT-ISOLATION-STATUS.md)
- [Data classification](../../docs/DATA-CLASSIFICATION.md)
