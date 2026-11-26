# Release 5.52.0 deliverables

Status: **release prepared; deployment verification pending.**

| Item | Value |
|---|---|
| Version | `5.52.0` |
| Signed tag | `v5.52.0` |
| Release date | 25 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.51.2` |

## Changed

| Area | Detail |
|---|---|
| Exercise knowledge check | One question at a time with numbered jump buttons, **Previous question**, **Next question**, answered count, last-question reminder, a separate **Submit knowledge check** panel, unanswered warning, and confirmation. |
| Level quiz | The same navigation and submission pattern. The final action is **Submit quiz for certificate**, and the warning/confirmation make it clear that the score can be recorded for the level certificate. |
| Shared UI | Added `QuizQuestionDots`, `QuizNavigation`, and `QuizSubmitPanel` so the three quiz surfaces cannot drift again. |
| Accessibility | Current-question state, answered-state labels, visible focus, native radio inputs, polite progress announcements, and mobile stacking. |
| Documentation | Added the student guide page **Knowledge Checks and Level Quizzes**, updated the README, changelog, SECURITY supported versions, LICENSING release status, release index, and deployment runbook. |

## Verification

| Check | Result |
|---|---|
| Frontend tests | `56 passed` (21 files) |
| New quiz component tests | Navigation, jump state, answered state, warning, confirmation, and cancel |
| Frontend lint | `0 errors` |
| Frontend build | Passed |
| UI string budget | Passed |
| Link check | `1,220` Markdown files, no broken links |
| Browser smoke | Knowledge check verified at desktop and mobile widths; no console or page errors |
| Backend tests | `637 passed`, `559 skipped` (DB-backed tests need `TEST_DATABASE_URL`) |
| Supply-chain lock | Updated and signed |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.0` | Pending |
| Production | `5.52.0` | Pending |

Post-deploy checks: `/api/version` on both hosts, nginx test, backend/frontend health, registered labs, and pre/post backups.
