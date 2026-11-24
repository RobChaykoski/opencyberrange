# Release 5.40.0 deliverables

Status: **released and deployed** to development and production on 24 November
2026.

| Item | Value |
|---|---|
| Version | `5.40.0` |
| Signed tag | `v5.40.0` |
| Release commit | `9e227983` |
| Alembic | `0059_capstone_plans` |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a passed restore drill |

## Release 6 foundation

| Deliverable | What it does | Where |
|---|---|---|
| Coverage audit | Checks 215 lab contracts, 9 quiz pathways, 14 exercise quizzes, capstones, and badges | `scripts/audit-release6-coverage.py` |
| CI coverage gate | Fails on a structural mapping gap | `.github/workflows/quality.yml` |
| Quiz competency mappings | Every certification pathway declares a competency list | Question bank |
| Learner-visible rule | A null score renders as **unmeasured**, never `0` | DNA, portfolio, readiness, taxonomy |
| Unmeasured regression test | Rejects `0/99` for a null overall score | `CareerAtlas.test.js` |
| Review packets | Per-track contract packet with taxonomy names, weights, and checklist | `scripts/competency-review-packet.py` |
| Review guide | Records decisions in `competency-contract-overrides.yaml`, not the generated contract | `docs/COMPETENCY-REVIEW-GUIDE.md` |
| Admin coverage | Per-domain question counts and thin-domain highlight | Admin question banks |

## Capstone Builder

| Deliverable | What it does | Where |
|---|---|---|
| Role profiles | 13 profiles with critical competencies, tracks, and capstone briefs | `GET /api/capstones/profiles` |
| Deterministic planner | Greedy weighted set cover over reviewed contracts, with prerequisite ordering | `POST /api/capstones/plan` |
| Validation gate | Coverage, workload, weights, objective evidence, prerequisites, waivers | Plan response |
| Saved plans | Draft persistence with owner scope and version | `POST /api/capstones/plans` |
| Plan history | List and read saved plans | `GET /api/capstones/plans` |
| Versioned edit | Rebuild, increment version, reset to draft, clear approval | `PUT /api/capstones/plans/{id}` |
| Approval gate | Approve only when the validation gate passes | `POST /api/capstones/plans/{id}/approve` |
| Archive | Retire a plan without deleting it | `POST /api/capstones/plans/{id}/archive` |

The planner is honest about the current curriculum. `soc-analyst` has 29
critical competencies; the matching contracts cover about half. A waived,
12-hour plan with 9 labs and an assumed entry level passes the gate. An
unwaived 40-hour plan does not.

## Platform and data

| Deliverable | Detail |
|---|---|
| Migration | `0059_capstone_plans` |
| Tenant isolation | Forced RLS with four policies on `capstone_plans` |
| Plan privacy | Owner-scoped; another instructor receives `404` |
| No auto-publish | Approval does not publish a course or expose a learner record |

## Verification

| Check | Result |
|---|---|
| CI | Green |
| Quality checks | Green |
| CodeQL | Green |
| Trivy | Green |
| Security delta | Green |
| Supply-chain lock | Verified with the release key |
| Production `/api/version` | `5.40.0` |
| Production health | `200` |
| Alembic on production | `0059_capstone_plans (head)` |
| Public version | `5.40.0` |
| Public health | `200` |
| Existing routes | `/journey`, `/impact`, `/practice`, `/my-evidence`, `/evidence-review` return `200` |
| Capstone API | Gated (`401` unauthenticated) |
| SSO | Authentik OIDC present; `sso_enabled` true |
| Restore drill | 69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events |
| Rollback images | `pre-5.40.0` backend and frontend tags retained |

## Not in 5.40.0

- Capstone editor UI and publication to a course.
- The six instructor dashboards from 6.1.
- HA/Kubernetes, federation, AI Mentor, and localization.
- The 190 pending competency contract reviews. The review campaign is in
  progress and is the 6.0 gate.

## Acceptance checklist

- [x] Signed tag and verified supply-chain lock.
- [x] Migration `0059` applied on development and production.
- [x] Production health, version, SSO, and public routes verified.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill passed.
- [x] Rollback images retained.
- [x] Manual and API reference regenerated.
- [x] Coverage audit passes structurally.
- [x] Test suite and component regression test pass.
