# Release 5.55.1 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.55.1` |
| Signed tag | `v5.55.1` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.55.0` |

## Changed

| Area | Detail |
|---|---|
| URL-backed focus | The Exercises hub keeps `view` and `target` in the URL (`?view=focused&target=...` or `?view=all`). Refresh, shared links, and back/forward restore the same focus. |
| Server-side narrowing | `GET /api/exercises/tracks` accepts an optional `role` career-pathway id and returns only the tracks visible to that learner and aligned with the pathway. |
| Scope count | The response includes `total_tracks`, so the focused page shows "X of Y" without downloading every track. |
| Least privilege | The pathway filter is applied after the existing visibility and course-assignment checks. It can only narrow the result, never add a hidden or unavailable track. An unknown pathway returns an empty focused list, and the UI offers the full catalogue. |
| Dashboard | The student dashboard's **Track progress** card follows the same career target and links to the focused catalogue. |
| API manual | The tracks endpoint documents the optional `role` query parameter. |
| Catalogue cleanup | The role catalogue exposes the `tracks` mapping needed by the catalogue and no longer carries the unused `categories` field. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `670 passed`, `562 skipped` |
| Frontend tests | `77 passed` (25 files) |
| Frontend lint | `0 errors`; bare-string budget passes |
| Frontend build | Passed; bundle budget passes |
| Publication audit | `0 findings` |
| Link check | No broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match release `5.55.1` |

## Least-privilege and loading checks

| Check | Result |
|---|---|
| Available tracks | The backend still starts from `_is_lab_visible()` and the course-assignment access set; role filtering runs afterward. |
| Hidden track test | An unknown or unowned pathway returns no focused tracks; it cannot widen the response. |
| Focused request | The browser sends `role=<selected-pathway>` only in the focused view; `view=all` sends no role filter. |
| Full catalogue | The full catalogue is still one request away and remains the same visible set as before. |
| Route restore | Changing the target or view updates the URL with `router.replace`, so reload and history work without adding duplicate entries. |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.55.1` | Deployed and verified |
| Production | `5.55.1` | Deployed and verified |

The change is frontend routing, the tracks query filter, role-catalogue
metadata, and documentation. It has no database migration and does not change
lab definitions.
