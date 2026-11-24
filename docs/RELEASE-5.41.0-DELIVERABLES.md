# Release 5.41.0 deliverables

Status: **released and deployed** to development and production on 24 November
2026.

| Item | Value |
|---|---|
| Version | `5.41.0` |
| Signed tag | `v5.41.0` |
| Release commit | `c8ca2ca5` |
| Alembic | `0060_competency_reviews` |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a passed restore drill |

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
| Backend tests | `1,164 passed` |
| Frontend build and tests | Build passed; `35` component tests passed |
| Quality checks | Green |
| Supply-chain lock | Verified with the release key |
| Production `/api/version` | `5.41.0` |
| Production health | `200` |
| Alembic on production | `0060_competency_reviews (head)` |
| Public version and health | `5.41.0` and `200` |
| Existing routes | `/journey`, `/impact`, `/practice`, `/my-evidence`, `/evidence-review`, `/contract-review` return `200` |
| Review API | `/api/competency-reviews/catalogue` is gated (`401` unauthenticated) |
| SSO | Authentik OIDC provider present; `sso_enabled` true |
| Restore drill | 69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events |
| Rollback images | `opencyberrange-backend:pre-v5.41.0`, `ocr-frontend:pre-v5.41.0` |

## Known limitations

- The embedded lab target still sends `frame-ancestors 'self'`, so a lab whose
  own web server sets that header remains usable through **Open in new tab**, not
  inside the SPA frame. Changing that requires the lab target's own headers or a
  platform-origin proxy.
- The review export is still an operator step. The signed-review manifest and its
  CI gate are the next slice and are not part of this release.
- The workbook popup refreshes the wiki cookie after opening the window. On a
  slow connection the wiki can briefly land on the SPA login before the cookie
  is present. The next slice will open a blank window and navigate after the
  cookie is set.
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

- [x] Signed tag and verified supply-chain lock.
- [x] Migration `0060` applied on development and production.
- [x] Production health, version, SSO, and public routes verified.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill passed.
- [x] Rollback images retained.
- [x] Manual and API reference regenerated.
- [x] Coverage audit passes structurally.
- [x] Test suite and component regression test pass.
