# UI verification

Last run: **2026-11-08** against both deployments:

- development `https://172.16.16.44` (`2.4.0`)
- production `https://172.16.16.41` (`2.4.0`)

Tool: Playwright with Microsoft Edge, using short-lived test tokens for an
administrator and the three career-discovery profiles. No learner records were
modified by the checks.

## Profiles checked

| Profile | Purpose |
|---|---|
| `swocts` (admin) | Admin panel, Reports & analytics, Events, profile tabs |
| `demo_career_ready` | Well-versed learner; offensive-security affinity |
| `demo_career_starting` | New learner; early investigation evidence |
| `demo_career_changer` | Career changer; DFIR/investigation affinity |

## Result

- Development: **101 checks, 0 failed**
- Production admin: **25 checks, 0 failed**
- Production admin mobile shell: **12 checks, 0 failed** (bottom tabs are student-only)
- Admin and student routes loaded without page errors.
- `/events` loaded for every profile.
- Admin sidebar exposed **Reports & analytics** and **Events**.
- Admin header linked to `/reports`.
- All five profile tabs rendered: Overview, Skill tree, Learning record,
  Account, Security & privacy.
- Keyboard arrow navigation moved between profile tabs.
- The skill tree SVG rendered with five branches and an accessible label.
- Practice affinities rendered for every profile, including the expected
  recommended affinity.
- Career-profile export buttons rendered.
- No mobile page overflow on the skill tree tab at 390 px.
- No empty or `javascript:` links were found in the admin navigation.

## Endpoint and safety checks

- `/api/profile/career-dossier` returned 200 for every checked profile.
- Every dossier contained four affinities.
- Dossier endpoints require authentication, send `Cache-Control: no-store`,
  escape HTML, and audit the export.
- Admin and user panels loaded with the current `2.4.0` build.

## Mobile shell

The student shell was checked at `390 × 844` with touch enabled and the
`demo_career_starting` learner.

- **15 checks, 0 failed** after the final CSS fix.
- The sidebar starts off-canvas and opens as a drawer from the top-bar menu.
- The backdrop, close button, and Escape key close the drawer.
- The bottom tab bar shows Home, Exercises, RangeBox, Courses, and Profile.
- The desktop theme switch is hidden; the top-bar theme control is shown.
- No page-level horizontal overflow on the checked student routes.
- Touch targets in the mobile shell are at least `24 × 24px`.
- The RangeBox tab is reachable and shows the deployed-box count.
- The embedded RangeBox viewer is replaced on phones with a desktop-recommended
  notice and an explicit full-screen opt-in.
- No page errors were raised during the mobile checks.
- Breakpoint check at `375`, `768`, `769`, `1024`, and `1440` px: the mobile
  shell is active at `768` px and below, the desktop shell at `769` px and
  above, with no page-level horizontal overflow at any width.

Production admin mobile shell was also checked at `390 × 844`: the top bar, the
off-canvas drawer, and the theme control work, with no horizontal overflow.
The student bottom tab bar is intentionally not shown for admin and instructor
roles.

## What this does not prove

- A full interactive lab launch and VPN connection were not part of this run.
- Docker host state was not read by the browser test; use
  `docker compose ps` on each deployment host for that check.
- Production `172.16.16.41` was upgraded to `2.4.0`; its admin surface,
  reports, events, profile tabs, skill tree, and mobile layout were verified.

