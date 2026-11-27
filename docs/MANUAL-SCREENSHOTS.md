# Refreshing the manual screenshots

The user manual under `Manual-Lite/` uses live screenshots of the platform.
`scripts/ui-manual-screenshots.mjs` regenerates them with Playwright so the
images do not drift when the interface changes.

## What it captures

- Guest pages: login, registration, and the login screen used by troubleshooting.
- Student pages: dashboard, sidebar navigation, exercises hub, track page, lab
  statuses, courses, course overview, VPN setup, the threat map, the tools
  catalogue (including the ZAP card), profile sections (including the AI and
  career data consent panel), community events, change password, the mobile
  shell, and a workbook in its own tab.
- Lab workspace (opt-in): the active-lab panel, timer controls, flag form, hints,
  and the workbook pane, including the resizable desktop/details/workbook split.
- Instructor pages: panel overview, course cards, and every course-management
  sub-tab.
- Admin pages: overview, pending approvals, create-user form, locked users,
  exercises, import-exercise modal, tracks, edit-lab and compose modals,
  create-lab, disk management, sessions, VPN peers, activity log, settings,
  features, and the system tab.

## Run it

```bash
export UI_BASE_URL=https://<dev-host-ip>
export UI_STUDENT_USERNAME="..." UI_STUDENT_PASSWORD="..."
export UI_INSTRUCTOR_USERNAME="..." UI_INSTRUCTOR_PASSWORD="..."
export UI_ADMIN_USERNAME="..." UI_ADMIN_PASSWORD="..."
# Keep Privacy Mode on when the capture host mirrors production users.
export UI_MANUAL_PRIVACY=1
node scripts/ui-manual-screenshots.mjs
```

Optional flags:

- `UI_MANUAL_ACTIVE_LAB=1` spawns `linux-1-1-ssh-service-detection`, captures
  the lab-workspace images, and stops the session. Without it, those images are
  left unchanged.
- `UI_MANUAL_SKIP_ADMIN=1` skips the admin section when no admin account is
  available.
- `UI_MANUAL_PRIVACY=1` leaves Privacy Mode on, which masks usernames, emails,
  and display names. Use it whenever the capture host mirrors production users;
  the current development host does.

Install the browser once per machine with `npx playwright install chromium`
from `platform/frontend/`.

## Prerequisites

The script performs only GETs plus the optional lab spawn/stop. It does not
create accounts or data. To capture the admin samples:

- at least one account awaiting approval (Users > Pending);
- at least one locked account (Users, filter **Locked**);
- one active lab session if you want a populated Sessions card.

If a selector is missing, the script logs `SKIP` and leaves that image as it is.
That is expected on a deployment without demo data.

## Rules

- Use demo or test accounts, never a real learner or instructor. The current
  images use synthetic names such as `alex_chen`, `demotest_instructor_01`,
  `demo_shots_admin`, `demo_shots_pending`, and `demo_shots_locked`, with
  `example.edu` / `example.invalid` addresses.
- Confirm the served release and catalogue before capturing:
  `curl -k -s "$UI_BASE_URL/api/version"` must return the current version, and
  the student dashboard must show the current **public** exercise total (**175**;
  production registers 218 labs, of which 47 are course-scoped). A footer
  that shows only `v5`, or an old total such as 149, means the capture is stale.
- The script turns **Privacy Mode** off by default so names are readable. On a
  host that mirrors production users, set `UI_MANUAL_PRIVACY=1` and keep it on;
  the masks make a mistaken real account safe to publish. Do not publish
  screenshots that contain unmasked personal data either way.
- Capture on the development host, not production.
- Review every diff for PII, secrets, and outdated counts before committing:
  screenshots are binary and easy to miss.
- Keep the image paths stable; the manual pages reference them directly.
- If the demo credentials are unavailable, do not commit a partially refreshed
  set. Leave the existing images, mark the refresh as pending in the pull
  request, and do not claim the screenshots are current.

## Build and check

```bash
python -m mkdocs build -f mkdocs-manual-lite.yml
python scripts/check-doc-assets.py
python scripts/check-links.py Manual-Lite --mkdocs
```
