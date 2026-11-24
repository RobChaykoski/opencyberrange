# Release 5.41.0 deliverables

Status: **release prepared; deployment pending** on 24 November 2026.

| Item | Value |
|---|---|
| Version | `5.41.0` |
| Signed tag | `v5.41.0` |
| Release commit | Pending tag |
| Alembic | `0060_competency_reviews` |
| Production | Pending |
| Development | Pending |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a restore drill |

## Contract review operations

| Deliverable | What it does | Where |
|---|---|---|
| Review dashboard | Queue, status chips, search, and status filters | `/contract-review` |
| Contract detail | Current contract, last signed review, history, and hashes | `GET /api/competency-reviews/{lab_slug}` |
| Competency editor | Taxonomy picker with explicit weights that must total 1.00 | Review form |
| Evidence editor | Evidence type, weight, source, and validation per item | Review form |
| Reliability and criteria | Level, score, completeness, determinism, validation, and rationale | Review form |
| Cycle selector | 6, 12, or 24 months, defaulting to 12 | Review form |
| Attestation | The reviewer confirms they inspected the exercise, workbook, and evidence | Sign-off |
| Sign-off | Approve or request changes; the signature records the contract, lab, and taxonomy hashes | `POST /api/competency-reviews/{lab_slug}/sign` |
| Draft ownership | One reviewer owns a draft; another reviewer cannot overwrite it | Service guard |
| Export-ready panel | Administrators see approved reviews waiting for export | `/contract-review` |
| Catalogue endpoint | Taxonomy domains, competencies, evidence types, and cycle lengths | `GET /api/competency-reviews/catalogue` |
| Migration | Tenant-scoped reviews, one active signed review per institution and lab, immutable signatures | `0060_competency_reviews` |

The review records a decision. It does not edit the generated contract file. An
administrator still exports approved reviews into
`competency-contract-overrides.yaml`, regenerates the contracts, and signs the
supply-chain lock.

## Evidence reporting

| Deliverable | Detail |
|---|---|
| Minor exclusion | Non-admin analytics exclude learners recorded as minors |
| Superseded exclusion | Superseded evidence is not counted |
| Decision denominator | Acceptance is accepted-of-decided, not accepted-of-all |
| Suppression | Suppressed rates return null, never zero |
| Cohort floor | Weakest and strongest competency slices require at least five learners |
| Learner filter | The review queue accepts an optional `learner_id` without changing its oldest-first order |
| Decision flow | A successful decision clears the prior error and advances the workbench |

## Security and reliability

| Deliverable | Detail |
|---|---|
| Frame policy | The SPA document, HTTPS server, and shared header snippet agree on `frame-src` for dynamic lab targets; the workbook stays pinned to `:8443` |
| Shared-VM console | Neutral placeholder and an explicit manual-close fallback |
| Revocation policy | The docstring now matches the fail-closed behaviour |
| WebSocket tickets | Expiry converts aware timestamps instead of replacing the offset |
| Login streaks | Awards retry on deadlock |
| Completion ordering | A deterministic tie-breaker prevents unstable recent lists |

## Verification

| Check | Result |
|---|---|
| Backend tests | Pending |
| Frontend build and tests | Pending |
| Quality checks | Pending |
| Supply-chain lock | Pending |
| Production `/api/version` | Pending |
| Production health | Pending |
| Alembic on production | Pending |
| Public version and health | Pending |
| Existing routes | Pending |
| Review API | Pending |
| SSO | Pending |
| Restore drill | Pending |
| Rollback images | Pending |

## Known limitations

- The embedded lab target still sends `frame-ancestors 'self'`, so a lab whose
  own web server sets that header remains usable through **Open in new tab**, not
  inside the SPA frame. Changing that requires the lab target's own headers or a
  platform-origin proxy.
- The review export is still an operator step. The signed-review manifest and its
  CI gate are the next slice and are not part of this release.
- 190 competency contracts remain baseline-derived. Subject-matter review is the
  Release 6.0 gate.

## Not in 5.41.0

- The signed-review export manifest and CI consistency gate.
- A learner-visible contract-status gate.
- The dean aggregate review view.
- Track assignment, due-date notification, and escalation.
- Reauthentication and MFA before sign-off.
- The 190 pending competency contract reviews.

## Acceptance checklist

- [ ] Signed tag and verified supply-chain lock.
- [ ] Migration `0060` applied on development and production.
- [ ] Production health, version, SSO, and public routes verified.
- [ ] Pre-deploy and post-deploy backups.
- [ ] Restore drill passed.
- [ ] Rollback images retained.
- [ ] Manual and API reference regenerated.
- [ ] Coverage audit passes structurally.
- [ ] Test suite and component regression test pass.
