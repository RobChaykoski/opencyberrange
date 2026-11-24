# Two-tenant pilot

Purpose: prove that a second institution is isolated in practice before any
multi-tenant claim, without changing the single-tenant production default.

This is a **pilot**, not a supported multi-tenant edition. It runs against a
signed release, with a backup and a named owner.

## What it proves

- The 47 tenant tables hide another institution's rows.
- Course-owned content derives its tenant from the course.
- Shared catalogue content (labs, competitions, framework data) remains visible.
- Admin screens scope to the actor's institution.

## What it does not prove

- Authentication tables are outside RLS by design; they are protected by token,
  role, and secret handling.
- The consent tables are not yet tenant-scoped. Do not run cross-tenant consent
  or erasure flows during the pilot.
- HA, cross-region failover, and per-tenant quotas are out of scope.
- There is no institution registry table. `institution_id` is a lower-case string
  convention of at most 64 characters, for example `pilot-b`.

## Preconditions

1. Development and production are on the same signed tag and `alembic check`
   reports `0`.
2. `scripts/check-tenant-isolation.py` passes on both hosts (see below).
3. A fresh production backup exists.
4. A named pilot owner and a maintenance window are recorded.

## Setup

1. As a **platform admin**, open Admin → Users and create the tenant B
   instructor with `institution_id = pilot-b`. Only a platform admin can create
   a user in a different institution; an institution admin is restricted to its
   own.
2. Sign in as the instructor and create **Course B**. The course tenant is taken
   from the instructor.
3. As the platform admin, create the tenant B learner with
   `institution_id = pilot-b`.
4. As the instructor, enroll the learner in Course B and create one of each
   course-owned object: a cohort, a lab assignment, a requirement, an exercise
   set, a survey attachment, and a report export.
5. As the learner, start one lab and submit one quiz or evidence item.
6. Use or create a `default`-institution course, learner, and enrollment as the
   comparison set.

## Validation

Run the control audit inside the backend container. It checks the column,
index, forced RLS, four policies, and derivation trigger on all 47 tables, then
queries every table as a foreign tenant that owns nothing.

```bash
docker exec -i ocr-backend python - < scripts/check-tenant-isolation.py
```

Expected:

```text
tenant tables: 47
role: superuser=False bypassrls=False
probe: tenant __isolation_probe__, 0 table(s) leaked
PASSED: tenant controls and cross-tenant probe
```

Then check the product:

| Check | Expected |
|---|---|
| Learner A opens Course B by URL | `403` or `404`, never the course |
| Learner B opens Course A by URL | `403` or `404` |
| Learner A lists courses | Only `default` courses |
| Instructor A lists users | Only `default` users |
| Institution admin B lists courses/users | Only `pilot-b` |
| Platform admin lists users | Both institutions |
| Both learners open the lab catalogue | Shared catalogue visible |
| Learner B starts a lab | Session tenant is `pilot-b` |
| Report export from Course B | Visible only to `pilot-b` staff |

Database spot checks:

```sql
select institution_id, count(*) from course_enrollments group by 1;
select institution_id, count(*) from lab_sessions group by 1;
select count(*) from course_cohorts where institution_id is null;
```

## Rollback

1. Deactivate the `pilot-b` users.
2. Delete Course B; its cohorts, assignments, requirements, exercise sets, and
   exports cascade.
3. Keep the audit and security events; do not delete log evidence.
4. If any cross-tenant read or write appears, restore the pre-pilot backup and
   stop the pilot.

## Acceptance record

| Item | Value |
|---|---|
| Pilot owner | |
| Institution id | `pilot-b` |
| Release / tag | |
| Pre-pilot backup | |
| Audit result | |
| Product checks | |
| Date | |
| Decision | |
