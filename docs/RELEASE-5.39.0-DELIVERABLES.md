# Release 5.39.0 deliverables

Status: **released and deployed** to development and production on 24 November
2026.

| Item | Value |
|---|---|
| Version | `5.39.0` |
| Signed tag | `v5.39.0` |
| Release commit | `6b25be9b` |
| Alembic | `0058_practice_sessions` |
| Production | Deployed and verified |
| Development | Deployed and verified |
| Supply-chain lock | Refreshed and signed with the release key |
| Backups | Pre-deploy and post-deploy dumps, plus a passed restore drill |

## Learner deliverables

| Deliverable | What it does | Where |
|---|---|---|
| My Evidence | Lists the learner's evidence, review state, reviewer notes, and appeals | `/my-evidence` |
| Evidence appeals | One second review of a rejected record; acceptance returns it to `in_review` | Evidence API |
| Your Journey | Mission cards, eight traditions, and the Living Archive observation | `/journey` |
| Your Impact | Contribution ledger, Legacy Score, Meaning Index, stewardship band, historical markers | `/impact` |
| Living Archive | Infers a tradition from verified contribution; never asks the learner to declare one | `/journey`, `/api/archive/me` |
| Recognition | Earned markers, clue-only secrets, sealed achievements, rotating whisper | `/impact` |
| Practice exams | Timed mock exams and domain drills with review and progress | `/practice` |
| Workbook answers | Saves each distinct answer version into the evidence ledger | `/workbook-answers` |

## Instructor and administrator deliverables

| Deliverable | What it does | Where |
|---|---|---|
| Evidence review | Queue, rubric criteria, prior decisions, accept / more evidence / reject | `/evidence-review` |
| Appeal queue | Accept or reject a learner appeal with notes | `/evidence-review` |
| Evidence operations summary | Status totals, backlog age, source/rubric mix, strongest/weakest competencies, documentation coverage, confidence trend, accepted rate | `/evidence-review` |
| Recognition awards | Audited manual award with an evidence reference and note | `/api/recognition` |
| Contribution verification | Verify, rate, set reach, reject with notes | `/api/impact` |
| Practice configuration | Per-pathway exam size, duration, and pass mark | Question bank |
| Question-bank coverage | Per-domain counts and thin-domain highlight | Admin question banks |

## Content deliverables

| Deliverable | Count |
|---|---:|
| Reviewed certification pathways | 9 |
| Original question-bank items | 158 |
| New items in 5.39.0 | 30 |
| Versioned rubrics | 5 |
| Lab competency contracts | 215 |
| Public reference URLs | 115 |

## Platform and data deliverables

| Deliverable | Detail |
|---|---|
| Migrations | `0054_evidence_appeals`, `0055_learner_journeys`, `0056_impact_ledger`, `0057_achievement_awards`, `0058_practice_sessions` |
| Tenant isolation | Forced RLS on the new learner and recognition tables |
| Answer-key protection | Correct answers and explanations withheld until submission |
| Practice privacy | Self-only sessions; another learner receives `404` |
| Recognition safety | No learner ranking; secret triggers never returned before earning |
| Analytics suppression | No aggregate below five learners for non-admin reviewers |
| No guest practice | Authenticated and self-only by design |

## Documentation deliverables

- `CHANGELOG.md` — 5.39.0 release section.
- `docs/RELEASES.md` — signed tag and deployment record.
- `docs/PRODUCTION-DEPLOYMENT-STATEMENT.md` — release identity, verification, backups.
- `docs/BACKUP-RESTORE-TEST.md` — 5.39.0 restore drill evidence.
- `docs/API-ERROR-CODES.md` — evidence, impact, recognition, practice, and capstone codes.
- `docs/DATA-DICTIONARY.md` — every new table and the deletion outcome.
- `docs/TENANT-ISOLATION-STATUS.md` — 39 tenant tables.
- `docs/RELEASE-6-SCOPE.md` — Release 6 status and critical path.
- `docs/LIVING-ARCHIVE.md`, `docs/IMPACT-AND-LEGACY.md`, `docs/ACHIEVEMENTS.md`, `docs/IDENTITY-QUESTS.md`, `docs/FOUNDATIONS.md`.
- `docs/PRACTICE-EXAMS.md`, `docs/CERTIFICATION-QUESTION-BANKS.md`.
- `Manual-Lite/` — My Evidence, Your Journey, Your Impact, Recognition, The Traditions, Practice Exams, Recognition Awards, and the regenerated API reference.

## Verification evidence

| Check | Result |
|---|---|
| CI | Green |
| Quality checks | Green |
| CodeQL | Green |
| Trivy | Green |
| Security delta | Green |
| Supply-chain lock | Verified with the release key |
| Production `/api/version` | `5.39.0` |
| Production health | `200` |
| Alembic on production | `0058_practice_sessions (head)` |
| Public routes | `/journey`, `/impact`, `/practice`, `/my-evidence`, `/evidence-review` return `200` |
| SSO | Authentik OIDC present; `sso_enabled` true |
| Restore drill | 69 users, 215 labs, 2 courses, 64 enrollments, 134 completions, 497 achievements, 1,575 activity events |
| Rollback images | `pre-5.39.0` backend and frontend tags retained |

## Not in 5.39.0

These are post-release `5.40` development work, not part of the signed tag:

- Release 6 coverage audit and the CI `--fail-on-gaps` gate.
- Competency mappings for the nine quiz pathways.
- Learner-visible "unmeasured" rule in DNA, portfolio, and readiness views.
- Competency review packet generator and guide.
- Deterministic capstone planner and validation API.
- The 190 pending competency contract reviews.

## Acceptance checklist

- [x] Signed tag and verified supply-chain lock.
- [x] Migrations applied on development and production.
- [x] Production health and version verified.
- [x] Pre-deploy and post-deploy backups.
- [x] Restore drill passed.
- [x] Rollback images retained.
- [x] Manual and API reference regenerated.
- [x] Development smoke test for journeys, impact, archive, recognition, and practice.
- [x] CI, Quality, CodeQL, Trivy, and Security delta green.
