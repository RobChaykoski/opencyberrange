# Pilot readiness review — 2026-11-20

Pre-event review of the production Moodle LTI pilot before the first participant
session on 2026-11-21.

- Public Moodle: `https://moodle.swocts.com` (backend `172.16.16.41:8092`)
- Public platform: `https://ctfd.swocts.com`
- Public DNS: both names resolve to `70.54.16.7`; the internal view resolves to
  NPM at `172.16.16.11`
- Roles tested: student, editing teacher

## Verdict

The pilot path is ready. Student and instructor launches, the workbook pane,
grade passback, roster sync, accounts, mail, secrets, backups, and the public
TLS/HSTS path all passed. No blocking defects were found.

Two items are deliberate pilot exceptions and one code change is pending:

1. LTI teachers are mapped to the local student role until the pending backend
   change is deployed. `pilot.instructor` has a reversible live workaround so
   the instructor UI is usable now.
2. `sso_enabled=true`, the relaxed cURL host allow-list, and the broad
   `wiki_frame_ancestor` list are pilot-only settings to revert after the event.
3. Cloudflare DDNS is deployed and verified; the pilot token should be rotated
   after the event because it was supplied interactively.

## Verified

### Public path

| Check | Result |
|---|---|
| Public DNS for both hosts | `70.54.16.7` |
| Moodle login from an external fetcher | `200`, `Server: openresty` |
| Platform root from an external fetcher | `200` |
| Public TLS certificate (Moodle) | Let's Encrypt, valid to 2027-02-18 |
| Public TLS certificate (platform) | Let's Encrypt, valid to 2026-12-22 |
| `Strict-Transport-Security` (Moodle) | present after this review |
| `Strict-Transport-Security` (platform) | present |
| LTI JWKS from an external fetcher | `200 application/json` |

### Moodle and LTI

| Check | Result |
|---|---|
| Pilot accounts that can log in | 11 / 11 |
| Instructor role in Moodle | `editingteacher`, editing mode available |
| Moodle schema check | `Database structure is ok` |
| Cron | runs every minute; scheduled tasks advancing |
| LTI tool type | `OpenCyberRange Pilot`, state configured |
| Moodle LTI activity | `OpenCyberRange Pilot Lab`, max grade 100 |
| Grade passback | `80.00 / 100` visible in the student gradebook |
| NRPS roster | 11 members, 11 distinct subjects |
| Deep link / launch | student and instructor both reach the exercise |
| Workbook pane | renders `Exercise 0.1 — Ping Basics` |
| Console errors during launch | none |

### Workbooks and links

The authoritative audit crawled every workbook referenced by the production
database, authenticated as an instructor:

| Check | Result |
|---|---|
| Workbook references in `labs.workbook` | 201 |
| Pages returning `200` with an article | 201 / 201 |
| Pages with an empty or short article | 0 |
| Unique assets requested | 137, all `200` |
| Unique internal wiki links requested | 385, all `200` |
| Placeholder markers | 6 hits, all legitimate prose (`placeholders`, `TODO` in an OSINT exercise about source comments) |
| Offline crawl (3,392 pages) | only 4 broken links, all in the high-school wiki (excluded pages) |

The workbook URL used by the pilot activity is
`https://ctfd.swocts.com/wiki/range/netfor/CH_N0_Network_Foundations/01_Ping_Basics/`.
Its HTML, CSS, JS, images, and sitemap all return `200`, and the page renders
inside the sandboxed iframe with the `ocr-embed` class.

### Moodle course navigation

| Role | Links checked | Failures |
|---|---|---|
| Student (course, activity, gradebook) | 31 | 0 |
| Instructor (course, activity, gradebook, tool config) | 98 | 0 |

### Security and operations

| Check | Result |
|---|---|
| OCR database secrets | encrypted (`v1:gAAAA…`), no plaintext |
| Moodle SMTP password | Compose secret, mode `600`, `daemon:daemon`; DB `smtppass` length 0 |
| Moodle `.env` / pilot CSV | mode `600` |
| Latest OCR backup | 2.4 MB dump + SHA-256, mode `600` |
| OCR/Frontend error logs | no current errors |
| Certificates | valid; NPM renewal in place |
| Public crawler headers | `X-Robots-Tag` present on both hosts |

## Changes applied during the review

- Added HSTS at the Moodle origin (`deploy/moodle-prod/apache-hsts.conf`,
  mounted by Compose); NPM passes the origin header through. Verified
  externally.
- Fixed `platform_settings.mail_public_url` from `https//ctfd.swocts.com` to
  `https://ctfd.swocts.com`.
- Renamed the Moodle course section from the default “New section” to
  “Pilot activities”.
- Disabled Moodle’s stock user tours so the course activity is visible on first
  login instead of behind the “Find your way around” modal.
- Set `pilot.instructor` to the local instructor role and stopped the LTI
  re-provisioning from resetting it (reversible pilot workaround).
- Updated the LTI identity provider config with
  `instructor_group="Instructor"`.
- Added LTI role-claim mapping and a regression test in the repository
  (`app/services/lti.py`, `tests/test_lti.py`). **Not deployed yet.**
- Fixed the high-school wiki exclusions that produced four broken links
  (`mkdocs-highschool.yml`). Takes effect on the next wiki build.

## Findings and recommendations

### 1. LTI teacher role mapping — deploy after the event

Moodle editing teachers launch as local `student` accounts because
`provision_launch_user` did not pass the LTI role claim into the SSO role
mapper, and the LTI provider has no instructor group. The code fix is ready and
tested; deploying it requires a backend rebuild.

Until then:

- `pilot.instructor` is usable as an instructor.
- `pilot.mentor` and `pilot.ta` will be provisioned as students on first launch.
- To deploy later, rebuild `ocr-backend` from the repository and ensure the
  provider config contains `"instructor_group": "Instructor"` (already set).

### 2. Postgres is reachable on the LAN

`ocr-pg-gateway` (an `alpine/socat` container) publishes `172.16.16.41:5432`.
The database is password-protected, but any host on `172.16.16.0/24` can reach
it. Restrict the gateway to the lab bridge, or bind it to `127.0.0.1` if no lab
depends on it. Do not change this during the pilot without checking the lab
network path.

### 3. Workbooks cards open the shared landing page

All 13 cards on `/workbooks` link to `/wiki/range/<slug>/`. Each track root
serves the same shared workbook introduction; the track-specific chapters are
in the left navigation. This is navigable but the card label (“Open workbook”)
promises a per-track workbook. Consider pointing each card at the track’s first
workbook page after the pilot.

### 4. Instructor dashboard has no courses

The Moodle course is not mapped to an OCR course, so the instructor dashboard
shows “No active courses are available for this view.” This is expected for an
LTI-only pilot; the LTI activity and gradebook are the pilot surfaces.

### 5. First-login discovery

Students are redirected to `/discover` (“Discover your Cyber DNA”) when they
open the dashboard before completing discovery. An LTI launch bypasses it. The
flow has a Skip action. Leave as-is unless the pilot wants a shorter first-run.

### 6. Post-event cleanup

Revert the pilot-only settings documented in `deploy/moodle-prod/README.md`:

- `sso_enabled=true`
- cURL allow-list that omits `172.16.0.0/12`
- broad `wiki_frame_ancestor` list
- `pilot.instructor` local role workaround, once the role mapping is deployed

### 7. Cloudflare DDNS

Deployed on `ocr-prod` and verified on 2026-11-20:

- container running with `unless-stopped`, Docker enabled at boot
- detects WAN IPv4 `70.54.16.7`
- both records current; a no-op write returned `200`, confirming edit access
- checks every five minutes and on startup

Rotate the pilot token after the event, replace it in
`~/cloudflare-ddns/.env`, and run `docker compose up -d`. Public DNS currently
resolves correctly; DDNS is a resilience control for firewall/WAN changes.

## Operational note

During the audit, `admin/cli/purge_caches.php` was run as root inside the Moodle
container. It created root-owned cache files under `/bitnami/moodledata`, and
Moodle returned `500 Invalid permissions detected when trying to create a
directory`. Ownership was restored to `daemon:daemon`, the cache was purged as
the `daemon` user, and login returned to `200`. Run Moodle CLI commands as
`daemon` (`docker exec -u daemon …`), never as root.

## Reproduction commands

The audit scripts used for this review were temporary, but the durable checks
are:

```bash
# Public reachability and HSTS (from outside)
curl -sSI https://moodle.swocts.com/login/index.php | grep -i strict-transport
curl -sSI https://ctfd.swocts.com/ | grep -i strict-transport

# LTI JWKS
curl -sS https://ctfd.swocts.com/api/lti/jwks | head

# Workbook page and sitemap (authenticated browser session required)
#   https://ctfd.swocts.com/wiki/range/netfor/CH_N0_Network_Foundations/01_Ping_Basics/
#   https://ctfd.swocts.com/wiki/range/netfor/sitemap.xml

# Backups
ssh ocr-prod 'ls -lt ~/backups | head -4'
```
