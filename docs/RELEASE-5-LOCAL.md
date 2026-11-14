# Release 5 local development stack

Status: **development only.** Production remains on Release 4.

This guide brings up the Release 5 branch on a workstation without touching the
development or production hosts.

## Images

Built locally from the `release5` branch:

```bash
cd platform
docker compose -p ocr-r5 \
  -f docker-compose.dev.yml \
  -f docker-compose.release5-local.yml \
  --env-file /path/to/ocr-r5.env \
  build backend frontend
```

Tags: `opencyberrange-backend:release5`,
`opencyberrange-frontend:release5`.

The local override publishes:

| Service | URL |
|---|---|
| Frontend | `http://localhost:18081` |
| Backend | `http://localhost:18080` |

The default 80/443 ports are left free for an existing local stack.

## Environment

The local env file is disposable and must not be committed. Required values:

- `JWT_SECRET` and `WG_ENCRYPTION_KEY` generated for this stack only.
- `SETUP_TOKEN` for the first-run wizard (`local-r5-setup-token` in the local
  test).
- `DATABASE_URL`, `POSTGRES_PASSWORD`, and the usual Compose values.
- `LABS_HOST_PATH` pointing at `platform/labs` on the host.
- `PUBLIC_BASE_URL` / `FRONTEND_BASE_URL` = `http://localhost:18081`.

## First run

```bash
curl -X POST http://localhost:18081/api/setup/complete \
  -H "Content-Type: application/json" \
  --data-binary @ocr-r5-setup.json

docker exec ocr-r5-backend python /app/app/scripts/init_platform.py
```

The example-course seed requires an admin user; create the admin through setup
first, then rerun the initializer.

## Wiki

Build the workbook wiki into the local volume:

```bash
docker build -t ocr-wiki-builder:release5 wiki-builder
docker run --rm \
  -v "$PWD/..:/repo:ro" \
  -v ocr-r5_wiki_data:/out \
  ocr-wiki-builder:release5
```

## LTI core slice

The first Release 5 feature set is in the branch:

- `POST/GET/PATCH/DELETE /api/lti/admin/platforms` — register one LMS deployment
  (issuer, client_id, deployment_id, auth/token/JWKS URLs, encrypted private
  key).
- `GET /api/lti/login` — OIDC third-party initiated login with a single-use
  state and nonce.
- `POST /api/lti/launch` — verifies the LMS `id_token` against its JWKS, binds
  issuer/audience/deployment/nonce, rejects replay, links the LMS `sub` through
  `external_identities`, and hands off to the normal SPA ticket exchange.
- **Admin -> Settings -> LTI platforms** — register, edit, test the JWKS, and
  delete a deployment. The panel shows the login URL and launch/redirect URI to
  give the LMS administrator, plus launched links, score history, line-item
  creation, result retrieval, and the reviewed score form.
- **AGS 2.0 score foundation** — private_key_jwt client assertion, LMS access
  token, line-item creation/reuse, reviewed score payload, result retrieval,
  append-only `lti_scores` ledger, and admin link/score endpoints with a reviewed
  score form in the LTI panel.
- **NRPS 2.0 roster sync** — captures the membership endpoint, fetches with the
  NRPS scope, and persists only subject, role, status, and context per link on
  an explicit admin sync. Admin live/saved roster endpoints and panel actions
  included.
- **Deep Linking 2.0** — an `LtiDeepLinkingRequest` creates a single-use picker
  session bound to the launching instructor. `/lti/deep-link` selects exercises
  and posts back a signed `LtiDeepLinkingResponse` whose `ltiResourceLink`
  content items carry `/api/lti/launch?lab=<slug>` plus the `lab_slug` custom
  claim. Starting a deep-linked assignment resolves the lab and lands on the
  exercise. The picker and the launch callback render without app chrome and
  share an LTI-only CSP so an LMS can frame them and receive the return POST.
- **Per-student accommodations** — a 1.0x–3.0x time multiplier and a 0–365
  day due-date extension can be set per learner from the instructor student
  panel. Lab sessions and assignment due dates use the record; changes are
  append-only in `accommodation_events` and the activity log. The learner can
  also pause the session clock with a reason; the scheduler skips paused
  sessions and resume credits the paused time.
- **Minor-account consent and retention** — a minor enrollment records the
  institution's parental/guardian consent reference and the staff member who
  recorded it; the instructor roster flags minors whose consent is still
  missing. Each course also has a retention date and note, a preview of the
  records in scope, and append-only preview/completion evidence. The destructive
  purge remains a documented operator step after backup.
- **Human review** — the exercise result panel explains deterministic flag
  matching and lets a learner request review. Instructors see pending requests
  in the course **Reviews** tab and approve or reject with a note; requests and
  decisions are audited.
- Migrations `0015_lti_platforms`, `0016_lti_links_scores`, `0017_lti_nrps`,
  `0018_lti_roster`, `0019_lti_deep_link`, `0020_lti_dl_multiple`,
  `0021_accommodations`, `0022_lab_pause`, `0023_minor_consent`,
  `0024_retention`, and `0025_review_requests` create the platform, login-state,
  link, score, NRPS fields, roster, picker-session, multi-selection,
  accommodation, pause, consent, retention, and review tables/columns
  idempotently.

Verified against a mock LMS with a locally generated RSA key and JWKS:

- login redirect carried the required parameters;
- a signed launch reached `/sso/callback` and exchanged for a platform JWT;
- the user was provisioned as `lti-student` with the LMS student role;
- replaying the same state returned `400` and was rejected.
- the admin panel added, listed, and deleted a mock platform without console
  errors.
- the AGS client obtained a mock access token with a signed client assertion and
  posted a reviewed score to a mock line item.
- the Deep Linking flow returned a 302 to the picker with a single-use session,
  listed 179 labs, and produced a signed `LtiDeepLinkingResponse` with a lab
  launch URL and `lab_slug` custom claim.
- `GET /api/lti/jwks` published the tool key with its `kid`; the response JWT
  verified against that JWKS with the matching `kid`.

## Real Moodle staging pass

A local Moodle 5.0.2 site (bitnami/moodle + MariaDB, port 18082) was registered
as an LTI 1.3 platform. The pass on 2026-11-13 covered:

- OIDC login, including the form POST and `lti_message_hint` echo Moodle requires;
- a student launch that opened the deep-linked lab at `/exercises?labId=...`;
- the sequential-lock bypass for an LTI-assigned lab (short-lived launch grant);
- Deep Linking content selection with 179 labs and a stored activity link;
- AGS line-item creation, a reviewed score passback, result retrieval, and the
  score visible in Moodle's gradebook (80/100);
- NRPS sync of the LIS 2.0 membership container (2 members, minimum fields only).

Local-only adjustments used for this test, not production code: Moodle fetched
the tool JWKS and AGS/NRPS URLs through `host.docker.internal`, and its cURL
security allow-list had to include the local ports. Canvas and Brightspace
staging remain recommended.

Still to do: a Canvas or Brightspace staging test.

## Development deployment

`172.16.16.44` (`ocrv2`, `~/opencyberrange`) now tracks `main` at the `v5.1.1`
patch release.

- `/api/version` = **5**, health = **healthy**, Alembic = **0025**.
- 188 lab rows; 12 tracks and 139 track-visible labs in the authenticated API.
- Ten randomly sampled labs returned their detail payload.
- Authenticated page pass: dashboard, exercises, Windows track, workbooks,
  courses, profile, instructor, admin, and admin settings with no console or
  page errors.
- Live lab spawn on the host, then pause and resume: paused time credited
  correctly and the session was stopped cleanly.
- Exercise workspace tabs: Desktop, Exercise, and Workbook each fill the pane;
  RangeBox stayed connected across tab switches and the workbook rendered.
- The same tabbed shell appeared for a RangeBox lab, a VPN-only session, and a
  lab with no session; the Desktop tab showed the matching guidance. The lab
  and tab survived a refresh, and the mobile layout filled the viewport below
  the app bar.
- The Desktop uses a single RangeBox toolbar (no duplicate pane header), and
  left/right arrow keys move between tabs.
- Workbooks are served from `https://172.16.16.44:8443` (the `wiki_origin`
  setting). The separate origin lets the workbook use its own storage/search
  and removes the sandbox CORS/localStorage errors; the SPA CSP allows that
  frame via `frame-src`. Port 8443 must stay reachable from browsers.
- The workbook iframe loads on first tab use (zero wiki requests before that)
  and stays mounted across switches.
- Per-student accommodation set through the API and read back by the learner
  (`1.5x`, `+4 days`).
- LTI admin panel present; `/lti/deep-link` served with the LTI embed CSP.
- Rebuilt `opencyberrange/rangebox:lite` from the pinned Kali digest and SecLists
  commit. The documented wordlist paths exist in the image and a fresh container
  served noVNC within 6 seconds.
- Temporary verification accounts were deleted after the pass.

Production also runs Release 5 (`v5.1.1`); see the deployment record in
[`RELEASE-5-PRODUCTION-READINESS.md`](RELEASE-5-PRODUCTION-READINESS.md).

## Verified on this stack

- `/api/version` = **5**, release name **Release 5 (Powered by OpenCyberRange)**.
- Platform initialization imported **179 labs** and **12 tracks**.
- Ten randomly selected labs passed validation and API discoverability:
  High School, AI, Windows, Malware, Web, Identity, OSINT, Linux, Forensics,
  and OT.
- Authenticated page pass: dashboard, exercises, workbooks, courses, profile,
  admin users, admin settings, and the Wiki settings tab.
- Backend: **358 passed, 219 skipped**.
- Frontend build and lint: clean (existing warnings only).
- Licence, safe-URL, CSP, and signed supply-chain guards pass on the branch.

## Known local limitations

- Lab spawning requires the host firewall/network setup and the RangeBox image.
  The local override sets `HOST_NETWORK=192.168.65.0/24` (Docker Desktop's host
  network), but Docker Desktop still cannot execute the privileged iptables
  verification (`'NoneType' object has no attribute 'decode'`). The local stack
  therefore verifies the platform, content, wiki, and pages but does not
  complete a live RangeBox launch. Live workspace regression is run on
  development (`172.16.16.44`), where host isolation works.
- The local stack uses HTTP on port 18081. Production keeps TLS and the
  custom-hostname settings.

## Skills and templates used

- `opencyberrange-student-tester` — ten-lab content and discoverability pass.
- `opencyberrange-design-tester` — page hierarchy, themes, responsive workspace,
  and admin settings review.
- `opencyberrange-software-security` — safe-URL bindings and the security delta
  review.
- `opencyberrange-inclusive-curriculum` — minor-account and high-school framing.
- `opencyberrange-learning-impact` — analytics and retention planning.
- `opencyberrange-course-content-management` — course/lab relationship checks.
- `opencyberrange-ha-architecture` and `opencyberrange-program-management` —
  local-versus-deployed boundaries and release gating.
- Existing `platform/templates` and the Compose templates; no new lab template
  or content pattern was introduced for the local stack.

## Do not deploy

Do not promote `release5` to development or production until the Release 5
exit criteria in [`RELEASE-5-SCOPE.md`](RELEASE-5-SCOPE.md) are met. Production
must stay on the signed `v4` tag.


