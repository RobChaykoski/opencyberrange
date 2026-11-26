# Release 5.55.0 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.55.0` |
| Signed tag | `v5.55.0` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.54.2` |

## Added

| Area | Detail |
|---|---|
| Career-focused catalogue | The Exercises hub shows the tracks aligned with the learner's career target. New learners default to **Cybersecurity Foundations** and learners with fewer than three completions start in the focused view. |
| Career target control | The career-target selector sits on the Exercises hub, so a learner can switch pathway without visiting the profile. The full catalogue remains one click away. |
| Progressive completion | The page marks a pathway complete when every focused track is complete and invites the learner to explore all tracks. The focus is a preference, not a hard lock. |
| Dashboard consistency | The student dashboard's **Track progress** card follows the same career target and links to the focused catalogue. |
| Role catalogue | `GET /api/profile/roles` now exposes each pathway's `tracks` and `categories`, so the hub and dashboard use the same mapping as role readiness. |
| Learner guide | The Exercises hub and dashboard pages document the focus, the career-target selector, and the full-catalogue escape hatch. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `669 passed`, `562 skipped` |
| Frontend tests | `77 passed` (25 files) |
| Frontend lint | `0 errors`; bare-string budget updated for the new learner copy |
| Frontend build | Passed; bundle budget passes |
| Publication audit | `0 findings` |
| Link check | No broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match release `5.55.0` |

## Accessibility and behaviour checks

| Check | Result |
|---|---|
| Focus control | Visible labels and `aria-label` on the scope bar; the career selector has a visible label |
| Default view | New learners see the focused set; returning learners with three or more completions see all tracks |
| Preference persistence | The explicit focus/all choice is stored locally; a career-target change updates both the hub and dashboard |
| Empty focus | If no active track matches the target, the page says so and offers the full catalogue |
| Staff view | Instructors and admins keep the full catalogue and drag-to-reorder handles |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.55.0` | Deployed and verified |
| Production | `5.55.0` | Deployed and verified |

The change is frontend, role-catalogue metadata, and learner documentation. It
has no database migration and does not change lab definitions.
