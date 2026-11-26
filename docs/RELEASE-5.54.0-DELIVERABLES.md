# Release 5.54.0 deliverables

Status: **released and deployed** to development and production on 26 November
2026.

| Item | Value |
|---|---|
| Version | `5.54.0` |
| Signed tag | `v5.54.0` |
| Release date | 26 November 2026 |
| Alembic | `0067_course_content_rls` (no migration) |
| Lab definitions | `217` |
| Workbook-mapped labs | `206` |
| Supersedes | `5.53.1` |

## Added

| Area | Detail |
|---|---|
| Exercise briefing tab | The exercise workspace has a read-only **Briefing** tab beside Desktop, Exercise, and Workbook. It renders the scenario, objectives, target hostnames, workbook link, and already-unlocked hints. The selected tab is carried in `?tab=briefing`, so refresh and deep links restore it. |
| Read-only pop-out | **Pop out briefing** opens `/exercises/:trackSlug/briefing` in a new window with no app chrome, no opener reference, and print support. The tab and pop-out share `ExerciseBrief`, so the content cannot drift. Wide layouts expose the pop-out from the Scenario panel. |
| Shared content path | `utils/markdown.js` owns the placeholder escaping and hard-wrap unwrapping used by scenario and hint text. `utils/workbook.js` resolves the workbook link for both views. Neither view accepts the flag, VPN keys, credentials, or learner PII. |

## Verification

| Check | Result |
|---|---|
| Backend tests | `668 passed`, `559 skipped` (no backend source change) |
| Frontend tests | `70 passed` (24 files) |
| Frontend lint | `0 errors`; existing bare-string warnings remain baselined |
| Frontend build | Passed; bundle budget passed |
| Compose YAML | Parses for production and development (unchanged) |
| Publication audit | `0 findings` |
| Link check | `1,234` Markdown files, no broken links |
| Supply-chain lock | Signed; `142` files and `217` lab hashes match release `5.54.0` |

## Accessibility and safety checks

| Check | Result |
|---|---|
| Tab semantics | `tablist` / `tab` / `tabpanel`, with left/right arrow navigation and `aria-selected` |
| Tab strip on narrow screens | Horizontal scroll with non-shrinking tab labels |
| Panel scrolling | The brief scrolls independently inside the workspace panel |
| Pop-out at 375 px | Page and action buttons wrap to full width |
| Pop-out window safety | `window.open(..., 'noopener,noreferrer')`; route is authenticated and bare |
| Markdown rendering | One sanctioned marked + DOMPurify path; regression tests cover script tags and event handlers |
| Secrets | No flag or learner PII in either view; tests assert the flag field is not rendered |

## Deployment

| Environment | Version | Status |
|---|---|---|
| Development | `5.54.0` | Deployed and verified |
| Production | `5.54.0` | Deployed and verified |

The feature is frontend-only. Alembic stays at `0067_course_content_rls`, and
the lab and workbook definitions are unchanged.
