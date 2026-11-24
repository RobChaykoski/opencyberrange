# Release 5.49.0 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.49.0` |
| Signed tag | `v5.49.0` |
| Release commit | Pending tag |
| Alembic | `0067_course_content_rls` |
| Production | Pending |
| Development | Deployed and verified: `0067`, drift `0` |
| Supply-chain lock | Refreshed and signed with the release key |

## Course-owned RLS

| Deliverable | Detail |
|---|---|
| Migration | `0067_course_content_rls` adds `institution_id`, derives it from `course_id`, sets `NOT NULL`, and creates the index |
| Tables | `course_cohorts`, `course_lab_assignments`, `course_requirements`, `survey_attachments`, `exercise_sets`, `report_exports` |
| Policies | Forced RLS with select, insert, update, and delete tenant policies |
| Derivation | Course-only trigger: no user owner and no client-chosen tenant |
| Enforcement set | `41` → **`47`** tables |
| Test | Two-institution probe extended to a course-owned table |
| Docs | Auth family confirmed as deliberately outside RLS; consent subsystem recorded as the next wave |

## Verification

| Check | Result |
|---|---|
| Backend tests | `1,196 passed` |
| Tenant/IDOR suites | `18 passed` |
| Alembic safety guard | Single head `0067_course_content_rls` |
| Development drift | `0` operations |
| Development RLS | Forced RLS on all six new tables |
| Development nulls | `0` |
| Production drift | Pending |
| Restore-drift gate | Pending at `0` |
| Production health | Pending |
| Rollback images | Pending |

## Known limitations

- Auth tables remain outside RLS by design: they are read before a tenant
  context exists.
- Consent tables are the next RLS wave; the consent read path must be
  tenant-stamped first.
- Multi-tenant operation stays deferred until the consent wave is complete and
  a two-tenant pilot passes.
- The 25 legacy and 190 pending contracts still need subject-matter sign-off.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] CI integrity gate passes on the release commit.
- [ ] Production migration reaches `0067_course_content_rls`.
- [ ] Production drift is `0`.
- [ ] All six tables have forced RLS and no null tenant values.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill and restore-drift gate at `0` passed.
- [ ] Rollback images retained.
