# UI verification

> **Historical record.** The 2.5.3 sections below keep the placeholder
> management subnet used at the time. Current host status and build assets are
> in [Deployment status](status-dashboard.md).

## Release 4 QA and dev deployment (12 November 2026)

Status: **deployed to development `.44`; production unchanged.** Platform
`/api/version` reports `4`.

### Automated checks

| Check | Result |
|---|---|
| Backend suite with PostgreSQL (`TEST_DATABASE_URL`) | **510 passed, 0 failed** |
| Backend suite without a database | **293 passed, 217 skipped** |
| Lab validator (`validate-lab.py --all`) | **170 labs, 0 errors, 0 warnings** |
| Topology engine unit tests | **18 passed** |

| Relative links in README, docs, Manual-Lite, Workbook | **479 files, all resolve** |
| Frontend build | **Passed** |
| Frontend lint | **0 errors** (existing warnings only) |
| Licence guard (`check-licences.py`) | **OK** |
| Supply-chain lock + signature | **OK, release 4** |

### Deployed smoke tests

- `/api/version` = `4`; `/health` healthy.
- `/login`, `/sso/callback`, `/exercises`, `/profile`, `/admin` return the SPA.
- Institution sign-in lists the Dex OIDC and LDAP providers.
- LDAP student login + ticket exchange = student; instructor = instructor, and
  the directory role refresh applied on the second login.
- Full OIDC flow (Dex → LDAP connector → callback → ticket exchange) = student.
- Admin-only endpoints return `401` without a token.
- `/docs`, `/redoc`, and `/openapi.json` return `404` on the public origin.
- `enable_api_docs` toggles `200 → 404` on the direct backend port immediately.
- `advanced_dna_insights_enabled` removes/adds the career atlas payload.
- The built SPA contains the new **Practice this branch**, **How this is
  calculated**, **No evidence yet**, and **Established** strings.
- **Topology engine:** `network-12-2-device-topology-engine` spawned `h1`, `r1`,
  and `svc`; the node status endpoints reported host/router/service; `h1` had a
  default route via `r1`; `r1` reported `ip_forward=1` and both connected
  `/29` links; `h1` fetched `OCR{t0p0l0gy_r0ut3d}` from the service link
  address.

### Known gaps

- The network device topology engine is not part of this deployed build; it
  remains planned work.
- Production has not been upgraded to Release 4.
- SAML single logout and a formal SSO security review remain.
- LTI, multi-tenancy, per-student accommodations, a signed VPAT, SOC 2, and
  ISO 27001 are Release 5 (`docs/RELEASE-5-SCOPE.md`).

## Hardening deployment (12 November 2026)

Status: **deployed to development; production unchanged.**

- **Runtime:** single-worker default, multi-stage non-root image, Python
  healthcheck, and no `gcc` in the final layer.
- **Docker control:** the backend talks to `tecnativa/docker-socket-proxy` on a
  private `docker_control` network. A full compose lifecycle test through the
  proxy succeeded: network create, container create/start/logs/stop/remove, and
  network remove.
- **Valkey:** `/api/about` reports Valkey 9.1.3; the backend uses
  `redis://valkey:6379/0`; the old `ocr-redis` container was removed.
- **Alembic:** the development database reports
  `0014_performance_indexes`; `0013` and `0014` columns and indexes are present.
- **Crypto:** a new secret round-trips with the `v1:` envelope; the re-encryption
  pass moved 2 stored secrets and then reported 0 remaining.
- **Permissions:** the backend runs as the dev override UID 1000; `/app/backups`
  and `/workbook` are writable.
- **Health:** backend and frontend return 200; the backend reports healthy.
- **Not yet verified:** a full lab launch through the learner API (the Docker
  proxy compose lifecycle is verified), a production-shaped run with the
  non-root UID 10001 and named volumes, and a restore drill from the backups
  volume.

## Public About contrast (12 November 2026)

The public About page's **Create an account** primary button was unreadable in
dark mode: `.public-about a` set the link colour to the accent blue and
overrode the button's white text. The rule is now scoped to
`.public-about a:not(.btn)`.

Verified with `platform/frontend/ui-about-contrast.mjs` against production
`172.16.16.41`: white text on `rgb(37, 99, 235)`, contrast **5.17:1** (WCAG AA
requires 4.5:1 for normal text).

## Advanced DNA Insights preview (development)

Status: **implemented in the development tree; deployed to `.44`; live profile
screenshots captured on 12 November 2026.**

- **Backend:** `skill_momentum.py` and `career_explorer.py` add the derived
  Momentum and Career Atlas layers without changing Cyber DNA `2026.14`. The
  surfaces are gated by `advanced_dna_insights_enabled` (default off).
- **Frontend:** the Profile **Careers** tab (Cyber GPS and Career Atlas), the
  Momentum panel, branch progress rings, node unlock states, the Canada/US
  salary lens, and the role ladder.
- **Live capture:** `Manual-Lite/02_Student_Guide/img/profile-cyber-dna.png`,
  `profile-dna-tree.png`, `profile-dna-continuing-education.png`,
  `profile-dna-class.png`, `profile-cyber-gps.png`, and
  `profile-cyber-gps-signal.png` were captured from the dev profile.
- **Verified in this tree:** `npm run lint` (0 errors), `npm run build`, the
  Career Atlas and feature-gate unit tests, `check-doc-assets.py`, and the
  Markdown/MkDocs link check.
- **Not yet verified:** the database-backed Momentum tests and the
  375/768/1024/1440 dark/light manual pass. Do not mark the preview
  production-ready until those are recorded here.

### Portfolio, GPS, and curriculum demand (11 November 2026)

Status: **implemented; deployed to development; GPS screenshots captured on 12 November 2026.**

- **Profile -> Careers tab:** the Cybersecurity GPS (optional questions kept in
  component state and never stored) and the Career Atlas. The GPS shows an
  active/fading practice signal and names fading interest domains.
- **Profile -> Portfolio tab:** Role Readiness (pathway selector, skills held,
  gaps, next workbooks with readiness labels, capstone, certifications, employer
  evidence, and the five-stage pipeline), the professional portfolio, and the
  competency taxonomy with five-dimension scores.
- **Colour indicators:** green/amber/red/grey are always paired with a text
  label and a sample size. No colour-only meaning.
- **Course analytics:** the per-exercise heatmap shows completion, first-attempt,
  hint-free, and abandonment rates with suppressed rows kept explicit.
- **Reports:** the instructor **Curriculum demand** panel turns pulse topics,
  exercise friction, and competency coverage into prioritised build prompts with
  the same small-cohort suppression.
- **Verified in this tree:** `ruff` and `py_compile` on the new services and
  routers; `pytest tests/test_curriculum_demand.py tests/test_career_readiness.py`
  (13 passed); `npm run lint` (0 errors) and `npm run build`; live service
  calls against the development database for three learner accounts and an
  administrator; `/api/analytics/reports/curriculum-demand` returned five
  reporting courses and ten prioritised prompts.
- **Not yet verified:** screenshots for the Portfolio tab, taxonomy, exercise
  heatmap, and Curriculum demand at 375/768/1024/1440 in both themes. Cyber DNA,
  GPS, Momentum, Career Atlas, Admin Features, and the workbook reading view are
  live captures. Capture the remaining views on development and replace the
  preview images before announcing the preview.

### Achievement studio and question banks (12 November 2026)

Status: **implemented; deployed to development; live capture pending.**

- **Admin → Settings → Achievements:** one grouped, filterable studio for
  built-in and custom badges. Summary cards, search, group/tier/source/state
  filters, a create/edit form with a live preview, and a two-step delete.
- **Values:** tier (Bronze/Silver/Gold/Platinum) and difficulty
  (Starter/Standard/Advanced/Expert) set the point value. Platinum Expert is
  worth 200 points; Bronze Starter is worth 8.
- **Quiz ladder:** a perfect three-question sampled check earns **Platinum
  Check**; advanced/expert items can earn **Relevance Ace**; three exercises
  earn **Hat Trick**; three tracks earn **Polymath**; five passes in a row earn
  **Five in a Row**; a climb from below 70% to 100% earns **Tier Climb**.
- **Admin → Settings → Question banks:** read-only full bank with answers,
  explanations, objectives, and public references. Validation runs on demand.
- **Reliability:** `python scripts/check-question-banks.py` passes for 9
  pathways and 34 questions; references are external `https://` sources.
- **Verified in this tree:** `ruff` and `py_compile`; 29 tests across the
  achievement catalogue, certification banks, curriculum demand, and career
  readiness; `npm run lint` (0 errors) and `npm run build`.
- **Not yet verified:** a live browser pass for the studio and question-bank
  tabs at 375/768/1024/1440 in both themes.

### DevFest Cyber Discovery event layer (12 November 2026)

Status: **implemented on the existing event engine; development rehearsal
pending.**

- **Event engine:** a normal `Competition` with `experience_key = "devfest-2027"`
  shows the Cyber Discovery panel on `/events/:id`. Participants, labs,
  leaderboard, sponsors, certificates, and verification are unchanged.
- **Learner panel:** four morning investigations with completion and lab links,
  Cyber DNA snapshot, four afternoon pathways with readiness and next workbooks,
  Career Stories, and the exclusive `DVF-CYBER-2027` certificate.
- **Instructor panel:** aggregate investigation starts, pathway starts, and
  certificate availability with the configured small-cohort suppression.
- **Seed:** `python -m app.scripts.seed_devfest_event --preview` creates or
  refreshes the event with the eight mapped labs and three sponsors.
- **Verified in this tree:** `ruff` and `py_compile`; 31 tests across the event,
  achievement, certification, and career suites; `npm run lint` (0 errors) and
  `npm run build`.
- **Verified on development (12 November 2026):** migration added
  `competitions.experience_key`; the seed created event `id=4` with 9 labs and 3
  sponsors; `/api/competitions/4/discovery` returned 4 blocks, 4 pathways, DNA,
  and the certificate; `/api/competitions/4/discovery/overview` returned the
  suppressed state for a one-participant cohort; the learner certificate list
  included `discovery`; `/api/competitions/4/certificate/discovery` returned the
  `DVF-CYBER-2027-1223B` serial; `/events/4` and
  `/certificate/event/4/discovery` served 200.
- **Not yet verified:** the visual event page, discovery panel, and certificate
  PDF at 375/768/1024/1440 in both themes, and a full six-hour rehearsal with a
  mixed cohort.

## 2.7.0 release verification

Released and deployed on **11 November 2026**. Tag `v2.7.0` points at
`ce7c25bb` and the same commit runs on development (`172.16.16.44`) and
production (`172.16.16.41` / `https://ctfd.swocts.com`).

- **Version and health:** both hosts report `2.7.0` with
  `{"status":"healthy","database":"up"}`, the frontend and backend containers
  are healthy, and the WireGuard route `10.255.0.0/16 dev wg0` is present.
- **Quiz banks:** both databases hold the four Beginner banks (5/5/4/4
  questions, pass 70). The track API reports `has_quiz=true` for all four
  levels, and a Stage 2 submission returned **100% (5/5)** with explanations on
  both hosts.
- **Learning smoke:** `scripts/ui-learning-smoke.mjs` passed **13/13** on a
  completed (18/18) account and **13/13** on a fresh account, on development and
  production. The fresh account correctly showed no Quiz or Certificate button.
  Evidence: `ui-workspace-artifacts/release-270/{dev,prod}-{complete,fresh}/learning-smoke.json`.
- **VPN-only target reveal:** a VPN-only Web lab showed the computed address
  (`10.100.232.17` on development, `10.100.54.17` on production) and the hosts
  mapping. The RangeBox versions of the same lab kept `hostnames` without an
  `ip` on both hosts.
- **Non-Beginner lab:** Malware `malware-1-1-eicar-triage` spawned VPN-only on
  development, the EICAR sample was retrieved from the evidence server, and the
  flag was accepted; `malware-1-2-strings-static-analysis` unlocked.
- **CI:** CI, Quality checks, CodeQL, and Trivy are green on `ce7c25bb` in the
  public repository. The private v2 mirror keeps Actions disabled.
- **Disk:** development has about **189 GB** free; production has about
  **34 GB** free, above the 10 GB per-launch threshold and the current prebuilt
  image set.
- **Cleanup:** the four temporary QA accounts and their completions were
  deleted, no lab containers or lab networks remain on either host, and the
  status dashboard reports `healthy` on `2.7.0` for both deployments.

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
  2G; a later pass removed **100 stale `ocr-lab` hash tags** and left about
  **35 GB free** on the production volume. `docker system df` still reports
  roughly 32 GB reclaimable because the current `:latest` and current hash tags
  are live. Do not run `docker image prune -a` on this host.
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
  level and the UI hides the Quiz button when no active level quiz exists.
- The Beginner quiz banks are now seeded from
  `platform/backend/app/scripts/seed_level_quizzes.py`: Stage 1 and Stage 2 have
  5 questions each, Stage 3 and Stage 4 have 4, and the passing score is 70.
  The Quiz button appears only for a completed level with an active bank.
  Verified on dev: **10/10 checks**, four Quiz buttons, Stage 2 submitted
  **100% (5/5)** with per-question explanations, and the Stage 3/4 banks loaded
  with the expected question counts. On production the API reports
  `has_quiz=true` for all four levels and the Stage 2 submission returned
  **100% (5/5)**.
- Repeatable learning smoke: `scripts/ui-learning-smoke.mjs` compares the Quiz
  and Certificate buttons against the track API for every level. It passed
  **13/13** on a completed (18/18) development account and **13/13** on a fresh
  account, where both buttons correctly stayed hidden. Evidence:
  `ui-workspace-artifacts/journey-20261111/learning-smoke.json`.
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

