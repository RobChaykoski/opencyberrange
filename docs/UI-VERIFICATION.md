# UI verification

Last run: **2026-11-07** against the development deployment at
`https://172.16.16.44` (`2.1.4`).

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

- **101 checks, 0 failed**
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
- Admin and user panels loaded with the current `2.1.4` build.

## What this does not prove

- A full interactive lab launch and VPN connection were not part of this run.
- Docker host state was not read by the browser test; use
  `docker compose ps` on each deployment host for that check.
- Production `172.16.16.41` remains on the Community / Academic `1.1.3`
  maintenance line and was not upgraded in this run.
