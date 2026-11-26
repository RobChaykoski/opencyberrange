# Release 5.52.3 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.52.3` |
| Signed tag | `v5.52.3` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.52.2` |

## Fixed and changed

| Area | Detail |
|---|---|
| Warning text contrast | Added `--warning-text` to the dark, light, and high-contrast themes. The learning-analytics early-signal note and the intermediate track tag now meet 4.5:1 instead of 2.91:1 on the light theme. |
| Heading order | Track cards on the Exercises page are `h2` under the page `h1`; the previous `h3` skipped a level. |
| Review evidence | Captured desktop and mobile screenshots for administrator, instructor, and student roles under `ui-review-artifacts/2026-11-26/`, with a machine-readable check log. |

## Three-role accessibility pass

Three scoped review accounts were created on production (`review-admin`,
`review-instructor`, `review-student`) and signed in through the API. The pass
loaded the role dashboard, the role-specific work page, and the profile at
1440×900 and 390×844.

| Check | Result |
|---|---|
| Horizontal overflow | No overflow at either width |
| Visible focus ring | Present on every page for the first tabbable controls |
| Table header scope | Every `<th>` in the admin and instructor tables is scoped |
| Accessible names | No unnamed buttons, links, inputs, selects, or textareas |
| Decorative images | Logos use `alt=""`; no image without an `alt` attribute |
| Warning text contrast | Fixed in this release |
| Heading order | Fixed in this release |

## Verification

| Check | Result |
|---|---|
| Frontend tests | `56 passed` (21 files) |
| Frontend lint | `0 errors` |
| Frontend build | Passed |
| UI string budget | Passed (`5,412` budgeted strings) |
| Bundle budget | Passed |
| Link check | `1,223` Markdown files, no broken links |
| Backend tests | `637 passed`, `559 skipped` (unchanged backend) |
| Supply-chain lock | Updated and signed |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.52.3` | Pending |
| Production | `5.52.3` | Pending |

Rollback images are tagged `pre-v5.52.3` on both hosts.
