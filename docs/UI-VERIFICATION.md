# UI verification

Last run: **2026-11-08** against both deployments:

- development `https://192.168.120.44` (`2.5.3`)
- production `https://192.168.120.41` (`2.5.3`)

`192.168.120.0/24` is a placeholder management subnet used throughout the
documentation. Replace it with your own; the addresses are not real deployments.

Tool: Playwright with Microsoft Edge, using short-lived test tokens for an
administrator and the three career-discovery profiles. No learner records were
modified by the checks.

## 2.5.3 competency radar accessibility

Run **2026-11-08** against the development deployment on `2.5.3`:

- student `/dashboard` (individual radar) at 1280×900 and 320×800;
- instructor `/courses/10?tab=analytics` (cohort radar) at 1280×900 and 320×800;
- instructor `/reports` at 1280×900 and 320×800.

Result: **0 axe WCAG 2.2 AA violations** on every radar route and viewport.
Both radar charts expose a `role="img"` text alternative and an eight-row
screen-reader table. At 200% text, the radar routes have no page-level
horizontal overflow; the `/reports` data tables scroll horizontally, which
WCAG 1.4.10 permits for two-dimensional data. The run also fixed two contrast
defects in the skill matrix and analytics RAG badges and made the activity and
analytics table regions keyboard-focusable.

Evidence: `docs/reviews/V2.5.3-RELEASE-EVIDENCE.md`.

## 2.5.2 privacy verification

Run **2026-11-08** against the production and development deployments on
`2.5.2`.

- **14/14 checks passed** on each deployment.
- A fresh admin browser started with privacy mode matching the platform default.
- The current-browser toggle flipped masking off and back on.
- The platform default persisted as off, and a new admin browser inherited it.
- A legacy auto-written `"on"` value without the explicit marker followed the
  platform default.
- An explicit per-browser choice still won.
- The About inventory reported the same version as `/api/version`.
- The temporary QA admin was removed and the platform default restored.

The scheduled UI smoke now runs the same privacy checks when
`UI_PRIVACY_USERNAME` and `UI_PRIVACY_PASSWORD` are configured with an admin
account. Without those secrets it skips the privacy block and keeps the existing
deployment checks. See `scripts/ui-smoke.mjs`.

The detailed 2.4.1 results below are the previous broader UI pass.

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
- The skill tree SVG rendered with six branches and an accessible label.
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
- Admin and user panels loaded with the current `2.4.1` build.

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

## Repeatable deployment smoke

`scripts/ui-smoke.mjs` is the deployment smoke suite used by the optional
`.github/workflows/ui-smoke.yml` workflow. It checks the mobile shell, profile
tabs, Events, the RangeBox tab, version, and page errors.

Required repository configuration:

- variable `UI_BASE_URL` — for example `https://192.168.120.44`
- secret `UI_SMOKE_TOKEN` — a JWT for a student or admin smoke account, **or**
- secrets `UI_SMOKE_USERNAME` and `UI_SMOKE_PASSWORD` — a smoke account that logs
  in for a short-lived token
- optional variable `UI_EXPECTED_VERSION` — for example `2.5.3`

The scheduled workflow is configured for the public production URL
`https://ctfd.swocts.com` with a dedicated `smoke_tester` student account. It
runs daily at 03:30 UTC and on manual dispatch.

Run it locally with:

```bash
UI_BASE_URL=https://192.168.120.44 \
UI_SMOKE_TOKEN=... \
node scripts/ui-smoke.mjs
```

On a workstation with Edge installed, set `UI_BROWSER_EXECUTABLE` to the Edge
executable path and skip the Playwright browser download. The CI workflow runs
`npx playwright install --with-deps chromium` instead.

### Evidence artifacts

Each run writes to `UI_ARTIFACT_DIR` (default `ui-smoke-artifacts/`):

- `evidence.json` — the release evidence: schema version, start and finish
  timestamps, deployment URL, expected and actual version, release name, role,
  every check with its result, failure count, screenshot names, and CI run
  metadata (`GITHUB_RUN_ID`, `GITHUB_SHA`, `GITHUB_REF`) when present.
- `checks.json` — the check list, kept for compatibility with existing tooling.
- `mobile-dashboard.png` and `desktop-rangebox.png` — visual evidence.

The evidence file never contains the token, a password, learner records, or
private deployment addresses. The CI workflow uploads the directory as the
`ui-smoke-evidence` artifact and keeps it for 30 days. Attach the same artifact
to the release record.

A green smoke run proves the deployment is reachable, on the expected version,
and rendering the checked surfaces. It does **not** measure host capacity; the
RangeBox capacity test in [RangeBox capacity](RANGEBOX-CAPACITY.md) is the
sizing evidence.

CI runs the same static checks on every push:

- `scripts/check-nginx-security-headers.py`
- `scripts/check-doc-assets.py`
- `scripts/check-links.py Manual-Lite docs Workbook --mkdocs`

## What this does not prove

- A full interactive lab launch and VPN connection were not part of this run.
- Docker host state was not read by the browser test; use
  `docker compose ps` on each deployment host for that check.
- A smoke run does not measure capacity. Use the
  [RangeBox capacity test](RANGEBOX-CAPACITY.md) on each host class.
- Production `192.168.120.41` was upgraded to `2.4.1`; its admin surface,
  reports, events, profile tabs, skill tree, and mobile layout were verified.

