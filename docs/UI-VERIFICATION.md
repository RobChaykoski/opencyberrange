# UI verification

> **Historical record.** The 2.5.3 sections below keep the placeholder
> management subnet used at the time. Current host status and build assets are
> in [Deployment status](status-dashboard.md).

## 2.6.0 combined exercise workspace

Checked on **11 November 2026** with a dedicated test student and test
instructor account against production (`https://ctfd.swocts.com`):

- Desktop RangeBox exercise (`RangeBox First Steps`) rendered the combined
  workspace: RangeBox top-left, scenario/details and flag form on the right, and
  the workbook in a framed bottom pane.
- The workbook iframe resolved to the correct chapter under
  `/wiki/range/high-school/`.
- **Expand/Restore** resized the workbook pane.
- **Request Hint** returned a hint without completing the exercise.
- An invalid flag produced an error message and did not complete the lab.
- **Stop Exercise** accepted the confirmation and closed the panel.
- The mobile viewport (390 px) kept the stacked panel and section jump bar, with
  no horizontal overflow.
- The initial walkthrough found one button bug: **Open in new tab** used in-page
  routing. It now opens the resolved `/rangebox?...` URL in a new tab. It also
  found that the workbook CSP blocked the Material for MkDocs Google Fonts
  stylesheet; the wiki locations now allow the font stylesheet and font files.

Evidence: `scripts/ui-workspace-regression.mjs` writes
`ui-workspace-artifacts/workspace-regression.json` plus desktop dark, desktop
light, and mobile screenshots. The rerun after the fixes passed **44/44 checks**
(0 failures) for the test student and test instructor, including RangeBox VNC
connected, both new-tab controls, Expand/Restore, Request Hint, invalid-flag
handling, Stop, and the mobile fallback. Screenshots:
`docs/img/exercise-workspace.png` (desktop) and
`docs/img/exercise-workspace-mobile.png` (phone fallback).

The same walkthrough exposed a stop/relaunch race: background cleanup for an old
session could remove the network and RangeBox created by a newer session for the
same lab, which silently launched the new lab VPN-only. Cleanup now checks for a
newer starting/running session and leaves the live environment alone.

Deployment on **11 November 2026**:

- Production `172.16.16.41` / `https://ctfd.swocts.com` and development
  `172.16.16.44` run `2.6.0` and are healthy. Production is on `2835303b`; the
  development checkout advanced to `f3234e80`, which contains documentation and
  test additions only.
- The wiki builder published 13 sites. The WEB01 page
  `01_Web_Target_and_Scope_Preflight` and the `W1.11` navigation entry are
  present.
- The wiki CSP serves the Material for MkDocs font stylesheet from
  `fonts.googleapis.com` and font files from `fonts.gstatic.com`; the SPA policy
  remains self-only.
- The temporary test student and instructor accounts and their sessions were
  removed after the run.
- The broader deployment UI smoke (`scripts/ui-smoke.mjs`) also passed **9/9**
  checks against the student account: API version, mobile shell, profile tabs,
  events, RangeBox tab, and no page errors.

Development rerun on **11 November 2026** against `https://172.16.16.44`
(`f3234e80` checkout, app reports `2.6.0`):

- `scripts/ui-workspace-regression.mjs` passed **44/44 checks** for the seeded
  development demo student and instructor accounts: combined workspace, RangeBox
  VNC, workbook iframe, Expand/Restore, both new-tab controls, hint, invalid
  flag, Stop, and the 390 px mobile fallback.
- `scripts/ui-smoke.mjs` passed **9/9 checks**: API version, mobile shell,
  profile tabs, events, RangeBox tab, and no page errors.
- The demo accounts' password hashes were temporarily replaced for the run and
  restored afterwards. No learner accounts or completions were changed, and no
  lab containers remained running.
- Curriculum card and lock-sequence check: **40/40 checks** on desktop and at
  390 px. The new **Beginner Cybersecurity**, **Identity & Access**, and
  **Software Security** cards render with the expected current level and
  exercise counts. Beginner Cybersecurity shows all four stages and 18 labs,
  with **1 unlocked / 17 locked**; Identity & Access shows **1/3 unlocked** and
  Software Security **1/2**. The DOM lock state matched the API
  `is_unlocked` value for every lab, including the Level 10 first lab staying
  locked until Level 9 is complete.
- RangeBox target access and timings: four Stage 2/3 labs were launched with a
  Kali RangeBox, and the target was reached from inside the desktop. DNS
  resolved and HTTP returned **200** in every case:

  | Lab | Target | Spawn | RangeBox ready | HTTP | Stop / cleanup |
  |---|---|---:|---:|---:|---:|
  | RangeBox Network Basics | `network.lab` | 9.5 s | 21.0 s | 200 / 2.4 ms | 42.6 s |
  | RangeBox Browser and Source | `web.lab` | 11.6 s | 23.0 s | 200 / 2.3 ms | 42.6 s |
  | Dissect an Email | `emailmeta.lab` | 11.6 s | 23.0 s | 200 / 4.0 ms | 42.6 s |
  | RangeBox Log Detective | `logs.lab` | 10.4 s | 21.9 s | 200 / 2.6 ms | 43.7 s |

  These are single-lab timings on the development host, not a capacity result;
  use [RangeBox capacity](RANGEBOX-CAPACITY.md) for sizing.
- Evidence: `ui-workspace-artifacts/dev-20261111/` and
  `ui-smoke-artifacts/dev-20261111/` on the operator workstation.

## 2.6.0 event certificate additions

Checked on **2026-11-10** through the production frontend build and backend
compilation, not a live browser session:

- Competition detail page shows **Your event certificates** only after the event
  ends and lists participation, placement, and trophy awards the learner earned.
- Certificate page switches to event mode at `/certificate/event/:eventId/:award`,
  shows the event logo, award wording, event dates, and a **Supported by**
  sponsor strip, and downloads the PDF from the event endpoint.
- Public verification renders event award metadata for `OCR-EVT-` IDs and keeps
  the track certificate result layout for existing IDs.
- The verification input validates both ID shapes before enabling **Verify**:
  `OCR-<track>-L<level>-<digest>` and
  `OCR-EVT-<competition>-<user>-<award>-<digest>`.
- `npm run build` and `python -m py_compile` pass for the changed files.
- A4 PDF layout and embedded artwork now have regression coverage.
  `platform/backend/tests/test_event_certificate_pdf_layout.py` renders a
  certificate with an event logo, gold/silver/bronze sponsor logos, and a QR
  code, then asserts the A4 landscape page size (841.89 x 595.28 pt) and at
  least five embedded images. Result: **1 passed**.
- Mobile and desktop verification form behaviour was checked in a browser on
  **11 November 2026** against production (`https://ctfd.swocts.com`) and
  development (`https://172.16.16.44`). `scripts/ui-verify-public.mjs` passed
  **60/60 checks**: the page loads without sign-in, malformed IDs are rejected
  before submit, a well-formed unknown ID returns the generic invalid result
  without account details, there is no horizontal overflow at 390 px, and no
  page or console errors were raised.
- Visual review on **11 November 2026** used a temporary ended development event
  with a 960 x 300 event logo and gold/silver/bronze sponsor logos. The event
  detail page, certificate page, mobile certificate, and public verification
  passed **25/25 checks**. Every event and sponsor image loaded at its natural
  size, the five award certificates were listed, and the public result exposed
  the award and event but no account details. The PDF rendered at A4 landscape
  (841.89 x 595.28 pt) with five embedded images: event logo, three sponsor
  logos, and the QR code. Evidence:
  `ui-workspace-artifacts/dev-20261111/certificate-event-desktop.png`,
  `certificate-event-mobile.png`, `certificate-verify-desktop.png`,
  `certificate-first.pdf`, and `certificate-first.png`. The temporary event and
  its awards were removed and the demo account hashes restored after the run.

Deployment smoke on **2026-11-10**:

- Development (`172.16.16.44`) and production (`172.16.16.41`,
  `https://ocr.swocts.com`) both report `2.6.0`.
- `/health` is healthy, lab discovery reports 162 labs with 0 errors, and both
  frontends serve `index-Dx733NF9.js`.
- `GET /api/competitions/1/certificates` without a token returns `401`, so the
  event-certificate route is present; public `OCR-EVT-` verification returns the
  generic invalid result for an unknown ID.
- No backend errors were logged in the final 200 lines on either host.

## 2.6.0 fresh student journey

Run on **11 November 2026** against development (`https://172.16.16.44`) with a
temporary approved student account. The account was created for the run and
deleted afterwards, so no seeded demo or learner data was changed.

- **59/59 checks passed** through the real sign-in form: dashboard, Exercises,
  Workbooks, all five Profile tabs (Overview, Skill tree, Learning record,
  Account, Security & privacy), Events, Competitions, Celebrations, VPN setup,
  RangeBox, About, Privacy, and public certificate verification.
- Completed **RangeBox First Steps** end to end: RangeBox VNC connected in 17 s,
  the desktop read `http://rangebox.lab:8080/welcome.txt`, the flag was
  submitted, the flag celebration appeared, the lab stopped, the completion
  appeared in the learning record, and the next lab unlocked.
- Completed **RangeBox File Hunt**: RangeBox VNC connected in 19 s, the desktop
  downloaded and unpacked `evidence.zip`, and read the real token from
  `evidence/archive/old/flag.txt`. The archive contains an intentional decoy
  token; the automated harness first matched the decoy with `grep`, and the
  documented path returned the real flag. The UI accepted the flag, the lab
  stopped, and the third lab unlocked.
- Progression stopped at the third lab (`CyberChef: Decode a Base64 Message`)
  because it is not a RangeBox lab and needs the VPN / CyberChef path.
- No page errors, console errors, or unexpected network responses were recorded.
- Evidence: `ui-workspace-artifacts/journey-20261111/` (`user-journey.json`,
  `second-lab.json`, and screenshots `01-dashboard.png` through
  `22-profile-two-completions.png`).

## 2.6.0 account security and VPN verification

Run on **11 November 2026** against development (`https://172.16.16.44`).

### Registration and account security

- Registration through the public form: **8/8 checks**. The new account showed
  the pending-administrator message and could not sign in before approval. After
  approval, sign-in worked.
- Password change: the old password was rejected and the new password accepted.
  The success message is shown for 1.5 s before the forced re-login. During that
  window the browser logs expected 401s from profile and course fetches while the
  invalid token is being dropped; the user-facing flow completes normally.
- MFA: enrollment, TOTP sign-in, ten recovery codes, single use, and reuse
  rejection all passed.
- The temporary account was deleted after the run.

### VPN and VPN-only lab

- `/api/labs/vpn-config` generated a config (`10.255.0.227/32`, endpoint
  `172.16.16.44:51820`, route `10.100.218.0/24`) and registered the peer.
  The WireGuard handshake succeeded from a client.
- Initial target access failed because the server had no route to the
  `10.255.0.0/16` client pool, so return traffic went to the LAN gateway.
  Adding `ip route add 10.255.0.0/16 dev wg0` on the server fixed it. The
  installer now writes this route in `PostUp`/`PostDown`
  (`scripts/setup-range-server.sh`); existing hosts need the route added or
  their `wg0.conf` updated.
- The client config does not set `DNS`, so `cyberchef-b64.lab` does not resolve
  over the tunnel. The lab panel shows the lab subnet (`10.100.218.0/24`) and
  instructs the learner to scan, and the target was reached at
  `10.100.218.93:8080`.
- Fixed the VPN-only hostname gap in
  `platform/backend/app/routers/curriculum.py`: when the active session is
  VPN-only, the lab detail response includes the computed target IPs and a
  hosts-file mapping. RangeBox sessions keep IPs hidden unless the lab sets
  `show_target_ips`, so the discovery flow is unchanged there. Unit tests:
  **4 passed**; live API check: a VPN-only session returned
  `10.100.223.93` for `cyberchef-b64.lab`, while a RangeBox session returned no
  IPs.
- Applied to both hosts on **11 November 2026**: the runtime route is active on
  development (`172.16.16.44`) and production (`172.16.16.41`), and persisted in
  each host's `/etc/wireguard/wg0.conf` (backup `wg0.conf.bak-20261111`).
- Deployed the target-IP change to production on **11 November 2026**: the
  backend was rebuilt and restarted healthy. A VPN-only Web lab panel passed
  **9/9 checks** and showed the subnet, `10.100.48.17`, `recon.lab`, and the
  hosts-file mapping, with no page or console errors. Evidence:
  `prod-target-ip-panel.png` and `prod-target-ip-panel.json`.
- The new beginner labs were in the production catalogue but seven of their
  images were not prebuilt. Spawning CyberChef Base64 initially failed with “not
  prepared on this server; on-demand builds are disabled.” The seven images were
  then built on production, and all 18 Beginner lab images are now present. The
  full **18/18 Beginner track was completed end-to-end on production** with a
  temporary student: every target was read, every flag accepted, and each next
  lab unlocked. Disk cleanup removed three old backend tags and reclaimed about
  2G; 26G remains free, with 40.1G still reclaimable from unused prebuilt lab
  images. Do not run `docker image prune -a` on this host.
- Other existing hosts can apply the same fix with
  `sudo bash scripts/fix-wireguard-client-route.sh`. It adds the runtime route,
  backs up `wg0.conf`, and persists the route in `PostUp`/`PostDown`.
- The Base64 message was downloaded over the tunnel, decoded to
  `OCR{b4s364_is_encoding_not_encryption}`, and submitted through the UI. The
  lab completed and the next CyberChef lab unlocked.
- **Stage 1 completed end to end.** The remaining CyberChef and digital-safety
  labs were launched VPN-only and their targets read over WireGuard: ROT13
  (Caesar), Base64 then ROT13 (two layers), URL decoding (lookalike link), a
  disguised ZIP (file type), and the capstone notice then disguised ZIP. All
  eight Stage 1 flags were accepted, and **RangeBox Network Basics** in Stage 2
  unlocked.
- UI verification: **6/6 checks**. Stage 1 showed **8/8 completed** and the
  first Stage 2 lab had a Launch action. Evidence:
  `ui-workspace-artifacts/journey-20261111/stage1-complete.png` and
  `stage1-complete.json`.
- Stage 2 completed **6/6** with a second student account: **RangeBox Network
  Basics**, **RangeBox Browser and Source**, **Dissect an Email**, **MFA and the
  Lost Phone**, **RangeBox Log Review**, and **RangeBox Beginner Challenge**.
  The MFA recovery flow was driven over the VPN. The log labs contain an
  intentional decoy token; filtering the `admin?token=` request returns the
  real token. UI verification: **5/5 checks**, Stage 2 shows 6/6 and Stage 3's
  first lab, RangeBox Log Detective, is unlocked. Evidence:
  `ui-workspace-artifacts/journey-20261111/stage2-complete.png` and
  `stage2-complete.json`.
- Stage 3 and Stage 4 were completed over the VPN: **RangeBox Log Detective**
  (real token in the `admin?token=` log request), **Media Provenance**
  (`/verify?id=river-cleanup`), **DevFest Community Portal** (flag in the
  exported PNG text metadata), and **Crypto Rug Pull** (ledger, drained wallet,
  then case file). The full Beginner Cybersecurity track is now **18/18
  completed, 100%**, with no locked labs.
- Final UI verification: **12/12 checks**. The track card shows 18/18 and
  **Complete**; the Stage 1 certificate opens at
  `/certificate/high-school/40` and renders “8 of 8 exercises completed”.
  Evidence: `beginner-complete.png`, `beginner-complete-card.png`,
  `beginner-certificate.png`, and `beginner-complete.json`.
- Stage 2-4 certificates passed **3/3**. The level **Quiz** buttons previously
  opened an empty modal because
  `/api/exercises/tracks/high-school/levels/{41,42,43}/quiz` returns `404` “No
  quiz available for this level.” The track response now includes `has_quiz` per
  level and the UI hides the Quiz button when no active level quiz exists, so
  the High School Stage 2-4 buttons are hidden until quiz banks are added.
  Verified on dev: **6/6 checks**, no Quiz buttons on completed levels, four
  Certificate buttons still present, and `has_quiz=false` for every level. The
  `level_quizzes` table is empty, so all level Quiz buttons are hidden until the
  quiz engine and banks are created. Deployed to dev and prod; the production
  API also reports `has_quiz=false` for all four Beginner levels.
- Cleanup-race guard added: `create_lab_environment` now preserves networks
  owned by a session that is still `starting`/`running` and removes only stale
  lab networks for that user. Unit tests: **4 passed**.
- Broader smoke beyond Beginner: Malware `malware-1-1-eicar-triage` (VPN-only,
  target `evidence` at `10.100.225.40`) and Linux
  `linux-2-1-ssh-basic-login` both spawned and reached `running` on development;
  Web `web-1-1-basic-directory-enumeration` was verified on production.
- Evidence for the earlier parts: `signup.json`, `account-security.json`,
  `cyberchef-lab.json`, and the matching screenshots.

## Post-2.5.5 UI additions

Checked on **2026-11-10** against the development and production deployments:

- Public `/about` loads without sign-in and links to register, sign in,
  certificate verification, and the privacy notice.
- `/about/installation` remains authenticated and reads the live release
  inventory with `Cache-Control: no-store`.
- Certificate verification page has a public layout, ID guidance, privacy
  explanation, and role-aware navigation.
- Login and registration use skip links, visible focus, Caps Lock warnings,
  password-strength text, reduced-motion handling, and explicit privacy/under-18
  acknowledgment.
- The student sidebar shows a **CyberChef** item in **Tools**; the active-lab
  panel has a CyberChef button.
- The three new High School Grade 9 CyberChef labs pass `validate-lab.py` and
  their target decode paths were smoke-tested.

Not verified in a real browser at that time: a live RangeBox desktop session,
mobile drawer rendering of the new Tools item, and a live learner walkthrough of
the CyberChef labs.

## Post-2.5.5 lab additions

Checked on **2026-11-10** through static lab validation and deployment smoke
tests, not a live browser session:

- Grade 9 digital-safety labs: **Read the Link**, **Know the File**, and the
  **Forwarded Message** capstone. The targets are isolated and the workbook
  links resolve.
- Grade 10 **Dissect an Email** lab: raw-message download, header table, and
  workbook page resolve.
- **Identity & Access** track: secure authentication, OAuth/OIDC, and identity
  lifecycle labs, with the track, levels, workbook pages, and certification
  guidance present in the catalogue.
- **Grade 10–12 Digital Frontier** labs: MFA recovery, media provenance, and a
  simulated crypto rug pull, with workbook pages, six-question knowledge checks,
  three per-lab badges, and the Digital Frontier collection badge.
- **VPN configuration update:** the Dashboard VPN card now tells learners whose
  tunnel stopped working to download a fresh config. The client uses a `/32`
  address and routes only the learner's own lab `/24`; old `/16` configs must be
  re-imported.
- The student workbook wiki rebuilt with the new chapters; the track card uses
  the existing web icon and the violet track colour.
- Deployment, seed, and discovery scripts now emit ASCII status markers, so
  logs render correctly in Windows terminals and CI.

Not verified in a real browser: the new track cards, level unlock sequence,
workbook rendering for the new chapters, and RangeBox access to the new target
hostnames. Timings for the new labs remain provisional.

## 2.5.4 deployment smoke

Run **2026-11-10** against the public OCR deployment at
`https://ocr.swocts.com` on **2.5.4**:

- Workflow: **UI smoke** (`42741914124`)
- Result: **success**
- Expected version: `2.5.4`
- Checks include API version, authenticated dashboard access, About inventory
  version parity, desktop and mobile dashboard rendering, and the privacy
  settings round-trip.

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

`scripts/ui-verify-public.mjs` checks the public certificate verification page
at desktop and 390 px mobile widths. It needs no account or token and writes
`ui-verify-artifacts/verify-public.json` plus screenshots:

```bash
UI_VERIFY_URLS=https://ctfd.swocts.com,https://172.16.16.44 \
node scripts/ui-verify-public.mjs
```

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

- A full interactive lab launch and RangeBox desktop were covered by the
  workspace regression and target-host checks above. A WireGuard VPN client
  connection was not part of those browser runs.
- Docker host state was not read by the browser test; use
  `docker compose ps` on each deployment host for that check.
- A smoke run does not measure capacity. Use the
  [RangeBox capacity test](RANGEBOX-CAPACITY.md) on each host class.
- Production `192.168.120.41` was upgraded to `2.4.1`; its admin surface,
  reports, events, profile tabs, skill tree, and mobile layout were verified.

