# Page and Interaction Patterns

Use these patterns as defaults. Match the page's actual job before adding a new visual idea.

## Application shell

- `AppSidebar.vue` owns primary navigation: Ops Center, Academy, Instructor (role-gated), Admin (role-gated), and Profile.
- The main content area scrolls independently; page views start with a page container and a clear title.
- The theme toggle is global. Do not add a second theme switch inside a page.
- The SWOCTS footer is global. Do not duplicate it inside views.
- The sidebar collapses; content must remain usable when it is narrow.
- Do not add marketing navigation to authenticated operational pages.

## Student dashboard / Ops Center

- Lead with the current objective, then progress, VPN status, rank, and completion matrix.
- Use a responsive card grid (`auto-fit`, `minmax(260–320px, 1fr)`).
- Use a strong primary action for the next lab.
- Progress is always expressed as both a visual bar and a text ratio (`17 / 42 exercises`).
- Matrix/table data must remain readable at narrow widths; horizontal scroll is acceptable inside the card.
- Status indicators need a text label, not colour alone.
- Loading should preserve layout; avoid a blank page.

## Exercises catalogue

- Track cards show icon, name, description, completed/total, percentage, and current level.
- Keep the track icon mapping in `components/icons/trackIcons.js`; never hard-code a new icon in a page.
- Track colour from the API may tint the icon/accent, but body content uses the normal text tokens.
- Locked states must explain the prerequisite: "Complete previous exercise" is clearer than a padlock alone.
- Level rings/pills should include `completed / total` and a complete state.
- Empty catalogue: explain that no labs are available and point to courses or the administrator.

## Profile

The profile is a record page, not a settings dump. Preserve this order:

1. **Hero** — avatar, display name, username/email, role and approval badges, member since, completion stats.
2. **Certificates and completion** — certificate cards linking to the certificate page, track progress, expandable completion details, achievements, and the PDF download.
3. **Personal information** — first/last name, organisation, certificate-name preview.
4. **Account information** — username, email, status, registration date, VPN, role.
5. **Course enrolment** — join form and enrolled courses.
6. **Security** — MFA and password change.
7. **Privacy and data** — download the account export and delete the account. Deletion requires the current password, MFA when enabled, and typing `DELETE`; explain what is erased, what is anonymised, and the backup retention window.
8. **Instructor Studio** — only when the module is available and the user is instructor/admin.

Profile rules:

- Avatar supports initials fallback; never leave a blank circle.
- Avatar actions are secondary; the certificate/PDF action is the primary page action.
- Certificate cards must show track, level, award date, exercise count, and certificate ID.
- Track progress uses a bar plus level pills with a check mark for certified levels.
- Completion details can be collapsed with `<details>`; keep the summary count visible.
- Print/PDF styling must not include sidebar, buttons, or form controls.
- The hero must not push the record below the fold on a typical laptop.
- Account deletion is never a one-click action. Show the consequences, require re-authentication, and keep the export action next to it so the user can take their data first.
- If deletion is blocked by course ownership or the last-admin rule, explain the fix (transfer courses, promote another admin) instead of showing a generic failure.

## Track detail / lab catalogue

- Header: track icon, name, description, overall progress, and a back action.
- Levels are ordered and show completion counts.
- Lab rows: name, difficulty, duration, tools, lock/launch state, active session state.
- Use badges for Drill, KVM/shared VM, and completed state.
- Do not hide the lock reason.
- A running lab replaces "Launch" with a clear resume/open action.

## Course and instructor views

- Course pages are roster-and-workflow tools first.
- Primary tabs: overview/roster, assignments, scoreboard, achievements, settings.
- Roster tables need search/filter, clear identity columns, and destructive actions separated from normal actions.
- Grade/report downloads are secondary actions.
- Scoreboard/achievement views must not expose more student PII than necessary.
- Empty states should tell the instructor what to do next (assign labs, share invite code, wait for enrolment).

## Admin

- Dense, scannable, and conservative.
- Use tabs or sections for Users, Courses, Exercises, Live activity, System, Settings.
- Destructive controls (delete user, reset lab, stop container, reset password) require confirmation and should not sit beside low-risk actions.
- Status rows should include labels and timestamps, not just coloured dots.
- Tables should support filtering and horizontal scroll on narrow screens.
- Settings forms need explicit save/revert affordances and clear scope (global vs course).
- Never display secrets after creation. Use masked values and "replace" workflows.

## Authentication and setup

- Single-column, focused layout.
- One primary action per screen.
- Explain prerequisites before asking for secrets.
- Inline validation with associated error text.
- Preserve entered values after server errors.
- MFA setup must show the secret/URI with copy affordance, then verify with a code.
- Setup wizard steps need a visible progress indicator and a way back.

## Lab workspace / RangeBox

- Maximise working area; the lab is the content.
- Keep the session timer, stop/resume, and target details reachable but not dominant.
- Use full-screen or near-full-screen layout only inside the workspace.
- Destructive actions (stop, delete, reset) need confirmation.
- Terminal and console text use mono; do not apply decorative effects that reduce readability.
- Never place student flags or VPN keys in URL query strings or visible metadata.
- Mobile is a fallback for many labs; if unsupported, say so explicitly.

## Workbook / MkDocs pages

- Content first: headings, code blocks, admonitions, tables, and diagrams.
- Use Material admonitions consistently: `!!! note`, `!!! warning`, `!!! tip`.
- Keep code blocks copyable; don't use screenshots where text suffices.
- Every lab walkthrough follows: Before You Begin → Scenario → Objectives → Background → Walkthrough → Analysis Questions → Defensive Takeaways → If You Get Stuck.
- The chapter review includes self-assessment, answer key, and command cheat sheet.
- Do not hide the flag answer in hints. Hints should scaffold, not solve.

## Certificates and PDF transcripts

- Certificate pages use a light paper surface with a restrained gold frame, serif display type, and a clear seal/signature area.
- Print CSS hides all application chrome (`no-print`, sidebar, theme toggle).
- Transcript PDFs include identity, totals, certificate table, track progress, completed exercises, and achievements.
- Keep certificate IDs in mono and visible.
- Never put an unverified claim of accreditation in a certificate; use the configured issuer text.

## Loading, empty, and error states

Every data-driven view needs:

- **Loading:** preserve layout and say what is loading.
- **Empty:** explain the next action, not just "No data".
- **Error:** state what failed and offer a retry or safe path.
- **Permission denied:** explain the role/entitlement needed, and link to a safe destination.
- **Partial data:** render the sections that succeeded instead of replacing the whole page with an error.
