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
| Warning text contrast | No text below 4.5:1 (or 3:1 for large text) |
| Heading order | No skipped heading levels |
| Total | **129 checks, 0 failures** |

The run used three scoped accounts created for the review (`review-admin`,
`review-instructor`, `review-student`). Screenshots and `checks.json` were
written to the git-ignored `ui-review-artifacts/2026-11-26/` directory on the
review workstation; they are not published. The accounts remain on production
for the manual pass and should be deleted afterwards.

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
| Development | `5.52.3` | Deployed and verified |
| Production | `5.52.3` | Deployed and verified |

Post-deploy checks: `/api/version` reports `5.52.3` on both hosts, backend and
frontend containers are healthy, `nginx -t` passes, and the production wiki
rebuilt 14 sites. Production pre-deploy backup:
`ocr-backup-20261126-040918.dump`; rollback images are tagged `pre-v5.52.3`.
The development host was updated by syncing the tag into the split layout;
rollback there is a rebuild of `v5.52.2`, because that path does not create
`pre-` tags.
